from Map import *
from Button import *
from Timer import *
from Nation import *
import pygame
import random
#from pygame import mixer # music/sounds
import math

class Engine:
    
    def __init__(self, map, height, width, tileSize, numPlayers, color = ""):

        #Initialize pygame
        pygame.init()

        self.timer = Timer()
        self.clock = pygame.time.Clock()

        self.UISPACEX = 450
        self.UISPACEY = 40
        self.HEIGHT = height
        self.WIDTH = width
        self.IMAGES = {}
        self.font = pygame.font.Font(MAIN_FONT[0], MAIN_FONT[1])

        self.velocity = 0
        self.currentMap = 2
        self.allMaps = {
            1 : self.drawMapPolitical, # population
            2 : self.drawMapTerrain, # terrain
            3 : self.drawMapPopulation, # population
            4 : self.drawMapRivers,
        }

        self.sizeX = width / tileSize
        self.sizeY = height / tileSize

        self.map = map
        self.nations = [] # sucks not having pointers...
        #self.playerColor = color # will be used later
        self.tileSize = tileSize
        self.tilesByNation = {}
        self.numPlayers = numPlayers

        self.politicalAlphaValue = 180

        # the texts which will be shown on the screen
        self.texts = [
            "Welcome to CivSim!", "top2", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "bottom", "bottom2"
        ]
        self.textInit = -280 # 175
        self.textDif = 35
        self.textX = self.WIDTH + 30

        # Special Cases
        self.textTopY1 = 90
        self.textTopY2 = self.textTopY1 + self.textDif
        self.textBottomY1 = self.HEIGHT - self.textTopY1 - self.textDif
        self.textBottomY2 = self.HEIGHT - self.textTopY1

        # Date text
        self.day = 0

        # buttonSize
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
    # TODO
    def drawMapPolitical(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                colorTerrain = tile.terrain.color
                nation = self.nations[self.tilesByNation[tile.coords]]

                color1 = (nation.color[0], nation.color[1], nation.color[2], self.politicalAlphaValue)
                color = self.blendColors(color1, colorTerrain) if nation.id != 0 else colorTerrain

                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tileSize, y*self.tileSize, self.tileSize, self.tileSize))
            
                if hills in tile.terrain.features:
                    fstP = [x*self.tileSize + 1, y*self.tileSize + self.tileSize - 1]
                    sndP = [x*self.tileSize + self.tileSize - 1, y*self.tileSize + self.tileSize - 1]
                    trdP = [x*self.tileSize + (self.tileSize // 2), y*self.tileSize - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fstP, sndP, trdP], 1)

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

    # Will use this for later when I need to draw things on the map
    #def loadImages(self):
    #    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK','bP','wR', 'wN', 'wB', 'wQ', 'wK',255 'wP']
    #    for piece in pieces:
    #        self.IMAGES[piece] = pygame.transform.scale(pygame.image.load("images/" + piece + ".png"), (self.tileSize, self.tileSize))

    # shows an individual label on the screen
    def showText(self, font, text, x, y):
        text = font.render(text, True, (0, 0, 0))
        self.screen.blit(text, (x,y))

    # shows the labels on the screen
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
    
    def drawRightButtons(self):
        for button in self.rightButtons:
            button.draw(self.screen, (0,0,0))
    
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

    def genRandomColor(self):
        c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        while (c[0] == c[1] or c[0] == c[2] or c[1] == c[2]): # I don't want 3 equal colors
            c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return c

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

    def addItem(self, tileCoords, controllerId):
        self.tilesByNation[tileCoords] = controllerId

    # run the game
    def run(self):
        # Game Loop
        running = True

        lastVel = 0

        #self.loadImages()

        squareSelected = ()
        #playerClicks = [] #keep track of player clicks: 2 tuples [(6,4),(4,4)]
        
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
        i = self.numPlayers
        while i > 0:
            tile = self.map.tiles[random.randint(1, len(self.map.tiles) - 1)][random.randint(1, len(self.map.tiles[0]) - 1)]
            while tile.terrain.name in noBeginningTerrains or self.tilesByNation[tile.coords] != 0:
                tile = self.map.tiles[random.randint(1, self.map.sizeY - 1)][random.randint(1, self.map.sizeY - 1)]

            # Create a new nation on the random tile
            id = len(self.nations)
            color = self.genRandomColor()
            n = Nation.getNewNation(id, color)
            n.changeTileOwnership(tile, self.tilesByNation)
            self.nations.append(n)
            print(f"Created nation with: id:{id} name:{n.name}")

            i -= 1

        #print(f"Name: {self.nations[0].name} | Representation: {self.nations[0].representation} | Controlled Tiles: {len(self.nations[0].controlledTiles)}")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        lastVel = self.velocity if self.velocity != 0 else lastVel
                        self.velocity = 0 if self.velocity != 0 else lastVel
                        if self.velocity != 0:
                            self.velButton.text = ">" * self.velocity
                        else:
                            self.velButton.text = "||"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    location = pygame.mouse.get_pos() #(x,y) do rato
                    col = location[0] // self.tileSize
                    row = location[1] // self.tileSize
                    #if squareSelected == (row,col) or col >= 8 or row >= 8: #clicked the same square twice
                    if squareSelected == (): 
                        tile = self.map.findTile((0,0))
                    if col < self.sizeX and row < self.sizeY: #clicked outside the box
                        squareSelected = (col, row) # x and y
                        tile = self.map.findTile(squareSelected)
                    #self.printStats(tile)
                    self.updateTexts(tile.getInfo(self.getController(tile)))

                    # print some nation information on the terminal
                    controller = self.getController(tile)
                    print(f"\nController: {controller.representation}")
                    print(f"Resources: {controller.resourcesToString()}")
                    print(f"Phase: {controller.phase}")
                    print(f"{controller.printTiles(controller.tilesToDev)}")
                    print(f"Influence: {controller.influence}\n")

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
                        color = self.genRandomColor()
                        n = Nation.getNewNation(id, color)
                        
                        lastVel = self.velocity if self.velocity != 0 else lastVel
                        self.velocity = 0
                        self.velButton.text = "||"

                        squareSelected = ()
                        # quick UI changes because of the freeze on self.waitForTileInput()
                        pygame.draw.rect(self.screen, BACKGROUND_COLOR, pygame.Rect(self.WIDTH + 5, 5, self.UISPACEX, self.UISPACEY + self.textBottomY2))
                        self.updateTexts(["", "", "Click on a tile", "to place a new nation."])
                        self.showTexts()
                        pygame.display.flip()

                        n.changeTileOwnership(self.waitForTileInput(), self.tilesByNation)

                        self.updateTexts(["", "", "Done!", "A new nation was born!"])
                        self.nations.append(n)

                    # right buttons
                    for button in self.rightButtons:
                        if button.isOver(location):
                            self.currentMap = button.info

                    """ if len(playerClicks) == 1 and getPieceAtLocation(playerClicks[0]) == "--":
                        squareSelected = ()
                        playerClicks = []
                    if len(playerClicks) == 2: # after 2nd click
                        if not updateBoard(playerClicks): # if the piece cant move, then reset
                            squareSelected = ()
                            playerClicks = []
                        else:
                            playerTurn = -playerTurn
                            legalMoves = getAllLegalMoves(playerTurn)
                            updateMateText(legalMoves)
                            printStats(legalMoves, playerClicks)
                            squareSelected = ()
                            playerClicks = [] """

            # Game logic
            # 1 in-game day, may change it
            if self.velocity != 0:
                if self.timer.getTimePassed()>=1/(GAME_SPEED * self.velocity):
                    self.day += 1
                    #for y in range(len(self.map.tiles)):
                    #    for x in range(len(self.map.tiles[0])):
                    #        if self.map.tiles[y][x].population > 0:
                    #            tile.develop()
                            
                    for nation in self.nations:
                        #gameState = (self.map.tiles, self.nations, self.tilesByNation)
                        #newGameState = nation.makeTurn(gameState)
                        nation.makeTurn(self.map.tiles, self.nations, self.tilesByNation)
                        #self.map.tiles = newGameState[0]
                        #self.nations = newGameState[1]
                        #self.tilesByNation = newGameState[2]


                    # restart the timer
                    self.timer.restart()
            
            # UI-related functions

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

            """ if not playerClicks:
                drawBoard([])
            else:
                drawBoard(getAllLegalMovesWithPiece(getPieceAtLocation(playerClicks[0]), playerClicks[0]))
            drawPieces() """

            #self.drawMapTerrain()
            self.drawMap()

            self.showTexts()
            # date text
            self.showText(pygame.font.Font(SMALL_FONT[0], SMALL_FONT[1]), f"Day {self.day}", self.WIDTH - 150, self.HEIGHT + 7)

            #update the display
            #pygame.display.update()
            pygame.display.flip() # I don't know the difference between these 2
            self.clock.tick(60)