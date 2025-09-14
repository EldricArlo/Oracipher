# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
)

# --- 1. 定义项目变量 ---
# SPECPATH 是 PyInstaller 提供的变量，代表 .spec 文件所在的目录
# 我们假定 .spec 文件位于项目根目录
project_root = SPECPATH
app_name = 'Oracipher'
# 为 Windows 可执行文件准备一个 .ico 格式的图标。
# 您需要自己创建一个，例如从 icon-256.png 转换得到。
# 将其放置在项目根目录的 images 文件夹下。
icon_file = os.path.join(project_root, 'images', 'logo.ico')


# --- 2. 收集数据文件 (datas) ---
# 这是打包最重要的部分之一，需要包含所有非代码资源。
# 格式为 ('源路径', '打包后在可执行文件根目录下的目标路径')
datas = [
    # 包含所有 UI 资源：QSS 样式表、图标等
    ('ui/assets', 'ui/assets'),
    # 包含所有语言文件
    ('language/locales', 'language/locales'),
    # 包含应用程序图标和图片
    ('images', 'images'),
    # 【关键修复】包含 PyQt6 的 SVG 和其他图像格式化插件。
    # 没有这部分，打包后所有 SVG 图标将无法加载。
    *collect_data_files('PyQt6.Qt6', subdir='plugins/imageformats'),
    # 【关键修复】包含 PyQt6 的 样式 插件。
    # 这有助于确保自定义样式在不同平台（特别是Windows）上正确应用。
    *collect_data_files('PyQt6.Qt6', subdir='plugins/styles'),
]

# 【健壮性改进】仅在 .env 文件存在时才包含它，避免报错
if os.path.exists(os.path.join(project_root, '.env')):
    datas.append(('.env', '.'))


# --- 3. 收集二进制依赖 (binaries) ---
# 对于像 pyzbar 这样依赖 C 库的模块，需要手动包含其动态链接库 (.dll, .so, .dylib)。
# 使用 collect_dynamic_libs 比 collect_data_files 更可靠。
binaries = collect_dynamic_libs('pyzbar')


# --- 4. 声明隐藏导入 (hiddenimports) ---
# 有些库是动态导入的，PyInstaller 可能无法自动检测到，需要在这里明确指出。
hiddenimports = [
    'pyzbar.pyzbar',        # pyzbar 的核心模块
    'PyQt6.QtSvg',          # 明确包含 QtSvg 模块
    'dotenv',               # python-dotenv 库
    'argon2-cffi',          # argon2 加密库
    'cryptography.hazmat.backends.openssl', # cryptography 的后端
    'PIL.Image',            # Pillow 库，用于 QR 码扫描
]


# --- 5. 创建 Analysis 对象 ---
# 这是 PyInstaller 的核心，它分析项目的所有依赖。
a = Analysis(
    ['main.py'],            # 应用程序的入口脚本
    pathex=[],              # 通常留空，PyInstaller 会自动处理 Python 路径
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)


# --- 6. 创建 EXE 对象 (单文件夹模式) ---
# 这部分定义了最终生成的可执行文件的属性。
# 默认生成一个包含所有依赖项的文件夹。
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,               # 使用 UPX 压缩可执行文件，可减小体积
    upx_exclude=[],
    runtime_tmpdir=None,
    # 对于 GUI 程序，必须设置为 False，这样运行时就不会弹出黑色的命令行窗口
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file          # 【修复】使用我们之前定义的变量
)


# --- (可选) 7. 创建 COLLECT 对象 (用于单文件夹模式) ---
# 如果您想生成一个文件夹，请使用此部分并注释掉下面的单文件部分
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name
)


