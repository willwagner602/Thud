__author__ = 'wbw'

from datetime import date, datetime
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import logging
import Thud
import sys


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")


class VersionHandler(BaseHandler):
    def get(self):
        response = {'name': 'ThudServer',
                    'version': '1.0',
                    'last_build': date.today().isoformat()}
        self.write(tornado.escape.json_encode(response))


class GetGameByIdHandler(BaseHandler):
    def get(self, id):
        response = {"id": 1,
                    "Name": "Thud",
                    "release_date": date.today().isoformat()}
        self.write(tornado.escape.json_encode(response))


class StartGameWithPlayers(BaseHandler):
    def post(self):
        start_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_start(start_data)
        self.write(tornado.escape.json_encode(response))


class ExecuteMove(BaseHandler):
    def post(self):
        move_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_move(move_data)
        self.write(tornado.escape.json_encode(response))


class ValidateMove(BaseHandler):
    def post(self):
        move_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_move(move_data, test=True)
        self.write(tornado.escape.json_encode(response))


class GetBoardState(BaseHandler):
    def post(self):
        game = tornado.escape.json_decode(self.request.body)
        response = game_manager.report_game_state(game)
        self.write(tornado.escape.json_encode(response))


class EndGame(BaseHandler):
    def post(self):
        end_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_end(end_data)
        self.write(tornado.escape.json_encode(response))


class PlayerConnection(tornado.websocket.WebSocketHandler):
    #ToDo:
    # Receive player name
    # Add playername to list
    # Return playerlist (without added name)
    # Receive player name, opponent name
    # Check that both are still in list
    # Remove both from list
    # Start game, return to both

    def check_origin(self, origin):
        # ToDo: only allow trusted domains?
        return True

    def open(self, player_id):
        self.player_id = player_id
        print("{}: Websocket opened for player {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                                                          player_id))
        logging.debug("{}: Websocket opened for player {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                                                                  player_id))
        player_list = game_manager.add_player_to_server(self.player_id, self)
        print("Reported player list: ", player_list)
        if player_list != False:
            self.write_message(tornado.escape.json_encode(["list", player_list]))
        else:
            self.write_message(tornado.escape.json_encode("Duplicate player name."))
            self.close()

    def on_message(self, message):
        print("Message:", message)
        print(tornado.escape.json_decode(message), type(tornado.escape.json_decode(message)), self.player_id)
        response = game_manager.process_socket_message(tornado.escape.json_decode(message), self.player_id)
        logging.debug("{}: Message {} received response {}.".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                                                                    message, response))
        print("Sending response: ", response)
        self.write_message(tornado.escape.json_encode(response))

    def send_message(self, message):
        print("Sending message: {}".format(message))
        self.write_message(tornado.escape.json_encode(message))

    def on_close(self):
        game_manager.remove_player_from_server(self.player_id)
        print("{}: Websocket closed for player {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                                                          self.player_id))
        logging.debug("{}: Websocket closed for player {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                                                                  self.player_id))


class TestWS(tornado.websocket.WebSocketHandler):

    sockets = []

    def check_origin(self, origin):
        # ToDo: only allow trusted domains?
        return True

    def open(self, player_id):
        print("Websocket opened for player", player_id)
        self.sockets.append(self)
        print(self.sockets)

    def on_message(self, message):
        print(tornado.escape.json_encode("You said " + message))
        self.write_message(tornado.escape.json_encode("You said " + message))

    def on_close(self):
        print("Websocket closed")


def run_server(port):

    application = tornado.web.Application([
        (r"/getgamebyid/([0-9]+)", GetGameByIdHandler),
        (r"/version", VersionHandler),
        (r"/start", StartGameWithPlayers),
        (r"/move", ExecuteMove),
        (r"/move/validate", ValidateMove),
        (r"/game", GetBoardState),
        (r"/match/([A-Za-z0-9]+)", PlayerConnection),
        (r"/websocket/([A-Za-z0-9]+)", TestWS)
    ])

    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        PORT = int(sys.argv[1])
    except (TypeError, IndexError):
        PORT = 80
    print("Thud server starting on port ", PORT)

    # start the game manager BEFORE the webserver
    game_manager = Thud.GameManager()
    run_server(PORT)


