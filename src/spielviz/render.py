"""Static rendering of game trees using matplotlib."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from spielviz.tree import TreeNode

# Colorblind-friendly color scheme
PLAYER_COLORS = {
    -1: "#808080",  # Chance: gray
    0: "#2196F3",   # Player 0: blue
    1: "#F44336",   # Player 1: red
    2: "#4CAF50",   # Player 2: green
    3: "#FF9800",   # Player 3: orange
    -4: "#000000",  # Terminal: black
}

NODE_SHAPES = {
    -1: "D",  # Chance: diamond
    -4: "s",  # Terminal: square
}
# Default for players: circle "o"


def render_tree(
    root: TreeNode,
    *,
    figsize: Optional[Tuple[float, float]] = None,
    title: Optional[str] = None,
    show_actions: bool = True,
    show_payoffs: bool = True,
    show_info_states: bool = False,
    highlight_info_sets: Optional[Dict[str, str]] = None,
    highlight_path: Optional[List[TreeNode]] = None,
    node_size: float = 200,
    font_size: float = 8,
    ax: Optional[plt.Axes] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """Render a game tree as a matplotlib figure.

    Args:
        root: Laid-out TreeNode (x, y must be populated).
        figsize: Figure size. Auto-computed if None.
        title: Optional figure title.
        show_actions: Label edges with action strings.
        show_payoffs: Show terminal payoffs.
        show_info_states: Label nodes with info state strings.
        highlight_info_sets: Dict mapping info_state -> color hex string.
        highlight_path: List of nodes to highlight.
        node_size: Marker size for nodes.
        font_size: Font size for labels.
        ax: Optional existing axes.

    Returns:
        (fig, ax) tuple.
    """
    # Collect all nodes via DFS
    all_nodes = []
    _collect_nodes(root, all_nodes)

    # Auto-compute figure size
    if figsize is None:
        xs = [n.x for n in all_nodes]
        ys = [n.y for n in all_nodes]
        width = max(max(xs) - min(xs) + 2, 6)
        height = max(max(ys) - min(ys) + 2, 4)
        figsize = (width * 1.2, height * 1.5)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.figure

    # Draw edges
    for node in all_nodes:
        for i, child in enumerate(node.children):
            ax.plot(
                [node.x, child.x],
                [-node.y, -child.y],
                color="#CCCCCC",
                linewidth=1.0,
                zorder=1,
            )
            # Action labels at edge midpoint
            if show_actions and i < len(node.action_strings):
                mid_x = (node.x + child.x) / 2
                mid_y = (-node.y + -child.y) / 2
                label = node.action_strings[i]
                # Add chance probability if available
                if node.chance_probs is not None and i < len(node.chance_probs):
                    prob = node.chance_probs[i]
                    label = f"{label} ({prob:.2g})"
                ax.text(
                    mid_x, mid_y, label,
                    fontsize=font_size - 1,
                    ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.8),
                    zorder=3,
                )

    # Draw info set highlights (background ellipses)
    if highlight_info_sets:
        from spielviz.tree import collect_info_sets
        info_sets = collect_info_sets(root)
        for info_state, color in highlight_info_sets.items():
            if info_state not in info_sets:
                continue
            nodes = info_sets[info_state]
            if len(nodes) < 1:
                continue
            xs = [n.x for n in nodes]
            ys = [-n.y for n in nodes]
            cx, cy = np.mean(xs), np.mean(ys)
            # Draw semi-transparent ellipse around the group
            if len(nodes) == 1:
                radius = 0.4
            else:
                radius = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 0.4
            ellipse = mpatches.Ellipse(
                (cx, cy), width=radius * 2, height=radius * 1.2,
                facecolor=color, alpha=0.15, edgecolor=color, linewidth=1.5,
                linestyle="--", zorder=0,
            )
            ax.add_patch(ellipse)

    # Draw highlight path
    if highlight_path and len(highlight_path) > 1:
        for i in range(len(highlight_path) - 1):
            n1, n2 = highlight_path[i], highlight_path[i + 1]
            ax.plot(
                [n1.x, n2.x], [-n1.y, -n2.y],
                color="#FFD700", linewidth=3.0, zorder=2,
            )

    # Draw nodes
    for node in all_nodes:
        color = PLAYER_COLORS.get(node.player, PLAYER_COLORS.get(0))
        marker = NODE_SHAPES.get(node.player, "o")
        ax.scatter(
            node.x, -node.y,
            c=color, s=node_size, marker=marker,
            edgecolors="white", linewidths=0.5, zorder=4,
        )

    # Draw payoffs at terminal nodes
    if show_payoffs:
        for node in all_nodes:
            if node.returns is not None:
                payoff_str = ", ".join(f"{r:+.1f}" for r in node.returns)
                ax.text(
                    node.x, -node.y - 0.35, payoff_str,
                    fontsize=font_size - 1, ha="center", va="top",
                    color="#555555", zorder=5,
                )

    # Draw info state labels
    if show_info_states:
        from spielviz._utils import truncate_label
        for node in all_nodes:
            if node.info_state is not None:
                ax.text(
                    node.x, -node.y + 0.3,
                    truncate_label(node.info_state),
                    fontsize=font_size - 2, ha="center", va="bottom",
                    color="#888888", zorder=5,
                )

    # Style
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=font_size + 4, fontweight="bold", pad=15)

    fig.tight_layout()
    return fig, ax


def save_tree(
    root: TreeNode,
    path: str,
    *,
    dpi: int = 150,
    **render_kwargs,
) -> None:
    """Render and save to file. Format inferred from extension."""
    fig, ax = render_tree(root, **render_kwargs)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def _collect_nodes(node: TreeNode, result: list) -> None:
    """DFS to collect all nodes."""
    result.append(node)
    for child in node.children:
        _collect_nodes(child, result)
