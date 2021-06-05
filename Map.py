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
    def __init__(self, sizeX, sizeY, riverNum):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.riverNum = riverNum # max number of rivers in the map
        self.tiles = [[0 for i in range(self.sizeX)] for j in range(self.sizeY)]

        # super ugly code, gotta make this more readable
        self.top1 = sizeY - (sizeY * 12 // 100)
        self.top2 = sizeY - (sizeY * 9 // 100)
        self.top3 = sizeY - (sizeY * 6 // 100)
        self.top4 = sizeY - (sizeY * 3 // 100)
        self.bot1 = (sizeY * 12 // 100)
        self.bot2 = (sizeY * 9 // 100)
        self.bot3 = (sizeY * 6 // 100)
        self.bot4 = (sizeY * 3 // 100)

    # chooses the resource for a tile given its terrain
    def weightChooser(self, list, rarities):     
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

        return self.weightChooser(list, rarities)

    # chooses the resource for a tile given its terrain
    def chooseResource(self, terrain):
        name = terrain.name
        resources = LAND_RESOURCES

        if name in noResourceTerrains:
            return noResource
        if name in waterTerrains:
            r = random.randint(0,5) # 1 in 6
            if r == 0:
                resources = WATER_RESOURCES
            else:
                return noResource
        
        rarities = []
        for r in resources:
            rarities.append(r.rarity)
        return self.weightChooser(resources, rarities)
    
    # chooses terrain for a specific tile using perlin noise
    def chooseTerrain(self, x, y):
        name = "Ocean"
        features = []

        hasHills = 0
        hasForest = 0
        hasBigForest = 0

        noise_val1 =         noise1([x*NOISE_SCALE, y*NOISE_SCALE])
        noise_val1 += 0.5  * noise2([x*NOISE_SCALE, y*NOISE_SCALE])
        noise_val1 += 0.25 * noise3([x*NOISE_SCALE, y*NOISE_SCALE])
        noise_val1 += 0.125* noise4([x*NOISE_SCALE, y*NOISE_SCALE])
        
        if noise_val1 > 0.5:
            name = "Mountain"
            hasHills = 1
            hasForest = 0
        elif noise_val1 > 0.3:
            name = random.choice(getNormalTerrains())
            hillsProb = random.randint(0,2)
            if hillsProb == 0:
                hasHills = 1
            forestProb = random.randint(0,5)
            if forestProb == 0:
                hasForest = 1
        elif noise_val1 > 0: 
            name = random.choice(getNormalTerrains())
            hillsProb = random.randint(0,5)
            if hillsProb == 0:
                hasHills = 1
            forestProb = random.randint(0,1)
            if forestProb == 0:
                hasForest = 1
            else:
                forestProb = random.randint(0,9)
                if forestProb == 0:
                    hasBigForest = 1
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

        if y >= self.sizeY - 1 or y <= 1:
            if noise_val1 < 0:
                name = "Ice"
            else:
                name = "Tundra"
        elif y >= self.sizeY - 2 or y <= 2:
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
        
        color = nameColorPairs[name]
        
        # Choosing other features:
        if hasHills:
            features.append(hills)
        if hasBigForest:
            hasForest = 0
            features.append(bigForest)
        if hasForest:
            features.append(forest)
        
        if len(features) < 2:
            prob = random.randint(1,6)
            if prob == 1:
                rarities = []
                if name not in waterTerrains and name != "Mountain":
                    for f in LAND_FEATURES:
                        rarities.append(f.rarity)
                    features.append(self.weightChooser(LAND_FEATURES, rarities))
                elif name == "Coast":
                    for f in WATER_FEATURES:
                        rarities.append(f.rarity)
                    features.append(self.weightChooser(WATER_FEATURES, rarities))

        return Terrain(name, color, features, noise_val1)

    # chooses wealth for a tile given its terrain
    def chooseWealth(self, terrain, res):
        if terrain.name in waterTerrains and res.name == "":
            return 0
        elif terrain.name == "Mountain": # inhabitable
            return 0
        else:
            w = random.randint(MIN_WEALTH, MAX_WEALTH)
        return w

    # chooses liferating for a tile given its terrain
    def chooseLiferating(self, terrain):
        min = nameLiferatingPairs[terrain.name][0]
        max = nameLiferatingPairs[terrain.name][1]
        lf = random.randint(min, max)
        return lf

    # chooses the population for a tile given its terrain
    def choosePopulation(self, terrain):
        if terrain.name in waterTerrains:
            return 0
        elif terrain.name == "Mountain": # inhabitable
            return 0
        else:
            p = random.randint(MIN_POP, MAX_POP)
        return p

    # generates the tiles
    def genTiles(self):
        i = 0
        #print(f"sizeY:{self.sizeY} sizeX:{self.sizeX}")
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                name = f"Number {i}"
                #ctrl = Nation(0,NON_CONTROLLED_TILE_COLOR , "", "", {}, [], []) # controller
                ldr = Character.getRandomCharacter() # leader
                terrain = self.chooseTerrain(x, y)
                pop = self.choosePopulation(terrain)
                res =  self.chooseResource(terrain)
                wlth = self.chooseWealth(terrain, res)
                lifer = self.chooseLiferating(terrain)
                mods = {"dev":0, "rev":0}
                #print(f"y:{y} x:{x}")
                self.tiles[y][x] = (Tile(i, name, x, y, ldr, terrain, pop, res, wlth, lifer, mods))
                i += 1

        # to clear random values on creation
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                self.tiles[y][x].updateValues()

    # river creation
    def genRivers(self):
        print("Generating rivers...")

        nR = self.riverNum
        riverHeight = 0.80
        n = 1
        while nR > 0:
            row = random.choice(self.tiles)
            tile = random.choice(row)
            if tile.terrain.height >= riverHeight and river not in tile.terrain.features:
                nR -= 1
                # then create the river
                while(tile.terrain.height > 0):
                    n = 1

                    if river not in tile.terrain.features:
                        tile.terrain.features.append(river)
                    for y in range(self.sizeY):
                        for x in range(self.sizeX):
                            if self.tiles[y][x].compareTile(tile):
                                self.tiles[y][x] = tile
                                tile = self.tiles[y][x]

                    neighbours = tile.getNeighbours(self.tiles, self.sizeX, self.sizeY)
                    smallest = neighbours[0]
                    secondSmallest = neighbours[1]
                    for neighbour in neighbours:
                        if neighbour.terrain.height < smallest.terrain.height:
                            secondSmallest = smallest
                            smallest = neighbour
                    
                    # to avoid infinite loops
                    if river in smallest.terrain.features and n == 1:
                        smallest = secondSmallest
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

                    for y in range(self.sizeY):
                        for x in range(self.sizeX):
                            if self.tiles[y][x].compareTile(smallest):
                                self.tiles[y][x] = tile
                                tile = smallest
            else:
                riverHeight -= 0.0005
                #print(f"Height: {round(riverHeight, 2)}, Rivers Generated: {self.riverNum - nR}")
                if riverHeight < 0.05:
                    nR = 0
                    break

    # creates map, will add more things here later
    def createMap(self):
        print("Generating tiles...")
        self.genTiles()
        self.genRivers()
    
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
    def findTile(self, coords):
        return self.tiles[coords[1]][coords[0]]
