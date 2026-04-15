"""Renderer — all pygame drawing code, isolated from game logic."""

from __future__ import annotations

import pygame

from civsim.settings import (
    BACKGROUND_COLOR,
    BLACK,
    CAPITAL_COLOR,
    MAIN_FONT,
    SMALL_FONT,
)
from civsim.simulation.nation import Nation, TilesByNation
from civsim.world.feature import HILLS, RIVER
from civsim.world.map import Map

# Map mode constants
MODE_POLITICAL = 1
MODE_TERRAIN = 2
MODE_POPULATION = 3
MODE_RIVERS = 4
MODE_DEVELOPMENT = 5


class Renderer:
    def __init__(
        self,
        screen: pygame.Surface,
        game_map: Map,
        nations: list[Nation],
        tiles_by_nation: TilesByNation,
        tile_size: int,
        width: int,
        height: int,
        ui_space_x: int,
        ui_space_y: int,
    ) -> None:
        self.screen = screen
        self.map = game_map
        self.nations = nations
        self.tiles_by_nation = tiles_by_nation
        self.tile_size = tile_size
        self.width = width
        self.height = height
        self.ui_space_x = ui_space_x
        self.ui_space_y = ui_space_y

        self.font = pygame.font.Font(MAIN_FONT[0], MAIN_FONT[1])
        self.small_font = pygame.font.Font(SMALL_FONT[0], SMALL_FONT[1])

        self.political_alpha = 180
        self.selected_nation_id: int = -1

        # Right-panel text layout
        self.text_x = width + 14
        self.text_top_margin = 14

        self.texts: list[str] = ["Welcome to CivSim!"] + [""] * 19

        self._draw_modes = {
            MODE_POLITICAL: self.draw_map_political,
            MODE_TERRAIN: self.draw_map_terrain,
            MODE_POPULATION: self.draw_map_population,
            MODE_RIVERS: self.draw_map_rivers,
            MODE_DEVELOPMENT: self.draw_map_development,
        }

    # ------------------------------------------------------------------
    # Color blending
    # ------------------------------------------------------------------

    @staticmethod
    def blend_colors(
        color_alpha: tuple[int, int, int, int],
        base_color: tuple[int, int, int],
    ) -> tuple[int, int, int]:
        a = color_alpha[3] / 255
        r = color_alpha[0] / 255 * a + base_color[0] / 255 * (1 - a)
        g = color_alpha[1] / 255 * a + base_color[1] / 255 * (1 - a)
        b = color_alpha[2] / 255 * a + base_color[2] / 255 * (1 - a)
        return (round(r * 255), round(g * 255), round(b * 255))

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _draw_hills(self, x: int, y: int) -> None:
        ts = self.tile_size
        fst = [x * ts + 1, y * ts + ts - 1]
        snd = [x * ts + ts - 1, y * ts + ts - 1]
        trd = [x * ts + ts // 2, y * ts - 1]
        pygame.draw.polygon(self.screen, BLACK, [fst, snd, trd], 1)

    # ------------------------------------------------------------------
    # Map draw modes
    # ------------------------------------------------------------------

    def draw_map_terrain(self) -> None:
        ts = self.tile_size
        for y, row in enumerate(self.map.tiles):
            for x, tile in enumerate(row):
                pygame.draw.rect(self.screen, tile.terrain.color, (x * ts, y * ts, ts, ts))
                if HILLS in tile.terrain.features:
                    self._draw_hills(x, y)

    def draw_map_rivers(self) -> None:
        ts = self.tile_size
        for y, row in enumerate(self.map.tiles):
            for x, tile in enumerate(row):
                pygame.draw.rect(self.screen, tile.terrain.color, (x * ts, y * ts, ts, ts))
                if RIVER in tile.terrain.features:
                    from civsim.settings import RIVER_COLOR

                    pygame.draw.rect(self.screen, RIVER_COLOR, (x * ts, y * ts, ts, ts))
                if HILLS in tile.terrain.features:
                    self._draw_hills(x, y)

    def draw_map_political(self) -> None:
        ts = self.tile_size
        for y, row in enumerate(self.map.tiles):
            for x, tile in enumerate(row):
                terrain_color = tile.terrain.color
                nation = self.nations[self.tiles_by_nation[tile.coords]]
                nc = (255, 255, 255) if self.selected_nation_id == nation.id else nation.color

                if nation.id != 0:
                    color = self.blend_colors(
                        (nc[0], nc[1], nc[2], self.political_alpha), terrain_color
                    )
                else:
                    color = terrain_color

                pygame.draw.rect(self.screen, color, (x * ts, y * ts, ts, ts))

                if HILLS in tile.terrain.features:
                    self._draw_hills(x, y)

                # Capital marker
                if nation.capital is tile:
                    cx = x * ts + ts // 2
                    cy = y * ts + ts // 2
                    pygame.draw.circle(self.screen, CAPITAL_COLOR, (cx, cy), ts // 2 - 1)

    def draw_map_population(self) -> None:
        ts = self.tile_size
        biggest = max(
            (tile.population for row in self.map.tiles for tile in row),
            default=1,
        )
        if biggest == 0:
            biggest = 1
        for y, row in enumerate(self.map.tiles):
            for x, tile in enumerate(row):
                if tile.population > 0:
                    green = 5 + 250 * tile.population // biggest
                    color = (0, min(255, green), 0)
                else:
                    color = tile.terrain.color
                pygame.draw.rect(self.screen, color, (x * ts, y * ts, ts, ts))

    def draw_map_development(self) -> None:
        """Heat-map showing tile development levels (green = high, grey = 0)."""
        ts = self.tile_size
        max_dev = max(
            (tile.modifiers.get("dev", 0) for row in self.map.tiles for tile in row),
            default=1,
        )
        if max_dev == 0:
            max_dev = 1
        for y, row in enumerate(self.map.tiles):
            for x, tile in enumerate(row):
                dev = tile.modifiers.get("dev", 0)
                if dev > 0:
                    intensity = int(50 + 200 * dev / max_dev)
                    color = (0, intensity, 0)
                else:
                    color = (80, 80, 80)
                pygame.draw.rect(self.screen, color, (x * ts, y * ts, ts, ts))

    def draw_map(self, mode: int) -> None:
        self._draw_modes.get(mode, self.draw_map_political)()

    # ------------------------------------------------------------------
    # UI text
    # ------------------------------------------------------------------

    def update_texts(self, text_array: list[str]) -> None:
        for i, text in enumerate(text_array):
            if i < len(self.texts):
                self.texts[i] = text
        for i in range(len(text_array), len(self.texts)):
            self.texts[i] = ""

    def show_text(self, font: pygame.font.Font, text: str, x: float, y: float) -> None:
        rendered = font.render(text, True, BLACK)
        self.screen.blit(rendered, (x, y))

    def show_texts(self) -> None:
        y = self.text_top_margin
        for i, text in enumerate(self.texts):
            if not text:
                y += self.small_font.get_linesize() // 2
                continue
            font = self.font if i == 0 else self.small_font
            rendered = font.render(text, True, BLACK)
            self.screen.blit(rendered, (self.text_x, y))
            y += font.get_linesize() + 2

    # ------------------------------------------------------------------
    # Frame
    # ------------------------------------------------------------------

    def draw_frame(self, turn: int) -> None:
        """Draw the background, UI borders, and turn counter."""
        self.screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(self.screen, BLACK, [self.width, 0, self.ui_space_x, self.height], 5)
        pygame.draw.rect(self.screen, BLACK, [0, self.height, self.width, self.ui_space_y], 5)
        pygame.draw.rect(
            self.screen, BLACK, [self.width, self.height, self.ui_space_x, self.ui_space_y], 5
        )
        self.show_text(self.small_font, f"Turn {turn}", self.width - 150, self.height + 7)
