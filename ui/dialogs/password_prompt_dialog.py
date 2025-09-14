# ui/dialogs/password_prompt_dialog.py

import logging
from typing import Optional, Tuple

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
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

# 修正：导入项目全局的翻译单例
from language import t

logger = logging.getLogger(__name__)


class PasswordPromptDialog(QDialog):
    """
    一个自定义的、风格化的对话框，用于在导入加密文件时提示用户输入密码。
    """

    # --- MODIFICATION START: Updated __init__ to accept instruction_text ---
    def __init__(
        self, parent: Optional[QWidget] = None, instruction_text: Optional[str] = None
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.drag_pos: QPoint = QPoint()

        # 使用传入的 instruction_text，如果未提供，则使用一个通用的后备文本
        self.instruction_text = (
            instruction_text or "Please enter the required password:"
        )

        self.init_ui()
        logger.debug("PasswordPromptDialog opened.")

    # --- MODIFICATION END ---

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        title_label = QLabel(t.get("dialog_input_password_title"))
        title_label.setObjectName("dialogTitle")

        # --- MODIFICATION START: Use the dynamic instruction text ---
        instruction_label = QLabel(self.instruction_text)
        instruction_label.setWordWrap(True)
        # --- MODIFICATION END ---

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton(t.get("button_cancel"))
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        ok_button = QPushButton(t.get("button_ok"))
        ok_button.setObjectName("saveButton")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        main_layout.addWidget(title_label)
        main_layout.addWidget(instruction_label)
        main_layout.addWidget(self.password_input)
        main_layout.addLayout(button_layout)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        self.adjustSize()

    def get_password(self) -> str:
        """返回用户输入的密码。"""
        return self.password_input.text()

    # --- FIX START: Updated type hint to Optional[QMouseEvent] to match the base class ---
    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        if a0 and a0.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        if a0 and a0.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + a0.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = a0.globalPosition().toPoint()
            a0.accept()

    # --- FIX END ---

    # --- MODIFICATION START: Updated getPassword to pass instruction_text ---
    @staticmethod
    def getPassword(
        parent: Optional[QWidget], instruction_text: str
    ) -> Tuple[str, bool]:
        """
        一个静态方法，模仿 QInputDialog.getText 的用法。
        返回 (密码, 是否点击了OK)。
        """
        dialog = PasswordPromptDialog(parent, instruction_text=instruction_text)
        result = dialog.exec()
        password = dialog.get_password()
        return password, result == QDialog.DialogCode.Accepted

    # --- MODIFICATION END ---