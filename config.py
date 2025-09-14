# config.py

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

APP_DATA_DIR: str = os.getenv("SAFEKEY_DATA_PATH", "safekey_data")

APP_LOG_DIR: str = os.getenv("SAFEKEY_LOG_PATH", "logs")

SETTINGS_FILE_PATH: str = os.path.join(APP_DATA_DIR, "settings.json")


def get_default_settings() -> Dict[str, Any]:
    """
    返回一个包含默认设置的字典。
    """
    return {
        "language": "zh_CN"
    }


def load_settings() -> Dict[str, Any]:
    """
    从 JSON 文件中加载用户设置。
    """
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    
    default_settings = get_default_settings()
    
    try:
        with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
            settings: Dict[str, Any] = json.load(f)
            
            if not isinstance(settings, dict):
                logger.warning(f"设置文件 '{SETTINGS_FILE_PATH}' 格式无效，将使用默认设置。")
                return default_settings
            
            is_dirty = False
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
                    is_dirty = True
            
            if is_dirty:
                logger.info("设置文件中缺少部分键，已使用默认值填充并重新保存。")
                save_settings(settings)

            return settings
            
    except FileNotFoundError:
        logger.info(f"未找到设置文件 '{SETTINGS_FILE_PATH}'，将创建并使用默认设置。")
        save_settings(default_settings)
        return default_settings
        
    except json.JSONDecodeError:
        logger.error(f"解析设置文件 '{SETTINGS_FILE_PATH}' 失败，文件可能已损坏。将使用默认设置。")
        return default_settings


def save_settings(settings: Dict[str, Any]) -> None:
    """
    将用户设置字典保存到 JSON 文件。
    """
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    
    try:
        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        logger.info(f"设置已成功保存到 '{SETTINGS_FILE_PATH}'。")
    except Exception as e:
        logger.error(f"保存设置到 '{SETTINGS_FILE_PATH}' 时发生错误: {e}", exc_info=True)