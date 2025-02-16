from Map import *
from Button import *
from Timer import *
from Nation import *
from Tile import *
import pygame
import random
#from pygame import mixer # music/sounds

class Engine:
    
    def __init__(self, map, height, width, tile_size, num_players, color = ""):

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

        self.last_vel = 1 # last velocity, used when pressing the space bar
        self.velocity = 0 # game velocity
        self.current_map = 1 # current way the map is being shown on the screen
        self.selected_nation = -1 # the id of the nation that's currently selected
        self.all_maps = {
            1 : self.draw_map_political, # population
            2 : self.draw_map_terrain, # terrain
            3 : self.draw_map_population, # population
            4 : self.draw_map_rivers,
        }

        # the number of tiles in x and y
        self.size_x = width / tile_size
        self.size_y = height / tile_size

        self.map = map # the game map
        self.nations = [] # each nation of the game
        #self.playerColor = color # will be used later
        self.tile_size = tile_size # the size of each tile
        self.tiles_by_nation = {} # stores each tile coords and it's owner's id, if it has no owner then the id will be 0
        self.num_players = num_players # the total number of players

        # the alpha value used when mixing colors to show the political map 
        self.political_alpha_value = 180

        # the labels which will be shown on the screen
        self.texts = [
            "Welcome to CivSim!", "top2", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "bottom", "bottom2"
        ]
        self.text_init = -280 # 175 # the top label upper Y, after both special cases (the main text basically)
        self.text_dif = 35 # the height difference between labels on the UI on the right
        self.text_x = self.WIDTH + 30 # the displacement between the game map and the labels on the right

        # Special Cases (for the labels, 2 on top and 2 on bottom)
        self.text_top_y1 = 90 # 
        self.text_top_y2 = self.text_top_y1 + self.text_dif
        self.text_bottom_y1 = self.HEIGHT - self.text_top_y1 - self.text_dif
        self.text_bottom_y2 = self.HEIGHT - self.text_top_y1

        # Date text
        self.turn = 0

        # buttonSize on x, basically each button's width
        self.b_s = 50

        # create buttons
        self.vel_button = Button(BUTTON_COLOR, 6, self.HEIGHT + 6, self.b_s, self.UISPACEY - 12, "||")
        self.nation_button = Button(BUTTON_COLOR, 12 + self.b_s, self.HEIGHT + 6, self.b_s, self.UISPACEY - 12, "NAT")
        self.right_buttons = [
            Button(BUTTON_COLOR, self.get_right_button_x(0), self.HEIGHT + 6, self.b_s, self.UISPACEY - 12, "POL", 1), # populationButton
            Button(BUTTON_COLOR, self.get_right_button_x(1), self.HEIGHT + 6, self.b_s, self.UISPACEY - 12, "TERR", 2), # terrainButton
            Button(BUTTON_COLOR, self.get_right_button_x(2), self.HEIGHT + 6, self.b_s, self.UISPACEY - 12, "POP", 3), # populationButton
            Button(BUTTON_COLOR, self.get_right_button_x(3), self.HEIGHT + 6, self.b_s, self.UISPACEY - 12, "RIV", 4), # populationButton
        ]

        #Create the screen (width and height)
        self.screen = pygame.display.set_mode((self.WIDTH + self.UISPACEX, self.HEIGHT + self.UISPACEY))

        #Title and icon
        pygame.display.set_caption("CivSim!")

    # blends two colors, used when showing the political map
    def blend_colors(self, color_alpha_, color_2_):
        color_alpha = (color_alpha_[0] / 255, color_alpha_[1] / 255, color_alpha_[2] / 255, color_alpha_[3] / 255)
        color_2 = (color_2_[0] / 255, color_2_[1] / 255, color_2_[2] / 255)
        output_red = (color_alpha[0] * color_alpha[3]) + (color_2[0] * (1.0 - color_alpha[3]))
        output_green = (color_alpha[1] * color_alpha[3]) + (color_2[1] * (1.0 - color_alpha[3]))
        output_blue = (color_alpha[2] * color_alpha[3]) + (color_2[2] * (1.0 - color_alpha[3]))
        return (round(output_red * 255), round(output_green * 255), round(output_blue * 255))

    # The x position of the buttons on the right
    def get_right_button_x(self, n):
        return self.WIDTH + (6 * (n+1)) + (self.b_s * n)

    # draws the map on the screen based on the terrain of each tile
    def draw_map_terrain(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                color = pygame.Color(tile.terrain.color)
                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))
                if hills in tile.terrain.features:
                    fst_p = [x*self.tile_size + 1, y*self.tile_size + self.tile_size - 1]
                    snd_p = [x*self.tile_size + self.tile_size - 1, y*self.tile_size + self.tile_size - 1]
                    trd_p = [x*self.tile_size + (self.tile_size // 2), y*self.tile_size - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fst_p, snd_p, trd_p], 1)

    # draws rivers above the normal terrain map
    def draw_map_rivers(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                color = pygame.Color(tile.terrain.color)
                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))
                if river in tile.terrain.features:
                    pygame.draw.rect(self.screen, RIVER_COLOR, pygame.Rect(x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))
                if hills in tile.terrain.features:
                    fst_p = [x*self.tile_size + 1, y*self.tile_size + self.tile_size - 1]
                    snd_p = [x*self.tile_size + self.tile_size - 1, y*self.tile_size + self.tile_size - 1]
                    trd_p = [x*self.tile_size + (self.tile_size // 2), y*self.tile_size - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fst_p, snd_p, trd_p], 1)

    # draws the map on the screen based on political entities
    # each nation's color is mixed with the terrain color using the blend_colors() function
    # TODO
    def draw_map_political(self):
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                color_terrain = tile.terrain.color
                nation = self.nations[self.tiles_by_nation[tile.coords]]

                # selecting the color for this nation and checking if it's selected
                if self.selected_nation == nation.id:
                    color_1 = (SELECTED_NATION_COLOR[0], SELECTED_NATION_COLOR[1], SELECTED_NATION_COLOR[2], self.political_alpha_value)
                else:
                    color_1 = (nation.color[0], nation.color[1], nation.color[2], self.political_alpha_value)
                color = self.blend_colors(color_1, color_terrain) if nation.id != 0 else color_terrain

                pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))
            
                if hills in tile.terrain.features:
                    fst_p = [x*self.tile_size + 1, y*self.tile_size + self.tile_size - 1]
                    snd_p = [x*self.tile_size + self.tile_size - 1, y*self.tile_size + self.tile_size - 1]
                    trd_p = [x*self.tile_size + (self.tile_size // 2), y*self.tile_size - 1]
                    pygame.draw.polygon(self.screen, BLACK, [fst_p, snd_p, trd_p], 1)

                # drawing the capital
                if nation.capital == tile:
                    fst_p = [x*self.tile_size, y*self.tile_size + self.tile_size / 2]
                    snd_p = [x*self.tile_size + self.tile_size, y*self.tile_size + self.tile_size / 2]
                    #pygame.draw.polygon(self.screen, CAPITAL_COLOR, [fst_p, snd_p], 1)
                    pygame.draw.circle(self.screen, CAPITAL_COLOR, (x*self.tile_size + self.tile_size / 2, y*self.tile_size + self.tile_size / 2), self.tile_size / 2 - 1)

    # draws the map on the screen based on population values of each tile
    def draw_map_population(self):
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
                    pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))
                else:
                    color = pygame.Color(tile.terrain.color)
                    pygame.draw.rect(self.screen, color, pygame.Rect(x*self.tile_size, y*self.tile_size, self.tile_size, self.tile_size))

    # neat function I made xD
    def draw_map(self):
        self.all_maps[self.current_map]()

    # shows an individual label on the screen
    def show_text(self, font, text, x, y):
        text = font.render(text, True, (0, 0, 0))
        self.screen.blit(text, (x,y))

    # shows the labels on the screen
    # weird function i made, i don't really remember how it works
    def show_texts(self):
        i = 0
        for text in self.texts:
            text = self.font.render(text, True, (0, 0, 0))
            x = self.text_x
            if i == 0:
                y = self.text_top_y1
            elif i == 1:
                y = self.text_top_y2
            elif i == len(self.texts) - 2:
                y = self.text_bottom_y1
            elif i == len(self.texts) - 1:
                y = self.text_bottom_y2
            else:
                y = self.HEIGHT // 2 + (self.text_init + self.text_dif * i)
            self.screen.blit(text, (x, y))
            i += 1
    
    # draws the button on the bottom right side of the screen
    def draw_right_buttons(self):
        for button in self.right_buttons:
            button.draw(self.screen, (0,0,0))
    
    # returns the controller of a given tile
    def get_controller(self, tile):
        for nation in self.nations:
            if self.is_nation_controller(nation, tile):
                return nation
        return empty_nation

    # will have to stay here so the performance goes up
    def is_nation_controller(self, nation, tile):
        if nation.id == self.find(tile.coords):
            return True
        return False

    # updates the labels with the argument given which must be an array
    def update_texts(self, text_array):
        i = 0
        # max 10 iterations because there aren't more text thingys
        for info in text_array:
            self.texts[i] = info
            i += 1
        # clear texts that were not used
        for i in range(i, len(self.texts)):
            self.texts[i] = ""

    # prints info on a tile to the console
    def print_stats(self, tile):
        print("---------------------------------")
        tile.print_info(self.get_controller(tile))

    # change the game velocity
    def change_vel(self):
        if self.velocity == 4:
            self.velocity = 0
        else:
            self.velocity += 1

    # creates a loop that waits for user input, and returns the tile the user clicks on
    def wait_for_tile_input(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    location = pygame.mouse.get_pos() #(x,y) do rato
                    col = location[0] // self.tile_size
                    row = location[1] // self.tile_size
                    if col < self.size_x and row < self.size_y: #clicked outside the box
                        square_selected = (col, row) # x and y
                        tile = self.map.find_tile(square_selected)
                        return tile

    # These two functions will match a tile id with a nation id
    def find(self, tile_coords):
        return self.tiles_by_nation[tile_coords]

    # adds a controller to a certain tile inside the tiles_by_nation dict
    def add_item(self, tile_coords, controller_id):
        self.tiles_by_nation[tile_coords] = controller_id

    # updates the id stored on self.selected_nation
    def update_selected_nation(self, controller):
        self.selected_nation = controller.id

    # run the game
    def run(self):
        # Game Loop
        running = True

        last_vel = 0
        
        square_selected = ()
        tile = None

        # Before game logic
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                self.map.tiles[y][x].set_production()
        
        # Spawn nations

        # Uncontrolled Lands
        print("Generating nations...")
        for y in range(len(self.map.tiles)):
            for x in range(len(self.map.tiles[0])):
                tile = self.map.tiles[y][x]
                self.add_item(tile.coords, empty_nation.id)
        self.nations.append(empty_nation)

        # Normal nations
        for i in range(self.num_players):
            tile = self.map.tiles[random.randint(1, len(self.map.tiles) - 1)][random.randint(1, len(self.map.tiles[0]) - 1)]
            while tile.terrain.name in no_beginning_terrains or self.tiles_by_nation[tile.coords] != 0:
                tile = self.map.tiles[random.randint(4, self.map.size_y - 4)][random.randint(4, self.map.size_y - 4)]

            # Create a new nation on the random tile
            id = len(self.nations)
            n = Nation.get_new_nation(id)
            n.change_tile_ownership(tile, self.tiles_by_nation)
            n.set_capital(tile)
            self.nations.append(n)
            #print(f"Created nation with: id:{id} name:{n.name}") # for testing only basically

        print("Generation complete")
        tile = None # reset the value of "tile"
        #print(f"Name: {self.nations[0].name} | Representation: {self.nations[0].representation} | Controlled Tiles: {len(self.nations[0].controlled_tiles)}")

        # the main game loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.last_vel = self.velocity if self.velocity != 0 else self.last_vel
                        self.velocity = 0 if self.velocity != 0 else self.last_vel
                        if self.velocity != 0:
                            self.vel_button.text = ">" * self.velocity
                        else:
                            self.vel_button.text = "||"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    location = pygame.mouse.get_pos() # mouses' (x,y)
                    col = location[0] // self.tile_size
                    row = location[1] // self.tile_size
                    #if square_selected == (): 
                    #    tile = self.map.find_tile((0,0))
                    if col < self.size_x and row < self.size_y: #clicked outside the box
                        square_selected = (col, row) # x and y
                        tile = self.map.find_tile(square_selected)

                        #self.print_stats(tile)
                        self.update_texts(tile.get_info(self.get_controller(tile)))

                        # print some nation information on the terminal
                        controller = self.get_controller(tile)
                        self.update_selected_nation(controller)
                        print(f"\nClicked coords (x, y): ({col}, {row})")
                        print(f"Tile (x, y): {tile.coords}")
                        print(f"Controller: {controller.id} | {controller.representation}")
                        print(f"Resources: {controller.resources_to_string()}")
                        print(f"Phase: {controller.personality.phase}")
                        print(f"Wars: {controller.wars}")
                        print(f"Tiles to Develop: {controller.print_tiles(controller.tiles_to_dev)}")
                        print(f"Number of Buildings: {controller.num_buildings}")
                        print(f"Technology level: {controller.tech_level}")
                        print(f"Actions left: {controller.actions}")
                        print(f"Money: {controller.money} ({controller.money - controller.last_money})")
                        print(f"Influence: {controller.influence} ({controller.influence - controller.last_influence})")

                    # button logic:
                    # velocityButton
                    if self.vel_button.is_over(location):
                        self.change_vel()
                        if self.velocity != 0:
                            self.vel_button.text = ">" * self.velocity
                        else:
                            self.vel_button.text = "||"

                    # placenation_button
                    if self.nation_button.is_over(location):
                        id = len(self.nations)
                        n = Nation.get_new_nation(id)
                        
                        last_vel = self.velocity if self.velocity != 0 else last_vel
                        self.velocity = 0
                        self.vel_button.text = "||"

                        square_selected = ()
                        # quick UI changes because of the freeze on self.wait_for_tile_input()
                        pygame.draw.rect(self.screen, BACKGROUND_COLOR, pygame.Rect(self.WIDTH + 5, 5, self.UISPACEX, self.UISPACEY + self.text_bottom_y2))
                        self.update_texts(["", "", "Click on a tile", "to place a new nation."])
                        self.show_texts()
                        pygame.display.flip()

                        new_tile = self.wait_for_tile_input()
                        n.change_tile_ownership(new_tile, self.tiles_by_nation)
                        n.set_capital(new_tile)

                        self.update_texts(["", "", "Done!", "A new nation was born!"])
                        self.nations.append(n)

                        print(f"\nCreated a new nation with id {n.id}")

                    # right buttons
                    for button in self.right_buttons:
                        if button.is_over(location):
                            self.current_map = button.info

            # Game logic
            # 1 in-game day, may change it
            if self.velocity != 0:
                if self.timer.get_time_passed()>=1/(GAME_SPEED * self.velocity):
                    self.turn += 1 # updating the turn

                    if tile: self.update_texts(tile.get_info(self.get_controller(tile))) # updating the on-scren text 

                    print(f"---- Starting turn {self.turn} ----")
                    for nation in self.nations:
                        #if self.turn == 30: # testing if negative influence crashes the game (used to)
                        #    nation.influence -= 300000
                        if nation.id != 0:
                            print(f"starting turn id: {nation.id} | ", end = "")
                            nation.make_turn(self.map.tiles, self.nations, self.tiles_by_nation, self.turn)
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
            self.vel_button.draw(self.screen, (0,0,0))
            self.nation_button.draw(self.screen, (0,0,0))
            self.draw_right_buttons()

            self.draw_map()

            self.show_texts()

            # date text
            self.show_text(pygame.font.Font(SMALL_FONT[0], SMALL_FONT[1]), f"Turn {self.turn}", self.WIDTH - 150, self.HEIGHT + 7)

            #update the display
            #pygame.display.update()
            pygame.display.flip()
            self.clock.tick(60)
