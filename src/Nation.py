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
        self.focused_tiles = [] # list of tiles to make an attack on, so countries don't grow in random shapes
        self.capital = None # contains the tile this country was first created in
        self.attack_center = None # a tile from where attacks will "center" so countries don't just become round blobs
        self.turns_with_no_change_in_attack_center = 0 # number of turns our tile in self.attack_center hasn't changed

        self.last_influence = 0 # to track if the ifluence is growing or not
        self.influence = 5 # current influence amount

        self.tech_level = 0 # max 10
        self.country_dev = 1 # testing purposes to decide our tech level

        self.last_money = 0
        self.money = 5 # available money for this nation

        self.actions = 2 # number of things this nation can do per turn
        self.max_actions = 2 # copy of self.actions to use after the actions are consumed

        self.num_buildings = 0 # to make it easier to print on the console

        #self.units = [] # probably won't use this

        self.war_influence_cost = 0 # cost in influence for maintaining a war

        self.neighbour_tiles = [] # all the tiles adjacent to our nation that don't belong to us

        self.techs = [] # idk if I'll use this

        self.was_eliminated = False

        self.personality = personality
        self.tiles_to_dev = []
        self.turns_no_expand = 0
        self.rot_percentage = BASE_ROT_PERCENTAGE - (self.tech_level * 2)

        self.size = 1

        self.representation = "Uncontrolled" if name == "" else f"{self.name}"

    # sets this nation's capital as the tile passed
    def set_capital(self, tile):
        self.capital = tile
        self.attack_center = tile

    # updates our current capital if it's not controlledByUs
    def update_capital(self, controlled_tiles, tiles_by_nation):
        changed_capital = False
        if not self.is_nation_controller(self.capital, tiles_by_nation) and controlled_tiles:
            random_tiles = random.sample(controlled_tiles, len(controlled_tiles))
            for tile in random_tiles:
                if tile.terrain.name not in no_beginning_terrains:
                    changed_capital = True
                    break
            self.set_capital(tile)
            return changed_capital

    # prints the coords of a list of given tiles controlled by a nation
    def print_tiles(self, tiles):
        #values = "Tiles to Develop: "
        values = ""
        if tiles:
            for tile in tiles:
                values += f"{tile.coords} "
        return values

    # writes all tiles resources on a string and returns it
    def resources_to_string(self):
        values = "Production: "
        for r in self.resources:
            values += f"{r[0].upper()}:{self.resources[r]} "
        return values

    # returns the coords of all controlled tiles by this nation, given the tiles_by_nation found on Engine.py
    def get_controlled_tiles(self, tiles_by_nation):
        coords = []
        for coord in tiles_by_nation:
            if tiles_by_nation[coord] == self.id:
                coords.append(coord)
        return coords

    # returns all controlled tiles (not their coords) given a list of coords and a list of tiles 
    def get_tiles_by_coords(self, coords, tiles):
        ctrl = []
        for coord in coords:
            ctrl.append(tiles[coord[1]][coord[0]]) # first y, then x (but why? i dont remember why i made it like this)
        return ctrl

    # returns the tile at the passed coords
    def get_tile_by_coords(self, coords, tiles):
        return tiles[coords[1]][coords[0]] # first y, then x (but why? i dont remember why i made it like this)

    # return all tiles this nation controls
    def get_tiles(self, tiles_by_nation, tiles):
        ctrl = []
        for coord in tiles_by_nation:
            if tiles_by_nation[coord] == self.id:
                ctrl.append(tiles[coord[1]][coord[0]])
        return ctrl

    # adds resources to a nation's available resources, given a dictionary of resources
    def add_resources(self, rs):
        for r in rs:
            self.resources[r] += rs[r]
    
    # decreases a certain percentage of resources of this nation's stockpile, usually called each turn
    def rot_resources(self, percentage):
        for r in self.resources:
            percentage -= self.leader.prosperity # more prosperity, more resources
            self.resources[r] = round(self.resources[r] * ((100-percentage) / 100))

    # returns the total maintenance value of all our wars, in money 
    def get_war_maintenance(self):
        maintenance = 0
        for war in self.wars:
            maintenance += war[1]
        return maintenance

    # returns all neighbours of a tile that belong to an enemy nation
    def get_enemy_neighbours(self, tiles, tiles_by_nation, nations):
        enemy_neighbours = []
        self.focused_tiles = []

        # get the ids of the nations we are at war with
        ids = []
        for war in self.wars:
            ids.append(war[0].id)

        # then check if the tiles belong to any of them
        for n in self.neighbour_tiles:
            neighbour_nation_id = self.get_controller_id(n, tiles_by_nation)
            if neighbour_nation_id in ids: # small check in case some nations lose and keep territory
                enemy_neighbours.append(n)
                #enemy_tile_neighbours = n.get_neighbours(tiles, len(tiles[0]), len(tiles))
                
                # checking if the tile is an enclave inside this nation's territory
                # though I dislike having all of these loops :(
                # and I'm not sure if this even works
                is_enclave = True
                for t in enemy_neighbours:
                    if not self.is_nation_controller(t, tiles_by_nation):
                        is_enclave = False
                        break
                if is_enclave:
                    self.focused_tiles.append(n)

        return enemy_neighbours

    # returns total maintenance, the total value, the average value, the biggest population and the average population in our controlled tiles
    # this was made like this to avoid looping several times, this way we loop only one and get all the data we need
    def get_data(self, tiles, controlled_tiles, tiles_by_nation, turn):
        total_influence = 0
        maintenance = [0,0]
        average = 0
        total_value = 0
        biggest = 0
        pop = 0
        num_buildings = 0
        self.neighbour_tiles = [] # emptying the neighbour tiles so it doesn't accumulate infinitely
        for tile in controlled_tiles:

            # since we are looping through all tiles we will take this chance to fill this
            neighbours = tile.get_neighbours(tiles, len(tiles[0]), len(tiles))
            for n in neighbours:
                if not self.is_nation_controller(n, tiles_by_nation): # this if increases performance by a LOT
                    if n not in self.neighbour_tiles:
                        self.neighbour_tiles.append(n)
            
            tile_maintenance = tile.get_maintenance() # temp variable

            num_buildings += tile.get_num_buildings()
            total_influence += tile.get_influence()
            maintenance[0] += tile_maintenance[0]
            maintenance[1] += tile_maintenance[1]
            total_value += tile.value
            pop += tile.population
            if tile.value > biggest:
                biggest = tile.value
        maintenance[0] += self.get_war_maintenance() # war maintenance added to total money maintenance
        average = 0 if len(controlled_tiles) == 0 else round(total_value / len(controlled_tiles), 2)
        total_influence *= TECH_BONUS[self.tech_level] # the higher the tech, the better the bonus on influence gain
        return (num_buildings, total_influence, maintenance, total_value, average, biggest, pop)

    # returns our leader's influence bonus, will be added each turn to our nation
    def get_leader_influence_bonus(self):
        return self.leader.prosperity

    # develops all our inhabitated tiles and updates our resources
    def update_tiles(self, controlled_tiles):
        for tile in controlled_tiles:
            if tile.population > 0: # develop only inhabitated tiles
                # these 3 are necessary, don't remove them
                tile.set_production()
                tile.develop()
                self.add_resources(tile.get_leftovers())
    
    # see if we can change our personality's phase and other stats
    def update_personality(self):
        if self.turns_no_expand > TURNS_TO_EXPAND:
            self.personality.phase = "peacefully-expanding"
        if self.personality.phase != "aggressively-expanding":
            prob = random.randint(0,100)
            if prob < PROBABILITY_AGGRESSIVE_EXPANSION:
                self.personality.phase = "aggressively-expanding"

        self.personality.update_values()

    # updates our size and the number of turns without changing our size
    def update_size(self, controlled_tiles):
        if self.size != len(controlled_tiles):
            self.size = len(controlled_tiles)
            self.turns_no_expand = 0
        else:
            self.turns_no_expand += 1

    # udpates the current amount of money this nation has
    def update_money(self, total_population, total_maintenance):
        self.last_money = self.money
        self.money += total_population * TAX_BY_POP
        self.money -= total_maintenance
        self.money = round(self.money, 3)
        return True if self.money - self.last_money > 0 else False # returns if our money is growing or not

    # updates the current amount of influence this nation has
    def update_influence(self, total_maintenance, tile_bonus):
        self.last_influence = self.influence
        self.influence += BASE_INFLUENCE_PER_TURN # basic bonus
        self.influence += self.get_leader_influence_bonus() # leader bonus
        self.influence += tile_bonus
        self.influence -= total_maintenance # maintenance of our territory
        self.influence -= self.war_influence_cost
        self.influence = round(self.influence, 2)
        influence_dif = self.influence - self.last_influence
        return True if influence_dif > 0 else False # returns True if the influence is growing, False if not

    # returns a list with the country_dev level of all nations that are still playing
    def get_nations_devs(self, nations):
        list = []
        for nation in nations:
            if not nation.was_eliminated and nation.country_dev != 0 and self.country_dev > COUNTRY_DEV_STABILIZER:
                list.append(nation.country_dev)
        return list

    # updates our current tech level according to the total number of buildings in our nation
    def update_tech(self, average_value, total_value, num_buildings, controlled_tiles, turn, nations):

        # determine our country development. will be used to determine our tech level
        if turn > 1 and controlled_tiles:
            multiplier = (average_value * self.max_actions * self.size)
            if multiplier != 0:
                self.country_dev = ((total_value + num_buildings) / multiplier) + COUNTRY_DEV_STABILIZER
            else:
                self.country_dev = COUNTRY_DEV_STABILIZER
            self.country_dev = round(self.country_dev, 4)

            dev_list = self.get_nations_devs(nations) # to sort by the second element of the tuple, the indice
            new_tech_level = self.tech_level
            if dev_list: # if it's not empty
                min_d = min(dev_list)
                max_d = max(dev_list)
                dif = (max_d - min_d) / MAX_TECH_LEVEL 
                new_tech_level = 0
                while min_d <= self.country_dev and self.tech_level < MAX_TECH_LEVEL and min_d > 0.1:
                    min_d += dif
                    new_tech_level += 1

            # increase our tech level slowly
            if new_tech_level > self.tech_level:
                self.tech_level += 1
            elif new_tech_level < self.tech_level:
                self.tech_level -= 1

    # conquers a tile for this nation; consumes influence
    def conquer_tile(self, tile, tiles_by_nation, consumes_action):
        self.change_tile_ownership(tile, tiles_by_nation)
        self.influence -= self.personality.influence_cost_to_conquer
        if consumes_action: self.actions -= 1 # consumes an action point

    # what happens to this nation if it fails to conquer a tile
    def lose_battle(self):
        tech_bonus = TECH_BONUS[self.tech_level]
        self.influence -= self.personality.influence_cost_to_conquer * tech_bonus

    # updates this nation's available actions according to our size
    def update_actions(self, controlled_tiles):
        num_tiles = len(controlled_tiles)
        self.actions = MIN_ACTIONS
        self.actions += (num_tiles//ACTIONS_STEP_VALUE) * ACTIONS_STEP
        self.max_actions = self.actions

    # algorithm that returns a value in money to be alocated to a war
    def return_new_war_budget(self, money_dif, nations, nation):
        if money_dif > WAR_MAINTENANCE_RANGE[1]:
            limit = WAR_MAINTENANCE_RANGE[1]
        else:
            limit = int(money_dif)
        
        prob = random.randint(1,10)
        if prob < 2:
            return random.randint(limit - 5, limit)
        elif prob <= 5:
            half_maintenance = int((limit - WAR_MAINTENANCE_RANGE[0]) / 2)
            return random.randint(half_maintenance, limit)
        else:
            return random.randint(WAR_MAINTENANCE_RANGE[0], limit)

    # returns this nation's war budget for a specific war against the given nation
    def get_war_budget(self, nation):
        for war in self.wars:
            if war[0].id == nation.id:
                return war[1]
        
        print("get_war_budget failed, probably this nation is not at war with the other nation that called it?")
        return -1 # if something is wrong
    
    # removes a war with a certain nation
    def remove_war(self, nation):
        for war in self.wars:
            n = war[0]
            if n == nation:
                self.wars.remove(war)
                return True
        print("remove_war failed, this nation is not at war with the passed nation")

    # ends a war with the passed nation
    def end_war(self, nation):
        self.remove_war(nation)
        nation.remove_war(self)

    # penalties this nation will take for losing a war against the passed nation
    def take_lost_war_penalties(self, nation):
        tech_bonus = TECH_BONUS[nation.tech_level]
        self.money -= WAR_MONEY_REWARD * tech_bonus
        nation.money += WAR_MONEY_REWARD * tech_bonus
        self.influence -= WAR_INFLUENCE_REWARD * tech_bonus
        nation.influence += WAR_INFLUENCE_REWARD * tech_bonus

    #TODO, take leader's personality into account after calculating this
    # update's our nations max number of possible concurrent wars. More than this and the nation will take heavy penalties
    def update_max_wars(self, controlled_tiles):
        num_tiles = len(controlled_tiles)
        self.max_wars = MIN_WARS
        self.max_wars += (num_tiles//WARS_STEP_VALUE) * WARS_STEP

    # what happens to the passed nation when its capital is conquered by this nation
    def conquered_capital(self, nation, tiles, tiles_by_nation):
        for tile_coords in tiles_by_nation: # key are the tile coords, value is the id of the owner
            if self.influence > (self.personality.influence_cost_to_conquer * TECH_BONUS[self.tech_level] * TECH_BONUS[nation.tech_level]):
                if tiles_by_nation[tile_coords] == nation.id:
                    self.change_tile_ownership(self.get_tile_by_coords(tile_coords, tiles), tiles_by_nation)
                    self.influence -= self.personality.influence_cost_to_conquer

    # return to monke
    def disband(self, nation, tiles, tiles_by_nation):
        for tile_coords in tiles_by_nation: # key are the tile coords, value is the id of the owner
            if tiles_by_nation[tile_coords] == nation.id:
                tiles_by_nation[tile_coords] = 0

    # determines the result of a battle between this nation and nation we are at war with in the passed war
    def do_battle(self, war):
        nation = war[0]
        attacker_rng = random.randint(1, MAX_BATTLE_RNG)
        defender_rng = random.randint(1, MAX_BATTLE_RNG)
        attacker_iron_per_capita = 0
        defender_iron_per_capita = 0
        if self.size > 0 and nation.size > 0: # having a lot of iron is important
            attacker_iron_per_capita = round((self.resources["iron"] / self.size) * 10)
            defender_iron_per_capita = round((nation.resources["iron"] / nation.size) * 10)
        our_chances = (war[1] + attacker_rng + attacker_iron_per_capita) + (TECH_BONUS[self.tech_level] * self.leader.martial)
        their_chances = (nation.get_war_budget(self) + defender_rng + defender_iron_per_capita) + (TECH_BONUS[nation.tech_level] * nation.leader.martial)
        wins_battle = our_chances > their_chances
        return wins_battle

    # tries to conquer an enemy tile if we are at war with someone
    def make_attack(self, tiles, nations, tiles_by_nation, controlled_tiles, is_money_growing):
        num_wars = len(self.wars)
        if num_wars > 0:
            enemy_tiles = self.get_enemy_neighbours(tiles, tiles_by_nation, nations)
            
            # will select some random Tiles from our enemies and select the closest to the capital
            # to avoid conquering tiles that are too far away from the main territory and avoid enclaves
            def choose_tile(n):
                dist_list = []
                for i in range(n):
                    tile_to_conquer = random.choice(enemy_tiles)
                    distance_to_attack_center = sqrt((tile_to_conquer.x - self.attack_center.x)**2 + (tile_to_conquer.y - self.attack_center.y)**2) # distance formula
                    dist_list.append((distance_to_attack_center, tile_to_conquer))
                dist_list.sort(key=lambda x:x[0]) # sort by distance to the capital
                return dist_list[0][1] # return the closest to the capital
            
            if enemy_tiles:
                # choosing a random tile to attack
                if self.focused_tiles: # if there are enclaves inside our territory or important tiles we need to conquer:
                    if not self.is_nation_controller(self.focused_tiles[0], tiles_by_nation):
                        tile_to_conquer = self.focused_tiles[0]
                    else:
                        self.focused_tiles.remove(self.focused_tiles[0])
                else: # if not, let's semi-randomly choose them
                    tile_to_conquer = choose_tile(CONQUER_ACCURACY) # number of tiles to choose from
                nation_id = self.get_controller_id(tile_to_conquer, tiles_by_nation)
                nation = self.get_nation(nations, nation_id)
                war = 0
                # finding the right nation and war
                for w in self.wars:
                    if w[0].id == nation_id:
                        nation = w[0]
                        war = w
                        break

                if nation.size <= 0: # just in case the nation doesn't exist anymore
                    self.end_war(nation)
                if self.influence > self.personality.influence_cost_to_conquer: # it will still cost influence tho
                    # leaders and technology are very important in battles too:
                    wins_battle = self.do_battle(war)
                    if wins_battle and nation.get_war_budget(self) != -1 and self.actions > 0:
                        self.conquer_tile(tile_to_conquer, tiles_by_nation, True)
                        if tile_to_conquer == nation.capital:
                            self.conquered_capital(nation, tiles, tiles_by_nation)
                    elif nation.get_war_budget(self) == -1: # to delete wars with nations that might be bugged?
                        self.end_war(nation)
                    else: # if it doesn't conquer this tile, it will still lose influence trying to attack it
                        self.lose_battle()
                #else:
                #    print("No influence to conquer tile!")
            else: # no adjacent enemy tile to conquer, make peace with everyone
                for war in self.wars:
                    self.end_war(war[0])
    
    # updates this nation's attack center and the turns required to change it
    def update_attack_center(self, tiles, tiles_by_nation, controlled_tiles):
        self.turns_with_no_change_in_attack_center += 1 # update this variable
        r = random.randint(1, 100)
        if r <= self.turns_with_no_change_in_attack_center * 2 or not self.is_nation_controller(self.attack_center, tiles_by_nation):
            if controlled_tiles:
                self.attack_center = random.choice(controlled_tiles)

    #TODO
    # updates wars and tries to conquer enemy tiles
    def update_stance(self, tiles, nations, tiles_by_nation, controlled_tiles, is_money_growing):
        
        self.update_attack_center(tiles, tiles_by_nation, controlled_tiles)
        
        money_dif = self.money - self.last_money
        num_wars = len(self.wars)
        num_tiles = len(controlled_tiles)

        # in case a nation has no tiles / was conquered:
        if num_tiles == 0: # make peace with everyone in case this nation has no tiles
            if num_wars > 0:
                for war in self.wars:
                    #self.end_war(war[0])
                    self.wars.remove(war)
            self.war_influence_cost = 0

        if num_wars == 0: # updating the influence maintenance on wars
            self.war_influence_cost = 0
        else:
            # the better the tech, the costly it is to maintain wars for longer periods of time
            # making this to avoid countries from getting too big
            self.war_influence_cost += (TECH_BONUS[self.tech_level] * WAR_INFLUENCE_MAINTENANCE_COST) * num_wars

        new_war = False # will be True if a new war is added, to avoid unnecessary looping
        # first we determine if we can declare war, and if so we see if we will do that
        if self.money > WAR_COST and money_dif > WAR_MAINTENANCE_RANGE[0] and num_wars < self.max_wars:
            prob = random.randint(1,100)
            will_declare_war = True if prob <= PROBABILITY_WAR_PER_TURN else False
            if will_declare_war:
                for tile in controlled_tiles:
                    for n in tile.get_neighbours(tiles, len(tiles[0]), len(tiles)):
                        neighbour_nation_id = self.get_controller_id(n, tiles_by_nation)
                        if neighbour_nation_id not in [self.id, 0]: # if True means it's a neighbour nation
                            #warNation = None
                            for nation in nations:
                                if nation.id == neighbour_nation_id and num_wars < self.max_wars:
                                    #warNation = nation
                                    self.wars.append([nation, self.return_new_war_budget(money_dif, nations, nation)])
                                    nation.wars.append([self, nation.return_new_war_budget(money_dif, nations, self)])
                                    new_war = True
                                    break
                        if new_war:
                            break
                    if new_war:
                        break
        
        # make peace with a random nation we are at war with
        if num_wars > 0 and not new_war: # if it's not empty, len(self.wars) > 0
            num_wars = len(self.wars)
            r = random.randint(1,100)
            if (num_wars > self.max_wars or self.influence < 0 or self.money < 0) and num_wars > 0:
                if r <= PROBABILITY_ENDING_WAR_MAX:
                    random_war = random.choice(self.wars)
                    self.end_war(random_war[0])
                    self.take_lost_war_penalties(random_war[0])
            elif num_wars > 0 and r <= PROBABILITY_ENDING_WAR:
                random_war = random.choice(self.wars)
                self.end_war(random_war[0])

    # adds development to the specified tile; consumes influence
    def add_dev_to_tile(self, dev_value, tile):
        tile.add_development(dev_value)
        self.influence -= self.personality.influence_cost_to_dev

    # will develop one of our tiles_to_dev at the cost of influence
    def develop_tiles(self, tiles, controlled_tiles, tiles_by_nation, is_influence_growing):
        if not self.tiles_to_dev:
            self.tiles_to_dev = self.get_dev_tiles(tiles, tiles_by_nation, controlled_tiles)
        elif is_influence_growing or self.influence > (SAFE_INFLUENCE_TO_DEV * self.personality.influence_cost_to_dev):
            tile = random.choice(self.tiles_to_dev)
            # either develop tile if it's controlled by us
            if self.is_nation_controller(tile, tiles_by_nation):
                dev_to_add = 1 # 1 level of development, may change later according to AI personality
                if tile.can_develop(dev_to_add) and self.influence > self.personality.influence_cost_to_dev: # 1 level of development
                    self.add_dev_to_tile(dev_to_add, tile)
                    self.actions -= 1
            elif self.get_controller_id(tile, tiles_by_nation) != 0:
                # an AI shouldn't develop another nation's tile, so we'll delete the tile from the list
                self.tiles_to_dev.remove(tile)
            else: # if the tile is not ours and it's empty (neutral, id == 0) then we conquer it
                #self.personality.influence_cost_to_conquer = biggest_val * (len(controlled_tiles) // 2) * self.personality.conquerPhaseBonus
                if self.influence > self.personality.influence_cost_to_conquer:
                    self.conquer_tile(tile, tiles_by_nation, True)
        else: # no influence to develop our tiles
            pass 
    
    # returns a building depending on the code passed and the available money and influence this nation has
    # returns None if it didn't find any building
    def choose_building(self, code):
        if code == "i": # influence building
            if self.money >= BASE_BUILDING_MONEY_COST:
                return random.choice(L1_INFLUENCE_BUILDINGS)
        elif code == "m": # money building
            if self.influence >= BASE_BUILDING_INFLUENCE_COST:
                return random.choice(L1_MONEY_BUILDINGS)
        return None # if we end up not choosing any building

    # will construct a building in one of our tiles
    def build_things(self, controlled_tiles, is_money_growing, is_influence_growing, number_of_buildings):

        if controlled_tiles:
            # so we don't repeat code
            def choose_tiles(n): # n is the number of tiles to choose
                i = len(controlled_tiles) - 1
                shuffled_tiles = random.sample(controlled_tiles, i + 1)
                tiles_to_build = []
                random_tile = shuffled_tiles[i]
                while n > 0:
                    while i >= 0 and (len(random_tile.buildings) >= MAX_BUILDINGS_PER_TILE or random_tile.population <= 0):
                        random_tile = shuffled_tiles[i]
                        i -= 1
                    if i >= 0: tiles_to_build.append(random_tile)
                    n -= 1
                return tiles_to_build if tiles_to_build else None
            
            def missing_money(building):
                if not (self.money > building.money_cost or building.money_cost <= 0):
                    return True
                return False

            def missing_influence(building):
                if not (self.influence > building.influence_cost or building.influence_cost <= 0):
                    return True
                return False

            def build_on_tile(tile, building):
                if building.influence_cost > 0: # then it's a money building:
                    if not missing_influence(building):
                        tile.buildings.append(building)
                        self.influence -= building.influence_cost
                        self.money -= building.money_cost
                        self.actions -= 1
                else: # influence building:
                    if not missing_money(building):
                        tile.buildings.append(building)
                        self.influence -= building.influence_cost
                        self.money -= building.money_cost
                        self.actions -= 1
            
            tiles_to_build = choose_tiles(number_of_buildings)
            buildings = []

            # We'll try to build 2 buildings, one for influence and another for money:

            # influence building
            if is_money_growing: # we can spend on influence buildings
                buildings.append(self.choose_building("i"))
            else:
                buildings.append(self.choose_building("m"))

            # money building
            if is_influence_growing: # we can spend on money buildings
                buildings.append(self.choose_building("m"))
            else:
                buildings.append(self.choose_building("i"))

            # and now build them
            for i in range(number_of_buildings):
                if buildings[i] is not None and tiles_to_build and self.actions > 0:
                    build_on_tile(tiles_to_build[i], buildings[i])

    # TODO
    # returns a list of tiles to be developed for this nation (NOT their coords)
    # I want each AI to have different strategies and different dev_tiles
    # Maybe I should put this function on a separate file inside data or something 
    # and let each personality import it's own get_dev_tiles() function
    def get_dev_tiles(self, tiles, tiles_by_nation, controlled_tiles):
        dev_tiles = []
        if self.personality.name == "basic":
            # weird algorithm i made
            tries = 0
            while not dev_tiles and (tries < MAX_DEV_TRIES or tries < len(controlled_tiles) // 2):
                if len(controlled_tiles) > 0:
                    random_tile = random.choice(controlled_tiles) # first we choose a random controlled tile

                    # avoid expanding into these tiles
                    if random_tile.terrain.name in uncontrollable_terrains:
                        tries += 1
                        continue

                    # now according to the AI's personality, we make it a tile to develop or not
                    prob = random.randint(1,100)
                    if self.personality.phase == "aggressively-expanding":
                        if prob <= PROBABILITY_AGGR_EXP_DEV_TILE:
                            dev_tiles.append(random_tile)
                            break
                        else:
                            tries -= 0.1 # maybe it's too low?
                    # since it's "peacefully-expanding", it will just develop a random owned tile
                    # the more tiles it has, bigger the chance to develop a tile
                    elif self.personality.phase == "peacefully-expanding":
                        if prob <= PROBABILITY_PEACE_EXP_DEV_TILE:
                            dev_tiles.append(random_tile)
                            break
                    elif self.personality.phase == "developing":
                        if prob <= PROBABILITY_DEVELOPING_DEV_TILE:
                            dev_tiles.append(random_tile)
                            break
                    
                    # then we pick it's neighbours
                    its_neighbours = random_tile.get_neighbours(tiles, len(tiles[0]), len(tiles))
                    for n in its_neighbours:
                        # it can only expand to uncontrolled tiles
                        if self.find(tiles_by_nation, n.coords) == 0: #and self.personality.phase != "aggressively-expanding": # Uncontrolled
                            dev_tiles.append(n)

                else:
                    # If they do not control any tile then that means they were conquered, so they shouldn't get into this loop
                    print(f"\n{self.name} with id {self.id} has no tiles!!! Something went wrong! Controlled Tiles: {self.get_controlled_tiles(tiles_by_nation)}")
                    break

                tries += 1
        else:
            print(f"\nIf this nation's personality isn't basic, then what is it?! Name: {self.name}, id: {self.id}")
        return dev_tiles

    # given the tiles_by_nation found in Engine.py, checks if all the tiles to be developed are controlled by this nation.
    def check_tiles_to_dev(self, tiles_by_nation):
        for tile in self.tiles_to_dev:
            #if not self.is_nation_controller(tile, tiles_by_nation) and self.get_controller_id(tile, tiles_by_nation) != 0:
            if self.get_controller_id(tile, tiles_by_nation) != 0:
                self.tiles_to_dev.remove(tile)

    # removes this nation from the game if it controlls no tiles (i.e. they were conquered)
    def check_existence(self, nations, tiles, tiles_by_nation, controlled_tiles):
        if len(controlled_tiles) <= 0:
            print(f"{self.name} with id {self.id} was deleted because it had no tiles")
            #nations.remove(self) # doesn't work
            self.was_eliminated = True
            self.disband(self, tiles, tiles_by_nation)

    # makes a turn for this AI, called each turn for each AI/nation
    def make_turn(self, tiles, nations, tiles_by_nation, turn):
        if self.id != 0 and not self.was_eliminated:
            # updating and defining basic variables
            controlled_tiles = self.get_tiles(tiles_by_nation, tiles) #self.get_tiles_by_coords(self.get_controlled_tiles(tiles_by_nation), tiles) # list of tiles, NOT their coords
            num_buildings, total_influence_bonus, total_maintenance, total_value, average_value, biggest_val, total_population = self.get_data(tiles, controlled_tiles, tiles_by_nation, turn)
            self.update_size(controlled_tiles)
            self.update_actions(controlled_tiles)
            self.update_max_wars(controlled_tiles)
            self.num_buildings = num_buildings
            is_money_growing = self.update_money(total_population, total_maintenance[0]) # updating our money and checking if it's growing or not
            is_influence_growing = self.update_influence(total_maintenance[1], total_influence_bonus) # updating our influence and checking if it's growing or not
            
            # debug prints:
            print_arrow_money = "↓" # just for the print
            print_arrow_inf = "↓" # just for the print
            if is_money_growing:
                print_arrow_money = "↑"
            if is_influence_growing:
                print_arrow_inf  = "↑"
            print(f"num tiles: {len(controlled_tiles)} | money {round(self.money)} {print_arrow_money} | inf {round(self.influence)} {print_arrow_inf} | wars {len(self.wars)}({self.max_wars}) | ", end = "")

            # ------ THINGS THAT CONSUME ACTION POINTS

            # first check if we don't have enemy tiles in our tiles to dev
            # idk why but without this weird function I made countries won't conquer other tiles
            # they will still develop their tiles, even though the function removes owned tiles from the list
            self.check_tiles_to_dev(tiles_by_nation)

            did_something = True

            while self.actions > 0 and did_something:
                before_actions = self.actions # update "before_actions" so we always know each loop if the AI did something or not

                # update and develop our tiles_to_dev
                self.develop_tiles(tiles, controlled_tiles, tiles_by_nation, is_influence_growing) # consumes influence

                # try to build something on our tiles
                self.build_things(controlled_tiles, is_money_growing, is_influence_growing, BUILDINGS_PER_ACTION)

                # attack nearby neighbour tiles from our enemies
                self.make_attack(tiles, nations, tiles_by_nation, controlled_tiles, is_money_growing)

                did_something = True if self.actions != before_actions else False
            print(f"actions: {self.actions}({self.max_actions}) | ", end = "")

            # ------ AND THAT DON'T CONSUME ACTION POINTS

            # update our tiles resources, pops, etc
            self.update_tiles(controlled_tiles)

            # personality update, includes changing the phase and other stats realted to it
            self.update_personality()

            # declares wars on neighbours and tries to conquer their tiles
            self.update_stance(tiles, nations, tiles_by_nation, controlled_tiles, is_money_growing)

            # updates our capital (in case we lost ours)
            self.update_capital(controlled_tiles, tiles_by_nation)

            # Some of the resources will "rot" every turn, so nations don't accumulate infinite resources
            self.rot_resources(self.rot_percentage)

            # update our leader stats/age
            self.leader = self.leader.update()

            # update our tech level
            self.update_tech(average_value, total_value, num_buildings, controlled_tiles, turn, nations)
            print(f"dev: {self.country_dev} | tech: {self.tech_level} | ", end = "")

            # check if the nation is still in the game
            self.check_existence(nations, tiles, tiles_by_nation, controlled_tiles)

    # I have to copy these functions to this class because I can't import Engine
    # There surely is a better way to do this
    # returns the id of the nation that controls the tile with the passed coords
    def find(self, tiles_by_nation, tile_coords):
        return tiles_by_nation[tile_coords]

    # returns the nation with a certain id
    def get_nation(self, nations, id):
        if nations[id].id == id:
            return nations[id]
        else:
            for n in nations:
                if n.id == id:
                    return n
        print("Error, nation isn't on the nations list")
        return -1

    # returns True if this nations controls the passed tile
    def is_nation_controller(self, tile, tiles_by_nation):
        if self.id == self.find(tiles_by_nation, tile.coords):
            return True
        return False

    # returns the id of the nation that controls a certain tile
    def get_controller_id(self, tile, tiles_by_nation):
        return self.find(tiles_by_nation, tile.coords)
    
    # conquers a tile for this nation by changing the tiles_by_nation found in Engine.py
    def change_tile_ownership(self, tile, tiles_by_nation):
        tiles_by_nation[tile.coords] = self.id

    # generates a random color, mostly used when creating new nations
    @staticmethod
    def gen_random_color():
        # color will only go to 230 here so it doesnt conflict with the white selectedColor.
        # if that one is changed, then I guess we can change this one
        c = (random.randint(0, 230), random.randint(0, 230), random.randint(0, 230))
        while (c[0] == c[1] or c[0] == c[2] or c[1] == c[2]): # I don't want 3 equal colors
            c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return c

    # returns a new random nation
    @staticmethod
    def get_new_nation(id):
        nation_name = Nation.gen_nation_name()
        leader = Character.get_random_character()
        color = Nation.gen_random_color()
        modifiers = []
        wars = []
        persona = random.choice(SIMPLE_PERSONALITIES)
        n = Nation(id, color, nation_name, leader, modifiers, wars, persona)
        return n

    # returns a random name in the form of a string for a nation
    @staticmethod
    def gen_nation_name():
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
empty_nation = Nation(0,BARBARIANS_COLOR2, "", Character("", 0, "", 0, 0, 0), [], [], random.choice(SIMPLE_PERSONALITIES))
