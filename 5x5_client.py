import socket
from time import sleep
from game import DEFAULT_PLAYERS, TicTacToeGame, TicTacToeBoard

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12347
s.connect(('127.0.0.1', port))
i = int(s.recv(1024).decode())
game = TicTacToeGame(s)

board = TicTacToeBoard(game, s, i, "")

if (i == 0):
    s.recv(1024).decode()

turn = 0
player = DEFAULT_PLAYERS[i]

print(player[0])

board.mainloop()

s.send("exit".encode())
s.close()
