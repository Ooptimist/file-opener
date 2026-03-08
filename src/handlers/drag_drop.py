"""
drag_drop.py
Windows 文件拖拽处理模块

处理从资源管理器拖拽文件到窗口的功能
仅在 Windows 平台上有效
"""

import ctypes
from ctypes import windll, wintypes, POINTER, byref, c_void_p, c_int
from ..defines import (
    WIN_GMEM_MOVEABLE,
    WIN_WM_DROPFILES,
    WIN_GWL_WNDPROC,
    DELAY_DROP_REGISTER,
    DELAY_UPDATE_AFTER_DROP
)


class DragDropHandler:
    """
    Windows 文件拖拽处理器
    
    使用 Windows API 实现从资源管理器拖拽文件到窗口
    """
    
    def __init__(self, widget, on_files_dropped):
        """
        初始化拖拽处理器
        
        Args:
            widget: Tkinter/CustomTkinter 窗口部件
            on_files_dropped (callable): 当文件被拖入时的回调函数，接收文件列表参数
        """
        self.widget = widget
        self.on_files_dropped = on_files_dropped
        self._old_wndproc = None
        self._wndproc = None
        
    def setup(self):
        """
        设置拖拽功能（延迟执行以确保窗口已创建）
        """
        try:
            self.widget.after(DELAY_DROP_REGISTER, self._register)
        except Exception as e:
            print(f"拖拽设置错误: {e}")
    
    def _register(self):
        """
        注册拖拽功能到 Windows 窗口
        """
        try:
            hwnd = self.widget.winfo_id()
            windll.shell32.DragAcceptFiles(hwnd, True)
            
            # 定义窗口过程回调类型
            WNDPROC = ctypes.WINFUNCTYPE(c_int, c_int, c_int, c_int, c_int)
            
            # 保存原始窗口过程
            self._old_wndproc = windll.user32.GetWindowLongPtrW(hwnd, WIN_GWL_WNDPROC)
            
            # 创建新的窗口过程
            def new_wndproc(hwnd, msg, wparam, lparam):
                if msg == WIN_WM_DROPFILES:
                    self._process_drop(wparam)
                    return 0
                return windll.user32.CallWindowProcW(
                    self._old_wndproc, hwnd, msg, wparam, lparam)
            
            self._wndproc = WNDPROC(new_wndproc)
            windll.user32.SetWindowLongPtrW(
                hwnd, WIN_GWL_WNDPROC, ctypes.cast(self._wndproc, c_void_p).value)
            
            print("拖拽功能注册成功!")
            
        except Exception as e:
            print(f"拖拽注册错误: {e}")
    
    def _process_drop(self, hdrop):
        """
        处理拖拽的文件
        
        Args:
            hdrop: Windows HDROP 句柄
        """
        try:
            # 获取拖拽的文件数量
            num_files = windll.shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
            
            files = []
            for i in range(num_files):
                # 获取每个文件的路径长度
                length = windll.shell32.DragQueryFileW(hdrop, i, None, 0)
                if length > 0:
                    # 创建缓冲区并获取文件路径
                    buf = ctypes.create_unicode_buffer(length + 1)
                    windll.shell32.DragQueryFileW(hdrop, i, buf, length + 1)
                    filepath = buf.value
                    files.append(filepath)
            
            # 释放 HDROP
            windll.shell32.DragFinish(hdrop)
            
            # 调用回调函数
            if files and self.on_files_dropped:
                # 延迟执行以确保UI更新
                self.widget.after(DELAY_UPDATE_AFTER_DROP, 
                                  lambda: self.on_files_dropped(files))
            
        except Exception as e:
            print(f"处理拖拽文件错误: {e}")
