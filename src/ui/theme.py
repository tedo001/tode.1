"""
ui/theme.py
────────────
Dark theme for the tode PySide6 UI — a single global stylesheet plus a palette
that the canvas painting code can share, so the app matches the product design.
"""
from __future__ import annotations

# ── palette ─────────────────────────────────────────────────────────────────
BG        = "#0e0f13"   # app background
PANEL     = "#16181d"   # panels / cards
PANEL_2   = "#1c1f26"   # raised elements (inputs, list rows)
BORDER    = "#282c34"
TEXT      = "#e6e8ec"
TEXT_MUTED = "#8b909c"
ACCENT    = "#2f6bff"   # primary blue
ACCENT_HOVER = "#3f78ff"
GREEN     = "#2ecc71"
AMBER     = "#e6a23c"
RED       = "#e5484d"
CANVAS_BG = "#101216"

APP_QSS = f"""
* {{
    font-family: "Segoe UI", "SF Pro Text", -apple-system, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QMainWindow, QDialog, QWidget {{ background: {BG}; }}

QToolBar {{
    background: {PANEL};
    border: none;
    border-bottom: 1px solid {BORDER};
    spacing: 2px;
    padding: 4px 6px;
}}
QToolBar QToolButton {{
    background: transparent;
    color: {TEXT};
    padding: 6px 10px;
    border-radius: 6px;
}}
QToolBar QToolButton:hover {{ background: {PANEL_2}; }}
QToolBar QToolButton:pressed {{ background: {BORDER}; }}

QLabel {{ background: transparent; }}

/* Buttons */
QPushButton {{
    background: {PANEL_2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 12px;
}}
QPushButton:hover {{ background: {BORDER}; }}
QPushButton:disabled {{ color: {TEXT_MUTED}; background: {PANEL}; }}
QPushButton#primary {{
    background: {ACCENT};
    border: 1px solid {ACCENT};
    color: white;
    font-weight: 600;
}}
QPushButton#primary:hover {{ background: {ACCENT_HOVER}; border-color: {ACCENT_HOVER}; }}
QPushButton#danger {{ background: transparent; color: {RED}; border: 1px solid {RED}; }}
QPushButton#danger:hover {{ background: {RED}; color: white; }}

/* Inputs */
QComboBox, QLineEdit, QDoubleSpinBox, QSpinBox, QPlainTextEdit, QTextEdit {{
    background: {PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: {ACCENT};
}}
QComboBox:hover, QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
    border-color: {ACCENT};
}}
QComboBox QAbstractItemView {{
    background: {PANEL_2};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    outline: none;
}}

/* Lists / tables */
QListWidget, QTreeWidget, QTableWidget {{
    background: {PANEL_2};
    border: 1px solid {BORDER};
    border-radius: 6px;
    outline: none;
}}
QListWidget::item {{ padding: 6px 8px; border-radius: 4px; }}
QListWidget::item:selected {{ background: {ACCENT}; color: white; }}
QListWidget::item:hover {{ background: {BORDER}; }}
QHeaderView::section {{
    background: {PANEL}; color: {TEXT_MUTED};
    border: none; border-bottom: 1px solid {BORDER}; padding: 6px;
}}
QTableWidget {{ gridline-color: {BORDER}; }}

/* Checkboxes / toggles */
QCheckBox {{ spacing: 8px; background: transparent; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid {BORDER}; background: {PANEL_2};
}}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}

/* Sliders */
QSlider::groove:horizontal {{
    height: 4px; background: {BORDER}; border-radius: 2px;
}}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: white; width: 14px; height: 14px;
    margin: -6px 0; border-radius: 7px;
}}

/* Progress */
QProgressBar {{
    background: {PANEL_2}; border: 1px solid {BORDER};
    border-radius: 6px; text-align: center; height: 14px;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 5px; }}

/* Status bar */
QStatusBar {{ background: {PANEL}; border-top: 1px solid {BORDER}; color: {TEXT_MUTED}; }}
QStatusBar::item {{ border: none; }}

/* Menus */
QMenu {{ background: {PANEL_2}; border: 1px solid {BORDER}; border-radius: 8px; padding: 4px; }}
QMenu::item {{ padding: 6px 24px 6px 12px; border-radius: 4px; }}
QMenu::item:selected {{ background: {ACCENT}; color: white; }}
QMenu::separator {{ height: 1px; background: {BORDER}; margin: 4px 8px; }}

/* Scrollbars */
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 5px; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}

QToolTip {{
    background: {PANEL_2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 6px;
}}
"""


def apply_theme(app) -> None:
    """Apply the dark stylesheet to a QApplication."""
    app.setStyleSheet(APP_QSS)
