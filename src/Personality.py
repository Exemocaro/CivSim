from Terrain import *
from Settings import *
import random


class Personality:
    def __init__(self, name, phase, influence_cost_to_dev, influence_cost_to_conquer):
        self.name = name
        self.phase = phase # basically what they are doing now
        self.influence_cost_to_conquer = influence_cost_to_conquer
        self.influence_cost_to_dev = influence_cost_to_dev

        self.max_wars = 0

        self.update_values()
    
    # I need to organize these in a dict
    # updates the cost of influence to conquer a new tile
    def update_influence_to_conquer(self):
        if self.phase == "aggressively-expanding":
            self.influence_cost_to_conquer =  round(BASE_CONQUER_COST / 2, 2)
        elif self.phase == "peacefully-expanding":
            self.influence_cost_to_conquer =  round(BASE_CONQUER_COST)
        elif self.phase == "developing":
            self.influence_cost_to_conquer =  round(BASE_CONQUER_COST * 2)
    
    # updates the cost of influence to develop a tile of the AI's nation
    def update_influence_to_dev(self):
        if self.phase == "developing":
            self.influence_cost_to_dev =  round(BASE_DEV_COST / 2, 2)
        elif self.phase == "peacefully-expanding":
            self.influence_cost_to_dev =  round(BASE_DEV_COST)
        elif self.phase == "aggressively-expanding":
            self.influence_cost_to_dev =  round(BASE_DEV_COST * 2)

    # updates the maximum number of wars this nation can be at war with
    #def updatemax_wars(self):
    #    if self.phase == "developing":
    #        self.max_wars =  round(MIN_WARS / 2, 2)
    #    elif self.phase == "peacefully-expanding":
    #        self.max_wars =  round(MIN_WARS)
    #    elif self.phase == "aggressively-expanding":
    #        self.max_wars =  round(MIN_WARS * 2)

    # giving intial values to the variables on our AI
    def update_values(self):
        self.update_influence_to_dev()
        self.update_influence_to_conquer()
        #self.updatemax_wars()

# the values passed to dev and to conquer don't really matter as they are dinamically updated
SIMPLE_PERSONALITIES = [
    Personality("basic", random.choice(["peacefully-expanding", "aggressively-expanding", "developing"]), BASE_DEV_COST, BASE_CONQUER_COST),
]
