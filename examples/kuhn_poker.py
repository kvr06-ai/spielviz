"""Visualize Kuhn Poker game tree with information sets and CFR strategy."""

import pyspiel
from open_spiel.python.algorithms import cfr
import spielviz

# 1. Basic game tree
game = pyspiel.load_game("kuhn_poker")
root = spielviz.build_tree(game)
root = spielviz.layout_tree(root)

# 2. Render with information sets for player 0
colors = spielviz.auto_color_info_sets(root, player=0)
fig, ax = spielviz.render_tree(
    root,
    highlight_info_sets=colors,
    show_actions=True,
    show_payoffs=True,
    title="Kuhn Poker — Player 0 Information Sets",
)
fig.savefig("kuhn_infosets.png", dpi=150, bbox_inches="tight")
print("Saved kuhn_infosets.png")

# 3. Add info set connection lines
spielviz.draw_info_set_connections(ax, root, player=0)
fig.savefig("kuhn_connections.png", dpi=150, bbox_inches="tight")
print("Saved kuhn_connections.png")

# 4. Run CFR and visualize equilibrium strategy
solver = cfr.CFRSolver(game)
for _ in range(1000):
    solver.evaluate_and_update_policy()

policy = solver.average_policy()
fig, ax = spielviz.plot_strategy_profile(
    game, policy, player=0, title="CFR Strategy — Player 0"
)
fig.savefig("kuhn_strategy.png", dpi=150, bbox_inches="tight")
print("Saved kuhn_strategy.png")

# 5. Strategy overlaid on tree
fig, ax = spielviz.plot_strategy_on_tree(root, game, policy, player=0)
fig.savefig("kuhn_strategy_tree.png", dpi=150, bbox_inches="tight")
print("Saved kuhn_strategy_tree.png")

# 6. Quick one-liner
spielviz.quick_render("kuhn_poker", path="kuhn_quick.png")
print("Saved kuhn_quick.png")
