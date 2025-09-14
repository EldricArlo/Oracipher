# ui/components/custom_widgets.py

from PyQt6.QtWidgets import QListWidget, QTextEdit, QScrollBar
from ui.theme_manager import get_current_theme

# --- 为滚动条定义的QSS样式字符串 ---

SCROLLBAR_STYLE_DARK = """
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 14px;
        margin: 0;
    }

    /* 默认状态下的滑块：极细的线条 */
    QScrollBar::handle:vertical {
        background-color: #44475a;
        min-height: 30px;
        border-radius: 2px;
        width: 3px;
        margin: 0 5px;
    }

    /* 鼠标悬停在整个滚动条区域时，滑块的样式 */
    QScrollBar::handle:vertical:hover, QScrollBar::handle:vertical:pressed {
        /* --- MODIFICATION START: Softer hover color --- */
        background-color: #51546e; /* 一个更中性的、更浅的灰色 */
        /* --- MODIFICATION END --- */
        width: 12px;
        border-radius: 6px;
        margin: 0 1px;
        border: 1px solid #282a36;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
"""

SCROLLBAR_STYLE_LIGHT = """
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 14px;
        margin: 0;
    }

    /* 默认状态下的滑块：极细的线条 */
    QScrollBar::handle:vertical {
        background-color: #D1CBCB;
        min-height: 30px;
        border-radius: 2px;
        width: 3px;
        margin: 0 5px;
    }

    /* 鼠标悬停在整个滚动条区域时，滑块的样式 */
    QScrollBar::handle:vertical:hover, QScrollBar::handle:vertical:pressed {
        /* --- MODIFICATION START: Lighter hover color --- */
        background-color: #C0B8B7; /* 一个比之前更浅、更柔和的灰色 */
        /* --- MODIFICATION END --- */
        width: 12px;
        border-radius: 6px;
        margin: 0 1px;
        border-top: 1px solid rgba(255, 255, 255, 0.9);
        border-left: 1px solid rgba(255, 255, 255, 0.9);
        border-bottom: 1px solid rgba(181, 177, 176, 0.6);
        border-right: 1px solid rgba(181, 177, 176, 0.6);
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
"""

class StyledListWidget(QListWidget):
    """一个自动应用自定义滚动条样式的QListWidget。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_scrollbar_style()

    def update_scrollbar_style(self):
        theme = get_current_theme()
        style = SCROLLBAR_STYLE_DARK if theme == 'dark' else SCROLLBAR_STYLE_LIGHT
        self.verticalScrollBar().setStyleSheet(style)
        self.horizontalScrollBar().setStyleSheet(style) 

class StyledTextEdit(QTextEdit):
    """一个自动应用自定义滚动条样式的QTextEdit。"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_scrollbar_style()
    
    def update_scrollbar_style(self):
        theme = get_current_theme()
        style = SCROLLBAR_STYLE_DARK if theme == 'dark' else SCROLLBAR_STYLE_LIGHT
        self.verticalScrollBar().setStyleSheet(style)
        self.horizontalScrollBar().setStyleSheet(style)