# app.py

import logging
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, QPoint

from config import APP_DATA_DIR
from core.crypto import CryptoHandler
from core.data_manager import DataManager
from ui.unlock_screen import UnlockScreen
from ui.main_interface import MainWindow

# 为此模块创建一个专用的 logger 实例
logger = logging.getLogger(__name__)

class SafeKeyApp(QMainWindow):
    """
    应用程序的主窗口。

    该窗口采用无边框、半透明的现代UI风格。它内部包含一个 QStackedWidget
    来管理和切换解锁屏幕 (UnlockScreen) 和主功能界面 (MainWindow)。
    同时，它还负责处理窗口的拖动、样式加载和核心组件的初始化。
    """
    def __init__(self):
        """
        初始化主应用程序窗口。
        """
        super().__init__()
        logger.info("主应用程序窗口 (SafeKeyApp) 初始化开始...")
        
        self.setWindowTitle("SafeKey")
        self.resize(900, 600)
        
        # 设置窗口为无边框和背景透明。
        # WA_TranslucentBackground 允许 QSS 中的 border-radius 生效，
        # 从而创建圆角窗口。
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.drag_pos = QPoint()
        
        # 初始化核心处理程序
        logger.info(f"应用程序数据目录: {APP_DATA_DIR}")
        self.crypto_handler = CryptoHandler(APP_DATA_DIR)
        self.data_manager = DataManager(APP_DATA_DIR, self.crypto_handler)
        
        self.init_ui()
        self.apply_stylesheet()
        self.center()
        
        logger.info("主应用程序窗口初始化完成。")

    def init_ui(self):
        """
        初始化用户界面布局。

        此方法构建了窗口的基本结构：一个作为背景板的 QFrame，
        内部包含一个用于切换页面的 QStackedWidget。
        """
        # 1. 创建一个 QFrame 作为我们可见的、带有样式的背景。
        #    这是实现圆角无边框窗口的关键。
        background_panel = QFrame(self)
        background_panel.setObjectName("backgroundPanel")
        
        # 2. 将此面板设置为主窗口的中央部件。
        self.setCentralWidget(background_panel)
        
        # 3. 在背景面板内部创建一个布局。
        panel_layout = QVBoxLayout(background_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        
        # 4. 将 QStackedWidget 放入面板的布局中。
        self.stacked_widget = QStackedWidget()
        panel_layout.addWidget(self.stacked_widget)
        
        # 5. 将解锁屏幕添加到 QStackedWidget 中。
        self.unlock_screen = UnlockScreen(self.crypto_handler, self)
        self.unlock_screen.unlocked.connect(self.show_main_app)
        
        # 主界面将在成功解锁后才被创建和添加。
        self.main_widget = None 
        
        self.stacked_widget.addWidget(self.unlock_screen)
        logger.debug("UI布局初始化完成，已添加解锁屏幕。")

    def apply_stylesheet(self):
        """
        加载并应用全局 QSS 样式表。

        它会加载 style.qss (用于底层背景) 和 app_ui.qss (用于所有组件)，
        然后将它们合并并应用到整个应用程序。
        """
        try:
            logger.info("正在加载样式表...")
            # 使用 pathlib 确保路径在不同操作系统上的兼容性
            root_dir = Path(__file__).parent
            ui_dir = root_dir / "ui"
            
            style_qss_path = root_dir / "style.qss"
            with open(style_qss_path, "r", encoding="utf-8") as f:
                style_qss = f.read()

            app_ui_qss_path = ui_dir / "app_ui.qss"
            with open(app_ui_qss_path, "r", encoding="utf-8") as f:
                app_ui_qss = f.read()
            
            # 合并两个样式表并为整个应用程序设置
            self.setStyleSheet(style_qss + app_ui_qss)
            logger.info("样式表加载并应用成功。")

        except FileNotFoundError as e:
            logger.error(f"样式表文件未找到: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"加载样式表时发生未知错误: {e}", exc_info=True)

    def show_main_app(self):
        """
        在用户成功解锁后，显示主应用程序界面。
        """
        logger.info("解锁成功，正在切换到主界面...")
        if not self.main_widget:
            # 延迟实例化：只有在需要时才创建主界面，可以加快初始启动速度
            self.main_widget = MainWindow(self.data_manager)
            self.stacked_widget.addWidget(self.main_widget)
            logger.info("主界面 (MainWindow) 已创建并添加到堆栈。")
            
        self.stacked_widget.setCurrentWidget(self.main_widget)
        logger.info("已切换到主界面。")

    def center(self):
        """
        将窗口移动到屏幕中央。
        """
        if self.screen():
            screen_geometry = self.screen().availableGeometry()
            center_point = screen_geometry.center()
            self.move(
                int(center_point.x() - self.width() / 2),
                int(center_point.y() - self.height() / 2)
            )

    def mousePressEvent(self, event):
        """
        处理鼠标按下事件，用于实现无边框窗口拖动。
        
        Args:
            event (QMouseEvent): 鼠标事件对象。
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # 记录当前鼠标的全局位置
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        处理鼠标移动事件，用于实现无边框窗口拖动。

        Args:
            event (QMouseEvent): 鼠标事件对象。
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            # 计算鼠标移动的向量，并移动窗口
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()

    def closeEvent(self, event):
        """
        在应用程序关闭前，执行清理操作。

        Args:
            event (QCloseEvent): 关闭事件对象。
        """
        logger.info("接收到关闭事件，正在关闭数据库连接...")
        self.data_manager.close()
        logger.info("数据库连接已关闭。应用程序即将退出。")
        event.accept()