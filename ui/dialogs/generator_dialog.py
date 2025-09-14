# ui/dialogs/generator_dialog.py

import secrets
import string
import logging
from typing import Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QSlider, QCheckBox,
                             QApplication, QFrame, QWidget)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent

from language import t

logger = logging.getLogger(__name__)

class GeneratorWindow(QDialog):
    SAFE_SYMBOLS: str = "!@#$%^&*()_+-=[]{}|'"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")
        self.setModal(True)
        self.setMinimumSize(450, 350)
        self.drag_pos: QPoint = QPoint()
        self.init_ui()
        self.generate_password()
        logger.debug("GeneratorWindow 打开。")

    def init_ui(self) -> None:
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        title_label = QLabel(t.get('gen_title'))
        title_label.setObjectName("dialogTitle")
        display_layout = QHBoxLayout()
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setObjectName("fieldValueDisplay")
        self.password_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(self.password_display)
        copy_button = QPushButton(t.get('button_copy'))
        copy_button.setObjectName("saveButton")
        copy_button.clicked.connect(self.copy_to_clipboard)
        display_layout.addWidget(copy_button)
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
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        done_button = QPushButton(t.get('button_done'))
        done_button.setObjectName("cancelButton")
        done_button.clicked.connect(self.accept)
        button_layout.addWidget(done_button)
        main_layout.addWidget(title_label)
        main_layout.addLayout(display_layout)
        main_layout.addLayout(options_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)
        self.update_options()

    def update_options(self) -> None:
        length = self.length_slider.value()
        self.length_label.setText(t.get('gen_label_len', length=length))
        self.generate_password()

    def generate_password(self) -> None:
        length = self.length_slider.value()
        chars = string.ascii_lowercase
        if self.uppercase_check.isChecked(): chars += string.ascii_uppercase
        if self.numbers_check.isChecked(): chars += string.digits
        if self.symbols_check.isChecked(): chars += self.SAFE_SYMBOLS
        if not chars:
            self.password_display.setText(t.get('gen_no_charset'))
            return
        password = "".join(secrets.choice(chars) for _ in range(length))
        self.password_display.setText(password)
        logger.debug(f"生成了新密码，长度: {length}, 大写: {self.uppercase_check.isChecked()}, 数字: {self.numbers_check.isChecked()}, 符号: {self.symbols_check.isChecked()}")

    def copy_to_clipboard(self) -> None:
        password = self.password_display.text()
        if password != t.get('gen_no_charset'):
            QApplication.clipboard().setText(password)
            logger.info("已将生成的密码复制到剪贴板。")

    def get_password(self) -> str:
        return self.password_display.text()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()