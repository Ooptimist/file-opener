"""
dialogs.py
对话框模块

提供各种对话框的实现，包括保存文件组、删除确认等
"""

import os
import customtkinter as ctk
from tkinter import filedialog
from ..defines import (
    DIALOG_SAVE_WIDTH,
    DIALOG_SAVE_HEIGHT,
    DIALOG_DELETE_WIDTH,
    DIALOG_DELETE_HEIGHT,
    DIALOG_EDIT_WIDTH,
    DIALOG_EDIT_HEIGHT,
    FILE_DIALOG_TITLE,
    FILE_TYPES,
    TEXT_SAVE_GROUP_TITLE,
    TEXT_SAVE_GROUP_PROMPT,
    TEXT_EDIT_GROUP_TITLE,
    TEXT_EDIT_GROUP_FILES,
    TEXT_EDIT_ADD_FILES,
    TEXT_EDIT_REMOVE_SELECTED,
    TEXT_SAVE,
    TEXT_CANCEL,
    TEXT_DELETE_GROUP_TITLE,
    TEXT_DELETE_GROUP_PROMPT,
    TEXT_CHECK_EXISTS,
    TEXT_CHECK_MISSING,
    COLOR_BG_PANEL,
    COLOR_BG_FILE_LIST,
    COLOR_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_DANGER,
    COLOR_DANGER_HOVER,
    COLOR_SECONDARY,
    COLOR_SECONDARY_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    CORNER_RADIUS_NORMAL,
)
from ..utils import Fonts, get_ui_icon


