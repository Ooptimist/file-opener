# -*- mode: python ; coding: utf-8 -*-
"""
FileOpener.spec
PyInstaller 打包配置文件

使用方法：
  python -m PyInstaller --clean FileOpener.spec
或：
  build.bat (Windows)
"""

import os
import shutil

# 配置
EXE_NAME = 'FileOpener'
DIST_DIR = 'dist'
OUTPUT_EXE = os.path.join(DIST_DIR, f'{EXE_NAME}.exe')

# 如果旧EXE存在，尝试删除或重命名（解决文件占用问题）
if os.path.exists(OUTPUT_EXE):
    try:
        os.remove(OUTPUT_EXE)
        print(f"[INFO] 已删除旧EXE文件: {OUTPUT_EXE}")
    except Exception as e:
        # 如果无法删除，尝试重命名
        backup_exe = os.path.join(DIST_DIR, f'{EXE_NAME}_old.exe')
        try:
            if os.path.exists(backup_exe):
                os.remove(backup_exe)
            shutil.move(OUTPUT_EXE, backup_exe)
            print(f"[WARNING] 无法删除旧文件，已重命名为: {backup_exe}")
        except Exception as e2:
            print(f"[WARNING] 无法处理旧EXE文件: {e2}")
            print("[WARNING] 如果打包失败，请手动关闭正在运行的程序后重试")

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('icon.ico', '.')],
    hiddenimports=[
        'src',
        'src.defines',
        'src.utils',
        'src.handlers',
        'src.handlers.file_handler',
        'src.handlers.drag_drop',
        'src.handlers.group_manager',
        'src.ui',
        'src.ui.dialogs',
        'src.ui.ui_components',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=EXE_NAME,
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
    icon='icon.ico',
)

# 打包完成后尝试清理备份文件
backup_exe = os.path.join(DIST_DIR, f'{EXE_NAME}_old.exe')
if os.path.exists(backup_exe):
    try:
        os.remove(backup_exe)
        print(f"[INFO] 已清理备份文件")
    except:
        pass
