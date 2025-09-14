# ui/unlock_screen.py

import logging
import string
from typing import Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QApplication)
from PyQt6.QtCore import (Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, 
                          QRect)
from PyQt6.QtGui import QMouseEvent

from core.crypto import CryptoHandler
from ui.dialogs.message_box_dialog import CustomMessageBox
from language import t

logger = logging.getLogger(__name__)

class ShakeAnimation:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.animation = QPropertyAnimation(widget, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutBounce)
    
    def start(self) -> None:
        original_rect = self.widget.geometry()
        self.animation.setStartValue(original_rect)
        keyframes = [
            (0.1, QRect(original_rect.x() - 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.2, QRect(original_rect.x() + 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.3, QRect(original_rect.x() - 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.4, QRect(original_rect.x() + 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.5, QRect(original_rect.x() - 5, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.6, QRect(original_rect.x() + 5, original_rect.y(), original_rect.width(), original_rect.height())),
            (1.0, original_rect),
        ]
        for time, rect in keyframes: 
            self.animation.setKeyValueAt(time, rect)
        self.animation.start()


class UnlockScreen(QWidget):
    unlocked = pyqtSignal()
    
    def __init__(self, crypto_handler: CryptoHandler, parent_window: QWidget):
        super().__init__()
        self.crypto_handler: CryptoHandler = crypto_handler
        self.is_setup_mode: bool = not self.crypto_handler.is_key_setup()
        self.setObjectName("UnlockScreen")
        self.shake_animation: ShakeAnimation = ShakeAnimation(parent_window)
        self.init_ui()
        logger.info(f"解锁屏幕初始化完成。当前模式: {'设置模式' if self.is_setup_mode else '解锁模式'}")

    def init_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_widget.setMaximumWidth(400)
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(content_widget)
        
        self.logo_label = QLabel()
        self.logo_label.setObjectName("logoLabel")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label = QLabel()
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label = QLabel()
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setWordWrap(True)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.process_password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.returnPressed.connect(self.process_password)
        self.action_button = QPushButton()
        self.action_button.setObjectName("mainActionButton")
        self.action_button.clicked.connect(self.process_password)
        self.exit_button = QPushButton()
        self.exit_button.setObjectName("unlockExitButton") 
        self.exit_button.clicked.connect(QApplication.instance().quit)
        
        content_layout.addWidget(self.logo_label)
        content_layout.addWidget(self.welcome_label)
        content_layout.addWidget(self.instruction_label)
        content_layout.addWidget(self.password_input)
        content_layout.addWidget(self.confirm_password_input)
        content_layout.addWidget(self.action_button)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.exit_button)
        
        self.retranslate_ui()
        self.update_ui_for_mode()
        
    def retranslate_ui(self) -> None:
        self.logo_label.setText(t.get('app_title'))
        self.exit_button.setText(t.get('button_exit'))
        self.update_ui_for_mode()

    def update_ui_for_mode(self) -> None:
        if self.is_setup_mode:
            self.welcome_label.setText(t.get('setup_welcome'))
            self.instruction_label.setText(t.get('setup_instruction'))
            self.instruction_label.setVisible(True)
            self.password_input.setPlaceholderText(t.get('setup_placeholder'))
            self.confirm_password_input.setPlaceholderText(t.get('setup_confirm_placeholder'))
            self.confirm_password_input.setVisible(True)
            self.action_button.setText(t.get('setup_button'))
        else:
            self.welcome_label.setText(t.get('unlock_welcome'))
            self.instruction_label.setVisible(False)
            self.password_input.setPlaceholderText(t.get('unlock_placeholder'))
            self.confirm_password_input.setVisible(False)
            self.action_button.setText(t.get('unlock_button'))

    def _is_password_strong(self, password: str) -> bool:
        if len(password) < 8: return False
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        return has_lower and has_upper and has_digit

    def process_password(self) -> None:
        password = self.password_input.text()
        if self.is_setup_mode:
            confirm_password = self.confirm_password_input.text()
            if not self._is_password_strong(password):
                logger.warning("用户尝试设置一个弱密码。")
                CustomMessageBox.information(self, t.get('error_title_weak_password'), t.get('error_msg_weak_password'))
                self.shake_animation.start()
                return
            if password != confirm_password:
                logger.warning("用户在设置密码时两次输入不匹配。")
                CustomMessageBox.information(self, t.get('error_title_mismatch'), t.get('error_msg_mismatch'))
                self.shake_animation.start()
                return
            self.crypto_handler.set_master_password(password)
            CustomMessageBox.information(self, t.get('setup_success_title'), t.get('setup_success_msg'))
            logger.info("新保险库创建成功，界面切换到解锁模式。")
            self.is_setup_mode = False
            self.password_input.clear()
            self.confirm_password_input.clear()
            self.update_ui_for_mode()
        else:
            if self.crypto_handler.unlock_with_master_password(password):
                self.unlocked.emit()
            else:
                self.password_input.selectAll()
                self.shake_animation.start()
                CustomMessageBox.information(self, t.get('error_title_generic'), t.get('error_msg_wrong_password'))