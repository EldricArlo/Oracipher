# ui/dialogs/message_box_dialog.py

import logging
from enum import Enum

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, QPoint

from language import t

logger = logging.getLogger(__name__)

class CustomMessageBox(QDialog):
    """
    一个自定义的、与应用整体风格一致的消息框。

    取代 PyQt 内置的 QMessageBox，以实现完全的视觉统一。
    提供了两种类型的对话框：
    - `Information`: 只显示一个 "OK" 按钮。
    - `Question`: 显示 "OK" 和 "Cancel" 按钮。

    通过静态方法 `information()` 和 `question()` 来方便地调用。
    """
    class DialogType(Enum):
        """定义消息框的类型。"""
        Information = 1
        Question = 2

    def __init__(self, parent, dialog_type: DialogType, title: str, message: str):
        """
        初始化自定义消息框。

        Args:
            parent (QWidget): 父控件。
            dialog_type (DialogType): 对话框类型 (Information 或 Question)。
            title (str): 对话框的标题。
            message (str): 要显示的消息文本。
        """
        super().__init__(parent)
        self.dialog_type = dialog_type
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")  # 共享样式
        self.setModal(True)
        self.setMinimumWidth(380)
        self.drag_pos = QPoint()
        
        self.init_ui(title, message)
        
        log_type = "Question" if dialog_type == self.DialogType.Question else "Information"
        logger.debug(f"显示 CustomMessageBox ({log_type}): Title='{title}', Message='{message}'")
        
    def init_ui(self, title: str, message: str):
        """
        构建对话框的所有UI组件。

        Args:
            title (str): 对话框标题。
            message (str): 对话框消息。
        """
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # --- 文本内容 ---
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        message_label = QLabel(message)
        message_label.setWordWrap(True) # 确保长消息能自动换行
        
        # --- 按钮 ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 如果是 "Question" 类型，添加 "Cancel" 按钮
        if self.dialog_type == self.DialogType.Question:
            cancel_button = QPushButton(t.get('button_cancel'))
            cancel_button.setObjectName("cancelButton")
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)

        # 所有类型都有 "OK" 按钮
        ok_button = QPushButton(t.get('button_ok'))
        ok_button.setObjectName("saveButton") # 沿用 "save" 按钮的醒目样式
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        # --- 组装布局 ---
        main_layout.addWidget(title_label)
        main_layout.addWidget(message_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(button_layout)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        
        # 自动调整对话框大小以适应内容
        self.adjustSize()

    @staticmethod
    def information(parent, title: str, message: str) -> QDialog.DialogCode:
        """
        显示一个模态的“信息”类型对话框。

        Args:
            parent (QWidget): 父控件。
            title (str): 对话框标题。
            message (str): 对话框消息。

        Returns:
            QDialog.DialogCode: 总是返回 Accepted，因为只有一个OK按钮。
        """
        dialog = CustomMessageBox(parent, CustomMessageBox.DialogType.Information, title, message)
        return dialog.exec()

    @staticmethod
    def question(parent, title: str, message: str) -> QDialog.DialogCode:
        """
        显示一个模态的“问题”类型对话框。

        Args:
            parent (QWidget): 父控件。
            title (str): 对话框标题。
            message (str): 对话框消息。

        Returns:
            QDialog.DialogCode: 如果用户点击OK，返回 Accepted；如果点击Cancel，返回 Rejected。
        """
        dialog = CustomMessageBox(parent, CustomMessageBox.DialogType.Question, title, message)
        return dialog.exec()
        
    # --- 窗口拖动事件处理 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()