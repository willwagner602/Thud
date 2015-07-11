__author__ = 'wwagner'

import logging
import datetime

logging.basicConfig(filename='ThudLog.log', level=logging.DEBUG)


class Board(object):

    def __init__(self):
        self.name = 'Game Board'
        self.squares = [[str(x) + ',' + str(y) for x in range(15)] for y in range(15)]
        self.populate_invalid_moves()
        self.populate_starting_units()

    def print_board(self):
        for row in self.squares:
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

    def populate_starting_units(self):
        # add dwarves to edges
        for row in range(len(self.squares)):
            for column in range(len(self.squares[row])):
                # don't add any dwarves to the center row
                if not self.squares[row][column] or row == 7:
                    pass
                # if it's the first or last square in a complete row, add a dwarf
                elif column in (0, 14):
                    self.squares[row][column] = Dwarf(row, column)
                # if it's the first or last square in a row with blocked squares, add a dwarf
                elif self.squares[row][column-1] == 0 or self.squares[row][column+1] == 0:
                    self.squares[row][column] = Dwarf(row, column)
                # the final dwarves fill out the top and bottom rows except for the center space
                elif row in (0, 14) and column in (6, 8):
                    self.squares[row][column] = Dwarf(row, column)

        # add trolls to center rows and columns around the center stone
        for row in range(6, 9):
            for column in range(6, 9):
                if self.squares[row][column]:
                    self.squares[row][column] = Troll(row, column)

    def validate_clear_path(self, start, destination):
        x_travel = list(range(start[0], destination[0]))
        y_travel = list(range(start[1], destination[1]))
        # rig up dummy list for horizontal or vertical moves
        if not x_travel:
            x_travel = [start[0] for x in range(0, len(y_travel))]
        if not y_travel:
            y_travel = [start[1] for x in range(0, len(x_travel))]
        for x, y in list(zip(x_travel, y_travel)):
            if isinstance(self.squares[x][y], Piece) or not self.squares[x][y]:
                return False
        return True


    def validate_dwarf_move(self, start, destination):
        # is a valid diagonal move
        if abs(start[0] - destination[0]) == abs(start[1] - destination[1]):
            return validate_clear_path(start, destination)
        # or is a throw
        pass

    def validate_troll_move(self, start, destination):
        # is a straight move 1 square in any direction

        # or is a throw
        pass

    def validate_throw(self, piece, destination):
        # throw less than or equal to number of allies in line opposite direction of travel
        pass

    def validate_move(self, start, destination):
        if self.confirm_move_on_board(start, destination):
            if start.name == 'Dwarf':
                return self.validate_dwarf_move(start, destination)
            else:
                return self.validate_troll_move(start, destination)
        else:
            return False

    def remove_captured_piece(self, piece):
        self.board[piece.x][piece.y] = 1
        piece.capture()


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

    # returns false so that moves can be evaluated against this object
    def __bool__(self):
        return True

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