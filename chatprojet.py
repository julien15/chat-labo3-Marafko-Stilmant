#!/usr/bin/env python3
# chat.py
# authors: Julien Stilemant, Oscar Marafko
# inspired of the work of Sebastien Combefis
# contributor: thumb sucking


import socket
import sys
import threading
import time
import os

SERVERADDRESS = (socket.gethostname(), 5000)
CLIENTADDRESS = (socket.gethostname(), 6000)

class Server:
    def __init__(self, host=SERVERADDRESS[0], port=SERVERADDRESS[1]):
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s
        print('Hearing on {}:{}'.format(host, port))
        global whoshere
        whoshere = dict()

    def run(self):
        self.__running = True
        self.__address = None
        threading.Thread(target=self._sendback).start()
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ')+1:].rstrip()
            # Call the command handler

    def _sendback(self):
        while self.__running:
            try:
                data, address = self.__s.recvfrom(1024)
                dt = eval(data.decode())
                if dt[2] == 'online':
                    whoshere[dt[0]] = [address[0], dt[1], dt[2]]
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print('Hearing on {}:{}'.format(SERVERADDRESS[0], SERVERADDRESS[1]))
                    for i in whoshere:
                        print(i, whoshere[i])
                    message = str(whoshere).encode()
                    s = socket.socket(type=socket.SOCK_DGRAM)
                    clientaddress = (address[0], dt[1])
                    totalsent = 0
                    while totalsent < len(message):
                        sent = s.sendto(message[totalsent:], clientaddress)
                        totalsent += sent
                else:
                    try:
                        for i in whoshere:
                            if i == dt[0]:
                                del(whoshere[i])
                                os.system('cls' if os.name == 'nt' else 'clear')
                                print('Hearing on {}:{}'.format(SERVERADDRESS[0], SERVERADDRESS[1]))
                                for i in whoshere:
                                    print(i, whoshere[i])
                    except:
                        pass
            except socket.timeout:
                pass
            except OSError:
                return



class Client:
    def __init__(self, host=CLIENTADDRESS[0], port=CLIENTADDRESS[1]):
        s = socket.socket(type=socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.bind((host, port))
        self.__s = s
        print('Hearing on {}:{}'.format(host, port))
        print('use :"/help" to get help')
        print('use :"/exit" command to close the program')
        global username
        username = ""

    def run(self):
        handlers = {
            '/exit': self._exit,
            '/quit': self._quit,
            '/join': self._join,
            '/send': self._send,
            '/nick': self._nick,
            '/connect': self._connect,
            '/help': self._help,
            '/clear': self._clear
        }
        self.__running = True
        self.__address = None
        threading.Thread(target=self._receive).start()
        while self.__running:
            line = sys.stdin.readline().rstrip() + ' '
            # Extract the command and the param
            command = line[:line.index(' ')]
            param = line[line.index(' ')+1:].rstrip()
            # Call the command handler
            if command in handlers:
                try:
                    handlers[command]() if param == '' else handlers[command](param)
                except:
                    print("Erreur lors de l'exécution de la commande.")
            else:
                print('Unknown command:', command)

    def _connect(self):
        #connection au serveur
        if username == "":
            name = input("please choose a username to talk in on the chat: ")
            self._nick(name)
        s = socket.socket(type=socket.SOCK_DGRAM)
        address = (SERVERADDRESS[0], SERVERADDRESS[1])
        name = [username, CLIENTADDRESS[1], 'online']
        message = str(name).encode()
        totalsent = 0
        while totalsent < len(message):
            sent = s.sendto(message[totalsent:], address)
            totalsent += sent

    def _exit(self):
        #quite le programme après avoir envoyé un changement de statut de connection
        s = socket.socket(type=socket.SOCK_DGRAM)
        address = (SERVERADDRESS[0], SERVERADDRESS[1])
        name = [username, CLIENTADDRESS[1], 'offline']
        message = str(name).encode()
        totalsent = 0
        while totalsent < len(message):
                sent = s.sendto(message[totalsent:], address)
                totalsent += sent
        self.__running = False
        self.__address = None
        self.__s.close()

    def _quit(self):
        #coupe la connection avec un autre utlilisateur
        self.__address = None

    def _join(self, param):
        tokens = param.split(' ')
        if len(tokens) == 2:
            try:
                self.__address = (socket.gethostbyaddr(tokens[0])[0], int(tokens[1]))
                print('Connecté à {}:{}'.format(*self.__address))
            except OSError:
                print("Erreur lors de l'envoi du message.")

    def _send(self, param):
        #envoie un message à un autre utilisateur
        if self.__address is not None:
            try:
                if username == "":
                    name = input("please choose a username to talk in on the chat: ")
                    self._nick(name)
                param = username+" : " + param
                message = param.encode()
                totalsent = 0
                while totalsent < len(message):
                    sent = self.__s.sendto(message[totalsent:], self.__address)
                    totalsent += sent
                print("message sent")
            except OSError:
                print('Erreur lors de la reception du message.')

    def _receive(self):
        #boucle de réception
        while self.__running:
            try:
                data, address = self.__s.recvfrom(1024)
                print(data.decode())
            except socket.timeout:
                pass
            except OSError:
                return

    def _nick(self, param):
        global username
        username = param

    def _clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Hearing on {}:{}'.format(CLIENTADDRESS[0], CLIENTADDRESS[1]))
        print('use for :"/help" for help')
        print('use :"/exit" command to close the program')

    def _help(self):
        print('Possible commands:')
        print('/exit', 'to exit the chat application')
        print('/connect', 'to connect to the server and know who''s connected')
        print('/quit', 'to quit a chatroom')
        print('/join', 'to join a chat room example:"/join 28.12.18.04 5000"')
        print('/send', 'to send a message to members of the same chatroom example:"/send Hello World')
        print('/clear', 'to clear the command prompt')
        print('/nick', 'to chose a nickname example:"/nick Georges')

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'server':
        Server().run()
    elif len(sys.argv) > 3 and sys.argv[1] == 'client':
        Client(sys.argv[2:]).run()
    else:
        Client().run()
