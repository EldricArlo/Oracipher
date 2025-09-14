# core/crypto.py

import os
import base64
import logging
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class CryptoHandler:
    """
    处理所有与加密解密相关的操作。

    本类使用 `cryptography.fernet` 实现对称加密，并使用 PBKDF2
    从用户主密码安全地派生加密密钥。它负责：
    - 从主密码派生密钥。
    - 设置初始主密码并创建保险库。
    - 使用主密码解锁保险库。
    - 安全地更改主密码。
    - 加密和解密数据。
    """

    _SALT_SIZE = 16  # 盐的字节数，16字节 (128位) 是标准推荐
    _ITERATIONS = 600000  # PBKDF2的迭代次数，高迭代次数能有效抵抗暴力破解
    _VERIFICATION_TOKEN = (
        b"safekey-verification-token"  # 用于验证密码正确性的固定字节串
    )

    def __init__(self, data_dir: str):
        """
        初始化 CryptoHandler。

        Args:
            data_dir (str): 存放盐值和验证文件的应用程序数据目录。
        """
        self.key = None  # 加密密钥，只有在成功解锁后才会被加载到内存
        self.salt_path = os.path.join(data_dir, "salt.key")
        self.verification_path = os.path.join(data_dir, "verification.key")
        os.makedirs(data_dir, exist_ok=True)

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        使用 PBKDF2HMAC 从主密码和盐派生一个加密密钥。

        Args:
            password (str): 用户输入的主密码。
            salt (bytes): 用于密钥派生的盐。

        Returns:
            bytes: 一个 URL-safe Base64 编码的32字节密钥，可用于 Fernet。
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet 要求32字节的密钥
            salt=salt,
            iterations=self._ITERATIONS,
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def set_master_password(self, password: str):
        """
        设置初始主密码，并创建新的盐和验证文件。

        此方法只应在首次设置应用程序时调用。

        Args:
            password (str): 用户设置的初始主密码。
        """
        logger.info("正在设置新的主密码...")
        # 1. 生成一个加密安全的随机盐
        salt = os.urandom(self._SALT_SIZE)

        # 2. 派生密钥
        self.key = self._derive_key(password, salt)
        fernet = Fernet(self.key)

        # 3. 将盐写入文件
        with open(self.salt_path, "wb") as f:
            f.write(salt)

        # 4. 加密验证令牌并写入文件
        encrypted_verification = fernet.encrypt(self._VERIFICATION_TOKEN)
        with open(self.verification_path, "wb") as f:
            f.write(encrypted_verification)

        logger.info("主密码设置成功，盐值和验证文件已创建。")

    def unlock_with_master_password(self, password: str) -> bool:
        """
        尝试使用提供的主密码解锁保险库。

        通过派生密钥并尝试解密验证文件来工作。如果成功且内容匹配，
        则认为密码正确，并将密钥加载到内存中。

        Args:
            password (str): 用户尝试解锁的密码。

        Returns:
            bool: 如果密码正确且成功解锁，返回 True；否则返回 False。
        """
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
                # 这种情况理论上很少发生，除非验证文件被篡改
                logger.warning("验证令牌不匹配。")
                return False
        except FileNotFoundError:
            logger.error("盐值或验证文件未找到。应用程序可能未正确设置。")
            return False
        except InvalidToken:
            # 这是最常见的情况：密码错误导致密钥派生错误，解密失败
            logger.warning("主密码不正确 (解密验证令牌失败)。")
            return False
        except Exception as e:
            logger.error(f"解锁过程中发生未知错误: {e}", exc_info=True)
            return False

    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """
        安全地更改主密码。

        此过程包括：
        1. 使用旧密码验证身份。
        2. 使用新密码派生新密钥。
        3. 使用新密钥重新加密验证令牌。
        4. 更新当前会话的密钥。
        注意：此方法只更新加密层的密钥，数据的重加密由 DataManager 负责。

        Args:
            old_password (str): 当前的主密码。
            new_password (str): 希望设置的新主密码。

        Returns:
            bool: 如果密码更改成功，返回 True；否则返回 False。
        """
        try:
            # 1. 读取盐并验证旧密码
            with open(self.salt_path, "rb") as f:
                salt = f.read()

            old_derived_key = self._derive_key(old_password, salt)
            old_fernet = Fernet(old_derived_key)

            with open(self.verification_path, "rb") as f:
                encrypted_verification = f.read()

            # 这一步如果失败，会抛出 InvalidToken 异常，从而验证失败
            old_fernet.decrypt(encrypted_verification)
            logger.info("旧主密码验证成功。")

            # 2. 旧密码验证成功，派生新密钥 (使用相同的盐)
            new_derived_key = self._derive_key(new_password, salt)
            new_fernet = Fernet(new_derived_key)

            # 3. 使用新密钥重新加密验证令牌并写入文件
            new_encrypted_verification = new_fernet.encrypt(self._VERIFICATION_TOKEN)
            with open(self.verification_path, "wb") as f:
                f.write(new_encrypted_verification)

            # 4. 更新当前会话的密钥
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
        """
        使用当前加载的密钥加密字符串数据。

        Args:
            data (str): 要加密的明文字符串。

        Returns:
            str: 加密后的密文字符串。

        Raises:
            ValueError: 如果密钥未加载（即未解锁），则抛出异常。
        """
        if not self.key:
            logger.error("加密失败：密钥未加载。请先解锁。")
            raise ValueError("Key is not loaded. Please unlock first.")
        fernet = Fernet(self.key)
        return fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        使用当前加载的密钥解密字符串数据。

        Args:
            encrypted_data (str): 要解密的密文字符串。

        Returns:
            str: 解密后的明文字符串。

        Raises:
            ValueError: 如果密钥未加载（即未解锁），则抛出异常。
        """
        if not self.key:
            logger.error("解密失败：密钥未加载。请先解锁。")
            raise ValueError("Key is not loaded. Please unlock first.")
        fernet = Fernet(self.key)
        return fernet.decrypt(encrypted_data.encode()).decode()

    def is_key_setup(self) -> bool:
        """
        检查保险库是否已经初始化。

        通过检查盐值和验证文件是否存在来判断。

        Returns:
            bool: 如果文件存在，返回 True；否则返回 False。
        """
        return os.path.exists(self.salt_path) and os.path.exists(self.verification_path)
