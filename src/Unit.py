# I probably won't use this since I don't know how to make a decent AI, so
# I'll just leave this here until I figure it out.

class Unit:
    def __init__(self, id, name, size, attack, defense, x, y, ownerID, leader):
        self.id = id
        self.name = name
        self.size = size
        self.attack = attack
        self.defense = defense
        self.x = x
        self.y = y
        self.ownerID = ownerID
        self.commander = leader

