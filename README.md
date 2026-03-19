# spielviz

[![PyPI](https://img.shields.io/pypi/v/spielviz)](https://pypi.org/project/spielviz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/kvr06-ai/spielviz/actions/workflows/ci.yml/badge.svg)](https://github.com/kvr06-ai/spielviz/actions)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kvr06-ai/spielviz/blob/main/examples/spielviz_demo.ipynb)

Python visualization library for [OpenSpiel](https://github.com/google-deepmind/open_spiel) game trees, information sets, and strategy profiles.

## Installation

```bash
pip install spielviz
```

## Quick Start

```python
import spielviz

# One-liner: render any OpenSpiel game
spielviz.quick_render("kuhn_poker", path="kuhn.png")
```

Or with more control:

```python
import pyspiel
import spielviz

game = pyspiel.load_game("kuhn_poker")
root = spielviz.build_tree(game)
root = spielviz.layout_tree(root)

# Highlight information sets
colors = spielviz.auto_color_info_sets(root, player=0)
fig, ax = spielviz.render_tree(
    root,
    highlight_info_sets=colors,
    show_actions=True,
    show_payoffs=True,
    title="Kuhn Poker",
)
fig.savefig("kuhn_poker.png", dpi=150, bbox_inches="tight")
```

## Features

### Game Tree Rendering

Render any OpenSpiel game as a publication-quality tree diagram:

- Player-colored nodes (colorblind-friendly palette)
- Action labels on edges
- Terminal payoffs displayed
- Chance node probabilities

### Information Set Visualization

Highlight which nodes a player cannot distinguish:

```python
colors = spielviz.auto_color_info_sets(root, player=0)
fig, ax = spielviz.render_tree(root, highlight_info_sets=colors)

# Or draw dashed connection lines (standard game theory notation)
spielviz.draw_info_set_connections(ax, root, player=0)
```

### Strategy Profile Visualization

Visualize policies from CFR, fictitious play, or any OpenSpiel algorithm:

```python
from open_spiel.python.algorithms import cfr

solver = cfr.CFRSolver(game)
for _ in range(1000):
    solver.evaluate_and_update_policy()
policy = solver.average_policy()

# Bar chart of action probabilities at each info set
fig, ax = spielviz.plot_strategy_profile(game, policy, player=0)

# Strategy overlaid directly on the game tree
fig, ax = spielviz.plot_strategy_on_tree(root, game, policy, player=0)
```

### Large Game Support

Use `max_depth` for games with large state spaces:

```python
spielviz.quick_render("tic_tac_toe", max_depth=3, path="ttt.png")
```

## API Reference

| Function | Description |
|:---------|:------------|
| `build_tree(game, max_depth=None)` | Build a TreeNode hierarchy from an OpenSpiel game |
| `layout_tree(root, algorithm="simple")` | Compute (x, y) positions for all nodes |
| `collect_info_sets(root)` | Group nodes by information state string |
| `render_tree(root, **kwargs)` | Render game tree as matplotlib figure |
| `save_tree(root, path, **kwargs)` | Render and save to file (PNG, SVG, PDF) |
| `auto_color_info_sets(root, player)` | Assign distinct colors to info sets |
| `draw_info_set_connections(ax, root, player)` | Draw dashed lines between info set nodes |
| `plot_strategy_profile(game, policy, player=0)` | Bar chart of strategy at each info set |
| `plot_strategy_on_tree(root, game, policy, player=0)` | Mini bar charts overlaid on tree |
| `quick_render(game_name, **kwargs)` | One-liner convenience function |

## Roadmap

This is an MVP (v0.1). If the community finds it useful, planned additions include:

- **Normal-form game rendering** — payoff matrix visualization with Nash equilibrium highlighting
- **Buchheim tree layout** — compact, aesthetically balanced layout for larger games
- **Subtree pruning & aggregation** — handle games with large state spaces
- **Learning dynamics plots** — exploitability curves, strategy evolution over iterations
- **Interactive HTML export** — hover, expand/collapse, zoom
- **Strategy comparison** — side-by-side multi-policy visualization
- **Learning animation** — animated strategy evolution during training

Feedback and feature requests welcome — please [open an issue](https://github.com/kvr06-ai/spielviz/issues).

## Tested Games

- `kuhn_poker` — 2-player Kuhn Poker
- `leduc_poker` — 2-player Leduc Poker (depth-limited)
- `tic_tac_toe` — Tic-Tac-Toe (depth-limited)

## Contributing

Contributions welcome! Please open an issue or PR.

```bash
git clone https://github.com/kvr06-ai/spielviz.git
cd spielviz
pip install -e ".[dev]"
pytest tests/
ruff check src/
```

## License

MIT
