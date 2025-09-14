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

# --- MODIFICATION START ---
def _load_and_parse_qss(file_path: str) -> str:
    """
    加载一个QSS文件，并递归解析其 @import 语句，同时将所有 url() 
    中的相对路径转换为绝对路径。
    """
    full_path = resource_path(file_path)
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error(f"Stylesheet file not found: {full_path}")
        return ""

    # 1. 递归解析 @import 语句
    import_pattern = re.compile(r'@import\s+url\("([^"]+)"\);')
    def import_replacer(match):
        imported_file_relative_path = match.group(1)
        # @import 中的路径是相对于当前QSS文件的
        imported_file_project_path = os.path.join(os.path.dirname(file_path), imported_file_relative_path)
        # 归一化路径以处理 '..' 等情况
        normalized_path = os.path.normpath(imported_file_project_path).replace('\\', '/')
        logger.debug(f"Parsing imported QSS file: {normalized_path}")
        return _load_and_parse_qss(normalized_path)

    content_with_imports = import_pattern.sub(import_replacer, content)

    # 2. 将所有 url() 路径转换为绝对路径
    # 这个正则表达式会查找 url(...)，但会忽略数据URI (如 url('data:image/...'))
    url_pattern = re.compile(r'url\((?![\'"]?data:)([^)]+)\)')
    def url_replacer(match):
        # 获取括号内的路径，并去除可能存在的引号和空格
        relative_path = match.group(1).strip().strip("'\"")
        # 假设所有 url() 中的路径都是相对于项目根目录的
        absolute_path = resource_path(relative_path).replace('\\', '/')
        return f'url("{absolute_path}")'

    parsed_content = url_pattern.sub(url_replacer, content_with_imports)
    return parsed_content
# --- MODIFICATION END ---

def apply_theme(app: QApplication, theme_name: str) -> None:
    """
    从文件加载并应用指定的主题样式表到整个应用程序。
    此函数现在会手动处理 @import 和 url() 语句。
    """
    if theme_name not in THEMES:
        logger.warning(f"Attempted to apply non-existent theme: '{theme_name}'")
        return

    theme_files = THEMES[theme_name]
    
    try:
        logger.info(f"Applying '{theme_name}' theme...")
        
        style_qss = _load_and_parse_qss(theme_files["style"])
        app_ui_qss = _load_and_parse_qss(theme_files["app_ui"])

        full_stylesheet = style_qss + "\n" + app_ui_qss
        
        app.setStyleSheet(full_stylesheet)
        logger.info(f"'{theme_name}' theme applied successfully.")
        
    except Exception as e:
        logger.error(f"Error applying theme '{theme_name}': {e}", exc_info=True)