from Terrain import *
import random


class Personality:
    def __init__(self, name, phase, influenceCostToConquer, conquerPhaseBonus):
        self.name = name
        self.phase = phase # basically what they are doing now
        self.influenceCostToConquer = influenceCostToConquer
        self.conquerPhaseBonusBase = conquerPhaseBonus
        self.conquerPhaseBonus = conquerPhaseBonus

        self.initialSetup()

    # udpates self.conquerPhaseBonus according to our phase
    def updateConquerPhaseBonus(self):
        self.conquerPhaseBonus = self.conquerPhaseBonusBase if self.phase == "aggressively-expanding" else 1

    # giving intial values to the variables on our AI
    def initialSetup(self):
        self.updateConquerPhaseBonus()

SIMPLE_PERSONALITIES = [
    Personality("basic", random.choice(["peacefully-expanding", "aggressively-expanding", "developing"]), 1, 0.1), # 0 0.1
]
