import random
import socket as sock
import sys
import time


FR_FORMAT = 'Sujet Verbe Objet-Direct Adjectif'


class Client(object):
    def __init__(self, socket):
        self.socket = socket 

    @staticmethod
    def from_connection(host, port):
        s = sock.socket()
        s.connect((host, port))
        return Client(s)

    def loop(self):
        while True:
            data = self.socket.recv(1024)
            if not data.startswith('#'):
                resp = raw_input(data)
                self.socket.send(resp)
            else:
                print(data[1:])


class Server(object):
    def __init__(self, sockets):
        self.sockets = sockets
        self.players = len(sockets) + 1

    @staticmethod
    def with_player_count(player_count, port):
        client_count = player_count - 1
        me = sock.socket()
        me.bind((sock.gethostname(), port))
        me.listen(client_count)
        print("Listening on: " + sock.gethostbyname(sock.gethostname()))
        sockets = []
        while len(sockets) < client_count:
            c, addr = me.accept()
            print('Connection accepted from ' + str(addr))
            sockets.append(c)
        return Server(sockets)

    def print_all(self, msg):
        for s in self.sockets:
            s.send('#' + msg)
        print(msg)

    def play_game(self):
        self.print_all('Un nouveau jeu commence!\nFormat: ' + FR_FORMAT)
        roles = FR_FORMAT.split(' ')
        player = random.randint(0, self.players) 
        string = ''
        for role in roles:
            player = (player + 1) % self.players
            if player == 0:
                resp = raw_input(role + ": ")
                string += resp
                string += ' '
            else:
                s = self.sockets[player - 1]
                s.send(role + ": ")
                resp = s.recv(1024)
                string += resp
                string += ' '
        self.print_all("Phrase Finale!\n\n" + string + "\n")
    
    def loop(self):
        while True:
            self.play_game()
            time.sleep(2)

def main(args):
    if len(args) < 2:
        print("Insufficient args")
        return
    if args[1] == 'host':
        if len(args) < 4:
            print("Insufficient args")
            return
        port = int(args[2])
        count = int(args[3])
        server = Server.with_player_count(count, port)
        server.loop()
    elif args[1] == 'connect':
        if len(args) < 4:
            print("Insufficient args")
            return
        host = args[2]
        port = int(args[3])
        client = Client.from_connection(host, port)
        client.loop()
    else:
        print("Unknown argument")
        return


if __name__ == '__main__':
    main(sys.argv)

