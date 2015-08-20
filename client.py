__author__ = 'wwagner'

import logging
from socket import *

logging.basicConfig(filename='ThudClient.log', level=logging.DEBUG)

HOST = '172.17.51.22'
PORT = 8080
BUFFERSIZE = 1024
ADDRESS = (HOST, PORT)



while True:
    data = input('> ')
    if data:
        try:
            tcpCliSock = socket(AF_INET, SOCK_STREAM)
            tcpCliSock.connect(ADDRESS)
        except ConnectionRefusedError:
            logging.debug('Connection to server could not be made.')
        tcpCliSock.send(data.encode())
        data = tcpCliSock.recv(BUFFERSIZE)
        print(data.decode())
        tcpCliSock.close()
    else:
        tcpCliSock.close()
        print("No data to be sent.")

tcpCliSock.close()