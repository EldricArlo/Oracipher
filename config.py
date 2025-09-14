# config.py

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 加载 .env 文件中的环境变量 (如果存在)
load_dotenv()

# 从环境变量获取数据和日志目录路径，如果未设置，则使用默认值
APP_DATA_DIR: str = os.getenv("SAFEKEY_DATA_PATH", "safekey_data")
APP_LOG_DIR: str = os.getenv("SAFEKEY_LOG_PATH", "logs")

# 设置文件的完整路径
SETTINGS_FILE_PATH: str = os.path.join(APP_DATA_DIR, "settings.json")

def get_default_settings() -> Dict[str, Any]:
    """
    返回一份默认的设置字典。
    """
    return {
        "language": "zh_CN",
        "theme": "light"  # 可选值: "light", "dark"
    }

def load_settings() -> Dict[str, Any]:
    """
    从 settings.json 文件加载应用程序设置。
    """
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    default_settings = get_default_settings()
    
    try:
        with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
            settings: Dict[str, Any] = json.load(f)
        
        if not isinstance(settings, dict):
            logger.warning("Settings file is corrupt. Resetting to default settings.")
            save_settings(default_settings)
            return default_settings

        # 检查是否有新的设置项需要从默认配置中添加
        is_dirty = False
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
                is_dirty = True
        
        if is_dirty:
            logger.info("New settings found. Updating settings file.")
            save_settings(settings)
            
        return settings
    except (FileNotFoundError, json.JSONDecodeError):
        logger.info("Settings file not found or invalid. Creating with default settings.")
        save_settings(default_settings)
        return default_settings

def save_settings(settings: Dict[str, Any]) -> None:
    """
    将设置字典以JSON格式保存到 settings.json 文件。
    """
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    try:
        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        logger.debug(f"Settings successfully saved to '{SETTINGS_FILE_PATH}'.")
    except Exception as e:
        logger.error(f"Error saving settings: {e}", exc_info=True)