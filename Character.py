from Settings import *
from include.nameGen import *
import random
#from Resource import *

class Character:

    globalID = 1

    def __init__(self, name, gender, martial, prosperity, darkness):
        self.id = Character.globalID
        self.name = name # Must have a limit, let's set it to 20 characters
        self.gender = gender
        self.martial = martial
        self.prosperity = prosperity
        self.darkness = darkness

        self.wealth = 0

        self.title = "King" if self.gender == "m" else "Queen"
        self.representation = "" if name == "" else f"{self.title} {self.name}"

        Character.globalID += 1

    # returns a character with given stats
    def getCharacter(name, martial, prosperity, darkness):
        if name == "":
            name = "" # to add the nameGen to this
        c = Character(name, martial, prosperity, darkness)
        return c
    
    # returns a random character
    def getRandomCharacter():
        gender = random.choice(["f", "m"])
        c = Character(nameGen(gender), gender, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
        return c
    
    # returns a string with a character's stats
    def getValues(self):
        if self.name == "":
            return ""
        return f"M:{self.martial} P:{self.prosperity} D:{self.darkness}"

    def getInfo(self):
        info = []
        #info.append(f"ID: {self.id}")
        #info.append(f"Name: {self.name}")
        #info.append(f"Martial: {self.martial}")
        #info.append(f"Prosperity: {self.prosperity}")
        #info.append(f"Darkness: {self.darkness}")
        info.append(self.getValues())
        #info.append(f"Wealth: {self.wealth}")
        return info 

    def printInfo(self):
        for i in self.getInfo():
            print(i)
