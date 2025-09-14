# ui/components/animated_bookmark_button.py

from typing import Optional, Union

from PyQt6.QtWidgets import (QWidget, QLabel, QGraphicsOpacityEffect,
                             QStyleOption, QStyle)
from PyQt6.QtGui import QIcon, QMouseEvent, QPaintEvent, QPainter
from PyQt6.QtCore import (Qt, QSize, QPropertyAnimation, QEasingCurve,
                          QEvent, pyqtSignal)
                          
class AnimatedBookmarkButton(QWidget):
    """
    一个带有展开/收缩动画的自定义书签按钮控件。
    """
    clicked = pyqtSignal()

    def __init__(self, icon_source: Union[QIcon, str], text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFixedHeight(40)
        
        self.compact_width = 50
        self.extended_width = 160
        self.setFixedWidth(self.compact_width)
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.icon_label = QLabel(self)
        icon = icon_source if isinstance(icon_source, QIcon) else QIcon(str(icon_source))
        self.icon_label.setPixmap(icon.pixmap(QSize(22, 22)))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setGeometry(5, 0, 40, 40)
        
        self.text_label = QLabel(text, self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.text_label.setGeometry(50, 0, self.extended_width - 55, 40)
        
        self.text_opacity_effect = QGraphicsOpacityEffect(self.text_label)
        self.text_label.setGraphicsEffect(self.text_opacity_effect)
        self.text_opacity_effect.setOpacity(0.0)
        
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.opacity_animation = QPropertyAnimation(self.text_opacity_effect, b"opacity")
        self.opacity_animation.setDuration(150)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        重写 paintEvent 以确保 QSS 样式能正确绘制控件的背景和边框。
        """
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def enterEvent(self, event: QEvent) -> None:
        """当鼠标进入控件区域时，触发展开动画。"""
        self.animation.stop()
        self.opacity_animation.stop()
        self.animation.setEndValue(self.extended_width)
        self.animation.start()
        self.opacity_animation.setStartValue(self.text_opacity_effect.opacity())
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """当鼠标离开控件区域时，触发收缩动画。"""
        self.animation.stop()
        self.opacity_animation.stop()
        self.animation.setEndValue(self.compact_width)
        self.animation.start()
        self.opacity_animation.setStartValue(self.text_opacity_effect.opacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理鼠标点击事件，并发出 `clicked` 信号。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)