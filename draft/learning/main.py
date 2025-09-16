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

