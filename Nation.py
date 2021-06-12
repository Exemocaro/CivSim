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

        self.lastInfluence = 0 # to track if the ifluence is growing or not
        self.influence = 0
        self.techLevel = 1 # max 11
        self.money = 0 # available money for this nation

        #self.units = [] # probably won't use this

        self.techs = [] # idk if I'll use this

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

    # returns total maintenance, the total value, the average value, the biggest population and the average population in our controlled tiles
    # this was made like this to avoid looping several times, this way we loop only one and get all the data we need
    def getData(self, controlledTiles):
        techBonus = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.3, 2.6, 3.0, 3.5, 4.0] # should it be on Settings.py?
        totalInfluence = 0
        maintenance = 0
        average = 0
        totalValue = 0
        biggest = 0
        pop = 0
        for tile in controlledTiles:
            totalInfluence += tile.getInfluence()
            maintenance += tile.getMaintenance()
            totalValue += tile.value
            pop += tile.population
            if tile.value > biggest:
                biggest = tile.value
        average = 0 if len(controlledTiles) == 0 else round(totalValue / len(controlledTiles), 2)
        totalInfluence *= techBonus[self.techLevel - 1] # the higher the tech, the better the bonus on influence gain
        return (totalInfluence, maintenance, totalValue, average, biggest, pop)
    
    # returns our leader's influence bonus, will be added each turn to our nation
    def getLeaderInfluenceBonus(self):
        return self.leader.prosperity

    # develops all our inhabitated tiles and updates our resources
    def developTiles(self, controlledTiles):
        for tile in controlledTiles:
            if tile.population > 0: # develop only inhabitated tiles
                # these 3 are necessary, don't remove them
                tile.setProduction()
                tile.develop()
                self.addResources(tile.getLeftovers())
    
    # see if we can change our personality's phase and other stats
    def updatePersonality(self):
        prob = random.randint(0,100)
        if self.turnsNoExpand > 10:
            self.personality.phase = "peacefully-expanding"
        if self.personality.phase != "aggressively-expanding":
            if prob < 5:
                self.personality.phase = "aggressively-expanding"

        self.personality.updateInfluenceToConquer()
        self.personality.updateInfluenceToDev()

    # updates our size and the number of turns without changing our size
    def updateSize(self, controlledTiles):
        if self.size != len(controlledTiles):
            self.size = len(controlledTiles)
            self.turnsNoExpand = 0
        else:
            self.turnsNoExpand += 1

    # udpates the current amount of money this nation has
    def updateMoney(self, totalPopulation):
        self.money += round(totalPopulation * TAX_BY_POP, 3)

    # conquers a tile for this nation; consumes influence
    def conquerTile(self, tile, tilesByNation):
        self.changeTileOwnership(tile, tilesByNation)
        self.influence -= self.personality.influenceCostToConquer

    # adds development to the specified tile; consumes influence
    def addDevToTile(self, devValue, tile):
        tile.addDevelopment(devValue)
        self.influence -= self.personality.influenceCostToDev

    # TODO
    # will develop one of our tilesToDev at the cost of influence
    def devTiles(self, controlledTiles, tilesByNation, isInfluenceGrowing):
        numOfTiles = len(self.tilesToDev)
        shuffledTiles = random.sample(self.tilesToDev, numOfTiles) # to add some RNG (idk if this is the right expression)

        for i in range(numOfTiles):
            tile = shuffledTiles[i]
            # either develop tile if it's controlled by us
            if self.isNationController(tile, tilesByNation):
                devToAdd = 1 # 1 level of development, may change later according to AI personality
                if tile.canDevelop(devToAdd) and self.influence > self.personality.influenceCostToDev: # 1 level of development
                    self.addDevToTile(devToAdd, tile)
                    break
            # TODO
            # or conquer an unoccupied tile (other nations tiles will be implemented later)
            else:
                #self.personality.influenceCostToConquer = biggestVal * (len(controlledTiles) // 2) * self.personality.conquerPhaseBonus
                if self.influence > self.personality.influenceCostToConquer:
                    self.conquerTile(tile, tilesByNation)
                    break
            continue # if it ends up not having influence or resources

    # will construct buildings in our tiles
    def buildThings(self, controlledTiles):
        pass

    # TODO
    # returns a list of tiles to be developed for this nation (NOT their coords)
    # I want each AI to have different strategies and different devTiles
    # Maybe I should put this function on a separate file inside data or something 
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
            # updating and defining basic variables
            controlledTiles = self.getTilesByCoords(self.getControlledTiles(tilesByNation), tiles) # list of tiles, NOT their coords
            totalInfluenceBonus, totalMaintenance, totalValue, averageValue, biggestVal, totalPopulation = self.getData(controlledTiles)
            self.updateSize(controlledTiles)
            self.updateMoney(totalPopulation)

            # updating influence
            self.lastInfluence = self.influence
            self.influence += BASE_INFLUENCE_PER_TURN # basic bonus
            self.influence += self.getLeaderInfluenceBonus() # leader bonus
            self.influence -= totalMaintenance # maintenance of our territory
            isInfluenceGrowing = True if self.influence - self.lastInfluence > 0 else False

            # update and develop our tilesToDev
            if self.tilesToDev:
                self.devTiles(controlledTiles, tilesByNation, isInfluenceGrowing) # consumes influence
                self.tilesToDev = self.checkTilesToDev(tilesByNation)
            else:
                self.tilesToDev = self.getDevTiles(tiles, tilesByNation, controlledTiles)
            
            # Phase change
            self.updatePersonality()

            # Make ~~units~~ and buildings
            self.buildThings(controlledTiles) # empty for now

            # develop our Tiles
            self.developTiles(controlledTiles)

            # Some of the resources will "rot" every turn, so nations don't accumulate infinite resources
            self.rotResources(self.rotPercentage)

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
