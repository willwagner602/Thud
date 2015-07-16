__author__ = 'wwagner'

import logging
from socket import *
from time import ctime

logging.basicConfig(filename='ThudServer.log', level=logging.DEBUG)

HOST = ''
PORT = 12000
BUFFERSIZE = 1024
ADDRESS = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDRESS)
tcpSerSock.listen(5)

while True:
    try:
        print('waiting for connection . . . ')
        tcpCliSock, addr = tcpSerSock.accept()
        print('. . . connected from: ', addr)

        while True:
            data = tcpCliSock.recv(BUFFERSIZE)
            if not data:
                break
            message = '{} {}'.format(ctime(), data.decode())
            tcpCliSock.send(message.encode())

        tcpCliSock.close()

    except ConnectionResetError:
        logging.debug('Connection to client dropped.')

tcpSerSock.close()