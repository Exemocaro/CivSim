from pygame import encode_file_path
from Resource import *
from Character import *
from Terrain import *
from nameGen import *
#from Unit import *
from Settings import *
from Personality import *
from Building import *
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
        self.wars = wars # list of lists that contain the nations we are at war with and the war maintenance of each war
        #self.capital = 0 # contains the tile this country was first created in

        self.lastInfluence = 0 # to track if the ifluence is growing or not
        self.influence = 5
        self.techLevel = 1 # max 11
        self.lastMoney = 0
        self.money = 5 # available money for this nation

        self.actions = 0 # number of things this nation can do per turn

        self.numBuildings = 0 # to make it easier to print on the console

        #self.units = [] # probably won't use this

        self.warInfluenceCost = 0

        self.neighbourTiles = [] # all the tiles adjacent to our nation that don't belong to us

        self.techs = [] # idk if I'll use this

        self.wasEliminated = False

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

    # return all tiles this nation controls
    def getTiles(self, tilesByNation, tiles):
        ctrl = []
        for coord in tilesByNation:
            if tilesByNation[coord] == self.id:
                ctrl.append(tiles[coord[1]][coord[0]])
        return ctrl

    # adds resources to a nation's available resources, given a dictionary of resources
    def addResources(self, rs):
        for r in rs:
            self.resources[r] += rs[r]
    
    # decreases a certain percentage of resources of this nation's stockpile, usually called each turn
    def rotResources(self, percentage):
        for r in self.resources:
            self.resources[r] = round(self.resources[r] * ((100-percentage) / 100))

    # returns the total maintenance value of all our wars, in money 
    def getWarMaintenance(self):
        maintenance = 0
        for war in self.wars:
            maintenance += war[1]
        return maintenance

    # TODO
    # returns all neighbours of a tile that belong to an enemy nation
    def getEnemyNeighbours(self, tilesByNation):
        enemyNeighbours = []
        for war in self.wars:
            nation = war[0]
            for n in self.neighbourTiles:
                neighbourNationID = self.getController(n, tilesByNation)
                if nation.id == neighbourNationID:
                    enemyNeighbours.append(n)
        return enemyNeighbours

    # returns total maintenance, the total value, the average value, the biggest population and the average population in our controlled tiles
    # this was made like this to avoid looping several times, this way we loop only one and get all the data we need
    def getData(self, tiles, controlledTiles):
        totalInfluence = 0
        maintenance = [0,0]
        average = 0
        totalValue = 0
        biggest = 0
        pop = 0
        numBuildings = 0
        self.neighbourTiles = [] # emptying the neighbour tiles so it doesn't accumulate infinitely
        for tile in controlledTiles:

            # since we are looping through all tiles we will take this chance to fill this
            neighbours = tile.getNeighbours(tiles, len(tiles[0]), len(tiles))
            for n in neighbours:
                if n not in self.neighbourTiles:
                    self.neighbourTiles.append(n)
            
            tileMaintenance = tile.getMaintenance() # temp variable

            numBuildings += tile.getNumBuildings()
            totalInfluence += tile.getInfluence()
            maintenance[0] += tileMaintenance[0]
            maintenance[1] += tileMaintenance[1]
            totalValue += tile.value
            pop += tile.population
            if tile.value > biggest:
                biggest = tile.value
        maintenance[0] += self.getWarMaintenance() # war maintenance added to total money maintenance
        average = 0 if len(controlledTiles) == 0 else round(totalValue / len(controlledTiles), 2)
        totalInfluence *= TECH_BONUS[self.techLevel - 1] # the higher the tech, the better the bonus on influence gain
        return (numBuildings, totalInfluence, maintenance, totalValue, average, biggest, pop)

    # returns our leader's influence bonus, will be added each turn to our nation
    def getLeaderInfluenceBonus(self):
        return self.leader.prosperity

    # develops all our inhabitated tiles and updates our resources
    def developTiles(self, controlledTiles, isInfluenceGrowing):
        if isInfluenceGrowing:
            for tile in controlledTiles:
                if tile.population > 0: # develop only inhabitated tiles
                    # these 3 are necessary, don't remove them
                    tile.setProduction()
                    tile.develop()
                    self.addResources(tile.getLeftovers())
    
    # see if we can change our personality's phase and other stats
    def updatePersonality(self):
        if self.turnsNoExpand > TURNS_TO_EXPAND:
            self.personality.phase = "peacefully-expanding"
        if self.personality.phase != "aggressively-expanding":
            prob = random.randint(0,100)
            if prob < PROBABILITY_AGGRESSIVE_EXPANSION:
                self.personality.phase = "aggressively-expanding"

        self.personality.updateValues()

    # updates our size and the number of turns without changing our size
    def updateSize(self, controlledTiles):
        if self.size != len(controlledTiles):
            self.size = len(controlledTiles)
            self.turnsNoExpand = 0
        else:
            self.turnsNoExpand += 1

    # udpates the current amount of money this nation has
    def updateMoney(self, totalPopulation, totalMaintenance):
        self.lastMoney = self.money
        self.money += totalPopulation * TAX_BY_POP
        self.money -= totalMaintenance
        self.money = round(self.money, 3)
        return True if self.money - self.lastMoney > 0 else False # returns if our money is growing or not

    # updates the current amount of influence this nation has
    def updateInfluence(self, totalMaintenance, tileBonus):
        self.lastInfluence = self.influence
        self.influence += BASE_INFLUENCE_PER_TURN # basic bonus
        self.influence += self.getLeaderInfluenceBonus() # leader bonus
        self.influence += tileBonus
        self.influence -= totalMaintenance # maintenance of our territory
        self.influence -= self.warInfluenceCost
        self.influence = round(self.influence, 2)
        return True if self.influence - self.lastInfluence > 0 else False # returns if the influence is growing or not

    # updates our current leader with either new stats or with death :( will also replace it in that case
    def updateLeader(self):
        self.leader.age += 1

        # starting at 20, the probability of dying will increase given the leader's vitality
        probabilityOfDying = 1 # out of 100, base starting value for each year
        if self.leader.age > 50:
            probabilityOfDying = 3
        elif self.leader.age > 60:
            probabilityOfDying = 5
        elif self.leader.age > 70:
            probabilityOfDying = 10

        if (self.leader.vitality + 2) * 10 > self.leader.age:
            probabilityOfDying += 5
        
        r = random.randint(1,100)
        if r <= probabilityOfDying: # the leader died :(
            self.leader = Character.getSuccessor(self.leader)

    # updates our current tech level according to the total number of buildings in our nation
    def updateTech(self, numBuildings):
        newTechLevel = 1 # 1 it's the minimum value
        while numBuildings >= NUM_BUILDINGS_TO_INCREASE_TECH:
            numBuildings -= NUM_BUILDINGS_TO_INCREASE_TECH
            newTechLevel += 1
        self.techLevel = newTechLevel if newTechLevel <= 11 else 11

    # conquers a tile for this nation; consumes influence
    def conquerTile(self, tile, tilesByNation):
        self.changeTileOwnership(tile, tilesByNation)
        self.influence -= self.personality.influenceCostToConquer

    # updates this nation's availabe actions according to our size
    def updateActions(self):
        if self.size >= SIZE_MAX_ACTIONS:
            self.actions = MAX_ACTIONS
        elif self.size >= SIZE_MEDIUM_ACTIONS:
            self.actions = MEDIUM_ACTIONS
        else:
            self.actions = MIN_ACTIONS

    # returns a value in money to be alocated to a war
    def returnNewWarBudget(self, moneyDif, nations, nation):
        if moneyDif > WAR_MAINTENANCE_RANGE[1]:
            limit = WAR_MAINTENANCE_RANGE[1]
        else:
            limit = int(moneyDif)
        
        prob = random.randint(1,10)
        if prob < 2:
            return random.randint(limit - 5, limit)
        elif prob <= 5:
            halfMaintenance = int((limit - WAR_MAINTENANCE_RANGE[0]) / 2)
            return random.randint(halfMaintenance, limit)
        else:
            return random.randint(WAR_MAINTENANCE_RANGE[0], limit)

    # returns this nation's war budget for a specific war against the given nation
    def getWarBudget(self, nation):
        for war in self.wars:
            if war[0].id == nation.id:
                return war[1]
        print("getWarBudget failed, probably this nation is not at war with the other nation that called it...")
        return -1 # if something is wrong
    
    # removes a war with a certain nation
    def removeWar(self, nation):
        for war in self.wars:
            n = war[0]
            if n == nation:
                self.wars.remove(war)
                break

    # updates wars and tries to conquer enemy tiles
    def updateStance(self, tiles, nations, tilesByNation, controlledTiles, isMoneyGrowing):
        moneyDif = self.money - self.lastMoney
        numWars = len(self.wars)

        # in case a nation has no tiles / was conquered:
        if len(controlledTiles) == 0 and numWars > 0: # make peace with everyone in case this nation has no tiles
            self.warInfluenceCost = 0
            for war in self.wars:
                self.wars.remove(war)
                war[0].removeWar(self)
        elif len(controlledTiles) == 0: # reset some values and ignore the rest of the function
            self.warInfluenceCost = 0
            return None

        if len(self.wars) == 0: # updating the influence maintenance on wars
            self.warInfluenceCost = 0
        else:
            # the better the tech, the costly it is to maintain wars for longer periods of time
            # making this to avoid countries from getting too big
            self.warInfluenceCost += TECH_BONUS[self.techLevel - 1] * WAR_INFLUENCE_MAINTENANCE_COST
        newWar = False # will be True if a new war is added, to avoid unnecessary looping
        # first we determine if we can declare war, and if so we see if we will do that
        if self.money > WAR_COST and moneyDif > WAR_MAINTENANCE_RANGE[0] and numWars < self.personality.maxWars:
            prob = random.randint(1,100)
            willDeclareWar = True if prob <= PROBABILITY_WAR_PER_TURN else False
            if willDeclareWar:
                # another loop :( I'll try to fix this if it consumes too much CPU
                for tile in controlledTiles:
                    for n in tile.getNeighbours(tiles, len(tiles[0]), len(tiles)):
                        neighbourNationID = self.getController(n, tilesByNation)
                        if neighbourNationID not in [self.id, 0]: # if True means it's a neighbour nation
                            #warNation = None
                            for nation in nations:
                                if nation.id == neighbourNationID and numWars < self.personality.maxWars:
                                    #warNation = nation
                                    self.wars.append([nation, self.returnNewWarBudget(moneyDif, nations, nation)])
                                    nation.wars.append([self, nation.returnNewWarBudget(moneyDif, nations, self)])
                                    newWar = True
                                    break
                        if newWar:
                            break
                    if newWar:
                        break
    
        # then we see if we can conquer a tile from an enemy
        # for now it won't take an action to conquer a tile
        if numWars > 0 and not newWar: # if it's not empty, len(self.wars) > 0
            enemyTiles = self.getEnemyNeighbours(tilesByNation)
            if len(enemyTiles) > 0:
                tileToConquer = random.choice(enemyTiles)
                for war in self.wars:
                    nation = war[0]
                    nationID = self.getController(tileToConquer, tilesByNation)
                    if nation.id == nationID:
                        if nation.size <= 0: # just in case the nation doesn't exist anymore
                            self.wars.remove(war)
                            nation.removeWar(self)
                            break
                        if self.influence > self.personality.influenceCostToConquer: # it will still cost influence tho
                            # leaders and technology are very important in battles too:
                            winsBattle = (war[1] + (TECH_BONUS[self.techLevel - 1] * self.leader.martial)) > (nation.getWarBudget(self) + (TECH_BONUS[nation.techLevel - 1] * nation.leader.martial))
                            if winsBattle and nation.getWarBudget != -1:
                                self.conquerTile(tileToConquer, tilesByNation)
                                #self.actions -= 1
                            elif nation.getWarBudget(self) == -1: # to delete wars with nations that might be bugged?
                                self.wars.remove(war)
                                nation.removeWar(self)
                            else: # if it doesn't conquer this tile, it will still lose influence trying to attack it
                                self.influence -= self.personality.influenceCostToConquer
                            break
            else: # no adjacent enemy tile to conquer, make peace with everyone
                for war in self.wars:
                    self.wars.remove(war)
                    war[0].removeWar(self)
            
            # make peace with a random nation we are at war with
            numWars = len(self.wars)
            r = random.randint(1,100)
            if numWars > self.personality.maxWars:
                if r <= PROBABILITY_ENDING_WAR_MAX:
                    randomWar = random.choice(self.wars)
                    self.wars.remove(randomWar)
                    randomWar[0].removeWar(self)
            elif numWars > 0 and r <= PROBABILITY_ENDING_WAR:
                randomWar = random.choice(self.wars)
                self.wars.remove(randomWar)
                randomWar[0].removeWar(self)

    # adds development to the specified tile; consumes influence
    def addDevToTile(self, devValue, tile):
        tile.addDevelopment(devValue)
        self.influence -= self.personality.influenceCostToDev

    # TODO
    # will develop one of our tilesToDev at the cost of influence
    def devTiles(self, controlledTiles, tilesByNation, isInfluenceGrowing):
        numOfTiles = len(self.tilesToDev)
        shuffledTiles = random.sample(self.tilesToDev, numOfTiles) # to add some RNG (idk if this is the right expression)

        if isInfluenceGrowing or self.influence > (SAFE_INFLUENCE_TO_DEV * self.personality.influenceCostToDev):
            for i in range(numOfTiles):
                tile = shuffledTiles[i]
                # either develop tile if it's controlled by us
                if self.isNationController(tile, tilesByNation):
                    devToAdd = 1 # 1 level of development, may change later according to AI personality
                    if tile.canDevelop(devToAdd) and self.influence > self.personality.influenceCostToDev: # 1 level of development
                        self.addDevToTile(devToAdd, tile)
                        self.actions -= 1
                        break
                elif self.getController(tile, tilesByNation) != 0:
                    # an AI shouldn't develop antoher nation's tile, so we'll delete the tile from the list
                    self.tilesToDev.remove(tile)
                else: # if the tile is not ours and it's empty then we conquer it
                    #self.personality.influenceCostToConquer = biggestVal * (len(controlledTiles) // 2) * self.personality.conquerPhaseBonus
                    if self.influence > self.personality.influenceCostToConquer:
                        self.conquerTile(tile, tilesByNation)
                        self.actions -= 1
                        break
                continue # if it ends up not having influence or resources
    
    # returns a building depending on the code passed and the available money and influence this nation has
    # returns None if it didn't find any building
    def chooseBuilding(self, code):
        if code == "i": # influence building
            if self.money >= BASE_BUILDING_MONEY_COST:
                return random.choice(L1_INFLUENCE_BUILDINGS)
        elif code == "m": # money building
            if self.influence >= BASE_BUILDING_INFLUENCE_COST:
                return random.choice(L1_MONEY_BUILDINGS)
        return None # if we end up not choosing any building

    # will construct buildings in our tiles
    def buildThings(self, controlledTiles, isMoneyGrowing, isInfluenceGrowing):
        
        if len(controlledTiles) > 0:
            # so we don't repeat code
            def chooseTile():
                shuffledTiles = random.sample(controlledTiles, self.size)
                i = 0
                tileToBuild = random.choice(shuffledTiles)
                while i < self.size and tileToBuild.population <= 0 and len(tileToBuild.buildings) == MAX_BUILDINGS_PER_TILE:
                    tileToBuild = shuffledTiles[i]
                    i += 1
                return tileToBuild if i < self.size else None
            
            tileToBuild = chooseTile()
            buildings = []
            if isMoneyGrowing: # we can spend on influence buildings
                buildings.append(self.chooseBuilding("i"))
            if not isInfluenceGrowing: # prioritize influence above everything
                buildings.append(self.chooseBuilding("i"))
            elif isInfluenceGrowing: # we can spend on money buildings
                buildings.append(self.chooseBuilding("m"))

            if tileToBuild is not None:
                for building in buildings:
                    if building is not None:
                        tileToBuild.buildings.append(building)
                        self.influence -= building.influenceCost
                        self.money -= building.moneyCost
                        self.actions -= 1

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
            while not devTiles and (tries < MAX_DEV_TRIES or tries < len(controlledTiles) // 2):
                if len(controlledTiles) > 0:
                    randomTile = random.choice(controlledTiles) # first we choose a random controlled tile

                    # avoid expanding into these tiles
                    if randomTile.terrain.name in uncontrollableTerrains:
                        tries += 1
                        continue

                    # now according to the AI's personality, we make it a tile to develop or not
                    prob = random.randint(1,100)
                    if self.personality.phase == "aggressively-expanding":
                        if prob <= PROBABILITY_AGGR_EXP_DEV_TILE:
                            devTiles.append(randomTile)
                            break
                        else:
                            tries -= 0.1 # maybe it's too low?
                    # since it's "peacefully-expanding", it will just develop a random owned tile
                    # the more tiles it has, bigger the chance to develop a tile
                    elif self.personality.phase == "peacefully-expanding":
                        if prob <= PROBABILITY_PEACE_EXP_DEV_TILE:
                            devTiles.append(randomTile)
                            break
                    elif self.personality.phase == "developing":
                        if prob <= PROBABILITY_DEVELOPING_DEV_TILE:
                            devTiles.append(randomTile)
                            break
                    
                    # then we pick it's neighbours
                    itsNeighbours = randomTile.getNeighbours(tiles, len(tiles[0]), len(tiles))
                    for n in itsNeighbours:
                        # it can only expand to uncontrolled tiles
                        if self.find(tilesByNation, n.coords) == 0: #and self.personality.phase != "aggressively-expanding": # Uncontrolled
                            devTiles.append(n)
                        #else:
                        #    devTiles.append(n)
                else:
                    # If they do not control any tile then that means they were conquered, so they shouldn't get into this loop
                    print(f"\n{self.name} with id {self.id} has no tiles!!! Something went wrong! Controlled Tiles: {self.getControlledTiles(tilesByNation)}")
                    break

                tries += 1
        else:
            print(f"\nIf this nation's personality isn't basic, then what is it?! Name: {self.name}, id: {self.id}")
        return devTiles

    # given the tilesByNation found in Engine.py, checks if all the tiles to be developed are controlled by this nation.
    def checkTilesToDev(self, tilesByNation):
        for tile in self.tilesToDev:
            if self.getController(tile, tilesByNation) != 0:
                self.tilesToDev.remove(tile)
    
    # removes this nation from the game if it controlls no tiles (i.e. they were conquered)
    # TODO, delete from tilesByNation too?
    def checkExistence(self, nations, controlledTiles):
        if len(controlledTiles) <= 0:
            print(f"{self.name} with id {self.id} was deleted because it had no tiles")
            #nations.remove(self) # doesnt work
            self.wasEliminated = True

    # makes a turn for this AI, called each turn for each AI/nation
    def makeTurn(self, tiles, nations, tilesByNation):
        if self.id != 0 and not self.wasEliminated:
            print("math | ", end = "")
            # updating and defining basic variables
            controlledTiles = self.getTiles(tilesByNation, tiles) #self.getTilesByCoords(self.getControlledTiles(tilesByNation), tiles) # list of tiles, NOT their coords
            numBuildings, totalInfluenceBonus, totalMaintenance, totalValue, averageValue, biggestVal, totalPopulation = self.getData(tiles, controlledTiles)
            self.updateSize(controlledTiles)
            self.updateActions()
            self.numBuildings = numBuildings
            isMoneyGrowing = self.updateMoney(totalPopulation, totalMaintenance[0])
            isInfluenceGrowing = self.updateInfluence(totalMaintenance[1], totalInfluenceBonus) # updating our influence and checking if it's growing or not

            print(f"id {self.id} | num tiles: {len(controlledTiles)} | money {self.money} | inf {self.influence} | wars {len(self.wars)} | ", end = "")

            # ------ THINGS THAT CONSUME ACTION POINTS

            beforeActions = self.actions
            didSomething = True
            while self.actions > 0 and didSomething:
                # first check if we don't have enemy tiles in our tiles to dev
                self.checkTilesToDev(tilesByNation)
                # update and develop our tilesToDev
                if len(self.tilesToDev) > 0:
                    self.devTiles(controlledTiles, tilesByNation, isInfluenceGrowing) # consumes influence
                else:
                    self.tilesToDev = self.getDevTiles(tiles, tilesByNation, controlledTiles)

                # Try to build something on our tiles
                self.buildThings(controlledTiles, isMoneyGrowing, isInfluenceGrowing)

                didSomething = True if self.actions != beforeActions else False

            # ------ AND THAT DON'T CONSUME ACTION POINTS 

            # develop our Tiles
            print("1 | ", end = "")
            self.developTiles(controlledTiles, isInfluenceGrowing)

            # personality update, includes changing the phase and other stats realted to it
            print("2 | ", end = "")
            self.updatePersonality()

            # declares wars on neighbours and tries to conquer their tiles
            print("3 | ", end = "")
            self.updateStance(tiles, nations, tilesByNation, controlledTiles, isMoneyGrowing)

            # Some of the resources will "rot" every turn, so nations don't accumulate infinite resources
            print("4 | ", end = "")
            self.rotResources(self.rotPercentage)

            # update our leader stats/age
            print("5 | ", end = "")
            self.updateLeader()

            # update our tech level
            print("6 | ", end = "")
            self.updateTech(numBuildings)

            # check if the nation is still in the game
            #self.checkExistence(nations, controlledTiles)

            print("turn end")

    # I have to copy these functions to this class because I can't import Engine
    # There surely is a better way to do this
    def find(self, tilesByNation, tileCoords):
        return tilesByNation[tileCoords]

    def isNationController(self, tile, tilesByNation):
        if self.id == self.find(tilesByNation, tile.coords):
            return True
        return False

    # returns the id of the nation that controls a certain tile
    def getController(self, tile, tilesByNation):
        #tiles = gameState[0]
        #nations = gameState[1]
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
        with open("../data/kingdomNames.txt", "r") as file:
            names = file.readlines()
        while len(name) < 4: # just to avoid empty lines
            name = random.choice(names)
        
        # to make the first char upperCase and remove a weird last char
        name = name[0].upper() + name[1:(-1)]
        #print(f"\nChosen Name:{name}\n")

        return name

# The "nation" that represents unclaimed land
emptyNation = Nation(0,BARBARIANS_COLOR2, "", Character("", 0, "", 0, 0, 0), [], [], random.choice(SIMPLE_PERSONALITIES))
