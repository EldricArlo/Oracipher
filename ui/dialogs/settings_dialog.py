# ui/dialogs/settings_dialog.py

import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QComboBox)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal

from language import t
from config import load_settings

logger = logging.getLogger(__name__)

class SettingsDialog(QDialog):
    """
    一个用于更改应用程序设置的自定义对话框。
    
    目前支持：
    - 更改界面语言。
    - 提供一个入口来触发“更改主密码”流程。

    Signals:
        change_password_requested: 当用户点击“更改主密码”按钮时发射此信号。
                                   主窗口 (MainWindow) 会监听这个信号来打开
                                   ChangePasswordDialog。
    """
    # 定义一个自定义信号。这是子窗口(对话框)与父窗口(主界面)通信的最佳实践之一。
    change_password_requested = pyqtSignal()

    def __init__(self, parent=None):
        """
        初始化设置对话框。

        Args:
            parent (QWidget, optional): 父控件。默认为 None。
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("AddEditDialog")  # 共享样式
        self.setModal(True)
        self.setMinimumSize(450, 250)
        self.drag_pos = QPoint()
        
        self.init_ui()
        logger.debug("SettingsDialog 打开。")

    def init_ui(self):
        """
        构建对话框的所有UI组件。
        """
        container = QFrame(self)
        container.setObjectName("dialogContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel(t.get('settings_title'))
        title_label.setObjectName("dialogTitle")
        
        # --- 设置项表单 ---
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setColumnStretch(1, 1) # 让第二列自动伸展

        # --- 语言选择 ---
        self.lang_combo = QComboBox()
        available_languages = t.get_available_languages()
        current_settings = load_settings()
        current_lang_code = current_settings.get('language', 'en')
        
        for code, name in available_languages.items():
            # addItem 可以存储一个显示名称和一个关联的用户数据 (这里是语言代码)
            self.lang_combo.addItem(name, userData=code)
            if code == current_lang_code:
                # 设置当前显示的项
                self.lang_combo.setCurrentText(name)

        form_layout.addWidget(QLabel(t.get('settings_lang_label')), 0, 0)
        form_layout.addWidget(self.lang_combo, 0, 1)

        # --- 更改主密码 ---
        change_pass_button = QPushButton(t.get('change_pass_title'))
        change_pass_button.setObjectName("inlineButton")
        # 将按钮的点击事件连接到自定义信号的发射
        change_pass_button.clicked.connect(self.change_password_requested.emit)
        
        form_layout.addWidget(QLabel(t.get('label_pass')), 1, 0)
        form_layout.addWidget(change_pass_button, 1, 1)

        # --- 对话框底部按钮 (取消/保存) ---
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
        
        # --- 组装布局 ---
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.addWidget(container)

    def get_selected_language(self) -> str:
        """
        获取用户在下拉框中选择的语言代码。

        Returns:
            str: 选中的语言代码 (例如 'en', 'zh_CN')。
        """
        # currentData() 返回与当前选中项关联的用户数据
        return self.lang_combo.currentData()

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