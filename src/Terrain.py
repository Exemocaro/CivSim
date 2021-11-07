from Feature import *

class Terrain:
    def __init__(self, name, color, features, height):
        self.name = name
        self.color = color
        self.features = features
        self.height = height
        self.defenseValue = self.getDefenseValue()
        if name == "Mountain":
            self.defenseValue += 1

    def getDefenseValue(self):
        value = 0
        for feature in self.features:
            value += feature.defBonus
        return value

    def showFeatures(self):
        value = ""
        for feature in self.features:
            if feature == self.features[-1]:
                value += f"{feature.name}"
            else:
                value += f"{feature.name}; "
        return value

    def getInfo(self):
        #hill = ""
        #forest = ""
        #if self.hills:
        #    hill = "(H)"
        #if self.forest:
        #    forest = "(F)"
        return (f"{self.name}")  #{hill}{forest}")

#the colors to be used in pygame to represent each terrain
nameColorPairs = { # in rgb
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

nameLiferatingPairs = {
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

specialTerrains = ["Coast", "Desert", "Ocean", "Tundra", "Mountain", "Highland", "Ice"]

waterTerrains = ["Coast", "Ocean", "Ice"]

noResourceTerrains = ["Mountain", "Ocean", "Ice"]

uncontrollableTerrains = ["Mountain", "Ocean", "Ice"]

noBeginningTerrains = ["Mountain", "Ocean", "Coast", "Ice"]

def getNormalTerrains():
    terrains = []
    for tile in nameColorPairs:
        if tile not in specialTerrains:
            terrains.append(tile)
    return terrains

def getAllTerrains():
    terrains = []
    for tile in nameColorPairs:
        terrains.append(tile)
    return terrains