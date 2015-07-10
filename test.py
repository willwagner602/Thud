__author__ = 'wwagner'

import unittest

class BoardTest(unittest.TestCase):

    def test_move_piece_success(self):
        self.assertTrue(piece.move('valid space'))

    def test_move_piece_failure(self):
        self.assertFalse(piece.move('invalid space'))