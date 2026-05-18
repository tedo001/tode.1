"""
ui/widgets/
───────────
Reusable Tkinter widget library.

Public API::

    from ui.widgets import (
        Tooltip, IconButton, ScrollableFrame, LabeledScale,
        ConfidenceBadge, ColorSwatch, Badge,
    )
"""

from ui.widgets.badge import Badge
from ui.widgets.color_swatch import ColorSwatch
from ui.widgets.confidence_badge import ConfidenceBadge
from ui.widgets.icon_button import IconButton
from ui.widgets.labeled_scale import LabeledScale
from ui.widgets.scrollable_frame import ScrollableFrame
from ui.widgets.tooltip import Tooltip

__all__ = [
    "Badge",
    "ColorSwatch",
    "ConfidenceBadge",
    "IconButton",
    "LabeledScale",
    "ScrollableFrame",
    "Tooltip",
]
