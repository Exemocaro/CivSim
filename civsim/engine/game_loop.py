"""Game loop — turn management and the main run() method."""

from __future__ import annotations

import logging
import random

import pygame

from civsim.characters.character import Character
from civsim.engine.input_handler import (
    InputHandler,
    MapModeAction,
    PlaceNationAction,
    QuitAction,
    TileClickedAction,
    VelocityChangeAction,
    VelocityToggleAction,
)
from civsim.engine.renderer import (
    MODE_DEVELOPMENT,
    MODE_POLITICAL,
    MODE_POPULATION,
    MODE_RIVERS,
    MODE_TERRAIN,
    Renderer,
)
from civsim.settings import (
    BARBARIANS_COLOR2,
    BLACK,
    BUTTON_COLOR,
    GAME_SPEED,
    MAP_SIZES,
    NATION_SPAWN_BORDER_MARGIN,
)
from civsim.simulation.nation import Nation, TilesByNation
from civsim.simulation.personality import Personality
from civsim.ui.button import Button
from civsim.ui.timer import Timer
from civsim.world.map import Map
from civsim.world.terrain import NO_BEGINNING_TERRAINS
from civsim.world.tile import Tile

logger = logging.getLogger(__name__)

# The neutral "empty" nation that represents unclaimed land.  Created once at
# module level and prepended to the nations list at game start.
EMPTY_NATION = Nation(
    0,
    BARBARIANS_COLOR2,
    "",
    Character("", 0, "m", 0, 0, 0),
    [],
    Personality("basic", "peacefully-expanding", 1.0, 1.5),
)


