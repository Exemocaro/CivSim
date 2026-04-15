"""Procedural map generation using Perlin noise."""

from __future__ import annotations

import logging
import random

from perlin_noise import PerlinNoise

from civsim.settings import (
    MAX_POP,
    MAX_WEALTH,
    MIN_POP,
    MIN_WEALTH,
    NOISE_SCALE,
    RIVER_MIN_DISTANCE_DIVISOR,
)
from civsim.world.feature import (
    BIG_FOREST,
    FOREST,
    HILLS,
    LAND_FEATURES,
    RIVER,
    WATER_FEATURES,
)
from civsim.world.resource import LAND_RESOURCES, NO_RESOURCE, WATER_RESOURCES, Resource
from civsim.world.terrain import (
    NAME_COLOR_PAIRS,
    NAME_LIFERATING_PAIRS,
    NO_RESOURCE_TERRAINS,
    WATER_TERRAINS,
    Terrain,
    get_normal_terrains,
)
from civsim.world.tile import Tile

logger = logging.getLogger(__name__)

# Perlin noise generators — four octaves combined for fractal terrain
_noise1 = PerlinNoise(octaves=3)
_noise2 = PerlinNoise(octaves=6)
_noise3 = PerlinNoise(octaves=12)
_noise4 = PerlinNoise(octaves=24)


