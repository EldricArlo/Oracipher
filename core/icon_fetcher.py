# core/icon_fetcher.py

import base64
import io
import logging
import requests
from urllib.parse import urlparse

from PyQt6.QtGui import QPixmap, QIcon, QPainter
from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtSvg import QSvgRenderer

logger = logging.getLogger(__name__)

ICON_CACHE: dict[str, str | None] = {}

class IconFetcher:
    """
    负责获取、处理和提供网站或应用程序图标的工具类。
    """
    
    DEFAULT_ICON_SVG_STRING = """
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#5E5C5B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="8" cy="15" r="4" />
        <line x1="10.88" y1="12.12" x2="15" y2="8" />
        <line x1="18" y1="5" x2="15" y2="8" />
        <line x1="21" y1="2" x2="18" y2="5" />
    </svg>
    """

    @staticmethod
    def get_default_pixmap() -> QPixmap:
        renderer = QSvgRenderer(IconFetcher.DEFAULT_ICON_SVG_STRING.encode('utf-8'))
        pixmap = QPixmap(QSize(64, 64))
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    @staticmethod
    def get_default_icon_base64() -> str | None:
        try:
            pixmap = IconFetcher.get_default_pixmap()
            buffer = io.BytesIO()
            pixmap.save(buffer, "PNG")
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"生成默认图标Base64时出错: {e}", exc_info=True)
            return None

    @staticmethod
    def pixmap_from_base64(base64_str: str | None) -> QPixmap:
        if base64_str:
            try:
                byte_array = QByteArray.fromBase64(base64_str.encode('utf-8'))
                pixmap = QPixmap()
                if pixmap.loadFromData(byte_array):
                    return pixmap
            except Exception as e:
                logger.warning(f"从 Base64 创建 QPixmap 失败: {e}")
        return IconFetcher.get_default_pixmap()
        
    @staticmethod
    def icon_from_base64(base64_str: str | None) -> QIcon:
        return QIcon(IconFetcher.pixmap_from_base64(base64_str))

    @staticmethod
    def fetch_icon_from_url(url: str) -> str | None:
        if not url:
            return None
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if domain in ICON_CACHE:
                return ICON_CACHE[domain]
            favicon_service_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
            response = requests.get(favicon_service_url, timeout=5, stream=True)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                logger.warning(f"从 {favicon_service_url} 获取的不是图片: {content_type}")
                ICON_CACHE[domain] = None
                return None
            icon_data = response.content
            base64_icon = base64.b64encode(icon_data).decode('utf-8')
            ICON_CACHE[domain] = base64_icon
            logger.info(f"成功从 {domain} 获取图标。")
            return base64_icon
        except requests.RequestException as e:
            logger.error(f"从 URL '{url}' 获取图标时网络错误: {e}")
            if 'domain' in locals():
                ICON_CACHE[domain] = None
            return None
        except Exception as e:
            logger.error(f"处理 URL '{url}' 时发生未知错误: {e}", exc_info=True)
            if 'domain' in locals():
                ICON_CACHE[domain] = None
            return None