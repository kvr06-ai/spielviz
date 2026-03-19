"""Visualize Tic-Tac-Toe game tree (depth-limited)."""

import spielviz

# Tic-Tac-Toe is too large for full tree — use max_depth
spielviz.quick_render("tic_tac_toe", max_depth=3, path="ttt_depth3.png")
print("Saved ttt_depth3.png")

# Render with info sets
root = spielviz.build_tree(
    __import__("pyspiel").load_game("tic_tac_toe"), max_depth=3
)
root = spielviz.layout_tree(root)
colors = spielviz.auto_color_info_sets(root, player=0)
fig, ax = spielviz.render_tree(
    root,
    highlight_info_sets=colors,
    title="Tic-Tac-Toe (depth 3) — Player 0 Info Sets",
)
fig.savefig("ttt_infosets.png", dpi=150, bbox_inches="tight")
print("Saved ttt_infosets.png")
