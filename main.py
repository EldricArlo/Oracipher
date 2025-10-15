# main.py

import sys
import logging
from logging.handlers import RotatingFileHandler
import os

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QImageReader, QIcon

from config import APP_LOG_DIR, load_settings
from language import t
from utils import icon_cache
from utils.paths import resource_path


def setup_logging():
    """配置全局日志记录器。"""
    if not os.path.exists(APP_LOG_DIR):
        os.makedirs(APP_LOG_DIR)

    log_file = os.path.join(APP_LOG_DIR, "oracipher.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = RotatingFileHandler(
        log_file, maxBytes=1 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info(f"Oracipher Application Starting Up (Log Level: {log_level})")
    logger.info(f"Logging configured. Log file at: {log_file}")
    logger.info("=" * 60)


def main():
    """主函数，用于启动应用程序。"""
    setup_logging()

    logger = logging.getLogger(__name__)
    app = QApplication(sys.argv)

    supported_formats = [
        f.data().decode("ascii").lower() for f in QImageReader.supportedImageFormats()
    ]
    if "svg" not in supported_formats:
        logger.critical("CRITICAL ERROR: SVG image format is NOT supported.")
        QMessageBox.critical(
            None,
            "Critical Error",
            "This application requires SVG image format support, which is missing in your current Qt installation.\nThe application will now exit.",
        )
        sys.exit(1)

    try:
        settings = load_settings()
        t.set_language(settings.get("language", "zh_CN"))
    except Exception as e:
        logger.critical(f"Failed to load settings or set language: {e}", exc_info=True)
        t.set_language("zh_CN")

    icon_cache.preload()

    from app import SafeKeyApp

    logo_path = resource_path("images/icon-256.png")
    app_icon = QIcon(logo_path)
    if app_icon.isNull():
        logger.critical(
            f"Failed to load application icon from path: {logo_path}. The icon will be missing."
        )

    app.setWindowIcon(app_icon)

    window = SafeKeyApp()
    window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
