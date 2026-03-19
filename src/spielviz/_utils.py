"""Internal helpers for spielviz."""

from __future__ import annotations

import matplotlib.colors as mcolors


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    """Convert hex color string to RGBA tuple."""
    rgb = mcolors.hex2color(hex_color)
    return (*rgb, alpha)


def truncate_label(label: str, max_len: int = 12) -> str:
    """Truncate a label string for display, keeping the end."""
    if len(label) <= max_len:
        return label
    return "..." + label[-(max_len - 3):]
