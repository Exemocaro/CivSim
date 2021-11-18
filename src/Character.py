from Settings import *
from nameGen import *
import random
#from Resource import *

class Character:

    globalID = 1

    def __init__(self, name, age, gender, martial, prosperity, vitality):
        self.id = Character.globalID
        self.name = name # Must have a limit, let's set it to 20 characters
        self.age = age
        self.gender = gender
        self.martial = martial # a bonus for this nation when at war
        self.prosperity = prosperity # increases nation bonuses on money and influence
        self.vitality = vitality # the time this character will live
        self.probabilityOfDying = 0

        self.wealth = 0 # probably won't be used? idk, maybe in rebellions

        self.title = "King" if self.gender == "m" else "Queen"
        self.representation = "" if name == "" else f"{self.title} {self.name}"

        Character.globalID += 1

    # returns a character with given stats
    def getCharacter(name, age, martial, prosperity, vitality):
        if name == "":
            name = "" # to add the nameGen to this
        c = Character(name, age, martial, prosperity, vitality)
        return c
    
    # returns a random character
    def getRandomCharacter():
        gender = random.choice(["f", "m"])
        age = random.choice(range(18,40)) # initial age of randomly generated characters
        c = Character(nameGen(gender), age, gender, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
        return c

    # returns the passed character's son/daughter. it will have similar stats
    def getSuccessor(char):
        newAge = 17 if char.age < 35 else random.randint(17, char.age - 17)
        gender = random.choice(["f", "m"])
        martialValues = [char.martial, char.martial-1, char.martial-2, char.martial+1, char.martial+2]
        prosperityValues = [char.prosperity, char.prosperity-1, char.prosperity-2, char.prosperity+1, char.prosperity+2]
        vitalityValues = [char.vitality, char.vitality-1, char.vitality-2, char.vitality+1, char.vitality+2]
        # these loops are necessary to avoid 0 and negative numbers
        # tho there's probably a better and cleaner way to do this
        martial = 0
        while martial <= 0:
            martial = random.choice(martialValues)
        prosperity = 0
        while prosperity <= 0:
            prosperity = random.choice(prosperityValues)
        vitality = 0
        while vitality <= 0:
            vitality = random.choice(vitalityValues)

        c = Character(nameGen(gender), newAge, gender, martial, prosperity, vitality)
        return c

    # updates this character with either new stats or with death :( will also replace it in that case
    def update(self):
        self.age += 1 # increase the age

        # i tried to make it so that the probability of dying slowly increases as a character gets older
        # but the numbers are a bit random, i put there what i felt was right xD
        if self.age > 95:
            self.probabilityOfDying = 500
        if self.age > 90:
            self.probabilityOfDying = 250
        elif self.age > 85:
            self.probabilityOfDying = 120
        elif self.age > 80:
            self.probabilityOfDying = 80
        elif self.age > 75:
            self.probabilityOfDying = 50
        elif self.age > 70:
            self.probabilityOfDying = 25
        elif self.age > 65:
            self.probabilityOfDying = 10
        elif self.age > 60:
            self.probabilityOfDying = 5
        elif self.age > 55:
            self.probabilityOfDying = 4
        elif self.age > 50:
            self.probabilityOfDying = 3
        elif self.age > 45:
            self.probabilityOfDying = 2
        elif self.age > 40:
            self.probabilityOfDying = 1
        else:
            self.probabilityOfDying = 0
        
        # adding base death value
        self.probabilityOfDying += BASE_DEATH_VALUE # out of 100, base starting value for each year

        # starting at 20, the probability of dying will increase given the leader's vitality
        if (self.vitality + 2) * 10 > self.age:
            self.probabilityOfDying += VITALITY_DEATH_PENALTY
        else:
            self.probabilityOfDying -= VITALITY_DEATH_BONUS
        
        r = random.randint(1, 1000) # out of 100
        print(f"age: {self.age} chance: {r} | dying: {self.probabilityOfDying} | ", end = "")
        if r <= self.probabilityOfDying: # the leader died :(
            return Character.getSuccessor(self)
        else:
            return self
    
    # returns a string with a character's stats
    def getValues(self):
        if self.name == "":
            return ""
        return f"Age:{self.age} M:{self.martial} P:{self.prosperity} V:{self.vitality}"

    def getInfo(self):
        info = []
        info.append(self.getValues())
        return info 

    def printInfo(self):
        for i in self.getInfo():
            print(i)
