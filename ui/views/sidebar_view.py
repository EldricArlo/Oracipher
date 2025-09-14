# ui/views/sidebar_view.py

import logging
from typing import Optional, List, Dict

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLayout, QLabel, QHBoxLayout, QStyle
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QEvent, QObject
from PyQt6.QtGui import QPixmap, QShowEvent

from language import t
from core.icon_fetcher import IconFetcher
from ..components.animated_bookmark_button import AnimatedBookmarkButton
from utils import icon_cache, resource_path

logger = logging.getLogger(__name__)


class SidebarView(QWidget):
    category_clicked = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("sidebarContainer")
        self.category_buttons: dict[str, AnimatedBookmarkButton] = {}

        self._filter_installed = False
        self.hover_check_timer = QTimer(self)
        self.hover_check_timer.setInterval(100)  # 每秒检查10次，响应迅速
        self.hover_check_timer.timeout.connect(self._continuously_check_hover_states)

        self.init_ui()

    def showEvent(self, a0: Optional[QShowEvent]) -> None:
        """在控件首次显示时，为父窗口安装事件过滤器。"""
        super().showEvent(a0)
        if not self._filter_installed:
            parent_window = self.window()
            if parent_window:
                parent_window.installEventFilter(self)
                self._filter_installed = True
                # 检查窗口是否已经激活，如果是，则立即启动定时器
                if parent_window.isActiveWindow():
                    self.hover_check_timer.start()

    def eventFilter(self, a0: Optional[QObject], a1: Optional[QEvent]) -> bool:
        """
        监听父窗口的激活/非激活事件，以启动/停止悬停状态检查定时器。
        这是为了优化性能，仅在应用处于前台时才进行检查。
        """
        # 增加对 None 的检查，以确保类型安全
        if not a0 or not a1:
            return super().eventFilter(a0, a1)

        if a0 == self.window():
            if a1.type() == QEvent.Type.WindowActivate:
                if not self.hover_check_timer.isActive():
                    self.hover_check_timer.start()
            elif a1.type() == QEvent.Type.WindowDeactivate:
                if self.hover_check_timer.isActive():
                    self.hover_check_timer.stop()
                    # 当窗口失活时，强制所有按钮收缩
                    self._force_collapse_all()

        return super().eventFilter(a0, a1)

    def _get_all_buttons(self) -> List[AnimatedBookmarkButton]:
        """获取侧边栏上所有动画按钮的列表。"""
        return list(self.category_buttons.values()) + [
            self.add_account_button,
            self.generate_password_button,
            self.settings_button,
            self.minimize_button,
            self.exit_button,
        ]

    def _continuously_check_hover_states(self) -> None:
        """
        定时器触发时调用，遍历所有动画按钮，并调用它们的状态检查方法来强制同步UI。
        """
        for button in self._get_all_buttons():
            if button.isVisible():
                button.check_hover_state_and_correct()

    def _force_collapse_all(self) -> None:
        """当窗口失活时，强制收缩所有按钮。"""
        for button in self._get_all_buttons():
            if button.isVisible() and button.width() != button.compact_width:
                button._collapse()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 15)
        main_layout.setSpacing(10)

        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)

        logo_layout.setContentsMargins(0, 0, 0, 15)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label = QLabel()

        logo_path = resource_path("images/icon-256.png")
        pixmap = QPixmap(logo_path)

        if pixmap.isNull():
            logger.critical(
                f"Failed to load logo for Sidebar from path: {logo_path}. Logo will be missing."
            )
        else:
            if self.devicePixelRatio() > 1:
                pixmap.setDevicePixelRatio(self.devicePixelRatio())

            scaled_pixmap = pixmap.scaled(
                48,
                48,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(scaled_pixmap)

        logo_layout.addWidget(logo_label)

        self.category_buttons_layout = QVBoxLayout()
        self.category_buttons_layout.setSpacing(5)

        self.add_account_button = AnimatedBookmarkButton(icon_cache.get("add"), "")
        self.generate_password_button = AnimatedBookmarkButton(
            icon_cache.get("generate"), ""
        )
        self.settings_button = AnimatedBookmarkButton(icon_cache.get("settings"), "")
        self.minimize_button = AnimatedBookmarkButton(icon_cache.get("minimize"), "")
        self.exit_button = AnimatedBookmarkButton(icon_cache.get("exit"), "")

        main_layout.addWidget(logo_container)
        main_layout.addLayout(self.category_buttons_layout)
        main_layout.addStretch(1)
        main_layout.addWidget(self.add_account_button)
        main_layout.addWidget(self.generate_password_button)
        main_layout.addWidget(self.settings_button)
        main_layout.addStretch(1)
        main_layout.addWidget(self.minimize_button)
        main_layout.addWidget(self.exit_button)

        self.retranslate_ui()

    def _clear_layout(self, layout: QLayout):
        while layout.count():
            child = layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.deleteLater()

    def populate_categories(
        self, categories: List[str], icon_map: Dict[str, str]
    ) -> None:
        self._clear_layout(self.category_buttons_layout)
        self.category_buttons.clear()

        all_items_text = t.get("all_categories")
        all_items_button = AnimatedBookmarkButton(
            icon_cache.get("list"), all_items_text
        )
        all_items_button.clicked.connect(
            lambda: self.category_clicked.emit(all_items_text)
        )
        self.category_buttons[all_items_text] = all_items_button
        self.category_buttons_layout.addWidget(all_items_button)

        for category_name in categories:
            icon = (
                IconFetcher.icon_from_base64(icon_map.get(category_name))
                if icon_map.get(category_name)
                else icon_cache.get("folder")
            )
            button = AnimatedBookmarkButton(icon, category_name)
            button.clicked.connect(
                lambda checked=False, name=category_name: self.category_clicked.emit(
                    name
                )
            )
            self.category_buttons[category_name] = button
            self.category_buttons_layout.addWidget(button)

    def set_active_category(self, active_category_name: str) -> None:
        for name, button in self.category_buttons.items():
            is_active = name == active_category_name
            button.setProperty("active", is_active)

            style = button.style()
            if style:
                style.unpolish(button)
                style.polish(button)

    def retranslate_ui(self) -> None:
        self.add_account_button.text_label.setText(t.get("button_add_account"))
        self.generate_password_button.text_label.setText(
            t.get("button_generate_password")
        )
        self.settings_button.text_label.setText(t.get("button_settings"))
        self.minimize_button.text_label.setText(t.get("button_minimize"))
        self.exit_button.text_label.setText(t.get("button_exit"))
