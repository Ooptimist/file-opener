"""
utils.py
工具函数模块

提供各种通用工具函数，包括文件图标映射、应用目录管理等
"""

from typing import Literal
import customtkinter as ctk
from .defines import (
    FONT_FAMILY,
    FILE_ICONS,
    DEFAULT_FILE_ICON,
    FONT_SIZE_NORMAL,
    FONT_SIZE_SMALL,
    FONT_SIZE_GROUP_COUNT,
    FONT_SIZE_GROUP_NAME,
    FONT_SIZE_GROUP_FILE,
    FONT_SIZE_GROUP_TITLE,
    FONT_SIZE_HEADER,
    FONT_SIZE_TITLE,
    FONT_SIZE_DIALOG,
    FONT_SIZE_DIALOG_TITLE,
    FONT_SIZE_ICON,
    FONT_SIZE_TINY,
)


def get_file_icon(file_ext):
    """
    根据文件扩展名获取对应的图标
    
    Args:
        file_ext (str): 文件扩展名（包含点号，如 .txt）
    
    Returns:
        str: 对应的emoji图标
    """
    return FILE_ICONS.get(file_ext.lower(), DEFAULT_FILE_ICON)


def create_ctk_font(size, weight: Literal["normal", "bold"] = "normal"):
    """
    创建CustomTkinter字体对象
    
    Args:
        size (int): 字体大小
        weight (Literal["normal", "bold"]): 字体粗细
    
    Returns:
        ctk.CTkFont: 配置好的字体对象
    """
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


# 预定义的字体对象（常用字体）
class Fonts:
    """预定义字体集合，避免重复创建"""
    
    @staticmethod
    def title():
        """标题字体"""
        return create_ctk_font(FONT_SIZE_TITLE, "bold")
    
    @staticmethod
    def header():
        """副标题字体"""
        return create_ctk_font(FONT_SIZE_HEADER, "bold")
    
    @staticmethod
    def normal():
        """正文字体"""
        return create_ctk_font(FONT_SIZE_NORMAL)
    
    @staticmethod
    def normal_bold():
        """正文粗体"""
        return create_ctk_font(FONT_SIZE_NORMAL, "bold")
    
    @staticmethod
    def small():
        """小字体"""
        return create_ctk_font(FONT_SIZE_SMALL)
    
    @staticmethod
    def tiny():
        """极小字体"""
        return create_ctk_font(FONT_SIZE_TINY)
    
    @staticmethod
    def dialog():
        """对话框字体"""
        return create_ctk_font(FONT_SIZE_DIALOG)
    
    @staticmethod
    def dialog_title():
        """对话框标题字体"""
        return create_ctk_font(FONT_SIZE_DIALOG_TITLE, "bold")
    
    @staticmethod
    def icon():
        """图标字体"""
        return create_ctk_font(FONT_SIZE_ICON)
    
    @staticmethod
    def group_title():
        """文件组标题字体"""
        return create_ctk_font(FONT_SIZE_GROUP_TITLE, "bold")
    
    @staticmethod
    def group_name():
        """文件组名称字体"""
        return create_ctk_font(FONT_SIZE_GROUP_NAME, "bold")
    
    @staticmethod
    def group_count():
        """文件组计数字体"""
        return create_ctk_font(FONT_SIZE_GROUP_COUNT)
    
    @staticmethod
    def group_file():
        """文件列表字体"""
        return create_ctk_font(FONT_SIZE_GROUP_FILE)
