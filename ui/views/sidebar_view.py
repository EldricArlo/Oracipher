# ui/views/sidebar_view.py

from typing import Optional, List, Dict

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLayout
from PyQt6.QtCore import pyqtSignal

from language import t
from core.icon_fetcher import IconFetcher
from ..components.animated_bookmark_button import AnimatedBookmarkButton
from utils import icon_cache

class SidebarView(QWidget):
    """
    应用程序左侧的侧边栏视图。
    """
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
        
        self.category_buttons_layout = QVBoxLayout()
        self.category_buttons_layout.setSpacing(5)

        self.add_account_button = AnimatedBookmarkButton(icon_cache.get("add"), "")
        self.generate_password_button = AnimatedBookmarkButton(icon_cache.get("generate"), "")
        self.settings_button = AnimatedBookmarkButton(icon_cache.get("settings"), "")
        self.minimize_button = AnimatedBookmarkButton(icon_cache.get("minimize"), "")
        self.exit_button = AnimatedBookmarkButton(icon_cache.get("exit"), "")

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
        """安全地清空一个布局中的所有小部件。"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_categories(self, categories: List[str], icon_map: Dict[str, str]) -> None:
        """由控制器调用，用最新的分类数据填充侧边栏。"""
        self._clear_layout(self.category_buttons_layout)
        self.category_buttons.clear()

        all_items_text = t.get('all_categories')
        all_items_icon = icon_cache.get("list")
        all_items_button = AnimatedBookmarkButton(all_items_icon, all_items_text)
        all_items_button.clicked.connect(lambda: self.category_clicked.emit(all_items_text))
        self.category_buttons[all_items_text] = all_items_button
        self.category_buttons_layout.addWidget(all_items_button)
        
        for category_name in categories:
            icon_base64 = icon_map.get(category_name)
            icon = IconFetcher.icon_from_base64(icon_base64) if icon_base64 else icon_cache.get("folder")
            button = AnimatedBookmarkButton(icon, category_name)
            button.clicked.connect(lambda checked=False, name=category_name: self.category_clicked.emit(name))
            self.category_buttons[category_name] = button
            self.category_buttons_layout.addWidget(button)

    def set_active_category(self, active_category_name: str) -> None:
        """根据传入的分类名称，高亮对应的按钮。"""
        for name, button in self.category_buttons.items():
            is_active = (name == active_category_name)
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)

    def retranslate_ui(self) -> None:
        """更新所有按钮的显示文本。"""
        self.add_account_button.text_label.setText(t.get('button_add_account'))
        self.generate_password_button.text_label.setText(t.get('button_generate_password'))
        self.settings_button.text_label.setText(t.get('button_settings'))
        self.minimize_button.text_label.setText(t.get('button_minimize'))
        self.exit_button.text_label.setText(t.get('button_exit'))