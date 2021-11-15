from Map import *
from Button import *
from Timer import *
from Nation import *
from Tile import *
import pygame
import random
#from pygame import mixer # music/sounds

class Engine:
    
    def __init__(self, map, height, width, tileSize, numPlayers, color = ""):

        #Initialize pygame
        pygame.init()

        # time control things
        self.timer = Timer()
        self.clock = pygame.time.Clock()

        self.UISPACEX = 450 # space in the right og the game for the UI
        self.UISPACEY = 40 # space below the game for the UI, mostly buttons
        self.HEIGHT = height # window height
        self.WIDTH = width # window width
        self.IMAGES = {}
        self.font = pygame.font.Font(MAIN_FONT[0], MAIN_FONT[1])

        self.lastVel = 1 # last velocity, used when pressing the space bar
        self.velocity = 0 # game velocity
        self.currentMap = 1 # current way the map is being shown on the screen
        self.selectedNation = -1 # the id of the nation that's currently selected
        self.allMaps = {
            1 : self.drawMapPolitical, # population
            2 : self.drawMapTerrain, # terrain
            3 : self.drawMapPopulation, # population
            4 : self.drawMapRivers,
        }

        # the number of tiles in x and y
        self.sizeX = width / tileSize
        self.sizeY = height / tileSize

        self.map = map # the game map
        self.nations = [] # each nation of the game
        #self.playerColor = color # will be used later
        self.tileSize = tileSize # the size of each tile
        self.tilesByNation = {} # stores each tile coords and it's owner's id, if it has no owner then the id will be 0
        self.numPlayers = numPlayers # the total number of players

        # the alpha value used when mixing colors to show the political map 
        self.politicalAlphaValue = 180

        # the labels which will be shown on the screen
        self.texts = [
            "Welcome to CivSim!", "top2", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "bottom", "bottom2"
        ]
        self.textInit = -280 # 175 # the top label upper Y, after both special cases (the main text basically)
        self.textDif = 35 # the height difference between labels on the UI on the right
        self.textX = self.WIDTH + 30 # the displacement between the game map and the labels on the right

        # Special Cases (for the labels, 2 on top and 2 on bottom)
        self.textTopY1 = 90 # 
        self.textTopY2 = self.textTopY1 + self.textDif
        self.textBottomY1 = self.HEIGHT - self.textTopY1 - self.textDif
        self.textBottomY2 = self.HEIGHT - self.textTopY1

        # Date text
        self.turn = 0

        # buttonSize on x, basically each button's width
        self.bS = 50

        # create buttons
        self.velButton = Button(BUTTON_COLOR, 6, self.HEIGHT + 6, self.bS, self.UISPACEY - 12, "||")
        self.nationButton = Button(BUTTON_COLOR, 12 + self.bS, self.HEIGHT + 6, self.bS, self.UISPACEY - 12, "NAT")
        self.rightButtons = [
            Button(BUTTON_COLOR, self.getRightButtonX(0), self.HEIGHT + 6, self.bS, self.UISPACEY - 12, "POL", 1), # populationButton
            Button(BUTTON_COLOR, self.getRightButtonX(1), self.HEIGHT + 6, self.bS, self.UISPACEY - 12, "TERR", 2), # terrainButton
            Button(BUTTON_COLOR, self.getRightButtonX(2), self.HEIGHT + 6, self.bS, self.UISPACEY - 12, "POP", 3), # populationButton
            Button(BUTTON_COLOR, self.getRightButtonX(3), self.HEIGHT + 6, self.bS, self.UISPACEY - 12, "RIV", 4), # populationButton
        ]

        #Create the screen (width and height)
        self.screen = pygame.display.set_mode((self.WIDTH + self.UISPACEX, self.HEIGHT + self.UISPACEY))

        #Title and icon
        pygame.display.set_caption("CivSim!")

    # blends two colors, used when showing the political map
    def blendColors(self, colorAlpha_, color2_):
        colorAlpha = (colorAlpha_[0] / 255, colorAlpha_[1] / 255, colorAlpha_[2] / 255, colorAlpha_[3] / 255)
        color2 = (color2_[0] / 255, color2_[1] / 255, color2_[2] / 255)
        outputRed = (colorAlpha[0] * colorAlpha[3]) + (color2[0] * (1.0 - colorAlpha[3]))
        outputGreen = (colorAlpha[1] * colorAlpha[3]) + (color2[1] * (1.0 - colorAlpha[3]))
        outputBlue = (colorAlpha[2] * colorAlpha[3]) + (color2[2] * (1.0 - colorAlpha[3]))
        return (round(outputRed * 255), round(outputGreen * 255), round(outputBlue * 255))

    # The x position of the buttons on the right
    def getRightButtonX(self, n):
        return self.WIDTH + (6 * (n+1)) + (self.bS * n)

    # draws the map on the screen based on the terrain of each tile
    def drawMapTerrain(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                color = pygame.Color(tile.terrain.color)
                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))
                if hills in tile.terrain.features:
                    fstP = [x*self.tileSize + 1, y*self.tileSize + self.tileSize - 1]
                    sndP = [x*self.tileSize + self.tileSize - 1, y*self.tileSize + self.tileSize - 1]
                    trdP = [x*self.tileSize + (self.tileSize // 2), y*self.tileSize - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fstP, sndP, trdP], 1)

    # draws rivers above the normal terrain map
    def drawMapRivers(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                color = pygame.Color(tile.terrain.color)
                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))
                if river in tile.terrain.features:
                    pygame.draw.rect(self.screen, RIVER_COLOR, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))
                if hills in tile.terrain.features:
                    fstP = [x*self.tileSize + 1, y*self.tileSize + self.tileSize - 1]
                    sndP = [x*self.tileSize + self.tileSize - 1, y*self.tileSize + self.tileSize - 1]
                    trdP = [x*self.tileSize + (self.tileSize // 2), y*self.tileSize - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fstP, sndP, trdP], 1)

    # draws the map on the screen based on political entities
    # each nation's color is mixed with the terrain color using the blendColors() function
    # TODO
    def drawMapPolitical(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                colorTerrain = tile.terrain.color
                nation = self.nations[self.tilesByNation[tile.coords]]

                # selecting the color for this nation and checking if it's selected
                if self.selectedNation == nation.id:
                    color1 = (SELECTED_NATION_COLOR[0], SELECTED_NATION_COLOR[1], SELECTED_NATION_COLOR[2], self.politicalAlphaValue)
                else:
                    color1 = (nation.color[0], nation.color[1], nation.color[2], self.politicalAlphaValue)
                color = self.blendColors(color1, colorTerrain) if nation.id != 0 else colorTerrain

                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))
            
                if hills in tile.terrain.features:
                    fstP = [x*self.tileSize + 1, y*self.tileSize + self.tileSize - 1]
                    sndP = [x*self.tileSize + self.tileSize - 1, y*self.tileSize + self.tileSize - 1]
                    trdP = [x*self.tileSize + (self.tileSize // 2), y*self.tileSize - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fstP, sndP, trdP], 1)

                # drawing the capital
                if nation.capital == tile:
                    fstP = [x*self.tileSize, y*self.tileSize + self.tileSize / 2]
                    sndP = [x*self.tileSize + self.tileSize, y*self.tileSize + self.tileSize / 2]
                    #pygame.draw.polygon(self.screen, CAPITAL_COLOR, [fstP, sndP], 1)
                    pygame.draw.circle(self.screen, CAPITAL_COLOR, (x*self.tileSize + self.tileSize / 2, y*self.tileSize + self.tileSize / 2), self.tileSize / 2 - 1)

    # draws the map on the screen based on population values of each tile
    def drawMapPopulation(self):
        biggest = 0 # biggest pop
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                if tile.population > biggest:
                    biggest = tile.population
        
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                if tile.population > 0:
                    color = (0, 250 * tile.population // biggest + 5, 0)
                    pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))
                else:
                    color = pygame.Color(tile.terrain.color)
                    pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))

    # neat function I made xD
    def drawMap(self):
        self.allMaps[self.currentMap]()

    # shows an individual label on the screen
    def showText(self, font, text, x, y):
        text = font.render(text, True, (0, 0, 0))
        self.screen.blit(text, (x,y))

    # shows the labels on the screen
    # weird function i made, i don't really remember how it works
    def showTexts(self):
        i = 0
        for text in self.texts:
            text = self.font.render(text, True, (0, 0, 0))
            x = self.textX
            if i == 0:
                y = self.textTopY1
            elif i == 1:
                y = self.textTopY2
            elif i == len(self.texts) - 2:
                y = self.textBottomY1
            elif i == len(self.texts) - 1:
                y = self.textBottomY2
            else:
                y = self.HEIGHT // 2 + (self.textInit + self.textDif * i)
            self.screen.blit(text, (x, y))
            i += 1
    
    # draws the button on the bottom right side of the screen
    def drawRightButtons(self):
        for button in self.rightButtons:
            button.draw(self.screen, (0,0,0))
    
    # returns the controller of a given tile
    def getController(self, tile):
        for nation in self.nations:
            if self.isNationController(nation, tile):
                return nation
        return emptyNation

    # will have to stay here so the performance goes up
    def isNationController(self, nation, tile):
        if nation.id == self.find(tile.coords):
            return True
        return False

    # updates the labels with the argument given which must be an array
    def updateTexts(self, textArray):
        i = 0
        # max 10 iterations because there aren't more text thingys
        for info in textArray:
            self.texts[i] = info
            i += 1
        # clear texts that were not used
        for i in range(i, len(self.texts)):
            self.texts[i] = ""

    # prints info on a tile to the console
    def printStats(self, tile):
        print("---------------------------------")
        tile.printInfo(self.getController(tile))

    # change the game velocity
    def changeVel(self):
        if self.velocity == 4:
            self.velocity = 0
        else:
            self.velocity += 1

    # creates a loop that waits for user input, and returns the tile the user clicks on
    def waitForTileInput(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    location = pygame.mouse.get_pos() #(x,y) do rato
                    col = location[0] // self.tileSize
                    row = location[1] // self.tileSize
                    if col < self.sizeX and row < self.sizeY: #clicked outside the box
                        squareSelected = (col, row) # x and y
                        tile = self.map.findTile(squareSelected)
                        return tile

    # These two functions will match a tile id with a nation id
    def find(self, tileCoords):
        return self.tilesByNation[tileCoords]

    # adds a controller to a certain tile inside the tilesByNation dict
    def addItem(self, tileCoords, controllerId):
        self.tilesByNation[tileCoords] = controllerId

    # updates the id stored on self.selectedNation
    def updateSelectedNation(self, controller):
        self.selectedNation = controller.id

    # run the game
    def run(self):
        # Game Loop
        running = True

        lastVel = 0
        
        squareSelected = ()

        # Before game logic
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                self.map.tiles[y][x].setProduction()
        
        # Spawn nations

        # Uncontrolled Lands
        print("Generating nations...")
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                self.addItem(tile.coords, emptyNation.id)
        self.nations.append(emptyNation)

        # Normal nations
        for i in range(self.numPlayers):
            tile = self.map.tiles[random.randint(1, len(self.map.tiles) - 1)][random.randint(1, len(self.map.tiles[0]) - 1)]
            while tile.terrain.name in noBeginningTerrains or self.tilesByNation[tile.coords] != 0:
                tile = self.map.tiles[random.randint(4, self.map.sizeY - 4)][random.randint(4, self.map.sizeY - 4)]

            # Create a new nation on the random tile
            id = len(self.nations)
            n = Nation.getNewNation(id)
            n.changeTileOwnership(tile, self.tilesByNation)
            n.setCapital(tile)
            self.nations.append(n)
            #print(f"Created nation with: id:{id} name:{n.name}") # for testing only basically

        print("Generation complete")
        #print(f"Name: {self.nations[0].name} | Representation: {self.nations[0].representation} | Controlled Tiles: {len(self.nations[0].controlledTiles)}")

        # the main game loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.lastVel = self.velocity if self.velocity != 0 else self.lastVel
                        self.velocity = 0 if self.velocity != 0 else self.lastVel
                        if self.velocity != 0:
                            self.velButton.text = ">" * self.velocity
                        else:
                            self.velButton.text = "||"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    location = pygame.mouse.get_pos() # mouses' (x,y)
                    col = location[0] // self.tileSize
                    row = location[1] // self.tileSize
                    #if squareSelected == (): 
                    #    tile = self.map.findTile((0,0))
                    if col < self.sizeX and row < self.sizeY: #clicked outside the box
                        squareSelected = (col, row) # x and y
                        tile = self.map.findTile(squareSelected)

                        #self.printStats(tile)
                        self.updateTexts(tile.getInfo(self.getController(tile)))

                        # print some nation information on the terminal
                        controller = self.getController(tile)
                        self.updateSelectedNation(controller)
                        print(f"\nClicked coords (x, y): ({col}, {row})")
                        print(f"Tile (x, y): {tile.coords}")
                        print(f"Controller: {controller.id} | {controller.representation}")
                        print(f"Resources: {controller.resourcesToString()}")
                        print(f"Phase: {controller.personality.phase}")
                        print(f"Wars: {controller.wars}")
                        print(f"Tiles to Develop: {controller.printTiles(controller.tilesToDev)}")
                        print(f"Number of Buildings: {controller.numBuildings}")
                        print(f"Technology level: {controller.techLevel}")
                        print(f"Actions left: {controller.actions}")
                        print(f"Money: {controller.money} ({controller.money - controller.lastMoney})")
                        print(f"Influence: {controller.influence} ({controller.influence - controller.lastInfluence})")

                    # button logic:
                    # velocityButton
                    if self.velButton.isOver(location):
                        self.changeVel()
                        if self.velocity != 0:
                            self.velButton.text = ">" * self.velocity
                        else:
                            self.velButton.text = "||"

                    # placeNationButton
                    if self.nationButton.isOver(location):
                        id = len(self.nations)
                        n = Nation.getNewNation(id)
                        
                        lastVel = self.velocity if self.velocity != 0 else lastVel
                        self.velocity = 0
                        self.velButton.text = "||"

                        squareSelected = ()
                        # quick UI changes because of the freeze on self.waitForTileInput()
                        pygame.draw.rect(self.screen, BACKGROUND_COLOR, pygame.Rect(self.WIDTH + 5, 5, self.UISPACEX, self.UISPACEY + self.textBottomY2))
                        self.updateTexts(["", "", "Click on a tile", "to place a new nation."])
                        self.showTexts()
                        pygame.display.flip()

                        newTile = self.waitForTileInput()
                        n.changeTileOwnership(newTile, self.tilesByNation)
                        n.setCapital(newTile)

                        self.updateTexts(["", "", "Done!", "A new nation was born!"])
                        self.nations.append(n)

                        print(f"\nCreated a new nation with id {n.id}")

                    # right buttons
                    for button in self.rightButtons:
                        if button.isOver(location):
                            self.currentMap = button.info

            # Game logic
            # 1 in-game day, may change it
            if self.velocity != 0:
                if self.timer.getTimePassed()>=1/(GAME_SPEED * self.velocity):
                    self.turn += 1
                    print(f"---- Starting turn {self.turn} ----")
                    for nation in self.nations:
                        #if self.turn == 30: # testing if negative influence crashes the game (used to)
                        #    nation.influence -= 300000
                        if nation.id != 0:
                            print(f"starting turn id: {nation.id} | ", end = "")
                            nation.makeTurn(self.map.tiles, self.nations, self.tilesByNation)
                            print("turn end")
                        else:
                            print("skipping turn; neutral nation; id == 0")
                    # restart the timer
                    self.timer.restart()
            
            # UI-related functions
            #print("ui draw | ", end = "")

            # Fill the screen with that grey color
            self.screen.fill(BACKGROUND_COLOR)
            
            # Right big rectangle
            pygame.draw.rect(self.screen, BLACK, [self.WIDTH, 0, self.UISPACEX, self.HEIGHT], 5)
            
            # Bottom big rectangle
            pygame.draw.rect(self.screen, BLACK, [0, self.HEIGHT, self.WIDTH, self.UISPACEY], 5)

            # Bottom right rectangle
            pygame.draw.rect(self.screen, BLACK, [self.WIDTH, self.HEIGHT, self.UISPACEX, self.UISPACEY], 5)

            # Draw the buttons
            self.velButton.draw(self.screen, (0,0,0))
            self.nationButton.draw(self.screen, (0,0,0))
            self.drawRightButtons()

            self.drawMap()

            self.showTexts()

            # date text
            self.showText(pygame.font.Font(SMALL_FONT[0], SMALL_FONT[1]), f"Turn {self.turn}", self.WIDTH - 150, self.HEIGHT + 7)

            #update the display
            #pygame.display.update()
            pygame.display.flip()
            self.clock.tick(60)
