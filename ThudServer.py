__author__ = 'wbw'

from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
import logging
import Thud
import sys

logging.basicConfig(filename='ThudSocketServer.log', level=logging.DEBUG)


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


class EndGame(BaseHandler):
    def post(self):
        end_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_end(end_data)
        self.write(tornado.escape.json_encode(response))


def run_server(port):

    application = tornado.web.Application([
        (r"/getgamebyid/([0-9]+)", GetGameByIdHandler),
        (r"/version", VersionHandler),
        (r"/start", StartGameWithPlayers),
        (r"/move", ExecuteMove),
        (r"/move/validate", ValidateMove),
    ])

    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    try:
        PORT = int(sys.argv[1])
    except (TypeError, IndexError):
        PORT = 80
    print("Thud server starting on port ", PORT)

    run_server(PORT)
    game_manager = Thud.GameManager()