class GameLoop:
    def __init__(self, game_map: Map, num_players: int, map_size_key: str = "small") -> None:
        self.map = game_map
        self.num_players = num_players
        size_cfg = MAP_SIZES[map_size_key]
        self.width = size_cfg[0] * size_cfg[2]
        self.height = size_cfg[1] * size_cfg[2]
        self.tile_size = size_cfg[2]

        self.ui_space_x = 450
        self.ui_space_y = 40
        self.button_size = 50

        self.nations: list[Nation] = []
        self.tiles_by_nation: TilesByNation = {}

        self.turn = 0
        self.velocity = 0
        self.last_vel = 1
        self.current_map_mode = MODE_POLITICAL

        self.selected_tile: Tile | None = None

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.width + self.ui_space_x, self.height + self.ui_space_y)
        )
        pygame.display.set_caption("CivSim")

        self.timer = Timer()
        self.clock = pygame.time.Clock()

        self._setup_ui()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _get_right_button_x(self, n: int) -> float:
        return self.width + (6 * (n + 1)) + (self.button_size * n)

    def _setup_ui(self) -> None:
        bs = self.button_size
        h = self.height
        uis_y = self.ui_space_y

        self.vel_button = Button(BUTTON_COLOR, 6, h + 6, bs, uis_y - 12, "||")
        self.nation_button = Button(BUTTON_COLOR, 12 + bs, h + 6, bs, uis_y - 12, "NAT")
        self.right_buttons = [
            Button(
                BUTTON_COLOR,
                self._get_right_button_x(0),
                h + 6,
                bs,
                uis_y - 12,
                "POL",
                MODE_POLITICAL,
            ),
            Button(
                BUTTON_COLOR,
                self._get_right_button_x(1),
                h + 6,
                bs,
                uis_y - 12,
                "TERR",
                MODE_TERRAIN,
            ),
            Button(
                BUTTON_COLOR,
                self._get_right_button_x(2),
                h + 6,
                bs,
                uis_y - 12,
                "POP",
                MODE_POPULATION,
            ),
            Button(
                BUTTON_COLOR, self._get_right_button_x(3), h + 6, bs, uis_y - 12, "RIV", MODE_RIVERS
            ),
            Button(
                BUTTON_COLOR,
                self._get_right_button_x(4),
                h + 6,
                bs,
                uis_y - 12,
                "DEV",
                MODE_DEVELOPMENT,
            ),
        ]

        self.renderer = Renderer(
            self.screen,
            self.map,
            self.nations,
            self.tiles_by_nation,
            self.tile_size,
            self.width,
            self.height,
            self.ui_space_x,
            self.ui_space_y,
        )
        self.input_handler = InputHandler(
            self.renderer,
            self.map,
            self.tiles_by_nation,
            self.tile_size,
            self.map.size_x,
            self.map.size_y,
            self.vel_button,
            self.nation_button,
            self.right_buttons,
        )

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_tiles_by_nation(self) -> None:
        for row in self.map.tiles:
            for tile in row:
                tile.set_production()
                self.tiles_by_nation[tile.coords] = 0  # neutral

    def _spawn_nations(self) -> None:
        logger.info("Spawning %d nations...", self.num_players)
        margin = NATION_SPAWN_BORDER_MARGIN
        for _i in range(self.num_players):
            # Find a valid starting tile
            nation_id = len(self.nations)
            attempts = 0
            while True:
                row_idx = random.randint(margin, self.map.size_y - margin - 1)
                col_idx = random.randint(margin, self.map.size_x - margin - 1)
                tile = self.map.tiles[row_idx][col_idx]
                if (
                    tile.terrain.name not in NO_BEGINNING_TERRAINS
                    and self.tiles_by_nation.get(tile.coords, 0) == 0
                ):
                    break
                attempts += 1
                if attempts > 1000:
                    logger.warning(
                        "Could not find valid spawn tile for nation %d after 1000 attempts",
                        nation_id,
                    )
                    break

            nation = Nation.get_new_nation(nation_id)
            nation.change_tile_ownership(tile, self.tiles_by_nation)
            nation.set_capital(tile)
            self.nations.append(nation)
            logger.debug("Spawned nation %r at %s", nation.name, tile.coords)

        logger.info("Generation complete. %d nations spawned.", len(self.nations) - 1)

    # ------------------------------------------------------------------
    # Velocity helpers
    # ------------------------------------------------------------------

    def _set_velocity(self, new_vel: int) -> None:
        self.velocity = new_vel
        self.vel_button.text = ">" * new_vel if new_vel > 0 else "||"

    def _cycle_velocity(self) -> None:
        self._set_velocity(0 if self.velocity == 4 else self.velocity + 1)

    def _toggle_pause(self) -> None:
        if self.velocity != 0:
            self.last_vel = self.velocity
            self._set_velocity(0)
        else:
            self._set_velocity(self.last_vel)

    # ------------------------------------------------------------------
    # Action handling
    # ------------------------------------------------------------------

    def _handle_tile_clicked(self, action: TileClickedAction) -> None:
        self.selected_tile = action.tile
        controller = self._get_controller(action.tile)
        self.renderer.selected_nation_id = controller.id
        self.renderer.update_texts(action.tile.get_info(controller))

        logger.debug(
            "Tile clicked (%d,%d) | Controller: %d %s | Phase: %s | Wars: %s",
            action.col,
            action.row,
            controller.id,
            controller.representation,
            controller.personality.phase,
            [(w[0].name, w[1]) for w in controller.wars],
        )

    def _get_controller(self, tile: Tile) -> Nation:
        nation_id = self.tiles_by_nation.get(tile.coords, 0)
        if nation_id < len(self.nations):
            return self.nations[nation_id]
        # Fallback linear search
        for n in self.nations:
            if n.id == nation_id:
                return n
        return EMPTY_NATION

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        # Initialise tile ownership and production
        self.nations.append(EMPTY_NATION)
        self._init_tiles_by_nation()
        self._spawn_nations()

        running = True
        while running:
            actions = self.input_handler.process_events()

            for action in actions:
                if isinstance(action, QuitAction):
                    running = False
                elif isinstance(action, VelocityToggleAction):
                    self._toggle_pause()
                elif isinstance(action, VelocityChangeAction):
                    self._cycle_velocity()
                elif isinstance(action, TileClickedAction):
                    self._handle_tile_clicked(action)
                elif isinstance(action, MapModeAction):
                    self.current_map_mode = action.mode
                elif isinstance(action, PlaceNationAction):
                    self._place_new_nation()

            # Game logic
            if self.velocity != 0 and self.timer.get_time_passed() >= 1 / (
                GAME_SPEED * self.velocity
            ):
                self.turn += 1
                if self.selected_tile:
                    self.renderer.update_texts(
                        self.selected_tile.get_info(self._get_controller(self.selected_tile))
                    )

                logger.debug("---- Turn %d ----", self.turn)
                for nation in self.nations:
                    if nation.id != 0:
                        nation.make_turn(
                            self.map.tiles, self.nations, self.tiles_by_nation, self.turn
                        )

                self.timer.restart()

            # Render
            self.renderer.draw_frame(self.turn)
            self.renderer.draw_map(self.current_map_mode)

            self.vel_button.draw(self.screen, BLACK)
            self.nation_button.draw(self.screen, BLACK)
            for btn in self.right_buttons:
                btn.draw(self.screen, BLACK)

            self.renderer.show_texts()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    # ------------------------------------------------------------------
    # Place nation interactively
    # ------------------------------------------------------------------

    def _place_new_nation(self) -> None:
        nation_id = len(self.nations)
        nation = Nation.get_new_nation(nation_id)

        last_vel = self.velocity
        self._set_velocity(0)

        self.renderer.draw_frame(self.turn)
        self.renderer.draw_map(self.current_map_mode)
        self.renderer.update_texts(["", "", "Click on a tile", "to place a new nation."])
        self.renderer.show_texts()
        pygame.display.flip()

        tile = self.input_handler.wait_for_tile_click()
        nation.change_tile_ownership(tile, self.tiles_by_nation)
        nation.set_capital(tile)
        self.nations.append(nation)

        self.renderer.update_texts(["", "", "Done!", f"{nation.name} was born!"])
        self._set_velocity(last_vel)
        logger.info("Placed new nation %r (id=%d) at %s", nation.name, nation.id, tile.coords)
