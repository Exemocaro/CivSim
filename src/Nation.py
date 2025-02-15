from pygame.cursors import sizer_x_strings
from Resource import *
from Character import *
from Terrain import *
from Names import *
#from Unit import *
from Settings import *
from Personality import *
from Building import *
import random
from math import sqrt

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
        self.max_wars = 0 # max number of wars a nation can participate in at a certain a moment
        self.focusedTiles = [] # list of tiles to make an attack on, so countries don't grow in random shapes
        self.capital = None # contains the tile this country was first created in
        self.attackCenter = None # a tile from where attacks will "center" so countries don't just become round blobs
        self.turnsWithNoChangeInAttackCenter = 0 # number of turns our tile in self.attackCenter hasn't changed

        self.lastInfluence = 0 # to track if the ifluence is growing or not
        self.influence = 5 # current influence amount

        self.techLevel = 0 # max 10
        self.countryDev = 1 # testing purposes to decide our tech level

        self.lastMoney = 0
        self.money = 5 # available money for this nation

        self.actions = 2 # number of things this nation can do per turn
        self.maxActions = 2 # copy of self.actions to use after the actions are consumed

        self.numBuildings = 0 # to make it easier to print on the console

        #self.units = [] # probably won't use this

        self.warinfluence_cost = 0 # cost in influence for maintaining a war

        self.neighbourTiles = [] # all the tiles adjacent to our nation that don't belong to us

        self.techs = [] # idk if I'll use this

        self.wasEliminated = False

        self.personality = personality
        self.tilesToDev = []
        self.turnsNoExpand = 0
        self.rotPercentage = BASE_ROT_PERCENTAGE - (self.techLevel * 2)

        self.size = 1

        self.representation = "Uncontrolled" if name == "" else f"{self.name}"

    # sets this nation's capital as the tile passed
    def setCapital(self, tile):
        self.capital = tile
        self.attackCenter = tile

    # updates our current capital if it's not controlledByUs
    def updateCapital(self, controlledTiles, tilesByNation):
        changedCapital = False
        if not self.isNationController(self.capital, tilesByNation) and controlledTiles:
            randomTiles = random.sample(controlledTiles, len(controlledTiles))
            for tile in randomTiles:
                if tile.terrain.name not in no_beginning_terrains:
                    changedCapital = True
                    break
            self.setCapital(tile)
            return changedCapital

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

    # returns the tile at the passed coords
    def getTileByCoords(self, coords, tiles):
        return tiles[coords[1]][coords[0]] # first y, then x (but why? i dont remember why i made it like this)

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
            percentage -= self.leader.prosperity # more prosperity, more resources
            self.resources[r] = round(self.resources[r] * ((100-percentage) / 100))

    # returns the total maintenance value of all our wars, in money 
    def getWarMaintenance(self):
        maintenance = 0
        for war in self.wars:
            maintenance += war[1]
        return maintenance

    # returns all neighbours of a tile that belong to an enemy nation
    def getEnemyNeighbours(self, tiles, tilesByNation, nations):
        enemyNeighbours = []
        self.focusedTiles = []

        # get the ids of the nations we are at war with
        ids = []
        for war in self.wars:
            ids.append(war[0].id)

        # then check if the tiles belong to any of them
        for n in self.neighbourTiles:
            neighbourNationID = self.getControllerId(n, tilesByNation)
            if neighbourNationID in ids: # small check in case some nations lose and keep territory
                enemyNeighbours.append(n)
                enemyTileNeighbours = n.get_neighbours(tiles, len(tiles[0]), len(tiles))
                
                # checking if the tile is an enclave inside this nation's territory
                # though I dislike having all of these loops :(
                # and I'm not sure if this even works
                isEnclave = True
                for t in enemyNeighbours:
                    if not self.isNationController(t, tilesByNation):
                        isEnclave = False
                        break
                if isEnclave:
                    self.focusedTiles.append(n)

        return enemyNeighbours

    # returns total maintenance, the total value, the average value, the biggest population and the average population in our controlled tiles
    # this was made like this to avoid looping several times, this way we loop only one and get all the data we need
    def getData(self, tiles, controlledTiles, tilesByNation, turn):
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
            neighbours = tile.get_neighbours(tiles, len(tiles[0]), len(tiles))
            for n in neighbours:
                if not self.isNationController(n, tilesByNation): # this if increases performance by a LOT
                    if n not in self.neighbourTiles:
                        self.neighbourTiles.append(n)
            
            tileMaintenance = tile.get_maintenance() # temp variable

            numBuildings += tile.get_num_buildings()
            totalInfluence += tile.get_influence()
            maintenance[0] += tileMaintenance[0]
            maintenance[1] += tileMaintenance[1]
            totalValue += tile.value
            pop += tile.population
            if tile.value > biggest:
                biggest = tile.value
        maintenance[0] += self.getWarMaintenance() # war maintenance added to total money maintenance
        average = 0 if len(controlledTiles) == 0 else round(totalValue / len(controlledTiles), 2)
        totalInfluence *= TECH_BONUS[self.techLevel] # the higher the tech, the better the bonus on influence gain
        return (numBuildings, totalInfluence, maintenance, totalValue, average, biggest, pop)

    # returns our leader's influence bonus, will be added each turn to our nation
    def getLeaderInfluenceBonus(self):
        return self.leader.prosperity

    # develops all our inhabitated tiles and updates our resources
    def updateTiles(self, controlledTiles):
        for tile in controlledTiles:
            if tile.population > 0: # develop only inhabitated tiles
                # these 3 are necessary, don't remove them
                tile.set_production()
                tile.develop()
                self.addResources(tile.get_leftovers())
    
    # see if we can change our personality's phase and other stats
    def updatePersonality(self):
        if self.turnsNoExpand > TURNS_TO_EXPAND:
            self.personality.phase = "peacefully-expanding"
        if self.personality.phase != "aggressively-expanding":
            prob = random.randint(0,100)
            if prob < PROBABILITY_AGGRESSIVE_EXPANSION:
                self.personality.phase = "aggressively-expanding"

        self.personality.update_values()

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
        self.influence -= self.warinfluence_cost
        self.influence = round(self.influence, 2)
        influenceDif = self.influence - self.lastInfluence
        return True if influenceDif > 0 else False # returns True if the influence is growing, False if not

    # returns a list with the countryDev level of all nations that are still playing
    def getNationsDevs(self, nations):
        list = []
        for nation in nations:
            if not nation.wasEliminated and nation.countryDev != 0 and self.countryDev > COUNTRY_DEV_STABILIZER:
                list.append(nation.countryDev)
        return list

    # updates our current tech level according to the total number of buildings in our nation
    def updateTech(self, averageValue, totalValue, numBuildings, controlledTiles, turn, nations):

        # determine our country development. will be used to determine our tech level
        if turn > 1 and controlledTiles:
            multiplier = (averageValue * self.maxActions * self.size)
            if multiplier != 0:
                self.countryDev = ((totalValue + numBuildings) / multiplier) + COUNTRY_DEV_STABILIZER
            else:
                self.countryDev = COUNTRY_DEV_STABILIZER
            self.countryDev = round(self.countryDev, 4)

            devList = self.getNationsDevs(nations) # to sort by the second element of the tuple, the indice
            newTechLevel = self.techLevel
            if devList: # if it's not empty
                minD = min(devList)
                maxD = max(devList)
                dif = (maxD - minD) / MAX_TECH_LEVEL 
                newTechLevel = 0
                while minD <= self.countryDev and self.techLevel < MAX_TECH_LEVEL and minD > 0.1:
                    minD += dif
                    newTechLevel += 1

            # increase our tech level slowly
            if newTechLevel > self.techLevel:
                self.techLevel += 1
            elif newTechLevel < self.techLevel:
                self.techLevel -= 1

    # conquers a tile for this nation; consumes influence
    def conquerTile(self, tile, tilesByNation, consumesAction):
        self.changeTileOwnership(tile, tilesByNation)
        self.influence -= self.personality.influence_cost_to_conquer
        if consumesAction: self.actions -= 1 # consumes an action point

    # what happens to this nation if it fails to conquer a tile
    def loseBattle(self):
        techBonus = TECH_BONUS[self.techLevel]
        self.influence -= self.personality.influence_cost_to_conquer * techBonus

    # updates this nation's available actions according to our size
    def updateActions(self, controlledTiles):
        numTiles = len(controlledTiles)
        self.actions = MIN_ACTIONS
        self.actions += (numTiles//ACTIONS_STEP_VALUE) * ACTIONS_STEP
        self.maxActions = self.actions

    # algorithm that returns a value in money to be alocated to a war
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
        
        print("getWarBudget failed, probably this nation is not at war with the other nation that called it?")
        return -1 # if something is wrong
    
    # removes a war with a certain nation
    def removeWar(self, nation):
        for war in self.wars:
            n = war[0]
            if n == nation:
                self.wars.remove(war)
                return True
        print("removeWar failed, this nation is not at war with the passed nation")

    # ends a war with the passed nation
    def endWar(self, nation):
        self.removeWar(nation)
        nation.removeWar(self)

    # penalties this nation will take for losing a war against the passed nation
    def takeLostWarPenalties(self, nation):
        techBonus = TECH_BONUS[nation.techLevel]
        self.money -= WAR_MONEY_REWARD * techBonus
        nation.money += WAR_MONEY_REWARD * techBonus
        self.influence -= WAR_INFLUENCE_REWARD * techBonus
        nation.influence += WAR_INFLUENCE_REWARD * techBonus

    #TODO, take leader's personality into account after calculating this
    # update's our nations max number of possible concurrent wars. More than this and the nation will take heavy penalties
    def updatemax_wars(self, controlledTiles):
        numTiles = len(controlledTiles)
        self.max_wars = MIN_WARS
        self.max_wars += (numTiles//WARS_STEP_VALUE) * WARS_STEP

    # what happens to the passed nation when its capital is conquered by this nation
    def conqueredCapital(self, nation, tiles, tilesByNation):
        for tileCoords in tilesByNation: # key are the tile coords, value is the id of the owner
            if self.influence > (self.personality.influence_cost_to_conquer * TECH_BONUS[self.techLevel] * TECH_BONUS[nation.techLevel]):
                if tilesByNation[tileCoords] == nation.id:
                    self.changeTileOwnership(self.getTileByCoords(tileCoords, tiles), tilesByNation)
                    self.influence -= self.personality.influence_cost_to_conquer

    # return to monke
    def disband(self, nation, tiles, tilesByNation):
        for tileCoords in tilesByNation: # key are the tile coords, value is the id of the owner
            if tilesByNation[tileCoords] == nation.id:
                tilesByNation[tileCoords] = 0

    # determines the result of a battle between this nation and nation we are at war with in the passed war
    def doBattle(self, war):
        nation = war[0]
        attackerRNG = random.randint(1, MAX_BATTLE_RNG)
        defenderRNG = random.randint(1, MAX_BATTLE_RNG)
        attackerIronPerCapita = 0
        defenderIronPerCapita = 0
        if self.size > 0 and nation.size > 0: # having a lot of iron is important
            attackerIronPerCapita = round((self.resources["iron"] / self.size) * 10)
            defenderIronPerCapita = round((nation.resources["iron"] / nation.size) * 10)
        ourChances = (war[1] + attackerRNG + attackerIronPerCapita) + (TECH_BONUS[self.techLevel] * self.leader.martial)
        theirChances = (nation.getWarBudget(self) + defenderRNG + defenderIronPerCapita) + (TECH_BONUS[nation.techLevel] * nation.leader.martial)
        winsBattle = ourChances > theirChances
        return winsBattle

    # tries to conquer an enemy tile if we are at war with someone
    def makeAttack(self, tiles, nations, tilesByNation, controlledTiles, isMoneyGrowing):
        numWars = len(self.wars)
        if numWars > 0:
            enemyTiles = self.getEnemyNeighbours(tiles, tilesByNation, nations)
            
            # will select some random Tiles from our enemies and select the closest to the capital
            # to avoid conquering tiles that are too far away from the main territory and avoid enclaves
            def chooseTile(n):
                distList = []
                for i in range(n):
                    tileToConquer = random.choice(enemyTiles)
                    distanceToAttackCenter = sqrt((tileToConquer.x - self.attackCenter.x)**2 + (tileToConquer.y - self.attackCenter.y)**2) # distance formula
                    distList.append((distanceToAttackCenter, tileToConquer))
                distList.sort(key=lambda x:x[0]) # sort by distance to the capital
                return distList[0][1] # return the closest to the capital
            
            if enemyTiles:
                # choosing a random tile to attack
                if self.focusedTiles: # if there are enclaves inside our territory or important tiles we need to conquer:
                    if not self.isNationController(self.focusedTiles[0], tilesByNation):
                        tileToConquer = self.focusedTiles[0]
                    else:
                        self.focusedTiles.remove(self.focusedTiles[0])
                else: # if not, let's semi-randomly choose them
                    tileToConquer = chooseTile(CONQUER_ACCURACY) # number of tiles to choose from
                nationID = self.getControllerId(tileToConquer, tilesByNation)
                nation = self.getNation(nations, nationID)
                war = 0
                # finding the right nation and war
                for w in self.wars:
                    if w[0].id == nationID:
                        nation = w[0]
                        war = w
                        break

                if nation.size <= 0: # just in case the nation doesn't exist anymore
                    self.endWar(nation)
                if self.influence > self.personality.influence_cost_to_conquer: # it will still cost influence tho
                    # leaders and technology are very important in battles too:
                    winsBattle = self.doBattle(war)
                    if winsBattle and nation.getWarBudget(self) != -1 and self.actions > 0:
                        self.conquerTile(tileToConquer, tilesByNation, True)
                        if tileToConquer == nation.capital:
                            self.conqueredCapital(nation, tiles, tilesByNation)
                    elif nation.getWarBudget(self) == -1: # to delete wars with nations that might be bugged?
                        self.endWar(nation)
                    else: # if it doesn't conquer this tile, it will still lose influence trying to attack it
                        self.loseBattle()
                #else:
                #    print("No influence to conquer tile!")
            else: # no adjacent enemy tile to conquer, make peace with everyone
                for war in self.wars:
                    self.endWar(war[0])
    
    # updates this nation's attack center and the turns required to change it
    def updateAttackCenter(self, tiles, tilesByNation, controlledTiles):
        self.turnsWithNoChangeInAttackCenter += 1 # update this variable
        r = random.randint(1, 100)
        if r <= self.turnsWithNoChangeInAttackCenter * 2 or not self.isNationController(self.attackCenter, tilesByNation):
            if controlledTiles:
                self.attackCenter = random.choice(controlledTiles)

    #TODO
    # updates wars and tries to conquer enemy tiles
    def updateStance(self, tiles, nations, tilesByNation, controlledTiles, isMoneyGrowing):
        
        self.updateAttackCenter(tiles, tilesByNation, controlledTiles)
        
        moneyDif = self.money - self.lastMoney
        numWars = len(self.wars)
        numTiles = len(controlledTiles)

        # in case a nation has no tiles / was conquered:
        if numTiles == 0: # make peace with everyone in case this nation has no tiles
            if numWars > 0:
                for war in self.wars:
                    #self.endWar(war[0])
                    self.wars.remove(war)
            self.warinfluence_cost = 0

        if numWars == 0: # updating the influence maintenance on wars
            self.warinfluence_cost = 0
        else:
            # the better the tech, the costly it is to maintain wars for longer periods of time
            # making this to avoid countries from getting too big
            self.warinfluence_cost += (TECH_BONUS[self.techLevel] * WAR_INFLUENCE_MAINTENANCE_COST) * numWars

        newWar = False # will be True if a new war is added, to avoid unnecessary looping
        # first we determine if we can declare war, and if so we see if we will do that
        if self.money > WAR_COST and moneyDif > WAR_MAINTENANCE_RANGE[0] and numWars < self.max_wars:
            prob = random.randint(1,100)
            willDeclareWar = True if prob <= PROBABILITY_WAR_PER_TURN else False
            if willDeclareWar:
                for tile in controlledTiles:
                    for n in tile.get_neighbours(tiles, len(tiles[0]), len(tiles)):
                        neighbourNationID = self.getControllerId(n, tilesByNation)
                        if neighbourNationID not in [self.id, 0]: # if True means it's a neighbour nation
                            #warNation = None
                            for nation in nations:
                                if nation.id == neighbourNationID and numWars < self.max_wars:
                                    #warNation = nation
                                    self.wars.append([nation, self.returnNewWarBudget(moneyDif, nations, nation)])
                                    nation.wars.append([self, nation.returnNewWarBudget(moneyDif, nations, self)])
                                    newWar = True
                                    break
                        if newWar:
                            break
                    if newWar:
                        break
        
        # make peace with a random nation we are at war with
        if numWars > 0 and not newWar: # if it's not empty, len(self.wars) > 0
            numWars = len(self.wars)
            r = random.randint(1,100)
            if (numWars > self.max_wars or self.influence < 0 or self.money < 0) and numWars > 0:
                if r <= PROBABILITY_ENDING_WAR_MAX:
                    randomWar = random.choice(self.wars)
                    self.endWar(randomWar[0])
                    self.takeLostWarPenalties(randomWar[0])
            elif numWars > 0 and r <= PROBABILITY_ENDING_WAR:
                randomWar = random.choice(self.wars)
                self.endWar(randomWar[0])

    # adds development to the specified tile; consumes influence
    def addDevToTile(self, devValue, tile):
        tile.add_development(devValue)
        self.influence -= self.personality.influence_cost_to_dev

    # will develop one of our tilesToDev at the cost of influence
    def developTiles(self, tiles, controlledTiles, tilesByNation, isInfluenceGrowing):
        if not self.tilesToDev:
            self.tilesToDev = self.getDevTiles(tiles, tilesByNation, controlledTiles)
        elif isInfluenceGrowing or self.influence > (SAFE_INFLUENCE_TO_DEV * self.personality.influence_cost_to_dev):
            tile = random.choice(self.tilesToDev)
            # either develop tile if it's controlled by us
            if self.isNationController(tile, tilesByNation):
                devToAdd = 1 # 1 level of development, may change later according to AI personality
                if tile.can_develop(devToAdd) and self.influence > self.personality.influence_cost_to_dev: # 1 level of development
                    self.addDevToTile(devToAdd, tile)
                    self.actions -= 1
            elif self.getControllerId(tile, tilesByNation) != 0:
                # an AI shouldn't develop another nation's tile, so we'll delete the tile from the list
                self.tilesToDev.remove(tile)
            else: # if the tile is not ours and it's empty (neutral, id == 0) then we conquer it
                #self.personality.influence_cost_to_conquer = biggestVal * (len(controlledTiles) // 2) * self.personality.conquerPhaseBonus
                if self.influence > self.personality.influence_cost_to_conquer:
                    self.conquerTile(tile, tilesByNation, True)
        else: # no influence to develop our tiles
            pass 
    
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

    # will construct a building in one of our tiles
    def buildThings(self, controlledTiles, isMoneyGrowing, isInfluenceGrowing, numberOfBuildings):

        if controlledTiles:
            # so we don't repeat code
            def chooseTiles(n): # n is the number of tiles to choose
                i = len(controlledTiles) - 1
                shuffledTiles = random.sample(controlledTiles, i + 1)
                tilesToBuild = []
                randomTile = shuffledTiles[i]
                while n > 0:
                    while i >= 0 and (len(randomTile.buildings) >= MAX_BUILDINGS_PER_TILE or randomTile.population <= 0):
                        randomTile = shuffledTiles[i]
                        i -= 1
                    if i >= 0: tilesToBuild.append(randomTile)
                    n -= 1
                return tilesToBuild if tilesToBuild else None
            
            def missingMoney(building):
                if not (self.money > building.money_cost or building.money_cost <= 0):
                    return True
                return False

            def missingInfluence(building):
                if not (self.influence > building.influence_cost or building.influence_cost <= 0):
                    return True
                return False

            def buildOnTile(tile, building):
                if building.influence_cost > 0: # then it's a money building:
                    if not missingInfluence(building):
                        tile.buildings.append(building)
                        self.influence -= building.influence_cost
                        self.money -= building.money_cost
                        self.actions -= 1
                else: # influence building:
                    if not missingMoney(building):
                        tile.buildings.append(building)
                        self.influence -= building.influence_cost
                        self.money -= building.money_cost
                        self.actions -= 1
            
            tilesToBuild = chooseTiles(numberOfBuildings)
            buildings = []

            # We'll try to build 2 buildings, one for influence and another for money:

            # influence building
            if isMoneyGrowing: # we can spend on influence buildings
                buildings.append(self.chooseBuilding("i"))
            else:
                buildings.append(self.chooseBuilding("m"))

            # money building
            if isInfluenceGrowing: # we can spend on money buildings
                buildings.append(self.chooseBuilding("m"))
            else:
                buildings.append(self.chooseBuilding("i"))

            # and now build them
            for i in range(numberOfBuildings):
                if buildings[i] is not None and tilesToBuild and self.actions > 0:
                    buildOnTile(tilesToBuild[i], buildings[i])

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
                    if randomTile.terrain.name in uncontrollable_terrains:
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
                    itsNeighbours = randomTile.get_neighbours(tiles, len(tiles[0]), len(tiles))
                    for n in itsNeighbours:
                        # it can only expand to uncontrolled tiles
                        if self.find(tilesByNation, n.coords) == 0: #and self.personality.phase != "aggressively-expanding": # Uncontrolled
                            devTiles.append(n)

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
            #if not self.isNationController(tile, tilesByNation) and self.getControllerId(tile, tilesByNation) != 0:
            if self.getControllerId(tile, tilesByNation) != 0:
                self.tilesToDev.remove(tile)

    # removes this nation from the game if it controlls no tiles (i.e. they were conquered)
    def checkExistence(self, nations, tiles, tilesByNation, controlledTiles):
        if len(controlledTiles) <= 0:
            print(f"{self.name} with id {self.id} was deleted because it had no tiles")
            #nations.remove(self) # doesn't work
            self.wasEliminated = True
            self.disband(self, tiles, tilesByNation)

    # makes a turn for this AI, called each turn for each AI/nation
    def makeTurn(self, tiles, nations, tilesByNation, turn):
        if self.id != 0 and not self.wasEliminated:
            # updating and defining basic variables
            controlledTiles = self.getTiles(tilesByNation, tiles) #self.getTilesByCoords(self.getControlledTiles(tilesByNation), tiles) # list of tiles, NOT their coords
            numBuildings, totalInfluenceBonus, totalMaintenance, totalValue, averageValue, biggestVal, totalPopulation = self.getData(tiles, controlledTiles, tilesByNation, turn)
            self.updateSize(controlledTiles)
            self.updateActions(controlledTiles)
            self.updatemax_wars(controlledTiles)
            self.numBuildings = numBuildings
            isMoneyGrowing = self.updateMoney(totalPopulation, totalMaintenance[0]) # updating our money and checking if it's growing or not
            isInfluenceGrowing = self.updateInfluence(totalMaintenance[1], totalInfluenceBonus) # updating our influence and checking if it's growing or not
            
            # debug prints:
            printArrowMoney = "↓" # just for the print
            printArrowInf = "↓" # just for the print
            if isMoneyGrowing:
                printArrowMoney = "↑"
            if isInfluenceGrowing:
                printArrowInf  = "↑"
            print(f"num tiles: {len(controlledTiles)} | money {round(self.money)} {printArrowMoney} | inf {round(self.influence)} {printArrowInf} | wars {len(self.wars)}({self.max_wars}) | ", end = "")

            # ------ THINGS THAT CONSUME ACTION POINTS

            # first check if we don't have enemy tiles in our tiles to dev
            # idk why but without this weird function I made countries won't conquer other tiles
            # they will still develop their tiles, even though the function removes owned tiles from the list
            self.checkTilesToDev(tilesByNation)

            didSomething = True

            while self.actions > 0 and didSomething:
                beforeActions = self.actions # update "beforeActions" so we always know each loop if the AI did something or not

                # update and develop our tilesToDev
                self.developTiles(tiles, controlledTiles, tilesByNation, isInfluenceGrowing) # consumes influence

                # try to build something on our tiles
                self.buildThings(controlledTiles, isMoneyGrowing, isInfluenceGrowing, BUILDINGS_PER_ACTION)

                # attack nearby neighbour tiles from our enemies
                self.makeAttack(tiles, nations, tilesByNation, controlledTiles, isMoneyGrowing)

                didSomething = True if self.actions != beforeActions else False
            print(f"actions: {self.actions}({self.maxActions}) | ", end = "")

            # ------ AND THAT DON'T CONSUME ACTION POINTS

            # update our tiles resources, pops, etc
            self.updateTiles(controlledTiles)

            # personality update, includes changing the phase and other stats realted to it
            self.updatePersonality()

            # declares wars on neighbours and tries to conquer their tiles
            self.updateStance(tiles, nations, tilesByNation, controlledTiles, isMoneyGrowing)

            # updates our capital (in case we lost ours)
            self.updateCapital(controlledTiles, tilesByNation)

            # Some of the resources will "rot" every turn, so nations don't accumulate infinite resources
            self.rotResources(self.rotPercentage)

            # update our leader stats/age
            self.leader = self.leader.update()

            # update our tech level
            self.updateTech(averageValue, totalValue, numBuildings, controlledTiles, turn, nations)
            print(f"dev: {self.countryDev} | tech: {self.techLevel} | ", end = "")

            # check if the nation is still in the game
            self.checkExistence(nations, tiles, tilesByNation, controlledTiles)

    # I have to copy these functions to this class because I can't import Engine
    # There surely is a better way to do this
    # returns the id of the nation that controls the tile with the passed coords
    def find(self, tilesByNation, tileCoords):
        return tilesByNation[tileCoords]

    # returns the nation with a certain id
    def getNation(self, nations, id):
        if nations[id].id == id:
            return nations[id]
        else:
            for n in nations:
                if n.id == id:
                    return n
        print("Error, nation isn't on the nations list")
        return -1

    # returns True if this nations controls the passed tile
    def isNationController(self, tile, tilesByNation):
        if self.id == self.find(tilesByNation, tile.coords):
            return True
        return False

    # returns the id of the nation that controls a certain tile
    def getControllerId(self, tile, tilesByNation):
        return self.find(tilesByNation, tile.coords)
    
    # conquers a tile for this nation by changing the tilesByNation found in Engine.py
    def changeTileOwnership(self, tile, tilesByNation):
        tilesByNation[tile.coords] = self.id

    # generates a random color, mostly used when creating new nations
    def genRandomColor():
        # color will only go to 230 here so it doesnt conflict with the white selectedColor.
        # if that one is changed, then I guess we can change this one
        c = (random.randint(0, 230), random.randint(0, 230), random.randint(0, 230))
        while (c[0] == c[1] or c[0] == c[2] or c[1] == c[2]): # I don't want 3 equal colors
            c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return c

    # returns a new random nation
    def getNewNation(id):
        nationName = Nation.genNationName()
        leader = Character.get_random_character()
        color = Nation.genRandomColor()
        modifiers = []
        wars = []
        persona = random.choice(SIMPLE_PERSONALITIES)
        n = Nation(id, color, nationName, leader, modifiers, wars, persona)
        return n

    # returns a random name in the form of a string for a nation
    def genNationName():
        names = []
        name = "ahh"
        with open(KINGDOM_NAMES_FILE, "r") as file:
            names = file.readlines()
        while len(name) < 4: # just to avoid empty lines
            name = random.choice(names)
        
        # to make the first char upperCase and remove a weird last char
        name = name[0].upper() + name[1:(-1)]
        #print(f"\nChosen Name:{name}\n")

        return name

# The "nation" that represents unclaimed land
emptyNation = Nation(0,BARBARIANS_COLOR2, "", Character("", 0, "", 0, 0, 0), [], [], random.choice(SIMPLE_PERSONALITIES))
