from Settings import *
from Terrain import *
from Feature import *
from Building import *
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

        self.buildings = [] # will be empty for now until I implement buildings
        self.base_wealth = self.wealth
        self.base_liferating = self.liferating
        self.growth_rate = 0 #BASE_GROWTH_RATE + self.liferating * 0.001
        self.value = 0
        self.tax_revenue = 0
        self.food_to_grow = 0
        self.minimum_food = 0
        self.is_happy = True # not used, will work on this later

        # the available resources on a certain turn
        self.available_resources = {
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
    def get_leftovers(self):
        return self.available_resources

    # returns True if the tile has resources to sustain a new level of development
    def can_develop(self, amount):
        if self.production["wood"] > 2:
            return True
        return False

    # adds new levels of development to this tile
    def add_development(self, amount):
        self.modifiers["dev"] += amount
    
    # updates self.production with the correct values, it's usually used each turn
    def set_production(self):
        # adding the resource bonus
        self.wealth = self.base_wealth
        self.liferating = self.base_liferating
        self.production["food"] = BASE_FOOD
        self.production["wood"] = BASE_WOOD
        self.production["stone"] = BASE_STONE
        self.production["iron"] = BASE_IRON
        self.production["gold"] = BASE_GOLD

        for r in self.production:
            name = self.resource.name.lower()
            if name == r or (name[:4] == "food" and r == "food"):
                self.production[r] = (self.production[r] + self.resource.fixed_val) * (self.resource.bonus / 100)
                
                # adding the feature bonus
                for f in self.terrain.features:
                    if f.res_bonus != 0:
                        self.production[r] = self.production[r] * (f.res_bonus / 100)

            # adding the wealth bonus
            if self.production[r] != 0:
                self.production[r] += (1 * self.wealth)

            # adding development bonus
            if self.production[r] != 0:
                self.production[r] += (1 * self.modifiers["dev"])

            # subtracting revolt bonus
            if self.production[r] != 0:
                self.production[r] -= (2 * self.modifiers["rev"])
            
            self.update_values()
            
            self.production[r] = round(self.production[r])

        # feature fixed bonus
        self.add_features_bonus()

        # development maintenance
        self.production["wood"] -= (2 * self.modifiers["dev"])

    # some basic values and error checking
    def update_values(self):
        # checking if there were errors on tile creation
        if self.terrain.name in water_terrains:
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
    def compare_tile(self, tile):
        if self.id == tile.id:
            return True
        return False

    # returns this tile's neighbours, up, down, left and right
    def get_neighbours(self, tiles, max_x, max_y):

        n = []
        if (self.y+1 < max_y and self.x+1 < max_x):#
            n.append(tiles[self.y+1][self.x+1])

        if (self.x+1 < max_x):#
            n.append(tiles[self.y][self.x+1])

        if (self.y-1 >= 0 and self.x+1 < max_x):#
            n.append(tiles[self.y-1][self.x+1])

        if (self.y+1 < max_y):#
            n.append(tiles[self.y+1][self.x])

        if (self.y-1 >= 0):#
            n.append(tiles[self.y-1][self.x])

        if (self.y+1 < max_y and self.x-1 >= 0):#
            n.append(tiles[self.y+1][self.x-1])

        if (self.x-1 >= 0):#
            n.append(tiles[self.y][self.x-1])

        if (self.y-1 >= 0 and self.x-1 >= 0):#
            n.append(tiles[self.y-1][self.x-1])

        return n
        
        # My version for some reason goes around the map, for example
        # the neighbour of 99,0 in a map with 100 tiles gets 0,0 as it's neighbour...
        '''
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
        '''

    # adds each features bonus to self.production
    def add_features_bonus(self):
        for f in self.terrain.features:
            #state = "nice" if is_nice else "not nice"
            self.wealth += f.wel_bonus
            self.liferating += f.life_bonus
            self.production["food"] += f.food_bonus #if self.production["food"] != 0 else 0
            self.production["wood"] += f.wood_bonus #if self.production["wood"] != 0 else 0
            self.production["stone"] += f.stone_bonus #if self.production["stone"] != 0 else 0
            self.production["iron"] += f.iron_bonus #if self.production["iron"] != 0 else 0
            self.production["gold"] += f.gold_bonus #if self.production["gold"] != 0 else 0

    # returns a string that contains this tile's resources production
    def production_to_string(self):
        values = "Production: "
        for r in self.production:
            values += f"{r[0].upper()}:{self.production[r]} "
        return values
    
    # made most of these weird formulas a long time ago, don't ask me how I came up with them and how they work xD
    def develop(self):
        # first restock with produced supplies
        for r in self.available_resources:
            self.available_resources[r] = self.production[r]
        
        # then go to the market to buy if they have none/negative, but it will be implemented later (?)

        self.food_to_grow = math.ceil(self.population // 1000 * 10) // 10 # necessary food to grow the tile's population
        self.minimum_food = math.ceil(self.food_to_grow / 2) # minimum food for the tile to not lose population

        if self.available_resources["food"] >= self.food_to_grow:
            self.available_resources["food"] -= self.food_to_grow
            self.available_resources["food"] = round(self.available_resources["food"] * 10) // 10
            if self.available_resources["food"] < 0:
                self.available_resources["food"] = 0
            
            # Not yet implemented
            #if is_happy:
            self.growth_rate = BASE_GROWTH_RATE + self.liferating * 0.001
            #else:

        elif (self.available_resources["food"] >= self.minimum_food and self.available_resources["food"] < self.food_to_grow):
            # if the city doesn't have the necessary food to grow but it has more than the minimum food then it won't grow.
            self.available_resources["food"] -= self.minimum_food
            # TODO
            self.growth_rate = 0

        elif self.available_resources["food"] < self.minimum_food:
            # it will lose population if the city doesn't have enough food
            self.growth_rate = BASE_DECLINE_RATE
        
        self.growth_rate = round(self.growth_rate * 10000) / 10000 # what??
        self.population += round(self.population * self.growth_rate)

        # Update value
        # TODO
        self.value = round((round(math.log10(self.population) * 100) / 100) - 2, 2) # so it has 2 decimal places

        # Update tax_revenue
        # TODO
        #if is_happy:
        self.tax_revenue = round(self.population * TAX_BY_POP)

    # returns this tile's maintenance value, I'll probably change this later
    def get_maintenance(self):
        building_maint = [0,0] # [money_maintenance, influence_maintenance]
        maintenance = [0,0] # [money_maintenance, influence_maintenance]
        if self.population > 0:
            # let's say the maintenance equals to the value + development + buildings + revolt level on it. 
            # each building/development level doubles the "dev_maintenance" starting with a base value
            for building in self.buildings:
                building_maint[0] += building.get_maintenance()[0]
                building_maint[1] += building.get_maintenance()[1]

            dev_number = self.modifiers["dev"]
            dev_maintenance = BASE_DEV_MAINTENANCE + dev_number #  *100 so the number doesn't decrease if it's too low
            maintenance[1] = self.modifiers["rev"] + self.value + dev_maintenance + building_maint[1] # the revolt level, value, development maintenance and building maintenance
            maintenance[0] = building_maint[0]
        return maintenance # [money_maintenance, influence_maintenance]

    def get_num_buildings(self):
        return len(self.buildings)

    # returns this tile's influence bonus, which is added each turn to this tile's controller
    def get_influence(self):
        # for now it's just this tile's value
        return self.value

    # returns the tile's information on a list of strings, 
    # to be represented on the right panel of the game. Each element will be a new line
    def get_info(self, nation):
        info = []
        #info.append(f"{self.controller.representation}")
        info.append(f"{nation.id} | {nation.representation}")
        info.append(f"Name: {self.name}")
        info.append(f"Coords: {self.coords}")
        info.append(f"Terrain: {self.terrain.get_info()}")
        info.append(f"Population: {self.population}")
        info.append(f"Resource: {self.resource.name}")
        info.append(f"Wealth: {self.wealth}")
        info.append(f"Liferating: {self.liferating}")
        info.append(f"Features: {self.terrain.show_features()}")
        info.append(f"Modifiers: {self.modifiers}")
        #info.append(f"Growth Rate: {self.growth_rate}")
        info.append(f"Value: {self.value}")
        info.append(self.production_to_string())
        info.append(f"Tax Revenue: {self.tax_revenue}")
        info.append(f"Technology level: {nation.tech_level}")
        info.append(f"Actions left: {nation.actions}")
        info.append(f"{nation.leader.representation}")
        info.append(f"{nation.leader.get_values()}")
        return info

    def print_info(self, rep):
        for i in self.get_info(rep):
            print(i)
