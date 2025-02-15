from Settings import *
from Names import name_gen
import random

class Character:

    global_id = 1

    def __init__(self, name, age, gender, martial, prosperity, vitality):
        self.id = Character.global_id
        self.name = name # Must have a limit, let's set it to 20 characters
        self.age = age
        self.gender = gender
        self.martial = martial # a bonus for this nation when at war
        self.prosperity = prosperity # increases nation bonuses on money and influence
        self.vitality = vitality # the time this character will live
        self.probability_of_dying = 0

        self.wealth = 0 # probably won't be used? idk, maybe in rebellions

        self.title = "King" if self.gender == "m" else "Queen"
        self.representation = "" if name == "" else f"{self.title} {self.name}"

        Character.global_id += 1

    # returns a character with given stats
    @staticmethod
    def get_character(name, age, martial, prosperity, vitality):
        if name == "":
            name = "" # to add the name_gen to this
        c = Character(name, age, martial, prosperity, vitality)
        return c
    
    # returns a random character
    @staticmethod
    def get_random_character():
        gender = random.choice(["f", "m"])
        age = random.choice(range(18,40)) # initial age of randomly generated characters
        c = Character(name_gen(gender), age, gender, random.randint(1, 10), random.randint(1, 10), random.randint(1, 10))
        return c

    # returns the passed character's son/daughter. it will have similar stats
    @staticmethod
    def get_successor(char):
        new_age = 17 if char.age < 35 else random.randint(17, char.age - 17)
        gender = random.choice(["f", "m"])
        martial_values = [char.martial, char.martial-1, char.martial-2, char.martial+1, char.martial+2]
        prosperity_values = [char.prosperity, char.prosperity-1, char.prosperity-2, char.prosperity+1, char.prosperity+2]
        vitality_values = [char.vitality, char.vitality-1, char.vitality-2, char.vitality+1, char.vitality+2]
        # these loops are necessary to avoid 0 and negative numbers
        # tho there's probably a better and cleaner way to do this
        martial = 0
        while martial <= 0:
            martial = random.choice(martial_values)
        prosperity = 0
        while prosperity <= 0:
            prosperity = random.choice(prosperity_values)
        vitality = 0
        while vitality <= 0:
            vitality = random.choice(vitality_values)

        c = Character(name_gen(gender), new_age, gender, martial, prosperity, vitality)
        return c

    # updates this character with either new stats or with death :( will also replace it in that case
    def update(self):
        self.age += 1 # increase the age
        self.probability_of_dying = 0 # starts at 0

        # add age-related death probability
        for age_prob_par in AGE_PROBABILITIES_PAR:
            if self.age > age_prob_par[0]:
                self.probability_of_dying = age_prob_par[1]
                break

        # adding base death value
        self.probability_of_dying += BASE_DEATH_VALUE # out of 100, base starting value for each year

        # starting at 20, the probability of dying will increase given the leader's vitality
        if (self.vitality + 2) * 10 > self.age:
            self.probability_of_dying += VITALITY_DEATH_PENALTY
        else:
            self.probability_of_dying -= VITALITY_DEATH_BONUS
        
        r = random.randint(1, 1000)
        #print(f"age: {self.age} chance: {r} | dying: {self.probability_of_dying} | ", end = "")
        if r <= self.probability_of_dying: # the leader died :(
            return Character.get_successor(self)
        else:
            return self
    
    # returns a string with a character's stats
    def get_values(self):
        if self.name == "":
            return ""
        return f"Age:{self.age} M:{self.martial} P:{self.prosperity} V:{self.vitality}"

    def get_info(self):
        info = []
        info.append(self.get_values())
        return info 

    def print_info(self):
        for i in self.get_info():
            print(i)
