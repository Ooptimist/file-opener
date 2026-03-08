"""
main.py
文件批量打开工具主程序

整合所有模块，提供文件批量打开和管理功能
"""

import os
import ctypes
from ctypes import windll
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

# 导入配置
from src.defines import (
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_RESIZABLE,
    THEME_APPEARANCE,
    THEME_COLOR,
    TEXT_TITLE,
    TEXT_SELECT_FILES,
    TEXT_SAVE_GROUP,
    TEXT_REMOVE,
    TEXT_OPEN,
    TEXT_MY_GROUPS,
    TEXT_CURRENT_FILES,
    TEXT_NO_GROUPS,
    PAD_X_LARGE,
    PAD_X_NORMAL,
    PAD_Y_LARGE,
    PAD_Y_NORMAL,
    PAD_X_SMALL,
    PAD_Y_SMALL,
    CORNER_RADIUS_LARGE,
    get_icon_path,
    APP_ID,
)

# 导入工具模块
from src.utils import Fonts, get_file_icon

# 导入功能模块
from src.handlers.file_handler import (
    select_files_dialog,
    open_files,
    count_existing_files
)
from src.handlers.tkdnd_drop_zone import TkDnDDropZone
from src.handlers.group_manager import GroupManager
from src.ui.dialogs import SaveGroupDialog, DeleteConfirmDialog, EditGroupDialog
from src.ui.ui_components import GroupWidget, FileCheckbox


