# -*- mode: python ; coding: utf-8 -*-

# ===================================================================
# Oracipher - Minimal & Safe .spec File for Troubleshooting
# ===================================================================

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# --- 1. 基础定义 ---
project_root = SPECPATH
app_name = 'Oracipher'
icon_file = os.path.join(project_root, 'images', 'logo.ico')


# --- 2. 关键数据文件 ---
# 只包含绝对必要的资源和插件
datas = [
    # 应用资源
    ('ui/assets', 'ui/assets'),
    ('language/locales', 'language/locales'),
    ('images', 'images'),
    
    # 【必需】PyQt6 图像格式插件 (为了 SVG)
    *collect_data_files('PyQt6.Qt6', subdir='plugins/imageformats'),
    
    # 【必需】PyQt6 平台插件 (为了在某些 Windows 版本上正确显示)
    *collect_data_files('PyQt6.Qt6', subdir='plugins/platforms'),
]

# .env 文件是可选的
if os.path.exists(os.path.join(project_root, '.env')):
    datas.append(('.env', '.'))


# --- 3. 二进制依赖 ---
# 包含有 C 扩展的库的动态链接库
binaries = (
    collect_dynamic_libs('pyzbar') +
    collect_dynamic_libs('cryptography') # 显式包含 cryptography 的库总是个好主意
)


# --- 4. 隐藏导入 ---
# 告诉 PyInstaller 一些它可能找不到的库
hiddenimports = [
    'pyzbar.pyzbar',
    'PyQt6.QtSvg',
    'dotenv',
    'argon2-cffi',
    'cryptography.hazmat.backends.openssl',
    'PIL.Image',
]


# --- 5. 主分析对象 ---
# 这是 PyInstaller 的核心分析步骤
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)


# --- 6. EXE 和 COLLECT 对象 ---
# 定义最终的输出
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True, # 在 COLLECT 模式下，二进制文件由 COLLECT 处理
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # GUI 程序必须是 False
    icon=icon_file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name=app_name
)