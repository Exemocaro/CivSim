"""AI strategy functions — tile selection logic for each personality type.

Extracted from Nation.get_dev_tiles() so that adding a new AI behaviour means
adding a new function here, not editing Nation.
Each strategy function receives the nation and map data and returns a list of
tiles the nation should develop or expand into next.
"""

from __future__ import annotations

import logging
import random
from math import sqrt
from typing import TYPE_CHECKING

from civsim.settings import (
    MAX_DEV_TRIES,
    PROBABILITY_AGGR_EXP_DEV_TILE,
    PROBABILITY_DEVELOPING_DEV_TILE,
    PROBABILITY_PEACE_EXP_DEV_TILE,
    SCORE_W_DEFENSE,
    SCORE_W_DISTANCE,
    SCORE_W_ENCLAVE,
    SCORE_W_ISOLATION,
    SCORE_W_VALUE,
)
from civsim.world.terrain import UNCONTROLLABLE_TERRAINS

if TYPE_CHECKING:
    from collections.abc import Callable

    from civsim.simulation.nation import Nation
    from civsim.world.tile import Tile

    StrategyFn = Callable[..., list[Tile]]

logger = logging.getLogger(__name__)

TilesByNation = dict[tuple[int, int], int]


def _prob_for_phase(phase: str) -> int:
    """Return the dev-tile probability for a given personality phase."""
    return {
        "aggressively-expanding": PROBABILITY_AGGR_EXP_DEV_TILE,
        "peacefully-expanding": PROBABILITY_PEACE_EXP_DEV_TILE,
        "developing": PROBABILITY_DEVELOPING_DEV_TILE,
    }.get(phase, PROBABILITY_PEACE_EXP_DEV_TILE)


def _score_border_tile(
    tile: Tile,
    nation: Nation,
    tiles: list[list[Tile]],
    tiles_by_nation: TilesByNation,
) -> float:
    """Score a border tile. Higher = more desirable to conquer.

    Rewards: high tile value, proximity to capital, low defense.
    Bonuses: tiles nearly surrounded by our territory; isolated enemy tiles.
    """
    ref = nation.capital
    if ref is None:
        return 0.0

    dist = sqrt((tile.x - ref.x) ** 2 + (tile.y - ref.y) ** 2)
    tile_defense = tile.terrain.defense_value + sum(b.def_bonus for b in tile.buildings)

    neighbours = tile.get_neighbours(tiles, len(tiles[0]), len(tiles))
    if not neighbours:
        return 0.0

    owned_neighbours = sum(1 for n in neighbours if tiles_by_nation.get(n.coords, 0) == nation.id)
    # Quadratic: a tile 7/8 surrounded scores nearly as high as a full enclave.
    owned_ratio = owned_neighbours / len(neighbours)
    enclave_bonus = SCORE_W_ENCLAVE * (owned_ratio**2)

    # Enemy tiles with few same-nation neighbours are isolated and easy to absorb.
    tile_nation_id = tiles_by_nation.get(tile.coords, 0)
    isolation_bonus = 0.0
    if tile_nation_id not in (0, nation.id):
        same_nation_neighbours = sum(
            1 for n in neighbours if tiles_by_nation.get(n.coords, 0) == tile_nation_id
        )
        isolation_ratio = 1.0 - (same_nation_neighbours / len(neighbours))
        isolation_bonus = SCORE_W_ISOLATION * isolation_ratio

    return (
        SCORE_W_VALUE * tile.value
        - SCORE_W_DISTANCE * dist
        - SCORE_W_DEFENSE * tile_defense
        + enclave_bonus
        + isolation_bonus
    )


def scored_strategy(
    nation: Nation,
    tiles: list[list[Tile]],
    tiles_by_nation: TilesByNation,
    controlled_tiles: list[Tile],
) -> list[Tile]:
    """Score all border tiles and return the best ones as a ranked expansion queue."""
    if not controlled_tiles:
        logger.warning("Nation %s has no controlled tiles in scored_strategy.", nation.id)
        return []

    prob = _prob_for_phase(nation.personality.phase)

    # ---------- In-place development ----------
    if random.randint(1, 100) <= prob:
        # Occasionally develop one of our own tiles (same logic as basic_strategy).
        developable = [t for t in controlled_tiles if t.terrain.name not in UNCONTROLLABLE_TERRAINS]
        if developable:
            return [random.choice(developable)]
        return []

    # ---------- Scored expansion ----------
    candidates = [
        t
        for t in nation.neighbour_tiles
        if tiles_by_nation.get(t.coords, 0) == 0  # neutral only for expansion
        and t.terrain.name not in UNCONTROLLABLE_TERRAINS
    ]

    if not candidates:
        # No neutral neighbours — try claiming back any uncontrolled neighbour
        candidates = [
            t for t in nation.neighbour_tiles if t.terrain.name not in UNCONTROLLABLE_TERRAINS
        ]

    if not candidates:
        return []

    scored = sorted(
        candidates,
        key=lambda t: _score_border_tile(t, nation, tiles, tiles_by_nation),
        reverse=True,
    )

    # Return the top MAX_DEV_TRIES tiles as a ranked queue.
    return scored[:MAX_DEV_TRIES]


# ---------------------------------------------------------------------------
# Strategy registry — keyed by personality name.
# Add new strategies here to extend AI behaviour without touching Nation.
# ---------------------------------------------------------------------------
STRATEGY_REGISTRY: dict[str, StrategyFn] = {
    "basic": scored_strategy,
}


def get_dev_tiles(
    nation: Nation,
    tiles: list[list[Tile]],
    tiles_by_nation: TilesByNation,
    controlled_tiles: list[Tile],
) -> list[Tile]:
    """Dispatch to the correct strategy for this nation's personality."""
    strategy = STRATEGY_REGISTRY.get(nation.personality.name)
    if strategy is None:
        logger.warning(
            "Unknown personality name %r for nation %s — falling back to scored.",
            nation.personality.name,
            nation.id,
        )
        strategy = scored_strategy
    return strategy(nation, tiles, tiles_by_nation, controlled_tiles)
