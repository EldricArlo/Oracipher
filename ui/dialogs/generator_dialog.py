# ui/dialogs/generator_dialog.py

import secrets
import string
import logging

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QSlider, QCheckBox,
                             QApplication, QFrame)
from PyQt6.QtCore import Qt, QPoint

from language import t

logger = logging.getLogger(__name__)

class GeneratorWindow(QDialog):
    """
    一个用于生成强随机密码的自定义对话框。
    
    允许用户自定义密码长度和包含的字符集（大写、数字、符号）。
    """
    # 定义一个安全的、不易混淆的符号集
    SAFE_SYMBOLS = "!@#$%^&*()_+-=[]{}|'"

    def __init__(self, parent=None):
        """
        初始化密码生成器窗口。

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
        # 窗口一显示就立即生成一个默认密码
        self.generate_password()
        logger.debug("GeneratorWindow 打开。")

    def init_ui(self):
        """
        构建对话框的所有UI组件。
        """
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel(t.get('gen_title'))
        title_label.setObjectName("dialogTitle")

        # --- 密码显示和复制区域 ---
        display_layout = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setObjectName("fieldValueDisplay")
        self.password_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(self.password_display)
        
        copy_button = QPushButton(t.get('button_copy'))
        copy_button.setObjectName("saveButton") # 沿用 "save" 按钮的醒目样式
        copy_button.clicked.connect(self.copy_to_clipboard)
        display_layout.addWidget(copy_button)

        # --- 密码选项区域 ---
        options_layout = QGridLayout()
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(8, 64)
        self.length_slider.setValue(16)
        self.length_label = QLabel()
        self.length_slider.valueChanged.connect(self.update_options)
        
        self.uppercase_check = QCheckBox(t.get('gen_check_upper'))
        self.uppercase_check.setChecked(True)
        self.uppercase_check.stateChanged.connect(self.generate_password)
        
        self.numbers_check = QCheckBox(t.get('gen_check_num'))
        self.numbers_check.setChecked(True)
        self.numbers_check.stateChanged.connect(self.generate_password)
        
        self.symbols_check = QCheckBox(t.get('gen_check_sym'))
        self.symbols_check.setChecked(True)
        self.symbols_check.stateChanged.connect(self.generate_password)
        
        options_layout.addWidget(self.length_label, 0, 0)
        options_layout.addWidget(self.length_slider, 0, 1)
        options_layout.addWidget(self.uppercase_check, 1, 0, 1, 2)
        options_layout.addWidget(self.numbers_check, 2, 0, 1, 2)
        options_layout.addWidget(self.symbols_check, 3, 0, 1, 2)

        # --- 底部按钮 ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        done_button = QPushButton(t.get('button_done'))
        done_button.setObjectName("cancelButton")
        done_button.clicked.connect(self.accept)
        button_layout.addWidget(done_button)
        
        # --- 组装布局 ---
        main_layout.addWidget(title_label)
        main_layout.addLayout(display_layout)
        main_layout.addLayout(options_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        
        # 初始化长度标签的文本
        self.update_options()

    def update_options(self):
        """
        当滑块值改变时，更新长度标签并重新生成密码。
        """
        length = self.length_slider.value()
        self.length_label.setText(t.get('gen_label_len', length=length))
        self.generate_password()

    def generate_password(self):
        """
        根据当前选项生成一个新的随机密码。
        """
        length = self.length_slider.value()
        chars = string.ascii_lowercase
        
        if self.uppercase_check.isChecked(): chars += string.ascii_uppercase
        if self.numbers_check.isChecked(): chars += string.digits
        if self.symbols_check.isChecked(): chars += self.SAFE_SYMBOLS
        
        # 如果用户取消了所有字符集，则显示提示信息
        if not chars:
            self.password_display.setText(t.get('gen_no_charset'))
            return
            
        # 使用 secrets 模块生成加密安全的随机密码
        password = "".join(secrets.choice(chars) for _ in range(length))
        self.password_display.setText(password)
        logger.debug(f"生成了新密码，长度: {length}, "
                     f"大写: {self.uppercase_check.isChecked()}, "
                     f"数字: {self.numbers_check.isChecked()}, "
                     f"符号: {self.symbols_check.isChecked()}")


    def copy_to_clipboard(self):
        """
        将生成的密码复制到系统剪贴板。
        """
        password = self.password_display.text()
        if password != t.get('gen_no_charset'):
            QApplication.clipboard().setText(password)
            logger.info("已将生成的密码复制到剪贴板。")

    def get_password(self) -> str:
        """
        获取当前显示的密码。

        Returns:
            str: 密码显示框中的文本。
        """
        return self.password_display.text()

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