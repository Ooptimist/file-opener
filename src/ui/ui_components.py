"""
ui_components.py
UI组件模块

提供各种自定义UI组件的创建和管理
"""

import os
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
    COLOR_BG_CARD,
    COLOR_BG_CARD_HOVER,
    COLOR_BG_FILE_LIST,
    COLOR_BG_FILE_ITEM,
    COLOR_BG_FILE_ITEM_HOVER,
    COLOR_BORDER,
    COLOR_BORDER_SOFT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    TEXT_EXPAND_ICON,
    TEXT_COLLAPSE_ICON,
    TEXT_CHECK_EXISTS,
    TEXT_CHECK_MISSING,
    TEXT_SELECT_FILES,
    TEXT_SAVE_GROUP,
    TEXT_REMOVE,
    TEXT_OPEN,
)
from ..utils import Fonts, get_ui_icon


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
    icon = get_ui_icon("expand", 14)
    return ctk.CTkButton(
        parent,
        text="" if icon else TEXT_EXPAND_ICON,
        image=icon,
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
        self.path_visible = False
        self._hover_job = None
        self._watchdog_job = None

        file_name = os.path.basename(file_path)

        # 创建行容器
        self.row = ctk.CTkFrame(
            parent,
            fg_color=COLOR_BG_FILE_ITEM,
            corner_radius=CORNER_RADIUS_SMALL,
            border_width=1,
            border_color=COLOR_BORDER_SOFT,
        )
        self.row.pack(fill="x", pady=3)

        # 创建复选框
        self.checkbox = ctk.CTkCheckBox(
            self.row,
            text=f"{file_icon} {file_name}",
            font=Fonts.normal(),
            text_color=COLOR_TEXT_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            fg_color=COLOR_PRIMARY,
            border_color=COLOR_BORDER_SOFT,
            checkbox_width=20,
            checkbox_height=20
        )
        self.checkbox.pack(side="left", fill="x", expand=True, padx=10, pady=7)

        # 悬停时显示完整路径（更淡文本）
        self.path_label = ctk.CTkLabel(
            self.row,
            text=self.file_path,
            font=Fonts.small(),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
            justify="left",
        )
        self.path_label.bind("<Enter>", self._on_hover, add="+")
        self.path_label.bind("<Button-1>", self._on_row_click, add="+")

        self.row.bind("<Enter>", self._on_hover)
        self.row.bind("<Leave>", self._on_leave)
        self.row.bind("<Button-1>", self._on_row_click)

        bg_canvas = getattr(self.checkbox, "_bg_canvas", None)
        box_canvas = getattr(self.checkbox, "_canvas", None)
        text_label = getattr(self.checkbox, "_text_label", None)

        if bg_canvas is not None:
            bg_canvas.bind("<Enter>", self._on_hover, add="+")
            bg_canvas.bind("<Button-1>", self._on_row_click, add="+")

        if box_canvas is not None:
            box_canvas.bind("<Enter>", self._on_hover, add="+")

        if text_label is not None:
            text_label.bind("<Enter>", self._on_hover, add="+")
            text_label.bind("<Button-1>", self._on_row_click, add="+")

    def _is_pointer_within_row(self):
        try:
            x, y = self.row.winfo_pointerxy()
            widget = self.row.winfo_containing(x, y)
        except Exception:
            return False

        while widget is not None:
            if widget == self.row:
                return True
            widget = widget.master
        return False

    def _show_path(self):
        if self.path_visible:
            return
        self.path_label.pack(fill="x", padx=14, pady=(4, 4))
        self.path_visible = True
        self._start_watchdog()

    def _hide_path(self):
        if not self.path_visible:
            return
        self.path_label.pack_forget()
        self.path_visible = False
        self._stop_watchdog()

    def _start_watchdog(self):
        if self._watchdog_job is not None:
            return

        def _tick():
            self._watchdog_job = None
            if not self.path_visible:
                return
            if not self._is_pointer_within_row():
                self.row.configure(fg_color=COLOR_BG_FILE_ITEM)
                self._hide_path()
                return
            self._watchdog_job = self.row.after(40, _tick)

        self._watchdog_job = self.row.after(40, _tick)

    def _stop_watchdog(self):
        if self._watchdog_job is None:
            return
        try:
            self.row.after_cancel(self._watchdog_job)
        except Exception:
            pass
        self._watchdog_job = None

    def _on_hover(self, _event):
        if self._hover_job is not None:
            try:
                self.row.after_cancel(self._hover_job)
            except Exception:
                pass
            self._hover_job = None
        self.row.configure(fg_color=COLOR_BG_FILE_ITEM_HOVER)
        self._show_path()

    def _on_leave(self, _event):
        def _hide_if_outside():
            self._hover_job = None
            if self._is_pointer_within_row():
                return
            self.row.configure(fg_color=COLOR_BG_FILE_ITEM)
            self._hide_path()

        if self._hover_job is not None:
            try:
                self.row.after_cancel(self._hover_job)
            except Exception:
                pass
        self._hover_job = self.row.after(20, _hide_if_outside)

    def _on_row_click(self, _event):
        """Toggle checkbox when clicking anywhere in row."""
        if self.checkbox.get():
            self.checkbox.deselect()
        else:
            self.checkbox.select()
    
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
        if self._hover_job is not None:
            try:
                self.row.after_cancel(self._hover_job)
            except Exception:
                pass
        self._stop_watchdog()
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
        self.expand_icon_img = get_ui_icon("expand", 14)
        self.collapse_icon_img = get_ui_icon("collapse", 14)
        self.folder_icon_img = get_ui_icon("folder", 16)
        self.open_icon_img = get_ui_icon("open", 14)
        self.edit_icon_img = get_ui_icon("edit", 14)
        self.delete_icon_img = get_ui_icon("remove", 14)
        
        # 创建主框架
        self.frame = ctk.CTkFrame(
            parent,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_BG_CARD,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        self.frame.grid_columnconfigure(1, weight=1)  # 组名列可拉伸
        
        # 展开/折叠按钮
        self.expand_btn = ctk.CTkButton(
            self.frame,
            text="" if self.expand_icon_img else TEXT_EXPAND_ICON,
            image=self.expand_icon_img,
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
            text=group_name,
            image=self.folder_icon_img,
            compound="left",
            font=Fonts.group_name(),
            text_color=COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        # 文件计数标签
        self.count_label = ctk.CTkLabel(
            self.frame,
            text=f"{valid_count}/{total_count}",
            font=Fonts.group_count(),
            text_color=COLOR_TEXT_MUTED
        )
        self.count_label.grid(row=0, column=2, padx=10)
        
        # 打开按钮
        open_btn = ctk.CTkButton(
            self.frame,
            text="打开",
            image=self.open_icon_img,
            compound="left",
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
            image=self.edit_icon_img,
            compound="left",
            height=BUTTON_HEIGHT_ICON,
            width=BUTTON_WIDTH_ICON,
            corner_radius=CORNER_RADIUS_SMALL,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            font=Fonts.small(),
            command=lambda: on_edit(group_name)
        )
        edit_btn.grid(row=0, column=4, padx=(PAD_X_TINY, 4))
        
        # 删除按钮
        delete_btn = ctk.CTkButton(
            self.frame,
            text="删除",
            image=self.delete_icon_img,
            compound="left",
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
            icon_img = self.collapse_icon_img if expanded else self.expand_icon_img
            fallback_text = TEXT_COLLAPSE_ICON if expanded else TEXT_EXPAND_ICON
            self.expand_btn.configure(image=icon_img, text="" if icon_img else fallback_text)
    
    def create_files_frame(self, files):
        """
        创建文件列表框架
        
        Args:
            files (list): 文件路径列表
        
        Returns:
            ctk.CTkFrame: 文件列表框架
        """
        if self.files_frame:
            self.files_frame.destroy()

        self.files_frame = ctk.CTkFrame(
            self.frame,
            fg_color=COLOR_BG_FILE_LIST,
            corner_radius=CORNER_RADIUS_SMALL,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            exists_icon = TEXT_CHECK_EXISTS if os.path.exists(file_path) else TEXT_CHECK_MISSING
            file_label = ctk.CTkLabel(
                self.files_frame,
                text=f"{exists_icon} {file_name}",
                font=Fonts.group_file(),
                text_color=COLOR_TEXT_SECONDARY,
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
