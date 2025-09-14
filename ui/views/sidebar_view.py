# ui/views/sidebar_view.py

import logging
from typing import Optional, List, Dict

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap

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
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 15, 0, 15)
        main_layout.setSpacing(10)
        
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        
        logo_layout.setContentsMargins(0, 0, 0, 15)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label = QLabel()
        
        logo_path = resource_path("ui/assets/icons/logo.png")
        pixmap = QPixmap(logo_path)
        
        if pixmap.isNull():
            logger.critical(f"Failed to load logo for Sidebar from path: {logo_path}. Logo will be missing.")
        else:
            if self.devicePixelRatio() > 1:
                 pixmap.setDevicePixelRatio(self.devicePixelRatio())
            
            scaled_pixmap = pixmap.scaled(
                48, 48, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        
        logo_layout.addWidget(logo_label)

        self.category_buttons_layout = QVBoxLayout()
        self.category_buttons_layout.setSpacing(5)

        self.add_account_button = AnimatedBookmarkButton(icon_cache.get("add"), "")
        self.generate_password_button = AnimatedBookmarkButton(icon_cache.get("generate"), "")
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
            if child.widget():
                child.widget().deleteLater()

    def populate_categories(self, categories: List[str], icon_map: Dict[str, str]) -> None:
        self._clear_layout(self.category_buttons_layout)
        self.category_buttons.clear()

        all_items_text = t.get('all_categories')
        all_items_button = AnimatedBookmarkButton(icon_cache.get("list"), all_items_text)
        all_items_button.clicked.connect(lambda: self.category_clicked.emit(all_items_text))
        self.category_buttons[all_items_text] = all_items_button
        self.category_buttons_layout.addWidget(all_items_button)
        
        for category_name in categories:
            icon = IconFetcher.icon_from_base64(icon_map.get(category_name)) if icon_map.get(category_name) else icon_cache.get("folder")
            button = AnimatedBookmarkButton(icon, category_name)
            button.clicked.connect(lambda checked=False, name=category_name: self.category_clicked.emit(name))
            self.category_buttons[category_name] = button
            self.category_buttons_layout.addWidget(button)

    def set_active_category(self, active_category_name: str) -> None:
        for name, button in self.category_buttons.items():
            is_active = (name == active_category_name)
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def retranslate_ui(self) -> None:
        self.add_account_button.text_label.setText(t.get('button_add_account'))
        self.generate_password_button.text_label.setText(t.get('button_generate_password'))
        self.settings_button.text_label.setText(t.get('button_settings'))
        self.minimize_button.text_label.setText(t.get('button_minimize'))
        self.exit_button.text_label.setText(t.get('button_exit'))