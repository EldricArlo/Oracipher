# -*- mode: python ; coding: utf-8 -*-

import os
import sys
# 导入 pyzbar 模块来动态获取其安装路径
try:
    import pyzbar
except ImportError:
    # 如果环境中没有安装 pyzbar，则抛出错误提示
    raise ImportError("错误：请先在你的打包环境中安装 'pyzbar' (pip install pyzbar)，否则无法找到所需的 DLL 文件。")

block_cipher = None

# --- 主要修改部分开始 ---

# 1. 自动获取 pyzbar 库的安装路径
pyzbar_path = pyzbar.__path__[0]

# 2. 构建所需的 DLL 文件的完整路径
#    pyzbar 依赖这两个核心的 dll 文件
pyzbar_binaries = [
    (os.path.join(pyzbar_path, 'libiconv.dll'), 'pyzbar'),
    (os.path.join(pyzbar_path, 'libzbar-64.dll'), 'pyzbar')
]

# --- 主要修改部分结束 ---


a = Analysis(
    ['main.py'],
    pathex=[],
    # 3. 将上面找到的 DLL 文件列表添加到 binaries 参数中
    binaries=pyzbar_binaries,
    # datas: 直接使用相对路径。这是最简单且正确的方式。
    # PyInstaller会从 .spec 文件的位置开始查找。
    datas=[
        ('ui/assets', 'ui/assets'),
        ('language/locales', 'language/locales')
    ],
    hiddenimports=['pyzbar.pyzbar'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    # name: 确保这个名字和你的 .spec 文件名一致
    name='Oracipher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon: 这里也直接使用相对路径
    icon='D:/Project/SafeKey/images/favicon.ico'
)