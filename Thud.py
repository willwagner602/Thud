__author__ = 'wwagner'

import logging
import datetime
import random
import string

#database testing stuff
import sqlite3
from pathlib import Path
import json
from types import *

logging.basicConfig(filename='ThudLog.log', level=logging.DEBUG)


class Board(object):

    def __init__(self):
        self.name = 'Gameboard'
        self.squares = [[str(x) + ',' + str(y) for y in range(15)] for x in range(15)]
        self.moves = []
        self.piece_id = 0
        self.populate_invalid_moves()
        self.units = self.populate_units()

    def __getitem__(self, key):
        return self.squares[key]

    def __setitem__(self, key, value):
        self.squares[key] = value

    def generate_piece_id(self):
        self.piece_id += 1
        return self.piece_id

    def print_board(self):
        for row in zip(*self.squares[::1]):
            row_text = ""
            for square in row:
                if isinstance(square, Piece):
                    text = square.type
                    buffer = "  "
                    row_text += buffer + text + buffer
                elif square == 0:
                    row_text += "    *    "
                else:
                    buffer = int((9 - len(square))/2) * " "
                    row_text += buffer + square + str((9 - len(buffer+square)) * " ")
            print(row_text)

    def populate_invalid_moves(self):
        invalid_flag = 0
        # fill 5x5 equilateral triangles at 4 corners of board
        for y in range(15):
            if y < 5:
                row_squares = range(5-y, 10+y)
                for x in range(15):
                    if x not in row_squares:
                        self.squares[y][x] = invalid_flag
            elif y > 9:
                row_squares = range((1+y-10), 24-y)
                for x in range(15):
                    if x not in row_squares:
                        self.squares[y][x] = invalid_flag
        # Place center stone
        self.squares[7][7] = 0

    def populate_units(self):
        units = []
        # add dwarves to edges
        for row in range(len(self.squares)):
            for column in range(len(self.squares[row])):
                # don't add any dwarves to the center row
                if not self.squares[row][column] or row == 7:
                    pass
                # if it's the first or last square in a complete row, add a dwarf
                elif column in (0, 14):
                    self.squares[row][column] = Dwarf(row, column, self.generate_piece_id())
                    units.append(self.squares[row][column])
                # if it's the first or last square in a row with blocked squares, add a dwarf
                elif self.squares[row][column-1] == 0 or self.squares[row][column+1] == 0:
                    self.squares[row][column] = Dwarf(row, column, self.generate_piece_id())
                    units.append(self.squares[row][column])
                # the final dwarves fill out the top and bottom rows except for the center space
                elif row in (0, 14) and column in (6, 8):
                    self.squares[row][column] = Dwarf(row, column, self.generate_piece_id())
                    units.append(self.squares[row][column])

        # add trolls to center rows and columns around the center stone
        for row in range(6, 9):
            for column in range(6, 9):
                if self.squares[row][column]:
                    self.squares[row][column] = Troll(row, column, self.generate_piece_id())
                    units.append(self.squares[row][column])
        return units

    def move_piece_on_board(self, piece, x, y):
        piece_x = piece.x
        piece_y = piece.y
        self.squares[x][y] = piece
        self.squares[piece_x][piece_y] = str(piece_x) + ',' + str(piece_y)
        return True

    def get_piece(self, x, y):
        tenant = self.squares[x][y]
        if isinstance(tenant, Piece):
            return tenant
        else:
            return False

    def set_square(self, x, y, value):
        self.squares[x][y] = value

    def capture_piece(self, piece):
        x, y = piece.x, piece.y
        piece.capture()
        self.set_square(x, y, str(x) + ',' + str(y))


