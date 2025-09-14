# ui/components/no_focus_delegate.py

from typing import Optional
from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QModelIndex, QObject

class NoFocusDelegate(QStyledItemDelegate):
    """
    一个自定义的样式委托 (Style Delegate)，其唯一目的是在绘制项目时
    移除默认的焦点指示器（通常是一个虚线框）。
    """
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

    def paint(self, painter: Optional[QPainter], option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """
        重写 `paint` 方法来修改绘制选项。
        """
        custom_option = QStyleOptionViewItem(option)
        
        if custom_option.state & QStyle.StateFlag.State_HasFocus:
            custom_option.state = custom_option.state & ~QStyle.StateFlag.State_HasFocus
        
        super().paint(painter, custom_option, index)