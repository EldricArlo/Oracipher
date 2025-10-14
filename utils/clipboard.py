# utils/clipboard.py

import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

logger = logging.getLogger(__name__)

class ClipboardManager:
    """
    一个用于安全处理剪贴板操作的全局工具类。
    
    主要功能是提供一个统一的接口来复制文本，并能为敏感信息
    (如密码、2FA代码) 设置一个自动清理的定时器。
    """
    SENSITIVE_DATA_TIMEOUT_MS = 30000  # 30秒

    @staticmethod
    def copy(text: str, is_sensitive: bool = False) -> None:
        """
        将文本复制到系统剪贴板。

        Args:
            text: 要复制的文本字符串。
            is_sensitive: 如果为 True，则在设定的超时时间后自动清理剪贴板。
        """
        clipboard = QApplication.clipboard()
        if not clipboard:
            logger.warning("QApplication clipboard is not available.")
            return
            
        clipboard.setText(text)
        
        if is_sensitive:
            logger.debug(f"Sensitive data copied to clipboard. Will clear in {ClipboardManager.SENSITIVE_DATA_TIMEOUT_MS / 1000} seconds.")
            # 使用单次定时器在超时后检查并清理剪贴板
            QTimer.singleShot(
                ClipboardManager.SENSITIVE_DATA_TIMEOUT_MS,
                lambda: ClipboardManager._clear_if_matches(text)
            )

    @staticmethod
    def _clear_if_matches(original_text: str) -> None:
        """
        这是一个私有辅助方法，用于在定时器触发时执行清理操作。
        它会检查剪贴板当前的内容是否仍是当初复制的敏感信息，
        如果是，则清空；如果用户已经复制了其他内容，则不进行任何操作。
        """
        clipboard = QApplication.clipboard()
        if clipboard and clipboard.text() == original_text:
            clipboard.clear()
            logger.info("Clipboard cleared of sensitive data after timeout.")

# 创建一个全局实例，方便在其他模块中直接导入和使用。
clipboard_manager = ClipboardManager()