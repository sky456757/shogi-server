import socket
from _thread import *
import pickle
import random

#server = socket.gethostbyname(socket.gethostname())
server = "shogi-server-production.up.railway.app"
print(server)
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

games = {}
players = []
turns = 0

def threaded_client(conn1, conn2, gameId):
    global move
    global turns
    global players

    conn1.sendall(pickle.dumps(str("started")))

    while True:
        if(turns == 0):
            try:
                data = conn1.recv(4096).decode()
                if not data:
                    break
                else:
                    #move = data
                    conn2.sendall(pickle.dumps(data))
                    rec = conn2.recv(4096).decode()
                    conn1.sendall(pickle.dumps(rec))
                    turns = 1
                    if(rec == "wolf"):
                        rec2 = conn1.recv(4096).decode()
                        conn2.sendall(pickle.dumps(rec2))
                        if(rec2 == "king"):
                            del games[gameId]
                            print("Closing Game", gameId)
                            break

                    if(rec == "king"):
                        del games[gameId]
                        print("Closing Game", gameId)
                        break
            except:
                break
        else:
            try:
                data = conn2.recv(4096).decode()
                if not data:
                    break
                else:
                    #move = data
                    conn1.sendall(pickle.dumps(data))
                    rec = conn1.recv(4096).decode()
                    conn2.sendall(pickle.dumps(rec))
                    turns = 0
                    if(rec == "wolf"):
                        rec2 = conn2.recv(4096).decode()
                        conn1.sendall(pickle.dumps(rec2))
                        if(rec2 == "king"):
                            del games[gameId]
                            print("Closing Game", gameId)
                            break
                    if(rec == "king"):
                        del games[gameId]
                        print("Closing Game", gameId)
                        break
            except:
                break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    conn1.close()
    conn2.close()
    players = []
    turns = 0



while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    conn.send(str.encode(str("connected")))
    clientMessage = conn.recv(4096).decode()
    print(clientMessage)
    p = 0
    roomid = clientMessage
    gameId = roomid
    if gameId == "0":
        roomid = str(random.randint(10000,99999))
        while roomid in games:
            roomid = str(random.randint(10000,99999))
        print(roomid)
        conn.sendall(pickle.dumps(str(roomid)))
        games[roomid] = True
        print("Creating a new game...")
        players.append(conn)
    else:
        if(gameId in games):
            p = 1
            conn.sendall(pickle.dumps("connected"))
            players.append(conn)
            start_new_thread(threaded_client, (players[0], players[1], gameId))
        else:
            conn.sendall(pickle.dumps('failed'))
            conn.close()
            continue


