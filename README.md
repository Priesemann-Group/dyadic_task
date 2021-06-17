Dyadic Task
=========

Rules
-----

This task is a competetive and/or cooperative game where players increase their score depending on the type of dot they conquer. The blue/orange cooperative dots yield more reward on average (on avg. 8 points per dot) and require that both players hover over them. However the reward of each of them is unfairly distributed. That requires social cooperation to alternate between the blue and orange dots such that both players receive similar total award. The green competitive dots on the other hand yield less reward on average (6) but doesn't requires the cooperation of the other player.

![til](./res/vid.gif)




Play on Server
--------

In order to play online the following python modules should be installed, install them with the following command:

    pip3 install numpy pyglet twisted

Start the game with the following command:

    python3 client.py

Note that this works only if the server is not full and if the server is online, which should be the case.

In order to test the multiplayer, two clients can be executed at the same time.

Host a local Server
--------

This method works independed from server and internet connection. The following packages are required:

    pip3 install numpy pyglet twisted numba

Additionally, PyTables is required. Installing PyTables on Ubuntu:

    sudo apt install python3-pytables

Installing PyTables on ArchLinux:

    sudo pacman -S python-pytables

In order to start the server run:

    python3 server.py

And in order to join your local server run:

    python3 client.py local

In order to test the multiplayer, two clients can be executed at the same time.
