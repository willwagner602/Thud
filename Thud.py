__author__ = 'wwagner'

import logging
import datetime
import random
import string

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
            print(row)

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
        logging.debug('Game Manager started at {}.'.format(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
        self.name = 'Game Manager'
        self.active_games = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def start_game(self, player_one, player_two):
        """
        Generates a game token, and individual player tokens for authentication
        """
        game = Game(player_one, player_two)
        game_token = self.generate_game_token(game)
        self.active_games[game_token] = game
        return game_token, game.player_one_token, game.player_two_token

    def generate_game_token(self, game):
        # ToDo: max_game queries the database for the highest game token played by these two players
        max_game = '1'
        return game.player_one + game.player_two + max_game

    def end_game(self, game_token, player_one_token, player_two_token):
        try:
            game = self.active_games[game_token]
            if game.player_one_token == player_one_token and game.player_two_token == player_two_token:
                # todo:
                # push game data to database
                # remove game from the list
                return True
        except KeyError:
            return False

    def execute_move(self, game_token, player_token, start, destination):
        game = self.active_games[game_token]
        return game.execute_move(player_token, start, destination)

    def report_game_state(self, game_id):
        """
        Returns a json representation of the current game state
        """
        board_state = []
        for row in self.active_games[game_id].board:
            row_state = []
            for square in row:
                if isinstance(square, Piece):
                    row_state.append(square.id)
                else:
                    row_state.append(square)
            board_state += row_state
            print(board_state)


class Game(object):
    """
    Contains all the game logic - moving pieces around the board, capturing and removing pieces.
    """

    def __init__(self, player_one, player_two):
        self.name = ''
        self.board = Board()
        # ToDo: Initialize players as a dict holding the player names with their tokens. Use tokens to call names
        # players = {}
        self.player_one = player_one
        self.player_two = player_two
        self.player_one_token = self.generate_player_token()
        self.player_two_token = self.generate_player_token()
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

    def validate_player(self, player_token):
        """
        Used to ensure the correct player is making a move - returns False for players moving out of order
        :param player_token:
        :return bool:
        """
        # Dwarf player starts turn 1, players alternate for rest of game
        player_one_turn = (len(self.move_history) + 1) % 2 > 0
        if player_one_turn and player_token == self.player_one_token:
            logging.debug("{}: Validated Dwarf move.".format(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
            return True
        elif not player_one_turn and player_token == self.player_two_token:
            logging.debug("{}: Validated Troll move.".format(datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')))
            return True
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
            destination_x, destination_y = destination
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
        logging.debug('Checking squares {}'.format(', '.join(map(str, travel_squares))))
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
            x, y = target
            return [self.board.get_piece(x, y), ]
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
        inverse_x = piece.x - x
        inverse_y = piece.y - y

        logging.debug("{}: Checking valid attack at {},{}.".format(
            datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S'), x, y))

        if piece.x - inverse_x > 0:
            x_check = list(range(piece.x - 1, inverse_x, -1))
        else:
            x_check = list(range(piece.x + 1, inverse_x))
        if piece.y - inverse_y > 0:
            y_check = list(range(piece.y - 1, inverse_y, -1))
        else:
            y_check = list(range(piece.y + 1, inverse_y))

        if not x_check:
            x_check = [piece.x for x in range(0, len(x_check))]
        if not y_check:
            y_check = [piece.y for x in range(0, len(y_check))]

        check_squares = list(zip(x_check, y_check))
        logging.debug('Checking squares {} for toss.'.format(', '.join(map(str, check_squares))))
        for x, y in check_squares:
            if not isinstance(self.board.get_piece(x, y), Piece):
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
        logging.debug("{}: Validating troll move or attack at {},{} Single Space Move: {}".format(
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

            # is a dwarf attack or invalid, because only dwarves can move on top of another piece
            if isinstance(target, Piece):
                if isinstance(piece, Dwarf) and isinstance(target, Troll):
                    dwarf_attack = self.validate_dwarf_attack(piece, target)
                    return dwarf_attack
                # trolls cannot move on top of another piece
                else:
                    return False

            # is a move - see the dwarf and troll move rules
            else:
                target = destination
                if isinstance(piece, Dwarf):
                    return self.validate_dwarf_move(piece, target)
                else:
                    return self.validate_troll_move_or_attack(piece, target)
        else:
            return False

    def remove_captured_piece(self, target):
        x, y = target.x, target.y
        target.capture()
        self.board[x][y] = (x, y)
        return True

    def execute_move(self, player_token, start, destination):
        x, y = start
        piece = self.board.get_piece(x, y)
        if piece and self.validate_player(player_token):
            move = self.validate_move(start, destination)
            if type(move) == 'list':
                for target in move:
                    self.board.capture_piece(target)
                self.move(piece, destination)
                return move
            elif move:
                self.move(piece, destination)
                return True
            else:
                return False
        return False

    def move(self, piece, destination):
        x, y = destination
        self.store_move((piece.x, piece.y), destination)
        self.board.move_piece_on_board(piece, x, y)
        piece.move(destination)


class Piece(object):

    def __init__(self, start_x, start_y, piece_id):
        self.name = 'Piece'
        self.x = start_x
        self.y = start_y
        self.moves = [(self.x, self.y), ]
        self.status = 'Alive'
        self.id = piece_id

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

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
        self.name = 'Dwarf'


class Troll(Piece):

    def __init__(self, start_x, start_y, piece_id):
        super().__init__(start_x, start_y, piece_id)
        self.name = 'Troll'


class Player(object):

    def __init__(self, name, race):
        self.name = name
        if race == 'D':
            self.race = 'Dwarf'
        elif race == 'T':
            self.race = 'Troll'
        else:
            raise ValueError('Race of {} is not valid - choose D (Dwarf) or (Troll)'.format(race))