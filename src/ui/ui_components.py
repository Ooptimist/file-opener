"""
ui_components.py
UI组件模块

提供各种自定义UI组件的创建和管理
"""

import customtkinter as ctk
from ..defines import (
    BUTTON_HEIGHT_LARGE,
    BUTTON_HEIGHT_NORMAL,
    BUTTON_HEIGHT_ICON,
    BUTTON_WIDTH_ICON,
    CORNER_RADIUS_NORMAL,
    CORNER_RADIUS_SMALL,
    PAD_X_TINY,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    COLOR_SECONDARY,
    COLOR_SECONDARY_HOVER,
    TEXT_SELECT_FILES,
    TEXT_SAVE_GROUP,
    TEXT_REMOVE,
    TEXT_OPEN,
)
from ..utils import Fonts


def create_primary_button(parent, text, command):
    """
    创建主按钮（蓝色）
    
    Args:
        parent: 父容器
        text (str): 按钮文字
        command: 点击回调函数
    
    Returns:
        ctk.CTkButton: 创建的按钮
    """
    return ctk.CTkButton(
        parent,
        text=text,
        font=Fonts.normal_bold(),
        height=BUTTON_HEIGHT_LARGE,
        corner_radius=CORNER_RADIUS_NORMAL,
        fg_color=COLOR_PRIMARY,
        hover_color=COLOR_PRIMARY_HOVER,
        command=command
    )


def create_success_button(parent, text, command):
    """
    创建成功按钮（绿色）
    
    Args:
        parent: 父容器
        text (str): 按钮文字
        command: 点击回调函数
    
    Returns:
        ctk.CTkButton: 创建的按钮
    """
    return ctk.CTkButton(
        parent,
        text=text,
        font=Fonts.normal_bold(),
        height=BUTTON_HEIGHT_LARGE,
        corner_radius=CORNER_RADIUS_NORMAL,
        fg_color=COLOR_SUCCESS,
        hover_color=COLOR_SUCCESS_HOVER,
        command=command
    )


def create_danger_button(parent, text, command, width=None):
    """
    创建危险按钮（红色）
    
    Args:
        parent: 父容器
        text (str): 按钮文字
        command: 点击回调函数
        width (int, optional): 按钮宽度
    
    Returns:
        ctk.CTkButton: 创建的按钮
    """
    kwargs = {
        "text": text,
        "font": Fonts.small(),
        "height": BUTTON_HEIGHT_NORMAL,
        "corner_radius": CORNER_RADIUS_NORMAL,
        "fg_color": COLOR_DANGER,
        "hover_color": COLOR_DANGER_HOVER,
        "command": command
    }
    if width:
        kwargs["width"] = width
    return ctk.CTkButton(parent, **kwargs)


def create_icon_button(parent, text, command, color_type="success"):
    """
    创建图标按钮（小尺寸）
    
    Args:
        parent: 父容器
        text (str): 按钮文字
        command: 点击回调函数
        color_type (str): 颜色类型 ("success", "danger")
    
    Returns:
        ctk.CTkButton: 创建的按钮
    """
    if color_type == "success":
        fg_color = COLOR_SUCCESS
        hover_color = COLOR_SUCCESS_HOVER
    else:
        fg_color = COLOR_DANGER
        hover_color = COLOR_DANGER_HOVER
    
    return ctk.CTkButton(
        parent,
        text=text,
        height=BUTTON_HEIGHT_ICON,
        width=BUTTON_WIDTH_ICON,
        corner_radius=CORNER_RADIUS_SMALL,
        fg_color=fg_color,
        hover_color=hover_color,
        font=Fonts.small(),
        command=command
    )


def create_expand_button(parent, command):
    """
    创建展开/折叠按钮
    
    Args:
        parent: 父容器
        command: 点击回调函数
    
    Returns:
        ctk.CTkButton: 创建的按钮
    """
    return ctk.CTkButton(
        parent,
        text="▶",
        width=32,
        height=32,
        corner_radius=CORNER_RADIUS_SMALL,
        fg_color=COLOR_SECONDARY,
        hover_color=COLOR_SECONDARY_HOVER,
        font=Fonts.icon(),
        command=command
    )


class FileCheckbox:
    """
    文件复选框组件
    
    显示文件名和图标的复选框
    """
    
    def __init__(self, parent, file_path, file_icon):
        """
        初始化文件复选框
        
        Args:
            parent: 父容器
            file_path (str): 完整文件路径
            file_icon (str): 文件图标
        """
        self.file_path = file_path
        self.file_index = 0  # 需要在创建后设置
        
        import os
        file_name = os.path.basename(file_path)
        
        # 创建行容器
        self.row = ctk.CTkFrame(parent, fg_color="transparent")
        self.row.pack(fill="x", pady=2)
        
        # 创建复选框
        self.checkbox = ctk.CTkCheckBox(
            self.row,
            text=f"{file_icon} {file_name}",
            font=Fonts.normal(),
            checkbox_width=20,
            checkbox_height=20
        )
        self.checkbox.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def is_checked(self):
        """
        检查是否被选中
        
        Returns:
            bool: 是否选中
        """
        return self.checkbox.get()
    
    def destroy(self):
        """
        销毁组件
        """
        self.row.destroy()


