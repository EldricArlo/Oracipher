# core/crypto.py

import os
import base64
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from argon2.low_level import hash_secret_raw, Type

logger = logging.getLogger(__name__)

class CryptoHandler:
    """
    负责处理所有与加密、解密及主密码相关的核心安全操作。

    本模块采用业界推荐的安全实践：
    - 密钥派生: 使用 Argon2id 算法从用户主密码中派生出加密密钥。
      Arg2id 是一种内存困难型函数，能有效抵抗来自 GPU 的暴力破解和侧信道攻击。
    - 对称加密: 使用 Fernet (基于 AES-128-CBC 和 HMAC-SHA256 的认证加密方案)，
      确保数据的保密性和完整性，防止数据被篡改。
    """
    _SALT_SIZE: int = 16  # 128-bit 盐值，提供足够的唯一性。

    # Argon2id 参数，基于 OWASP (Open Web Application Security Project) 的推荐起点。
    # 这些参数可以在未来根据硬件发展进行调整以增强安全性。
    _ARGON2_TIME_COST: int = 3       # 迭代次数，增加计算耗时。
    _ARGON2_MEMORY_COST: int = 65536 # 内存消耗 (64 MiB)，有效对抗并行攻击。
    _ARGON2_PARALLELISM: int = 4      # 并行度，利用多核处理器。

    _KEY_LENGTH: int = 32 # 派生密钥长度为 256 bits (32 bytes)，用于 Fernet。

    # 一个静态的、用于验证密码正确性的“魔法字符串”。
    # 当用户解锁时，我们会尝试用派生的密钥解密验证文件，如果解密后的内容与此令牌匹配，
    # 则证明密码正确，避免了直接存储密码或其哈希值。
    _VERIFICATION_TOKEN: bytes = b"oracipher-verification-token-v1-argon2"

    def __init__(self, data_dir: str):
        """
        初始化 CryptoHandler。

        Args:
            data_dir: 应用程序数据目录的路径，用于存放盐值和验证文件。
        """
        self.key: Optional[bytes] = None
        self.salt_path: str = os.path.join(data_dir, "salt.key")
        self.verification_path: str = os.path.join(data_dir, "verification.key")
        os.makedirs(data_dir, exist_ok=True)

    # --- MODIFICATION START: Converted to a static method ---
    # 将此方法转换为静态方法，使其不依赖于实例 (self)。
    # 这样就可以在 data_handler.py 中安全地重用，以确保加密参数的一致性。
    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """
        使用 Argon2id 从主密码和盐派生一个 URL-safe Base64 编码的加密密钥。
        
        这是整个安全系统的基石。相同的密码和盐值总会派生出相同的密钥。
        """
        logger.debug("Deriving encryption key using Argon2id...")
        raw_key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=CryptoHandler._ARGON2_TIME_COST,
            memory_cost=CryptoHandler._ARGON2_MEMORY_COST,
            parallelism=CryptoHandler._ARGON2_PARALLELISM,
            hash_len=CryptoHandler._KEY_LENGTH,
            type=Type.ID  # 明确使用 Argon2id
        )
        return base64.urlsafe_b64encode(raw_key)
    # --- MODIFICATION END ---

    def set_master_password(self, password: str) -> None:
        """
        首次设置主密码。

        此过程会生成一个全新的随机盐值，并用派生的密钥加密验证令牌，
        然后将盐值和加密后的令牌分别存入文件。
        """
        logger.info("Setting a new master password for the vault...")
        try:
            salt = os.urandom(self._SALT_SIZE)
            # 现在调用的是静态方法
            self.key = CryptoHandler._derive_key(password, salt)
            fernet = Fernet(self.key)
            
            with open(self.salt_path, "wb") as f:
                f.write(salt)
            
            encrypted_verification = fernet.encrypt(self._VERIFICATION_TOKEN)
            with open(self.verification_path, "wb") as f:
                f.write(encrypted_verification)
                
            logger.info("Master password set successfully. Salt and verification files created.")
        except IOError as e:
            logger.critical(f"Failed to write vault setup files: {e}", exc_info=True)
            raise

    def unlock_with_master_password(self, password: str) -> bool:
        """
        使用提供的主密码尝试解锁保险库。

        如果成功，会将派生的密钥加载到内存中以供后续加解密操作使用。
        """
        try:
            with open(self.salt_path, "rb") as f:
                salt = f.read()
            
            # 现在调用的是静态方法
            derived_key = CryptoHandler._derive_key(password, salt)
            fernet = Fernet(derived_key)
            
            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()
            
            decrypted_verification = fernet.decrypt(encrypted_verification, ttl=None)

            if decrypted_verification == self._VERIFICATION_TOKEN:
                self.key = derived_key
                logger.info("Vault unlocked successfully.")
                return True
            else:
                # 理论上，如果令牌不匹配，fernet.decrypt 会直接抛出 InvalidToken 异常。
                # 但保留此分支以防万一。
                logger.warning("Verification token mismatch after successful decryption. This should not happen.")
                return False
        except FileNotFoundError:
            logger.error("Salt or verification file not found. Vault may not be initialized.")
            return False
        except InvalidToken:
            logger.warning("Incorrect master password (failed to decrypt verification token).")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during unlock: {e}", exc_info=True)
            return False

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        更改主密码。

        此方法仅负责在验证旧密码后，用新密码重新加密验证文件并更新当前会话的密钥。
        注意：所有保险库数据的重新加密是由 DataManager 协调完成的。
        """
        try:
            salt = self.get_salt()
            if salt is None:
                raise FileNotFoundError("Salt file not found during password change.")

            # 1. 验证旧密码是否正确，通过尝试解密验证令牌。
            old_derived_key = CryptoHandler._derive_key(old_password, salt)
            old_fernet = Fernet(old_derived_key)

            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()
            
            old_fernet.decrypt(encrypted_verification, ttl=None) # 如果失败会抛出 InvalidToken
            logger.info("Old master password verified successfully.")

            # 2. 生成新密钥，并用它重新加密验证令牌，写入文件。
            new_derived_key = CryptoHandler._derive_key(new_password, salt)
            new_fernet = Fernet(new_derived_key)

            new_encrypted_verification = new_fernet.encrypt(self._VERIFICATION_TOKEN)
            with open(self.verification_path, "wb") as f:
                f.write(new_encrypted_verification)

            # 3. 更新当前会话的密钥，以便后续操作使用新密钥。
            self.key = new_derived_key
            logger.info("Master key has been successfully changed at the crypto layer.")
            return True
        except InvalidToken:
            logger.warning("The provided 'old' master password was incorrect during change attempt.")
            return False
        except FileNotFoundError:
            logger.error("Cannot change password, vault setup files not found.")
            return False
        except Exception as e:
            logger.error(f"An unknown error occurred while changing master password: {e}", exc_info=True)
            return False

    def encrypt(self, data: str) -> str:
        """
        使用当前会话的密钥加密字符串数据。

        Raises:
            ValueError: 如果密钥未加载 (保险库未解锁)。
        """
        if not self.key:
            logger.error("Encryption failed: Key is not loaded. The vault must be unlocked first.")
            raise ValueError("Encryption key is not loaded. Please unlock the vault.")
        fernet = Fernet(self.key)
        return fernet.encrypt(data.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """
        使用当前会话的密钥解密字符串数据。

        Raises:
            ValueError: 如果密钥未加载 (保险库未解锁)。
            InvalidToken: 如果数据损坏或密钥不正确。
        """
        if not self.key:
            logger.error("Decryption failed: Key is not loaded. The vault must be unlocked first.")
            raise ValueError("Decryption key is not loaded. Please unlock the vault.")
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_data.encode('utf-8'), ttl=None).decode('utf-8')

    def is_key_setup(self) -> bool:
        """
        检查保险库是否已经初始化 (通过检查盐值和验证文件是否存在)。
        """
        return os.path.exists(self.salt_path) and os.path.exists(self.verification_path)

    def get_salt(self) -> Optional[bytes]:
        """
        安全地读取并返回盐值文件的内容。
        """
        if not self.is_key_setup():
            return None
        try:
            with open(self.salt_path, "rb") as f:
                return f.read()
        except IOError as e:
            logger.error(f"Could not read salt file: {e}", exc_info=True)
            return None