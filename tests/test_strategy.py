"""Tests for strategy.py — strategy profile visualization."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyspiel
import pytest

from open_spiel.python.algorithms import cfr
from open_spiel.python import policy as policy_module

from spielviz.tree import build_tree, layout_tree
from spielviz.strategy import plot_strategy_profile, plot_strategy_on_tree


@pytest.fixture
def kuhn_game():
    return pyspiel.load_game("kuhn_poker")


@pytest.fixture
def kuhn_laid_out(kuhn_game):
    root = build_tree(kuhn_game)
    layout_tree(root)
    return root


@pytest.fixture
def uniform_policy(kuhn_game):
    return policy_module.UniformRandomPolicy(kuhn_game)


@pytest.fixture
def cfr_policy(kuhn_game):
    solver = cfr.CFRSolver(kuhn_game)
    for _ in range(100):
        solver.evaluate_and_update_policy()
    return solver.average_policy()


class TestPlotStrategyProfile:
    def test_plot_uniform(self, kuhn_game, uniform_policy):
        """Uniform policy should render without error."""
        fig, ax = plot_strategy_profile(kuhn_game, uniform_policy, player=0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_cfr(self, kuhn_game, cfr_policy):
        """CFR policy should render without error."""
        fig, ax = plot_strategy_profile(kuhn_game, cfr_policy, player=0)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_with_title(self, kuhn_game, uniform_policy):
        """Custom title should appear."""
        fig, ax = plot_strategy_profile(
            kuhn_game, uniform_policy, player=0, title="Test Strategy"
        )
        assert "Test Strategy" in ax.get_title()
        plt.close(fig)

    def test_plot_player_1(self, kuhn_game, uniform_policy):
        """Should work for player 1."""
        fig, ax = plot_strategy_profile(kuhn_game, uniform_policy, player=1)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestPlotStrategyOnTree:
    def test_strategy_on_tree(self, kuhn_game, kuhn_laid_out, uniform_policy):
        """Strategy overlay should render without error."""
        fig, ax = plot_strategy_on_tree(
            kuhn_laid_out, kuhn_game, uniform_policy, player=0
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_strategy_on_tree_cfr(self, kuhn_game, kuhn_laid_out, cfr_policy):
        """CFR strategy overlay should render."""
        fig, ax = plot_strategy_on_tree(
            kuhn_laid_out, kuhn_game, cfr_policy, player=0
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