class GroupWidget:
    """
    文件组显示组件
    
    显示文件组名称、文件数量、展开/折叠按钮和操作按钮
    """
    
    def __init__(self, parent, group_name, valid_count, total_count, 
                 on_expand, on_open, on_edit, on_delete):
        """
        初始化文件组组件
        
        Args:
            parent: 父容器
            group_name (str): 文件组名称
            valid_count (int): 存在的文件数
            total_count (int): 总文件数
            on_expand: 展开/折叠回调
            on_open: 打开组回调
            on_edit: 编辑组回调
            on_delete: 删除组回调
        """
        self.group_name = group_name
        self.files_frame = None
        self.count_label = None
        self.expand_btn = None
        
        # 创建主框架
        self.frame = ctk.CTkFrame(parent, corner_radius=CORNER_RADIUS_NORMAL, fg_color="#2b2b2b")
        self.frame.grid_columnconfigure(1, weight=1)  # 组名列可拉伸
        
        # 展开/折叠按钮
        self.expand_btn = ctk.CTkButton(
            self.frame,
            text="▶",
            width=32,
            height=32,
            corner_radius=CORNER_RADIUS_SMALL,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            font=Fonts.icon(),
            command=lambda: on_expand(group_name)
        )
        self.expand_btn.grid(row=0, column=0, padx=(10, 8), pady=8)
        
        # 组名标签
        name_label = ctk.CTkLabel(
            self.frame,
            text=f"📁 {group_name}",
            font=Fonts.group_name(),
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        # 文件计数标签
        self.count_label = ctk.CTkLabel(
            self.frame,
            text=f"{valid_count}/{total_count}",
            font=Fonts.group_count(),
            text_color="gray"
        )
        self.count_label.grid(row=0, column=2, padx=10)
        
        # 打开按钮
        open_btn = ctk.CTkButton(
            self.frame,
            text="打开",
            height=BUTTON_HEIGHT_ICON,
            width=BUTTON_WIDTH_ICON,
            corner_radius=CORNER_RADIUS_SMALL,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            font=Fonts.small(),
            command=lambda: on_open(group_name)
        )
        open_btn.grid(row=0, column=3, padx=(PAD_X_TINY, 4))
        
        # 编辑按钮
        edit_btn = ctk.CTkButton(
            self.frame,
            text="编辑",
            height=BUTTON_HEIGHT_ICON,
            width=BUTTON_WIDTH_ICON,
            corner_radius=CORNER_RADIUS_SMALL,
            fg_color="#34495e",
            hover_color="#2c3e50",
            font=Fonts.small(),
            command=lambda: on_edit(group_name)
        )
        edit_btn.grid(row=0, column=4, padx=(PAD_X_TINY, 4))
        
        # 删除按钮
        delete_btn = ctk.CTkButton(
            self.frame,
            text="删除",
            height=BUTTON_HEIGHT_ICON,
            width=BUTTON_WIDTH_ICON,
            corner_radius=CORNER_RADIUS_SMALL,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            font=Fonts.small(),
            command=lambda: on_delete(group_name)
        )
        delete_btn.grid(row=0, column=5, padx=(4, 10))
    
    def update_count(self, valid_count, total_count):
        """
        更新文件计数显示
        
        Args:
            valid_count (int): 存在的文件数
            total_count (int): 总文件数
        """
        if self.count_label:
            self.count_label.configure(text=f"{valid_count}/{total_count}")
    
    def set_expand_icon(self, expanded):
        """
        设置展开/折叠图标
        
        Args:
            expanded (bool): 是否展开
        """
        if self.expand_btn:
            icon = "▼" if expanded else "▶"
            self.expand_btn.configure(text=icon)
    
    def create_files_frame(self, files):
        """
        创建文件列表框架
        
        Args:
            files (list): 文件路径列表
        
        Returns:
            ctk.CTkFrame: 文件列表框架
        """
        import os
        from ..defines import TEXT_CHECK_EXISTS, TEXT_CHECK_MISSING
        
        if self.files_frame:
            self.files_frame.destroy()
        
        self.files_frame = ctk.CTkFrame(self.frame, fg_color="#1e1e1e", corner_radius=4)
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            exists_icon = TEXT_CHECK_EXISTS if os.path.exists(file_path) else TEXT_CHECK_MISSING
            file_label = ctk.CTkLabel(
                self.files_frame,
                text=f"{exists_icon} {file_name}",
                font=Fonts.group_file(),
                anchor="w"
            )
            file_label.pack(fill="x", padx=8, pady=2)
        
        return self.files_frame
    
    def show_files(self):
        """
        显示文件列表
        """
        if self.files_frame:
            # columnspan=6 因为有6列（展开、名称、计数、打开、编辑、删除）
            self.files_frame.grid(row=1, column=0, columnspan=6, padx=6, pady=(0, 4), sticky="ew")
    
    def hide_files(self):
        """
        隐藏文件列表
        """
        if self.files_frame:
            self.files_frame.grid_forget()
    
    def destroy(self):
        """
        销毁组件
        """
        self.frame.destroy()
