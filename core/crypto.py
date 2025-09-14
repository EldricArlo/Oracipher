# core/crypto.py

import os
import base64
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
import argon2
from argon2.low_level import hash_secret_raw, Type

logger = logging.getLogger(__name__)

class CryptoHandler:
    """
    处理所有与加密解密相关的操作。
    """
    _SALT_SIZE: int = 16
    
    _ARGON2_TIME_COST: int = 3
    _ARGON2_MEMORY_COST: int = 65536
    _ARGON2_PARALLELISM: int = 4
    
    _KEY_LENGTH: int = 32
    _VERIFICATION_TOKEN: bytes = b"safekey-verification-token-v2-argon2"

    def __init__(self, data_dir: str):
        self.key: Optional[bytes] = None
        self.salt_path: str = os.path.join(data_dir, "salt.key")
        self.verification_path: str = os.path.join(data_dir, "verification.key")
        os.makedirs(data_dir, exist_ok=True)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        使用 argon2.low_level.hash_secret_raw 从主密码和盐派生一个加密密钥。
        """
        raw_key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=self._ARGON2_TIME_COST,
            memory_cost=self._ARGON2_MEMORY_COST,
            parallelism=self._ARGON2_PARALLELISM,
            hash_len=self._KEY_LENGTH,
            type=Type.ID
        )
        return base64.urlsafe_b64encode(raw_key)

    def set_master_password(self, password: str) -> None:
        logger.info("正在设置新的主密码 (使用 argon2-cffi)...")
        salt = os.urandom(self._SALT_SIZE)
        self.key = self._derive_key(password, salt)
        fernet = Fernet(self.key)
        
        with open(self.salt_path, "wb") as f:
            f.write(salt)
        
        encrypted_verification = fernet.encrypt(self._VERIFICATION_TOKEN)
        with open(self.verification_path, "wb") as f:
            f.write(encrypted_verification)
            
        logger.info("主密码设置成功，盐值和验证文件已创建。")

    def unlock_with_master_password(self, password: str) -> bool:
        try:
            with open(self.salt_path, "rb") as f:
                salt = f.read()
            
            derived_key = self._derive_key(password, salt)
            fernet = Fernet(derived_key)
            
            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()
            
            decrypted_verification = fernet.decrypt(encrypted_verification)

            if decrypted_verification == self._VERIFICATION_TOKEN:
                self.key = derived_key
                logger.info("保险库成功解锁。")
                return True
            else:
                logger.warning("验证令牌不匹配。")
                return False
        except FileNotFoundError:
            logger.error("盐值或验证文件未找到。应用程序可能未正确设置。")
            return False
        except InvalidToken:
            logger.warning("主密码不正确 (解密验证令牌失败)。")
            return False
        except Exception as e:
            logger.error(f"解锁过程中发生未知错误: {e}", exc_info=True)
            return False

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        try:
            with open(self.salt_path, "rb") as f:
                salt = f.read()
            
            old_derived_key = self._derive_key(old_password, salt)
            old_fernet = Fernet(old_derived_key)

            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()
            
            old_fernet.decrypt(encrypted_verification)
            logger.info("旧主密码验证成功。")

            new_derived_key = self._derive_key(new_password, salt)
            new_fernet = Fernet(new_derived_key)

            new_encrypted_verification = new_fernet.encrypt(self._VERIFICATION_TOKEN)
            with open(self.verification_path, "wb") as f:
                f.write(new_encrypted_verification)

            self.key = new_derived_key
            logger.info("主密码在加密层已成功更改。")
            return True
        except InvalidToken:
            logger.warning("提供的旧主密码不正确。")
            return False
        except FileNotFoundError:
            logger.error("无法更改密码，找不到保险库文件。")
            return False
        except Exception as e:
            logger.error(f"更改主密码时发生未知错误: {e}", exc_info=True)
            return False

    def encrypt(self, data: str) -> str:
        if not self.key:
            logger.error("加密失败：密钥未加载。请先解锁。")
            raise ValueError("Key is not loaded. Please unlock first.")
        fernet = Fernet(self.key)
        return fernet.encrypt(data.encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        if not self.key:
            logger.error("解密失败：密钥未加载。请先解锁。")
            raise ValueError("Key is not loaded. Please unlock first.")
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')

    def is_key_setup(self) -> bool:
        return os.path.exists(self.salt_path) and os.path.exists(self.verification_path)