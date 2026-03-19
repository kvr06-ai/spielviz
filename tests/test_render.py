"""Tests for render.py — matplotlib rendering."""

import os
import tempfile

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for tests
import matplotlib.pyplot as plt
import pyspiel
import pytest

from spielviz.tree import build_tree, layout_tree, collect_info_sets
from spielviz.render import render_tree, save_tree
from spielviz.infosets import auto_color_info_sets


@pytest.fixture
def kuhn_laid_out():
    game = pyspiel.load_game("kuhn_poker")
    root = build_tree(game)
    layout_tree(root)
    return root


class TestRenderTree:
    def test_render_no_error(self, kuhn_laid_out):
        """Rendering should not raise."""
        fig, ax = render_tree(kuhn_laid_out)
        plt.close(fig)

    def test_render_returns_fig_ax(self, kuhn_laid_out):
        """Should return (Figure, Axes)."""
        result = render_tree(kuhn_laid_out)
        assert isinstance(result, tuple)
        assert len(result) == 2
        fig, ax = result
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_render_with_title(self, kuhn_laid_out):
        """Title should appear."""
        fig, ax = render_tree(kuhn_laid_out, title="Test Title")
        assert ax.get_title() == "Test Title"
        plt.close(fig)

    def test_render_with_actions(self, kuhn_laid_out):
        """Action labels should be drawn as text."""
        fig, ax = render_tree(kuhn_laid_out, show_actions=True)
        texts = [t.get_text() for t in ax.texts]
        assert len(texts) > 0, "Expected action labels"
        plt.close(fig)

    def test_render_with_payoffs(self, kuhn_laid_out):
        """Payoff labels should appear at terminal nodes."""
        fig, ax = render_tree(kuhn_laid_out, show_payoffs=True)
        texts = [t.get_text() for t in ax.texts]
        # Look for payoff patterns like "+1.0" or "-1.0"
        payoff_texts = [t for t in texts if "+" in t or "-" in t]
        assert len(payoff_texts) > 0, "Expected payoff labels"
        plt.close(fig)

    def test_render_highlight_info_sets(self, kuhn_laid_out):
        """Info set highlighting should add ellipse patches."""
        colors = auto_color_info_sets(kuhn_laid_out, player=0)
        fig, ax = render_tree(kuhn_laid_out, highlight_info_sets=colors)
        patches = [p for p in ax.patches if hasattr(p, 'get_facecolor')]
        assert len(patches) > 0, "Expected info set ellipses"
        plt.close(fig)

    def test_render_with_existing_ax(self, kuhn_laid_out):
        """Should draw on provided axes."""
        fig, ax = plt.subplots()
        result_fig, result_ax = render_tree(kuhn_laid_out, ax=ax)
        assert result_ax is ax
        plt.close(fig)

    def test_render_custom_figsize(self, kuhn_laid_out):
        """Custom figsize should be respected."""
        fig, ax = render_tree(kuhn_laid_out, figsize=(10, 8))
        w, h = fig.get_size_inches()
        assert abs(w - 10) < 0.1
        assert abs(h - 8) < 0.1
        plt.close(fig)


class TestSaveTree:
    def test_save_png(self, kuhn_laid_out):
        """Save to PNG, verify file exists and is non-empty."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            save_tree(kuhn_laid_out, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_save_svg(self, kuhn_laid_out):
        """Save to SVG, verify file exists."""
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            save_tree(kuhn_laid_out, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)
