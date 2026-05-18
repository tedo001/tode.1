"""
ui/dialogs/
───────────
Application modal dialogs.

Public API::

    from ui.dialogs import (
        AboutDialog, SettingsDialog, ShortcutsDialog,
        ClassManagerDialog, ProgressDialog, ImportDialog,
    )
"""

from ui.dialogs.about_dialog import AboutDialog
from ui.dialogs.class_manager import ClassManagerDialog
from ui.dialogs.import_dialog import ImportDialog
from ui.dialogs.progress_dialog import ProgressDialog
from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.shortcuts_dialog import ShortcutsDialog

__all__ = [
    "AboutDialog",
    "ClassManagerDialog",
    "ImportDialog",
    "ProgressDialog",
    "SettingsDialog",
    "ShortcutsDialog",
]
