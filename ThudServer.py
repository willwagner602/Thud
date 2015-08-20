__author__ = 'wbw'

from datetime import date
import tornado.escape
import tornado.ioloop
import tornado.web
import logging
import Thud

logging.basicConfig(filename='ThudSocketServer.log', level=logging.DEBUG)


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")


class VersionHandler(BaseHandler):
    def get(self):
        response = { 'version': '1',
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


class ValidateMove(BaseHandler):
    def post(self):
        move_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_move(move_data)
        self.write(tornado.escape.json_encode(response))

class EndGame(BaseHandler):
    def post(self):
        end_data = tornado.escape.json_decode(self.request.body)
        response = game_manager.process_end(end_data)
        self.write(tornado.escape.json_encode(response))


def runserver(port=80):

    PORT = port

    game_manager = Thud.GameManager()

    application = tornado.web.Application([
        (r"/getgamebyid/([0-9]+)", GetGameByIdHandler),
        (r"/version", VersionHandler),
        (r"/start", StartGameWithPlayers),
        (r"/move", ValidateMove)
    ])

    application.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()