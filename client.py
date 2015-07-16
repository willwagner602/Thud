__author__ = 'wwagner'

import logging
from socket import *

logging.basicConfig(filename='ThudClient.log', level=logging.DEBUG)

HOST = 'localhost'
PORT = 12000
BUFFERSIZE = 1024
ADDRESS = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)
try:
    tcpCliSock.connect(ADDRESS)
except ConnectionRefusedError:
    logging.debug('Connection to server could not be made.')

while True:
    try:
        data = input('> ')
        if not data:
            break
        tcpCliSock.send(data.encode())
        data = tcpCliSock.recv(BUFFERSIZE)
        if not data:
            break
        print(data.decode())

    except ConnectionResetError:
        logging.debug('Connection to server dropped.')

tcpCliSock.close()