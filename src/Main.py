from Map import *
from Engine import *
from Settings import *

def main():
    map_size = MAP_SIZES["small"]
    size_x = map_size[0]
    size_y = map_size[1]
    tile_size = map_size[2]
    river_num = map_size[3]
    width = size_y * tile_size
    height = size_x * tile_size
    map = Map(size_x, size_y, river_num)
    map.create_map()
    #map.printMapResources()

    engine = Engine(map, width, height, tile_size, 30, "")
    engine.run()

if __name__ == "__main__":
    main()
