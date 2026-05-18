"""
ui/panels/
───────────
Reusable side-panel widgets for the tode application.

Public API::

    from ui.panels import StatsPanel, TimelinePanel, ClassPanel, HistoryPanel
"""

from ui.panels.class_panel import ClassPanel
from ui.panels.history_panel import HistoryPanel
from ui.panels.stats_panel import StatsPanel
from ui.panels.timeline_panel import TimelinePanel

__all__ = [
    "ClassPanel",
    "HistoryPanel",
    "StatsPanel",
    "TimelinePanel",
]
