"""
file_handler.py
文件操作处理模块

负责打开文件、处理文件选择对话框等功能
"""

import os
import subprocess
from tkinter import filedialog
from ..defines import FILE_DIALOG_TITLE, FILE_TYPES


def open_single_file(file_path):
    """
    打开单个文件
    
    使用 os.startfile（Windows）或 subprocess 作为备用方案
    
    Args:
        file_path (str): 要打开的文件路径
    
    Returns:
        bool: 是否成功打开
    """
    if not os.path.exists(file_path):
        return False
    
    try:
        os.startfile(file_path)
        return True
    except Exception as e:
        print(f"os.startfile 失败: {e}")
        try:
            subprocess.Popen(["cmd", "/c", "start", "", file_path])
            return True
        except Exception as e2:
            print(f"subprocess 启动失败: {e2}")
            return False


def open_files(file_list):
    """
    批量打开文件
    
    Args:
        file_list (list): 文件路径列表
    
    Returns:
        tuple: (成功打开的数量, 失败的文件列表)
    """
    success_count = 0
    failed_files = []
    
    for file_path in file_list:
        if os.path.exists(file_path):
            if open_single_file(file_path):
                success_count += 1
            else:
                failed_files.append(file_path)
        else:
            print(f"文件不存在: {file_path}")
            failed_files.append(file_path)
    
    return success_count, failed_files


def select_files_dialog():
    """
    显示文件选择对话框
    
    Returns:
        list: 用户选择的文件路径列表（如果用户取消则返回空列表）
    """
    files = filedialog.askopenfilenames(
        title=FILE_DIALOG_TITLE,
        filetypes=FILE_TYPES
    )
    return list(files)


def filter_existing_files(file_list):
    """
    从文件列表中筛选出存在的文件
    
    Args:
        file_list (list): 文件路径列表
    
    Returns:
        list: 存在的文件路径列表
    """
    return [f for f in file_list if os.path.exists(f)]


def count_existing_files(file_list):
    """
    统计文件列表中存在的文件数量
    
    Args:
        file_list (list): 文件路径列表
    
    Returns:
        tuple: (存在的数量, 总数)
    """
    existing = sum(1 for f in file_list if os.path.exists(f))
    return existing, len(file_list)
