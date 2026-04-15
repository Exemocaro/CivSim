# CivSim

An AI-only civilization simulation built with Python and Pygame. Nations spawn on a procedurally generated map and compete for dominance entirely on their own — no player input required.

![Alt Text](preview.gif)

## How it works

Each nation is an autonomous AI that expands its territory, wages wars, develops its tiles, and manages an economy — all at the same time. The world is generated fresh every run using Perlin noise, so no two games look the same.

### Economy

Nations earn **influence** and **money** each turn from their tiles, buildings, and leaders. Influence is the primary currency for everything territorial — conquering tiles, developing them, building improvements, and sustaining wars all cost influence. Money funds buildings and war budgets.

### Expansion

Nations expand by conquering adjacent tiles. Rather than picking targets randomly, each border tile is scored by how valuable it is, how close it sits to the capital, how well-defended it is, and how surrounded it already is by friendly territory. This means nations naturally fill their own gaps and isolated pockets before pushing outward, and tend to grow in coherent shapes instead of random blobs.

### War

Wars are declared when a nation has enough money and sees a neighbour worth fighting. Combat is resolved by comparing the two sides' war budgets, iron stockpiles, tech levels, and leader martial skill against the defending tile's terrain and buildings. Terrain matters — hills, rivers, and fortifications provide real defensive advantages. Wars end through negotiation, exhaustion, or total conquest.

### Population and happiness

Every tile has a population that grows when food is plentiful and shrinks when it isn't. Unhappy tiles — those that can't feed themselves or have too much revolt — suffer a production penalty that compounds over time. Keeping tiles fed and developed is essential to a healthy empire.

### Leaders

Each nation is led by a character with martial, prosperity, and vitality traits. A strong leader improves combat, boosts income, and slows resource decay. Leaders age and eventually die; succession always comes with a stability cost, so long-lived rulers are genuinely valuable.

### Technology

As a nation develops its tiles and builds more, it advances through tech levels. Higher tech multiplies production, combat strength, and economic output, creating a meaningful snowball effect for well-developed empires.

### Buildings and improvements

Cities can be upgraded with buildings — markets, granaries, barracks, and more — that boost income or provide military bonuses. Any land tile can also receive improvements like farms, lumber camps, mines, or roads. Roads specifically reduce the influence cost to conquer adjacent tiles, making them useful for planned offensives.

### Personalities

Each nation is assigned a personality that shifts between three phases over time: aggressive expansion, peaceful expansion, and internal development. This phase changes dynamically based on circumstances and a random chance of snapping into a new mode — so the same nation can behave very differently across a long game.

### Map modes

Switch between views with the buttons at the bottom:

- **Political** — nation borders and territory colors
- **Terrain** — base terrain types
- **Population** — population density across the map
- **Rivers** — terrain with river overlay
- **Development** — how developed each tile is

## How to run

```bash
uv sync
uv run civsim
```

Or with plain Python:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -e .
python main.py
```

The recommended map size is **small** — larger maps work but run slower. Map size can be changed in `civsim/__main__.py`.

## Development

Dev dependencies (ruff, mypy, pre-commit) are installed automatically by `uv sync`. Activate the git hooks once after cloning:

```bash
uv run pre-commit install
```

After that, ruff (lint + format) and mypy run automatically on every commit.
