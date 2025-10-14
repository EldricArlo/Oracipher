# ui/dialogs/change_password_dialog.py

import logging
from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGridLayout,
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


class ChangePasswordDialog(QDialog):
    """
    一个用于更改主密码的专用对话框。
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(450, 350)
        
        # --- 修改部分 ---
        self.drag_pos: QPoint = QPoint()
        self._is_dragging: bool = False  # 新增状态标志
        # --- 修改结束 ---

        self.init_ui()
        logger.debug("ChangePasswordDialog opened.")

    def init_ui(self) -> None:
        container = QFrame(self)
        # 确保容器有 objectName，以便在 mousePressEvent 中查找
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel(t.get("change_pass_title"))
        title_label.setObjectName("dialogTitle")

        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        self.old_pass_input = QLineEdit()
        self.old_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_pass_input.setPlaceholderText(t.get("placeholder_old_pass"))
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setPlaceholderText(t.get("placeholder_new_pass"))
        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setPlaceholderText(t.get("placeholder_confirm_pass"))

        form_layout.addWidget(QLabel(t.get("label_old_pass")), 0, 0)
        form_layout.addWidget(self.old_pass_input, 0, 1)
        form_layout.addWidget(QLabel(t.get("label_new_pass")), 1, 0)
        form_layout.addWidget(self.new_pass_input, 1, 1)
        form_layout.addWidget(QLabel(t.get("label_confirm_pass")), 2, 0)
        form_layout.addWidget(self.confirm_pass_input, 2, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton(t.get("button_cancel"))
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton(t.get("button_save"))
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)

    def _is_password_strong(self, password: str) -> bool:
        """Checks if the password meets the required strength criteria."""
        return (
            len(password) >= 8
            and any(c.isupper() for c in password)
            and any(c.islower() for c in password)
            and any(c.isdigit() for c in password)
        )

    def get_passwords(self) -> Tuple[Optional[Tuple[str, str]], Optional[str]]:
        """
        获取并验证用户输入的密码。
        """
        old_pass = self.old_pass_input.text()
        new_pass = self.new_pass_input.text()
        confirm_pass = self.confirm_pass_input.text()

        if not all([old_pass, new_pass, confirm_pass]):
            return None, "empty"
        if new_pass != confirm_pass:
            return None, "mismatch"
        if not self._is_password_strong(new_pass):
            return None, "weak"

        return (old_pass, new_pass), None

    # --- vvv 完整修改的拖动事件处理 vvv ---

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            # 查找背景容器
            container = self.findChild(QFrame, "dialogContainer")
            # 获取点击位置的子控件
            child_at_click = self.childAt(event.position().toPoint())

            # 只有当点击发生在背景上时，才启动拖动模式
            if not child_at_click or child_at_click == container:
                self.drag_pos = event.globalPosition().toPoint()
                self._is_dragging = True
                event.accept()
            else:
                self._is_dragging = False
                # 将事件传递给子控件
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mouseMoveEvent(event)
            return

        # 移动窗口前，必须检查拖动标志
        if event.buttons() == Qt.MouseButton.LeftButton and self._is_dragging:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mouseReleaseEvent(event)
            return

        # 鼠标松开时，重置拖动标志
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # --- ^^^ 完整修改的拖动事件处理 ^^^ ---