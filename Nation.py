from Resource import *
from Character import *
from Terrain import *
from include.nameGen import *
from Unit import *
from Settings import *
from Personality import *
import random

class Nation:
    def __init__(self, id, color, name, leader, modifiers, wars, personality):
        self.id = id
        self.color = color
        self.name = name
        self.leader = leader
        self.resources = {
            "food" : 0,
            "wood" : 0,
            "stone" : 0,
            "iron" : 0,
            "gold" : 0,
        }
        self.modifiers = modifiers
        self.wars = wars

        self.influence = 0
        self.techLevel = 1 # max 10
        self.money = 0 # available money for this nation

        self.units = [] # probably won't use this

        self.techs = [] # idk if I'll use this

        # will add more
        self.personality = personality
        self.tilesToDev = []
        self.turnsNoExpand = 0
        self.rotPercentage = BASE_ROT_PERCENTAGE - (self.techLevel * 2)

        self.size = 1

        self.representation = "Uncontrolled" if name == "" else f"{self.name}"

    # prints the coords of a list of given tiles controlled by a nation
    def printTiles(self, tiles):
        #values = "Tiles to Develop: "
        values = ""
        if tiles:
            for tile in tiles:
                values += f"{tile.coords} "
        return values

    # writes all tiles resources on a string and returns it
    def resourcesToString(self):
        values = "Production: "
        for r in self.resources:
            values += f"{r[0].upper()}:{self.resources[r]} "
        return values

    # returns the coords of all controlled tiles by this nation, given the tilesByNation found on Engine.py
    def getControlledTiles(self, tilesByNation):
        coords = []
        for coord in tilesByNation:
            if tilesByNation[coord] == self.id:
                coords.append(coord)
        return coords

    # returns all controlled tiles (not their coords) given a list of coords and a list of tiles 
    def getTilesByCoords(self, coords, tiles):
        ctrl = []
        for coord in coords:
            ctrl.append(tiles[coord[1]][coord[0]]) # first y, then x (but why? i dont remember why i made it like this)
        return ctrl

    # adds resources to a nation's available resources, given a dictionary of resources
    def addResources(self, rs):
        for r in rs:
            self.resources[r] += rs[r]
    
    # decreases a certain percentage of resources of this nation's stockpile, usually called each turn
    def rotResources(self, percentage):
        for r in self.resources:
            self.resources[r] = round(self.resources[r] * ((100-percentage) / 100))

    # TODO
    # returns tile
    def getValueBiggestValueAndTotalPopulation(self, controlledTiles):
        points = 0
        biggest = 0
        pop = 0
        for tile in controlledTiles:
            points += tile.value
            pop += tile.population
            if tile.value > biggest:
                biggest = tile.value
        points = round(points / len(controlledTiles), 2)
        return (points, biggest, pop)

    # returns a list of coords with the tiles to be developed for this nation
    # I want each AI to have different strategies and different devTiles
    # TODO I should put this function on a separate file inside data or something 
    # and let each personality import it's own getDevTiles() function
    def getDevTiles(self, tiles, tilesByNation, controlledTiles):
        devTiles = []
        if self.personality.name == "basic":
            # weird algorithm i made
            tries = 0
            while not devTiles and (tries < 10 or tries < len(controlledTiles) // 2):
                if len(controlledTiles) > 0:
                    randomTile = random.choice(controlledTiles) # first we choose a random controlled tile

                    # avoid expanding into these tiles
                    if randomTile.terrain.name in uncontrollableTerrains:
                        tries += 1
                        continue

                    # now according to the AI's personality, we make it a tile to develop or not
                    prob = random.randint(1,100)
                    if self.personality.phase == "aggressively-expanding":
                        if prob <= 3:
                            devTiles.append(randomTile)
                            break
                        else:
                            tries -= 0.1 # maybe it's too low?
                    # since it's "peacefully-expanding", it will just develop a random owned tile
                    # the more tiles it has, bigger the chance to develop a tile
                    elif self.personality.phase == "peacefully-expanding":
                        if prob <= 20:
                            devTiles.append(randomTile)
                            break
                    elif self.personality.phase == "developing":
                        if prob <= 80:
                            devTiles.append(randomTile)
                            break
                    
                    # then we pick it's neighbours
                    itsNeighbours = randomTile.getNeighbours(tiles, len(tiles[0]), len(tiles))
                    for n in itsNeighbours:
                        # it can only expand to uncontrolled tiles
                        if self.find(tilesByNation, n.coords) == 0 and self.personality.phase != "aggressively-expanding": # Uncontrolled
                            devTiles.append(n)
                        else:
                            devTiles.append(n)
                else:
                    print(f"\n{self.name} with id {self.id} has no tiles!!! Something went wrong! Controlled Tiles: {self.getControlledTiles(tilesByNation)}")
                    break

                tries += 1
        else:
            print(f"\nIf this nation's personality isn't basic, then what is it?! Name: {self.name}, id: {self.id}")
        return devTiles

    # given the tilesByNation found in Engine.py, checks if all the tiles to be developed are controlled by this nation.
    def checkTilesToDev(self, tilesByNation):
        for tile in self.tilesToDev:
            if self.isNationController(tile, tilesByNation):
                self.tilesToDev.remove(tile)

    # makes a turn for this AI, called each turn for each AI/nation
    def makeTurn(self, tiles, nations, tilesByNation):
        if self.id != 0:
            # basic variables
            controlledTiles = self.getTilesByCoords(self.getControlledTiles(tilesByNation), tiles) # list of tiles, NOT their coords
            maintencanceRaw, biggestVal, totalPopulation = self.getValueBiggestValueAndTotalPopulation(controlledTiles)
            self.influence += BASE_INFLUENCE_PER_TURN
            self.influence -= maintencanceRaw
            self.size = len(controlledTiles)

            # fill the tiles to develop
            self.tilesToDev = self.checkTilesToDev(tilesByNation) if self.tilesToDev else self.getDevTiles(tiles, tilesByNation, controlledTiles)

            # do things in our tilesToDev
            if self.tilesToDev:
                pass

            # controlledTiles = self.getTilesByCoords(self.getControlledTiles(tilesByNation), tiles) # list of tiles, NOT their coords
            # influenceUnrounded, biggestVal, totalPopulation = self.getValueBiggestValueAndTotalPopulation(controlledTiles)
            # self.influence = round(influenceUnrounded + self.influence, 1)

            # if self.size != len(controlledTiles):
            #     self.size = len(controlledTiles)
            #     self.turnsNoExpand = 0
            # else:
            #     self.turnsNoExpand += 1

            # self.tilesToDev = self.checkTilesToDev(tilesByNation) if self.tilesToDev else self.getDevTiles(tiles, tilesByNation, controlledTiles)
            
            # if self.tilesToDev:
            #     tries = (len(self.tilesToDev) // 2 ) + 1
            #     while(tries > 0):
            #         tries -= 1
            #         tile = random.choice(self.tilesToDev)
            #         # develop tile
            #         if self.isNationController(tile, tilesByNation):
            #             if tile.canDevelop(1):
            #                 tile.addDevelopment(1)
            #             else:
            #                 continue
            #         # conquer tile
            #         else:
            #             self.personality.influenceCostToConquer = biggestVal * (len(controlledTiles) // 2) * self.personality.conquerPhaseBonus
            #             if self.influence > self.personality.influenceCostToConquer:
            #                 self.changeTileOwnership(tile, tilesByNation)
            #                 self.influence -= self.personality.influenceCostToConquer
            #                 break
            
            # # Phase change
            # prob = random.randint(0,100)
            # if self.turnsNoExpand > 10:
            #     self.personality.phase = "peacefully-expanding"
            # if self.personality.phase != "aggressively-expanding":
            #     if prob < 5:
            #         self.personality.phase = "aggressively-expanding"

            # # Make units and buildings

            # do things in our tiles
            for tile in controlledTiles:
                if tile.population > 0:
                    tile.setProduction()
                    tile.develop()
                    self.addResources(tile.getLeftovers())

            # Some of the resources will "rot" every turn, so nations don't accumulate infinite resources
            self.rotResources(self.rotPercentage)

            # #print("Next nation\n")

    # I have to copy these functions to this class because I can't import Engine
    # There surely is a better way to do this
    def find(self, tilesByNation, tileCoords):
        return tilesByNation[tileCoords]

    def isNationController(self, tile, tilesByNation):
        if self.id == self.find(tilesByNation, tile.coords):
            return True
        return False

    def getController(self, tile, gameState):
        #tiles = gameState[0]
        #nations = gameState[1]
        tilesByNation = gameState[2]
        return self.find(tilesByNation, tile.coords)
    
    # conquers a tile for this nation by changing the tilesByNation found in Engine.py
    def changeTileOwnership(self, tile, tilesByNation):
        tilesByNation[tile.coords] = self.id

    # generates a random color, mostly used when creating new nations
    def genRandomColor():
        c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        while (c[0] == c[1] or c[0] == c[2] or c[1] == c[2]): # I don't want 3 equal colors
            c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return c

    # returns a new random nation
    def getNewNation(id):
        nationName = Nation.genNationName()
        leader = Character.getRandomCharacter()
        color = Nation.genRandomColor()
        modifiers = []
        wars = []
        persona = random.choice(SIMPLE_PERSONALITIES)
        n = Nation(id, color, nationName, leader, modifiers, wars, persona)
        return n

    def genNationName():
        names = []
        name = "ahh"
        with open("data/kingdomNames.txt", "r") as file:
            names = file.readlines()
        while len(name) < 4: # just to avoid empty lines
            name = random.choice(names)
        
        # to make the first char upperCase and remove a weird last char
        name = name[0].upper() + name[1:(-1)]
        #print(f"\nChosen Name:{name}\n")

        return name

# The "nation" that represents unclaimed land
emptyNation = Nation(0,BARBARIANS_COLOR2, "", Character("", "", 0, 0, 0), [], [], random.choice(SIMPLE_PERSONALITIES))
