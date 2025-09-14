# core/icon_processor.py

from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QPainterPath
from PyQt6.QtCore import Qt, QSize

class IconProcessor:
    """
    一个专门用于处理和美化图标图像的工具类。

    其核心功能是将任意形状的 QPixmap 裁剪为带有可选边框的圆形，
    用于在整个应用中保持统一的圆形图标风格。
    """

    @staticmethod
    def circle_mask(
        pixmap: QPixmap, 
        size: int, 
        border_width: int = 0, 
        border_color: QColor = QColor("transparent")
    ) -> QPixmap:
        """
        将给定的 QPixmap 裁剪为圆形，并可选择性地添加一个圆形边框。

        Args:
            pixmap: 原始的 QPixmap 图标。
            size: 最终输出的圆形图标的直径（以像素为单位）。
            border_width: 边框的宽度（以像素为单位）。如果为0，则不添加边框。
            border_color: 边框的颜色，通常为半透明色以达到柔和效果。
        
        Returns:
            一个新的、经过圆形裁剪和处理的 QPixmap。
        """
        if pixmap.isNull():
            return QPixmap()

        # 1. 创建最终画布：一个尺寸为 `size x size` 的透明 QPixmap。
        target = QPixmap(QSize(size, size))
        target.fill(Qt.GlobalColor.transparent)

        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # 开启抗锯齿，使圆形边缘平滑。

        # 2. 绘制边框 (如果需要):
        # 先在最终画布上绘制一个作为边框背景的、用 `border_color` 填充的实心圆。
        if border_width > 0 and border_color.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(border_color))
            painter.drawEllipse(0, 0, size, size)

        # 3. 计算内部图标的尺寸和位置:
        # 图标的直径等于总尺寸减去两侧边框的宽度。
        # 绘制图标的起始点(左上角)需要向内偏移一个边框的宽度。
        icon_diameter = size - (border_width * 2)
        icon_offset = border_width

        # 4. 裁剪原始图标为圆形:
        # a. 创建一个临时的、用于裁剪的画布 `icon_canvas`。
        icon_canvas = QPixmap(QSize(icon_diameter, icon_diameter))
        icon_canvas.fill(Qt.GlobalColor.transparent)
        
        icon_painter = QPainter(icon_canvas)
        icon_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # b. 创建一个圆形路径，并将其设置为裁剪区域。
        #    此后所有在 `icon_painter` 上的绘制操作都只会在这个圆形区域内显示。
        path = QPainterPath()
        path.addEllipse(0, 0, icon_diameter, icon_diameter)
        icon_painter.setClipPath(path)
        
        # c. 将原始 pixmap 缩放到与裁剪画布相同的大小，并绘制上去。
        #    `KeepAspectRatioByExpanding` 确保图像填满整个圆形，避免黑边。
        scaled_pixmap = pixmap.scaled(
            icon_diameter, icon_diameter,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        icon_painter.drawPixmap(0, 0, scaled_pixmap)
        icon_painter.end()

        # 5. 合成最终图像:
        # 将刚刚裁剪好的圆形图标 (`icon_canvas`) 绘制到我们的最终画布 (`target`) 上，
        # 覆盖在之前绘制的边框背景之上。
        painter.drawPixmap(icon_offset, icon_offset, icon_canvas)
        painter.end()

        return target