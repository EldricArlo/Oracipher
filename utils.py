# utils.py

import sys
from pathlib import Path
from typing import Union

def resource_path(relative_path: Union[str, Path]) -> Path:
    """
    获取资源的绝对路径，无论是从源码运行还是从打包后的exe运行。
    """
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(".").resolve()

    return base_path.joinpath(relative_path)