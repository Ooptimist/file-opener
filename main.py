import customtkinter as ctk
from tkinter import filedialog
import os
import subprocess
import json
import sys

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 现代化字体定义
FONT_TITLE = ("Microsoft YaHei", 22, "bold")
FONT_HEADER = ("Microsoft YaHei", 16, "bold")
FONT_NORMAL = ("Microsoft YaHei", 13)
FONT_SMALL = ("Microsoft YaHei", 12)
FONT_TINY = ("Microsoft YaHei", 10)
FONT_DIALOG = ("Microsoft YaHei", 14)
FONT_DIALOG_TITLE = ("Microsoft YaHei", 16, "bold")
FONT_CHECKBOX = ("Microsoft YaHei", 13)
FONT_ICON = ("Microsoft YaHei", 14)

# 文件组专用字体
FONT_GROUP_TITLE = ("Microsoft YaHei", 18, "bold")
FONT_GROUP_NAME = ("Microsoft YaHei", 14, "bold")
FONT_GROUP_COUNT = ("Microsoft YaHei", 12)
FONT_GROUP_FILE = ("Microsoft YaHei", 11)

class FileOpenerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("文件批量打开工具")
        self.geometry("1600x1000")
        self.minsize(1000, 700)
        self.resizable(True, True)
        
        # 设置窗口图标
        self._setup_icon()
        
        # 优化窗口间距
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.selected_files = []
        self.saved_groups = {}
        self.checkboxes = []
        self.expanded_groups = set()
        self.group_widgets = {}

        self.groups_file = os.path.join(get_app_dir(), "file_groups.json")
        self.load_groups()

        self.setup_ui()
        self.update_groups_panel()
        self._setup_drop()

    def _setup_icon(self):
        """设置窗口图标和任务栏图标"""
        try:
            import ctypes
            from ctypes import windll
            
            # 设置应用程序ID，这样任务栏会显示正确的图标
            app_id = "FileOpenerApp.FileOpener.1.0"
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            
            # 加载图标
            icon_path = os.path.join(get_app_dir(), "icon.ico")
            if os.path.exists(icon_path):
                # 使用tkinter的iconbitmap设置窗口图标
                self.iconbitmap(icon_path)
                print(f"图标已加载: {icon_path}")
            else:
                print(f"图标文件不存在: {icon_path}")
        except Exception as e:
            print(f"图标设置失败: {e}")

    def _setup_drop(self):
        try:
            self.after(100, self._register_drop)
        except Exception as e:
            print(f"Setup error: {e}")

    def _register_drop(self):
        try:
            import ctypes
            from ctypes import windll, wintypes, POINTER, byref, c_void_p, c_int

            GMEM_MOVEABLE = 0x0002
            WM_DROPFILES = 0x0233

            hwnd = self.winfo_id()
            windll.shell32.DragAcceptFiles(hwnd, True)

            WNDPROC = ctypes.WINFUNCTYPE(c_int, c_int, c_int, c_int, c_int)

            GWL_WNDPROC = -4
            self._old_wndproc = windll.user32.GetWindowLongPtrW(hwnd, GWL_WNDPROC)

            def new_wndproc(hwnd, msg, wparam, lparam):
                if msg == WM_DROPFILES:
                    self._process_drop(wparam)
                    return 0
                return windll.user32.CallWindowProcW(
                    self._old_wndproc, hwnd, msg, wparam, lparam)

            self._wndproc = WNDPROC(new_wndproc)
            windll.user32.SetWindowLongPtrW(
                hwnd, GWL_WNDPROC, ctypes.cast(self._wndproc, c_void_p).value)

            print("Drop registered successfully!")
        except Exception as e:
            print(f"Drop registration error: {e}")

    def _process_drop(self, hdrop):
        try:
            import ctypes
            from ctypes import windll

            num_files = windll.shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)

            files = []
            for i in range(num_files):
                length = windll.shell32.DragQueryFileW(hdrop, i, None, 0)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    windll.shell32.DragQueryFileW(hdrop, i, buf, length + 1)
                    filepath = buf.value
                    files.append(filepath)

            windll.shell32.DragFinish(hdrop)

            for f in files:
                if f and f not in self.selected_files:
                    self.selected_files.append(f)

            self.after(10, self.update_file_list)

        except Exception as e:
            print(f"Process drop error: {e}")

    def load_groups(self):
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, 'r', encoding='utf-8') as f:
                    self.saved_groups = json.load(f)
            except:
                self.saved_groups = {}

    def save_groups(self):
        with open(self.groups_file, 'w', encoding='utf-8') as f:
            json.dump(self.saved_groups, f, ensure_ascii=False, indent=2)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="📁 文件批量打开工具",
            font=ctk.CTkFont(family=FONT_TITLE[0], size=FONT_TITLE[1], weight=FONT_TITLE[2])
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(25, 15))
        
        # 优化左侧面板间距
        left_frame = ctk.CTkFrame(self, corner_radius=10)
        left_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)
        
        top_btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_btn_frame.grid(row=0, column=0, padx=15, pady=(15, 0))
        top_btn_frame.grid_columnconfigure(0, weight=1)
        top_btn_frame.grid_columnconfigure(1, weight=1)
        
        add_file_btn = ctk.CTkButton(
            top_btn_frame,
            text="📝 选择文件",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            height=40,
            corner_radius=8,
            command=self.add_files
        )
        add_file_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        
        save_group_btn = ctk.CTkButton(
            top_btn_frame,
            text="💾 保存文件组",
            font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1], weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.save_group
        )
        save_group_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        
        list_frame = ctk.CTkFrame(left_frame, corner_radius=8)
        list_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.file_listbox = ctk.CTkScrollableFrame(
            list_frame,
            label_text="当前选择的文件",
            label_font=ctk.CTkFont(family=FONT_HEADER[0], size=FONT_HEADER[1], weight=FONT_HEADER[2])
        )
        self.file_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        
        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=15, pady=(10, 15))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        remove_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ 移除",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            height=38,
            corner_radius=8,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.remove_selected
        )
        remove_btn.grid(row=0, column=0, padx=(0, 6))
        
        open_btn = ctk.CTkButton(
            button_frame,
            text="🚀 打开",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            height=38,
            corner_radius=8,
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self.open_files
        )
        open_btn.grid(row=0, column=1, padx=(6, 0))
        
        # 优化右侧面板间距
        right_frame = ctk.CTkFrame(self, corner_radius=10)
        right_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        groups_title = ctk.CTkLabel(
            right_frame,
            text="📂 我的文件组",
            font=ctk.CTkFont(family=FONT_GROUP_TITLE[0], size=FONT_GROUP_TITLE[1], weight=FONT_GROUP_TITLE[2])
        )
        groups_title.grid(row=0, column=0, padx=20, pady=(20, 15))
        
        self.groups_container = ctk.CTkScrollableFrame(right_frame)
        self.groups_container.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.groups_container.grid_columnconfigure(0, weight=1)

    def update_groups_panel(self):
        existing_groups = set(self.group_widgets.keys())
        current_groups = set(self.saved_groups.keys())

        for group_name in existing_groups - current_groups:
            self.group_widgets[group_name]['frame'].destroy()
            del self.group_widgets[group_name]

        if not self.saved_groups:
            for widget in self.groups_container.winfo_children():
                widget.destroy()
            
            no_groups = ctk.CTkLabel(
                self.groups_container,
                text="暂无保存的文件组\n\n选择文件后点击「保存文件组」",
                font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
                text_color="gray"
            )
            no_groups.grid(row=0, column=0, pady=40)
            return
        else:
            for widget in self.groups_container.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and "暂无保存的文件组" in widget.cget("text"):
                    widget.destroy()

        for idx, (group_name, files) in enumerate(self.saved_groups.items()):
            valid_count = sum(1 for f in files if os.path.exists(f))
            
            if group_name in self.group_widgets:
                # 更新现有组件
                group_frame = self.group_widgets[group_name]['frame']
                self.group_widgets[group_name]['count_label'].configure(text=f"{valid_count}/{len(files)}")
                self.group_widgets[group_name]['expand_btn'].configure(text="▼" if group_name in self.expanded_groups else "▶")
                
                # 处理展开/折叠的文件列表
                files_frame = self.group_widgets[group_name].get('files_frame')
                if group_name in self.expanded_groups:
                    if files_frame is None:
                        # 创建新的文件列表框架
                        files_frame = ctk.CTkFrame(group_frame, fg_color="#1e1e1e", corner_radius=4)
                        self.group_widgets[group_name]['files_frame'] = files_frame
                        
                        # 添加文件列表
                        for file_path in files:
                            file_name = os.path.basename(file_path)
                            exists = "✅" if os.path.exists(file_path) else "❌"
                            file_label = ctk.CTkLabel(
                                files_frame,
                                text=f"{exists} {file_name}",
                                font=ctk.CTkFont(family=FONT_GROUP_FILE[0], size=FONT_GROUP_FILE[1]),
                                anchor="w"
                            )
                            file_label.pack(fill="x", padx=8, pady=2)
                    
                    # 显示文件列表（无论新建还是已存在）
                    files_frame.grid(row=1, column=0, columnspan=5, padx=6, pady=(0, 4), sticky="ew")
                else:
                    # 折叠状态，隐藏文件列表
                    if files_frame is not None:
                        files_frame.grid_forget()
                        
                # 更新位置
                group_frame.grid(row=idx, column=0, pady=3, sticky="ew")
            else:
                # 创建新组件
                group_frame = ctk.CTkFrame(self.groups_container, corner_radius=8, fg_color="#2b2b2b")
                group_frame.grid(row=idx, column=0, pady=5, sticky="ew")
                group_frame.grid_columnconfigure(1, weight=1)

                expand_btn = ctk.CTkButton(
                    group_frame,
                    text="▶",
                    width=32,
                    height=32,
                    corner_radius=6,
                    fg_color="#34495e",
                    hover_color="#2c3e50",
                    font=ctk.CTkFont(family=FONT_ICON[0], size=FONT_ICON[1]),
                    command=lambda g=group_name: self.toggle_group_expand(g)
                )
                expand_btn.grid(row=0, column=0, padx=(10, 8), pady=8)

                name_label = ctk.CTkLabel(
                    group_frame,
                    text=f"📁 {group_name}",
                    font=ctk.CTkFont(family=FONT_GROUP_NAME[0], size=FONT_GROUP_NAME[1], weight=FONT_GROUP_NAME[2]),
                    anchor="w"
                )
                name_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

                count_label = ctk.CTkLabel(
                    group_frame,
                    text=f"{valid_count}/{len(files)}",
                    font=ctk.CTkFont(family=FONT_GROUP_COUNT[0], size=FONT_GROUP_COUNT[1]),
                    text_color="gray"
                )
                count_label.grid(row=0, column=2, padx=10)

                open_btn = ctk.CTkButton(
                    group_frame,
                    text="打开",
                    height=30,
                    width=60,
                    corner_radius=6,
                    fg_color="#27ae60",
                    hover_color="#1e8449",
                    font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
                    command=lambda g=group_name: self.open_group(g)
                )
                open_btn.grid(row=0, column=3, padx=(6, 4))

                delete_btn = ctk.CTkButton(
                    group_frame,
                    text="删除",
                    height=30,
                    width=60,
                    corner_radius=6,
                    fg_color="#e74c3c",
                    hover_color="#c0392b",
                    font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
                    command=lambda g=group_name: self.delete_group(g)
                )
                delete_btn.grid(row=0, column=4, padx=(4, 10))

                self.group_widgets[group_name] = {
                    'frame': group_frame,
                    'count_label': count_label,
                    'expand_btn': expand_btn,
                    'files_frame': None
                }

                # 如果默认展开，则显示文件列表
                if group_name in self.expanded_groups:
                    files_frame = ctk.CTkFrame(group_frame, fg_color="#1e1e1e", corner_radius=4)
                    files_frame.grid(row=1, column=0, columnspan=5, padx=6, pady=(0, 4), sticky="ew")
                    self.group_widgets[group_name]['files_frame'] = files_frame
                    
                    for file_path in files:
                        file_name = os.path.basename(file_path)
                        exists = "✅" if os.path.exists(file_path) else "❌"
                        file_label = ctk.CTkLabel(
                            files_frame,
                            text=f"{exists} {file_name}",
                            font=ctk.CTkFont(family=FONT_GROUP_FILE[0], size=FONT_GROUP_FILE[1]),
                            anchor="w"
                        )
                        file_label.pack(fill="x", padx=8, pady=2)

    def toggle_group_expand(self, group_name):
        if group_name in self.expanded_groups:
            self.expanded_groups.remove(group_name)
        else:
            self.expanded_groups.add(group_name)
        self.update_groups_panel()

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择文件",
            filetypes=[("所有文件", "*.*"), ("文本文件", "*.txt"), ("图片文件", "*.png *.jpg *.jpeg *.gif"), ("文档文件", "*.pdf *.doc *.docx")]
        )
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
            self.update_file_list()

    def update_file_list(self):
        for widget in self.file_listbox.winfo_children():
            widget.destroy()
        
        self.checkboxes = []

        for i, file_path in enumerate(self.selected_files):
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            icon = self.get_file_icon(file_ext)
            
            row = ctk.CTkFrame(self.file_listbox, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            checkbox = ctk.CTkCheckBox(
                row,
                text=f"{icon} {file_name}",
                font=ctk.CTkFont(family=FONT_NORMAL[0], size=FONT_NORMAL[1]),
                checkbox_width=20,
                checkbox_height=20
            )
            checkbox.pack(side="left", fill="x", expand=True, padx=(0, 5))
            checkbox.file_index = i
            self.checkboxes.append(checkbox)

    def get_file_icon(self, ext):
        icons = {
            ".txt": "📝", ".pdf": "📕", ".doc": "📘", ".docx": "📘",
            ".xls": "📊", ".xlsx": "📊", ".ppt": "📙", ".pptx": "📙",
            ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️",
            ".mp3": "🎵", ".mp4": "🎬", ".zip": "📦", ".rar": "📦",
            ".exe": "⚙️", ".py": "🐍", ".js": "📜", ".html": "🌐", ".css": "🎨"
        }
        return icons.get(ext, "📄")

    def remove_selected(self):
        checked = []
        for checkbox in self.checkboxes:
            if checkbox.get():
                checked.append(checkbox.file_index)
        
        if not checked:
            return
            
        checked.sort(reverse=True)
        for idx in checked:
            if 0 <= idx < len(self.selected_files):
                self.selected_files.pop(idx)
        
        self.update_file_list()

    def save_group(self):
        if not self.selected_files:
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("保存文件组")
        dialog.geometry("380x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.withdraw()

        ctk.CTkLabel(
            dialog,
            text="请输入文件组名称:",
            font=ctk.CTkFont(family=FONT_DIALOG_TITLE[0], size=FONT_DIALOG_TITLE[1])
        ).pack(pady=(25, 10))

        entry = ctk.CTkEntry(dialog, width=250, height=38)
        entry.pack(pady=8)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        def confirm():
            group_name = entry.get().strip()
            if group_name:
                self.saved_groups[group_name] = self.selected_files.copy()
                self.save_groups()
                self.update_groups_panel()
            dialog.destroy()

        ctk.CTkButton(
            btn_frame,
            text="取消",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            height=30,
            width=60,
            corner_radius=6,
            command=dialog.destroy
        ).pack(side="left", padx=12)

        ctk.CTkButton(
            btn_frame,
            text="保存",
            font=ctk.CTkFont(family=FONT_SMALL[0], size=FONT_SMALL[1]),
            height=30,
            width=60,
            corner_radius=6,
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=confirm
        ).pack(side="left", padx=12)

        dialog.update_idletasks()
        entry.focus()
        dialog.deiconify()

    def open_group(self, group_name):
        if group_name in self.saved_groups:
            files = self.saved_groups[group_name]
            valid_files = [f for f in files if os.path.exists(f)]
            
            for file_path in valid_files:
                try:
                    os.startfile(file_path)
                except:
                    try:
                        subprocess.Popen(["cmd", "/c", "start", "", file_path])
                    except:
                        pass

    def delete_group(self, group_name):
        if group_name in self.saved_groups:
            dialog = ctk.CTkToplevel(self)
            dialog.title("确认删除")
            dialog.geometry("320x130")
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(False, False)
            dialog.withdraw()

            ctk.CTkLabel(
                dialog,
                text=f"确定要删除文件组「{group_name}」吗？",
                font=ctk.CTkFont(family="Microsoft YaHei", size=14)
            ).pack(pady=(25, 15))

            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=10)

            def confirm_delete():
                del self.saved_groups[group_name]
                self.expanded_groups.discard(group_name)
                if group_name in self.group_widgets:
                    self.group_widgets[group_name]['frame'].destroy()
                    del self.group_widgets[group_name]
                self.save_groups()
                self.update_groups_panel()
                dialog.destroy()

            ctk.CTkButton(
                btn_frame,
                text="取消",
                height=32,
                width=80,
                corner_radius=6,
                command=dialog.destroy
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                btn_frame,
                text="删除",
                height=32,
                width=80,
                corner_radius=6,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=confirm_delete
            ).pack(side="left", padx=10)

            dialog.update_idletasks()
            dialog.deiconify()

    def open_files(self):
        if not self.selected_files:
            return
            
        for file_path in self.selected_files:
            if os.path.exists(file_path):
                try:
                    os.startfile(file_path)
                except:
                    try:
                        subprocess.Popen(["cmd", "/c", "start", "", file_path])
                    except:
                        pass

if __name__ == "__main__":
    app = FileOpenerApp()
    app.mainloop()
