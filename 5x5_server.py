import socket
from game import TicTacToeGame, TicTacToeBoard

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

port = 12345

s.bind(('', port))

s.listen(5)



def close_connection(socket, connections):
    for con in connections:
        con.close()
    socket.close()

c = list()
addresses = list()

for i in range(2):
        conn, addr = s.accept()
        c.append(conn)
        conn.send(f"{i}".encode())
        addresses.append(addr)
        print(f"Jucatorul {i} conectat de la adresa {addr}")


turn = 0
c[turn].send("start".encode())

while True:

    message = c[turn].recv(10).decode().strip()
    c[(turn + 1) % 2].send(message.encode())
    if (message == "again" or message == "yes!"):
        continue
    if (message == "exit"):
        break
    message = c[((turn + 1) % 2)].recv(10).decode().strip()
    c[turn].send(message.encode())
    if (message == "exit"):
         break


close_connection(s, c)
