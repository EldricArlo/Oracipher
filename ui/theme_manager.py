# ui/theme_manager.py

import logging
import re
import os
from typing import Dict, List

from PyQt6.QtWidgets import QApplication

from utils.paths import resource_path
from config import load_settings, save_settings

logger = logging.getLogger(__name__)

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "style": "ui/assets/style.qss",
        "app_ui": "ui/assets/app_ui.qss"
    },
    "dark": {
        "style": "ui/assets/style_dark.qss",
        "app_ui": "ui/assets/app_ui_dark.qss"
    }
}

def get_current_theme() -> str:
    """获取当前保存的主题设置。"""
    settings = load_settings()
    return settings.get("theme", "light")

def set_current_theme(theme_name: str) -> None:
    """将新的主题名称保存到设置中。"""
    if theme_name not in THEMES:
        theme_name = "light"
    settings = load_settings()
    settings["theme"] = theme_name
    save_settings(settings)
    logger.info(f"Theme changed to '{theme_name}' and saved to settings.")

def _load_and_parse_qss(file_path: str) -> str:
    """
    加载一个QSS文件，并递归解析其 @import 语句。
    """
    full_path = resource_path(file_path)
    base_dir = os.path.dirname(full_path)
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"Stylesheet file not found: {full_path}")
        return ""

    # 使用正则表达式查找所有的 @import url("..."); 语句
    import_pattern = re.compile(r'@import\s+url\("([^"]+)"\);')
    
    def replacer(match):
        # 对于每一个找到的 @import，递归加载并解析其内容
        imported_file_relative_path = match.group(1)
        # 将相对路径转换为相对于项目根目录的路径
        imported_file_project_path = os.path.join(os.path.dirname(file_path), imported_file_relative_path)
        # 归一化路径以处理 '..' 或 '.'
        normalized_path = os.path.normpath(imported_file_project_path).replace('\\', '/')
        logger.debug(f"Parsing imported QSS file: {normalized_path}")
        return _load_and_parse_qss(normalized_path)

    # 将文件内容中的 @import 语句替换为实际的文件内容
    parsed_content = import_pattern.sub(replacer, content)
    return parsed_content

def apply_theme(app: QApplication, theme_name: str) -> None:
    """
    从文件加载并应用指定的主题样式表到整个应用程序。
    此函数现在会手动处理 @import 语句。
    """
    if theme_name not in THEMES:
        logger.warning(f"Attempted to apply non-existent theme: '{theme_name}'")
        return

    theme_files = THEMES[theme_name]
    
    try:
        logger.info(f"Applying '{theme_name}' theme...")
        
        # 加载并解析基础样式 (style.qss / style_dark.qss)
        style_qss = _load_and_parse_qss(theme_files["style"])
        
        # 加载并解析组件样式 (app_ui.qss / app_ui_dark.qss)
        app_ui_qss = _load_and_parse_qss(theme_files["app_ui"])

        # 使用换行符安全地拼接两个最终的样式表字符串
        full_stylesheet = style_qss + "\n" + app_ui_qss
        
        app.setStyleSheet(full_stylesheet)
        logger.info(f"'{theme_name}' theme applied successfully.")
        
    except Exception as e:
        logger.error(f"Error applying theme '{theme_name}': {e}", exc_info=True)