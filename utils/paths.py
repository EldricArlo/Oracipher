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
    # 使用 hasattr 检查可以确保代码在非打包环境下安全运行。
    # PyInstaller 会在运行时动态地向 sys 模块添加 _MEIPASS 属性。
    if hasattr(sys, '_MEIPASS'):
        # --- MODIFICATION START: Replaced direct access with getattr ---
        # 使用 getattr() 来动态获取属性。
        # 这种方式对静态代码分析工具 (如 Pylance) 是友好的，
        # 因为它明确表示了这是一次运行时属性查找，从而避免了报错。
        meipass_path = getattr(sys, '_MEIPASS')
        base_path = Path(meipass_path)
        # --- MODIFICATION END ---
    else:
        # 在正常的源码环境中运行
        # 假设此文件在 utils/ 目录下，项目的根目录是上一级目录
        base_path = Path(__file__).resolve().parent.parent

    # 使用 os.path.join 确保跨平台兼容性
    return str(os.path.join(base_path, str(relative_path)))