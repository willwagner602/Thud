__author__ = 'wwagner'

import unittest
import Thud


class BoardTest(unittest.TestCase):

    def setUp(self):
        self.test_board = Thud.Board()

    def test_initial_piece_setup(self):
        # Arrayed identically to board
        dwarf_positions = [(5, 14), (6, 14), (8, 14), (9, 14),
                           (4, 13), (10, 13),
                           (3, 12), (11, 12),
                           (2, 11), (12, 11),
                           (1, 10), (13, 10),
                           (0, 9), (14, 9),
                           (0, 8), (14, 8),
                           (0, 6), (14, 6),
                           (0, 5), (14, 5),
                           (1, 4), (13, 4),
                           (2, 3), (12, 3),
                           (3, 2), (11, 2),
                           (4, 1), (10, 1),
                           (5, 0), (6, 0), (8, 0), (9, 0)
                           ]
        for coordinates in dwarf_positions:
            row = coordinates[0]
            column = coordinates[1]
            self.assertEqual(self.test_board.squares[row][column].name, 'Dwarf')

        # Arrayed identically to board
        troll_positions = [(6, 8), (7, 8), (8, 8),
                           (6, 7), (8, 7),
                           (6, 6), (7, 6), (8, 6)]
        for coordinates in troll_positions:
            row = coordinates[0]
            column = coordinates[1]
            self.assertEqual(self.test_board.squares[row][column].name, 'Troll')

    def test_getitem(self):
        self.assertEqual(self.test_board[7][7], 0)

    def test_setitem(self):
        self.assertEqual(self.test_board[7][7], 0)
        self.test_board[7][7] = 12345
        self.assertEqual(self.test_board[7][7], 12345)


class GameTest(unittest.TestCase):

    def setUp(self):
        self.test_game = Thud.Game()

    def test_validate_clear_path_success(self):
        self.assertTrue(self.test_game.validate_clear_path((1, 5), (1, 10)))

    def test_validate_clear_path_through_piece_failure(self):
        self.assertFalse(self.test_game.validate_clear_path((5, 8), (7, 8)))

    def test_determine_move_or_attack_is_attack(self):
        self.test_game.dwarf_move_or_attack((0, 8), (6, 8))

    def test_determine_move_or_attack_is_friendly(self):
        self.test_game.dwarf_move_or_attack((0, 8), (0, 9))

    def test_dwarf_move_east_success(self):
        pass
        # self.assertTrue(Thud.Board.validate_dwarf_move())

    def test_dwarf_move_west_success(self):
        pass

    def test_dwarf_move_north_success(self):
        pass

    def test_dwarf_move_south_success(self):
        pass

    def test_dwarf_move_failure(self):
        pass

# class PieceTest(unittest.TestCase)
#     def test_move_piece_success(self):
#         self.assertTrue(piece.move('valid space'))
#
#     def test_move_piece_failure(self):
#         self.assertFalse(piece.move('invalid space'))