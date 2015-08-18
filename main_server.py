__author__ = 'wbw'

import socket_server
import Thud

if __name__ == "__main__":
    game = Thud.GameManager()
    server = socket_server.SocketServer(game)
    server.run_socket_server()