class Map:
    def __init__(self, size_x: int, size_y: int, river_num: int) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.river_num = river_num
        self.tiles: list[list[Tile]] = [[None for _ in range(size_x)] for _ in range(size_y)]  # type: ignore[misc]

        # Pre-compute latitude band boundaries used for polar terrain
        self.top1 = size_y - (size_y * 12 // 100)
        self.top2 = size_y - (size_y * 9 // 100)
        self.top3 = size_y - (size_y * 6 // 100)
        self.top4 = size_y - (size_y * 3 // 100)
        self.bot1 = size_y * 12 // 100
        self.bot2 = size_y * 9 // 100
        self.bot3 = size_y * 6 // 100
        self.bot4 = size_y * 3 // 100

    # ------------------------------------------------------------------
    # Weighted random choice
    # ------------------------------------------------------------------

    @staticmethod
    def weight_chooser(items: list, rarities: list[int]):
        """Return a random element from *items* weighted by *rarities*."""
        total = sum(rarities)
        if total == 0:
            raise ValueError("weight_chooser: all rarities are 0")
        selection = random.randint(1, total)
        count = 0
        for item, weight in zip(items, rarities, strict=False):
            count += weight
            if selection <= count:
                return item
        raise ValueError(f"weight_chooser: selection {selection} not matched (total={total})")

    # ------------------------------------------------------------------
    # Terrain chooser
    # ------------------------------------------------------------------

    def choose_terrain(self, x: int, y: int) -> Terrain:
        noise_val = (
            _noise1([x * NOISE_SCALE, y * NOISE_SCALE])
            + 0.5 * _noise2([x * NOISE_SCALE, y * NOISE_SCALE])
            + 0.25 * _noise3([x * NOISE_SCALE, y * NOISE_SCALE])
            + 0.125 * _noise4([x * NOISE_SCALE, y * NOISE_SCALE])
        )

        name = "Ocean"
        features = []
        has_hills = False
        has_forest = False
        has_big_forest = False

        # Base terrain from noise value
        if noise_val > 0.5:
            name = "Mountain"
            has_hills = True
        elif noise_val > 0.3:
            name = random.choice(get_normal_terrains())
            has_hills = random.randint(0, 2) == 0
            has_forest = random.randint(0, 5) == 0
        elif noise_val > 0:
            name = random.choice(get_normal_terrains())
            has_hills = random.randint(0, 5) == 0
            if random.randint(0, 1) == 0:
                has_forest = True
            elif random.randint(0, 9) == 0:
                has_big_forest = True
        elif noise_val > -0.12:
            name = "Coast"

        # Highland overrides
        if (
            noise_val > 0.25
            and random.randint(0, 6) <= 2
            or noise_val > 0.15
            and random.randint(0, 5) == 0
        ):
            name = "Highland"

        # Polar overrides — probability increases toward the poles
        polar_cases = [
            (self.size_y - 1, 1),  # edge row: always polar
            (self.size_y - 2, 4),  # near-edge: very likely
            (self.top4, 3),
            (self.top3, 2),
            (self.top2, 2),
            (self.top1, 1),
            (self.top1 - 1, 1),
        ]
        thresholds = [1, 1, 3, 2, 2, 1, 1]
        roll_outs = [1, 1, 6, 6, 8, 10, 15]

        for i, (boundary, _) in enumerate(polar_cases):
            if y >= boundary or y <= self.size_y - 1 - boundary:
                roll = random.randint(0, roll_outs[i])
                if roll <= thresholds[i]:
                    name = "Ice" if noise_val < 0 else "Tundra"
                break

        color = NAME_COLOR_PAIRS[name]

        if has_hills:
            features.append(HILLS)
        if has_big_forest:
            features.append(BIG_FOREST)
            has_forest = False
        if has_forest:
            features.append(FOREST)

        # Random extra feature (rarity-weighted)
        if len(features) < 2 and random.randint(1, 6) == 1:
            if name not in WATER_TERRAINS and name != "Mountain":
                rarities = [f.rarity for f in LAND_FEATURES]
                features.append(self.weight_chooser(LAND_FEATURES, rarities))
            elif name == "Coast":
                rarities = [f.rarity for f in WATER_FEATURES]
                features.append(self.weight_chooser(WATER_FEATURES, rarities))

        return Terrain(name, color, features, noise_val)

    # ------------------------------------------------------------------
    # Other choosers
    # ------------------------------------------------------------------

    def choose_resource(self, terrain: Terrain) -> Resource:
        if terrain.name in NO_RESOURCE_TERRAINS:
            return NO_RESOURCE
        if terrain.name in WATER_TERRAINS:
            if random.randint(0, 5) != 0:
                return NO_RESOURCE
            resources = WATER_RESOURCES
        else:
            resources = LAND_RESOURCES
        rarities = [r.rarity for r in resources]
        return self.weight_chooser(resources, rarities)

    def choose_wealth(self, terrain: Terrain, res: Resource) -> float:
        if terrain.name in WATER_TERRAINS and res.name == "":
            return 0
        if terrain.name == "Mountain":
            return 0
        return float(random.randint(MIN_WEALTH, MAX_WEALTH))

    def choose_liferating(self, terrain: Terrain) -> int:
        lo, hi = NAME_LIFERATING_PAIRS[terrain.name]
        return random.randint(lo, hi)

    def choose_population(self, terrain: Terrain) -> int:
        if terrain.name in WATER_TERRAINS or terrain.name == "Mountain":
            return 0
        return random.randint(MIN_POP, MAX_POP)

    # ------------------------------------------------------------------
    # Map generation
    # ------------------------------------------------------------------

    def gen_tiles(self) -> None:
        tile_id = 0
        for y in range(self.size_y):
            for x in range(self.size_x):
                terrain = self.choose_terrain(x, y)
                pop = self.choose_population(terrain)
                res = self.choose_resource(terrain)
                wealth = self.choose_wealth(terrain, res)
                liferating = self.choose_liferating(terrain)
                mods: dict[str, float] = {"dev": 0.0, "rev": 0.0}
                self.tiles[y][x] = Tile(
                    tile_id,
                    f"Tile {tile_id}",
                    x,
                    y,
                    terrain,
                    pop,
                    res,
                    wealth,
                    liferating,
                    mods,
                )
                tile_id += 1

        # Normalise values after full generation
        for row in self.tiles:
            for tile in row:
                tile.update_values()

    def gen_rivers(self) -> None:
        """Generate rivers flowing downhill from mountains to the sea.

        River sources are spaced out to avoid clustering.
        """
        logger.info("Generating rivers...")
        min_dist = max(self.size_x, self.size_y) // RIVER_MIN_DISTANCE_DIVISOR
        river_sources: list[tuple[int, int]] = []

        remaining = self.river_num
        river_height = 0.80

        while remaining > 0:
            row = random.choice(self.tiles)
            tile = random.choice(row)

            # Height check
            if tile.terrain.height < river_height or RIVER in tile.terrain.features:
                river_height -= 0.0005
                if river_height < 0.05:
                    break
                continue

            # Spacing check — avoid clustering
            too_close = any(
                abs(tile.x - sx) + abs(tile.y - sy) < min_dist for sx, sy in river_sources
            )
            if too_close:
                river_height -= 0.0005
                if river_height < 0.05:
                    break
                continue

            river_sources.append((tile.x, tile.y))
            remaining -= 1

            # Flow downhill until we reach the sea
            while tile.terrain.height > 0:
                if RIVER not in tile.terrain.features:
                    tile.terrain.features.append(RIVER)

                neighbours = tile.get_neighbours(self.tiles, self.size_x, self.size_y)
                # Sort by height ascending; pick lowest neighbour without a river
                sorted_neighbours = sorted(neighbours, key=lambda t: t.terrain.height)

                next_tile = None
                for candidate in sorted_neighbours:
                    if RIVER not in candidate.terrain.features:
                        next_tile = candidate
                        break

                if next_tile is None:
                    break  # Surrounded by river tiles — terminate this branch

                tile = next_tile

    def create_map(self) -> None:
        logger.info("Generating tiles...")
        self.gen_tiles()
        self.gen_rivers()

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def find_tile(self, coords: tuple[int, int]) -> Tile:
        return self.tiles[coords[1]][coords[0]]
