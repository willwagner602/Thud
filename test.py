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

    def test_get_piece_success(self):
        x = 6
        y = 7
        test_piece = self.test_board[x][y]
        self.assertEqual(self.test_board.get_piece(x, y), test_piece)

    def test_get_piece_failure(self):
        x = 4
        y = 7
        self.assertFalse(self.test_board.get_piece(x, y))

    def test_set_square_success(self):
        self.assertEqual(self.test_board.squares[4][7], '4,7')
        self.test_board.set_square(4, 7, '1,1')
        self.assertEqual(self.test_board.squares[4][7], '1,1')

    def test_move_piece(self):
        start_x = 6
        start_y = 7
        dest_x = 4
        dest_y = 7
        test_piece = self.test_board.squares[start_x][start_y]
        self.test_board.move_piece(test_piece, 4, 7)
        self.assertEqual(self.test_board.squares[dest_x][dest_y], test_piece)
        self.assertEqual(self.test_board.squares[start_x][start_y], (str(start_x) + ',' + str(start_y)))


class GameTest(unittest.TestCase):

    def setUp(self):
        self.test_game = Thud.Game()

    def test_validate_destination_success(self):
        self.assertTrue(self.test_game.validate_destination((6, 4)))
        self.assertTrue(self.test_game.validate_destination((13, 11)))
        self.assertTrue(self.test_game.validate_destination((11, 9)))
        self.assertTrue(self.test_game.validate_destination((4, 2)))

    def test_validate_destination_failure_over_max_x(self):
        self.assertFalse(self.test_game.validate_destination((15, 4)))

    def test_validate_destination_failure_under_min_x(self):
        self.assertFalse(self.test_game.validate_destination((-1, 4)))

    def test_validate_destination_failure_over_max_y(self):
        self.assertFalse(self.test_game.validate_destination((6, 15)))

    def test_validate_destination_failure_under_min_y(self):
        self.assertFalse(self.test_game.validate_destination((6, -1)))

    def test_validate_dwarf_move_success(self):
        test_piece = self.test_game.board.get_piece(6, 0)
        # self.ass

    def test_validate_clear_path_success(self):
        test_piece = self.test_game.board.get_piece(1, 4)
        self.assertTrue(self.test_game.validate_clear_path(test_piece, (1, 9)))

    def test_validate_clear_path_through_piece_failure(self):
        test_piece = self.test_game.board.get_piece(7, 8)
        self.assertFalse(self.test_game.validate_clear_path(test_piece, (9, 8)))

    def test_validate_clear_path_through_multiple_pieces_failure(self):
        test_piece = self.test_game.board.get_piece(12, 3)
        self.assertFalse(self.test_game.validate_clear_path(test_piece, (2, 13)))

    def test_validate_clear_path_to_troll_success(self):
        test_dwarf = self.test_game.board.get_piece(6, 0)
        test_troll = self.test_game.board.get_piece(6, 6)

    def test_validate_dwarf_move_east_success(self):
        test_dwarf = self.test_game.board.get_piece(0, 5)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (13, 5)))

    def test_validate_dwarf_move_west_success(self):
        test_dwarf = self.test_game.board.get_piece(12, 3)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (3, 3)))

    def test_validate_dwarf_move_north_success(self):
        test_dwarf = self.test_game.board.get_piece(10, 13)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (10, 2)))

    def test_validate_dwarf_move_south_success(self):
        test_dwarf = self.test_game.board.get_piece(3, 2)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (3, 11)))

    def test_validate_dwarf_move_northeast_success(self):
        test_dwarf = self.test_game.board.get_piece(2, 11)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (5, 8)))

    def test_validate_dwarf_move_southeast_success(self):
        test_dwarf = self.test_game.board.get_piece(2, 3)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (5, 6)))

    def test_validate_dwarf_move_northwest_success(self):
        test_dwarf = self.test_game.board.get_piece(10, 13)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (6, 9)))

    def test_validate_dwarf_move_southwest_success(self):
        test_dwarf = self.test_game.board.get_piece(12, 3)
        self.assertTrue(self.test_game.validate_dwarf_move(test_dwarf, (9, 6)))

    def test_validate_dwarf_move_non_diagonal_failure(self):
        test_dwarf = self.test_game.board.get_piece(12, 3)
        self.assertFalse(self.test_game.validate_dwarf_move(test_dwarf, (10, 6)))

    def test_validate_dwarf_move_non_horizontal_failure(self):
        test_dwarf = self.test_game.board.get_piece(12, 3)
        self.assertFalse(self.test_game.validate_dwarf_move(test_dwarf, (2, 4)))

    def test_validate_dwarf_move_impassable_failure(self):
        test_dwarf = self.test_game.board.get_piece(14, 5)
        self.assertFalse(self.test_game.validate_dwarf_move(test_dwarf, (14, 3)))

    def test_validate_dwarf_move_creature_failure(self):
        test_dwarf = self.test_game.board.get_piece(12, 3)
        self.assertFalse(self.test_game.validate_dwarf_move(test_dwarf, (5, 10)))

    def test_validate_troll_move_east_success(self):
        test_troll = self.test_game.board[8][6]
        pass

    def test_validate_troll_move_west_success(self):
        test_troll = self.test_game.board[6][8]
        pass

    def test_validate_troll_move_south_success(self):
        test_troll = self.test_game.board[6][8]
        pass

    def test_validate_troll_move_north_success(self):
        test_troll = self.test_game.board[8][6]
        pass

    def test_validate_troll_move_northeast_success(self):
        test_troll = self.test_game.board[8][6]
        pass

    def test_validate_troll_move_southeast_success(self):
        test_troll = self.test_game.board[8][6]
        pass

    def test_validate_troll_move_northwest_success(self):
        test_troll = self.test_game.board[6][8]
        pass

    def test_validate_troll_move_southwest_success(self):
        test_troll = self.test_game.board[6][8]
        pass

    def test_find_adjacent_dwarves_find_three_success(self):
        target_square = (1, 5)
        target_dwarves = [self.test_game.board.get_piece(0, 5), self.test_game.board.get_piece(1, 4),
                          self.test_game.board.get_piece(0, 6)]
        self.assertEqual(self.test_game.find_adjacent_dwarves(target_square), target_dwarves)

    def test_find_adjacent_dwarves_find_two_success(self):
        target_square = (14, 7)
        target_dwarves = [self.test_game.board.get_piece(14, 6), self.test_game.board.get_piece(14, 8)]
        self.assertEqual(self.test_game.find_adjacent_dwarves(target_square), target_dwarves)

    def test_validate_troll_move_or_attack_is_attack(self):
        test_troll = self.test_game.board[6][6]
        # need to manually move troll so that move is valid
        self.test_game.board.move_piece(test_troll, 2, 7)
        target_dwarves = [self.test_game.board.get_piece(0, 5), self.test_game.board.get_piece(1, 4),
                          self.test_game.board.get_piece(0, 6)]
        destination = (1, 5)
        self.assertEqual(self.test_game.validate_troll_move_or_attack(test_troll, destination), target_dwarves)

    def test_validate_troll_move_or_attack_is_move(self):
        test_troll = self.test_game.board.get_piece(6, 6)
        destination = (5, 6)
        self.assertTrue(self.test_game.validate_troll_move_or_attack(test_troll, destination))

    def test_validate_troll_move_or_attack_is_neither(self):
        test_troll = self.test_game.board.get_piece(6, 6)
        destination = (4, 6)
        self.assertFalse(self.test_game.validate_troll_move_or_attack(test_troll, destination))

    def test_validate__move_troll_on_top_of_troll(self):
        self.assertFalse(self.test_game.validate_move((8, 8), (8, 7)))

    def test_validate_throw_success(self):
        test_piece = self.test_game.board.get_piece(6, 6)
        # guard assertion to ensure this really was an empty square before
        self.assertFalse(self.test_game.find_adjacent_dwarves((3, 6)))
        # move a dwarf so that the attack check passes
        target_piece = self.test_game.board.get_piece(0, 6)
        self.assertIsInstance(self.test_game.board.get_piece(0, 6), Thud.Dwarf)
        self.test_game.board.move_piece(target_piece, 2, 6)
        self.assertEqual(self.test_game.validate_throw(test_piece, (3, 6)), self.test_game.board.get_piece(0, 6))

    def test_validate_throw_failure(self):
        test_piece = self.test_game.board.get_piece(6, 6)
        self.assertFalse(self.test_game.validate_throw(test_piece, (3, 6)))

    def test_validate_troll_move_or_attack_failure_through_piece(self):
        test_troll = self.test_game.board.get_piece(8, 7)
        # setup a dwarf to allow a shove
        test_dwarf = self.test_game.board.get_piece(5, 0)
        self.test_game.board.move_piece(test_dwarf, 8, 4)
        self.test_game.board.print_board()
        self.assertEqual(test_dwarf, self.test_game.board.get_piece(8, 4))
        self.assertFalse(self.test_game.validate_troll_move_or_attack(test_troll, (7, 5)))

    def test_validate_troll_move_or_attack_success_move(self):
        test_piece = self.test_game.board.get_piece(6, 6)
        self.assertTrue(self.test_game.validate_troll_move_or_attack(test_piece, (6, 5)))

# class PieceTest(unittest.TestCase)
#     def test_move_piece_success(self):
#         self.assertTrue(piece.move('valid space'))
#
#     def test_move_piece_failure(self):
#         self.assertFalse(piece.move('invalid space'))