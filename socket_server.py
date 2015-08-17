__author__ = 'wwagner'

import logging
from socket import *
from time import ctime
from datetime import datetime

logging.basicConfig(filename='ThudSocketServer.log', level=logging.DEBUG)

HOST = ''
PORT = 12000
BUFFERSIZE = 1024
ADDRESS = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDRESS)


class SocketServer:

    def __init__(self, game):
        self.game = game

    def run_socket_server(self):
        while True:
            try:
                # wait until tcpSerSock returns a connection
                tcpSerSock.listen(10)
                print('waiting for connection . . . ')
                tcpCliSock, addr = tcpSerSock.accept()
                print('. . . connected from: ', addr)
                data = tcpCliSock.recv(BUFFERSIZE)
                message = '{} {}'.format(ctime(), data.decode())
                tcpCliSock.send(message.encode())
                tcpCliSock.close()

            except ConnectionResetError:
                logging.debug('Connection to client dropped.')

    def manage_socket_server(self):
        while True:
            try:
                self.run_socket_server()
            except Exception as e:
                logging.debug("{}: {}".format(datetime.now().strftime("%m/%d/%y %H:%M:%S", e)))
                self.run_socket_server()