class SaveGroupDialog:
    """
    保存文件组对话框
    
    用于输入文件组名称并确认保存
    """
    
    def __init__(self, parent, on_confirm):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            on_confirm (callable): 确认回调函数，接收组名参数
        """
        self.parent = parent
        self.on_confirm = on_confirm
        self.dialog = None
        self.entry = None
        
    def show(self):
        """
        显示对话框
        """
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(TEXT_SAVE_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_SAVE_WIDTH}x{DIALOG_SAVE_HEIGHT}")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        self.dialog.configure(fg_color=COLOR_BG_PANEL)
        
        # 提示文字
        label = ctk.CTkLabel(
            self.dialog,
            text=TEXT_SAVE_GROUP_PROMPT,
            font=Fonts.dialog_title(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        label.pack(pady=(25, 10))
        
        # 输入框
        self.entry = ctk.CTkEntry(
            self.dialog,
            width=250,
            height=38,
            fg_color=COLOR_BG_FILE_LIST,
            border_color=COLOR_BORDER,
            corner_radius=CORNER_RADIUS_NORMAL,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.entry.pack(pady=8)
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        # 取消按钮
        ctk.CTkButton(
            btn_frame,
            text=TEXT_CANCEL,
            font=Fonts.small(),
            height=30,
            width=60,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            command=self._on_cancel
        ).pack(side="left", padx=12)
        
        # 保存按钮
        ctk.CTkButton(
            btn_frame,
            text=TEXT_SAVE,
            font=Fonts.small(),
            height=30,
            width=60,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            command=self._on_save
        ).pack(side="left", padx=12)
        
        # 显示对话框并聚焦输入框
        self.dialog.update_idletasks()
        self.entry.focus()
        self.dialog.deiconify()
        
        # 绑定回车键
        self.entry.bind("<Return>", lambda e: self._on_save())
    
    def _on_cancel(self):
        """取消按钮回调"""
        self.dialog.destroy()
    
    def _on_save(self):
        """保存按钮回调"""
        group_name = self.entry.get().strip()
        if group_name:
            self.on_confirm(group_name)
        self.dialog.destroy()


class DeleteConfirmDialog:
    """
    删除确认对话框
    
    用于确认删除文件组
    """
    
    def __init__(self, parent, group_name, on_confirm):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            group_name (str): 要删除的文件组名称
            on_confirm (callable): 确认回调函数
        """
        self.parent = parent
        self.group_name = group_name
        self.on_confirm = on_confirm
        self.dialog = None
        
    def show(self):
        """
        显示对话框
        """
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(TEXT_DELETE_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_DELETE_WIDTH}x{DIALOG_DELETE_HEIGHT}")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        self.dialog.configure(fg_color=COLOR_BG_PANEL)
        
        # 提示文字
        label = ctk.CTkLabel(
            self.dialog,
            text=TEXT_DELETE_GROUP_PROMPT.format(self.group_name),
            font=Fonts.dialog(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        label.pack(pady=(25, 15))
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        # 取消按钮
        ctk.CTkButton(
            btn_frame,
            text=TEXT_CANCEL,
            height=32,
            width=80,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            command=self._on_cancel
        ).pack(side="left", padx=10)
        
        # 删除按钮
        ctk.CTkButton(
            btn_frame,
            text="删除",
            height=32,
            width=80,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            command=self._on_delete
        ).pack(side="left", padx=10)
        
        # 显示对话框
        self.dialog.update_idletasks()
        self.dialog.deiconify()
    
    def _on_cancel(self):
        """取消按钮回调"""
        self.dialog.destroy()
    
    def _on_delete(self):
        """删除按钮回调"""
        self.on_confirm()
        self.dialog.destroy()


class EditGroupDialog:
    """
    编辑文件组对话框
    
    用于编辑已保存的文件组中的文件列表
    """
    
    def __init__(self, parent, group_name, current_files, on_save):
        """
        初始化对话框
        
        Args:
            parent: 父窗口
            group_name (str): 文件组名称
            current_files (list): 当前文件列表
            on_save (callable): 保存回调函数，接收新的文件列表参数
        """
        self.parent = parent
        self.group_name = group_name
        self.files = list(current_files)  # 创建副本
        self.on_save = on_save
        self.dialog = None
        self.file_checkboxes = []
        self.file_list_frame = None
        self.ui_icons = {
            "add_files": get_ui_icon("select-files", 16),
            "remove": get_ui_icon("remove", 16),
            "save": get_ui_icon("save-group", 16),
        }
    
    def show(self):
        """
        显示对话框
        """
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(f"{TEXT_EDIT_GROUP_TITLE} - {self.group_name}")
        self.dialog.geometry(f"{DIALOG_EDIT_WIDTH}x{DIALOG_EDIT_HEIGHT}")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.withdraw()
        self.dialog.configure(fg_color=COLOR_BG_PANEL)
        
        # 标题
        title_label = ctk.CTkLabel(
            self.dialog,
            text=f"{TEXT_EDIT_GROUP_TITLE}: {self.group_name}",
            font=Fonts.header(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title_label.pack(pady=(20, 10))
        
        # 文件列表区域
        list_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_BG_FILE_LIST,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        list_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 文件列表标题
        file_list_label = ctk.CTkLabel(
            list_container,
            text=TEXT_EDIT_GROUP_FILES,
            font=Fonts.normal_bold(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        file_list_label.pack(pady=(10, 5))
        
        # 可滚动文件列表
        scroll_frame = ctk.CTkScrollableFrame(
            list_container,
            label_text="",
            fg_color=COLOR_BG_FILE_LIST,
        )
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self.file_list_frame = scroll_frame
        self._update_file_list()
        
        # 按钮区域
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 添加文件按钮
        add_btn = ctk.CTkButton(
            btn_frame,
            text=TEXT_EDIT_ADD_FILES,
            image=self.ui_icons.get("add_files"),
            compound="left",
            font=Fonts.small(),
            height=35,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self._on_add_files
        )
        add_btn.grid(row=0, column=0, padx=10)
        
        # 删除选中按钮
        remove_btn = ctk.CTkButton(
            btn_frame,
            text=TEXT_EDIT_REMOVE_SELECTED,
            image=self.ui_icons.get("remove"),
            compound="left",
            font=Fonts.small(),
            height=35,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            command=self._on_remove_selected
        )
        remove_btn.grid(row=0, column=1, padx=10)
        
        # 保存按钮
        save_btn = ctk.CTkButton(
            btn_frame,
            text=TEXT_SAVE,
            image=self.ui_icons.get("save"),
            compound="left",
            font=Fonts.small(),
            height=35,
            width=80,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            command=self._on_save
        )
        save_btn.grid(row=0, column=2, padx=10)
        
        # 显示对话框
        self.dialog.update_idletasks()
        self.dialog.deiconify()
    
    def _update_file_list(self):
        """
        更新文件列表显示
        """
        if not self.file_list_frame:
            return
            
        # 清除现有列表
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        # 如果没有文件，显示提示
        if not self.files:
            no_files_label = ctk.CTkLabel(
                self.file_list_frame,
                text="暂无文件，请点击「添加文件」",
                font=Fonts.small(),
                text_color=COLOR_TEXT_MUTED,
            )
            no_files_label.pack(pady=20)
            return
        
        # 创建新的文件列表
        for idx, file_path in enumerate(self.files):
            file_name = os.path.basename(file_path)
            exists = os.path.exists(file_path)
            icon = TEXT_CHECK_EXISTS if exists else TEXT_CHECK_MISSING
            
            checkbox = ctk.CTkCheckBox(
                self.file_list_frame,
                text=f"{icon} {file_name}",
                font=Fonts.small(),
                text_color=COLOR_TEXT_PRIMARY,
                hover_color=COLOR_PRIMARY,
                fg_color=COLOR_PRIMARY,
                border_color=COLOR_BORDER,
                checkbox_width=18,
                checkbox_height=18
            )
            checkbox.pack(fill="x", padx=5, pady=2)
            checkbox.file_index = idx
            self.file_checkboxes.append(checkbox)
    
    def _on_add_files(self):
        """添加文件按钮回调"""
        files = filedialog.askopenfilenames(
            title=FILE_DIALOG_TITLE,
            filetypes=FILE_TYPES
        )
        
        if files:
            # 添加不重复的文件
            for file_path in files:
                if file_path not in self.files:
                    self.files.append(file_path)
            self._update_file_list()
    
    def _on_remove_selected(self):
        """删除选中按钮回调"""
        if not self.files:
            return
            
        checked_indices = []
        for item in self.file_checkboxes:
            # 检查是否是 CTkCheckBox（带 get 方法）
            if hasattr(item, 'get') and hasattr(item, 'file_index'):
                if item.get():
                    checked_indices.append(item.file_index)
        
        if not checked_indices:
            return
        
        # 从后往前删除，避免索引变化
        checked_indices.sort(reverse=True)
        for idx in checked_indices:
            if 0 <= idx < len(self.files):
                self.files.pop(idx)
        
        self._update_file_list()
    
    def _on_save(self):
        """保存按钮回调"""
        if self.files:
            self.on_save(self.files)
        self.dialog.destroy()
