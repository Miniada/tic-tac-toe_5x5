tudor_andrei.matei
andreea.munteanu05

# Short introduction

The app represents a 5x5 Tic-Tac-Toe game made in Python, that allows users to play against each other,
on the same computer or on different devices connected to the same network, or against an AI player, which
will take its time to think about the correct move. Unlike the classic 3x3 game, in order to win, a player
needs to have 4 spots in a line marked as theirs. The game is pretty simple to understand, every player
needs to click on one of the 25 buttons on the screen to make their selection, then wait for their turn.

(https://github.com/Miniada/tic-tac-toe_5x5)


# What we used in our project

The only programming language used in our project was Python. 
* In order to create the base game, we've used Python for the game logic and Tkinter for the interface
and to handle the "click" event and create 2 special buttons, one that asks for a tie and one that
resets the game. This is what's being used when playing against a real player on the same computer.
* Then, to expand it to a local network multiplayer, we've used sockets so that the clients can communicate
with the server.  But that wasn't enough, since they would block the program while waiting for updates.
Here is where multi-threading was introduced in our program to receive updates from the other players.
We created a thread that would run a function which contains a while(1) loop, so it will never stop checking
for any new messages sent on the socket.
* The AI player was used with the help of Math, being created with a Monte Carlo Tree Search algorithm in
order to determine the best move. If the algorithm can't determine the best move, it will simply search for
a random free spot on the table.


# How to use

When starting the program (python3 game.py), the user will be welcomed by an user-friendly menu, from
which he can select one of the 4 options available. The first two options will create a local game, so,
basically, you just need to click the button and the game will start. The other two options are strictly for
multiplayer games. In order to create one, you need to press the "Create a game" button, which will
create 2 processes: one server and one client. You will receive the ip of the server that you will connect to
by typing it in the console, when requested. The same ip will be shared to the player that wants to join your game, by pressing "Join a game".




# What each one of us has done


## Tudor (tudor_andrei.matei)

- wrote the introduction to this README (nothing difficult here)
- created the server and client source files and implemented it into the main game.py file
The making of the multiplayer game was much harder than I had expected, even though I wasn't thinking
it would be easy. I think it was even harder because I've tried to mostly use information available on the
Operating Systems course page. 
The first thing I've done was creating a way for the client and the server to communicate with each other by
using sockets. I also edited some of the base game code, so it checks for an active socket, which
will determine what methods to use.
After that, a harder part came: I needed to think how to use the information sent so that I
can edit both interfaces at the same time, after one user made an action. There were way too many bugs
at the beginning, but, slowly, I've managed to make it work, but there were some problems left:
the game was blocking while waiting for the other player and the tie and play again buttons were not
working. 
The problem with the buttons wasn't that hard to solve (it was about adding some new socket
messages), but it made me change the server code a little bit, so i could reset the state of the server easier,
when restarting a game.
The last problem left was how to not block the waiting player's game. Then, another concept learnt at the
OS course came into my mind: multi-threading. Whenever, the game is started with a socket linked to it,
it will also start a new thread that will continuously check for updates from the server.
After a bit, I've realized that it's kind of useless to have a multiplayer game that would create 2 instances
on the same device, so I've implemented a way too get the address of the server device on the local network
so you could connect from another computer if you knew the address. This last part was way easier than expected.


- also tried to help implementing the AI part, but it would have a serious bug where it would just start trying to
fill the rows one by one instead of making an actual good move. Andreea did most of the job here, by 
managing to fix it

- created the main menu for the game
I think this was the easiest part, I only used some Tkinter buttons, that return a different value, so I
know what should be initialized. 
For the creation of the server and execution of the client, 2 processes were created in the main source file.
This way, all an user has to do is just run the game.py from the terminal and select an option.



