"""Input handler — processes pygame events and translates them into game actions."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from civsim.engine.renderer import Renderer
from civsim.simulation.nation import TilesByNation
from civsim.ui.button import Button
from civsim.world.map import Map
from civsim.world.tile import Tile


@dataclass
class TileClickedAction:
    tile: Tile
    col: int
    row: int


@dataclass
class MapModeAction:
    mode: int


@dataclass
class VelocityToggleAction:
    pass


@dataclass
class VelocityChangeAction:
    pass


@dataclass
class PlaceNationAction:
    pass


@dataclass
class QuitAction:
    pass


GameAction = (
    TileClickedAction
    | MapModeAction
    | VelocityToggleAction
    | VelocityChangeAction
    | PlaceNationAction
    | QuitAction
)


class InputHandler:
    def __init__(
        self,
        renderer: Renderer,
        game_map: Map,
        tiles_by_nation: TilesByNation,
        tile_size: int,
        size_x: int,
        size_y: int,
        vel_button: Button,
        nation_button: Button,
        right_buttons: list[Button],
    ) -> None:
        self.renderer = renderer
        self.map = game_map
        self.tiles_by_nation = tiles_by_nation
        self.tile_size = tile_size
        self.size_x = size_x
        self.size_y = size_y
        self.vel_button = vel_button
        self.nation_button = nation_button
        self.right_buttons = right_buttons

    def process_events(self) -> list[GameAction]:
        actions: list[GameAction] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append(QuitAction())
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                actions.append(VelocityToggleAction())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                actions.extend(self._handle_mouse(pygame.mouse.get_pos()))
        return actions

    def _handle_mouse(self, pos: tuple[int, int]) -> list[GameAction]:
        actions: list[GameAction] = []
        col = pos[0] // self.tile_size
        row = pos[1] // self.tile_size

        if 0 <= col < self.size_x and 0 <= row < self.size_y:
            tile = self.map.find_tile((col, row))
            actions.append(TileClickedAction(tile=tile, col=col, row=row))

        if self.vel_button.is_over(pos):
            actions.append(VelocityChangeAction())

        if self.nation_button.is_over(pos):
            actions.append(PlaceNationAction())

        for button in self.right_buttons:
            if button.is_over(pos):
                actions.append(MapModeAction(mode=button.info))

        return actions

    def wait_for_tile_click(self) -> Tile:
        """Block until the user clicks on a valid map tile."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // self.tile_size
                    row = pos[1] // self.tile_size
                    if 0 <= col < self.size_x and 0 <= row < self.size_y:
                        return self.map.find_tile((col, row))
