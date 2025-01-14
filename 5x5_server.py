import socket
from game import TicTacToeGame, TicTacToeBoard

# get the ip of the server so the players can connect to it
def get_local_ipv4() -> int:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting local IP: {e}")
        return "127.0.0.1" 

# create the socket and make it reusable
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

port = 12346
ip = get_local_ipv4()

# bind it to the wanted address and port, and make it listen on the given port
s.bind((ip, port))
print(ip)
s.listen(5)



def close_connection(socket, connections):
    for con in connections:
        con.close()
    socket.close()

c = list()
addresses = list()

# wait for both players to connect
for i in range(2):
        conn, addr = s.accept()
        c.append(conn)
        conn.send(f"{i}".encode())
        addresses.append(addr)
        print(f"Player {i} connected from {addr}")


turn = 0
c[turn].send("start".encode())

while True:
    # wait for the first player to make his move
    message = c[turn].recv(10).decode().strip()
    # send the information to the other player
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