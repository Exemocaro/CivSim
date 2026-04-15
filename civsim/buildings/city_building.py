"""City buildings — structures that require a populated tile (population > 0).

Buildings produce either money (and cost influence) or influence (and cost money).
They are organised by level; L2 buildings cost roughly twice as much but produce
more, allowing for a simple tech-gated upgrade path.
"""

from __future__ import annotations

from civsim.settings import (
    BASE_BUILDING_INFLUENCE_COST,
    BASE_BUILDING_MAINTENANCE_INFLUENCE,
    BASE_BUILDING_MAINTENANCE_MONEY,
    BASE_BUILDING_MONEY_COST,
    BASE_INFLUENCE_BUILDING_BONUS,
    BASE_MONEY_BUILDING_BONUS,
)


class CityBuilding:
    def __init__(
        self,
        name: str,
        level: int,
        money_cost: float,
        influence_cost: float,
        money_maintenance: float,
        influence_maintenance: float,
        res_bonus: list[float],
        def_bonus: int = 0,
        description: str = "",
    ) -> None:
        self.name = name
        self.level = level
        self.money_cost = money_cost
        self.influence_cost = influence_cost
        self.money_maintenance = money_maintenance  # negative = income
        self.influence_maintenance = influence_maintenance  # negative = income
        self.food_bonus = res_bonus[0]
        self.wood_bonus = res_bonus[1]
        self.stone_bonus = res_bonus[2]
        self.iron_bonus = res_bonus[3]
        self.gold_bonus = res_bonus[4]
        self.def_bonus = def_bonus  # added to tile defense_value when this tile is attacked
        self.description = description

    def get_maintenance(self) -> tuple[float, float]:
        """Return (money_maintenance, influence_maintenance)."""
        return (self.money_maintenance, self.influence_maintenance)

    def __repr__(self) -> str:
        return f"CityBuilding({self.name!r}, lvl={self.level})"


# ---------------------------------------------------------------------------
# Level 1 city buildings
# ---------------------------------------------------------------------------

# Produce money, cost influence
L1_MONEY_BUILDINGS: list[CityBuilding] = [
    CityBuilding(
        "marketplace",
        1,
        money_cost=0,
        influence_cost=BASE_BUILDING_INFLUENCE_COST,
        money_maintenance=-BASE_MONEY_BUILDING_BONUS,
        influence_maintenance=BASE_BUILDING_MAINTENANCE_INFLUENCE,
        res_bonus=[0, 0, 0, 0, 0],
        description="Generates money from local trade.",
    ),
    CityBuilding(
        "granary",
        1,
        money_cost=0,
        influence_cost=3,
        money_maintenance=0,
        influence_maintenance=0.3,
        res_bonus=[2, 0, 0, 0, 0],
        description="Stores grain; boosts food production and slows food decay.",
    ),
]

# Produce influence, cost money
L1_INFLUENCE_BUILDINGS: list[CityBuilding] = [
    CityBuilding(
        "academy",
        1,
        money_cost=BASE_BUILDING_MONEY_COST,
        influence_cost=0,
        money_maintenance=BASE_BUILDING_MAINTENANCE_MONEY,
        influence_maintenance=-BASE_INFLUENCE_BUILDING_BONUS,
        res_bonus=[0, 0, 0, 0, 0],
        description="Generates influence through education.",
    ),
    CityBuilding(
        "barracks",
        1,
        money_cost=40,
        influence_cost=0,
        money_maintenance=30,
        influence_maintenance=0,
        res_bonus=[0, 0, 0, 0, 0],
        def_bonus=2,
        description="Trains soldiers; adds a defense bonus when this tile is attacked.",
    ),
]

# ---------------------------------------------------------------------------
# Level 2 city buildings  (roughly double cost/benefit of L1)
# ---------------------------------------------------------------------------

L2_MONEY_BUILDINGS: list[CityBuilding] = [
    CityBuilding(
        "grand market",
        2,
        money_cost=0,
        influence_cost=BASE_BUILDING_INFLUENCE_COST * 2.5,
        money_maintenance=-BASE_MONEY_BUILDING_BONUS * 2.4,
        influence_maintenance=BASE_BUILDING_MAINTENANCE_INFLUENCE * 2,
        res_bonus=[0, 0, 0, 0, 1],
        description="An upgraded marketplace that also produces gold.",
    ),
]

L2_INFLUENCE_BUILDINGS: list[CityBuilding] = [
    CityBuilding(
        "university",
        2,
        money_cost=BASE_BUILDING_MONEY_COST * 2,
        influence_cost=0,
        money_maintenance=BASE_BUILDING_MAINTENANCE_MONEY * 1.7,
        influence_maintenance=-BASE_INFLUENCE_BUILDING_BONUS * 2,
        res_bonus=[0, 0, 0, 0, 0],
        description="Enhanced academy; produces more influence and accelerates tech.",
    ),
    CityBuilding(
        "fortress",
        2,
        money_cost=80,
        influence_cost=5,
        money_maintenance=50,
        influence_maintenance=0.5,
        res_bonus=[0, 0, 1, 0, 0],
        def_bonus=4,
        description="A fortified garrison; significantly boosts tile defense.",
    ),
]
