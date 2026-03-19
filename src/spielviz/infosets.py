"""Information set grouping, coloring, and connection drawing."""

from __future__ import annotations

from typing import Dict, Optional

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from spielviz.tree import TreeNode, collect_info_sets


def auto_color_info_sets(
    root: TreeNode,
    player: int,
    *,
    colormap: str = "Set2",
) -> Dict[str, str]:
    """Assign distinct colors to each information set for a player.

    Args:
        root: TreeNode with info_state populated.
        player: Which player's info sets to color.
        colormap: Matplotlib colormap name.

    Returns:
        Dict mapping info_state_string -> hex color string.
        Pass directly to render_tree(highlight_info_sets=...).
    """
    all_info_sets = collect_info_sets(root)

    # Filter to the specified player's info sets
    player_info_sets = {
        k: v for k, v in all_info_sets.items()
        if any(n.player == player for n in v)
    }

    if not player_info_sets:
        return {}

    cmap = plt.get_cmap(colormap, max(len(player_info_sets), 3))
    colors = {}
    for i, info_state in enumerate(sorted(player_info_sets.keys())):
        rgba = cmap(i)
        colors[info_state] = mcolors.rgb2hex(rgba[:3])

    return colors


def draw_info_set_connections(
    ax: plt.Axes,
    root: TreeNode,
    player: int,
    *,
    style: str = "dashed",
    color: Optional[str] = None,
    alpha: float = 0.3,
    linewidth: float = 2.0,
) -> None:
    """Draw dashed lines connecting nodes in the same information set.

    This is the standard game theory notation: nodes the player
    cannot distinguish are connected by a dashed line.

    Args:
        ax: Matplotlib axes (from render_tree).
        root: Laid-out TreeNode.
        player: Which player's info sets to connect.
        style: Line style ("dashed", "dotted").
        color: Line color (None = use player color from render.py).
        alpha: Line transparency.
        linewidth: Width of connection lines.
    """
    from spielviz.render import PLAYER_COLORS

    all_info_sets = collect_info_sets(root)
    line_color = color or PLAYER_COLORS.get(player, "#808080")

    linestyle_map = {
        "dashed": "--",
        "dotted": ":",
    }
    ls = linestyle_map.get(style, "--")

    for info_state, nodes in all_info_sets.items():
        # Only draw for the specified player
        if not any(n.player == player for n in nodes):
            continue
        if len(nodes) < 2:
            continue

        # Connect consecutive pairs (sorted by x for clean lines)
        sorted_nodes = sorted(nodes, key=lambda n: n.x)
        for i in range(len(sorted_nodes) - 1):
            n1, n2 = sorted_nodes[i], sorted_nodes[i + 1]
            ax.plot(
                [n1.x, n2.x],
                [-n1.y, -n2.y],
                color=line_color,
                linestyle=ls,
                linewidth=linewidth,
                alpha=alpha,
                zorder=2,
            )
