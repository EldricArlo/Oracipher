# ui/dialogs/password_prompt_dialog.py

import logging
from typing import Optional, Tuple

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

from language import t

logger = logging.getLogger(__name__)

class PasswordPromptDialog(QDialog):
    """
    一个自定义的、风格化的对话框，用于在导入.skey文件时提示用户输入密码。
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog") # 复用现有样式
        self.setModal(True)
        self.setMinimumWidth(420)
        self.drag_pos: QPoint = QPoint()
        
        self.init_ui()
        logger.debug("PasswordPromptDialog opened for .skey import.")

    def init_ui(self) -> None:
        container = QFrame(self); container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)

        title_label = QLabel(t.get('dialog_input_password_title')); title_label.setObjectName("dialogTitle")
        instruction_label = QLabel(t.get('dialog_input_password_label')); instruction_label.setWordWrap(True)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.accept)
        
        button_layout = QHBoxLayout(); button_layout.addStretch()
        cancel_button = QPushButton(t.get('button_cancel')); cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        ok_button = QPushButton(t.get('button_ok')); ok_button.setObjectName("saveButton")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button); button_layout.addWidget(ok_button)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(instruction_label)
        main_layout.addWidget(self.password_input)
        main_layout.addLayout(button_layout)
        
        dialog_layout = QVBoxLayout(self); dialog_layout.addWidget(container)
        self.adjustSize()

    def get_password(self) -> str:
        """返回用户输入的密码。"""
        return self.password_input.text()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    @staticmethod
    def getPassword(parent: Optional[QWidget]) -> Tuple[str, bool]:
        """
        一个静态方法，模仿 QInputDialog.getText 的用法。
        返回 (密码, 是否点击了OK)。
        """
        dialog = PasswordPromptDialog(parent)
        result = dialog.exec()
        password = dialog.get_password()
        return password, result == QDialog.DialogCode.Accepted