# ui/dialogs/change_password_dialog.py

import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QPoint

from language import t

logger = logging.getLogger(__name__)

class ChangePasswordDialog(QDialog):
    """
    一个用于更改主密码的自定义对话框。
    
    提供输入旧密码、新密码和确认新密码的字段。
    """
    def __init__(self, parent=None):
        """
        初始化更改密码对话框。

        Args:
            parent (QWidget, optional): 父控件。默认为 None。
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")  # 共享样式
        self.setModal(True)
        self.setMinimumSize(450, 350)
        self.drag_pos = QPoint()
        
        self.init_ui()
        logger.debug("ChangePasswordDialog 打开。")

    def init_ui(self):
        """
        构建对话框的所有UI组件。
        """
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel(t.get('change_pass_title'))
        title_label.setObjectName("dialogTitle")
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        self.old_pass_input = QLineEdit()
        self.old_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_pass_input.setPlaceholderText(t.get('placeholder_old_pass'))

        self.new_pass_input = QLineEdit()
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setPlaceholderText(t.get('placeholder_new_pass'))

        self.confirm_pass_input = QLineEdit()
        self.confirm_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pass_input.setPlaceholderText(t.get('placeholder_confirm_pass'))

        form_layout.addWidget(QLabel(t.get('label_old_pass')), 0, 0)
        form_layout.addWidget(self.old_pass_input, 0, 1)
        form_layout.addWidget(QLabel(t.get('label_new_pass')), 1, 0)
        form_layout.addWidget(self.new_pass_input, 1, 1)
        form_layout.addWidget(QLabel(t.get('label_confirm_pass')), 2, 0)
        form_layout.addWidget(self.confirm_pass_input, 2, 1)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton(t.get('button_cancel'))
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)
        
        save_button = QPushButton(t.get('button_save'))
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

    def get_passwords(self) -> tuple[tuple[str, str] | None, str | None]:
        """
        获取并验证用户输入的密码。

        Returns:
            tuple: 一个包含两个元素的元组:
                   - 第一个元素: 如果输入有效，则为 (old_password, new_password) 的元组；否则为 None。
                   - 第二个元素: 如果输入无效，则为描述原因的字符串 ("empty" 或 "mismatch")；否则为 None。
        """
        old_pass = self.old_pass_input.text()
        new_pass = self.new_pass_input.text()
        confirm_pass = self.confirm_pass_input.text()
        
        if not all([old_pass, new_pass, confirm_pass]):
            return None, "empty"
        if new_pass != confirm_pass:
            return None, "mismatch"
            
        return (old_pass, new_pass), None

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