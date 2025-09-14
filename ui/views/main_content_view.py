# ui/views/main_content_view.py

import logging
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QListWidget, QListWidgetItem, QSplitter, QApplication)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QCursor

from language import t
from .details_view import DetailsView
from ..components.entry_list_item_widget import EntryListItemWidget
from ..components.no_focus_delegate import NoFocusDelegate

logger = logging.getLogger(__name__)

class MainContentView(QWidget):
    """
    主内容区域的视图组件。
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("contentContainer")
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15); layout.setSpacing(20)
        top_toolbar_layout = QHBoxLayout()
        self.search_input = QLineEdit(); self.search_input.setObjectName("search_input")
        self.add_button = QPushButton(); self.add_button.setObjectName("addButton")
        self.add_button.setFixedSize(45, 45)
        top_toolbar_layout.addWidget(self.search_input, 1); top_toolbar_layout.addStretch(0); top_toolbar_layout.addWidget(self.add_button)
        
        inner_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.entry_list = QListWidget(); self.entry_list.setItemDelegate(NoFocusDelegate(self))
        self.details_view = DetailsView()
        inner_splitter.addWidget(self.entry_list); inner_splitter.addWidget(self.details_view)
        inner_splitter.setSizes([300, 700])
        
        layout.addLayout(top_toolbar_layout); layout.addWidget(inner_splitter)
        self.retranslate_ui()

    def populate_entry_list(self, entries_by_name: Dict[str, List[Dict[str, Any]]], current_selection: Optional[str]) -> None:
        self.entry_list.blockSignals(True)
        self.entry_list.clear()

        # 当条目过多时，显示等待光标并分块处理，防止UI冻结
        total_items = len(entries_by_name)
        if total_items > 200:
            QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        sorted_names = sorted(entries_by_name.keys())
        item_to_select = None
        
        for i, name in enumerate(sorted_names):
            representative_entry = entries_by_name[name][0]
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, name)
            list_item.setSizeHint(QSize(0, 48))
            widget = EntryListItemWidget(representative_entry)
            self.entry_list.addItem(list_item)
            self.entry_list.setItemWidget(list_item, widget)
            if name == current_selection: item_to_select = list_item
            
            # 每处理100个条目，就强制处理一次UI事件
            if total_items > 200 and i % 100 == 0:
                QApplication.processEvents()
        
        if total_items > 200:
            QApplication.restoreOverrideCursor()

        self.entry_list.blockSignals(False)
        
        if item_to_select: self.entry_list.setCurrentItem(item_to_select)
        elif self.entry_list.count() > 0: self.entry_list.setCurrentRow(0)
    
    def get_selected_entry_name(self) -> Optional[str]:
        selected_items = self.entry_list.selectedItems()
        return selected_items[0].data(Qt.ItemDataRole.UserRole) if selected_items else None

    def retranslate_ui(self) -> None:
        self.search_input.setPlaceholderText(t.get('search_placeholder'))
        self.add_button.setText(t.get('button_add_icon'))
        self.details_view.retranslate_ui()