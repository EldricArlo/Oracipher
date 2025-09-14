# utils/paths.py

import sys
import os
from pathlib import Path
from typing import Union

def resource_path(relative_path: Union[str, Path]) -> str:
    """
    获取资源的绝对路径，无论是从源码运行还是从打包后的可执行文件运行。
    
    这是与 PyInstaller 等打包工具集成的关键函数。
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # 假设此文件在 utils/ 目录下，项目的根目录是上一级目录
        base_path = Path(__file__).resolve().parent.parent

    # 使用 os.path.join 确保跨平台兼容性
    return str(os.path.join(base_path, str(relative_path)))