"""
dialogs.py
对话框模块

提供各种对话框的实现，包括保存文件组、删除确认等
"""

import customtkinter as ctk
from ..defines import (
    DIALOG_SAVE_WIDTH,
    DIALOG_SAVE_HEIGHT,
    DIALOG_DELETE_WIDTH,
    DIALOG_DELETE_HEIGHT,
    TEXT_SAVE_GROUP_TITLE,
    TEXT_SAVE_GROUP_PROMPT,
    TEXT_SAVE,
    TEXT_CANCEL,
    TEXT_DELETE_GROUP_TITLE,
    TEXT_DELETE_GROUP_PROMPT,
)
from ..utils import Fonts


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
        
        # 提示文字
        label = ctk.CTkLabel(
            self.dialog,
            text=TEXT_SAVE_GROUP_PROMPT,
            font=Fonts.dialog_title()
        )
        label.pack(pady=(25, 10))
        
        # 输入框
        self.entry = ctk.CTkEntry(self.dialog, width=250, height=38)
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
            corner_radius=6,
            command=self._on_cancel
        ).pack(side="left", padx=12)
        
        # 保存按钮
        ctk.CTkButton(
            btn_frame,
            text=TEXT_SAVE,
            font=Fonts.small(),
            height=30,
            width=60,
            corner_radius=6,
            fg_color="#27ae60",
            hover_color="#1e8449",
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
        
        # 提示文字
        label = ctk.CTkLabel(
            self.dialog,
            text=TEXT_DELETE_GROUP_PROMPT.format(self.group_name),
            font=Fonts.dialog()
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
            corner_radius=6,
            command=self._on_cancel
        ).pack(side="left", padx=10)
        
        # 删除按钮
        ctk.CTkButton(
            btn_frame,
            text="删除",
            height=32,
            width=80,
            corner_radius=6,
            fg_color="#e74c3c",
            hover_color="#c0392b",
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
