"""
dialogs.py
Dialog components for save/delete/edit group operations.
"""

import os
import ctypes
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from customtkinter.windows.widgets.scaling.scaling_tracker import ScalingTracker
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


class StableDialogToplevel(tk.Toplevel):
    """
    Plain tkinter Toplevel wrapper used to avoid CTkToplevel first-map scaling glitches.
    CTk widgets can still be embedded inside this window.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._block_update_dimensions_event = False

    def block_update_dimensions_event(self):
        self._block_update_dimensions_event = True

    def unblock_update_dimensions_event(self):
        self._block_update_dimensions_event = False


def _set_windows_dark_title_bar(dialog):
    """Apply dark titlebar on Windows to match app appearance."""
    if os.name != "nt":
        return
    try:
        hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
        value = ctypes.c_int(1)
        # Windows 10 20H1+ attribute id
        if ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
        ) != 0:
            # Older Windows builds fallback attribute id
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 19, ctypes.byref(value), ctypes.sizeof(value)
            )
    except Exception:
        pass


def _configure_dialog_window(dialog):
    """Apply shared window styling compatible with tkinter.Toplevel."""
    try:
        dialog.configure(bg=COLOR_BG_PANEL)
    except Exception:
        pass
    dialog.after_idle(lambda d=dialog: _set_windows_dark_title_bar(d))


def _sync_dialog_scaling_with_parent(dialog, parent):
    """
    Sync dialog scaling callbacks to the parent's DPI scaling before revealing the dialog.
    This prevents first-show content re-scaling jumps.
    """
    try:
        if dialog not in ScalingTracker.window_widgets_dict:
            return

        parent_scale = ScalingTracker.window_dpi_scaling_dict.get(parent)
        if parent_scale is None:
            parent_scale = ScalingTracker.get_window_dpi_scaling(parent)

        if parent_scale is None:
            return

        previous = ScalingTracker.window_dpi_scaling_dict.get(dialog)
        if previous == parent_scale:
            return

        ScalingTracker.window_dpi_scaling_dict[dialog] = parent_scale
        try:
            dialog.block_update_dimensions_event()
        except Exception:
            pass
        ScalingTracker.update_scaling_callbacks_for_window(dialog)
    except Exception:
        pass
    finally:
        try:
            dialog.unblock_update_dimensions_event()
        except Exception:
            pass


def _resolve_dialog_size(dialog):
    """Resolve a stable dialog size for centering and animation."""
    fixed_size = getattr(dialog, "_fixed_size", None)
    if isinstance(fixed_size, (tuple, list)) and len(fixed_size) == 2:
        return max(1, int(fixed_size[0])), max(1, int(fixed_size[1]))

    dialog.update_idletasks()
    width = dialog.winfo_width() or dialog.winfo_reqwidth() or 1
    height = dialog.winfo_height() or dialog.winfo_reqheight() or 1
    return width, height


def _prime_dialog_internal_size(dialog, width, height):
    """Sync CTk internal unscaled size state with target dialog size."""
    try:
        dialog._current_width = int(width)
        dialog._current_height = int(height)
    except Exception:
        pass


def _get_center_position(parent, dialog_width, dialog_height):
    parent.update_idletasks()
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    x = max(parent_x + (parent_width - dialog_width) // 2, 0)
    y = max(parent_y + (parent_height - dialog_height) // 2, 0)
    return x, y


def _apply_dialog_geometry(dialog, width, height, x, y):
    dialog.geometry(f"{width}x{height}+{x}+{y}")


def _apply_dialog_size_keep_position(dialog, width, height):
    """Force width/height while preserving current window position."""
    try:
        x = dialog.winfo_x()
        y = dialog.winfo_y()
    except Exception:
        x, y = 0, 0
    _apply_dialog_geometry(dialog, width, height, x, y)


def _center_dialog_to_parent(dialog, parent, dialog_width=None, dialog_height=None):
    """Center a dialog relative to its parent window."""
    if dialog_width is None or dialog_height is None:
        dialog_width, dialog_height = _resolve_dialog_size(dialog)
    x, y = _get_center_position(parent, dialog_width, dialog_height)
    _apply_dialog_geometry(dialog, dialog_width, dialog_height, x, y)
    return x, y


def _dialog_is_visible(dialog):
    if not dialog.winfo_exists():
        return False
    try:
        return dialog.state() == "normal"
    except Exception:
        return False


def _cancel_dialog_jobs(dialog):
    jobs = getattr(dialog, "_show_anim_jobs", [])
    for job_id in jobs:
        try:
            dialog.after_cancel(job_id)
        except Exception:
            pass
    dialog._show_anim_jobs = []


def _register_dialog_job(dialog, job_id):
    if not hasattr(dialog, "_show_anim_jobs"):
        dialog._show_anim_jobs = []
    dialog._show_anim_jobs.append(job_id)


def _schedule_center_corrections(dialog, parent, width, height, delays_ms):
    """Schedule one-shot geometry corrections to absorb async WM size adjustments."""
    def _fix():
        if not _dialog_is_visible(dialog):
            return
        _center_dialog_to_parent(dialog, parent, dialog_width=width, dialog_height=height)

    for delay in delays_ms:
        if delay <= 0:
            job_id = dialog.after_idle(_fix)
        else:
            job_id = dialog.after(delay, _fix)
        _register_dialog_job(dialog, job_id)


def _start_transient_size_lock(dialog, width, height, duration_ms=220, interval_ms=16):
    """Temporarily enforce dialog size to absorb async WM/CTk size rewrites."""
    if duration_ms <= 0:
        return

    token = object()
    dialog._size_lock_token = token
    steps = max(1, int(duration_ms / max(1, interval_ms)))

    def _tick(remaining):
        if getattr(dialog, "_size_lock_token", None) is not token:
            return
        if not _dialog_is_visible(dialog):
            return

        _apply_dialog_size_keep_position(dialog, width, height)

        if remaining > 0:
            job_id = dialog.after(interval_ms, lambda: _tick(remaining - 1))
            _register_dialog_job(dialog, job_id)

    _tick(steps)


def _ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def _warm_dialog_offscreen_once(dialog):
    """Warm first map/render cycle offscreen once to avoid startup and first-show flicker."""
    if dialog is None or not dialog.winfo_exists():
        return False
    if getattr(dialog, "_is_warmed", False):
        return False

    original_state = None
    try:
        original_state = dialog.state()
    except Exception:
        pass
    try:
        original_alpha = dialog.attributes("-alpha")
    except Exception:
        original_alpha = 1.0

    _cancel_dialog_jobs(dialog)

    try:
        dialog.attributes("-alpha", 0.0)
    except Exception:
        pass

    width, height = _resolve_dialog_size(dialog)

    try:
        dialog.geometry(f"{width}x{height}+32000+32000")

        dialog.deiconify()
        parent = getattr(dialog, "master", None)
        if parent is not None:
            _sync_dialog_scaling_with_parent(dialog, parent)
        dialog.update_idletasks()
        try:
            dialog.update()
        except Exception:
            pass
        dialog.withdraw()
    finally:
        # Keep stable target size for the next visible show.
        dialog.geometry(f"{width}x{height}")

        try:
            if original_state == "normal":
                dialog.deiconify()
            else:
                dialog.withdraw()
        except Exception:
            pass

        try:
            dialog.attributes("-alpha", original_alpha)
        except Exception:
            try:
                dialog.attributes("-alpha", 1.0)
            except Exception:
                pass

        dialog._is_warmed = True
        return True


def _finalize_dialog_show(
    dialog,
    parent,
    focus_widget=None,
    final_geometry=None,
    target_size=None,
):
    if not _dialog_is_visible(dialog):
        return

    if final_geometry is not None:
        width, height, x, y = final_geometry
        _apply_dialog_geometry(dialog, width, height, x, y)

    # Ensure final position is centered even after animation timing/render jitter.
    if target_size is not None:
        _center_dialog_to_parent(
            dialog,
            parent,
            dialog_width=target_size[0],
            dialog_height=target_size[1],
        )
    else:
        _center_dialog_to_parent(dialog, parent)

    try:
        dialog.attributes("-alpha", 1.0)
    except Exception:
        pass

    dialog.grab_set()
    if focus_widget is not None:
        try:
            focus_widget.focus_set()
        except Exception:
            pass
    _cancel_dialog_jobs(dialog)
    if target_size is not None:
        _schedule_center_corrections(
            dialog,
            parent,
            target_size[0],
            target_size[1],
            delays_ms=(0, 16),
        )


def _show_dialog_atomically(
    dialog,
    parent,
    focus_widget=None,
    reveal_delay_ms=16,
    anim_duration_ms=140,
    anim_steps=10,
    slide_offset_px=12,
    _skip_warm=False,
):
    """Show dialog with a subtle fade+slide animation after first frame is ready."""
    _cancel_dialog_jobs(dialog)
    is_first_show = not getattr(dialog, "_first_show_done", False)
    if not _skip_warm and _warm_dialog_offscreen_once(dialog):
        # Let WM finish first-map bookkeeping before the first visible reveal.
        job_id = dialog.after(
            12,
            lambda: _show_dialog_atomically(
                dialog,
                parent,
                focus_widget=focus_widget,
                reveal_delay_ms=reveal_delay_ms,
                anim_duration_ms=anim_duration_ms,
                anim_steps=anim_steps,
                slide_offset_px=slide_offset_px,
                _skip_warm=True,
            ),
        )
        _register_dialog_job(dialog, job_id)
        return

    width, height = _resolve_dialog_size(dialog)
    _prime_dialog_internal_size(dialog, width, height)
    final_x, final_y = _get_center_position(parent, width, height)

    try:
        dialog.attributes("-alpha", 0.0)
    except Exception:
        pass

    # Pre-center before mapping to avoid first-open jump from default WM position.
    _apply_dialog_geometry(dialog, width, height, final_x, final_y)

    dialog.deiconify()
    dialog.lift()
    _sync_dialog_scaling_with_parent(dialog, parent)
    dialog.update_idletasks()
    _apply_dialog_geometry(dialog, width, height, final_x, final_y)
    dialog.update_idletasks()
    try:
        dialog.update()
    except Exception:
        pass

    # Re-center once in transparent state after mapping to account for async WM corrections.
    final_x, final_y = _center_dialog_to_parent(
        dialog,
        parent,
        dialog_width=width,
        dialog_height=height,
    )
    # First show gets a longer lock to absorb CTk delayed scaling callbacks.
    _start_transient_size_lock(
        dialog,
        width,
        height,
        duration_ms=1400 if is_first_show else 260,
        interval_ms=16,
    )
    _schedule_center_corrections(dialog, parent, width, height, delays_ms=(0, 8))

    start_y = final_y + max(slide_offset_px, 0)
    _apply_dialog_geometry(dialog, width, height, final_x, start_y)

    def _run_animation():
        if not _dialog_is_visible(dialog):
            return

        if anim_steps <= 1 or anim_duration_ms <= 0:
            _finalize_dialog_show(
                dialog,
                parent=parent,
                focus_widget=focus_widget,
                final_geometry=(width, height, final_x, final_y),
                target_size=(width, height),
            )
            dialog._first_show_done = True
            return

        interval_ms = max(1, int(anim_duration_ms / anim_steps))

        for step in range(1, anim_steps + 1):
            def _tick(s=step):
                if not _dialog_is_visible(dialog):
                    return

                progress = s / anim_steps
                eased = _ease_out_cubic(progress)
                current_y = final_y + round((1 - eased) * (start_y - final_y))

                try:
                    dialog.attributes("-alpha", eased)
                except Exception:
                    pass
                _apply_dialog_geometry(dialog, width, height, final_x, current_y)

                if s == anim_steps:
                    _finalize_dialog_show(
                        dialog,
                        parent=parent,
                        focus_widget=focus_widget,
                        final_geometry=(width, height, final_x, final_y),
                        target_size=(width, height),
                    )
                    dialog._first_show_done = True

            job_id = dialog.after(step * interval_ms, _tick)
            _register_dialog_job(dialog, job_id)

    if reveal_delay_ms > 0:
        job_id = dialog.after(reveal_delay_ms, _run_animation)
        _register_dialog_job(dialog, job_id)
    else:
        _run_animation()

class SaveGroupDialog:
    def __init__(self, parent, on_confirm=None):
        self.parent = parent
        self.on_confirm = on_confirm
        self.dialog = None
        self.entry = None

    def _build_if_needed(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            return

        self.dialog = StableDialogToplevel(self.parent)
        self.dialog.title(TEXT_SAVE_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_SAVE_WIDTH}x{DIALOG_SAVE_HEIGHT}")
        self.dialog._fixed_size = (DIALOG_SAVE_WIDTH, DIALOG_SAVE_HEIGHT)
        _prime_dialog_internal_size(self.dialog, DIALOG_SAVE_WIDTH, DIALOG_SAVE_HEIGHT)
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        _configure_dialog_window(self.dialog)
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        label = ctk.CTkLabel(
            self.dialog,
            text=TEXT_SAVE_GROUP_PROMPT,
            font=Fonts.dialog_title(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        label.pack(pady=(25, 10))

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

        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text=TEXT_CANCEL,
            font=Fonts.small(),
            height=30,
            width=60,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            command=self._on_cancel,
        ).pack(side="left", padx=12)

        ctk.CTkButton(
            btn_frame,
            text=TEXT_SAVE,
            font=Fonts.small(),
            height=30,
            width=60,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            command=self._on_save,
        ).pack(side="left", padx=12)

        self.entry.bind("<Return>", lambda e: self._on_save())

    def show(self, on_confirm=None):
        if on_confirm is not None:
            self.on_confirm = on_confirm

        self._build_if_needed()

        self.entry.delete(0, "end")
        _show_dialog_atomically(self.dialog, self.parent, focus_widget=self.entry)

    def _hide(self):
        if self.dialog and self.dialog.winfo_exists():
            _cancel_dialog_jobs(self.dialog)
            self.dialog._size_lock_token = None
            try:
                self.dialog.attributes("-alpha", 1.0)
            except Exception:
                pass
            try:
                self.dialog.grab_release()
            except Exception:
                pass
            self.dialog.withdraw()

    def _on_cancel(self):
        self._hide()

    def _on_save(self):
        group_name = self.entry.get().strip()
        if group_name and self.on_confirm:
            self.on_confirm(group_name)
        self._hide()


class DeleteConfirmDialog:
    def __init__(self, parent, group_name=None, on_confirm=None):
        self.parent = parent
        self.group_name = group_name or ""
        self.on_confirm = on_confirm
        self.dialog = None
        self.message_label = None

    def _build_if_needed(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            return

        self.dialog = StableDialogToplevel(self.parent)
        self.dialog.title(TEXT_DELETE_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_DELETE_WIDTH}x{DIALOG_DELETE_HEIGHT}")
        self.dialog._fixed_size = (DIALOG_DELETE_WIDTH, DIALOG_DELETE_HEIGHT)
        _prime_dialog_internal_size(self.dialog, DIALOG_DELETE_WIDTH, DIALOG_DELETE_HEIGHT)
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        _configure_dialog_window(self.dialog)
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.message_label = ctk.CTkLabel(
            self.dialog,
            text="",
            font=Fonts.dialog(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.message_label.pack(pady=(25, 15))

        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text=TEXT_CANCEL,
            height=32,
            width=80,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_SECONDARY,
            hover_color=COLOR_SECONDARY_HOVER,
            command=self._on_cancel,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="删除",
            height=32,
            width=80,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_DANGER,
            hover_color=COLOR_DANGER_HOVER,
            command=self._on_delete,
        ).pack(side="left", padx=10)

    def show(self, group_name=None, on_confirm=None):
        if group_name is not None:
            self.group_name = group_name
        if on_confirm is not None:
            self.on_confirm = on_confirm

        self._build_if_needed()
        self.message_label.configure(text=TEXT_DELETE_GROUP_PROMPT.format(self.group_name))

        _show_dialog_atomically(self.dialog, self.parent)

    def _hide(self):
        if self.dialog and self.dialog.winfo_exists():
            _cancel_dialog_jobs(self.dialog)
            self.dialog._size_lock_token = None
            try:
                self.dialog.attributes("-alpha", 1.0)
            except Exception:
                pass
            try:
                self.dialog.grab_release()
            except Exception:
                pass
            self.dialog.withdraw()

    def _on_cancel(self):
        self._hide()

    def _on_delete(self):
        if self.on_confirm:
            self.on_confirm()
        self._hide()


class EditGroupDialog:
    def __init__(self, parent, group_name=None, current_files=None, on_save=None):
        self.parent = parent
        self.group_name = group_name or ""
        self.files = list(current_files or [])
        self.on_save = on_save

        self.dialog = None
        self.title_label = None
        self.file_list_frame = None
        self.file_checkboxes = []

        self.ui_icons = {
            "add_files": get_ui_icon("select-files", 16),
            "remove": get_ui_icon("remove", 16),
            "save": get_ui_icon("save-group", 16),
        }

    def _build_if_needed(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            return

        self.dialog = StableDialogToplevel(self.parent)
        self.dialog.title(TEXT_EDIT_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_EDIT_WIDTH}x{DIALOG_EDIT_HEIGHT}")
        self.dialog._fixed_size = (DIALOG_EDIT_WIDTH, DIALOG_EDIT_HEIGHT)
        _prime_dialog_internal_size(self.dialog, DIALOG_EDIT_WIDTH, DIALOG_EDIT_HEIGHT)
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        _configure_dialog_window(self.dialog)
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.title_label = ctk.CTkLabel(
            self.dialog,
            text="",
            font=Fonts.header(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.title_label.pack(pady=(20, 10))

        list_container = ctk.CTkFrame(
            self.dialog,
            corner_radius=CORNER_RADIUS_NORMAL,
            fg_color=COLOR_BG_FILE_LIST,
            border_width=1,
            border_color=COLOR_BORDER,
        )
        list_container.pack(fill="both", expand=True, padx=20, pady=10)

        file_list_label = ctk.CTkLabel(
            list_container,
            text=TEXT_EDIT_GROUP_FILES,
            font=Fonts.normal_bold(),
            text_color=COLOR_TEXT_PRIMARY,
        )
        file_list_label.pack(pady=(10, 5))

        self.file_list_frame = ctk.CTkScrollableFrame(
            list_container,
            label_text="",
            fg_color=COLOR_BG_FILE_LIST,
        )
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(pady=(10, 20))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

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
            command=self._on_add_files,
        )
        add_btn.grid(row=0, column=0, padx=10)

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
            command=self._on_remove_selected,
        )
        remove_btn.grid(row=0, column=1, padx=10)

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
            command=self._on_save,
        )
        save_btn.grid(row=0, column=2, padx=10)

    def show(self, group_name=None, current_files=None, on_save=None):
        if group_name is not None:
            self.group_name = group_name
        if current_files is not None:
            self.files = list(current_files)
        if on_save is not None:
            self.on_save = on_save

        self._build_if_needed()
        self.dialog.title(f"{TEXT_EDIT_GROUP_TITLE} - {self.group_name}")
        self.title_label.configure(text=f"{TEXT_EDIT_GROUP_TITLE}: {self.group_name}")

        self._render_file_list()

        _show_dialog_atomically(self.dialog, self.parent)

    def _clear_file_list_widgets(self):
        self.file_checkboxes = []
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

    def _render_file_list(self):
        if not self.file_list_frame:
            return

        self._clear_file_list_widgets()

        if not self.files:
            ctk.CTkLabel(
                self.file_list_frame,
                text="暂无文件，请点击「添加文件」。",
                font=Fonts.small(),
                text_color=COLOR_TEXT_MUTED,
            ).pack(pady=20)
            return

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
                checkbox_height=18,
            )
            checkbox.pack(fill="x", padx=5, pady=2)
            checkbox.file_index = idx
            self.file_checkboxes.append(checkbox)

    def _on_add_files(self):
        files = filedialog.askopenfilenames(
            title=FILE_DIALOG_TITLE,
            filetypes=FILE_TYPES,
            parent=self.dialog,
        )

        if files:
            for file_path in files:
                if file_path not in self.files:
                    self.files.append(file_path)
            self._render_file_list()

    def _on_remove_selected(self):
        if not self.files:
            return

        checked_indices = []
        for item in self.file_checkboxes:
            if hasattr(item, "get") and hasattr(item, "file_index"):
                if item.get():
                    checked_indices.append(item.file_index)

        if not checked_indices:
            return

        checked_indices.sort(reverse=True)
        for idx in checked_indices:
            if 0 <= idx < len(self.files):
                self.files.pop(idx)

        self._render_file_list()

    def _hide(self):
        if self.dialog and self.dialog.winfo_exists():
            _cancel_dialog_jobs(self.dialog)
            self.dialog._size_lock_token = None
            try:
                self.dialog.attributes("-alpha", 1.0)
            except Exception:
                pass
            try:
                self.dialog.grab_release()
            except Exception:
                pass
            self.dialog.withdraw()

    def _on_cancel(self):
        self._hide()

    def _on_save(self):
        if self.files and self.on_save:
            self.on_save(self.files)
        self._hide()
