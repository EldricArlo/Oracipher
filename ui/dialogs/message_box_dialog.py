# ui/dialogs/message_box_dialog.py

import logging
from enum import Enum
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

from language import t

logger = logging.getLogger(__name__)


class CustomMessageBox(QDialog):
    """
    一个自定义的消息框对话框，以匹配应用的整体UI风格。
    提供了 `information` 和 `question` 两种静态方法，以模仿 QMessageBox 的用法。
    """

    class DialogType(Enum):
        Information = 1
        Question = 2

    def __init__(
        self,
        parent: Optional[QWidget],
        dialog_type: DialogType,
        title: str,
        message: str,
    ):
        super().__init__(parent)
        self.dialog_type = dialog_type
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 尽管 objectName 是 "AddEditDialog"，但容器 QFrame 的名称是 "dialogContainer"，这才是关键
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumWidth(380)
        
        # --- MODIFICATION START: 初始化拖动状态标志 ---
        self.drag_pos: QPoint = QPoint()
        self._is_dragging = False
        # --- MODIFICATION END ---

        self.init_ui(title, message)
        log_type = (
            "Question" if dialog_type == self.DialogType.Question else "Information"
        )
        logger.debug(f"Displaying CustomMessageBox ({log_type}): Title='{title}'")

    def init_ui(self, title: str, message: str) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        message_label = QLabel(message)
        message_label.setWordWrap(True)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if self.dialog_type == self.DialogType.Question:
            cancel_button = QPushButton(t.get("button_cancel"))
            cancel_button.setObjectName("cancelButton")
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)

        ok_button = QPushButton(t.get("button_ok"))
        ok_button.setObjectName("saveButton")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        main_layout.addWidget(title_label)
        main_layout.addWidget(message_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)

        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        self.adjustSize()

    @staticmethod
    def information(parent: Optional[QWidget], title: str, message: str) -> int:
        """显示一个信息对话框 (只有一个“确定”按钮)。"""
        dialog = CustomMessageBox(
            parent, CustomMessageBox.DialogType.Information, title, message
        )
        return dialog.exec()

    @staticmethod
    def question(parent: Optional[QWidget], title: str, message: str) -> int:
        """显示一个问题对话框 (“确定”和“取消”按钮)。"""
        dialog = CustomMessageBox(
            parent, CustomMessageBox.DialogType.Question, title, message
        )
        return dialog.exec()

    # --- MODIFICATION START: 修复窗口拖动逻辑 ---
    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            container = self.findChild(QFrame, "dialogContainer")
            child_at_click = self.childAt(event.position().toPoint())
            
            # 只有当点击发生在背景板上，而不是按钮等子控件上时，才启动拖动
            if not child_at_click or child_at_click == container:
                self.drag_pos = event.globalPosition().toPoint()
                self._is_dragging = True
                event.accept()
            else:
                self._is_dragging = False
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        event = a0
        if not event:
            super().mouseMoveEvent(event)
            return

        # 移动窗口前必须检查 _is_dragging 标志
        if event.buttons() == Qt.MouseButton.LeftButton and self._is_dragging:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, a0: Optional[QMouseEvent]) -> None:
        """新增此方法以在鼠标释放时重置拖动状态。"""
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