class FileOpenerApp(TkinterDnD.DnDWrapper, ctk.CTk):
    """
    文件批量打开工具主应用类
    """
    
    def __init__(self):
        """
        初始化应用程序
        """
        super().__init__()
        TkinterDnD._require(self)
        
        # 配置窗口基本属性
        self._setup_window()
        
        # 初始化数据
        self.selected_files = []
        self.file_checkboxes = []
        self.expanded_groups = set()
        self.group_widgets = {}
        
        # 初始化管理器
        self.group_manager = GroupManager()
        
        # 构建UI
        self._build_ui()
        
        # 初始化拖拽功能（仅文件列表区域生效）
        self.drag_drop = TkDnDDropZone(
            target_widget=self.file_list_container,
            on_files_dropped=self._on_files_dropped,
        )
        self.drag_drop.setup()
    
    def _setup_window(self):
        """
        配置窗口基本属性（标题、大小、图标等）
        """
        # 设置主题
        ctk.set_appearance_mode(THEME_APPEARANCE)
        ctk.set_default_color_theme(THEME_COLOR)
        
        # 窗口基本属性
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resizable(WINDOW_RESIZABLE, WINDOW_RESIZABLE)
        
        # 配置网格布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 设置窗口图标
        self._setup_icon()
    
    def _setup_icon(self):
        """
        设置窗口图标和任务栏图标
        """
        try:
            # 设置应用程序ID（用于Windows任务栏图标）
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
            
            # 加载图标文件
            icon_path = get_icon_path()
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                print(f"图标已加载: {icon_path}")
            else:
                print(f"图标文件不存在: {icon_path}")
                
        except Exception as e:
            print(f"图标设置失败: {e}")
    
    def _build_ui(self):
        """
        构建用户界面
        """
        # 创建标题
        self._create_title()
        
        # 创建左侧面板（文件选择和列表）
        self._create_left_panel()
        
        # 创建右侧面板（文件组列表）
        self._create_right_panel()
        
        # 更新文件组显示
        self._update_groups_panel()
    
    def _create_title(self):
        """
        创建窗口标题
        """
        title_label = ctk.CTkLabel(
            self,
            text=TEXT_TITLE,
            font=Fonts.title()
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=PAD_X_LARGE, pady=(PAD_Y_LARGE, PAD_Y_NORMAL))
    
    def _create_left_panel(self):
        """
        创建左侧面板（文件选择和列表区域）
        """
        # 主框架
        left_frame = ctk.CTkFrame(self, corner_radius=CORNER_RADIUS_LARGE)
        left_frame.grid(row=1, column=0, padx=(PAD_X_LARGE, PAD_X_SMALL), pady=PAD_Y_SMALL, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)
        
        # 顶部按钮区域
        self._create_left_buttons(left_frame)
        
        # 文件列表区域
        self._create_file_list(left_frame)
        
        # 底部操作按钮
        self._create_left_actions(left_frame)
    
    def _create_left_buttons(self, parent):
        """
        创建左侧面板顶部按钮
        
        Args:
            parent: 父容器
        """
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=0, column=0, padx=PAD_X_NORMAL, pady=(PAD_Y_NORMAL, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        # 选择文件按钮
        add_file_btn = ctk.CTkButton(
            btn_frame,
            text=TEXT_SELECT_FILES,
            font=Fonts.normal_bold(),
            height=40,
            corner_radius=8,
            command=self._add_files
        )
        add_file_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        
        # 保存文件组按钮
        save_group_btn = ctk.CTkButton(
            btn_frame,
            text=TEXT_SAVE_GROUP,
            font=Fonts.normal_bold(),
            height=40,
            corner_radius=8,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self._save_group
        )
        save_group_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")
    
    def _create_file_list(self, parent):
        """
        创建文件列表区域
        
        Args:
            parent: 父容器
        """
        list_frame = ctk.CTkFrame(parent, corner_radius=8)
        list_frame.grid(row=2, column=0, padx=PAD_X_NORMAL, pady=PAD_Y_SMALL, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        self.file_list_container = list_frame
        
        self.file_listbox = ctk.CTkScrollableFrame(
            list_frame,
            label_text=TEXT_CURRENT_FILES,
            label_font=Fonts.header()
        )
        self.file_listbox.pack(fill="both", expand=True, padx=8, pady=8)
    
    def _create_left_actions(self, parent):
        """
        创建左侧面板底部操作按钮
        
        Args:
            parent: 父容器
        """
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=PAD_X_NORMAL, pady=(PAD_Y_SMALL, PAD_Y_NORMAL))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # 移除按钮
        remove_btn = ctk.CTkButton(
            button_frame,
            text=TEXT_REMOVE,
            font=Fonts.small(),
            height=38,
            corner_radius=8,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self._remove_selected
        )
        remove_btn.grid(row=0, column=0, padx=(0, 6))
        
        # 打开按钮
        open_btn = ctk.CTkButton(
            button_frame,
            text=TEXT_OPEN,
            font=Fonts.small(),
            height=38,
            corner_radius=8,
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self._open_files
        )
        open_btn.grid(row=0, column=1, padx=(6, 0))
    
    def _create_right_panel(self):
        """
        创建右侧面板（文件组列表区域）
        """
        # 主框架
        right_frame = ctk.CTkFrame(self, corner_radius=CORNER_RADIUS_LARGE)
        right_frame.grid(row=1, column=1, padx=(PAD_X_SMALL, PAD_X_LARGE), pady=PAD_Y_SMALL, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        # 标题
        groups_title = ctk.CTkLabel(
            right_frame,
            text=TEXT_MY_GROUPS,
            font=Fonts.group_title()
        )
        groups_title.grid(row=0, column=0, padx=PAD_X_LARGE, pady=(PAD_Y_LARGE, PAD_Y_NORMAL))
        
        # 文件组列表容器
        self.groups_container = ctk.CTkScrollableFrame(right_frame)
        self.groups_container.grid(row=1, column=0, padx=PAD_X_NORMAL, pady=(0, PAD_Y_NORMAL), sticky="nsew")
        self.groups_container.grid_columnconfigure(0, weight=1)
    
    def _on_files_dropped(self, files):
        """
        处理拖拽的文件
        
        Args:
            files (list): 拖拽的文件路径列表
        """
        self._add_files_to_selection(files)

    def _add_files_to_selection(self, files):
        """
        统一添加文件到当前选择列表

        该方法被“选择文件按钮”和“拖拽文件”共用，确保行为一致。

        Args:
            files (list): 文件路径列表
        """
        if not files:
            return

        added = False
        for file_path in files:
            if not file_path:
                continue
            if not os.path.isfile(file_path):
                continue
            if file_path in self.selected_files:
                continue
            self.selected_files.append(file_path)
            added = True

        if added:
            self._update_file_list()
    
    def _add_files(self):
        """
        通过对话框添加文件
        """
        files = select_files_dialog()
        self._add_files_to_selection(files)
    
    def _update_file_list(self):
        """
        更新文件列表显示
        """
        # 清除现有列表
        for checkbox in self.file_checkboxes:
            checkbox.destroy()
        self.file_checkboxes = []
        
        # 创建新的复选框
        for idx, file_path in enumerate(self.selected_files):
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            icon = get_file_icon(file_ext)
            
            checkbox = FileCheckbox(self.file_listbox, file_path, icon)
            checkbox.file_index = idx
            self.file_checkboxes.append(checkbox)
    
    def _remove_selected(self):
        """
        移除选中的文件
        """
        # 获取选中的索引
        checked_indices = []
        for checkbox in self.file_checkboxes:
            if checkbox.is_checked():
                checked_indices.append(checkbox.file_index)
        
        if not checked_indices:
            return
        
        # 从后往前删除，避免索引变化
        checked_indices.sort(reverse=True)
        for idx in checked_indices:
            if 0 <= idx < len(self.selected_files):
                self.selected_files.pop(idx)
        
        self._update_file_list()
    
    def _open_files(self):
        """
        打开当前选中的所有文件
        """
        if not self.selected_files:
            return
        
        success_count, failed_files = open_files(self.selected_files)
        if failed_files:
            print(f"成功打开 {success_count} 个文件，{len(failed_files)} 个文件失败")
    
    def _save_group(self):
        """
        保存当前文件为文件组
        """
        if not self.selected_files:
            return
        
        def on_confirm(group_name):
            self.group_manager.add_group(group_name, self.selected_files)
            self._update_groups_panel()
        
        dialog = SaveGroupDialog(self, on_confirm)
        dialog.show()
    
    def _update_groups_panel(self):
        """
        更新文件组面板显示
        """
        groups = self.group_manager.get_all_groups()
        
        # 清理已删除的组件
        existing_groups = set(self.group_widgets.keys())
        current_groups = set(groups.keys())
        
        for group_name in existing_groups - current_groups:
            self.group_widgets[group_name].destroy()
            del self.group_widgets[group_name]
        
        # 清空容器（注意：这会销毁所有GroupWidget的frame，所以需要清空字典）
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        # 清空组件字典，因为所有frame都被销毁了，需要重新创建
        self.group_widgets.clear()
        
        # 如果没有文件组，显示提示
        if not groups:
            no_groups_label = ctk.CTkLabel(
                self.groups_container,
                text=TEXT_NO_GROUPS,
                font=Fonts.normal(),
                text_color="gray"
            )
            no_groups_label.grid(row=0, column=0, pady=40)
            return
        
        # 创建或更新文件组组件
        for idx, (group_name, files) in enumerate(groups.items()):
            valid_count, total_count = count_existing_files(files)
            
            if group_name in self.group_widgets:
                # 更新现有组件
                widget = self.group_widgets[group_name]
                widget.update_count(valid_count, total_count)
                widget.set_expand_icon(group_name in self.expanded_groups)
                
                # 处理展开/折叠的文件列表
                if group_name in self.expanded_groups:
                    if widget.files_frame is None:
                        widget.create_files_frame(files)
                    widget.show_files()
                else:
                    widget.hide_files()
                
                widget.frame.grid(row=idx, column=0, pady=3, sticky="ew")
            else:
                # 创建新组件
                widget = GroupWidget(
                    self.groups_container,
                    group_name,
                    valid_count,
                    total_count,
                    self._toggle_group_expand,
                    self._open_group,
                    self._edit_group,
                    self._delete_group
                )
                self.group_widgets[group_name] = widget
                
                # 如果默认展开
                if group_name in self.expanded_groups:
                    widget.create_files_frame(files)
                    widget.show_files()
                
                widget.frame.grid(row=idx, column=0, pady=5, sticky="ew")
    
    def _toggle_group_expand(self, group_name):
        """
        切换文件组的展开/折叠状态
        
        Args:
            group_name (str): 文件组名称
        """
        # 切换展开状态
        if group_name in self.expanded_groups:
            self.expanded_groups.remove(group_name)
            is_expanded = False
        else:
            self.expanded_groups.add(group_name)
            is_expanded = True
        
        # 只更新当前文件组的显示，不重建所有组件
        if group_name in self.group_widgets:
            widget = self.group_widgets[group_name]
            widget.set_expand_icon(is_expanded)
            
            if is_expanded:
                # 展开：创建并显示文件列表
                files = self.group_manager.get_group(group_name)
                if widget.files_frame is None:
                    widget.create_files_frame(files)
                widget.show_files()
            else:
                # 折叠：隐藏文件列表
                widget.hide_files()
    
    def _open_group(self, group_name):
        """
        打开指定文件组的所有文件
        
        Args:
            group_name (str): 文件组名称
        """
        files = self.group_manager.get_group(group_name)
        success_count, failed_files = open_files(files)
        if failed_files:
            print(f"成功打开 {success_count} 个文件，{len(failed_files)} 个文件失败")
    
    def _edit_group(self, group_name):
        """
        编辑指定文件组
        
        Args:
            group_name (str): 文件组名称
        """
        current_files = self.group_manager.get_group(group_name)
        
        def on_save(new_files):
            self.group_manager.update_group_files(group_name, new_files)
            self._update_groups_panel()
        
        dialog = EditGroupDialog(self, group_name, current_files, on_save)
        dialog.show()
    
    def _delete_group(self, group_name):
        """
        删除指定的文件组
        
        Args:
            group_name (str): 文件组名称
        """
        def on_confirm():
            self.group_manager.delete_group(group_name)
            self.expanded_groups.discard(group_name)
            if group_name in self.group_widgets:
                self.group_widgets[group_name].destroy()
                del self.group_widgets[group_name]
            self._update_groups_panel()
        
        dialog = DeleteConfirmDialog(self, group_name, on_confirm)
        dialog.show()


def main():
    """
    程序入口点
    """
    app = FileOpenerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
