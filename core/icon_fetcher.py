# core/icon_fetcher.py

import base64
import io
import logging
import requests
from urllib.parse import urlparse

# --- MODIFICATION START: Import lru_cache ---
from functools import lru_cache

# --- MODIFICATION END ---

from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor
from PyQt6.QtCore import QByteArray, QSize, Qt, QBuffer
from PyQt6.QtSvg import QSvgRenderer

from .icon_processor import IconProcessor

logger = logging.getLogger(__name__)

# --- MODIFICATION START: Removed the global ICON_CACHE dictionary ---
# The global ICON_CACHE dictionary is no longer needed as we will use lru_cache.
# ICON_CACHE: dict[str, str | None] = {}
# --- MODIFICATION END ---


class IconFetcher:
    """
    负责获取、处理和提供网站或应用程序图标的工具类。
    """

    TARGET_ICON_SIZE = 64
    BORDER_COLOR = QColor(0, 0, 0, 25)
    BORDER_WIDTH = 2

    DEFAULT_ICON_SVG_STRING = """
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#5E5C5B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="2" y1="12" x2="22" y2="12" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
    """

    FAVICON_SERVICES = [
        "https://www.google.com/s2/favicons?domain={domain}&sz=128",
        "https://icons.duckduckgo.com/ip3/{domain}.ico",
    ]

    @staticmethod
    def _get_raw_default_pixmap() -> QPixmap:
        """从SVG字符串渲染并返回一个 *原始的、未经处理的* QPixmap默认图标。"""
        renderer = QSvgRenderer(IconFetcher.DEFAULT_ICON_SVG_STRING.encode("utf-8"))
        pixmap = QPixmap(
            QSize(IconFetcher.TARGET_ICON_SIZE, IconFetcher.TARGET_ICON_SIZE)
        )
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    @staticmethod
    def get_default_pixmap() -> QPixmap:
        """获取一个 *经过圆形处理的* 默认图标。"""
        raw_pixmap = IconFetcher._get_raw_default_pixmap()
        return IconProcessor.circle_mask(
            raw_pixmap,
            IconFetcher.TARGET_ICON_SIZE,
            IconFetcher.BORDER_WIDTH,
            IconFetcher.BORDER_COLOR,
        )

    @staticmethod
    def get_default_icon_base64() -> str | None:
        """
        获取默认图标的Base64编码字符串。
        存储的是原始图标数据，在加载时再进行圆形化处理，以保持数据纯净。
        """
        try:
            raw_pixmap = IconFetcher._get_raw_default_pixmap()

            buffer = QBuffer()
            buffer.open(QBuffer.OpenModeFlag.WriteOnly)
            raw_pixmap.save(buffer, "PNG")

            icon_data = buffer.data().data()
            return base64.b64encode(icon_data).decode("utf-8")

        except Exception as e:
            logger.error(
                f"Failed to generate Base64 for default icon: {e}", exc_info=True
            )
            return None

    @staticmethod
    def pixmap_from_base64(base64_str: str | None) -> QPixmap:
        """
        从Base64字符串创建 QPixmap，并自动应用圆形遮罩和边框。
        如果输入为空或无效，则返回处理过的默认图标。
        """
        raw_pixmap = QPixmap()

        if base64_str:
            try:
                byte_array = QByteArray.fromBase64(base64_str.encode("utf-8"))
                if not raw_pixmap.loadFromData(byte_array):
                    logger.warning(
                        "Failed to load pixmap from byte array, data might be corrupt. Falling back to default."
                    )
                    raw_pixmap = IconFetcher._get_raw_default_pixmap()
            except Exception as e:
                logger.warning(
                    f"Failed to create QPixmap from Base64: {e}. Falling back to default."
                )
                raw_pixmap = IconFetcher._get_raw_default_pixmap()
        else:
            raw_pixmap = IconFetcher._get_raw_default_pixmap()

        return IconProcessor.circle_mask(
            raw_pixmap,
            IconFetcher.TARGET_ICON_SIZE,
            IconFetcher.BORDER_WIDTH,
            IconFetcher.BORDER_COLOR,
        )

    @staticmethod
    def icon_from_base64(base64_str: str | None) -> QIcon:
        """从Base64字符串创建 QIcon (其内部的pixmap已是圆形)。"""
        return QIcon(IconFetcher.pixmap_from_base64(base64_str))

    # --- MODIFICATION START: New private method with LRU cache ---
    # 这个新方法包含了实际的网络请求逻辑。
    # @lru_cache 装饰器会自动为这个函数的结果创建一个LRU缓存。
    # maxsize=128 意味着最多缓存128个不同域名的图标。
    @staticmethod
    @lru_cache(maxsize=128)
    def _fetch_icon_from_services(domain: str) -> str | None:
        """
        对给定的域名，尝试从多个服务获取图标。此函数的结果被缓存。
        """
        for service_template in IconFetcher.FAVICON_SERVICES:
            service_url = service_template.format(domain=domain)
            logger.info(f"Attempting to fetch icon for {domain} from {service_url}...")
            try:
                response = requests.get(service_url, timeout=5, stream=True)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                if "image" not in content_type:
                    logger.warning(
                        f"Content from {service_url} is not an image: {content_type}. Trying next service."
                    )
                    continue

                icon_data = response.content
                base64_icon = base64.b64encode(icon_data).decode("utf-8")

                logger.info(f"Successfully fetched and cached icon for {domain}.")
                return base64_icon

            except requests.RequestException as e:
                logger.warning(
                    f"Network error fetching from {service_url}: {e}. Trying next service."
                )
                continue

        logger.error(f"All favicon services failed for domain: {domain}")
        return None

    # --- MODIFICATION END ---

    @staticmethod
    def fetch_icon_from_url(url: str) -> str | None:
        """
        从给定的URL获取网站图标的Base64编码。
        此方法现在是一个包装器，负责解析URL并调用带缓存的抓取函数。
        """
        if not url:
            return None

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            if not domain:
                logger.warning(f"Could not parse a valid domain from URL: '{url}'")
                return None

            # 调用带缓存的内部方法
            return IconFetcher._fetch_icon_from_services(domain)

        except Exception as e:
            logger.error(
                f"An unexpected error occurred while processing URL '{url}': {e}",
                exc_info=True,
            )
            return None
