from Settings import *
from Terrain import *
from Feature import *
import math
#from Resource import *

class Tile:
    def __init__(self, id, name, x, y, leader, terrain, population, resource, wealth, liferating, modifiers):
        self.id = id
        self.name = name # Must have a limit, let's set it to 20 characters
        self.x = x
        self.y = y
        self.leader = leader
        self.terrain = terrain
        self.population = population
        self.resource = resource
        self.wealth = wealth
        self.liferating = liferating
        self.modifiers = modifiers
        self.coords = (self.x, self.y)

        self.baseWealth = self.wealth
        self.baseLiferating = self.liferating
        self.growthRate = 0 #BASE_GROWTH_RATE + self.liferating * 0.001
        self.value = 0
        self.taxRevenue = 0
        self.foodToGrow = 0
        self.minimumFood = 0
        self.isHappy = True # not used, will work on this later

        # the available resources on a certain turn
        self.availableResources = {
            "food" : 0,
            "wood" : 0,
            "stone" : 0,
            "iron" : 0,
            "gold" : 0,
        }

        # resources produced each turn
        self.production = {
            "food" : 0,
            "wood" : 0,
            "stone" : 0,
            "iron" : 0,
            "gold" : 0,
        }

    # returns all available resources
    def getLeftovers(self):
        return self.availableResources

    # returns True if the tile has resources to sustain a new level of development
    def canDevelop(self, amount):
        if self.production["wood"] > 2:
            return True
        return False

    # adds new levels of development to this tile
    def addDevelopment(self, amount):
        self.modifiers["dev"] += amount
    
    # updates self.production with the correct values, it's usually used each turn
    def setProduction(self):
        # adding the resource bonus
        self.wealth = self.baseWealth
        self.liferating = self.baseLiferating
        self.production["food"] = BASE_FOOD
        self.production["wood"] = BASE_WOOD

        for r in self.production:
            name = self.resource.name.lower()
            if name == r or (name[:4] == "food" and r == "food"):
                self.production[r] = (self.production[r] + self.resource.fixedVal) * (self.resource.bonus / 100)
                
                # adding the feature bonus
                for f in self.terrain.features:
                    if f.resBonus != 0:
                        self.production[r] = self.production[r] * (f.resBonus / 100)

            # adding the wealth bonus
            if self.production[r] != 0:
                self.production[r] += (1 * self.wealth)

            # adding development bonus
            if self.production[r] != 0:
                self.production[r] += (1 * self.modifiers["dev"])

            # subtracting revolt bonus
            if self.production[r] != 0:
                self.production[r] -= (2 * self.modifiers["rev"])
            
            self.updateValues()
            
            self.production[r] = round(self.production[r])

        # feature fixed bonus
        self.addFeaturesBonus()

        # maintenance
        self.production["wood"] -= (2 * self.modifiers["dev"])

    # some basic values and error checking
    def updateValues(self):
        # checking if there were errors on tile creation
        if self.terrain.name in waterTerrains:
            self.liferating = 0
            self.production["wood"] = 0
            if self.terrain.features == []:
                self.wealth = 0
                for r in self.production:
                    self.production[r] = 0
        if self.terrain.name == "Mountain": # inhabitable
            self.liferating = 0
            self.population = 0
            self.wealth = 0
            for r in self.production:
                self.production[r] = 0
    
    # comapres this tile with another one, returns True if they are the same
    def compareTile(self, tile):
        if self.id == tile.id:
            return True
        return False

    # returns this tile's neighbours, up, down, left and right
    def getNeighbours(self, tiles, maxX, maxY):
        n = []
        try:
            n.append(tiles[self.y+1][self.x])
        except IndexError:
            pass

        try:
            n.append(tiles[self.y-1][self.x])
        except IndexError:
            pass

        try:
            n.append(tiles[self.y][self.x-1])
        except IndexError:
            pass

        try:
            n.append(tiles[self.y][self.x+1])
        except IndexError:
            pass

        return n

    # adds each features bonus to self.production
    def addFeaturesBonus(self):
        for f in self.terrain.features:
            #state = "nice" if is_nice else "not nice"
            self.wealth += f.welBonus
            self.liferating += f.lifeBonus
            self.production["food"] += f.foodBonus #if self.production["food"] != 0 else 0
            self.production["wood"] += f.woodBonus #if self.production["wood"] != 0 else 0
            self.production["stone"] += f.stoneBonus #if self.production["stone"] != 0 else 0
            self.production["iron"] += f.ironBonus #if self.production["iron"] != 0 else 0
            self.production["gold"] += f.goldBonus #if self.production["gold"] != 0 else 0

    # returns a string that contains this tile's resources production
    def productionToString(self):
        values = "Production: "
        for r in self.production:
            values += f"{r[0].upper()}:{self.production[r]} "
        return values
    
    # made most of these weird formulas a long time ago, don't ask me how I came up with them and how they work xD
    def develop(self):
        # first restock with produced supplies
        for r in self.availableResources:
            self.availableResources[r] = self.production[r]
        
        # then go to the market to buy if they have none/negative, but it will be implemented later (?)

        self.foodToGrow = math.ceil(self.population // 1000 * 10) // 10 # necessary food to grow the tile's population
        self.minimumFood = math.ceil(self.foodToGrow / 2) # minimum food for the tile to not lose population

        if self.availableResources["food"] >= self.foodToGrow:
            self.availableResources["food"] -= self.foodToGrow
            self.availableResources["food"] = round(self.availableResources["food"] * 10) // 10
            if self.availableResources["food"] < 0:
                self.availableResources["food"] = 0
            
            # Not yet implemented
            #if isHappy:
            self.growthRate = BASE_GROWTH_RATE + self.liferating * 0.001
            #else:

        elif (self.availableResources["food"] >= self.minimumFood and self.availableResources["food"] < self.foodToGrow):
            # if the city doesn't have the necessary food to grow but it has more than the minimum food then it won't grow.
            self.availableResources["food"] -= self.minimumFood
            # TODO
            self.growthRate = 0

        elif self.availableResources["food"] < self.minimumFood:
            # it will lose population if the city doesn't have enough food
            self.growthRate = BASE_DECLINE_RATE
        
        self.growthRate = round(self.growthRate * 10000) / 10000 # what??
        self.population += round(self.population * self.growthRate)

        # Update value
        # TODO
        self.value = round((round(math.log10(self.population) * 100) / 100) - 2, 2) # so it has 2 decimal places

        # Update taxRevenue
        # TODO
        #if isHappy:
        self.taxRevenue = round(self.population * TAX_BY_POP)

    # returns the tile's information on a list of strings, 
    # to be represented on the right panel of the game. Each element will be a new line
    def getInfo(self, nation):
        info = []
        #info.append(f"{self.controller.representation}")
        info.append(f"{nation.representation}")
        info.append(f"Name: {self.name}")
        info.append(f"Coords: {self.coords}")
        info.append(f"Terrain: {self.terrain.getInfo()}")
        info.append(f"Population: {self.population}")
        info.append(f"Resource: {self.resource.name}")
        info.append(f"Wealth: {self.wealth}")
        info.append(f"Liferating: {self.liferating}")
        info.append(f"Features: {self.terrain.showFeatures()}")
        info.append(f"Modifiers: {self.modifiers}")
        #info.append(f"Growth Rate: {self.growthRate}")
        info.append(f"Value: {self.value}")
        info.append(self.productionToString())
        info.append(f"Tax Revenue: {self.taxRevenue}")
        info.append(f"FoodToGrow: {self.foodToGrow}")
        info.append(f"MinimumFood: {self.minimumFood}")
        info.append(f"{nation.leader.representation}")
        info.append(f"{nation.leader.getValues()}")
        return info

    def printInfo(self, rep):
        for i in self.getInfo(rep):
            print(i)
