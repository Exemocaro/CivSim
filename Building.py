from Settings import *

class Building:
    def __init__(self, name, level, moneyCost, influenceCost, moneyMaintenance, influenceMaintenance, resBonus, defBonus):
        self.name = name
        self.level = level
        self.moneyCost = moneyCost
        self.influenceCost = influenceCost
        self.moneyMaintenance = moneyMaintenance
        self.influenceMaintenance = influenceMaintenance

        # TODO
        # resBonus increases the bonus on a fixed val
        # I probably won't use this, but it will stay here for now
        self.foodBonus = resBonus[0]
        self.woodBonus = resBonus[1]
        self.stoneBonus = resBonus[2]
        self.ironBonus = resBonus[3]
        self.goldBonus = resBonus[4]
        self.defBonus = defBonus

    # returns both the money maintenance and influence maintenance
    def getMaintenance(self):
        return (self.moneyMaintenance, self.influenceMaintenance)

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
