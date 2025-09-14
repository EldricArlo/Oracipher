# main.py
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication

from app import SafeKeyApp
from config import load_settings
from language import t

def setup_logging():
    """
    配置全局日志系统。

    此函数会创建一个 `logs` 目录（如果不存在），并设置一个
    RotatingFileHandler。日志信息将被写入 `logs/app.log` 文件，
    这有助于在应用程序发布后进行调试和问题追踪。
    """
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 定义日志格式
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s'
    )
    
    # 设置日志文件处理器
    # maxBytes=5*1024*1024 表示日志文件最大为 5MB
    # backupCount=5 表示最多保留5个备份日志文件
    log_file = os.path.join(log_dir, "app.log")
    handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    handler.setFormatter(log_formatter)
    
    # 获取根日志记录器并配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # 可以设置为 DEBUG 以获取更详细的信息
    root_logger.addHandler(handler)
    
    logging.info("日志系统初始化完成。")


if __name__ == "__main__":
    # --- 步骤 1: 配置日志系统 ---
    # 这是应用程序启动后应该做的第一件事，以便后续所有模块
    # 的行为都可以被记录下来。
    setup_logging()

    # --- 步骤 2: 加载设置并设置语言 ---
    # 在创建任何UI组件之前，必须先确定要使用的语言。
    # 这样可以确保所有窗口、按钮和标签在第一次显示时
    # 就是正确的语言，避免了界面闪烁或需要手动刷新的问题。
    logging.info("正在加载应用程序设置...")
    settings = load_settings()
    lang_code = settings.get('language', 'en')
    t.set_language(lang_code)
    logging.info(f"语言已设置为: {lang_code}")

    # --- 步骤 3: 初始化并运行Qt应用程序 ---
    logging.info("启动 PyQt6 应用程序...")
    app = QApplication(sys.argv)
    
    window = SafeKeyApp()
    window.show()
    
    logging.info("应用程序主窗口已显示。进入事件循环。")
    sys.exit(app.exec())