# ui/dialogs/enter_secret_dialog.py

import logging
from typing import Optional
import base64

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QWidget,
)
from PyQt6.QtCore import Qt

from language import t
from .message_box_dialog import CustomMessageBox

logger = logging.getLogger(__name__)


class EnterSecretDialog(QDialog):
    """
    一个简单的对话框，用于让用户输入从外部服务获取的TOTP密钥。
    它会对输入的密钥进行基本的Base32格式验证。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.secret_key: Optional[str] = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumWidth(420)

        self.init_ui()
        logger.debug("EnterSecretDialog opened.")

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        title_label = QLabel(t.get("2fa_enter_secret_title"))
        title_label.setObjectName("dialogTitle")
        instruction_label = QLabel(t.get("2fa_enter_secret_instructions"))
        instruction_label.setWordWrap(True)

        self.secret_input = QLineEdit()
        self.secret_input.setPlaceholderText(t.get("2fa_enter_secret_placeholder"))

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton(t.get("button_cancel"))
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        ok_button = QPushButton(t.get("button_ok"))
        ok_button.setObjectName("saveButton")
        ok_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        main_layout.addWidget(title_label)
        main_layout.addWidget(instruction_label)
        main_layout.addWidget(self.secret_input)
        main_layout.addLayout(button_layout)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        self.adjustSize()

    def validate_and_accept(self) -> None:
        """验证输入的密钥是否为有效的Base32格式，然后接受对话框。"""
        key = self.secret_input.text().strip().replace(" ", "").upper()

        if not key:
            self.reject()
            return

        try:
            padding = "=" * (-len(key) % 8)
            base64.b32decode(key + padding)
            self.secret_key = key
            self.accept()
        except (ValueError, TypeError):
            logger.warning(f"Invalid Base32 secret key entered by user: {key}")
            CustomMessageBox.information(
                self, t.get("error_title_generic"), t.get("2fa_error_invalid_key")
            )

    def get_secret(self) -> Optional[str]:
        """返回经过验证和清理的TOTP密钥。"""
        return self.secret_key
