﻿# Pocket Jeopardy

This is a fun little project I made because of my love of Jeopardy. I connected an e-Paper HAT on to a Raspberry PI 4, and used the provided epd*.py files to interact with the screen.

The project comes in two parts: The python game, and a web scraper to collect the game data.

## Python game

The entire game is in the jeopardy.py file. When the Raspberry Pi is plugged in, the `startJeopardy.sh` file is called by the OS during startup. This shell file just starts the python program.

The python program interacts with the screen, the buttons, and the game data to make an interactive Jeopardy game that is the size of the Raspberry Pi!

## The Web scraper

The web scraper is a simple node.js project consisting of a single javascript file (index.js). It makes asynchronous HTTP GET calls to `https://www.j-archive.com/showgame.php?game_id=<SHOW_NUMBER>`, and all of the show's clues and answers are stored in a json file for that episode. This way, when generating the clues, you can decide how many shows you want to download.
