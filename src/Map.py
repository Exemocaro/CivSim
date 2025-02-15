from Tile import *
from Resource import *
from Terrain import *
from Settings import *
from Nation import *
from Character import *
from Feature import *

from perlin_noise import PerlinNoise

import random

# perlin noise things, don't mess with this if you don't know what you are doing.
noise1 = PerlinNoise(octaves=3)
noise2 = PerlinNoise(octaves=6)
noise3 = PerlinNoise(octaves=12)
noise4 = PerlinNoise(octaves=24)

class Map:
    def __init__(self, size_x, size_y, river_num):
        self.size_x = size_x
        self.size_y = size_y
        self.river_num = river_num # max number of rivers in the map
        self.tiles = [[0 for i in range(self.size_x)] for j in range(self.size_y)]

        # super ugly code, gotta make this more readable
        self.top1 = size_y - (size_y * 12 // 100)
        self.top2 = size_y - (size_y * 9 // 100)
        self.top3 = size_y - (size_y * 6 // 100)
        self.top4 = size_y - (size_y * 3 // 100)
        self.bot1 = (size_y * 12 // 100)
        self.bot2 = (size_y * 9 // 100)
        self.bot3 = (size_y * 6 // 100)
        self.bot4 = (size_y * 3 // 100)

    # chooses the resource for a tile given its terrain
    def weight_chooser(self, list, rarities):     
        weights = []
        sum = 0
        for r in rarities:
            weights.append(r)

        for weight in weights:
            sum += weight
        
        selection = random.randint(1, sum)
        count = 0
        for i in range(len(weights)):
            count += weights[i]
            if selection < count:
                return list[i]

        return self.weight_chooser(list, rarities)

    # chooses the resource for a tile given its terrain
    def choose_resource(self, terrain):
        name = terrain.name
        resources = LAND_RESOURCES

        if name in no_resource_terrains:
            return no_resource
        if name in water_terrains:
            r = random.randint(0,5) # 1 in 6
            if r == 0:
                resources = WATER_RESOURCES
            else:
                return no_resource
        
        rarities = []
        for r in resources:
            rarities.append(r.rarity)
        return self.weight_chooser(resources, rarities)
    
    # chooses terrain for a specific tile using perlin noise
    def choose_terrain(self, x, y):
        name = "Ocean"
        features = []

        has_hills = 0
        has_forest = 0
        has_big_forest = 0

        noise_val1 =         noise1([x*NOISE_SCALE, y*NOISE_SCALE])
        noise_val1 += 0.5  * noise2([x*NOISE_SCALE, y*NOISE_SCALE])
        noise_val1 += 0.25 * noise3([x*NOISE_SCALE, y*NOISE_SCALE])
        noise_val1 += 0.125* noise4([x*NOISE_SCALE, y*NOISE_SCALE])
        
        if noise_val1 > 0.5:
            name = "Mountain"
            has_hills = 1
            has_forest = 0
        elif noise_val1 > 0.3:
            name = random.choice(get_normal_terrains())
            hills_prob = random.randint(0,2)
            if hills_prob == 0:
                has_hills = 1
            forest_prob = random.randint(0,5)
            if forest_prob == 0:
                has_forest = 1
        elif noise_val1 > 0: 
            name = random.choice(get_normal_terrains())
            hills_prob = random.randint(0,5)
            if hills_prob == 0:
                has_hills = 1
            forest_prob = random.randint(0,1)
            if forest_prob == 0:
                has_forest = 1
            else:
                forest_prob = random.randint(0,9)
                if forest_prob == 0:
                    has_big_forest = 1
        elif noise_val1 > -0.12:
            name = "Coast"

        # special cases
        # again, ugly code, I'll eventually make this better and more readable
        if noise_val1 > 0.25:
            r = random.randint(0,6)
            if r <= 2:
                name = "Highland"
        elif noise_val1 > 0.15:
            r = random.randint(0,5)
            if r == 0:
                name = "Highland"

        if y >= self.size_y - 1 or y <= 1:
            if noise_val1 < 0:
                name = "Ice"
            else:
                name = "Tundra"
        elif y >= self.size_y - 2 or y <= 2:
            r = random.randint(0,4)
            if r <= 3:
                if noise_val1 < 0:
                    name = "Ice"
                else:
                    name = "Tundra"
        elif y > self.top4 or y < self.bot4:
            r = random.randint(0,6)
            if r <= 3:
                if noise_val1 < 0:
                    name = "Ice"
                else:
                    name = "Tundra"
        elif y > self.top3 or y < self.bot3:
            r = random.randint(0,6)
            if r <= 2:
                if noise_val1 < 0:
                    name = "Ice"
                else:
                    name = "Tundra"
        elif y > self.top2 or y < self.bot2:
            r = random.randint(0,8)
            if r <= 2:
                if noise_val1 < 0:
                    name = "Ice"
                else:
                    name = "Tundra"
        elif y > self.top1 or y < self.bot1:
            r = random.randint(0,10)
            if r <= 1:
                if noise_val1 < 0:
                    name = "Ice"
                else:
                    name = "Tundra"
        elif y > self.top1 - 1 or y < self.bot1 + 1:
            r = random.randint(0,15)
            if r <= 1:
                if noise_val1 < 0:
                    name = "Ice"
                else:
                    name = "Tundra"
        
        color = name_color_pairs[name]
        
        # Choosing other features:
        if has_hills:
            features.append(hills)
        if has_big_forest:
            has_forest = 0
            features.append(bigForest)
        if has_forest:
            features.append(forest)
        
        if len(features) < 2:
            prob = random.randint(1,6)
            if prob == 1:
                rarities = []
                if name not in water_terrains and name != "Mountain":
                    for f in LAND_FEATURES:
                        rarities.append(f.rarity)
                    features.append(self.weight_chooser(LAND_FEATURES, rarities))
                elif name == "Coast":
                    for f in WATER_FEATURES:
                        rarities.append(f.rarity)
                    features.append(self.weight_chooser(WATER_FEATURES, rarities))

        return Terrain(name, color, features, noise_val1)

    # chooses wealth for a tile given its terrain
    def choose_wealth(self, terrain, res):
        if terrain.name in water_terrains and res.name == "":
            return 0
        elif terrain.name == "Mountain": # inhabitable
            return 0
        else:
            w = random.randint(MIN_WEALTH, MAX_WEALTH)
        return w

    # chooses liferating for a tile given its terrain
    def choose_liferating(self, terrain):
        min = name_liferating_pairs[terrain.name][0]
        max = name_liferating_pairs[terrain.name][1]
        lf = random.randint(min, max)
        return lf

    # chooses the population for a tile given its terrain
    def choose_population(self, terrain):
        if terrain.name in water_terrains:
            return 0
        elif terrain.name == "Mountain": # inhabitable
            return 0
        else:
            p = random.randint(MIN_POP, MAX_POP)
        return p

    # generates the tiles
    def gen_tiles(self):
        i = 0
        #print(f"size_y:{self.size_y} size_x:{self.size_x}")
        for y in range(self.size_y):
            for x in range(self.size_x):
                name = f"Number {i}"
                ldr = Character.get_random_character() # leader
                terrain = self.choose_terrain(x, y)
                pop = self.choose_population(terrain)
                res =  self.choose_resource(terrain)
                wlth = self.choose_wealth(terrain, res)
                lifer = self.choose_liferating(terrain)
                mods = {"dev":0, "rev":0}
                #print(f"y:{y} x:{x}")
                self.tiles[y][x] = (Tile(i, name, x, y, ldr, terrain, pop, res, wlth, lifer, mods))
                i += 1

        # to clear random values on creation
        for y in range(self.size_y):
            for x in range(self.size_x):
                self.tiles[y][x].update_values()

    # generates the rivers for this map
    # TODO, some rivers are too close to each other, I want to spread them out more
    def gen_rivers(self):
        print("Generating rivers...")

        river_num= self.river_num # number of rivers
        river_height = 0.80 # starting height to search on tiles to make the first rivers, keeps decreasing
        n = 1
        while river_num> 0:
            row = random.choice(self.tiles) # chooses a random row of the map
            tile = random.choice(row) # chooses a random tile from the row
            if tile.terrain.height >= river_height and river not in tile.terrain.features:
                river_num-= 1
                # while the river hasn't reach the sea
                while(tile.terrain.height > 0):
                    n = 1

                    # append the river on this tile
                    if river not in tile.terrain.features:
                        tile.terrain.features.append(river)

                    # searches in the tile's neighbours for the one with the smallest height and the seond smallest height 
                    neighbours = tile.get_neighbours(self.tiles, self.size_x, self.size_y)
                    smallest = neighbours[0]
                    second_smallest = neighbours[1]
                    for neighbour in neighbours:
                        if neighbour.terrain.height < smallest.terrain.height:
                            second_smallest = smallest
                            smallest = neighbour
                    
                    # to avoid infinite loops
                    if river in smallest.terrain.features and n == 1:
                        smallest = second_smallest
                        n += 1
                    if river in smallest.terrain.features and n == 2:
                        smallest = random.choice(neighbours)
                        n = 0
                        while n < len(neighbours):
                            if river in smallest.terrain.features:
                                smallest = neighbours[n]
                            else:
                                break
                            n += 1
                        n = 1
                    # if the above didn't work then make another river
                    # just to avoid an infinite loop
                    if river in smallest.terrain.features:
                        break

                    tile = smallest
            else:
                river_height -= 0.0005
                #print(f"Height: {round(river_height, 2)}, Rivers Generated: {self.river_num - nR}")
                if river_height < 0.05:
                    river_num= 0
                    break

    # creates map, will add more things here later
    def create_map(self):
        print("Generating tiles...")
        self.gen_tiles()
        self.gen_rivers()
    
    # prints tiles with coords on console, for testing purposes
    """ def printMapCoords(self):
        lastY = self.tiles[0].y
        for tile in self.tiles:
            if lastY != tile.y:
                print()
            print(f" {tile.coords} ", end = "")
            lastY = tile.y """
    
    # prints tiles with resources on console, for testing purposes
    """ def printMapResources(self):
        lastY = self.tiles[0].y
        for tile in self.tiles:
            if lastY != tile.y:
                print()
            print(f" {tile.resource.name} ", end = "")
            lastY = tile.y """
    
    # returns a tile on given coords
    def find_tile(self, coords):
        return self.tiles[coords[1]][coords[0]]
