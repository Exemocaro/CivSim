from Settings import *

class Building:
    def __init__(self, name, level, money_cost, influence_cost, money_maintenance, influence_maintenance, res_bonus, def_bonus):
        self.name = name
        self.level = level
        self.money_cost = money_cost
        self.influence_cost = influence_cost
        self.money_maintenance = money_maintenance
        self.influence_maintenance = influence_maintenance

        # TODO
        # res_bonus increases the bonus on a fixed val
        # I probably won't use this, but it will stay here for now
        self.food_bonus = res_bonus[0]
        self.wood_bonus = res_bonus[1]
        self.stone_bonus = res_bonus[2]
        self.iron_bonus = res_bonus[3]
        self.gold_bonus = res_bonus[4]
        self.def_bonus = def_bonus

    # returns both the money maintenance and influence maintenance
    def get_maintenance(self):
        return (self.money_maintenance, self.influence_maintenance)

# buildings will be distributed in levels, lvl1 buildings will cost the base amount, lvl 2 twice that amount, and so on
# I made it like this to avoid looping through all the buildings to find an affordable one
# buildings that produce money and cost influence
L1_MONEY_BUILDINGS = [
    Building("marketplace", 1, 0, BASE_BUILDING_INFLUENCE_COST, -BASE_MONEY_BUILDING_BONUS, BASE_BUILDING_MAINTENANCE_INFLUENCE, [0,0,0,0,0], 0),
]

# buildings that produce influence and cost money
L1_INFLUENCE_BUILDINGS = [
    Building("academy", 1, BASE_BUILDING_MONEY_COST, 0, BASE_BUILDING_MAINTENANCE_MONEY, -BASE_INFLUENCE_BUILDING_BONUS, [0,0,0,0,0], 0), # basically a school
]
