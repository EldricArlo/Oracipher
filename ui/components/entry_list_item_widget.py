# ui/components/entry_list_item_widget.py

from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from core.icon_fetcher import IconFetcher

class EntryListItemWidget(QWidget):
    """
    用于在 QListWidget 中显示带有图标和文本的自定义条目。
    """
    # 修正：将 __init__ 方法正确缩进到类的内部
    def __init__(self, entry: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.entry_data = entry
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)
        
        # 图标标签
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(28, 28)
        self.icon_label.setScaledContents(True)
        
        details = entry.get("details", {})
        icon_data = details.get("icon_data")
        pixmap = IconFetcher.pixmap_from_base64(icon_data)
        self.icon_label.setPixmap(pixmap)
        
        # 文本标签
        self.name_label = QLabel(entry.get("name", "Unnamed"))
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label, 1)