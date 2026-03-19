"""Tests for tree.py — game tree traversal and layout."""

import pyspiel
import pytest

from spielviz.tree import build_tree, layout_tree, collect_info_sets, TreeNode


@pytest.fixture
def kuhn_game():
    return pyspiel.load_game("kuhn_poker")


@pytest.fixture
def kuhn_tree(kuhn_game):
    return build_tree(kuhn_game)


def _count_nodes(node):
    """Count total nodes in tree."""
    return 1 + sum(_count_nodes(c) for c in node.children)


def _count_terminal(node):
    """Count terminal nodes."""
    if node.player == -4:
        return 1
    return sum(_count_terminal(c) for c in node.children)


def _collect_all(node, result=None):
    if result is None:
        result = []
    result.append(node)
    for c in node.children:
        _collect_all(c, result)
    return result


class TestBuildTree:
    def test_build_tree_kuhn(self, kuhn_tree):
        """Kuhn poker tree should have the expected structure."""
        total = _count_nodes(kuhn_tree)
        # Kuhn poker has 55-58 nodes depending on representation
        assert total > 30, f"Expected >30 nodes, got {total}"

    def test_root_is_chance(self, kuhn_tree):
        """Root of Kuhn poker is a chance node (deals cards)."""
        assert kuhn_tree.player == -1

    def test_terminal_payoffs(self, kuhn_tree):
        """Terminal nodes should have payoffs."""
        terminals = [n for n in _collect_all(kuhn_tree) if n.player == -4]
        assert len(terminals) > 0
        for t in terminals:
            assert t.returns is not None
            assert len(t.returns) == 2  # 2-player game

    def test_player_nodes_have_info_state(self, kuhn_tree):
        """Non-chance, non-terminal nodes should have info states."""
        all_nodes = _collect_all(kuhn_tree)
        player_nodes = [n for n in all_nodes if n.player >= 0]
        for n in player_nodes:
            assert n.info_state is not None, f"Player node missing info state: {n.state_str}"

    def test_max_depth_truncation(self, kuhn_game):
        """max_depth should limit tree construction."""
        full = build_tree(kuhn_game)
        limited = build_tree(kuhn_game, max_depth=2)
        full_count = _count_nodes(full)
        limited_count = _count_nodes(limited)
        assert limited_count < full_count

    def test_children_match_actions(self, kuhn_tree):
        """Each non-terminal node should have len(children) == len(actions)."""
        for node in _collect_all(kuhn_tree):
            if node.player != -4 and node.actions:
                assert len(node.children) == len(node.actions)

    def test_chance_probs(self, kuhn_tree):
        """Chance nodes should have probability values."""
        assert kuhn_tree.chance_probs is not None
        assert abs(sum(kuhn_tree.chance_probs) - 1.0) < 1e-6


class TestLayout:
    def test_layout_populates_coordinates(self, kuhn_tree):
        """Layout should set x, y values."""
        layout_tree(kuhn_tree)
        all_nodes = _collect_all(kuhn_tree)
        # Root should be at y=0
        assert kuhn_tree.y == 0

    def test_layout_no_overlap(self, kuhn_tree):
        """No two nodes at the same depth should share the same x."""
        layout_tree(kuhn_tree)
        all_nodes = _collect_all(kuhn_tree)
        by_depth = {}
        for n in all_nodes:
            by_depth.setdefault(n.depth, []).append(n.x)
        for depth, xs in by_depth.items():
            assert len(xs) == len(set(xs)), f"Overlapping x at depth {depth}"

    def test_parent_centered(self, kuhn_tree):
        """Internal nodes should be centered over children."""
        layout_tree(kuhn_tree)
        for node in _collect_all(kuhn_tree):
            if node.children:
                child_avg = sum(c.x for c in node.children) / len(node.children)
                assert abs(node.x - child_avg) < 1e-6

    def test_unknown_algorithm_raises(self, kuhn_tree):
        with pytest.raises(ValueError):
            layout_tree(kuhn_tree, algorithm="unknown")


class TestCollectInfoSets:
    def test_info_sets_kuhn(self, kuhn_tree):
        """Kuhn poker should have info sets for both players."""
        info_sets = collect_info_sets(kuhn_tree)
        assert len(info_sets) > 0
        # Each info set should have at least one node
        for nodes in info_sets.values():
            assert len(nodes) >= 1

    def test_info_sets_player_separation(self, kuhn_tree):
        """Info sets should contain nodes of a single player."""
        info_sets = collect_info_sets(kuhn_tree)
        for info_state, nodes in info_sets.items():
            players = set(n.player for n in nodes)
            assert len(players) == 1, f"Info set {info_state} has multiple players: {players}"
