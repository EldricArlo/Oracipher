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

from language import t

logger = logging.getLogger(__name__)


class PasswordPromptDialog(QDialog):
    """
    一个自定义的、风格化的对话框，用于在导入加密文件时提示用户输入密码。
    """

    def __init__(
        self, parent: Optional[QWidget] = None, instruction_text: Optional[str] = None
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumWidth(420)
        
        # --- MODIFICATION START: 添加拖动状态标志 ---
        self.drag_pos: QPoint = QPoint()
        self._is_dragging = False
        # --- MODIFICATION END ---

        self.instruction_text = (
            instruction_text or "Please enter the required password:"
        )

        self.init_ui()
        logger.debug("PasswordPromptDialog opened.")

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        title_label = QLabel(t.get("dialog_input_password_title"))
        title_label.setObjectName("dialogTitle")

        instruction_label = QLabel(self.instruction_text)
        instruction_label.setWordWrap(True)

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

    # --- MODIFICATION START: 修复窗口拖动逻辑 ---
    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            # "dialogContainer" 是您在UI代码中设置的背景QFrame的objectName
            container = self.findChild(QFrame, "dialogContainer")
            child_at_click = self.childAt(event.position().toPoint())
            
            # 仅当点击发生在背景板本身（而不是其子控件上）时才开始拖动
            if not child_at_click or child_at_click == container:
                self.drag_pos = event.globalPosition().toPoint()
                self._is_dragging = True
                event.accept()
            else:
                self._is_dragging = False
                # 将事件传递给子控件处理
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mouseMoveEvent(event)
            return

        # 仅当拖动标志为True时才移动窗口
        if event.buttons() == Qt.MouseButton.LeftButton and self._is_dragging:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, a0: Optional[QMouseEvent]) -> None:
        """在鼠标按键松开时重置拖动标志。"""
        event = a0
        if not event:
            super().mouseReleaseEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    # --- MODIFICATION END ---

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