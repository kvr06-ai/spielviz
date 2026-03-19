"""Visualize Leduc Poker game tree (depth-limited)."""

import pyspiel
from open_spiel.python.algorithms import cfr
import spielviz

game = pyspiel.load_game("leduc_poker")

# 1. Depth-limited tree with info sets
root = spielviz.build_tree(game, max_depth=4)
root = spielviz.layout_tree(root)

colors = spielviz.auto_color_info_sets(root, player=0)
fig, ax = spielviz.render_tree(
    root,
    highlight_info_sets=colors,
    title="Leduc Poker (depth 4) — Player 0 Info Sets",
)
fig.savefig("leduc_infosets.png", dpi=150, bbox_inches="tight")
print("Saved leduc_infosets.png")

# 2. CFR strategy profile
solver = cfr.CFRSolver(game)
for _ in range(500):
    solver.evaluate_and_update_policy()

policy = solver.average_policy()
fig, ax = spielviz.plot_strategy_profile(
    game, policy, player=0, title="Leduc Poker — CFR Strategy (Player 0)"
)
fig.savefig("leduc_strategy.png", dpi=150, bbox_inches="tight")
print("Saved leduc_strategy.png")
