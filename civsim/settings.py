"""Central configuration for CivSim.

All tunable constants live here.  Import this module with:
    from civsim.settings import *
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — always resolved relative to this file so the game can be launched
# from any working directory.
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).parent.parent
FONTS_DIR = _ROOT / "fonts"
DATA_DIR = _ROOT / "data"

MAIN_FONT = (str(FONTS_DIR / "LEMONMILK-Regular.otf"), 20)
SMALL_FONT = (str(FONTS_DIR / "LEMONMILK-Regular.otf"), 14)
KINGDOM_NAMES_FILE = str(DATA_DIR / "kingdom_names.txt")
LOG_FILE = str(_ROOT / "logs" / "civsim.log")

# ---------------------------------------------------------------------------
# Debug / logging
# ---------------------------------------------------------------------------
DEBUG = False  # set True for verbose console output

# ---------------------------------------------------------------------------
# Population growth
# ---------------------------------------------------------------------------
BASE_GROWTH_RATE = 0.001
BASE_DECLINE_RATE = -0.01

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------
BASE_ROT_PERCENTAGE = 55  # base % of resources lost per turn
PROSPERITY_ROT_FACTOR = 0.5  # each prosperity point reduces rot by this much

BASE_FOOD = 1
BASE_WOOD = 1
BASE_STONE = 0
BASE_IRON = 0
BASE_GOLD = 0

# ---------------------------------------------------------------------------
# Influence
# ---------------------------------------------------------------------------
BASE_INFLUENCE_PER_TURN = 5
BASE_DEV_MAINTENANCE = 0.2  # starting maintenance per development level (must be > 0.01)
BASE_DEV_COST = 1  # influence cost to develop a tile
BASE_CONQUER_COST = 1.5  # influence cost to conquer a tile
BASE_BUILDING_MAINTENANCE_INFLUENCE = 0.4
BASE_INFLUENCE_BUILDING_BONUS = 1
BASE_BUILDING_INFLUENCE_COST = 2
SAFE_INFLUENCE_TO_DEV = 50  # multiplier: only dev when influence > cost * this

# ---------------------------------------------------------------------------
# Money
# ---------------------------------------------------------------------------
BASE_BUILDING_MAINTENANCE_MONEY = 60
BASE_MONEY_BUILDING_BONUS = 50
BASE_BUILDING_MONEY_COST = 50
TAX_BY_POP = 0.001
PROSPERITY_MONEY_BONUS = 0.5  # each prosperity point adds this to money per turn

# ---------------------------------------------------------------------------
# War
# ---------------------------------------------------------------------------
WAR_COST = 50
WAR_MAINTENANCE_RANGE = (15, WAR_COST)
WAR_INFLUENCE_MAINTENANCE_COST = 1
WAR_MONEY_REWARD = 150
WAR_INFLUENCE_REWARD = 1500
MAX_BATTLE_RNG = 8
CONQUER_ACCURACY = 3  # candidates sampled per attack; higher = cleaner borders
TERRAIN_DEFENSE_WEIGHT = 2  # multiplier applied to tile defense_value in battle

# ---------------------------------------------------------------------------
# Technology
# ---------------------------------------------------------------------------
MAX_TECH_LEVEL = 10
# Index = tech level (0–10); value = multiplier applied to various bonuses
TECH_BONUS = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.3, 2.6, 3.0, 3.5, 4.0]
COUNTRY_DEV_STABILIZER = 1

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
MIN_ACTIONS = 5
ACTIONS_STEP = 1
ACTIONS_STEP_VALUE = 20  # tiles needed to earn one extra action

# ---------------------------------------------------------------------------
# Wars (concurrent)
# ---------------------------------------------------------------------------
MIN_WARS = 2
WARS_STEP = 1
WARS_STEP_VALUE = 200
PROBABILITY_ENDING_WAR = 2  # out of 100 per turn
PROBABILITY_ENDING_WAR_MAX = 15  # used when nation is over war limit
PROBABILITY_WAR_PER_TURN = 8  # out of 100

# ---------------------------------------------------------------------------
# Personality / expansion
# ---------------------------------------------------------------------------
TURNS_TO_EXPAND = 10
PROBABILITY_AGGRESSIVE_EXPANSION = 5  # out of 100
PROBABILITY_AGGR_EXP_DEV_TILE = 3
PROBABILITY_PEACE_EXP_DEV_TILE = 20
PROBABILITY_DEVELOPING_DEV_TILE = 80
MAX_DEV_TRIES = 10

# ---------------------------------------------------------------------------
# Expansion scoring weights
# Score = w_value*value - w_distance*dist - w_defense*defense + enclave_bonus + isolation_bonus
# ---------------------------------------------------------------------------
SCORE_W_VALUE = 2.0  # reward for tile value (population-based)
SCORE_W_DISTANCE = 0.3  # penalty for distance from capital
SCORE_W_DEFENSE = 1.0  # penalty for terrain/building defense
SCORE_W_ENCLAVE = 8.0  # bonus for tiles nearly/fully surrounded by friendly territory
SCORE_W_ISOLATION = 3.0  # bonus for isolated enemy tiles with few same-nation neighbours

# ---------------------------------------------------------------------------
# Characters / leaders
# ---------------------------------------------------------------------------
BASE_DEATH_VALUE = 2  # base death chance per year (out of 1000)
VITALITY_DEATH_PENALTY = 1  # extra chance when vitality is low
VITALITY_DEATH_BONUS = 1  # chance reduction when vitality is high
# (age_threshold, death_probability_out_of_1000) — must be in descending age order
AGE_PROBABILITIES_PAR = [
    (95, 500),
    (90, 250),
    (85, 120),
    (80, 80),
    (75, 50),
    (70, 25),
    (65, 10),
    (60, 5),
    (55, 4),
    (50, 3),
    (45, 2),
    (40, 1),
]
LEADER_DEATH_INFLUENCE_PENALTY = 50
LEADER_DEATH_MONEY_PENALTY = 100

# ---------------------------------------------------------------------------
# Happiness / revolt
# ---------------------------------------------------------------------------
REVOLT_THRESHOLD = 5  # revolt level at which tile is considered unhappy
REVOLT_INCREMENT = 0.1  # revolt grows by this each turn when unhappy
REVOLT_DECAY = 0.05  # revolt shrinks by this each turn when happy
UNHAPPY_PRODUCTION_PENALTY = 0.7  # multiplier on all production when unhappy

# ---------------------------------------------------------------------------
# Buildings
# ---------------------------------------------------------------------------
MAX_BUILDINGS_PER_TILE = 15
BUILDINGS_PER_ACTION = 2

# ---------------------------------------------------------------------------
# Improvements
# ---------------------------------------------------------------------------
MAX_IMPROVEMENTS_PER_TILE = 3
IMPROVEMENT_ROAD_CONQUER_DISCOUNT = 0.8  # conquer cost multiplier for road-adjacent tiles

# ---------------------------------------------------------------------------
# Map generation
# ---------------------------------------------------------------------------
MIN_POP = 1000
MAX_POP = 5000
MIN_WEALTH = 1
MAX_WEALTH = 3
MIN_LIFERATING = 1
MAX_LIFERATING = 10
NOISE_SCALE = 0.02
RIVER_MIN_DISTANCE_DIVISOR = 8  # rivers must be at least map_size // this apart
NATION_SPAWN_BORDER_MARGIN = 4  # tiles from map edge where nations can't spawn

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (120, 120, 120)
BUTTON_COLOR = (150, 150, 150)
BARBARIANS_COLOR = (174, 214, 241)
BARBARIANS_COLOR2 = (52, 73, 94)
RIVER_COLOR = (30, 144, 255)
SELECTED_NATION_COLOR = (255, 255, 255)
CAPITAL_COLOR = (255, 255, 0)
MAX_NATION_COLOR_VALUE = 230  # cap on RGB channels for nation colours (avoids pure white)

# ---------------------------------------------------------------------------
# Speed
# ---------------------------------------------------------------------------
GAME_SPEED = 5  # turns per second at velocity 1; max effective is 5

# ---------------------------------------------------------------------------
# Map size presets  (width_tiles, height_tiles, tile_px, num_rivers)
# ---------------------------------------------------------------------------
MAP_SIZES: dict[str, tuple[int, int, int, int]] = {
    "huge": (240, 150, 6, 110),
    "large": (180, 110, 8, 90),
    "medium": (140, 90, 10, 70),  # don't exceed medium for good performance
    "small": (100, 60, 14, 50),  # recommended for best performance
    # "test": (50, 30, 20, 30),
}
