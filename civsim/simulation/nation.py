"""Nation — the core AI entity that controls tiles, declares wars, and expands."""

from __future__ import annotations

import logging
import random
from math import sqrt
from typing import TYPE_CHECKING

from civsim.buildings.city_building import (
    L1_INFLUENCE_BUILDINGS,
    L1_MONEY_BUILDINGS,
    L2_INFLUENCE_BUILDINGS,
    L2_MONEY_BUILDINGS,
    CityBuilding,
)
from civsim.buildings.improvement import IMPROVEMENTS, Improvement
from civsim.characters.character import Character
from civsim.settings import (
    ACTIONS_STEP,
    ACTIONS_STEP_VALUE,
    BASE_INFLUENCE_PER_TURN,
    BASE_ROT_PERCENTAGE,
    BUILDINGS_PER_ACTION,
    CONQUER_ACCURACY,
    COUNTRY_DEV_STABILIZER,
    IMPROVEMENT_ROAD_CONQUER_DISCOUNT,
    KINGDOM_NAMES_FILE,
    LEADER_DEATH_INFLUENCE_PENALTY,
    LEADER_DEATH_MONEY_PENALTY,
    MAX_BATTLE_RNG,
    MAX_NATION_COLOR_VALUE,
    MAX_TECH_LEVEL,
    MIN_ACTIONS,
    MIN_WARS,
    PROBABILITY_AGGRESSIVE_EXPANSION,
    PROBABILITY_ENDING_WAR,
    PROBABILITY_ENDING_WAR_MAX,
    PROBABILITY_WAR_PER_TURN,
    PROSPERITY_MONEY_BONUS,
    PROSPERITY_ROT_FACTOR,
    SAFE_INFLUENCE_TO_DEV,
    TAX_BY_POP,
    TECH_BONUS,
    TERRAIN_DEFENSE_WEIGHT,
    TURNS_TO_EXPAND,
    WAR_COST,
    WAR_INFLUENCE_MAINTENANCE_COST,
    WAR_INFLUENCE_REWARD,
    WAR_MAINTENANCE_RANGE,
    WAR_MONEY_REWARD,
    WARS_STEP,
    WARS_STEP_VALUE,
)
from civsim.simulation.personality import SIMPLE_PERSONALITIES, Personality
from civsim.world.terrain import NO_BEGINNING_TERRAINS

if TYPE_CHECKING:
    from civsim.world.tile import Tile

logger = logging.getLogger(__name__)

TilesByNation = dict[tuple[int, int], int]
War = list  # [Nation, float]  —  [enemy_nation, war_budget]


