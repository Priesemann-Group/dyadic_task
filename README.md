Dyadic Task
--------

![til](./res/vid.gif)


Dyadic Task is a competition and/or cooperation game where players gain score depending on the type of dot they conquer. The blue/orange cooperative dots yield more reward on average (8), but the reward of each of them is unfair distributed. That enforces some kind of social cooperation to split the reward in a fair manner. The green competitive dots on the other hand yield less reward on average (6) but can be occupied without the other player.

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
