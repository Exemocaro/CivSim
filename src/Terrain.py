from Feature import *

class Terrain:
    def __init__(self, name, color, features, height):
        self.name = name
        self.color = color
        self.features = features
        self.height = height
        self.defense_value = self.get_defense_value()
        if name == "Mountain":
            self.defense_value += 1

    def get_defense_value(self):
        value = 0
        for feature in self.features:
            value += feature.def_bonus
        return value

    def show_features(self):
        value = ""
        for feature in self.features:
            if feature == self.features[-1]:
                value += f"{feature.name}"
            else:
                value += f"{feature.name}; "
        return value

    def get_info(self):
        #hill = ""
        #forest = ""
        #if self.hills:
        #    hill = "(H)"
        #if self.forest:
        #    forest = "(F)"
        return (f"{self.name}")  #{hill}{forest}")

#the colors to be used in pygame to represent each terrain
name_color_pairs = { # in rgb
    "Plains" : (50, 205, 50),
    "Grassland" : (144, 238, 144),
    # special cases
    "Mountain" : (230, 230, 250),
    "Desert" : (255, 255, 0),
    "Ocean" : (0, 0, 128),
    "Coast" : (0, 0, 255),
    "Ice" : (255, 255, 255),
    "Tundra" : (255, 160, 122),
    "Highland" : (210, 180, 140),
}

name_liferating_pairs = {
    "Plains" : (5,9),
    "Grassland" : (5,9),
    # special cases
    "Mountain" : (0,0),
    "Desert" : (0,0),
    "Ocean" : (0,0),
    "Coast" : (0,0),
    "Ice" : (0,0),
    "Tundra" : (1,4),
    "Highland" : (4,8),
}

special_terrains = ["Coast", "Desert", "Ocean", "Tundra", "Mountain", "Highland", "Ice"]

water_terrains = ["Coast", "Ocean", "Ice"]

no_resource_terrains = ["Mountain", "Ocean", "Ice"]

uncontrollable_terrains = ["Mountain", "Ocean", "Ice"]

no_beginning_terrains = ["Mountain", "Ocean", "Coast", "Ice"]

def get_normal_terrains():
    terrains = []
    for tile in name_color_pairs:
        if tile not in special_terrains:
            terrains.append(tile)
    return terrains

def get_all_terrains():
    terrains = []
    for tile in name_color_pairs:
        terrains.append(tile)
    return terrains