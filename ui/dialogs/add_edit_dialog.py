# ui/dialogs/add_edit_dialog.py

import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, QPoint

from language import t
from .generator_dialog import GeneratorWindow

logger = logging.getLogger(__name__)

class AddEditDialog(QDialog):
    """
    一个用于添加新条目或编辑现有条目的自定义对话框。

    该对话框具有无边框窗口样式，并支持鼠标拖动。
    它会根据是否在初始化时传入 `entry` 数据来自动调整标题和内容，
    从而在“添加模式”和“编辑模式”之间切换。
    """
    def __init__(self, parent=None, entry: dict = None):
        """
        初始化添加/编辑对话框。

        Args:
            parent (QWidget, optional): 父控件。默认为 None。
            entry (dict, optional): 如果是编辑模式，则传入要编辑的条目数据。
                                    如果为 None，则对话框处于添加模式。
        """
        super().__init__(parent)
        self.entry = entry
        
        # --- 窗口样式设置 ---
        # FramelessWindowHint: 移除标准的窗口标题栏和边框
        # WA_TranslucentBackground: 允许背景透明，以便QSS中的border-radius能创建圆角窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置 objectName 以便应用 QSS 样式。所有对话框共享此名称以统一外观。
        self.setObjectName("AddEditDialog")
        self.setModal(True) # 模态对话框，阻止与其他窗口交互
        self.setMinimumSize(450, 500)
        
        self.drag_pos = QPoint() # 用于窗口拖动
        
        self.init_ui()
        
        # 如果是编辑模式，则加载现有数据到输入框中
        if self.entry:
            self.load_entry_data()
            logger.debug(f"AddEditDialog 在 '编辑模式' 下打开，条目: {self.entry.get('name')}")
        else:
            logger.debug("AddEditDialog 在 '添加模式' 下打开。")


    def init_ui(self):
        """
        构建对话框的所有UI组件。
        """
        # --- 基础容器和主布局 ---
        # 所有内容都放在一个 QFrame (dialogContainer) 中，以便通过 QSS 统一设置背景和边框
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # --- 标题 ---
        title_text = t.get('edit_title') if self.entry else t.get('add_title')
        title_label = QLabel(title_text)
        title_label.setObjectName("dialogTitle")
        
        # --- 表单布局 ---
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # 输入字段
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t.get('placeholder_name'))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(t.get('placeholder_user'))
        
        # 密码输入行（包含输入框和两个按钮）
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(10)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        show_hide_button = QPushButton(t.get('button_show'))
        show_hide_button.setObjectName("inlineButton")
        show_hide_button.setCheckable(True)
        show_hide_button.toggled.connect(self._toggle_password_visibility)

        generate_button = QPushButton(t.get('button_generate'))
        generate_button.setObjectName("inlineButton")
        generate_button.clicked.connect(self._open_generator)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(show_hide_button)
        password_layout.addWidget(generate_button)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText(t.get('placeholder_cat'))
        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(80) # 初始高度

        # 将标签和输入字段添加到表单网格布局
        form_layout.addWidget(QLabel(t.get('label_name')), 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)
        form_layout.addWidget(QLabel(t.get('label_user')), 1, 0)
        form_layout.addWidget(self.username_input, 1, 1)
        form_layout.addWidget(QLabel(t.get('label_pass')), 2, 0)
        form_layout.addLayout(password_layout, 2, 1)
        form_layout.addWidget(QLabel(t.get('label_cat')), 3, 0)
        form_layout.addWidget(self.category_input, 3, 1)
        form_layout.addWidget(QLabel(t.get('label_notes')), 4, 0)
        form_layout.addWidget(self.notes_input, 4, 1)
        
        # --- 底部按钮 (取消/保存) ---
        button_layout = QHBoxLayout()
        button_layout.addStretch() # 弹簧，将按钮推到右侧
        
        self.cancel_button = QPushButton(t.get('button_cancel'))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject) # reject() 会关闭对话框并返回 QDialog.DialogCode.Rejected
        
        self.save_button = QPushButton(t.get('button_save'))
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.accept) # accept() 会关闭对话框并返回 QDialog.DialogCode.Accepted
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        # --- 组装主布局 ---
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch() # 弹簧，将按钮推到底部
        main_layout.addLayout(button_layout)
        
        # 最终将容器放入对话框自身的布局中
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)

    def _open_generator(self):
        """
        打开密码生成器对话框，并将生成的密码填入密码输入框。
        """
        gen_dialog = GeneratorWindow(self)
        if gen_dialog.exec():
            generated_password = gen_dialog.get_password()
            # 确保用户没有选择空的字符集
            if generated_password != t.get('gen_no_charset'):
                self.password_input.setText(generated_password)
                logger.debug("已使用生成器生成并填充了新密码。")

    def _toggle_password_visibility(self, checked: bool):
        """
        切换密码输入框的可见性（星号/明文）。

        Args:
            checked (bool): 按钮是否被选中。
        """
        button = self.sender()
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText(t.get('button_hide'))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText(t.get('button_show'))
    
    def load_entry_data(self):
        """
        如果是编辑模式，将传入的 `entry` 数据填充到UI控件中。
        """
        if not self.entry:
            return
        self.name_input.setText(self.entry.get("name", ""))
        self.category_input.setText(self.entry.get("category", ""))
        details = self.entry.get("details", {})
        self.username_input.setText(details.get("username", ""))
        self.password_input.setText(details.get("password", ""))
        self.notes_input.setText(details.get("notes", ""))

    def get_data(self) -> dict:
        """
        从UI控件中收集用户输入的数据，并以标准字典格式返回。

        Returns:
            dict: 包含所有条目信息的字典。
        """
        return {
            "category": self.category_input.text().strip(),
            "name": self.name_input.text().strip(),
            "details": {
                "username": self.username_input.text().strip(),
                "password": self.password_input.text(),
                "notes": self.notes_input.toPlainText().strip(),
            },
        }

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