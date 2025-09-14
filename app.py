# app.py

import logging
from typing import Optional

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget, QFrame, QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QCloseEvent

from config import APP_DATA_DIR
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
        
        logger.info(f"Application data directory: {APP_DATA_DIR}")
        self.crypto_handler: CryptoHandler = CryptoHandler(APP_DATA_DIR)
        self.data_manager: DataManager = DataManager(APP_DATA_DIR, self.crypto_handler)
        
        app_instance = QApplication.instance()
        if app_instance:
            apply_theme(app_instance, get_current_theme())
        
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
        self.stacked_widget.addWidget(self.unlock_screen)
        
        self.main_widget: Optional[MainWindow] = None

    def show_main_app(self) -> None:
        logger.info("Unlock successful. Switching to the main application view.")
        if not self.main_widget:
            logger.info("Instantiating MainWindow for the first time...")
            self.main_widget = MainWindow(data_manager=self.data_manager, main_app_window=self)
            self.stacked_widget.addWidget(self.main_widget)
        
        self.stacked_widget.setCurrentWidget(self.main_widget)
        logger.info("View switched to MainWindow.")

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