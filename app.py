# app.py

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QStackedWidget,
    QFrame,
    QApplication,
    QWidget,
)
from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent, QObject
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

        self.setWindowTitle(t.get("app_title"))
        self.resize(1000, 700)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.drag_pos: QPoint = QPoint()
        self._is_dragging: bool = False

        self._is_shutting_down = False

        self.auto_lock_timer = QTimer(self)
        self.auto_lock_timer.setSingleShot(True)
        self.auto_lock_timer.timeout.connect(self.lock_vault)
        self._auto_lock_enabled = False
        self._auto_lock_timeout_ms = 0

        logger.info(f"Application data directory: {APP_DATA_DIR}")
        self.crypto_handler: CryptoHandler = CryptoHandler(APP_DATA_DIR)
        self.data_manager: DataManager = DataManager(APP_DATA_DIR, self.crypto_handler)

        app_instance = QApplication.instance()
        if isinstance(app_instance, QApplication):
            apply_theme(app_instance, get_current_theme())
            app_instance.installEventFilter(self)

        self.init_ui()
        self.center_on_screen()

        logger.info("SafeKeyApp main window initialization complete.")

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
        self.unlock_screen.exit_requested.connect(self.close)
        self.stacked_widget.addWidget(self.unlock_screen)

        self.main_widget: Optional[MainWindow] = None

    def show_main_app(self) -> None:
        logger.info("Unlock successful. Switching to the main application view.")
        if not self.main_widget:
            logger.info("Instantiating MainWindow for the first time...")
            self.main_widget = MainWindow(
                data_manager=self.data_manager, main_app_window=self
            )
            self.main_widget.controller.settings_changed.connect(
                self._on_settings_changed
            )
            self.stacked_widget.addWidget(self.main_widget)

        self.stacked_widget.setCurrentWidget(self.main_widget)
        self._setup_auto_lock()
        logger.info("View switched to MainWindow.")

    def lock_vault(self) -> None:
        if self.stacked_widget.currentWidget() == self.unlock_screen:
            return
        logger.info("Vault is being locked due to inactivity.")
        self.auto_lock_timer.stop()
        self.crypto_handler.key = None
        if self.main_widget:
            self.main_widget.deleteLater()
            self.main_widget = None
        self.stacked_widget.setCurrentWidget(self.unlock_screen)

    def _setup_auto_lock(self) -> None:
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

    def _on_settings_changed(self) -> None:
        logger.info("Settings have changed, re-evaluating auto-lock timer.")
        self._setup_auto_lock()

    def eventFilter(self, a0: "QObject | None", a1: "QEvent | None") -> bool:
        watched = a0
        event = a1

        if event and self._auto_lock_enabled and self.auto_lock_timer.isActive():
            if event.type() in [
                QEvent.Type.KeyPress,
                QEvent.Type.MouseButtonPress,
                QEvent.Type.MouseMove,
            ]:
                self.auto_lock_timer.start(self._auto_lock_timeout_ms)
        return super().eventFilter(watched, event)

    def center_on_screen(self) -> None:
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            center_point = screen_geometry.center()
            self.move(
                int(center_point.x() - self.width() / 2),
                int(center_point.y() - self.height() / 2),
            )

    def retranslate_ui(self) -> None:
        logger.info("Retranslating the entire application UI...")
        self.setWindowTitle(t.get("app_title"))

        if self.unlock_screen:
            self.unlock_screen.retranslate_ui()
        if self.main_widget:
            self.main_widget.retranslate_ui()

        logger.info("UI retranslation complete.")

    def mousePressEvent(self, a0: "QMouseEvent | None") -> None:
        event = a0
        if not event:
            super().mousePressEvent(event)
            return

        # 仅当鼠标左键按下时才处理
        if event.button() == Qt.MouseButton.LeftButton:
            # 这个事件只会在点击未被子控件（如按钮）消费的区域时触发
            # 因此，我们可以安全地认为拖动操作应该开始
            self.drag_pos = event.globalPosition().toPoint()
            self._is_dragging = True
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, a0: "QMouseEvent | None") -> None:
        event = a0
        if not event:
            super().mouseMoveEvent(event)
            return

        # 必须同时检查鼠标左键是否按下以及是否处于拖动状态
        if event.buttons() == Qt.MouseButton.LeftButton and self._is_dragging:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, a0: "QMouseEvent | None") -> None:
        event = a0
        if not event:
            super().mouseReleaseEvent(event)
            return
            
        # 当鼠标左键松开时，总是结束拖动状态
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def closeEvent(self, a0: "QCloseEvent | None") -> None:
        event = a0
        if not event:
            super().closeEvent(event)
            return
            
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
            on_error=on_shutdown_finished,
        )
