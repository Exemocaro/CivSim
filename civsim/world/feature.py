"""Terrain features that modify tile bonuses."""

from __future__ import annotations


class Feature:
    def __init__(
        self,
        name: str,
        rarity: int,
        res_bonus: int,
        wel_bonus: int,
        life_bonus: int,
        res_bonus2: list[int],
        def_bonus: int,
    ) -> None:
        self.name = name
        self.rarity = rarity  # 0 means the feature is not randomly placed during world gen
        self.res_bonus = res_bonus  # percentage multiplier on the tile's primary resource
        self.wel_bonus = wel_bonus
        self.life_bonus = life_bonus
        self.food_bonus = res_bonus2[0]
        self.wood_bonus = res_bonus2[1]
        self.stone_bonus = res_bonus2[2]
        self.iron_bonus = res_bonus2[3]
        self.gold_bonus = res_bonus2[4]
        self.def_bonus = def_bonus

    def __repr__(self) -> str:
        return f"Feature({self.name!r})"


# ---------------------------------------------------------------------------
# Special features — rarity=0 means they are placed by world-gen code directly,
# not drawn from the random feature pool.
# ---------------------------------------------------------------------------
RIVER = Feature("river", 0, 10, 0, 1, [1, 0, 0, 0, 0], 1)
HILLS = Feature("hills", 0, 10, 0, 0, [1, 0, 0, 0, 0], 1)
FOREST = Feature("forest", 0, 10, 0, 0, [0, 1, 0, 0, 0], 0)
BIG_FOREST = Feature("big forest", 1, 1, 0, 0, [0, 2, 0, 0, 0], 1)

# ---------------------------------------------------------------------------
# Land features — drawn from this pool during world generation.
# ---------------------------------------------------------------------------
LAND_FEATURES: list[Feature] = [
    Feature("small caves", 3, 1, 0, 0, [0, 0, 0, 1, 0], 0),
    Feature("big caves", 1, 10, 0, 0, [0, 0, 0, 2, 1], 0),
    Feature("gold-rich caves", 1, 1, 0, 0, [0, 0, 0, 0, 2], 0),
    Feature("valleys", 3, 1, 0, 1, [1, 0, 1, 0, 0], 0),
    Feature("cliffs", 3, 1, 0, 0, [0, 0, 1, 0, 0], 1),
    Feature("small lakes", 3, 10, 0, 1, [1, 0, 0, 0, 0], 0),
    Feature("mounds", 6, 1, 0, 0, [0, 0, 1, 0, 0], 0),
    Feature("canyon", 1, 1, 1, 0, [0, 0, 1, 0, 0], 1),
    BIG_FOREST,
]

# ---------------------------------------------------------------------------
# Water features — drawn for coast tiles.
# ---------------------------------------------------------------------------
WATER_FEATURES: list[Feature] = [
    Feature("coral reef", 3, 1, 0, 0, [1, 0, 0, 0, 0], 0),
    Feature("deep trench", 3, 1, 0, 0, [1, 0, 0, 0, 0], 0),
]
