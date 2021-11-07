from Map import *
from Engine import *
from Settings import *

def main():
    mapSize = MAP_SIZES["small"]
    sizeX = mapSize[0]
    sizeY = mapSize[1]
    tileSize = mapSize[2]
    riverNum = mapSize[3]
    width = sizeY * tileSize
    height = sizeX * tileSize
    map = Map(sizeX, sizeY, riverNum)
    map.createMap()
    #map.printMapResources()

    engine = Engine(map, width, height, tileSize, 30, "")
    engine.run()

if __name__ == "__main__":
    main()
