"""
tkdnd_drop_zone.py
基于 tkinterdnd2 的文件拖拽区域模块

特点：
- 不使用窗口过程子类化，避免 Win32 WndProc 相关闪退风险
- 仅在指定目标控件中放开鼠标时生效
- 回调输出与按钮选文件一致（文件路径列表）
"""

import os
from tkinterdnd2 import DND_FILES


class TkDnDDropZone:
    """为指定控件注册文件拖拽能力（tkdnd）。"""

    def __init__(self, target_widget, on_files_dropped):
        self.target_widget = target_widget
        self.on_files_dropped = on_files_dropped

    def setup(self):
        self.target_widget.drop_target_register(DND_FILES)
        self.target_widget.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event):
        files = self._parse_drop_data(event.data)
        if files:
            self.on_files_dropped(files)

    def _parse_drop_data(self, data):
        """
        解析 tkdnd 的 drop 数据。

        event.data 可能是：
        - 单个路径
        - 多个路径（空格分隔）
        - 含空格路径（花括号包裹）
        """
        if not data:
            return []

        try:
            raw_paths = list(self.target_widget.tk.splitlist(data))
        except Exception:
            raw_paths = [data]

        files = []
        for path in raw_paths:
            p = path.strip().strip("{}")
            if not p:
                continue
            if os.path.isfile(p):
                files.append(p)
        return files
