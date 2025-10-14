# ui/components/two_fa_widget.py

import pyotp
import time
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QProgressBar,
)
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

        # --- MODIFICATION START: Improved secret validation ---
        # 1. 首先，明确检查传入的 'secret' 是否为非空字符串。
        if secret and isinstance(secret, str):
            try:
                # 2. 只有在 secret 非空时，才尝试创建 TOTP 对象。
                #    这可以捕获真正格式错误的密钥（例如，非 Base32 字符）。
                self.totp = pyotp.TOTP(secret)
                self.is_valid = True
            except Exception:
                # 如果 pyotp 在这里报错，说明密钥格式有问题。
                self.is_valid = False
                logger.error(f"Invalid Base32 secret provided to TwoFAWidget.")
        else:
            # 3. 如果 'secret' 是 None, 空字符串, 或其他非字符串类型, 它就是无效的。
            self.is_valid = False
        # --- MODIFICATION END ---

        self.init_ui()

        if self.is_valid:
            # 只有在密钥绝对有效时，才启动定时器。
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_code)
            self.timer.start(1000)
            self.update_code()
        else:
            # --- MODIFICATION START: Improved UI for invalid state ---
            # 如果密钥无效或未设置，显示清晰的状态并禁用不必要的功能。
            self.code_display.setText(t.get("2fa_status_not_setup"))
            self.progress_bar.setVisible(False)
            self.copy_button.setEnabled(False)
            # --- MODIFICATION END ---

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        value_layout = QHBoxLayout()

        self.code_display = QLineEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setObjectName("fieldValueDisplay")
        # 修正样式，以适应可能出现的文本（如 "Not Set Up"）
        self.code_display.setStyleSheet(
            "font-size: 20px; font-weight: bold; background: transparent; border: none;"
        )
        self.code_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.copy_button = QPushButton()
        self.copy_button.setObjectName("inlineButton")
        self.copy_button.setIcon(QIcon(str(resource_path("ui/assets/icons/copy.svg"))))
        self.copy_button.setText("")
        self.copy_button.setFixedSize(32, 32)
        self.copy_button.setToolTip(t.get("button_copy"))
        self.copy_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.copy_button.clicked.connect(self.copy_to_clipboard)

        value_layout.addWidget(self.code_display, 1)
        value_layout.addWidget(self.copy_button)

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
            # 捕获在运行时可能出现的任何意外错误
            logger.error(f"Failed to update TOTP code: {e}", exc_info=True)
            if hasattr(self, "timer") and self.timer.isActive():
                self.timer.stop()
            self.code_display.setText("Error")
            self.copy_button.setEnabled(False)

    def copy_to_clipboard(self) -> None:
        """将当前代码（不含空格）安全地复制到剪贴板。"""
        if not self.is_valid:
            return

        current_code = self.totp.now()
        clipboard_manager.copy(current_code, is_sensitive=True)
        logger.info("2FA code copied to clipboard (will clear in 30s).")

    def stop_timer(self) -> None:
        """停止定时器，防止在小部件被销毁后继续运行。"""
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()

    def __del__(self) -> None:
        """确保在对象被销毁时停止定时器。"""
        self.stop_timer()
