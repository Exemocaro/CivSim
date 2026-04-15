"""Tile improvements — enhancements that can be built on any controlled land tile,
regardless of whether it has a population.

Unlike city buildings, improvements produce raw resources (food, wood, stone, iron,
gold) rather than money or influence.  They have terrain restrictions and a small
influence maintenance cost.
"""

from __future__ import annotations

from civsim.world.terrain import WATER_TERRAINS


class Improvement:
    def __init__(
        self,
        name: str,
        level: int,
        influence_cost: float,
        money_cost: float,
        food_bonus: int,
        wood_bonus: int,
        stone_bonus: int,
        iron_bonus: int,
        gold_bonus: int,
        influence_maintenance: float,
        allowed_terrains: list[str],
        description: str = "",
    ) -> None:
        self.name = name
        self.level = level
        self.influence_cost = influence_cost
        self.money_cost = money_cost
        self.food_bonus = food_bonus
        self.wood_bonus = wood_bonus
        self.stone_bonus = stone_bonus
        self.iron_bonus = iron_bonus
        self.gold_bonus = gold_bonus
        self.influence_maintenance = influence_maintenance
        self.allowed_terrains = allowed_terrains
        self.description = description

    def can_be_built_on(self, terrain_name: str) -> bool:
        return terrain_name in self.allowed_terrains and terrain_name not in WATER_TERRAINS

    def __repr__(self) -> str:
        return f"Improvement({self.name!r}, lvl={self.level})"


# ---------------------------------------------------------------------------
# Available improvements
# ---------------------------------------------------------------------------

IMPROVEMENTS: list[Improvement] = [
    Improvement(
        "farm", 1,
        influence_cost=1, money_cost=0,
        food_bonus=3, wood_bonus=0, stone_bonus=0, iron_bonus=0, gold_bonus=0,
        influence_maintenance=0.1,
        allowed_terrains=["Plains", "Grassland", "Highland"],
        description="Cultivates land; produces extra food each turn.",
    ),
    Improvement(
        "lumber camp", 1,
        influence_cost=1, money_cost=0,
        food_bonus=0, wood_bonus=3, stone_bonus=0, iron_bonus=0, gold_bonus=0,
        influence_maintenance=0.1,
        allowed_terrains=["Plains", "Grassland", "Highland", "Tundra"],
        description="Harvests timber; produces extra wood each turn.",
    ),
    Improvement(
        "mine", 1,
        influence_cost=2, money_cost=10,
        food_bonus=0, wood_bonus=0, stone_bonus=2, iron_bonus=2, gold_bonus=0,
        influence_maintenance=0.2,
        allowed_terrains=["Highland", "Mountain", "Tundra", "Desert"],
        description="Extracts stone and iron from the earth.",
    ),
    Improvement(
        "road", 1,
        influence_cost=1, money_cost=5,
        food_bonus=0, wood_bonus=0, stone_bonus=0, iron_bonus=0, gold_bonus=0,
        influence_maintenance=0.05,
        allowed_terrains=["Plains", "Grassland", "Highland", "Desert", "Tundra", "Coast"],
        description="Reduces the influence cost to conquer adjacent tiles by 20%.",
    ),
]
