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

# forever
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

tcpSerSock.close()