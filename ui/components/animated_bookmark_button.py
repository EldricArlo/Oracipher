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

    def check_hover_state_and_correct(self):
        """
        检查鼠标当前是否在此按钮上方，并强制更新视觉状态以匹配。
        这是解决最小化/恢复后动画状态不同步的核心。
        """
        if self:
            is_under_mouse = self.rect().contains(self.mapFromGlobal(self.cursor().pos()))
            
            if is_under_mouse:
                if self.width() != self.extended_width:
                    self._expand()
            else:
                if self.width() != self.compact_width:
                    self._collapse()

    def _expand(self):
        self.animation.stop()
        self.opacity_animation.stop()
        self.animation.setEndValue(self.extended_width)
        self.animation.start()
        self.opacity_animation.setStartValue(self.text_opacity_effect.opacity())
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

    def _collapse(self):
        self.animation.stop()
        self.opacity_animation.stop()
        self.animation.setEndValue(self.compact_width)
        self.animation.start()
        self.opacity_animation.setStartValue(self.text_opacity_effect.opacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.start()

    def paintEvent(self, event: QPaintEvent) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    # 我们仍然保留 enter/leaveEvent 以便在正常情况下获得最快的响应
    def enterEvent(self, event: QEvent) -> None:
        self._expand()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._collapse()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)