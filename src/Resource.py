class Resource:
    def __init__(self, name, rarity, bonus, fixed_val):
        self.name = name
        self.rarity = rarity
        self.bonus = bonus # works as a percentage of total output
        self.fixed_val = fixed_val # works as a fixed value produced by the province

# To add more and more mechanics
# Rarities are probabilities and must sum to 100
LAND_RESOURCES = [
    Resource("Iron", 10, 1, 1),
    Resource("Wood", 15, 20, 1),
    Resource("Stone", 10, 1, 2),
    Resource("Gold", 5, 1, 1),
    Resource("Food", 60, 20, 1),
]

WATER_RESOURCES = [
    Resource("Food(Fish)", 90, 1, 2),
    Resource("Food(Wales)", 10, 1, 5),
]

no_resource = Resource("", 0, 0, 0)
