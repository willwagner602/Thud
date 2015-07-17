__author__ = 'wwagner'

import logging
import datetime
import random

logging.basicConfig(filename='ThudLog.log', level=logging.DEBUG)


class Board(object):

    def __init__(self):
        self.name = 'Gameboard'
        self.squares = [[str(x) + ',' + str(y) for y in range(15)] for x in range(15)]
        self.populate_invalid_moves()
        self.units = self.populate_units()
        self.moves = []

    def __getitem__(self, key):
        return self.squares[key]

    def __setitem__(self, key, value):
        self.squares[key] = value

    def print_board(self):
        for row in zip(*self.squares[::1]):
            print(row)

    def populate_invalid_moves(self):
        invalid_flag = 0
        # fill triangles at 4 corners of board
        for x in range(15):
            if x < 5:
                row_squares = range(5-x, 10+x)
                for y in range(15):
                    if y not in row_squares:
                        self.squares[x][y] = invalid_flag
            elif x > 9:
                row_squares = range((1+x-10), 24-x)
                for y in range(15):
                    if y not in row_squares:
                        self.squares[x][y] = invalid_flag
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
                    self.squares[row][column] = Dwarf(row, column)
                    units.append(self.squares[row][column])
                # if it's the first or last square in a row with blocked squares, add a dwarf
                elif self.squares[row][column-1] == 0 or self.squares[row][column+1] == 0:
                    self.squares[row][column] = Dwarf(row, column)
                    units.append(self.squares[row][column])
                # the final dwarves fill out the top and bottom rows except for the center space
                elif row in (0, 14) and column in (6, 8):
                    self.squares[row][column] = Dwarf(row, column)
                    units.append(self.squares[row][column])

        # add trolls to center rows and columns around the center stone
        for row in range(6, 9):
            for column in range(6, 9):
                if self.squares[row][column]:
                    self.squares[row][column] = Troll(row, column)
                    units.append(self.squares[row][column])
        return units

    def move_piece(self, piece, x, y):
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


class GameManager(object):
    """
    Manages the interaction of players with the game and database
    Takes data in the format (gametoken, playertoken, start, destination)
    """

    def __init__(self, player_one, player_two):
        self.game = Game()
        self.name = ''
        self.turn = 1
        self.player_one = player_one
        self.player_two = player_two
        self.game_token = self.generate_game_token()
        self.player_one_token = self.generate_player_token()
        self.player_two_token = self.generate_player_token()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def process_move(self, token):
        # troll turn
        if self.turn % 2 > 0 and token == self.player_two_token:
            # process troll move
            pass
        # dwarf turn
        elif token == self.player_one_token:
            # process dwarf move
            pass

    def generate_game_token(self):
        # ToDo: max_game queries the database for the highest game token played by these two players
        max_game = 1
        return self.player_one + self.player_two + max_game

    def generate_player_token(self):
        """
        Used by process move to validate that the correct player is sending the move request
        """
        token = ''
        for x in range(20):
            token += random.choice("""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(){};':<>?/.,""")
        return token




class Game(object):
    """
    Contains all the game logic - moving pieces around the board, capturing and removing pieces.
    """

    def __init__(self):
        self.name = ''
        self.board = Board()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def validate_clear_path(self, piece, destination):
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
        if self.validate_throw(piece, target) and self.validate_clear_path(piece, target):
            x, y = target
            return [self.board.get_piece(x, y),]

    def validate_dwarf_move(self, piece, destination):
        x, y = destination
        if abs(piece.x - x) == abs(piece.y - y) or piece.x == x or piece.y == y:
            return self.validate_clear_path(piece, destination)
        else:
            return False

    def validate_throw(self, piece, target):
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
        x, y = destination
        if x < 0 or y < 0:
            return False
        try:
            destination = self.board[x][y]
            return True
        except IndexError:
            return False

    def validate_move(self, start, destination):
        piece = self.board.get_piece(start[0], start[1])
        # you can't move an empty square.
        if not piece:
            return False
        dest_x, dest_y = destination
        if self.validate_destination(destination):
            target = self.board.get_piece(dest_x, dest_y)
            # is a dwarf attack or invalid, because only dwarves can move on top of another piece
            if isinstance(target, Piece):
                if isinstance(piece, Dwarf) and isinstance(target, Troll):
                    return self.validate_dwarf_attack(piece, target)
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
        x, y = target
        piece = self.board.get_piece(x, y)
        piece.capture()
        self.board[x][y] = (x, y)
        return True


class Piece(object):

    def __init__(self, start_x, start_y):
        self.name = 'Piece'
        self.x = start_x
        self.y = start_y
        self.moves = [[self.x, self.y], ]
        self.status = 'Alive'

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

    def move(self, x, y):
        self.x = x
        self.y = y
        self.moves.append([x, y])


class Dwarf(Piece):

    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y)
        self.name = 'Dwarf'


class Troll(Piece):

    def __init__(self, start_x, start_y):
        super().__init__(start_x, start_y)
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