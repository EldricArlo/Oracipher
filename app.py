# app.py

import logging
from typing import Optional

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QCloseEvent

from config import APP_DATA_DIR
from core.crypto import CryptoHandler
from core.data_manager import DataManager
from ui.unlock_screen import UnlockScreen
from ui.main_interface import MainWindow
from utils import resource_path

logger = logging.getLogger(__name__)

class SafeKeyApp(QMainWindow):
    """
    应用程序的主窗口。
    """
    def __init__(self):
        super().__init__()
        logger.info("主应用程序窗口 (SafeKeyApp) 初始化开始...")
        
        self.setWindowTitle("SafeKey")
        self.resize(900, 600)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.drag_pos: QPoint = QPoint()
        
        logger.info(f"应用程序数据目录: {APP_DATA_DIR}")
        self.crypto_handler: CryptoHandler = CryptoHandler(APP_DATA_DIR)
        self.data_manager: DataManager = DataManager(APP_DATA_DIR, self.crypto_handler)
        
        self.init_ui()
        self.apply_stylesheet()
        self.center()
        
        logger.info("主应用程序窗口初始化完成。")

    def init_ui(self) -> None:
        background_panel = QFrame(self)
        background_panel.setObjectName("backgroundPanel")
        self.setCentralWidget(background_panel)
        
        panel_layout = QVBoxLayout(background_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        panel_layout.addWidget(self.stacked_widget)
        
        self.unlock_screen = UnlockScreen(self.crypto_handler, self)
        self.unlock_screen.unlocked.connect(self.show_main_app)
        
        self.main_widget: Optional[MainWindow] = None 
        
        self.stacked_widget.addWidget(self.unlock_screen)
        logger.debug("UI布局初始化完成，已添加解锁屏幕。")

    def apply_stylesheet(self) -> None:
        try:
            logger.info("正在加载样式表...")
            
            style_qss_path = resource_path("style.qss")
            with open(style_qss_path, "r", encoding="utf-8") as f:
                style_qss = f.read()

            app_ui_qss_path = resource_path("ui/app_ui.qss")
            with open(app_ui_qss_path, "r", encoding="utf-8") as f:
                app_ui_qss = f.read()
            
            self.setStyleSheet(style_qss + app_ui_qss)
            logger.info("样式表加载并应用成功。")

        except FileNotFoundError as e:
            logger.error(f"样式表文件未找到: {e.filename}", exc_info=True)
        except Exception as e:
            logger.error(f"加载样式表时发生未知错误: {e}", exc_info=True)

    def show_main_app(self) -> None:
        logger.info("解锁成功，正在切换到主界面...")
        if not self.main_widget:
            self.main_widget = MainWindow(self.data_manager)
            self.stacked_widget.addWidget(self.main_widget)
            logger.info("主界面 (MainWindow) 已创建并添加到堆栈。")
            
        self.stacked_widget.setCurrentWidget(self.main_widget)
        logger.info("已切换到主界面。")

    def center(self) -> None:
        if self.screen():
            screen_geometry = self.screen().availableGeometry()
            center_point = screen_geometry.center()
            self.move(
                int(center_point.x() - self.width() / 2),
                int(center_point.y() - self.height() / 2)
            )

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
        logger.info("接收到关闭事件，正在关闭数据库连接...")
        self.data_manager.close()
        logger.info("数据库连接已关闭。应用程序即将退出。")
        event.accept()