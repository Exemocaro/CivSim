# Population growth value
BASE_GROWTH_RATE = 0.001
BASE_DECLINE_RATE = -0.01

# Resources lost each turn
BASE_ROT_PERCENTAGE = 50

# minimum amount of influence each state gets each turn
BASE_INFLUENCE_PER_TURN = 5

# starting value for a development level/building on a tile
BASE_DEV_MAINTENANCE = 0.2 # don't put it lower than 0.1, or it will cause problems

# Tax of each pop
TAX_BY_POP = 0.01

# the speed of each turn
GAME_SPEED = 5 #faster than 5 and it just doesn't increase more

# Resource Values
BASE_FOOD = 1
BASE_WOOD = 1
BASE_STONE = 0
BASE_IRON = 0
BASE_GOLD = 0

# Population range at the start of a game
MIN_POP = 1000
MAX_POP = 5000

# Wealth range at the start of a game (1 to 5)
MIN_WEALTH = 1
MAX_WEALTH = 3

# Liferating range at the start of a game (1 to 30)
# Don't think I'll use this tho
MIN_LIFERATING = 1
MAX_LIFERATING = 10

# To be used with the Perlin Noise generator, don't mess with this
# unless you know what you are doing
NOISE_SCALE = 0.02

# some colors
BLACK = (0,0,0)
BACKGROUND_COLOR = (120,120,120)
BUTTON_COLOR = (150,150,150)
BARBARIANS_COLOR = (174, 214, 241)
BARBARIANS_COLOR2 = (52, 73, 94)
RIVER_COLOR = (30, 144, 255)

# the font used in the UI
MAIN_FONT = ("fonts/LEMONMILK-Regular.otf", 20)
SMALL_FONT = ("fonts/LEMONMILK-Regular.otf", 20)

# X, Y, tileSize and number of rivers
MAP_SIZES = {
    "huge" : (240, 150, 6, 110),
    "large" : (180, 110, 8, 90),
    "medium" : (140, 90, 10, 70),
    "small" : (100, 60, 14, 50)
}
