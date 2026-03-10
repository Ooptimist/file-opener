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

hiddenimports = [
    'src',
    'src.defines',
    'src.utils',
    'src.handlers',
    'src.handlers.file_handler',
    'src.handlers.drag_drop',
    'src.handlers.file_drop_zone',
    'src.handlers.tkdnd_drop_zone',
    'src.handlers.group_manager',
    'tkinterdnd2',
    'src.ui',
    'src.ui.dialogs',
    'src.ui.ui_components',
    'tkinter',
    '_tkinter',
]

datas = [('icon.ico', '.'), ('src/assets', 'assets')]
binaries = []


def collect_dir_files(src_root, dst_root):
    """Collect all files under src_root as (src_file, dst_dir) pairs."""
    pairs = []
    for root, _, files in os.walk(src_root):
        rel_dir = os.path.relpath(root, src_root)
        if rel_dir == '.':
            target_dir = dst_root
        else:
            target_dir = os.path.join(dst_root, rel_dir)
        for file_name in files:
            src_file = os.path.join(root, file_name)
            pairs.append((src_file, target_dir))
    return pairs

stdlib_dir = os.path.dirname(os.__file__)
python_root = os.path.dirname(stdlib_dir)
tkinter_dir = os.path.join(stdlib_dir, 'tkinter')
tcl_data_dir = os.path.join(python_root, 'tcl', 'tcl8.6')
tk_data_dir = os.path.join(python_root, 'tcl', 'tk8.6')

if os.path.isdir(tkinter_dir):
    datas.extend(collect_dir_files(tkinter_dir, 'tkinter'))
if os.path.isdir(tcl_data_dir):
    datas.extend(collect_dir_files(tcl_data_dir, '_tcl_data'))
if os.path.isdir(tk_data_dir):
    datas.extend(collect_dir_files(tk_data_dir, '_tk_data'))

for dll_name in ('_tkinter.pyd', 'tcl86t.dll', 'tk86t.dll'):
    dll_path = os.path.join(python_root, 'DLLs', dll_name)
    if os.path.exists(dll_path):
        binaries.append((dll_path, '.'))

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
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
