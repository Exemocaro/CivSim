from Terrain import *
from Settings import *
import random


class Personality:
    def __init__(self, name, phase, influenceCostToDev, influenceCostToConquer):
        self.name = name
        self.phase = phase # basically what they are doing now
        self.influenceCostToConquer = influenceCostToConquer
        self.influenceCostToDev = influenceCostToDev

        self.initialSetup()
    
    # I need to organize these in a dict
    # updates the cost of influence to conquer a new tile
    def updateInfluenceToConquer(self):
        if self.phase == "aggressively-expanding":
            self.influenceCostToConquer =  round(BASE_CONQUER_COST / 2, 2)
        elif self.phase == "peacefully-expanding":
            self.influenceCostToConquer =  round(BASE_CONQUER_COST)
        elif self.phase == "developing":
            self.influenceCostToConquer =  round(BASE_CONQUER_COST * 2)
    
    # updates the cost of influence to develop a tile of the AI's nation
    def updateInfluenceToDev(self):
        if self.phase == "developing":
            self.influenceCostToDev =  round(BASE_DEV_COST / 2, 2)
        elif self.phase == "peacefully-expanding":
            self.influenceCostToDev =  round(BASE_DEV_COST)
        elif self.phase == "aggressively-expanding":
            self.influenceCostToDev =  round(BASE_DEV_COST * 2)

    # giving intial values to the variables on our AI
    def initialSetup(self):
        self.updateInfluenceToDev()
        self.updateInfluenceToConquer()

# the values passed to dev and to conquer don't really matter as they are dinamically updated
SIMPLE_PERSONALITIES = [
    Personality("basic", random.choice(["peacefully-expanding", "aggressively-expanding", "developing"]), BASE_DEV_COST, BASE_CONQUER_COST),
]
