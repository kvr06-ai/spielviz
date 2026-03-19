"""Strategy profile visualization."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from spielviz.tree import TreeNode
from spielviz.render import render_tree


def plot_strategy_profile(
    game,
    policy,
    *,
    player: int = 0,
    figsize: Optional[Tuple[float, float]] = None,
    title: Optional[str] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """Bar chart of action probabilities at each information set.

    Args:
        game: pyspiel.Game instance.
        policy: Object with action_probabilities(state, player_id) or
            action_probabilities(state) method, or a TabularPolicy.
        player: Which player's strategy to plot.
        figsize: Figure size.
        title: Figure title.

    Returns:
        (fig, ax) tuple.
    """
    # Collect info states and their action probabilities
    info_state_data = _collect_strategy_data(game, policy, player)

    if not info_state_data:
        fig, ax = plt.subplots(figsize=figsize or (6, 4))
        ax.text(0.5, 0.5, "No information sets found for this player",
                ha="center", va="center", transform=ax.transAxes)
        return fig, ax

    # Sort by depth (tree order)
    info_state_data.sort(key=lambda x: x[2])

    info_states = [d[0] for d in info_state_data]
    action_probs_list = [d[1] for d in info_state_data]

    # Gather all unique action labels
    all_action_labels = set()
    for _, probs_dict, _ in info_state_data:
        all_action_labels.update(probs_dict.keys())
    all_action_labels = sorted(all_action_labels)

    n_states = len(info_states)
    n_actions = len(all_action_labels)

    if figsize is None:
        figsize = (max(n_states * 1.5, 6), max(n_actions * 0.8, 4))

    fig, ax = plt.subplots(figsize=figsize)

    x = np.arange(n_states)
    bar_width = 0.8 / max(n_actions, 1)

    colors = plt.cm.Set2(np.linspace(0, 1, max(n_actions, 1)))

    for i, action_label in enumerate(all_action_labels):
        values = []
        for probs_dict in action_probs_list:
            values.append(probs_dict.get(action_label, 0.0))
        offset = (i - n_actions / 2 + 0.5) * bar_width
        ax.bar(x + offset, values, bar_width, label=action_label,
               color=colors[i], edgecolor="white", linewidth=0.5)

    # Truncate long info state labels
    from spielviz._utils import truncate_label
    short_labels = [truncate_label(s, max_len=15) for s in info_states]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Probability")
    ax.set_ylim(0, 1.05)
    ax.legend(title="Actions", fontsize=8, title_fontsize=9)

    if title:
        ax.set_title(title, fontweight="bold")
    else:
        ax.set_title(f"Strategy Profile — Player {player}", fontweight="bold")

    fig.tight_layout()
    return fig, ax


def plot_strategy_on_tree(
    root: TreeNode,
    game,
    policy,
    *,
    player: int = 0,
    bar_width: float = 0.3,
    bar_height: float = 0.15,
    **render_kwargs,
) -> Tuple[plt.Figure, plt.Axes]:
    """Overlay mini bar charts on decision nodes in the game tree.

    Args:
        root: Laid-out TreeNode.
        game: pyspiel.Game instance.
        policy: Policy object.
        player: Which player's strategy to overlay.
        bar_width: Width of mini bar charts.
        bar_height: Max height of bars.
        **render_kwargs: Passed to render_tree().

    Returns:
        (fig, ax) tuple.
    """
    fig, ax = render_tree(root, **render_kwargs)

    # Collect strategy data
    info_state_data = _collect_strategy_data(game, policy, player)
    info_state_probs = {d[0]: d[1] for d in info_state_data}

    # Overlay mini bars on matching nodes
    all_nodes = []
    _collect_all_nodes(root, all_nodes)

    for node in all_nodes:
        if node.player != player or node.info_state is None:
            continue
        probs_dict = info_state_probs.get(node.info_state)
        if not probs_dict:
            continue

        actions = sorted(probs_dict.keys())
        n = len(actions)
        if n == 0:
            continue

        total_width = bar_width
        single_bar_w = total_width / n
        start_x = node.x - total_width / 2

        for i, action in enumerate(actions):
            prob = probs_dict[action]
            bx = start_x + i * single_bar_w
            by = -node.y + 0.2
            h = prob * bar_height
            rect = plt.Rectangle(
                (bx, by), single_bar_w * 0.9, h,
                facecolor=plt.cm.Set2(i / max(n, 1)),
                edgecolor="white", linewidth=0.3, zorder=6,
            )
            ax.add_patch(rect)

    return fig, ax


def _collect_strategy_data(
    game, policy, player: int
) -> List[Tuple[str, Dict[str, float], int]]:
    """Walk game tree and collect action probabilities at each info set.

    Returns list of (info_state_str, {action_label: prob}, depth).
    """
    seen_info_states = set()
    results = []

    def _walk(state, depth):
        if state.is_terminal():
            return
        if state.current_player() == player:
            info_state = state.information_state_string(player)
            if info_state not in seen_info_states:
                seen_info_states.add(info_state)
                # Get action probabilities from policy
                probs = _get_action_probs(policy, state, player)
                # Convert action indices to labels
                probs_labeled = {}
                for action, prob in probs:
                    label = state.action_to_string(player, action)
                    probs_labeled[label] = prob
                results.append((info_state, probs_labeled, depth))

        for action in state.legal_actions():
            _walk(state.child(action), depth + 1)

    _walk(game.new_initial_state(), 0)
    return results


def _get_action_probs(policy, state, player: int):
    """Extract action probabilities from various policy types."""
    # Try different policy API patterns
    try:
        # TabularPolicy and similar
        probs_dict = policy.action_probabilities(state, player)
        return list(probs_dict.items())
    except TypeError:
        pass

    try:
        probs_dict = policy.action_probabilities(state)
        return list(probs_dict.items())
    except (TypeError, AttributeError):
        pass

    # Fallback: uniform over legal actions
    legal = state.legal_actions()
    p = 1.0 / len(legal) if legal else 0.0
    return [(a, p) for a in legal]


def _collect_all_nodes(node: TreeNode, result: list) -> None:
    """DFS to collect all nodes."""
    result.append(node)
    for child in node.children:
        _collect_all_nodes(child, result)
