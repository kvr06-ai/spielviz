"""spielviz — Python visualization library for OpenSpiel games."""

from spielviz.tree import build_tree, layout_tree, collect_info_sets, TreeNode
from spielviz.render import render_tree, save_tree
from spielviz.infosets import auto_color_info_sets, draw_info_set_connections
from spielviz.strategy import plot_strategy_profile, plot_strategy_on_tree

__version__ = "0.1.1"

__all__ = [
    "build_tree",
    "layout_tree",
    "collect_info_sets",
    "TreeNode",
    "render_tree",
    "save_tree",
    "auto_color_info_sets",
    "draw_info_set_connections",
    "plot_strategy_profile",
    "plot_strategy_on_tree",
    "quick_render",
]


def quick_render(
    game_name,
    *,
    max_depth=None,
    show_info_sets=True,
    player=0,
    path=None,
    **kwargs,
):
    """One-liner to render a game tree.

    Usage:
        import spielviz
        spielviz.quick_render("kuhn_poker")
        spielviz.quick_render("kuhn_poker", path="kuhn.png")
    """
    import pyspiel

    game = pyspiel.load_game(game_name)
    root = build_tree(game, max_depth=max_depth)
    root = layout_tree(root)

    if show_info_sets:
        kwargs["highlight_info_sets"] = auto_color_info_sets(root, player)

    if path:
        save_tree(root, path, **kwargs)
    else:
        return render_tree(root, **kwargs)
