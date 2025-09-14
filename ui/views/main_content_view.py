# ui/views/main_content_view.py

import logging
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QListWidget, QListWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QSize

from language import t
from .details_view import DetailsView
from ..components.entry_list_item_widget import EntryListItemWidget
from ..components.no_focus_delegate import NoFocusDelegate

logger = logging.getLogger(__name__)

class MainContentView(QWidget):
    """
    主内容区域的视图组件。

    包含了搜索栏、条目列表和详情视图。它是一个纯粹的UI组件，
    不包含业务逻辑，所有用户交互都通过信号连接到控制器进行处理。
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("contentContainer")
        self.init_ui()

    def init_ui(self) -> None:
        """初始化主内容区域的UI布局和所有子组件。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(20)

        # 1. 顶部工具栏 (搜索框和添加按钮)
        top_toolbar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.add_button = QPushButton()
        self.add_button.setObjectName("addButton")
        self.add_button.setFixedSize(45, 45)
        top_toolbar_layout.addWidget(self.search_input, 1)
        top_toolbar_layout.addStretch(0)
        top_toolbar_layout.addWidget(self.add_button)

        # 2. 中间内容区域 (条目列表和详情视图)
        inner_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.entry_list = QListWidget()
        self.entry_list.setItemDelegate(NoFocusDelegate(self))
        self.details_view = DetailsView()
        inner_splitter.addWidget(self.entry_list)
        inner_splitter.addWidget(self.details_view)
        inner_splitter.setSizes([300, 700])

        # 3. 组合布局
        layout.addLayout(top_toolbar_layout)
        layout.addWidget(inner_splitter)
        
        self.retranslate_ui()

    def populate_entry_list(self, entries_by_name: Dict[str, List[Dict[str, Any]]], current_selection: Optional[str]) -> None:
        """
        由控制器调用，用已分组和过滤的数据填充条目列表。

        Args:
            entries_by_name: 一个字典，键是唯一的账户名，值是同名账户的列表。
            current_selection: 当前应该被选中的账户名。
        """
        self.entry_list.blockSignals(True)
        self.entry_list.clear()

        item_to_select = None
        sorted_names = sorted(entries_by_name.keys())

        for name in sorted_names:
            representative_entry = entries_by_name[name][0]
            list_item = QListWidgetItem()
            list_item.setData(Qt.ItemDataRole.UserRole, name)
            list_item.setSizeHint(QSize(0, 48))
            widget = EntryListItemWidget(representative_entry)
            self.entry_list.addItem(list_item)
            self.entry_list.setItemWidget(list_item, widget)
            if name == current_selection: item_to_select = list_item
        
        self.entry_list.blockSignals(False)
        
        if item_to_select:
            self.entry_list.setCurrentItem(item_to_select)
        elif self.entry_list.count() > 0:
            self.entry_list.setCurrentRow(0)
    
    def get_selected_entry_name(self) -> Optional[str]:
        """获取当前在列表中选中的条目名称。"""
        selected_items = self.entry_list.selectedItems()
        if not selected_items: return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def retranslate_ui(self) -> None:
        """更新此视图中所有需要翻译的文本。"""
        self.search_input.setPlaceholderText(t.get('search_placeholder'))
        self.add_button.setText(t.get('button_add_icon'))
        self.details_view.retranslate_ui()