"""Package entry point — ``uv run civsim`` or ``python -m civsim``."""

from __future__ import annotations

import logging

from civsim.engine.game_loop import GameLoop
from civsim.settings import DEBUG, MAP_SIZES
from civsim.world.map import Map


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format="%(levelname)s [%(name)s] %(message)s",
    )

    map_size_key = "small"  # change to "medium", "large", or "huge" as needed
    size_cfg = MAP_SIZES[map_size_key]
    size_x, size_y, tile_size, river_num = size_cfg

    game_map = Map(size_x, size_y, river_num)
    game_map.create_map()

    loop = GameLoop(game_map, num_players=30, map_size_key=map_size_key)
    loop.run()


if __name__ == "__main__":
    main()
