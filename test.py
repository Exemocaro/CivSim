import pygame
pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255, 50)  # This color contains an extra integer. It's the alpha value.
PURPLE = (255, 0, 255)

screen = pygame.display.set_mode((200, 325))
screen.fill(WHITE)  # Make the background white. Remember that the screen is a Surface!
clock = pygame.time.Clock()

size = (50, 50)
red_image = pygame.Surface(size)
green_image = pygame.Surface(size)
blue_image = pygame.Surface(size, pygame.SRCALPHA)  # Contains a flag telling pygame that the Surface is per-pixel alpha
purple_image = pygame.Surface(size)

red_image.set_colorkey(BLACK)
green_image.set_alpha(50)
# For the 'blue_image' it's the alpha value of the color that's been drawn to each pixel that determines transparency.
purple_image.set_colorkey(BLACK)
purple_image.set_alpha(50)

pygame.draw.rect(red_image, RED, red_image.get_rect(), 10)
pygame.draw.rect(green_image, GREEN, green_image.get_rect(), 10)
pygame.draw.rect(blue_image, BLUE, blue_image.get_rect(), 10)
pygame.draw.rect(purple_image, PURPLE, purple_image.get_rect(), 10)

def blendColors(colorAlpha_, color2_):
    colorAlpha = (colorAlpha_[0] / 255, colorAlpha_[1] / 255, colorAlpha_[2] / 255, colorAlpha_[3] / 255)
    color2 = (color2_[0] / 255, color2_[1] / 255, color2_[2] / 255)
    outputRed = (colorAlpha[0] * colorAlpha[3]) + (color2[0] * (1.0 - colorAlpha[3]))
    outputGreen = (colorAlpha[1] * colorAlpha[3]) + (color2[1] * (1.0 - colorAlpha[3]))
    outputBlue = (colorAlpha[2] * colorAlpha[3]) + (color2[2] * (1.0 - colorAlpha[3]))
    return (round(outputRed * 255), round(outputGreen * 255), round(outputBlue * 255))

while True:

    #print(blendColors((120, 130, 140, 150), (120, 120, 120)))

    def find(allItems, id):
        return allItems[id]

    def addItem(allItems, item):
        allItems[item['id']] = item

    # create a python dictionary called `allItems`
    allItems = {}

    # add some items to the dictionary
    item1 = { 'id': 1, 'name': 'James' }
    item2 = { 'id': 2, 'name': 'Susan' }
    addItem(allItems, item1)
    addItem(allItems, item2)

    # now lookup an item by its id
    result = find(allItems, 1)
    #print(result['name'])  # ==> 'James'

    tiles = [[1,2,3],[4,5,6]]
    for y in range(3):
        for x in range(3):
           print(tiles[y][x])


    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                screen.blit(red_image, (75, 25))
            elif event.key == pygame.K_2:
                screen.blit(green_image, (75, 100))
            elif event.key == pygame.K_3:
                screen.blit(blue_image, (75, 175))
            elif event.key == pygame.K_4:
                screen.blit(purple_image, (75, 250))

    pygame.display.update()
