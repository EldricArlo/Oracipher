# ui/unlock_screen.py

import logging
import string
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QApplication)
from PyQt6.QtCore import (Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, 
                          QRect, QRectF, QPointF)

from core.crypto import CryptoHandler
from ui.dialogs.message_box_dialog import CustomMessageBox
from language import t

logger = logging.getLogger(__name__)

class ShakeAnimation:
    """
    一个简单的动画类，用于实现窗口左右“抖动”的效果。

    常用于在用户输入错误（如密码错误）时提供视觉反馈。
    它通过动画化 widget 的 'geometry' 属性来实现。
    """
    def __init__(self, widget: QWidget):
        """
        初始化抖动动画。

        Args:
            widget (QWidget): 要应用抖动效果的控件。
        """
        self.widget = widget
        self.animation = QPropertyAnimation(widget, b"geometry")
        self.animation.setDuration(500)  # 动画总时长
        self.animation.setEasingCurve(QEasingCurve.Type.InOutBounce) # 缓动曲线，增加弹性效果
    
    def start(self):
        """
        开始播放抖动动画。
        """
        original_rect = self.widget.geometry()
        self.animation.setStartValue(original_rect)
        
        # 定义一系列关键帧来模拟抖动
        # (时间点, 几何位置)
        keyframes = [
            (0.1, QRect(original_rect.x() - 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.2, QRect(original_rect.x() + 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.3, QRect(original_rect.x() - 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.4, QRect(original_rect.x() + 10, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.5, QRect(original_rect.x() - 5, original_rect.y(), original_rect.width(), original_rect.height())),
            (0.6, QRect(original_rect.x() + 5, original_rect.y(), original_rect.width(), original_rect.height())),
            (1.0, original_rect), # 动画结束时回到原始位置
        ]
        
        for time, rect in keyframes: 
            self.animation.setKeyValueAt(time, rect)
            
        self.animation.start()


class UnlockScreen(QWidget):
    """
    应用程序的解锁/初始设置界面。

    这个界面有两种模式：
    1. 设置模式 (Setup Mode): 当应用程序首次运行时，引导用户创建主密码。
    2. 解锁模式 (Unlock Mode): 在后续运行中，要求用户输入主密码以解锁保险库。

    Signals:
        unlocked: 当用户成功解锁时发射此信号。
    """
    unlocked = pyqtSignal()
    
    def __init__(self, crypto_handler: CryptoHandler, parent_window: QWidget):
        """
        初始化解锁屏幕。

        Args:
            crypto_handler (CryptoHandler): 加密处理器实例。
            parent_window (QWidget): 父窗口，用于抖动动画。
        """
        super().__init__()
        self.crypto_handler = crypto_handler
        # 通过检查密钥是否已设置来决定当前是设置模式还是解锁模式
        self.is_setup_mode = not self.crypto_handler.is_key_setup()
        
        self.setObjectName("UnlockScreen")
        self.shake_animation = ShakeAnimation(parent_window)
        
        self.init_ui()
        logger.info(f"解锁屏幕初始化完成。当前模式: {'设置模式' if self.is_setup_mode else '解锁模式'}")

    def init_ui(self):
        """
        构建界面的所有UI组件。
        """
        # --- 布局结构 ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 内容容器，限制最大宽度以适应不同窗口大小
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_widget.setMaximumWidth(400)
        content_layout.setContentsMargins(50, 50, 50, 50)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        outer_layout.addWidget(content_widget)
        
        # --- UI组件 ---
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
        
        # --- 将组件添加到布局 ---
        content_layout.addWidget(self.logo_label)
        content_layout.addWidget(self.welcome_label)
        content_layout.addWidget(self.instruction_label)
        content_layout.addWidget(self.password_input)
        content_layout.addWidget(self.confirm_password_input)
        content_layout.addWidget(self.action_button)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.exit_button)
        
        # --- 初始化文本和可见性 ---
        self.retranslate_ui()
        self.update_ui_for_mode()
        
    def retranslate_ui(self):
        """
        应用文本翻译到所有UI元素。
        此方法在语言更改后可以被调用以刷新界面。
        """
        self.logo_label.setText(t.get('app_title'))
        self.exit_button.setText(t.get('button_exit'))
        # 重新调用 update_ui_for_mode 来处理依赖于模式的文本
        self.update_ui_for_mode()

    def update_ui_for_mode(self):
        """
        根据当前是“设置模式”还是“解锁模式”来更新UI。
        """
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
        """
        检查密码是否满足预设的强度要求。

        Args:
            password (str): 要检查的密码。

        Returns:
            bool: 如果密码强度足够，返回 True，否则返回 False。
        """
        if len(password) < 8: return False
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        return has_lower and has_upper and has_digit

    def process_password(self):
        """
        处理用户输入的密码。
        根据当前模式，执行设置或解锁操作。
        """
        password = self.password_input.text()
        
        if self.is_setup_mode:
            # --- 设置模式逻辑 ---
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
            
            # 密码验证通过，设置主密码
            self.crypto_handler.set_master_password(password)
            CustomMessageBox.information(self, t.get('setup_success_title'), t.get('setup_success_msg'))
            
            # 转换到解锁模式
            logger.info("新保险库创建成功，界面切换到解锁模式。")
            self.is_setup_mode = False
            self.password_input.clear()
            self.confirm_password_input.clear()
            self.update_ui_for_mode()
        else:
            # --- 解锁模式逻辑 ---
            if self.crypto_handler.unlock_with_master_password(password):
                self.unlocked.emit()
            else:
                # 日志记录已在 crypto_handler 中完成
                self.password_input.selectAll()
                self.shake_animation.start()
                CustomMessageBox.information(self, t.get('error_title_generic'), t.get('error_msg_wrong_password'))