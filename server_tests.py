__author__ = 'wwagner'

import unittest
import json
import requests
import subprocess


class LocalServerTest(unittest.TestCase):

    def setUp(self):
        # start the game by hitting the endpoint with an appropriate websocket
        self.start_url = 'http://127.0.0.1:12000/start'
        self.move_url = 'http://127.0.0.1:12000/move'
        self.validate_url = 'http://127.0.0.1:12000/move/validate'
        start_data = json.dumps({"game": "start", "player_one": "Will", "player_two": "Tom"})
        post = requests.post(self.start_url, start_data)
        data = json.loads(post.text)
        self.board = data['board']
        self.player_one = data['player_one']
        self.player_two = data['player_two']
        self.game = data['game']

    def test_start_game(self):
        test_board = json.loads(open('api_test.json').read())["base state"]
        self.assertEqual(self.board, test_board)

    def test_validate_move(self):
        # test simulated moves for checking moves/captures to display in the UI
        move_data = {"game": self.game, "player": self.player_one,
                     "start": [6, 0], "destination": [6, 5]}
        post = requests.post(self.move_url, json.dumps(move_data))
        data = json.loads(post.text)
        self.assertEqual(data, True)

    def test_troll_toss(self):
        # simulate a series of valid and invalid moves and attacks'
        first_move_data = {"game": self.game, "player": self.player_one,
                           "start": [6, 0], "destination": [6, 4]}
        second_move_data = {"game": self.game, "player": self.player_two,
                            "start": [6, 6], "destination": [6, 5]}
        data = json.loads(requests.post(self.move_url, json.dumps(first_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(second_move_data)).text)
        self.assertEqual(data, [[6, 4]])

    def test_toss_dwarf(self):
        first_move_data = {"game": self.game, "player": self.player_one,
                           "start": [10, 1], "destination": [6, 1]}
        second_move_data = {"game": self.game, "player": self.player_two,
                            "start": [6, 6], "destination": [6, 5]}
        third_move_data = {"game": self.game, "player": self.player_one,
                           "start": [11, 2], "destination": [6, 2]}
        fourth_move_data = {"game": self.game, "player": self.player_two,
                            "start": [7, 6], "destination": [6, 6]}
        fifth_move_data = {"game": self.game, "player": self.player_one,
                           "start": [6, 2], "destination": [6, 5]}
        data = json.loads(requests.post(self.move_url, json.dumps(first_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(second_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(third_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(fourth_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(fifth_move_data)).text)
        self.assertEqual(data, [[6, 5]])

    def test_validate_toss(self):
        first_move_data = {"game": self.game, "player": self.player_one,
                           "start": [10, 1], "destination": [6, 1]}
        second_move_data = {"game": self.game, "player": self.player_two,
                            "start": [6, 6], "destination": [6, 5]}
        third_move_data = {"game": self.game, "player": self.player_one,
                           "start": [11, 2], "destination": [6, 2]}
        fourth_move_data = {"game": self.game, "player": self.player_two,
                            "start": [7, 6], "destination": [6, 6]}
        fifth_move_data = {"game": self.game, "player": self.player_one,
                           "start": [6, 2], "destination": [6, 5]}
        data = json.loads(requests.post(self.move_url, json.dumps(first_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(second_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(third_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(fourth_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.validate_url, json.dumps(fifth_move_data)).text)
        print(type(data), data)


class LiveServerTest(unittest.TestCase):

    def setUp(self):
        # start the game by hitting the endpoint with an appropriate websocket
        self.start_url = 'http://192.241.198.50/start'
        self.move_url = 'http://192.241.198.50/move'
        self.validate_url = 'http://192.241.198.50/move/validate'
        start_data = json.dumps({"game": "start", "player_one": "Will", "player_two": "Tom"})
        post = requests.post(self.start_url, start_data)
        data = json.loads(post.text)
        self.board = data['board']
        self.player_one = data['player_one']
        self.player_two = data['player_two']
        self.game = data['game']

    def test_start_game(self):
        test_board = json.loads(open('api_test.json').read())["base state"]
        self.assertEqual(self.board, test_board)

    def test_validate_move(self):
        # test simulated moves for checking moves/captures to display in the UI
        move_data = {"game": self.game, "player": self.player_one,
                     "start": [6, 0], "destination": [6, 5]}
        post = requests.post(self.move_url, json.dumps(move_data))
        data = json.loads(post.text)
        self.assertEqual(data, True)

    def test_troll_toss(self):
        # simulate a series of valid and invalid moves and attacks'
        first_move_data = {"game": self.game, "player": self.player_one,
                           "start": [6, 0], "destination": [6, 4]}
        second_move_data = {"game": self.game, "player": self.player_two,
                            "start": [6, 6], "destination": [6, 5]}
        data = json.loads(requests.post(self.move_url, json.dumps(first_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(second_move_data)).text)
        self.assertEqual(data, [[6, 4]])

    def test_toss_dwarf(self):
        first_move_data = {"game": self.game, "player": self.player_one,
                           "start": [10, 1], "destination": [6, 1]}
        second_move_data = {"game": self.game, "player": self.player_two,
                            "start": [6, 6], "destination": [6, 5]}
        third_move_data = {"game": self.game, "player": self.player_one,
                           "start": [11, 2], "destination": [6, 2]}
        fourth_move_data = {"game": self.game, "player": self.player_two,
                            "start": [7, 6], "destination": [6, 6]}
        fifth_move_data = {"game": self.game, "player": self.player_one,
                           "start": [6, 2], "destination": [6, 5]}
        data = json.loads(requests.post(self.move_url, json.dumps(first_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(second_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(third_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(fourth_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(fifth_move_data)).text)
        self.assertEqual(data, [[6, 5]])

    def test_validate_toss(self):
        first_move_data = {"game": self.game, "player": self.player_one,
                           "start": [10, 1], "destination": [6, 1]}
        second_move_data = {"game": self.game, "player": self.player_two,
                            "start": [6, 6], "destination": [6, 5]}
        third_move_data = {"game": self.game, "player": self.player_one,
                           "start": [11, 2], "destination": [6, 2]}
        fourth_move_data = {"game": self.game, "player": self.player_two,
                            "start": [7, 6], "destination": [6, 6]}
        fifth_move_data = {"game": self.game, "player": self.player_one,
                           "start": [6, 2], "destination": [6, 5]}
        data = json.loads(requests.post(self.move_url, json.dumps(first_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(second_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(third_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.move_url, json.dumps(fourth_move_data)).text)
        self.assertEqual(data, True)
        data = json.loads(requests.post(self.validate_url, json.dumps(fifth_move_data)).text)
        print(type(data), data)