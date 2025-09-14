# main.py

import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

from PyQt6.QtWidgets import QApplication

from app import SafeKeyApp
from config import load_settings, APP_LOG_DIR
from language import t

def setup_logging() -> None:
    """
    配置全局日志系统。
    """
    log_dir: str = APP_LOG_DIR

    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s'
        )
        
        log_file = os.path.join(log_dir, "app.log")
        
        handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        handler.setFormatter(log_formatter)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 防止重复添加 handler
        if not root_logger.handlers:
            root_logger.addHandler(handler)
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(log_formatter)
            root_logger.addHandler(console_handler)
        
        logging.info(f"日志系统初始化完成。日志将写入: {log_file}")

    except (OSError, IOError) as e:
        print(f"CRITICAL: 无法设置日志系统，路径: '{log_dir}'. 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # 在 __main__ 块中进行所有操作，这是 Python 的最佳实践
    try:
        setup_logging()

        logging.info("正在加载应用程序设置...")
        settings: Dict[str, Any] = load_settings()
        lang_code: str = settings.get('language', 'en')
        t.set_language(lang_code)
        logging.info(f"语言已设置为: {lang_code}")

        logging.info("启动 PyQt6 应用程序...")
        app = QApplication(sys.argv)
        
        window = SafeKeyApp()
        window.show()
        
        logging.info("应用程序主窗口已显示。进入事件循环。")
        sys.exit(app.exec())

    except Exception as e:
        # 捕获任何未预料到的异常，并记录下来
        if logging.getLogger().handlers:
            logging.critical("应用程序在启动或运行期间遇到未处理的异常。", exc_info=True)
        else:
            # 如果日志系统本身就没成功，至少在控制台打印出来
            print(f"CRITICAL UNHANDLED EXCEPTION: {e}", file=sys.stderr)
        sys.exit(1)