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

# some simple builings
MONEY_BUILDINGS = [
    Building("marketplace", 1, 0, 1, -BASE_MONEY_BUILDING_BONUS, BASE_BUILDING_MAINTENANCE_INFLUENCE, [0,0,0,0,0], 0),
    #Building("marketplace", 2, 50, 0, BASE_BUILDING_MAINTENANCE_INFLUENCE, [0,0,0,0,0], 0),
]

INFLUENCE_BUILDINGS = [
    Building("academy", 1, 50, 0, BASE_BUILDING_MAINTENANCE_MONEY, -BASE_INFLUENCE_BUILDING_BONUS, [0,0,0,0,0], 0), # basically a school
]
