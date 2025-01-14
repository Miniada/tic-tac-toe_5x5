import socket
from time import sleep
from game import DEFAULT_PLAYERS, TicTacToeGame, TicTacToeBoard

# give the address of the server you want to connect to
ip = input("The address of the server you want to connect to: ").strip()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 12346
try:
    # connect to the server and receive the corresponding label (cross or zero)
    s.connect((ip, port))
    i = int(s.recv(1024).decode())
    # wait for the second player
    if (i == 0):
        print("Waiting for the other player to connect")
        s.recv(1024).decode()
    game = TicTacToeGame(s)

    board = TicTacToeBoard(game, s, i, "")

    
    # this is where the game starts
    turn = 0
    player = DEFAULT_PLAYERS[i]

    print(player[0])

    board.mainloop()

    s.send("exit".encode())
    s.close()
except ConnectionRefusedError:
        print(f"Connection refused by {ip}:{port}")