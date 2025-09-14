# ui/components/custom_widgets.py

from typing import Optional
from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QListWidget, QTextEdit
from ui.theme_manager import get_current_theme

# --- 为滚动条定义的QSS样式字符串 ---

# 暗色主题的滚动条样式
SCROLLBAR_STYLE_DARK = """
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 14px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #44475a; /* 暗色滑块 */
        min-height: 30px;
        border-radius: 2px;
        width: 3px;
        margin: 0 5px;
    }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:vertical:pressed {
        background-color: #51546e; /* 暗色滑块悬停 */
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

# 亮色主题的滚动条样式
SCROLLBAR_STYLE_LIGHT = """
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 14px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #D1CBCB; /* 亮色滑块 */
        min-height: 30px;
        border-radius: 2px;
        width: 3px;
        margin: 0 5px;
    }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:vertical:pressed {
        background-color: #C0B8B7; /* 亮色滑块悬停 */
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

        # 确保逻辑正确：如果是 'dark' 主题，则使用 SCROLLBAR_STYLE_DARK
        if theme == "dark":
            style = SCROLLBAR_STYLE_DARK
        else:  # 否则（即 'light' 主题），使用 SCROLLBAR_STYLE_LIGHT
            style = SCROLLBAR_STYLE_LIGHT

        v_scroll_bar = self.verticalScrollBar()
        if v_scroll_bar:
            v_scroll_bar.setStyleSheet(style)

        h_scroll_bar = self.horizontalScrollBar()
        if h_scroll_bar:
            h_scroll_bar.setStyleSheet(style)

    def changeEvent(self, a0: Optional[QEvent]) -> None:
        """
        重写 changeEvent 以捕获样式变化事件。
        """
        super().changeEvent(a0)
        if a0 and a0.type() == QEvent.Type.StyleChange:
            self.update_scrollbar_style()


class StyledTextEdit(QTextEdit):
    """一个自动应用自定义滚动条样式的QTextEdit。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_scrollbar_style()

    def update_scrollbar_style(self):
        theme = get_current_theme()

        # 确保逻辑正确：如果是 'dark' 主题，则使用 SCROLLBAR_STYLE_DARK
        if theme == "dark":
            style = SCROLLBAR_STYLE_DARK
        else:  # 否则（即 'light' 主题），使用 SCROLLBAR_STYLE_LIGHT
            style = SCROLLBAR_STYLE_LIGHT

        v_scroll_bar = self.verticalScrollBar()
        if v_scroll_bar:
            v_scroll_bar.setStyleSheet(style)

        h_scroll_bar = self.horizontalScrollBar()
        if h_scroll_bar:
            h_scroll_bar.setStyleSheet(style)

    def changeEvent(self, e: Optional[QEvent]) -> None:
        """
        重写 changeEvent 以捕獲样式变化事件。
        """
        super().changeEvent(e)
        if e and e.type() == QEvent.Type.StyleChange:
            self.update_scrollbar_style()
