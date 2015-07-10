__author__ = 'wwagner'

import unittest
import Thud


class BoardTest(unittest.TestCase):

    def test_populated_board(self):
        test = Thud.Board()
        test.print_board()



# class PieceTest(unittest.TestCase)
#     def test_move_piece_success(self):
#         self.assertTrue(piece.move('valid space'))
#
#     def test_move_piece_failure(self):
#         self.assertFalse(piece.move('invalid space'))