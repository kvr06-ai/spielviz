"""Tests for infosets.py — info set coloring and connections."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyspiel
import pytest

from spielviz.tree import build_tree, layout_tree, collect_info_sets
from spielviz.infosets import auto_color_info_sets, draw_info_set_connections
from spielviz.render import render_tree


@pytest.fixture
def kuhn_laid_out():
    game = pyspiel.load_game("kuhn_poker")
    root = build_tree(game)
    layout_tree(root)
    return root


class TestAutoColor:
    def test_auto_color_distinct(self, kuhn_laid_out):
        """All info sets should get different colors."""
        colors = auto_color_info_sets(kuhn_laid_out, player=0)
        assert len(colors) > 0
        color_values = list(colors.values())
        assert len(color_values) == len(set(color_values)), "Colors should be distinct"

    def test_auto_color_player_filter(self, kuhn_laid_out):
        """Should only color info sets for the specified player."""
        info_sets = collect_info_sets(kuhn_laid_out)
        colors_p0 = auto_color_info_sets(kuhn_laid_out, player=0)
        colors_p1 = auto_color_info_sets(kuhn_laid_out, player=1)

        # Player 0 and player 1 info sets should be disjoint
        assert set(colors_p0.keys()).isdisjoint(set(colors_p1.keys()))

    def test_auto_color_returns_hex(self, kuhn_laid_out):
        """Colors should be hex strings."""
        colors = auto_color_info_sets(kuhn_laid_out, player=0)
        for color in colors.values():
            assert color.startswith("#"), f"Expected hex color, got {color}"

    def test_auto_color_empty_for_invalid_player(self, kuhn_laid_out):
        """Non-existent player should return empty dict."""
        colors = auto_color_info_sets(kuhn_laid_out, player=99)
        assert colors == {}


class TestDrawConnections:
    def test_connections_drawn(self, kuhn_laid_out):
        """Connection lines should be added to axes."""
        fig, ax = render_tree(kuhn_laid_out)
        initial_lines = len(ax.lines)
        draw_info_set_connections(ax, kuhn_laid_out, player=0)
        assert len(ax.lines) > initial_lines, "Expected connection lines to be added"
        plt.close(fig)

    def test_connections_with_dotted_style(self, kuhn_laid_out):
        """Should work with dotted style."""
        fig, ax = render_tree(kuhn_laid_out)
        draw_info_set_connections(ax, kuhn_laid_out, player=0, style="dotted")
        plt.close(fig)

    def test_connections_custom_color(self, kuhn_laid_out):
        """Should work with custom color."""
        fig, ax = render_tree(kuhn_laid_out)
        draw_info_set_connections(ax, kuhn_laid_out, player=0, color="#FF0000")
        plt.close(fig)
