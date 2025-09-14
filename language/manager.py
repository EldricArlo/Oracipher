# language/manager.py

import logging
from typing import Dict, Any

# 动态导入语言环境文件
from .locales import en, zh_CN

logger = logging.getLogger(__name__)

class LanguageManager:
    """
    一个单例模式的语言管理器，负责处理应用程序中的所有UI文本翻译。
    """

    def __init__(self) -> None:
        self._language: str = "zh_CN"  # 默认语言
        self.TRANSLATIONS: Dict[str, Dict[str, str]] = {
            "en": en.translations,
            "zh_CN": zh_CN.translations,
        }

    def set_language(self, lang_code: str) -> None:
        """设置当前使用的语言。"""
        if lang_code in self.TRANSLATIONS:
            self._language = lang_code
            logger.info(f"Application language set to '{lang_code}'.")
        else:
            self._language = "en" # 如果指定的语言不存在，回退到英语
            logger.warning(
                f"Language code '{lang_code}' not found. Falling back to 'en'."
            )

    def get(self, key: str, **kwargs) -> str:
        """
        根据给定的键获取翻译后的字符串。
        """
        try:
            translation = self.TRANSLATIONS[self._language].get(key)
            if translation is None:
                raise KeyError
            return translation.format(**kwargs) if kwargs else translation
        except KeyError:
            try:
                translation = self.TRANSLATIONS["en"].get(key)
                if translation is None:
                    raise KeyError
                
                logger.warning(
                    f"Translation key '{key}' not found for lang '{self._language}'. Falling back to 'en'."
                )
                return translation.format(**kwargs) if kwargs else translation
            except KeyError:
                logger.error(f"CRITICAL: Translation key '{key}' not found in any language.")
                return key

    def get_available_languages(self) -> Dict[str, str]:
        """返回所有可用语言的代码和显示名称的字典。"""
        return {"en": "English", "zh_CN": "简体中文"}