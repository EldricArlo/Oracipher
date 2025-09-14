# ui/components/two_fa_widget.py

import pyotp
import time
import logging
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QProgressBar
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

from language import t
from utils.paths import resource_path
from utils.clipboard import clipboard_manager

logger = logging.getLogger(__name__)

class TwoFAWidget(QWidget):
    """
    一个用于显示TOTP（基于时间的一次性密码）代码和刷新倒计时的自包含小部件。
    """
    def __init__(self, secret: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # --- 修改开始 ---
        # 增加对 secret 参数的有效性检查，防止其为 None 或空字符串
        if not secret:
            self.is_valid = False
            logger.error("A null or empty secret was provided to TwoFAWidget.")
        else:
            try:
                self.totp = pyotp.TOTP(secret)
                self.is_valid = True
            except Exception:
                # 捕获 pyotp 可能因无效密钥（如非 Base32 字符串）抛出的异常
                self.is_valid = False
                logger.error(f"Invalid Base32 secret provided to TwoFAWidget.")
        # --- 修改结束 ---

        self.init_ui()
        
        if self.is_valid:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_code)
            self.timer.start(1000)
            
            self.update_code()
        else:
            # 如果密钥无效，直接显示错误信息
            self.code_display.setText("Invalid Key")
            self.progress_bar.setVisible(False)


    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(5)

        value_layout = QHBoxLayout()
        
        self.code_display = QLineEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setObjectName("fieldValueDisplay")
        self.code_display.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent; border: none;")
        self.code_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        copy_button = QPushButton()
        copy_button.setObjectName("inlineButton")
        copy_button.setIcon(QIcon(str(resource_path("ui/assets/icons/copy.svg"))))
        copy_button.setText("")
        copy_button.setFixedSize(32, 32)
        copy_button.setToolTip(t.get('button_copy'))
        copy_button.setFocusPolicy(Qt.FocusPolicy.NoFocus) # 修改: 解决焦点问题
        copy_button.clicked.connect(self.copy_to_clipboard)

        value_layout.addWidget(self.code_display, 1)
        value_layout.addWidget(copy_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 30)
        self.progress_bar.setFixedHeight(5)

        main_layout.addLayout(value_layout)
        main_layout.addWidget(self.progress_bar)

    def update_code(self) -> None:
        """生成新的TOTP代码并更新倒计时进度条。"""
        if not self.is_valid:
            return
            
        try:
            current_code = self.totp.now()
            formatted_code = f"{current_code[:3]} {current_code[3:]}"
            self.code_display.setText(formatted_code)
            
            time_remaining = 30 - (int(time.time()) % 30)
            self.progress_bar.setValue(time_remaining)
        except Exception as e:
            logger.error(f"Failed to update TOTP code: {e}", exc_info=True)
            if hasattr(self, 'timer') and self.timer.isActive():
                self.timer.stop()
            self.code_display.setText("Error")

    def copy_to_clipboard(self) -> None:
        """将当前代码（不含空格）安全地复制到剪贴板。"""
        if not self.is_valid:
            return
            
        current_code = self.totp.now()
        clipboard_manager.copy(current_code, is_sensitive=True)
        logger.info("2FA code copied to clipboard (will clear in 30s).")

    def stop_timer(self) -> None:
        """停止定时器，防止在小部件被销毁后继续运行。"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()

    def __del__(self) -> None:
        """确保在对象被销毁时停止定时器。"""
        self.stop_timer()