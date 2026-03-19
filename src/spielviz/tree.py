"""Game tree traversal and layout algorithms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TreeNode:
    """A node in the game tree with layout information."""

    state_str: str
    player: int  # -1=chance, -4=terminal, 0+=player
    actions: List[int] = field(default_factory=list)
    action_strings: List[str] = field(default_factory=list)
    children: List["TreeNode"] = field(default_factory=list)
    x: float = 0.0
    y: float = 0.0
    info_state: Optional[str] = None
    returns: Optional[List[float]] = None
    depth: int = 0
    chance_probs: Optional[List[float]] = None  # probabilities for chance actions


def build_tree(game, max_depth: Optional[int] = None) -> TreeNode:
    """Walk the game tree from the initial state, building a TreeNode hierarchy.

    Args:
        game: pyspiel.Game instance.
        max_depth: Optional depth limit for large games.

    Returns:
        Root TreeNode with all children populated.
    """
    state = game.new_initial_state()
    num_players = game.num_players()
    return _build_node(state, num_players, depth=0, max_depth=max_depth)


def _build_node(state, num_players: int, depth: int, max_depth: Optional[int]) -> TreeNode:
    """Recursively build a tree node from an OpenSpiel state."""
    node = TreeNode(
        state_str=str(state),
        player=state.current_player(),
        depth=depth,
    )

    if state.is_terminal():
        node.player = -4
        node.returns = list(state.returns())
        return node

    if max_depth is not None and depth >= max_depth:
        return node

    # Collect info state for player nodes
    if not state.is_chance_node() and node.player >= 0:
        node.info_state = state.information_state_string(node.player)

    if state.is_chance_node():
        outcomes = state.chance_outcomes()
        actions = [a for a, _ in outcomes]
        probs = [p for _, p in outcomes]
        node.actions = actions
        node.action_strings = [state.action_to_string(state.current_player(), a) for a in actions]
        node.chance_probs = probs
    else:
        actions = state.legal_actions()
        node.actions = actions
        node.action_strings = [state.action_to_string(node.player, a) for a in actions]

    for action in node.actions:
        child_state = state.child(action)
        child = _build_node(child_state, num_players, depth + 1, max_depth)
        node.children.append(child)

    return node


def layout_tree(root: TreeNode, algorithm: str = "simple") -> TreeNode:
    """Compute (x, y) positions for all nodes.

    Args:
        root: Root TreeNode from build_tree().
        algorithm: "simple" for layered layout (MVP).

    Returns:
        Same tree with x, y coordinates populated.
    """
    if algorithm == "simple":
        _simple_layout(root)
    else:
        raise ValueError(f"Unknown layout algorithm: {algorithm}")
    return root


_leaf_counter: int = 0


def _simple_layout(root: TreeNode) -> None:
    """Simple layered layout: y=depth, leaves placed left-to-right, parents centered."""
    counter = [0]  # mutable counter for leaf positions

    def _assign(node: TreeNode) -> None:
        node.y = node.depth
        if not node.children:
            node.x = counter[0]
            counter[0] += 1
        else:
            for child in node.children:
                _assign(child)
            node.x = sum(c.x for c in node.children) / len(node.children)

    _assign(root)


def collect_info_sets(root: TreeNode) -> Dict[str, List[TreeNode]]:
    """Group nodes by information state string.

    Returns:
        Dict mapping info_state_string -> list of TreeNodes in that info set.
    """
    info_sets: Dict[str, List[TreeNode]] = {}

    def _collect(node: TreeNode) -> None:
        if node.info_state is not None:
            info_sets.setdefault(node.info_state, []).append(node)
        for child in node.children:
            _collect(child)

    _collect(root)
    return info_sets
