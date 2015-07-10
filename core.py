__author__ = 'wwagner'


class Board(object):

    def __init__(self):
        self.name = 'Game Board'
        self.squares = [[[] for x in range(15)] for x in range(15)]

    def determine_move_vector(self, start, end):


    def validate_dwarf_move(self, piece, destination):


    def validate_troll_move(self, piece, destination):

    def validate_move(self, piece, destination):
        if self.confirm_move_on_board(piece, destination):
            if piece.name == 'Dwarf':
                return self.validate_dwarf_move(piece, destination)
            else:
                return self.validate_troll_move(piece, destination)
        else:
            return False


class Piece(object):

    def __init__(self, starting_space):
        self.name = 'Piece'
        self.space = starting_space
        self.moves = [self.starting_space, ]

    def __str__(self):
        return self.name


class Dwarf(Piece):

    def __init__(self, starting_space):
        super().__init__(starting_space)
        self.name = 'Dwarf'


class Troll(Piece):

    def __init__(self, starting_space):
        super().__init__(starting_space)
        self.name = 'Troll'