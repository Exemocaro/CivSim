"""Resource types and their production values."""

from __future__ import annotations


class Resource:
    def __init__(self, name: str, rarity: int, bonus: float, fixed_val: int) -> None:
        self.name = name
        self.rarity = rarity  # relative spawn probability; land resources must sum to 100
        self.bonus = bonus  # percentage multiplier applied to base production
        self.fixed_val = fixed_val  # flat production added before the multiplier

    def __repr__(self) -> str:
        return f"Resource({self.name!r})"


# Rarities are relative weights and must sum to 100 within each group.
LAND_RESOURCES: list[Resource] = [
    Resource("Iron", 10, 1, 1),
    Resource("Wood", 15, 20, 1),
    Resource("Stone", 10, 1, 2),
    Resource("Gold", 5, 1, 1),
    Resource("Food", 60, 20, 1),
]

WATER_RESOURCES: list[Resource] = [
    Resource("Food(Fish)", 90, 1, 2),
    Resource("Food(Whales)", 10, 1, 5),
]

# Sentinel used for tiles with no resource.
NO_RESOURCE = Resource("", 0, 0, 0)
