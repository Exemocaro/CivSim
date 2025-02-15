# CivSim
My first big project in Python, an AI-only game made in Python 3.9.1 and Pygame 2.0.1

![Alt Text](preview.gif)

## How does it work
This game consists of a series of AI players trying to conquer tiles on the map to get more resources; each tile has several of them and each nation will try to take as much tiles as they can to win the game.
Each tile gives a nation bonuses, *money* and *influence*, which can be used to declare wars and develop tiles.
For more details on basic game mechanics read *expanding.txt*.

## Things to improve
They are in no specific order:
* Improve the AI behaviour
* Increase overall performance
* Improve tile generation
* Add more flavour in the form of resources/features
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
python3 CivSim.py # for Linux

python CivSim.py # for Windows
```

## Notes
The code can be messy sometimes because I had no specific objective in min_d when first writing the code, and I changed my min_d a lot of times when deciding what some functions should do and how the game's mechanics works.

It works fine on 1080p, but keep in min_d that for smaller resolutions you'll have to decrease the size of the map and the UI.
For now the recommended map size is "small", but I'll try to make the game faster and improve the AI, if I'm not too lazy :)))
