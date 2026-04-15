"""Simple pygame button widget."""

from __future__ import annotations

import pygame

from civsim.settings import MAIN_FONT


class Button:
    def __init__(
        self,
        color: tuple[int, int, int],
        x: float,
        y: float,
        width: float,
        height: float,
        text: str = "",
        info: int = 0,
    ) -> None:
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.info = info  # arbitrary data tag (e.g. map-mode index)

    def draw(self, surface: pygame.Surface, outline: tuple[int, int, int] | None = None) -> None:
        if outline:
            pygame.draw.rect(
                surface, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4)
            )
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        if self.text:
            font = pygame.font.Font(MAIN_FONT[0], MAIN_FONT[1])
            rendered = font.render(self.text, True, (0, 0, 0))
            surface.blit(
                rendered,
                (
                    self.x + (self.width / 2 - rendered.get_width() / 2),
                    self.y + (self.height / 2 - rendered.get_height() / 2),
                ),
            )

    def is_over(self, pos: tuple[int, int]) -> bool:
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height
