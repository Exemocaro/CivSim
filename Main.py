from Map import *
from Engine import *
from Settings import *

def main():

    # Opens nameGen.cpp, compiles it, runs it and then deletes the executable.
    # I'm just that lazy to remake it in python...
    
    #os.system("g++ -o tempNameGen include/nameGen.cpp")
    #proc = subprocess.Popen(["./tempNameGen.exe"])
    #proc.wait()
    #os.system("del /f tempNameGen.exe")

    #generateNames()

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
