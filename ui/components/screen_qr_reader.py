# ui/components/screen_qr_reader.py

import logging
import io
from typing import Optional

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QBuffer, QTimer
from PyQt6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QScreen,
    QPixmap,
    QPaintEvent,
    QMouseEvent,
)

from PIL import Image
from pyzbar.pyzbar import decode

logger = logging.getLogger(__name__)


class ScreenQRReader(QWidget):
    """
    一个全屏覆盖的小部件，用于从屏幕上捕获并解码二维码。
    交互方式：通过鼠标拖拽选择区域。
    """

    qr_code_decoded = pyqtSignal(str)
    scan_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # --- MODIFICATION START: Corrected API call for multi-monitor support ---
        app_instance = QApplication.instance()
        if not app_instance:
            logger.critical("QApplication instance not found during ScreenQRReader init!")
            QTimer.singleShot(0, self.close)
            return
            
        primary_screen = app_instance.primaryScreen()
        if not primary_screen:
            logger.error("Could not get primary screen!")
            QTimer.singleShot(0, self.close)
            return

        # 正确的调用方式是 QScreen.virtualGeometry()
        all_screens_geometry = primary_screen.virtualGeometry()
        
        if all_screens_geometry.isEmpty():
            logger.error("Could not get virtual desktop geometry!")
            QTimer.singleShot(0, self.close)
            return

        self.setGeometry(all_screens_geometry)
        self.pixel_ratio: float = primary_screen.devicePixelRatio()
        # --- MODIFICATION END ---

        self.begin: QPoint = QPoint()
        self.end: QPoint = QPoint()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        with QPainter(self) as painter:
            painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(self.rect())
            if not self.begin.isNull() and not self.end.isNull():
                selection_rect = QRect(self.begin, self.end).normalized()
                painter.setCompositionMode(
                    QPainter.CompositionMode.CompositionMode_Clear
                )
                painter.drawRect(selection_rect)
                painter.setCompositionMode(
                    QPainter.CompositionMode.CompositionMode_SourceOver
                )
                painter.setPen(QPen(QColor("#FFFFFF"), 2, Qt.PenStyle.DashLine))
                painter.drawRect(selection_rect)

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0: return
        self.begin = a0.position().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0: return
        self.end = a0.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0: return
        self.capture_and_decode()

    def capture_and_decode(self) -> None:
        selection_rect = QRect(self.begin, self.end).normalized()
        
        if selection_rect.width() < 10 or selection_rect.height() < 10:
            logger.debug("QR code scan cancelled by selecting a small area.")
            self.scan_cancelled.emit()
            self.close()
            return

        screen: Optional[QScreen] = self.screen()
        if not screen:
            self.scan_cancelled.emit()
            self.close()
            return
            
        self.hide()
        QApplication.processEvents()

        try:
            physical_x = int(selection_rect.x() * self.pixel_ratio)
            physical_y = int(selection_rect.y() * self.pixel_ratio)
            physical_width = int(selection_rect.width() * self.pixel_ratio)
            physical_height = int(selection_rect.height() * self.pixel_ratio)
            
            pixmap = screen.grabWindow(0, physical_x, physical_y, physical_width, physical_height)
            
            image = self._convert_qpixmap_to_pil(pixmap)
            decoded_objects = decode(image)
            
            if decoded_objects:
                qr_data = decoded_objects[0].data.decode("utf-8")
                self.qr_code_decoded.emit(qr_data)
            else:
                logger.warning("No QR code found in the selected area.")
                self.scan_cancelled.emit()
                
        except Exception as e:
            logger.error(f"QR capture/decode error: {e}", exc_info=True)
            self.scan_cancelled.emit()
        finally:
            self.close()

    def _convert_qpixmap_to_pil(self, pixmap: QPixmap) -> Image.Image:
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        pixmap.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data().data()))
        return pil_image.convert("RGB")