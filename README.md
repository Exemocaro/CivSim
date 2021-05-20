# CivSim2
My first big project in Python, an AI-only game made in Python 3.9.1 and Pygame 2.0.1
This is still a WIP, since the AI can't do much for the time being.

## How does it work
This game consists of a series of AI players trying to conquer tiles on the map to get more resources, each tile has several of them and they can/will be used to increase each player's *influence*, which in turn allows them to conquer more tiles.
Tiles are stored in a *map*, which I created using a perlin noise library found in *requirements.txt*. For the UI I decided to use Pygame. It's recommended to stick with the "small" map or you may get performance issues.

## Things to improve
They are in no specific order:
* Improve the AI behaviour
* Increase overall performance
* Improve tile generation
* Add More flavour in the form of resources/features
* Add an event mechanic
* Add some music to the game
* Add a starting menu

## How to run
First we need to install all the packages in *requirements.txt*:
```
pip install -r requirements.txt
```
Then we can run the game:

```
python3 Main.py # for Linux

python Main.py # for Windows
```
