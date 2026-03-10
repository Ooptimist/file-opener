"""
dialogs.py
Dialog components for save/delete/edit group operations.
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


def _center_dialog_to_parent(dialog, parent):
    """Center a dialog relative to its parent window."""
    parent.update_idletasks()
    dialog.update_idletasks()

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()

    dialog_width = dialog.winfo_width()
    dialog_height = dialog.winfo_height()

    x = max(parent_x + (parent_width - dialog_width) // 2, 0)
    y = max(parent_y + (parent_height - dialog_height) // 2, 0)
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


def _show_dialog_atomically(dialog, parent, focus_widget=None, reveal_delay_ms=16):
    """Show dialog only after first frame is fully prepared."""
    try:
        dialog.attributes("-alpha", 0.0)
    except Exception:
        pass

    dialog.deiconify()
    dialog.lift()
    dialog.update_idletasks()
    try:
        dialog.update()
    except Exception:
        pass

    _center_dialog_to_parent(dialog, parent)

    if reveal_delay_ms > 0:
        dialog.after(reveal_delay_ms, lambda: _finalize_dialog_show(dialog, focus_widget))
    else:
        _finalize_dialog_show(dialog, focus_widget)


def _finalize_dialog_show(dialog, focus_widget=None):
    if not dialog.winfo_exists():
        return
    try:
        if dialog.state() != "normal":
            return
    except Exception:
        return

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


class SaveGroupDialog:
    def __init__(self, parent, on_confirm=None):
        self.parent = parent
        self.on_confirm = on_confirm
        self.dialog = None
        self.entry = None

    def _build_if_needed(self):
        if self.dialog is not None and self.dialog.winfo_exists():
            return

        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(TEXT_SAVE_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_SAVE_WIDTH}x{DIALOG_SAVE_HEIGHT}")
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        self.dialog.configure(fg_color=COLOR_BG_PANEL)
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

        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(TEXT_DELETE_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_DELETE_WIDTH}x{DIALOG_DELETE_HEIGHT}")
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        self.dialog.configure(fg_color=COLOR_BG_PANEL)
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

        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(TEXT_EDIT_GROUP_TITLE)
        self.dialog.geometry(f"{DIALOG_EDIT_WIDTH}x{DIALOG_EDIT_HEIGHT}")
        self.dialog.transient(self.parent)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        self.dialog.configure(fg_color=COLOR_BG_PANEL)
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
