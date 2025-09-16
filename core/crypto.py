# core/crypto.py

import os
import base64
import json
import logging
from typing import Optional, Dict, Any

from cryptography.fernet import Fernet, InvalidToken
from argon2.low_level import hash_secret_raw, Type

logger = logging.getLogger(__name__)


class CryptoHandler:
    """
    负责处理所有与加密、解密及主密码相关的核心安全操作。

    本模块采用业界推荐的安全实践：
    - 密钥派生: 使用 Argon2id 算法从用户主密码中派生出加密密钥。
        此版本的改进在于，Argon2id的参数与盐值一同存储，使其更具前瞻性。
    - 对称加密: 使用 Fernet (基于 AES-GCM 的认证加密方案)，
        确保数据的保密性和完整性，防止数据被篡改。
    """

    _SALT_SIZE: int = 16  # 128-bit 盐值，提供足够的唯一性。

    # --- MODIFICATION START: Default Argon2id parameters ---
    # 这些现在是新保险库的默认值，但可以被元数据文件覆盖。
    _DEFAULT_ARGON2_TIME_COST: int = 3  # 迭代次数
    _DEFAULT_ARGON2_MEMORY_COST: int = 65536  # 内存消耗 (64 MiB)
    _DEFAULT_ARGON2_PARALLELISM: int = 4  # 并行度
    # --- MODIFICATION END ---

    _KEY_LENGTH: int = 32  # 派生密钥长度为 256 bits (32 bytes)
    _VERIFICATION_TOKEN: bytes = b"oracipher-verification-token-v2-argon2-json"

    def __init__(self, data_dir: str):
        """
        初始化 CryptoHandler。

        Args:
            data_dir: 应用程序数据目录的路径。
        """
        self.key: Optional[bytes] = None
        # --- MODIFICATION START: Changed salt path to a metadata file ---
        self.metadata_path: str = os.path.join(data_dir, "vault.meta")
        self.verification_path: str = os.path.join(data_dir, "verification.key")
        # --- MODIFICATION END ---
        os.makedirs(data_dir, exist_ok=True)

    # --- MODIFICATION START: New methods for metadata handling ---
    def _load_vault_metadata(self) -> Optional[Dict[str, Any]]:
        """从 vault.meta 文件加载包含盐值和Argon2参数的JSON数据。"""
        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            # 基础验证
            if 'salt_b64' in meta and 'argon2_params' in meta:
                return meta
            logger.error("Vault metadata is missing required keys.")
            return None
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            logger.error(f"Could not load or parse vault metadata: {e}", exc_info=True)
            return None

    def _save_vault_metadata(self, salt: bytes, params: Dict[str, int]) -> None:
        """将盐值和Argon2参数保存到 vault.meta 文件。"""
        meta = {
            "salt_b64": base64.b64encode(salt).decode('utf-8'),
            "argon2_params": params
        }
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    # --- MODIFICATION END ---

    # --- MODIFICATION START: _derive_key is now a static method accepting params ---
    @staticmethod
    def _derive_key(password: str, salt: bytes, argon2_params: Dict[str, int]) -> bytes:
        """
        使用 Argon2id 从主密码、盐和指定的参数派生一个加密密钥。
        """
        logger.debug(f"Deriving encryption key using Argon2id with params: {argon2_params}")
        raw_key = hash_secret_raw(
            secret=password.encode("utf-8"),
            salt=salt,
            time_cost=argon2_params['time_cost'],
            memory_cost=argon2_params['memory_cost'],
            parallelism=argon2_params['parallelism'],
            hash_len=CryptoHandler._KEY_LENGTH,
            type=Type.ID,
        )
        return base64.urlsafe_b64encode(raw_key)
    # --- MODIFICATION END ---

    def set_master_password(self, password: str) -> None:
        """
        首次设置主密码。
        """
        logger.info("Setting a new master password for the vault...")
        try:
            salt = os.urandom(self._SALT_SIZE)

            # --- MODIFICATION START: Use default params for new vault ---
            current_params = {
                'time_cost': self._DEFAULT_ARGON2_TIME_COST,
                'memory_cost': self._DEFAULT_ARGON2_MEMORY_COST,
                'parallelism': self._DEFAULT_ARGON2_PARALLELISM
            }
            self.key = CryptoHandler._derive_key(password, salt, current_params)
            # --- MODIFICATION END ---

            fernet = Fernet(self.key)

            # --- MODIFICATION START: Save metadata instead of just salt ---
            self._save_vault_metadata(salt, current_params)
            # --- MODIFICATION END ---

            encrypted_verification = fernet.encrypt(self._VERIFICATION_TOKEN)
            with open(self.verification_path, "wb") as f:
                f.write(encrypted_verification)

            logger.info(
                "Master password set successfully. Metadata and verification files created."
            )
        except IOError as e:
            logger.critical(f"Failed to write vault setup files: {e}", exc_info=True)
            raise

    def unlock_with_master_password(self, password: str) -> bool:
        """
        使用提供的主密码尝试解锁保险库。
        """
        try:
            # --- MODIFICATION START: Load from metadata file ---
            meta = self._load_vault_metadata()
            if not meta:
                raise FileNotFoundError("Vault metadata not found or invalid.")
            salt = base64.b64decode(meta['salt_b64'])
            params = meta['argon2_params']

            derived_key = CryptoHandler._derive_key(password, salt, params)
            # --- MODIFICATION END ---

            fernet = Fernet(derived_key)

            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()

            decrypted_verification = fernet.decrypt(encrypted_verification, ttl=None)

            if decrypted_verification == self._VERIFICATION_TOKEN:
                self.key = derived_key
                logger.info("Vault unlocked successfully.")
                return True
            else:
                logger.warning(
                    "Verification token mismatch after successful decryption."
                )
                return False
        except FileNotFoundError:
            logger.error(
                "Metadata or verification file not found. Vault may not be initialized."
            )
            return False
        except InvalidToken:
            logger.warning(
                "Incorrect master password (failed to decrypt verification token)."
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during unlock: {e}", exc_info=True
            )
            return False

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        更改主密码。
        """
        try:
            # --- MODIFICATION START: Load from metadata file ---
            meta = self._load_vault_metadata()
            if not meta:
                raise FileNotFoundError("Vault metadata not found during password change.")
            salt = base64.b64decode(meta['salt_b64'])
            params = meta['argon2_params']
            # --- MODIFICATION END ---

            old_derived_key = CryptoHandler._derive_key(old_password, salt, params)
            old_fernet = Fernet(old_derived_key)

            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()
            old_fernet.decrypt(encrypted_verification, ttl=None)
            logger.info("Old master password verified successfully.")

            new_derived_key = CryptoHandler._derive_key(new_password, salt, params)
            new_fernet = Fernet(new_derived_key)

            new_encrypted_verification = new_fernet.encrypt(self._VERIFICATION_TOKEN)
            with open(self.verification_path, "wb") as f:
                f.write(new_encrypted_verification)

            self.key = new_derived_key
            logger.info("Master key has been successfully changed at the crypto layer.")
            return True
        except InvalidToken:
            logger.warning("The provided 'old' master password was incorrect.")
            return False
        except FileNotFoundError:
            logger.error("Cannot change password, vault setup files not found.")
            return False
        except Exception as e:
            logger.error(f"Error changing master password: {e}", exc_info=True)
            return False

    def encrypt(self, data: str) -> str:
        """
        使用当前会话的密钥加密字符串数据。
        """
        if not self.key:
            raise ValueError("Encryption key is not loaded. Please unlock the vault.")
        fernet = Fernet(self.key)
        return fernet.encrypt(data.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """
        使用当前会话的密钥解密字符串数据。
        """
        if not self.key:
            raise ValueError("Decryption key is not loaded. Please unlock the vault.")
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_data.encode("utf-8"), ttl=None).decode("utf-8")

    def is_key_setup(self) -> bool:
        """
        检查保险库是否已经初始化。
        """
        # --- MODIFICATION START: Check for metadata file ---
        return os.path.exists(self.metadata_path) and os.path.exists(self.verification_path)
        # --- MODIFICATION END ---

    # --- MODIFICATION START: Renamed get_salt to get_metadata ---
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """安全地读取并返回元数据文件的内容。"""
        return self._load_vault_metadata()
    # --- MODIFICATION END ---