class Nation:
    def __init__(
        self,
        nation_id: int,
        color: tuple[int, int, int],
        name: str,
        leader: Character,
        wars: list[War],
        personality: Personality,
    ) -> None:
        self.id = nation_id
        self.color = color
        self.name = name
        self.leader = leader
        self.wars = wars
        self.personality = personality

        self.resources: dict[str, float] = {
            "food": 0.0,
            "wood": 0.0,
            "stone": 0.0,
            "iron": 0.0,
            "gold": 0.0,
        }

        self.max_wars: int = 0
        self.focused_tiles: list[Tile] = []
        self.capital: Tile | None = None
        self.attack_center: Tile | None = None
        self.turns_with_no_change_in_attack_center: int = 0

        self.last_influence: float = 0.0
        self.influence: float = 5.0

        self.tech_level: int = 0
        self.country_dev: float = 1.0

        self.last_money: float = 0.0
        self.money: float = 5.0

        self.actions: int = 2
        self.max_actions: int = 2

        self.num_buildings: int = 0

        self.war_influence_cost: float = 0.0

        # Border tiles (tiles adjacent to our territory that we don't own).
        # Maintained incrementally: updated in conquer_tile / disband.
        self.neighbour_tiles: list[Tile] = []

        self.was_eliminated: bool = False

        self.tiles_to_dev: list[Tile] = []
        self.turns_no_expand: int = 0
        self.rot_percentage: float = BASE_ROT_PERCENTAGE - (self.tech_level * 2)

        self.size: int = 1
        self.representation = "Uncontrolled" if name == "" else name

    # ------------------------------------------------------------------
    # Capital
    # ------------------------------------------------------------------

    def set_capital(self, tile: Tile) -> None:
        self.capital = tile
        self.attack_center = tile

    def update_capital(self, controlled_tiles: list[Tile], tiles_by_nation: TilesByNation) -> None:
        if self.capital is None or (
            not self.is_nation_controller(self.capital, tiles_by_nation) and controlled_tiles
        ):
            for tile in random.sample(controlled_tiles, len(controlled_tiles)):
                if tile.terrain.name not in NO_BEGINNING_TERRAINS:
                    self.set_capital(tile)
                    return

    # ------------------------------------------------------------------
    # Tile ownership helpers
    # ------------------------------------------------------------------

    def change_tile_ownership(self, tile: Tile, tiles_by_nation: TilesByNation) -> None:
        tiles_by_nation[tile.coords] = self.id

    def is_nation_controller(self, tile: Tile, tiles_by_nation: TilesByNation) -> bool:
        return tiles_by_nation.get(tile.coords) == self.id

    def get_controller_id(self, tile: Tile, tiles_by_nation: TilesByNation) -> int:
        return tiles_by_nation.get(tile.coords, 0)

    def get_tiles(self, tiles_by_nation: TilesByNation, tiles: list[list[Tile]]) -> list[Tile]:
        return [
            tiles[coord[1]][coord[0]]
            for coord, nation_id in tiles_by_nation.items()
            if nation_id == self.id
        ]

    def get_tile_by_coords(self, coords: tuple[int, int], tiles: list[list[Tile]]) -> Tile:
        return tiles[coords[1]][coords[0]]

    # ------------------------------------------------------------------
    # Neighbour tile cache (performance fix)
    # ------------------------------------------------------------------

    def rebuild_neighbour_tiles(
        self, controlled_tiles: list[Tile], tiles: list[list[Tile]], tiles_by_nation: TilesByNation
    ) -> None:
        """Full rebuild — only used on first turn or after disband."""
        seen: set[tuple[int, int]] = set()
        result: list[Tile] = []
        for tile in controlled_tiles:
            for n in tile.get_neighbours(tiles, len(tiles[0]), len(tiles)):
                if not self.is_nation_controller(n, tiles_by_nation) and n.coords not in seen:
                    seen.add(n.coords)
                    result.append(n)
        self.neighbour_tiles = result

    def _update_neighbours_after_conquest(
        self, conquered: Tile, tiles: list[list[Tile]], tiles_by_nation: TilesByNation
    ) -> None:
        """Incrementally update neighbour_tiles when we conquer a tile."""
        # The conquered tile is now ours — remove it from neighbours
        self.neighbour_tiles = [t for t in self.neighbour_tiles if t.coords != conquered.coords]
        # Add its neighbours that we don't own
        seen = {t.coords for t in self.neighbour_tiles}
        for n in conquered.get_neighbours(tiles, len(tiles[0]), len(tiles)):
            if not self.is_nation_controller(n, tiles_by_nation) and n.coords not in seen:
                seen.add(n.coords)
                self.neighbour_tiles.append(n)

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    def add_resources(self, rs: dict[str, float]) -> None:
        for r, v in rs.items():
            self.resources[r] += v

    def rot_resources(self, percentage: float) -> None:
        """Decay stockpile by *percentage*%, reduced by leader prosperity."""
        effective_pct = percentage - self.leader.prosperity * PROSPERITY_ROT_FACTOR
        effective_pct = max(0.0, effective_pct)
        for r in self.resources:
            self.resources[r] = round(self.resources[r] * ((100 - effective_pct) / 100))

    def resources_to_string(self) -> str:
        return "Production: " + " ".join(
            f"{k[0].upper()}:{round(v)}" for k, v in self.resources.items()
        )

    # ------------------------------------------------------------------
    # Money & influence
    # ------------------------------------------------------------------

    def update_money(self, total_population: int, total_maintenance: float) -> bool:
        self.last_money = self.money
        self.money += total_population * TAX_BY_POP
        self.money += self.leader.prosperity * PROSPERITY_MONEY_BONUS
        self.money -= total_maintenance
        self.money = round(self.money, 3)
        return self.money > self.last_money

    def update_influence(self, total_maintenance: float, tile_bonus: float) -> bool:
        self.last_influence = self.influence
        self.influence += BASE_INFLUENCE_PER_TURN
        self.influence += self.leader.prosperity  # prosperity also boosts influence
        self.influence += tile_bonus
        self.influence -= total_maintenance
        self.influence -= self.war_influence_cost
        self.influence = round(self.influence, 2)
        return self.influence > self.last_influence

    def get_war_maintenance(self) -> float:
        return sum(war[1] for war in self.wars)

    # ------------------------------------------------------------------
    # Aggregated stats
    # ------------------------------------------------------------------

    def get_data(
        self,
        tiles: list[list[Tile]],
        controlled_tiles: list[Tile],
        tiles_by_nation: TilesByNation,
        turn: int,
    ) -> tuple[int, float, list[float], float, float, float, int]:
        """Collect per-turn nation statistics."""
        total_influence = 0.0
        maintenance = [0.0, 0.0]
        total_value = 0.0
        biggest = 0.0
        pop = 0
        num_buildings = 0

        for tile in controlled_tiles:
            tile_maint = tile.get_maintenance()
            num_buildings += tile.get_num_buildings()
            total_influence += tile.get_influence()
            maintenance[0] += tile_maint[0]
            maintenance[1] += tile_maint[1]
            total_value += tile.value
            pop += tile.population
            if tile.value > biggest:
                biggest = tile.value

        maintenance[0] += self.get_war_maintenance()
        average = 0.0 if not controlled_tiles else round(total_value / len(controlled_tiles), 2)
        total_influence *= TECH_BONUS[self.tech_level]
        return (num_buildings, total_influence, maintenance, total_value, average, biggest, pop)

    # ------------------------------------------------------------------
    # Technology
    # ------------------------------------------------------------------

    def get_nations_devs(self, nations: list[Nation]) -> list[float]:
        return [
            n.country_dev
            for n in nations
            if not n.was_eliminated
            and n.country_dev != 0
            and self.country_dev > COUNTRY_DEV_STABILIZER
        ]

    def update_tech(
        self,
        average_value: float,
        total_value: float,
        num_buildings: int,
        controlled_tiles: list[Tile],
        turn: int,
        nations: list[Nation],
    ) -> None:
        if turn <= 1 or not controlled_tiles:
            return
        multiplier = average_value * self.max_actions * self.size
        if multiplier != 0:
            self.country_dev = ((total_value + num_buildings) / multiplier) + COUNTRY_DEV_STABILIZER
        else:
            self.country_dev = COUNTRY_DEV_STABILIZER
        self.country_dev = round(self.country_dev, 4)

        dev_list = self.get_nations_devs(nations)
        if not dev_list:
            return
        min_d = min(dev_list)
        max_d = max(dev_list)
        diff = (max_d - min_d) / MAX_TECH_LEVEL if MAX_TECH_LEVEL else 0
        new_level = 0
        cursor = min_d
        while cursor <= self.country_dev and new_level < MAX_TECH_LEVEL and cursor > 0.1:
            cursor += diff
            new_level += 1

        if new_level > self.tech_level:
            self.tech_level += 1
        elif new_level < self.tech_level:
            self.tech_level -= 1

    # ------------------------------------------------------------------
    # Actions / war slots
    # ------------------------------------------------------------------

    def update_actions(self, controlled_tiles: list[Tile]) -> None:
        n = len(controlled_tiles)
        self.actions = MIN_ACTIONS + (n // ACTIONS_STEP_VALUE) * ACTIONS_STEP
        self.max_actions = self.actions

    def update_max_wars(self, controlled_tiles: list[Tile]) -> None:
        n = len(controlled_tiles)
        self.max_wars = MIN_WARS + (n // WARS_STEP_VALUE) * WARS_STEP

    # ------------------------------------------------------------------
    # Tile conquest
    # ------------------------------------------------------------------

    def conquer_tile(
        self,
        tile: Tile,
        tiles_by_nation: TilesByNation,
        tiles: list[list[Tile]],
        consumes_action: bool,
    ) -> None:
        self.change_tile_ownership(tile, tiles_by_nation)

        cost = self.personality.influence_cost_to_conquer
        # Road discount: if any adjacent friendly tile has a road, reduce cost
        for n in tile.get_neighbours(tiles, len(tiles[0]), len(tiles)):
            if self.is_nation_controller(n, tiles_by_nation) and any(
                imp.name == "road" for imp in n.improvements
            ):
                cost *= IMPROVEMENT_ROAD_CONQUER_DISCOUNT
                break
        self.influence -= cost

        self._update_neighbours_after_conquest(tile, tiles, tiles_by_nation)
        if consumes_action:
            self.actions -= 1

    def lose_battle(self) -> None:
        tech_bonus = TECH_BONUS[self.tech_level]
        self.influence -= self.personality.influence_cost_to_conquer * tech_bonus

    def conquered_capital(
        self, enemy: Nation, tiles: list[list[Tile]], tiles_by_nation: TilesByNation
    ) -> None:
        cost = self.personality.influence_cost_to_conquer
        bonus = TECH_BONUS[self.tech_level] * TECH_BONUS[enemy.tech_level]
        for coords, owner_id in list(tiles_by_nation.items()):
            if owner_id == enemy.id and self.influence > cost * bonus:
                t = self.get_tile_by_coords(coords, tiles)
                self.change_tile_ownership(t, tiles_by_nation)
                self.influence -= cost

    # ------------------------------------------------------------------
    # Disbanding
    # ------------------------------------------------------------------

    def disband(self, tiles_by_nation: TilesByNation) -> None:
        """Remove this nation from all tiles it controls."""
        for coords in list(tiles_by_nation.keys()):
            if tiles_by_nation[coords] == self.id:
                tiles_by_nation[coords] = 0
        self.neighbour_tiles = []

    # ------------------------------------------------------------------
    # Battle
    # ------------------------------------------------------------------

    def do_battle(self, war: War, tile: Tile) -> bool:
        """Resolve combat. Returns True if attacker wins."""
        enemy: Nation = war[0]
        attacker_rng = random.randint(1, MAX_BATTLE_RNG)
        defender_rng = random.randint(1, MAX_BATTLE_RNG)

        attacker_iron = round((self.resources["iron"] / self.size) * 10) if self.size > 0 else 0
        defender_iron = round((enemy.resources["iron"] / enemy.size) * 10) if enemy.size > 0 else 0

        our_chances = (
            war[1]
            + attacker_rng
            + attacker_iron
            + TECH_BONUS[self.tech_level] * self.leader.martial
        )
        their_chances = (
            enemy.get_war_budget(self)
            + defender_rng
            + defender_iron
            + TECH_BONUS[enemy.tech_level] * enemy.leader.martial
        )

        # Terrain and building defense bonus for the defender
        tile_defense = tile.terrain.defense_value
        tile_defense += sum(b.def_bonus for b in tile.buildings)
        their_chances += tile_defense * TERRAIN_DEFENSE_WEIGHT

        return our_chances > their_chances

    # ------------------------------------------------------------------
    # War management
    # ------------------------------------------------------------------

    def get_war_budget(self, enemy: Nation) -> float:
        for war in self.wars:
            if war[0].id == enemy.id:
                return war[1]
        logger.warning("get_war_budget: nation %d is not at war with nation %d", self.id, enemy.id)
        return -1.0

    def remove_war(self, enemy: Nation) -> bool:
        for war in self.wars:
            if war[0] is enemy:
                self.wars.remove(war)
                return True
        logger.warning("remove_war: nation %d is not at war with nation %d", self.id, enemy.id)
        return False

    def end_war(self, enemy: Nation) -> None:
        self.remove_war(enemy)
        enemy.remove_war(self)

    def take_lost_war_penalties(self, enemy: Nation) -> None:
        bonus = TECH_BONUS[enemy.tech_level]
        self.money -= WAR_MONEY_REWARD * bonus
        enemy.money += WAR_MONEY_REWARD * bonus
        self.influence -= WAR_INFLUENCE_REWARD * bonus
        enemy.influence += WAR_INFLUENCE_REWARD * bonus

    def return_new_war_budget(self, money_dif: float, enemy: Nation) -> float:
        limit = min(WAR_MAINTENANCE_RANGE[1], int(money_dif))
        prob = random.randint(1, 10)
        if prob < 2:
            return random.randint(max(1, limit - 5), max(1, limit))
        elif prob <= 5:
            half = (limit - WAR_MAINTENANCE_RANGE[0]) // 2
            return random.randint(max(1, half), max(1, limit))
        return random.randint(WAR_MAINTENANCE_RANGE[0], max(WAR_MAINTENANCE_RANGE[0], limit))

    # ------------------------------------------------------------------
    # Enemy neighbours
    # ------------------------------------------------------------------

    def get_enemy_neighbours(
        self, tiles: list[list[Tile]], tiles_by_nation: TilesByNation
    ) -> list[Tile]:
        enemy_ids = {war[0].id for war in self.wars}
        enemy_neighbours: list[Tile] = []
        self.focused_tiles = []

        for n in self.neighbour_tiles:
            if self.get_controller_id(n, tiles_by_nation) in enemy_ids:
                enemy_neighbours.append(n)
                # Detect enclaves — enemy tiles surrounded entirely by our territory
                if all(self.is_nation_controller(t, tiles_by_nation) for t in enemy_neighbours):
                    self.focused_tiles.append(n)

        return enemy_neighbours

    # ------------------------------------------------------------------
    # Attack
    # ------------------------------------------------------------------

    def make_attack(
        self,
        tiles: list[list[Tile]],
        nations: list[Nation],
        tiles_by_nation: TilesByNation,
        controlled_tiles: list[Tile],
    ) -> None:
        if not self.wars:
            return

        enemy_tiles = self.get_enemy_neighbours(tiles, tiles_by_nation)
        if not enemy_tiles:
            # No adjacent enemy tiles — make peace with everyone
            for _war in list(self.wars):
                self.end_war(_war[0])
            return

        # Choose target: prioritise enclaves, otherwise pick the tile closest
        # to attack_center from a sample of CONQUER_ACCURACY candidates.
        if self.focused_tiles and not self.is_nation_controller(
            self.focused_tiles[0], tiles_by_nation
        ):
            tile_to_conquer = self.focused_tiles[0]
        else:
            if self.focused_tiles:
                self.focused_tiles.pop(0)
            candidates = [random.choice(enemy_tiles) for _ in range(CONQUER_ACCURACY)]
            center = self.attack_center
            if center:
                candidates.sort(key=lambda t: sqrt((t.x - center.x) ** 2 + (t.y - center.y) ** 2))
            tile_to_conquer = candidates[0]

        nation_id = self.get_controller_id(tile_to_conquer, tiles_by_nation)
        war: War | None = next((w for w in self.wars if w[0].id == nation_id), None)
        if war is None:
            return

        enemy: Nation = war[0]
        if enemy.size <= 0:
            self.end_war(enemy)
            return

        if self.influence <= self.personality.influence_cost_to_conquer:
            return

        if self.do_battle(war, tile_to_conquer):
            if self.actions > 0:
                self.conquer_tile(tile_to_conquer, tiles_by_nation, tiles, True)
                if tile_to_conquer is enemy.capital:
                    self.conquered_capital(enemy, tiles, tiles_by_nation)
        else:
            self.lose_battle()

    # ------------------------------------------------------------------
    # Attack center
    # ------------------------------------------------------------------

    def update_attack_center(
        self, tiles_by_nation: TilesByNation, controlled_tiles: list[Tile]
    ) -> None:
        self.turns_with_no_change_in_attack_center += 1
        if (
            random.randint(1, 100) <= self.turns_with_no_change_in_attack_center * 2
            or (
                self.attack_center
                and not self.is_nation_controller(self.attack_center, tiles_by_nation)
            )
        ) and controlled_tiles:
            self.attack_center = random.choice(controlled_tiles)
            self.turns_with_no_change_in_attack_center = 0

    # ------------------------------------------------------------------
    # Diplomacy / stance
    # ------------------------------------------------------------------

    def update_stance(
        self,
        tiles: list[list[Tile]],
        nations: list[Nation],
        tiles_by_nation: TilesByNation,
        controlled_tiles: list[Tile],
        is_money_growing: bool,
    ) -> None:
        self.update_attack_center(tiles_by_nation, controlled_tiles)
        money_dif = self.money - self.last_money
        num_wars = len(self.wars)

        if not controlled_tiles:
            for war in list(self.wars):
                self.wars.remove(war)
            self.war_influence_cost = 0.0
            return

        if num_wars == 0:
            self.war_influence_cost = 0.0
        else:
            self.war_influence_cost += (
                TECH_BONUS[self.tech_level] * WAR_INFLUENCE_MAINTENANCE_COST
            ) * num_wars

        new_war = False
        if (
            self.money > WAR_COST
            and money_dif > WAR_MAINTENANCE_RANGE[0]
            and num_wars < self.max_wars
            and random.randint(1, 100) <= PROBABILITY_WAR_PER_TURN
        ):
            for tile in controlled_tiles:
                for n in tile.get_neighbours(tiles, len(tiles[0]), len(tiles)):
                    neighbour_id = self.get_controller_id(n, tiles_by_nation)
                    if neighbour_id not in (self.id, 0) and len(self.wars) < self.max_wars:
                        for nation in nations:
                            if nation.id == neighbour_id:
                                # Avoid declaring war on the same nation twice
                                if not any(w[0].id == nation.id for w in self.wars):
                                    self.wars.append(
                                        [nation, self.return_new_war_budget(money_dif, nation)]
                                    )
                                    nation.wars.append(
                                        [self, nation.return_new_war_budget(money_dif, self)]
                                    )
                                    new_war = True
                                break
                    if new_war:
                        break
                if new_war:
                    break

        if num_wars > 0 and not new_war:
            r = random.randint(1, 100)
            if (
                num_wars > self.max_wars or self.influence < 0 or self.money < 0
            ) and r <= PROBABILITY_ENDING_WAR_MAX:
                random_war = random.choice(self.wars)
                self.end_war(random_war[0])
                self.take_lost_war_penalties(random_war[0])
            elif r <= PROBABILITY_ENDING_WAR:
                random_war = random.choice(self.wars)
                self.end_war(random_war[0])

    # ------------------------------------------------------------------
    # Development
    # ------------------------------------------------------------------

    def add_dev_to_tile(self, dev_value: int, tile: Tile) -> None:
        tile.add_development(dev_value)
        self.influence -= self.personality.influence_cost_to_dev

    def check_tiles_to_dev(self, tiles_by_nation: TilesByNation) -> None:
        self.tiles_to_dev = [
            t
            for t in self.tiles_to_dev
            if self.get_controller_id(t, tiles_by_nation) == 0
            or self.is_nation_controller(t, tiles_by_nation)
        ]

    def develop_tiles(
        self,
        tiles: list[list[Tile]],
        controlled_tiles: list[Tile],
        tiles_by_nation: TilesByNation,
        is_influence_growing: bool,
    ) -> None:
        from civsim.simulation.ai_strategy import get_dev_tiles  # avoid circular

        if not self.tiles_to_dev:
            self.tiles_to_dev = get_dev_tiles(self, tiles, tiles_by_nation, controlled_tiles)
            if not self.tiles_to_dev:
                return

        if not (
            is_influence_growing
            or self.influence > SAFE_INFLUENCE_TO_DEV * self.personality.influence_cost_to_dev
        ):
            return

        tile = self.tiles_to_dev.pop(0)  # consume best-scored tile first (front of ranked queue)

        if self.is_nation_controller(tile, tiles_by_nation):
            if tile.can_develop() and self.influence > self.personality.influence_cost_to_dev:
                self.add_dev_to_tile(1, tile)
                self.actions -= 1
        elif self.get_controller_id(tile, tiles_by_nation) != 0:
            pass  # already removed above; enemy tile — skip
        else:
            if self.influence > self.personality.influence_cost_to_conquer:
                self.conquer_tile(tile, tiles_by_nation, tiles, True)

    # ------------------------------------------------------------------
    # Building construction
    # ------------------------------------------------------------------

    def choose_city_building(self, code: str) -> CityBuilding | None:
        """Pick an affordable building; 'i' = influence-producing, 'm' = money-producing."""
        if code == "i":
            pool = L2_INFLUENCE_BUILDINGS if self.tech_level >= 5 else L1_INFLUENCE_BUILDINGS
            if self.money >= pool[0].money_cost:
                return random.choice(pool)
        elif code == "m":
            pool = L2_MONEY_BUILDINGS if self.tech_level >= 5 else L1_MONEY_BUILDINGS
            if self.influence >= pool[0].influence_cost:
                return random.choice(pool)
        return None

    def choose_improvement(self, tile: Tile) -> Improvement | None:
        """Pick an affordable improvement compatible with the tile's terrain."""
        compatible = [
            imp
            for imp in IMPROVEMENTS
            if tile.can_build_improvement(imp) and self.influence >= imp.influence_cost
        ]
        return random.choice(compatible) if compatible else None

    def build_things(
        self,
        controlled_tiles: list[Tile],
        is_money_growing: bool,
        is_influence_growing: bool,
        num_buildings: int,
    ) -> None:
        if not controlled_tiles:
            return

        # --- City buildings (require population) ---
        populated = [
            t for t in controlled_tiles if t.population > 0 and t.can_build_city_building()
        ]
        if populated:
            # Shuffle to pick random candidate tiles
            candidates = random.sample(populated, min(num_buildings, len(populated)))
            buildings: list[CityBuilding | None] = [
                self.choose_city_building("i")
                if is_money_growing
                else self.choose_city_building("m"),
                self.choose_city_building("m")
                if is_influence_growing
                else self.choose_city_building("i"),
            ]
            for i, tile in enumerate(candidates):
                if i >= len(buildings):
                    break
                building = buildings[i]
                if building is None or self.actions <= 0:
                    continue
                if (
                    building.influence_cost > 0
                    and self.influence >= building.influence_cost
                    or building.money_cost > 0
                    and self.money >= building.money_cost
                ):
                    tile.buildings.append(building)
                    self.influence -= building.influence_cost
                    self.money -= building.money_cost
                    self.actions -= 1

        # --- Tile improvements (no population required) ---
        if self.actions > 0:
            improvable = [t for t in controlled_tiles if len(t.improvements) < 3]
            if improvable:
                tile = random.choice(improvable)
                imp = self.choose_improvement(tile)
                if imp and self.influence >= imp.influence_cost and self.money >= imp.money_cost:
                    tile.improvements.append(imp)
                    self.influence -= imp.influence_cost
                    self.money -= imp.money_cost
                    self.actions -= 1

    # ------------------------------------------------------------------
    # Per-turn update helpers
    # ------------------------------------------------------------------

    def update_tiles(self, controlled_tiles: list[Tile]) -> None:
        for tile in controlled_tiles:
            if tile.population > 0:
                tile.set_production()
                tile.develop()
                self.add_resources(tile.get_leftovers())

    def update_personality(self) -> None:
        if self.turns_no_expand > TURNS_TO_EXPAND:
            self.personality.phase = "peacefully-expanding"
        if (
            self.personality.phase != "aggressively-expanding"
            and random.randint(0, 100) < PROBABILITY_AGGRESSIVE_EXPANSION
        ):
            self.personality.phase = "aggressively-expanding"
        self.personality.update_values()

    def update_size(self, controlled_tiles: list[Tile]) -> None:
        new_size = len(controlled_tiles)
        if new_size != self.size:
            self.size = new_size
            self.turns_no_expand = 0
        else:
            self.turns_no_expand += 1

    def check_existence(
        self,
        tiles_by_nation: TilesByNation,
        controlled_tiles: list[Tile],
    ) -> None:
        if not controlled_tiles:
            logger.info("Nation %s (id=%d) was eliminated.", self.name, self.id)
            self.was_eliminated = True
            self.disband(tiles_by_nation)

    # ------------------------------------------------------------------
    # Main turn
    # ------------------------------------------------------------------

    def make_turn(
        self,
        tiles: list[list[Tile]],
        nations: list[Nation],
        tiles_by_nation: TilesByNation,
        turn: int,
    ) -> None:
        if self.id == 0 or self.was_eliminated:
            return

        controlled_tiles = self.get_tiles(tiles_by_nation, tiles)

        # First turn: build the neighbour cache from scratch
        if turn == 1:
            self.rebuild_neighbour_tiles(controlled_tiles, tiles, tiles_by_nation)

        (
            num_buildings,
            total_influence_bonus,
            total_maintenance,
            total_value,
            average_value,
            biggest_val,
            total_pop,
        ) = self.get_data(tiles, controlled_tiles, tiles_by_nation, turn)

        self.update_size(controlled_tiles)
        self.update_actions(controlled_tiles)
        self.update_max_wars(controlled_tiles)
        self.num_buildings = num_buildings

        is_money_growing = self.update_money(total_pop, total_maintenance[0])
        is_influence_growing = self.update_influence(total_maintenance[1], total_influence_bonus)

        if logger.isEnabledFor(logging.DEBUG):
            arrow_m = "↑" if is_money_growing else "↓"
            arrow_i = "↑" if is_influence_growing else "↓"
            logger.debug(
                "Nation %d | tiles=%d money=%.0f%s inf=%.0f%s wars=%d(%d)",
                self.id,
                len(controlled_tiles),
                self.money,
                arrow_m,
                self.influence,
                arrow_i,
                len(self.wars),
                self.max_wars,
            )

        # --- Action-consuming phase ---
        self.check_tiles_to_dev(tiles_by_nation)
        did_something = True
        while self.actions > 0 and did_something:
            before_actions = self.actions
            before_tiles_to_dev = len(self.tiles_to_dev)
            self.develop_tiles(tiles, controlled_tiles, tiles_by_nation, is_influence_growing)
            self.build_things(
                controlled_tiles, is_money_growing, is_influence_growing, BUILDINGS_PER_ACTION
            )
            self.make_attack(tiles, nations, tiles_by_nation, controlled_tiles)
            # Progress if actions were consumed OR tiles_to_dev queue moved forward
            did_something = (
                self.actions != before_actions or len(self.tiles_to_dev) != before_tiles_to_dev
            )

        # --- Free-action phase ---
        self.update_tiles(controlled_tiles)
        self.update_personality()
        self.update_stance(tiles, nations, tiles_by_nation, controlled_tiles, is_money_growing)
        self.update_capital(controlled_tiles, tiles_by_nation)
        self.rot_resources(self.rot_percentage)

        # Leader ageing — detect death by id change and apply penalties
        prev_leader_id = self.leader.id
        self.leader = self.leader.update()
        if self.leader.id != prev_leader_id:
            logger.info(
                "Nation %s: leader died. Applying death penalties (inf -%.0f, money -%.0f).",
                self.name,
                LEADER_DEATH_INFLUENCE_PENALTY,
                LEADER_DEATH_MONEY_PENALTY,
            )
            self.influence -= LEADER_DEATH_INFLUENCE_PENALTY
            self.money -= LEADER_DEATH_MONEY_PENALTY

        self.update_tech(average_value, total_value, num_buildings, controlled_tiles, turn, nations)
        self.check_existence(tiles_by_nation, controlled_tiles)

    # ------------------------------------------------------------------
    # Static factory methods
    # ------------------------------------------------------------------

    @staticmethod
    def gen_random_color() -> tuple[int, int, int]:
        """Generate a random nation colour.  Channels are capped at
        MAX_NATION_COLOR_VALUE so the colour doesn't clash with the white
        selection highlight.
        """
        cap = MAX_NATION_COLOR_VALUE
        c = (random.randint(0, cap), random.randint(0, cap), random.randint(0, cap))
        # Reroll until channels differ enough to avoid grayish/white-looking colours.
        while max(c) - min(c) < 80:
            c = (random.randint(0, cap), random.randint(0, cap), random.randint(0, cap))
        return c

    @staticmethod
    def gen_nation_name() -> str:
        names: list[str] = []
        try:
            with open(KINGDOM_NAMES_FILE, encoding="utf-8") as f:
                names = f.readlines()
        except FileNotFoundError:
            logger.error("Kingdom names file not found: %s", KINGDOM_NAMES_FILE)
            return "Unnamed"
        name = ""
        while len(name) < 4:
            name = random.choice(names).strip()
        return name[0].upper() + name[1:]

    @staticmethod
    def get_new_nation(nation_id: int) -> Nation:
        template = random.choice(SIMPLE_PERSONALITIES)
        # Each nation gets its own Personality copy so mutations don't affect others.
        personality = Personality(
            template.name,
            template.phase,
            template.influence_cost_to_dev,
            template.influence_cost_to_conquer,
        )
        return Nation(
            nation_id,
            Nation.gen_random_color(),
            Nation.gen_nation_name(),
            Character.get_random_character(),
            [],
            personality,
        )

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def get_nation_by_id(nations: list[Nation], nation_id: int) -> Nation | None:
        for n in nations:
            if n.id == nation_id:
                return n
        logger.warning("get_nation_by_id: no nation with id=%d", nation_id)
        return None

    def print_tiles(self, tile_list: list[Tile]) -> str:
        return " ".join(str(t.coords) for t in tile_list)

    def __repr__(self) -> str:
        return f"Nation({self.name!r}, id={self.id})"
