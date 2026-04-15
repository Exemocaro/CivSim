"""Individual map tile — population, production, buildings, and improvements."""

from __future__ import annotations

import logging
import math

from civsim.buildings.city_building import CityBuilding
from civsim.buildings.improvement import Improvement
from civsim.settings import (
    BASE_DECLINE_RATE,
    BASE_DEV_MAINTENANCE,
    BASE_FOOD,
    BASE_GOLD,
    BASE_GROWTH_RATE,
    BASE_IRON,
    BASE_STONE,
    BASE_WOOD,
    MAX_BUILDINGS_PER_TILE,
    MAX_IMPROVEMENTS_PER_TILE,
    REVOLT_DECAY,
    REVOLT_INCREMENT,
    REVOLT_THRESHOLD,
    TAX_BY_POP,
    UNHAPPY_PRODUCTION_PENALTY,
)
from civsim.world.resource import Resource
from civsim.world.terrain import WATER_TERRAINS, Terrain

logger = logging.getLogger(__name__)

# Type alias used for the production/resource dictionaries
Resources = dict[str, float]


class Tile:
    def __init__(
        self,
        tile_id: int,
        name: str,
        x: int,
        y: int,
        terrain: Terrain,
        population: int,
        resource: Resource,
        wealth: float,
        liferating: int,
        modifiers: dict[str, float],
    ) -> None:
        self.id = tile_id
        self.name = name
        self.x = x
        self.y = y
        self.terrain = terrain
        self.population = population
        self.resource = resource
        self.wealth = wealth
        self.liferating = liferating
        self.modifiers = modifiers  # {"dev": int, "rev": float}
        self.coords: tuple[int, int] = (x, y)

        self.buildings: list[CityBuilding] = []
        self.improvements: list[Improvement] = []

        self.base_wealth = wealth
        self.base_liferating = liferating
        self.growth_rate: float = 0.0
        self.value: float = 0.0
        self.tax_revenue: float = 0.0
        self.food_to_grow: int = 0
        self.minimum_food: int = 0
        self.is_happy: bool = True

        self.available_resources: Resources = {
            "food": 0.0,
            "wood": 0.0,
            "stone": 0.0,
            "iron": 0.0,
            "gold": 0.0,
        }
        self.production: Resources = {
            "food": 0.0,
            "wood": 0.0,
            "stone": 0.0,
            "iron": 0.0,
            "gold": 0.0,
        }

    # ------------------------------------------------------------------
    # Resource helpers
    # ------------------------------------------------------------------

    def get_leftovers(self) -> Resources:
        """Return available resources produced this turn."""
        return self.available_resources

    # ------------------------------------------------------------------
    # Development / building
    # ------------------------------------------------------------------

    def can_develop(self, amount: int = 1) -> bool:
        """True if the tile has enough wood to support a new development level."""
        return self.production["wood"] > 2

    def add_development(self, amount: int) -> None:
        self.modifiers["dev"] += amount

    def can_build_city_building(self) -> bool:
        return self.population > 0 and len(self.buildings) < MAX_BUILDINGS_PER_TILE

    def can_build_improvement(self, improvement: Improvement) -> bool:
        return (
            improvement.can_be_built_on(self.terrain.name)
            and len(self.improvements) < MAX_IMPROVEMENTS_PER_TILE
        )

    # ------------------------------------------------------------------
    # Production
    # ------------------------------------------------------------------

    def set_production(self) -> None:
        """Recalculate all production values for this tile."""
        self.wealth = self.base_wealth
        self.liferating = self.base_liferating

        self.production["food"] = BASE_FOOD
        self.production["wood"] = BASE_WOOD
        self.production["stone"] = BASE_STONE
        self.production["iron"] = BASE_IRON
        self.production["gold"] = BASE_GOLD

        res_name = self.resource.name.lower()
        for r in self.production:
            # Apply resource bonus to the matching production type
            if res_name == r or (res_name.startswith("food") and r == "food"):
                self.production[r] = (self.production[r] + self.resource.fixed_val) * (
                    self.resource.bonus / 100
                )
                # Multiplicative feature bonus on primary resource
                for f in self.terrain.features:
                    if f.res_bonus != 0:
                        self.production[r] *= f.res_bonus / 100

            # Flat wealth and development bonuses
            if self.production[r] != 0:
                self.production[r] += self.wealth
                self.production[r] += self.modifiers["dev"]
                self.production[r] -= 2 * self.modifiers["rev"]

            self.production[r] = round(self.production[r])

        self.update_values()

        # Flat feature bonuses
        self._add_features_bonus()

        # Improvement bonuses
        self._add_improvements_bonus()

        # Development maintenance reduces wood
        self.production["wood"] -= 2 * self.modifiers["dev"]

        # Unhappiness penalty on all production
        if not self.is_happy:
            for r in self.production:
                self.production[r] = round(self.production[r] * UNHAPPY_PRODUCTION_PENALTY)

    def update_values(self) -> None:
        """Enforce tile invariants (water/mountain have no production)."""
        if self.terrain.name in WATER_TERRAINS:
            self.liferating = 0
            self.production["wood"] = 0
            if not self.terrain.features:
                self.wealth = 0
                for r in self.production:
                    self.production[r] = 0
        if self.terrain.name == "Mountain":
            self.liferating = 0
            self.population = 0
            self.wealth = 0
            for r in self.production:
                self.production[r] = 0

    def _add_features_bonus(self) -> None:
        for f in self.terrain.features:
            self.wealth += f.wel_bonus
            self.liferating += f.life_bonus
            self.production["food"] += f.food_bonus
            self.production["wood"] += f.wood_bonus
            self.production["stone"] += f.stone_bonus
            self.production["iron"] += f.iron_bonus
            self.production["gold"] += f.gold_bonus

    def _add_improvements_bonus(self) -> None:
        for imp in self.improvements:
            self.production["food"] += imp.food_bonus
            self.production["wood"] += imp.wood_bonus
            self.production["stone"] += imp.stone_bonus
            self.production["iron"] += imp.iron_bonus
            self.production["gold"] += imp.gold_bonus

    # ------------------------------------------------------------------
    # Population / development cycle
    # ------------------------------------------------------------------

    def develop(self) -> None:
        """Update population, happiness, and accumulated resources for one turn."""
        # Restock available resources from this turn's production
        for r in self.available_resources:
            self.available_resources[r] = self.production[r]

        # Food needed to grow / survive
        self.food_to_grow = self.population // 1000
        self.minimum_food = math.ceil(self.food_to_grow / 2)

        can_feed = self.production["food"] >= self.minimum_food
        self.is_happy = can_feed and self.modifiers["rev"] < REVOLT_THRESHOLD

        if self.available_resources["food"] >= self.food_to_grow:
            self.available_resources["food"] -= self.food_to_grow
            self.available_resources["food"] = max(
                0.0, round(self.available_resources["food"] * 10) / 10
            )
            self.growth_rate = BASE_GROWTH_RATE + self.liferating * 0.001

        elif self.available_resources["food"] >= self.minimum_food:
            # Enough to survive but not grow
            self.available_resources["food"] -= self.minimum_food
            self.growth_rate = 0.0

        else:
            # Starving — population declines
            self.growth_rate = BASE_DECLINE_RATE

        self.growth_rate = round(self.growth_rate * 10000) / 10000
        self.population += round(self.population * self.growth_rate)

        # Update revolt based on happiness (already computed above)
        if self.is_happy:
            self.modifiers["rev"] = max(0.0, self.modifiers["rev"] - REVOLT_DECAY)
        else:
            self.modifiers["rev"] += REVOLT_INCREMENT

        # Tile value (log-scale population index; safe guard against pop=0)
        if self.population > 0:
            self.value = round(math.log10(self.population) * 100) / 100 - 2
        else:
            self.value = 0.0

        # Tax revenue
        self.tax_revenue = round(self.population * TAX_BY_POP)

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def get_maintenance(self) -> list[float]:
        """Return [money_maintenance, influence_maintenance]."""
        money_maint = 0.0
        influence_maint = 0.0

        if self.population > 0:
            for building in self.buildings:
                m, i = building.get_maintenance()
                money_maint += m
                influence_maint += i

            dev_level = self.modifiers["dev"]
            influence_maint += self.modifiers["rev"] + self.value + BASE_DEV_MAINTENANCE + dev_level

        # Improvements always incur maintenance (they're on the land, not in cities)
        for imp in self.improvements:
            influence_maint += imp.influence_maintenance

        return [money_maint, influence_maint]

    def get_num_buildings(self) -> int:
        return len(self.buildings)

    def get_num_improvements(self) -> int:
        return len(self.improvements)

    # ------------------------------------------------------------------
    # Influence contribution
    # ------------------------------------------------------------------

    def get_influence(self) -> float:
        return self.value

    # ------------------------------------------------------------------
    # Neighbours
    # ------------------------------------------------------------------

    def get_neighbours(self, tiles: list[list[Tile]], max_x: int, max_y: int) -> list[Tile]:
        """Return all 8 surrounding tiles (cardinal + diagonal), respecting boundaries."""
        neighbours: list[Tile] = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                ny, nx = self.y + dy, self.x + dx
                if 0 <= ny < max_y and 0 <= nx < max_x:
                    neighbours.append(tiles[ny][nx])
        return neighbours

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def compare_tile(self, other: Tile) -> bool:
        return self.id == other.id

    # ------------------------------------------------------------------
    # Info / display
    # ------------------------------------------------------------------

    def production_to_string(self) -> str:
        parts = [f"{k[0].upper()}:{round(v)}" for k, v in self.production.items()]
        return "Production: " + " ".join(parts)

    def get_info(self, nation: object) -> list[str]:
        """Return a list of strings shown in the right-panel UI."""
        from civsim.simulation.nation import Nation  # local import to avoid circular dep

        n: Nation = nation  # type: ignore[assignment]

        happiness_str = "Happy" if self.is_happy else "Unhappy"
        improvements_str = (
            ", ".join(i.name for i in self.improvements) if self.improvements else "None"
        )
        buildings_str = ", ".join(b.name for b in self.buildings) if self.buildings else "None"

        return [
            f"{n.id} | {n.representation}",
            f"Name: {self.name}",
            f"Coords: {self.coords}",
            f"Terrain: {self.terrain.get_info()}",
            f"Population: {self.population}",
            f"Resource: {self.resource.name}",
            f"Wealth: {round(self.wealth, 2)}",
            f"Life Rating: {self.liferating}",
            f"Features: {self.terrain.show_features()}",
            f"Dev: {int(self.modifiers['dev'])}  Revolt: {round(self.modifiers['rev'], 2)}",
            f"Value: {round(self.value, 2)}  {happiness_str}",
            self.production_to_string(),
            f"Tax Revenue: {round(self.tax_revenue, 2)}",
            f"Buildings: {buildings_str}",
            f"Improvements: {improvements_str}",
            f"Tech Level: {n.tech_level}",
            f"Phase: {n.personality.phase}  Wars: {len(n.wars)}",
            n.leader.representation,
            n.leader.get_values(),
        ]

    def print_info(self, nation: object) -> None:
        for line in self.get_info(nation):
            print(line)
