# app.py

import logging
from typing import Optional

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget, QFrame, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent
from PyQt6.QtGui import QMouseEvent, QCloseEvent

from config import APP_DATA_DIR, load_settings
from core.crypto import CryptoHandler
from core.database import DataManager
from language import t
from ui.theme_manager import apply_theme, get_current_theme
from ui.unlock_screen import UnlockScreen
from ui.main_window import MainWindow
from ui.task_manager import task_manager

logger = logging.getLogger(__name__)

class SafeKeyApp(QMainWindow):
    """
    应用程序的主窗口容器。
    它管理解锁屏幕和主界面之间的切换。
    """
    def __init__(self):
        super().__init__()
        logger.info("Initializing SafeKeyApp main window container...")
        
        self.setWindowTitle(t.get('app_title'))
        self.resize(1000, 700)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.drag_pos: QPoint = QPoint()
        self._is_shutting_down = False
        
        # 新增: 自动锁定功能相关属性
        self.auto_lock_timer = QTimer(self)
        self.auto_lock_timer.setSingleShot(True)
        self.auto_lock_timer.timeout.connect(self.lock_vault)
        self._auto_lock_enabled = False
        self._auto_lock_timeout_ms = 0
        
        logger.info(f"Application data directory: {APP_DATA_DIR}")
        self.crypto_handler: CryptoHandler = CryptoHandler(APP_DATA_DIR)
        self.data_manager: DataManager = DataManager(APP_DATA_DIR, self.crypto_handler)
        
        app_instance = QApplication.instance()
        if app_instance:
            apply_theme(app_instance, get_current_theme())
            app_instance.installEventFilter(self) # 新增: 安装事件过滤器以监测用户活动
        
        self.init_ui()
        self.center_on_screen()
        
        logger.info("SafeKeyApp main window initialization complete.")

    def init_ui(self) -> None:
        background_panel = QFrame(self); background_panel.setObjectName("backgroundPanel")
        self.setCentralWidget(background_panel)
        
        panel_layout = QVBoxLayout(background_panel); panel_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget(); panel_layout.addWidget(self.stacked_widget)
        
        self.unlock_screen = UnlockScreen(self.crypto_handler, self)
        self.unlock_screen.unlocked.connect(self.show_main_app)
        self.unlock_screen.exit_requested.connect(self.close) # 修改: 使用信号/槽解耦
        self.stacked_widget.addWidget(self.unlock_screen)
        
        self.main_widget: Optional[MainWindow] = None

    def show_main_app(self) -> None:
        logger.info("Unlock successful. Switching to the main application view.")
        if not self.main_widget:
            logger.info("Instantiating MainWindow for the first time...")
            self.main_widget = MainWindow(data_manager=self.data_manager, main_app_window=self)
            self.main_widget.controller.settings_changed.connect(self._on_settings_changed) # 新增
            self.stacked_widget.addWidget(self.main_widget)
        
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self._setup_auto_lock() # 新增: 解锁后启动自动锁定计时器
        logger.info("View switched to MainWindow.")

    # 新增: 锁定保险库的方法
    def lock_vault(self) -> None:
        """ 锁定保险库，返回到解锁界面并清除敏感数据。"""
        if self.stacked_widget.currentWidget() == self.unlock_screen:
            return
            
        logger.info("Vault is being locked due to inactivity.")
        self.auto_lock_timer.stop()
        self.crypto_handler.key = None # 关键: 从内存中清除加密密钥
        
        if self.main_widget:
            self.main_widget.deleteLater()
            self.main_widget = None
        
        self.stacked_widget.setCurrentWidget(self.unlock_screen)
        
    # 新增: 配置并启动自动锁定计时器
    def _setup_auto_lock(self) -> None:
        """ 根据设置配置并启动自动锁定计时器。"""
        settings = load_settings()
        self._auto_lock_enabled = settings.get("auto_lock_enabled", True)
        timeout_minutes = settings.get("auto_lock_timeout_minutes", 15)
        self._auto_lock_timeout_ms = timeout_minutes * 60 * 1000

        if self._auto_lock_enabled and self._auto_lock_timeout_ms > 0:
            logger.info(f"Auto-lock enabled. Timeout: {timeout_minutes} minutes.")
            self.auto_lock_timer.start(self._auto_lock_timeout_ms)
        else:
            logger.info("Auto-lock is disabled.")
            self.auto_lock_timer.stop()

    # 新增: 响应设置更改的槽函数
    def _on_settings_changed(self) -> None:
        logger.info("Settings have changed, re-evaluating auto-lock timer.")
        self._setup_auto_lock()
        
    # 新增: 事件过滤器，用于重置自动锁定计时器
    def eventFilter(self, obj, event: QEvent) -> bool:
        if self._auto_lock_enabled and self.auto_lock_timer.isActive():
            if event.type() in [QEvent.Type.KeyPress, QEvent.Type.MouseButtonPress, QEvent.Type.MouseMove]:
                self.auto_lock_timer.start(self._auto_lock_timeout_ms)
        return super().eventFilter(obj, event)

    def center_on_screen(self) -> None:
        if self.screen():
            screen_geometry = self.screen().availableGeometry()
            center_point = screen_geometry.center()
            self.move(
                int(center_point.x() - self.width() / 2),
                int(center_point.y() - self.height() / 2)
            )

    def retranslate_ui(self) -> None:
        """
        重新翻译此窗口及其所有活动子组件的UI文本。
        """
        logger.info("Retranslating the entire application UI...")
        self.setWindowTitle(t.get('app_title'))
        
        if self.unlock_screen:
            self.unlock_screen.retranslate_ui()
        if self.main_widget:
            self.main_widget.retranslate_ui()
        
        logger.info("UI retranslation complete.")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
            
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handles the shutdown process gracefully.
        """
        if self._is_shutting_down:
            event.ignore()
            return
            
        logger.info("Close event received. Scheduling graceful shutdown...")
        self._is_shutting_down = True
        
        self.hide()
        event.ignore()

        def on_shutdown_finished(*args):
            logger.info("Database connection closed. Exiting application.")
            app = QApplication.instance()
            if app:
                app.quit()

        task_manager.run_in_background(
            task=self.data_manager.close,
            on_success=on_shutdown_finished,
            on_error=on_shutdown_finished 
        )