Play on the Server
--------

In order to play online the following python modules should be installed, install them with the following command.

    pip3 install numpy pyglet twisted

Start the game with the following command:

    python3 client.py

Note that this works only if the server is not full and if the server
is online, which should be the case.

In order to test the multiplayer, two clients can be executed at the
same time.

Host a local Server
--------

This method works independed from the multiplayer server and the
internet connection. The following packages are required:

    pip3 install numpy pyglet twisted numba

In order to start the server run:

    python3 server.py

And in order to join your local server run:

    python3 client.py local

In order to test the multiplayer, two clients can be executed at the
same time.