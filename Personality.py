from Terrain import *
import random


class Personality:
    def __init__(self, name, phase, influenceCostToConquer, conquerPhaseBonus):
        self.name = name
        self.phase = phase # basically what they are doing now
        self.influenceCostToConquer = influenceCostToConquer
        self.conquerPhaseBonusBase = conquerPhaseBonus
        self.conquerPhaseBonus = self.updateConquerPhaseBonus()
    
    def updateConquerPhaseBonus(self):
        return self.conquerPhaseBonusBase if self.phase == "aggressively-expanding" else 1

SIMPLE_PERSONALITIES = [
    Personality("basic", random.choice(["peacefully-expanding", "aggressively-expanding", "developing"]), 0, 0.1),
]