class GameManager(object):
    """
    Manages the interaction of players with games and the database
    Takes moves in the format (gametoken, playertoken, start, destination)
    """

    def __init__(self):
        logging.debug('Game Manager started at {}.'.format(datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')))
        self.name = 'Game Manager'
        self.active_games = {}
        self.last_cleared = datetime.datetime.now()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def start_game(self, player_one, player_two):
        """
        Generates a game token and individual player tokens for authentication. Saves the new game to the database.
        """
        game = Game(player_one, player_two)
        game_token = self.generate_game_token(game)
        self.active_games[game_token] = game
        self.save_game(game_token,player_one,player_two)
        logging.debug("{}: Game {} start with players {}, {}".format(
            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), game_token, game.player_one.token,
            game.player_two.token))
        return game_token, game.player_one.token, game.player_two.token

    def generate_game_token(self, game, max_game=1):
        # ToDo: query the database along with active_games for the highest game token played by these two players
        token = game.player_one.name + game.player_two.name + str(max_game)
        try:
            existing_game = self.active_games[token]
            max_game += 1
            return self.generate_game_token(game, max_game)
        except KeyError:
            return token

    def end_game(self, game_token, player_one_token, player_two_token):
        try:
            game = self.active_games[game_token]
            if game.player_one.token == player_one_token and game.player_two.token == player_two_token:
                # todo: push game data to database, remove game from the list of active games
                return True
        except KeyError:
            return False

    def save_game(self, game_id, *players):
        '''
        Manages game saves. Saves gametoken, player1, player2, turn number, and the game board state to sql database.
        Executed upon game creation in Thud.GameManager.start_game and every turn in Thud.GameManager.process_move.
        It might be possible to ignore the json conversion entirely and load the string from self.report_game_state(game_id) directly
        to the database. Although serializing data into a single cell is generally frowned upon for SQL, I think it's okay to do it in
        this case because there's never an instance where we'd only want to retrieve parts of the board.
        '''
        # ToDo: 1) Saving all the game data: player names, races, possibly turn history, etc. 2) Figure out how to handle changing players in a game
        # 3) Break up repetitive work into new methods (e.g. loading database). 1) Exception catching for: connecting to database, writing to database, closing database.
        game_state = json.dumps(self.report_game_state(game_id), separators=(',', ': ')) # Production: Compact encoding.
        gamedbpath = Path('.\games.db')
        turn = len(self.active_games[game_id].move_history)
        player_one = self.active_games[game_id].player_one.token
        player_two = self.active_games[game_id].player_two.token

        # Create the sqlite database if it doesn't exist and connect to it. There also might be a cleaner way to do this part.
        if not gamedbpath.is_file():
            game_db = sqlite3.connect('.\games.db')
            c_game_db = game_db.cursor()
            c_game_db.execute('''CREATE TABLE Games (gametoken text, player1 text, player2 text, turn int, board text)''')
        else:
            game_db = sqlite3.connect('.\games.db')
            c_game_db = game_db.cursor()

        c_game_db.execute("SELECT ROWID FROM Games WHERE gametoken = (?) ",(game_id,))
        rowid = c_game_db.fetchone()

        if rowid:
            print("Saving Game")
            c_game_db.execute("UPDATE Games SET board = (?) WHERE ROWID = (?)",(game_state,rowid[0]))
            c_game_db.execute("UPDATE Games SET turn = (?) WHERE ROWID = (?)",(turn,rowid[0]))
            c_game_db.execute("UPDATE Games SET player1 = (?) WHERE ROWID = (?)",(player_one,rowid[0]))
            c_game_db.execute("UPDATE Games SET player2 = (?) WHERE ROWID = (?)",(player_two,rowid[0]))
        else:
            # Assuming this is only done upon game creation, we need to run tests to make sure this is okay
            print("Creating Game")
            c_game_db.execute("INSERT INTO Games VALUES (?,?,?,?,?)",(game_id,player_one,player_two,0,game_state))

        game_db.commit()
        game_db.close()
    
    def load_game(self, game_id):
        '''
        Retrieves player tokens the turn number, and board from database. We need to write a read_game_state
        method that does the reverse of GameManager.report_game_state so that the board is usable by the game engine.
        '''
        # ToDo: In addition to stuff from save_game: Exception catching for: can't find requested game token, closing
        # database, converting game board to engine readable.
        try:
            game_db = sqlite3.connect('.\games.db')
        except:
            print("Error accessing the database.")
        c_game_db = game_db.cursor()

        c_game_db.execute("SELECT player1 FROM Games WHERE gametoken = (?) ",(game_id,))
        player_one = c_game_db.fetchone()[0]
        c_game_db.execute("SELECT player2 FROM Games WHERE gametoken = (?) ",(game_id,))
        player_two = c_game_db.fetchone()[0]
        c_game_db.execute("SELECT turn FROM Games WHERE gametoken = (?) ",(game_id,))
        turn = c_game_db.fetchone()[0]
        c_game_db.execute("SELECT board FROM Games WHERE gametoken = (?) ",(game_id,))
        game_state = json.loads(c_game_db.fetchone()[0])

        self.active_games[game_id] = Game(player_one,player_two)
        self.read_game_state(game_id,game_state)
        self.active_games[game_id].move_history = [None] * turn
        self.active_games[game_id].player_one.token = player_one
        self.active_games[game_id].player_two.token = player_two

        game_db.close()
    
    def read_game_state(self, game_id, game_state):
        game_board = self.active_games[game_id].board

        for x, column in enumerate(self.active_games[game_id].board):
            before = str(self.active_games[game_id].board[x])
            for y, square in enumerate(column):
                if game_state[str(x)][y]['type'] == 'null':
                    square = 0
                elif game_state[str(x)][y]['type'] == 'open':
                    square = str(x) + ',' + str(y)
                else:
                    square.type = game_state[str(x)][y]['type']
                    square.id = game_state[str(x)][y]['id']
            after = str(self.active_games[game_id].board[x])

    def report_game_state(self, game_id):
        """
        Returns a json representation of the current game state
        """
        # This method has some weird ass behaviors, sometimes the id and the type get switched in order for no apparent reason and the rows
        # are never in order due to using board_state[str(x)]
        board_state = {}
        for x, column in enumerate(self.active_games[game_id].board):
            row_state = []
            for square in column:
                if isinstance(square, Piece):
                    row_state.append({"id": square.id, "type": square.type})
                elif square == 0:
                    row_state.append({"id": "null", "type": "null"})
                else:
                    row_state.append({"id": "null", "type": "open"})
            board_state[str(x)] = row_state
        return board_state

    def process_move(self, move_data, test=False):
        """
        Making a move:
            {"game": "correct_game_token",
            "player":"correct_player_token",
            "start": [x, y],
            "destination": [x, y]}
        Returns True, False, or [(x, y), ] of captures for an attack
        """
        try:
            game_token = move_data["game"]
            player_token = move_data["player"]
            start = move_data["start"]
            destination = move_data["destination"]
            if game_token in self.active_games:
                logging.debug("{}: Game {} found, attempting move from {} to {}.".format(
                    game_token, datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), start, destination))
                game = self.active_games[game_token]
                # Added turn by turn saving here, I figured it didn't belong in the "Game" object.
                self.save_game(game_token)
                return game.execute_move(player_token, start, destination, test)
            else:
                logging.debug("{}: Game {} not found.".format(game_token,
                                                              datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
                return False
        except KeyError as e:
            return "Bad JSON data {} as part of {}.".format(e, move_data)

    def process_start(self, start_data):
        try:
            player_one = start_data["player_one"]
            player_two = start_data["player_two"]
            game, player_one_token, player_two_token = self.start_game(player_one, player_two)
            return {"game": game, "board": self.report_game_state(game),
                    "player_one": player_one_token, "player_two": player_two_token}
        except KeyError:
            return "Bad JSON data."

    def clear_old_games(self):
        if datetime.datetime.now() - self.last_cleared > datetime.timedelta(hours=2):
            for game in self.active_games:
                if datetime.datetime.now() - game.last_accessed > datetime.timedelta(hours=2):
                    del self.active_games[game]
            return True
        else:
            return False


class Game(object):
    """
    Contains all the game logic - moving pieces around the board, capturing and removing pieces.
    """

    def __init__(self, player_one, player_two):
        self.name = ''
        self.board = Board()
        self.player_one = Player(player_one, self.generate_player_token(), "D")
        self.player_two = Player(player_two, self.generate_player_token(), "T")
        self.last_accessed = datetime.datetime.now()
        self.move_history = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def store_move(self, start, destination):
        """
        Save a move to the move history
        :param start:
        :param destination:
        :return:
        """
        self.move_history.append((start, destination))

    @staticmethod
    def generate_player_token():
        """
        Generates a 20 character token used for identifying players
        """
        token = ''
        characters = string.ascii_letters + string.digits + string.punctuation
        for x in range(20):
            token += random.choice(characters)
        return token

    def validate_player(self, player_token, piece):
        """
        Used to ensure the correct player is making a move - returns False for players moving out of order
        :param player_token:
        :return bool:
        """
        # Dwarf player starts turn 1, players alternate for rest of game
        player_one_turn = (len(self.move_history) + 1) % 2 > 0
        if player_one_turn and player_token == self.player_one.token:
            logging.debug("{}: Validated Dwarf player.".format(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
            if self.player_one.race == piece.type:
                return True
            else:
                logging.debug("{}: Dwarf player attempted to move Troll.".format(
                    datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
        elif not player_one_turn and player_token == self.player_two.token:
            logging.debug("{}: Validated Troll player.".format(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
            if self.player_two.race == piece.type:
                return True
            else:
                logging.debug("{}: Troll player attempted to move Dwarf.".format(
                    datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
        return False

    def validate_clear_path(self, piece, destination):
        """
        Checks all spaces between the piece and destination square to ensure there are not intervening
        pieces or impassable spaces.
        :param piece:
        :param destination:
        :return bool:
        """
        logging.debug("{}: Checking clear path from {} at {},{} to {}".format(
            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), piece, piece.x, piece.y, str(destination)))
        if isinstance(destination, Troll):
            destination_x, destination_y = destination.x, destination.y
        else:
            destination_x, destination_y = destination

        # don't look at the starting space because we know there's a piece there
        if piece.x - destination_x > 0:
            x_travel = list(range(piece.x - 1, destination_x, -1))
        else:
            x_travel = list(range(piece.x + 1, destination_x))
        if piece.y - destination_y > 0:
            y_travel = list(range(piece.y - 1, destination_y, -1))
        else:
            y_travel = list(range(piece.y + 1, destination_y))

        logging.debug("Move ranges: x - {}, y - {}".format(','.join(map(str, x_travel)), ','.join(map(str, y_travel))))

        if not x_travel:
            logging.debug("Horizontal move calculated along x == {}".format(piece.x))
            x_travel = [piece.x for x in range(0, len(y_travel))]
        if not y_travel:
            logging.debug("Vertical move calculated along y == {}".format(piece.y))
            # ToDo: figure out if this is necessary as a list comprehension
            y_travel = [piece.y for x in range(0, len(x_travel))]
        # move is only 1 square, is already validated by earlier functions
        if not x_travel and not y_travel:
            return True

        travel_squares = list(zip(x_travel, y_travel))
        logging.debug('Checking squares in path {}'.format(', '.join(map(str, travel_squares))))
        for x, y in travel_squares:
            if isinstance(self.board[x][y], Piece) or not self.board[x][y]:
                return False
        return True

    def validate_dwarf_attack(self, piece, target):
        """
        Used to pass back the target of a dwarf attack.
        :param piece:
        :param target:
        :return list:
        """
        if self.validate_throw(piece, target) and self.validate_clear_path(piece, target):
            x, y = target.x, target.y
            return [self.board.get_piece(x, y), ]
        else:
            logging.debug("Error: not a valid dwarf attack  {}, {} to {}, {}".format(piece.x, piece.y, target.x, target.y))
            return False

    def validate_dwarf_move(self, piece, destination):
        """
        Used to check that a Dwarf move is not blocked by the Thud stone or another creature
        :param piece:
        :param destination:
        :return bool:
        """
        x, y = destination
        if abs(piece.x - x) == abs(piece.y - y) or piece.x == x or piece.y == y:
            return self.validate_clear_path(piece, destination)
        else:
            logging.debug("Error: not a valid dwarf move from {}, {} to {}, {}".format(piece.x, piece.y, x, y))
            return False

    def validate_throw(self, piece, target):
        """
        Used for checking both Dwarf throws and Troll shoves, confirms that enough allied pieces
        are in a line to allow the throw/shove.
        :param piece:
        :param target:
        :return bool:
        """
        # calculate inverse target square to check for line of creatures
        if isinstance(target, Piece):
            x = target.x
            y = target.y
        else:
            x, y = target
        delta_x = piece.x - x
        delta_y = piece.y - y

        logging.info("{}: Checking valid attack at {},{}.".format(
            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), x, y))

        if delta_x > 0:
            x_check = list(range(piece.x + 1, piece.x + delta_x, 1))
        else:
            x_check = list(range(piece.x - 1, piece.x + delta_x, -1))

        if delta_y > 0:
            y_check = list(range(piece.y + 1, piece.y + delta_y, 1))
        else:
            y_check = list(range(piece.y - 1, piece.y + delta_y, -1))

        if not x_check:
            x_check = [piece.x for x in range(0, len(y_check))]
        if not y_check:
            y_check = [piece.y for x in range(0, len(x_check))]

        for x in x_check:
            if x < 0 or x > 14:
                return False

        for y in y_check:
            if y < 0 or y > 14:
                return False

        check_squares = list(zip(x_check, y_check))

        logging.debug("Delta x: {}, Delta y: {}, List of x to check: {}, List of y to check: {}".format(
            delta_x, delta_y, x_check, y_check
        ))

        logging.debug('Checking squares {} for friendly units to toss.'.format(', '.join(map(str, check_squares))))
        for x, y in check_squares:
            if not isinstance(self.board.get_piece(x, y), type(piece)):
                logging.debug("Error not enough friendly pieces in line for throw.")
                return False
        return True

    def validate_troll_move_or_attack(self, piece, target):
        """
        Differentiates between troll moves and attacks, returns a list of dwarves if it's an attack,
        True for a move, and False for an invalid move.
        :param piece:
        :param target:
        :return list | bool:
        """
        attacks = self.find_adjacent_dwarves(target)
        x, y = target
        single_space_move = (abs(piece.x - x) <= 1 and abs(piece.y - y) <= 1)
        logging.debug("{}: Validating troll move or attack at {},{}. Single Space Move is {}".format(
            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), piece.x, piece.y, single_space_move))
        if attacks and single_space_move:
            logging.debug("Checking single space attack at {},{} against {}.".format(x, y, ','.join(map(str, attacks))))
            return attacks
        elif single_space_move:
            logging.debug("Single space move from {},{} to {}, {}.".format(piece.x, piece.y, x, y))
            return True
        elif attacks:
            logging.debug("Checking shove attack at {},{} against {}.".format(x, y, ','.join(map(str, attacks))))
            if self.validate_throw(piece, target) and self.validate_clear_path(piece, target):
                return attacks
            else:
                return False
        else:
            return False

    def find_adjacent_dwarves(self, destination):
        """
        Determines whether a square has neighboring dwarves, and thus is a viable
        attack target for a troll.  Returns False if no dwarves found, or a list
        of dwarves to attack if they are found.
        :param destination:
        :return list | bool:
        """
        # given target square, return list of adjacent dwarf objects, or false
        dest_x, dest_y = destination
        check_squares = []
        targets = []
        for x_value in range(dest_x-1, dest_x+2):
            for y_value in range(dest_y-1, dest_y+2):
                check_squares.append((x_value, y_value))
        logging.debug("{}: Checking for dwarves at {}.".format(
            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'),', '.join(map(str, check_squares))))
        for x, y in check_squares:
            try:
                square = self.board[x][y]
                if isinstance(square, Dwarf):
                    targets.append(square)
            except IndexError:
                logging.debug("Checked for dwarf out of bounds at {},{}.".format(x, y))
        if targets:
            return targets
        else:
            return False

    def validate_destination(self, destination):
        """
        Ensures a the destination for a move is on the board
        :param destination:
        :return bool:
        """
        x, y = destination
        if x < 0 or y < 0:
            return False
        try:
            destination = self.board[x][y]
            if destination == 0:
                return False
            else:
                return True
        except IndexError:
            return False

    def validate_move(self, start, destination):
        """
        The highest level function for checking the validity of a move.
        Returns False if the destination isn't valid, or passes back the
        values returned by the move/attack checking functions.
        :param start:
        :param destination:
        :return list | bool:
        """

        x, y = start
        piece = self.board.get_piece(x, y)
        if not piece:
            return False

        dest_x, dest_y = destination

        if self.validate_destination(destination):
            target = self.board.get_piece(dest_x, dest_y)
            logging.debug("{}: Validating {} at {}, {} destination of {}, {}.".format(
                datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), piece, x, y, dest_x, dest_y
            ))

            # is a dwarf attack or invalid, because only dwarves can move on top of another piece
            if isinstance(target, Piece):
                if isinstance(piece, Dwarf) and isinstance(target, Troll):
                    logging.debug(
                        "Validated dwarf attack with piece {} at {}, {} destination of {}, {}.".format(
                            piece, x, y, dest_x, dest_y))
                    dwarf_attack = self.validate_dwarf_attack(piece, target)
                    return dwarf_attack
                # trolls cannot move on top of another piece
                else:
                    return False

            # is a move - see the dwarf and troll move rules
            else:
                target = destination
                if isinstance(piece, Dwarf):
                    logging.debug("Validated moving {} at {}, {} destination of {}, {}.".format(piece, x, y,
                                                                                                  dest_x, dest_y))
                    return self.validate_dwarf_move(piece, target)
                elif isinstance(piece, Troll):
                    logging.debug("Validated moving {} at {}, {} destination of {}, {}.".format(piece, x, y,
                                                                                                  dest_x, dest_y))
                    return self.validate_troll_move_or_attack(piece, target)
        else:
            return False

    def remove_captured_piece(self, target):
        x, y = target.x, target.y
        target.capture()
        self.board[x][y] = (x, y)
        return True

    def execute_move(self, player_token, start, destination, test=False):
        self.record_access()
        x, y = start
        piece = self.board.get_piece(x, y)
        if piece and self.validate_player(player_token, piece):
            move = self.validate_move(start, destination)
            if isinstance(move, list) and not test:
                for target in move:
                    self.board.capture_piece(target)
                self.move(piece, destination)
                logging.debug("Captured pieces at {}".format(', '.join([piece.type for piece in move])))
                return [(piece.x, piece.y) for piece in move]
            elif move and not test:
                logging.debug("Valid move - moving {} at {}, {} to {}".format(
                    piece.type, piece.x, piece.y, destination))
                self.move(piece, destination)
                return True
            elif move and test:
                if isinstance(move, list):
                    return [(piece.x, piece.y) for piece in move]
                else:
                    return True
            else:
                dest_x, dest_y = destination
                logging.debug("{}: Invalid move from {}, {} to {}, {}".format(
                    datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), x, y, dest_x, dest_y))
                return False
        elif not piece:
            logging.debug("{}: Invalid piece at {}, {}".format(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'),
                                                               x, y))
            return False
        else:
            logging.debug("{}: Invalid player id {} moving piece at {}, {}".format(player_token,
                                                            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'),x, y))
            return False

    def move(self, piece, destination):
        x, y = destination
        self.store_move((piece.x, piece.y), destination)
        self.board.move_piece_on_board(piece, x, y)
        piece.move(destination)

    def record_access(self):
        self.last_accessed = datetime.datetime.now()


class Piece(object):

    def __init__(self, start_x, start_y, piece_id):
        self.type = 'Piece'
        self.x = start_x
        self.y = start_y
        self.moves = [(self.x, self.y), ]
        self.status = 'Alive'
        self.id = piece_id

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.type

    def __bool__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False

    def __getnewargs__(self):
        return self.x, self.y

    def capture(self):
        self.status = 'Captured'

    def move(self, square):
        self.x, self.y = square
        self.moves.append(square)


class Dwarf(Piece):

    def __init__(self, start_x, start_y, piece_id):
        super().__init__(start_x, start_y, piece_id)
        self.type = 'Dwarf'


class Troll(Piece):

    def __init__(self, start_x, start_y, piece_id):
        super().__init__(start_x, start_y, piece_id)
        self.type = 'Troll'


class Player(object):

    def __init__(self, name, player_id, race):
        self.name = name
        self.token = player_id
        if race == 'D':
            self.race = 'Dwarf'
        elif race == 'T':
            self.race = 'Troll'
        else:
            raise ValueError('Race of {} is not valid - choose D (Dwarf) or (Troll)'.format(race))