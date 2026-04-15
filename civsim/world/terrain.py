"""Terrain types, their colours, and geographic metadata."""

from __future__ import annotations

from civsim.world.feature import Feature


class Terrain:
    def __init__(
        self, name: str, color: tuple[int, int, int], features: list[Feature], height: float
    ) -> None:
        self.name = name
        self.color = color
        self.features = features
        self.height = height  # Perlin noise value used for river generation
        self.defense_value = self._calculate_defense_value()
        if name == "Mountain":
            self.defense_value += 1

    def _calculate_defense_value(self) -> int:
        return sum(f.def_bonus for f in self.features)

    def show_features(self) -> str:
        return "; ".join(f.name for f in self.features)

    def get_info(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Terrain({self.name!r})"


# ---------------------------------------------------------------------------
# Terrain colour lookup  (RGB)
# ---------------------------------------------------------------------------
NAME_COLOR_PAIRS: dict[str, tuple[int, int, int]] = {
    "Plains": (50, 205, 50),
    "Grassland": (144, 238, 144),
    "Mountain": (230, 230, 250),
    "Desert": (255, 255, 0),
    "Ocean": (0, 0, 128),
    "Coast": (0, 0, 255),
    "Ice": (255, 255, 255),
    "Tundra": (255, 160, 122),
    "Highland": (210, 180, 140),
}

# Life-rating ranges per terrain (min, max)
NAME_LIFERATING_PAIRS: dict[str, tuple[int, int]] = {
    "Plains": (5, 9),
    "Grassland": (5, 9),
    "Mountain": (0, 0),
    "Desert": (0, 0),
    "Ocean": (0, 0),
    "Coast": (0, 0),
    "Ice": (0, 0),
    "Tundra": (1, 4),
    "Highland": (4, 8),
}

# ---------------------------------------------------------------------------
# Terrain category helpers
# ---------------------------------------------------------------------------
SPECIAL_TERRAINS: list[str] = ["Coast", "Desert", "Ocean", "Tundra", "Mountain", "Highland", "Ice"]
WATER_TERRAINS: list[str] = ["Coast", "Ocean", "Ice"]
NO_RESOURCE_TERRAINS: list[str] = ["Mountain", "Ocean", "Ice"]
UNCONTROLLABLE_TERRAINS: list[str] = ["Mountain", "Ocean", "Ice"]
NO_BEGINNING_TERRAINS: list[str] = ["Mountain", "Ocean", "Coast", "Ice"]


def get_normal_terrains() -> list[str]:
    """Return terrain names that are NOT in SPECIAL_TERRAINS."""
    return [t for t in NAME_COLOR_PAIRS if t not in SPECIAL_TERRAINS]


def get_all_terrains() -> list[str]:
    return list(NAME_COLOR_PAIRS.keys())
