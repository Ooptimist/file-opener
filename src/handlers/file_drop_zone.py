"""
file_drop_zone.py
Windows 文件拖拽区域模块（独立重构版）

设计目标：
- 仅在目标控件区域内放开鼠标时生效
- 与 UI 更新解耦：窗口过程只做解析，UI 更新通过 after_idle 调度
- 稳定性优先：窗口销毁时恢复原始 WndProc，避免异常闪退
"""

import ctypes
from ctypes import byref, c_void_p, windll, wintypes
from datetime import datetime


class FileDropZone:
    """Windows 拖拽文件区域管理器。"""

    GWL_WNDPROC = -4
    WM_DROPFILES = 0x0233
    WM_COPYDATA = 0x004A
    WM_COPYGLOBALDATA = 0x0049
    MSGFLT_ALLOW = 1

    def __init__(self, root_widget, target_widget, on_files_dropped, delay_ms=150):
        self.root_widget = root_widget
        self.target_widget = target_widget
        self.on_files_dropped = on_files_dropped
        self.delay_ms = delay_ms

        self._root_hwnd = None
        self._target_hwnd = None
        self._old_wndproc = None
        self._wndproc = None
        self._installed = False

    def setup(self):
        """延迟注册，等待窗口与目标控件尺寸就绪。"""
        self.root_widget.after(self.delay_ms, self._register)

    def _register(self):
        try:
            self.root_widget.update_idletasks()

            self._root_hwnd = self.root_widget.winfo_id()
            self._target_hwnd = self.target_widget.winfo_id()

            self._configure_winapi_signatures()
            self._allow_dragdrop_messages(self._root_hwnd)

            windll.shell32.DragAcceptFiles(self._root_hwnd, True)

            self._old_wndproc = windll.user32.GetWindowLongPtrW(self._root_hwnd, self.GWL_WNDPROC)

            wndproc_type = ctypes.WINFUNCTYPE(
                ctypes.c_ssize_t,
                wintypes.HWND,
                wintypes.UINT,
                wintypes.WPARAM,
                wintypes.LPARAM,
            )

            def new_wndproc(hwnd, msg, wparam, lparam):
                try:
                    if msg == self.WM_DROPFILES:
                        self._on_drop_message(hwnd, wparam)
                        return 0
                except Exception as exc:
                    self._log_debug(f"wndproc exception: {exc}")
                return windll.user32.CallWindowProcW(self._old_wndproc, hwnd, msg, wparam, lparam)

            self._wndproc = wndproc_type(new_wndproc)
            windll.user32.SetWindowLongPtrW(
                self._root_hwnd,
                self.GWL_WNDPROC,
                ctypes.cast(self._wndproc, c_void_p).value,
            )

            self._installed = True
            self.root_widget.bind("<Destroy>", self._on_root_destroy, add="+")
            print("Drop zone registered.")
        except Exception as exc:
            self._log_debug(f"register failed: {exc}")
            print(f"Drop zone register failed: {exc}")

    def _on_drop_message(self, hwnd, hdrop):
        """处理 WM_DROPFILES（仅做轻量解析，UI 更新延迟到主循环空闲时）。"""
        try:
            if not self._is_drop_in_target(hwnd, hdrop):
                windll.shell32.DragFinish(hdrop)
                return

            files = self._extract_files(hdrop)
            windll.shell32.DragFinish(hdrop)

            if files:
                self.root_widget.after_idle(lambda f=files: self._safe_dispatch(f))
        except Exception as exc:
            try:
                windll.shell32.DragFinish(hdrop)
            except Exception:
                pass
            print(f"Drop handle failed: {exc}")
            self._log_debug(f"drop handle failed: {exc}")

    def _safe_dispatch(self, files):
        """安全回调，避免异常冒泡影响主循环。"""
        try:
            self.on_files_dropped(files)
        except Exception as exc:
            print(f"Drop callback failed: {exc}")
            self._log_debug(f"drop callback failed: {exc}")

    def _is_drop_in_target(self, hwnd, hdrop):
        point_client = wintypes.POINT()
        windll.shell32.DragQueryPoint(hdrop, byref(point_client))

        point_screen = wintypes.POINT(point_client.x, point_client.y)
        windll.user32.ClientToScreen(hwnd, byref(point_screen))

        rect = wintypes.RECT()
        windll.user32.GetWindowRect(self._target_hwnd, byref(rect))

        return (
            rect.left <= point_screen.x <= rect.right
            and rect.top <= point_screen.y <= rect.bottom
        )

    @staticmethod
    def _extract_files(hdrop):
        files = []
        count = windll.shell32.DragQueryFileW(hdrop, 0xFFFFFFFF, None, 0)
        for i in range(count):
            length = windll.shell32.DragQueryFileW(hdrop, i, None, 0)
            if length <= 0:
                continue
            buf = ctypes.create_unicode_buffer(length + 1)
            windll.shell32.DragQueryFileW(hdrop, i, buf, length + 1)
            files.append(buf.value)
        return files

    def _on_root_destroy(self, event):
        if event.widget != self.root_widget:
            return
        self.teardown()

    def teardown(self):
        """恢复原始窗口过程，避免退出时闪退。"""
        if not self._installed:
            return
        try:
            if self._root_hwnd and self._old_wndproc:
                windll.user32.SetWindowLongPtrW(self._root_hwnd, self.GWL_WNDPROC, self._old_wndproc)
        except Exception as exc:
            print(f"Drop zone teardown failed: {exc}")
            self._log_debug(f"teardown failed: {exc}")
        finally:
            self._installed = False

    def _log_debug(self, message):
        """写入轻量调试日志，便于定位偶发闪退。"""
        try:
            with open("dist/drop_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
        except Exception:
            pass

    def _configure_winapi_signatures(self):
        windll.user32.GetWindowLongPtrW.restype = c_void_p
        windll.user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, c_void_p]
        windll.user32.SetWindowLongPtrW.restype = c_void_p
        windll.user32.CallWindowProcW.argtypes = [
            c_void_p,
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        windll.user32.CallWindowProcW.restype = ctypes.c_ssize_t
        windll.user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        windll.user32.ClientToScreen.restype = wintypes.BOOL
        windll.user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        windll.user32.GetWindowRect.restype = wintypes.BOOL

        windll.shell32.DragQueryPoint.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.POINT)]
        windll.shell32.DragQueryPoint.restype = wintypes.BOOL
        windll.shell32.DragQueryFileW.argtypes = [
            wintypes.HANDLE,
            wintypes.UINT,
            wintypes.LPWSTR,
            wintypes.UINT,
        ]
        windll.shell32.DragQueryFileW.restype = wintypes.UINT
        windll.shell32.DragFinish.argtypes = [wintypes.HANDLE]
        windll.shell32.DragFinish.restype = None

    @classmethod
    def _allow_dragdrop_messages(cls, hwnd):
        try:
            change_filter = getattr(windll.user32, "ChangeWindowMessageFilterEx", None)
            if change_filter is None:
                return

            change_filter(hwnd, cls.WM_DROPFILES, cls.MSGFLT_ALLOW, None)
            change_filter(hwnd, cls.WM_COPYDATA, cls.MSGFLT_ALLOW, None)
            change_filter(hwnd, cls.WM_COPYGLOBALDATA, cls.MSGFLT_ALLOW, None)
        except Exception:
            pass
