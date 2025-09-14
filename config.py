# config.py

import os
import json
import logging
from dotenv import load_dotenv

# 获取 logger 实例
logger = logging.getLogger(__name__)

# 加载项目根目录下的 .env 文件中的环境变量。
# 这使得配置（如数据路径）可以轻松地在不同开发环境中切换，而无需修改代码。
load_dotenv()

# --- 应用程序数据目录 ---
# 使用一个明确的、专用的目录来存储所有应用程序数据（数据库、密钥、设置）。
# 优先从环境变量 "SAFEKEY_DATA_PATH" 获取路径。
# 如果环境变量不存在，则默认使用当前工作目录下的 "safekey_data" 目录。
APP_DATA_DIR = os.getenv("SAFEKEY_DATA_PATH", "data")

# --- 设置文件路径 ---
SETTINGS_FILE_PATH = os.path.join(APP_DATA_DIR, "settings.json")


def get_default_settings() -> dict:
    """
    返回一个包含默认设置的字典。
    
    这是所有设置的“真实来源”，确保应用程序始终有可用的基础配置。

    Returns:
        dict: 包含默认设置的字典。
    """
    return {
        "language": "en"  # 默认语言为英语
    }


def load_settings() -> dict:
    """
    从 JSON 文件中加载用户设置。

    如果设置文件不存在、格式不正确或缺少某些键，
    此函数会返回默认设置或用默认值填充缺失的键，以确保程序的健壮性。

    Returns:
        dict: 一个完整的、可用的设置字典。
    """
    # 确保数据目录存在，以便可以读取文件
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    
    default_settings = get_default_settings()
    
    try:
        with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
            # 基本验证：确保加载的是一个字典
            if not isinstance(settings, dict):
                logger.warning(f"设置文件 '{SETTINGS_FILE_PATH}' 格式无效，将使用默认设置。")
                return default_settings
            
            # 健壮性检查：确保所有默认的键都存在于加载的设置中
            # 如果缺少了某个键（例如，在版本更新后新增了设置项），则用默认值补充
            is_dirty = False
            for key, value in default_settings.items():
                if key not in settings:
                    settings[key] = value
                    is_dirty = True
            
            if is_dirty:
                logger.info("设置文件中缺少部分键，已使用默认值填充。")
                # 可以选择性地将补充完整的设置保存回去
                # save_settings(settings)

            return settings
            
    except FileNotFoundError:
        logger.info(f"未找到设置文件 '{SETTINGS_FILE_PATH}'，将创建并使用默认设置。")
        # 如果文件不存在，保存一份默认设置文件
        save_settings(default_settings)
        return default_settings
        
    except json.JSONDecodeError:
        logger.error(f"解析设置文件 '{SETTINGS_FILE_PATH}' 失败，文件可能已损坏。将使用默认设置。")
        return default_settings


def save_settings(settings: dict):
    """
    将用户设置字典保存到 JSON 文件。

    Args:
        settings (dict): 要保存的设置字典。
    """
    # 确保数据目录存在，以便可以写入文件
    os.makedirs(APP_DATA_DIR, exist_ok=True)
    
    try:
        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
            # 使用 indent=4 使 JSON 文件格式化，便于人类阅读
            json.dump(settings, f, indent=4)
        logger.info(f"设置已成功保存到 '{SETTINGS_FILE_PATH}'。")
    except Exception as e:
        logger.error(f"保存设置到 '{SETTINGS_FILE_PATH}' 时发生错误: {e}", exc_info=True)