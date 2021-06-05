class Feature:
    def __init__(self, name, rarity, resBonus, welBonus, lifeBonus, resBonus2, defBonus):
        self.name = name
        self.rarity = rarity
        self.resBonus = resBonus # in percentage
        self.welBonus = welBonus
        self.lifeBonus = lifeBonus
        self.foodBonus = resBonus2[0]
        self.woodBonus = resBonus2[1]
        self.stoneBonus = resBonus2[2]
        self.ironBonus = resBonus2[3]
        self.goldBonus = resBonus2[4]
        self.defBonus = defBonus

# 0 rarity means it won't be picked on world creation

river = Feature("river",           0, 10, 0, 1, [1,0,0,0,0], 1)
hills = Feature("hills",           0, 10, 0, 0, [1,0,0,0,0], 1)
forest = Feature("forest",         0, 10, 0, 0, [0,1,0,0,0], 0)
bigForest = Feature("big forest",  1, 1, 0, 0, [0,2,0,0,0], 1)

LAND_FEATURES = [
    Feature("small caves",         3, 1, 0, 0, [0,0,0,1,0], 0),
    Feature("big caves",           1, 10, 0, 0, [0,0,0,2,1], 0),
    Feature("gold-rich caves",     1, 1, 0, 0, [0,0,0,0,2], 0),
    Feature("valleys",             3, 1, 0, 1, [1,0,1,0,0], 0),
    Feature("cliffs",              3, 1, 0, 0, [0,0,1,0,0], 1),
    Feature("small lakes",         3, 10, 0, 1, [1,0,0,0,0], 0),
    Feature("mounds",              6, 1, 0, 0, [0,0,1,0,0], 0),
    Feature("canyon",              1, 1, 1, 0, [0,0,1,0,0], 1),
]

WATER_FEATURES = [
    Feature("coral reef",          3, 1, 0, 0, [1,0,0,0,0], 0),
    Feature("deep trench",         3, 1, 0, 0, [1,0,0,0,0], 0),
]
