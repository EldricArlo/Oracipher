# utils/icon_cache.py

import logging
from typing import Dict

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from .paths import resource_path

logger = logging.getLogger(__name__)

class IconCache:
    """
    一个单例，用于在程序启动时预加载和缓存常用图标。
    这可以防止在首次使用图标（如按钮悬停）时因即时加载资源而导致的UI卡顿。
    """
    _instance = None
    
    # 定义所有需要预加载的图标的键和路径
    PRELOAD_ICONS = {
        "add": "ui/assets/icons/add.svg",
        "generate": "ui/assets/icons/generate.svg",
        "settings": "ui/assets/icons/settings.svg",
        "minimize": "ui/assets/icons/minimize.svg",
        "exit": "ui/assets/icons/exit.svg",
        "list": "ui/assets/icons/list.svg",
        "folder": "ui/assets/icons/folder.svg",
        "edit": "ui/assets/icons/edit.svg",
        "delete": "ui/assets/icons/delete.svg",
        "copy": "ui/assets/icons/copy.svg",
        "import": "ui/assets/icons/import.svg",
        "export": "ui/assets/icons/export.svg",
        "chevron-down": "ui/assets/icons/chevron-down.svg",
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconCache, cls).__new__(cls)
            cls._instance._cache: Dict[str, QIcon] = {}
            logger.info("IconCache instance created.")
        return cls._instance

    def preload(self) -> None:
        """
        加载所有在 PRELOAD_ICONS 中定义的图标并缓存它们。
        这个方法应该在程序启动的早期被调用。
        """
        logger.info("Preloading all application icons...")
        count = 0
        for key, path in self.PRELOAD_ICONS.items():
            try:
                # 创建 QIcon 对象
                icon = QIcon(resource_path(path))
                
                # 关键步骤: 调用 pixmap() 强制Qt立即渲染SVG到光栅图像
                if not icon.isNull():
                    icon.pixmap(QSize(32, 32)) # 使用一个典型尺寸强制渲染
                    self._cache[key] = icon
                    count += 1
                else:
                    logger.warning(f"Failed to preload icon '{key}' from path: {path}. Icon is null.")

            except Exception as e:
                logger.error(f"Error preloading icon '{key}' from path {path}: {e}", exc_info=True)
        
        logger.info(f"Successfully preloaded and cached {count}/{len(self.PRELOAD_ICONS)} icons.")

    def get(self, key: str) -> QIcon:
        """
        从缓存中获取一个 QIcon。
        """
        if key not in self._cache:
            logger.warning(f"Icon key '{key}' not found in cache. Attempting to load just-in-time.")
            path = self.PRELOAD_ICONS.get(key)
            if path:
                # 作为回退，即时加载并放入缓存
                icon = QIcon(resource_path(path))
                if not icon.isNull():
                    icon.pixmap(QSize(32, 32))
                    self._cache[key] = icon
                    return icon
            return QIcon() # 返回一个空图标
        
        return self._cache[key]

# 创建一个全局实例供整个应用程序使用
icon_cache = IconCache()