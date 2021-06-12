# Population growth value
BASE_GROWTH_RATE = 0.001
BASE_DECLINE_RATE = -0.01

# Resources lost each turn
BASE_ROT_PERCENTAGE = 50

# minimum amount of influence each state gets each turn
BASE_INFLUENCE_PER_TURN = 5

# related with influence expenditure
BASE_DEV_MAINTENANCE = 0.2 # starting value for a development level, must be above 0.01
BASE_DEV_COST = 1 # cost to develop a tile in influence
BASE_CONQUER_COST = 1.5
BASE_BUILDING_MAINTENANCE_INFLUENCE = 0.2 # maintenance cost of a building that produces money
BASE_INFLUENCE_BUILDING_BONUS = 0.6 # the bonus a building gives when it produces influence
BASE_BUILDING_INFLUENCE_COST = 1

# related with money expenditure
BASE_BUILDING_MAINTENANCE_MONEY = 60 # maintenance cost of a building that produces influence
BASE_MONEY_BUILDING_BONUS = 50 # the bonus a building gives when it produces money
BASE_BUILDING_MONEY_COST = 50

# tech realted variables
NUM_BUILDINGS_TO_INCREASE_TECH = 5 # each 5 buildings in a nation's territory will increase it's tech level

# Tax of each pop
TAX_BY_POP = 0.001

# max number of actions each nation can make in a turn (includes building, developing and conquering tiles)
MAX_ACTIONS = 7
MEDIUM_ACTIONS = 5
MIN_ACTIONS = 3 # don't mess with this value
SIZE_MAX_ACTIONS = 40 # number of tiles a nation needs to have to reach max number of actions
SIZE_MEDIUM_ACTIONS = 20 # self-explanatory

# max number of buildings a tile can have
MAX_BUILDINGS_PER_TILE = 3

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
