# language/__init__.py

from .manager import LanguageManager

# 创建一个全局单例，以便在应用的任何地方通过 `from language import t` 来方便地获取翻译。
t = LanguageManager()