# ui/components/screen_qr_reader.py

import logging
import io
from typing import Optional

from PyQt6.QtWidgets import QWidget, QApplication, QPushButton
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QBuffer, QTimer
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QScreen, QPixmap, 
                         QResizeEvent, QKeyEvent, QPaintEvent, QMouseEvent)

from PIL import Image
from pyzbar.pyzbar import decode

from language import t

logger = logging.getLogger(__name__)

class ScreenQRReader(QWidget):
    """
    一个全屏覆盖的小部件，用于从屏幕上捕获并解码二维码。
    """
    qr_code_decoded = pyqtSignal(str)
    scan_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            logger.error("Could not get primary screen! QR scan feature may be unavailable.")
            # 使用 QTimer.singleShot 确保在构造函数完成后再关闭
            QTimer.singleShot(0, self.close)
            return
            
        self.screen_geometry: QRect = primary_screen.geometry()
        self.setGeometry(self.screen_geometry)

        self.pixel_ratio: float = primary_screen.devicePixelRatio()
        logger.info(f"Screen QR reader initialized. Device pixel ratio: {self.pixel_ratio}")

        self.begin: QPoint = QPoint()
        self.end: QPoint = QPoint()
        
        self.cancel_button = QPushButton(t.get('button_cancel'), self)
        self.cancel_button.setObjectName("qrCancelButton")
        self.cancel_button.setCursor(Qt.CursorShape.ArrowCursor)
        self.cancel_button.clicked.connect(self._cancel_scan)
        self._position_cancel_button()

    def _cancel_scan(self):
        logger.debug("QR code scan cancelled by user.")
        self.scan_cancelled.emit()
        self.close()

    def _position_cancel_button(self):
        button_size = self.cancel_button.sizeHint()
        margin = 20
        self.cancel_button.move(self.width() - button_size.width() - margin, margin)

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        super().resizeEvent(a0)
        self._position_cancel_button()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        with QPainter(self) as painter:
            painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
            painter.setPen(QPen(Qt.PenStyle.NoPen))
            painter.drawRect(self.rect())

            if not self.begin.isNull() and not self.end.isNull():
                selection_rect = QRect(self.begin, self.end).normalized()
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                painter.drawRect(selection_rect)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                painter.setPen(QPen(QColor("#FFFFFF"), 2, Qt.PenStyle.DashLine))
                painter.drawRect(selection_rect)

    def mousePressEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0:
            return
        self.begin = a0.position().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0:
            return
        self.end = a0.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, a0: Optional[QMouseEvent]) -> None:
        if not a0:
            return
        if self.cancel_button.geometry().contains(a0.position().toPoint()):
            return
            
        self.close()
        QTimer.singleShot(50, self.capture_and_decode)

    def keyPressEvent(self, a0: Optional[QKeyEvent]) -> None:
        if not a0:
            return
        if a0.key() == Qt.Key.Key_Escape:
            self._cancel_scan()

    def capture_and_decode(self) -> None:
        selection_rect = QRect(self.begin, self.end).normalized()
        
        if selection_rect.width() < 10 or selection_rect.height() < 10:
            self.scan_cancelled.emit()
            return

        screen: Optional[QScreen] = self.screen()
        if not screen:
            logger.error("Could not get a screen to capture from.")
            self.scan_cancelled.emit()
            return
            
        try:
            physical_x = int(selection_rect.x() * self.pixel_ratio)
            physical_y = int(selection_rect.y() * self.pixel_ratio)
            physical_width = int(selection_rect.width() * self.pixel_ratio)
            physical_height = int(selection_rect.height() * self.pixel_ratio)
            
            pixmap = screen.grabWindow(0, physical_x, physical_y, physical_width, physical_height) # type: ignore
            
            image = self._convert_qpixmap_to_pil(pixmap)
            decoded_objects = decode(image)
            
            if decoded_objects:
                qr_data = decoded_objects[0].data.decode('utf-8')
                logger.info("Successfully decoded QR code.")
                self.qr_code_decoded.emit(qr_data)
            else:
                logger.warning("No QR code found in the selected area.")
                self.scan_cancelled.emit()
        except Exception as e:
            logger.error(f"An error occurred during QR capture/decode: {e}", exc_info=True)
            self.scan_cancelled.emit()

    def _convert_qpixmap_to_pil(self, pixmap: QPixmap) -> Image.Image:
        """将 QPixmap 高效地转换为 PIL.Image 对象。"""
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        pixmap.save(buffer, "PNG")
        
        image_bytes = buffer.data().data()
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        return pil_image.convert("RGB")