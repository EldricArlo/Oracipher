# ui/main_window.py

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QMainWindow
from PyQt6.QtCore import Qt, QTimer

from core.database import DataManager
from .views.sidebar_view import SidebarView
from .views.main_content_view import MainContentView
from .controllers.main_window_controller import MainWindowController


class MainWindow(QWidget):
    """
    主应用程序界面的根(root)小部件。
    """

    def __init__(self, data_manager: DataManager, main_app_window: QMainWindow):
        super().__init__()
        self.setObjectName("MainWindow")

        self.init_ui()

        self.controller = MainWindowController(
            main_app_window=main_app_window,
            sidebar_view=self.sidebar_view,
            content_view=self.content_view,
            data_manager=data_manager,
        )

        QTimer.singleShot(0, self.controller.load_initial_data)

    def init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.sidebar_view = SidebarView()
        self.content_view = MainContentView()

        main_splitter.addWidget(self.sidebar_view)
        main_splitter.addWidget(self.content_view)

        main_splitter.setSizes([180, 820])

        main_layout.addWidget(main_splitter)

    def retranslate_ui(self) -> None:
        self.content_view.retranslate_ui()
        self.controller.handle_language_change()
