__author__ = 'wbw'

from datetime import date
from django.http import HttpResponse
from Thud import Thud
from django.core import serializers
import json

game_manager = Thud.GameManager()


def get_version(request):
    response = {'name': 'ThudServer',
                'version': '1.0',
                'last_build': date.today().isoformat()}
    return HttpResponse(json.dumps(response))


def get_game_by_id_handler(request, game_id):
    response = {"id": 1,
                "Name": "Thud",
                "release_date": date.today().isoformat()}
    return HttpResponse(serializers.serialize('json', response))


def StartGameWithPlayers(request):
    print('request: ', vars(request))
    print(request.body.decode('utf-8'))
    start_data = json.loads(request.body.decode('utf-8'))
    print("start data", start_data)
    response = game_manager.process_start(start_data)
    print('response: ', response)
    return HttpResponse(json.dumps(response))


def ExecuteMove(request):
    move_data = json.loads(request)
    response = game_manager.process_move(move_data)
    return HttpResponse(json.dumps(response))


def ValidateMove(request):
    move_data = json.loads(request)
    response = game_manager.process_move(move_data, test=True)
    return HttpResponse(json.dumps(response))


def GetBoardState(request):
    game = json.loads(request)
    response = game_manager.report_game_state(game)
    return HttpResponse(json.dumps(response))


def SaveGame(request):
    game = json.loads(request)
    response = game_manager.process_save(game)
    return HttpResponse(json.dumps(response))


def LoadGame(request):
    game = json.loads(request)
    response = game_manager.process_load(game)
    return HttpResponse(json.dumps(response))


def EndGame(request):
    end_data = json.loads(request)
    response = '' # game_manager.process_end(end_data)
    return HttpResponse(json.dumps(response))


# def PlayerConnection():
#     #ToDo:
#     # Receive player name
#     # Add playername to list
#     # Return playerlist (without added name)
#     # Receive player name, opponent name
#     # Check that both are still in list
#     # Remove both from list
#     # Start game, return to both
#
#     def check_origin(self, origin):
#         # ToDo: only allow trusted domains?
#         return True
#
#     def open(self, player_id):
#         self.player_id = player_id
#         logging.debug("{}: Websocket opened for player {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
#                                                                   player_id))
#         player_list = game_manager.add_player_to_server(self.player_id, self)
#         logging.debug("{}: Reported player list {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
#                                                                   player_list))
#         if player_list != False:
#             self.write_message(json.dumps(["list", player_list]))
#         else:
#             self.write_message(json.dumps("Duplicate player name."))
#             self.close()
#
#     def on_message(self, message):
#         response = game_manager.process_socket_message(json.loads(message), self.player_id)
#         logging.debug("{}: Message {} received, response {}.".format(
#             datetime.now().strftime('%d/%m/%y %H:%M:%S'),
#             message, response))
#         self.write_message(json.dumps(response))
#
#     def send_message(self, message):
#         self.write_message(json.dumps(message))
#
#     def on_close(self):
#         game_manager.remove_player_from_server(self.player_id)
#         logging.debug("{}: Websocket closed for player {}".format(datetime.now().strftime('%d/%m/%y %H:%M:%S'),
#                                                                   self.player_id))