from copy import deepcopy
import numpy as np

from quoridor.board import Board
from .constants import BLACK, WHITE, ROWS, COLS

class Cache:
    def __init__(self):
        self.ZOBRIST_PIECE_TABLE = np.random.randint(0, 2**64, size=(ROWS, COLS, 2), dtype=np.uint64)
        self.ZOBRIST_WALL_TABLE = np.random.randint(0, 2**64, size=(ROWS, COLS, 2), dtype=np.uint64)
        self.ZOBRIST_COLOR_WHITE = np.random.randint(0, 2**64, dtype=np.uint64)
        self.ZOBRIST_COLOR_BLACK = np.random.randint(0, 2**64, dtype=np.uint64)
        self.transposition_table = {} 

    def compute_zobrist_hash(self, board, color):
        zobrist_hash = 0

        # Include the pieces
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.get_piece(row, col)
                if piece:
                    piece_index = 0 if piece.color == WHITE else 1
                    zobrist_hash ^= self.ZOBRIST_PIECE_TABLE[row, col, piece_index]

        # Include the walls
        for wall in board.horizontal_walls:
            row, col = wall
            zobrist_hash ^= self.ZOBRIST_WALL_TABLE[row, col, 0]  # XOR with the horizontal wall hash

        for wall in board.vertical_walls:
            row, col = wall
            zobrist_hash ^= self.ZOBRIST_WALL_TABLE[row, col, 1]  # XOR with the vertical wall hash

        if color == WHITE: 
            zobrist_hash ^= self.ZOBRIST_COLOR_WHITE
        else:
            zobrist_hash ^= self.ZOBRIST_COLOR_BLACK

        return zobrist_hash
    
    def clear(self):
        self.__init__()




class AI:
    def __init__(self):
        self.cache = Cache()

    def negamax(self, board, depth, alpha, beta, color):
        if depth == 0 or board.winner() is not None:
            evaluation = board.evaluate(color)
            return evaluation, board
        
        # Get the current Zobrist hash for the board state
        board_hash = self.cache.compute_zobrist_hash(board, color)
        
        # Check if this board state is in the transposition table
        if board_hash in self.cache.transposition_table:
            cached_value, cached_depth = self.cache.transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_value, board

        best_move = None
        best_value = float("-inf")

        moves = self.get_all_moves(board, color)
        for move in moves:
            evaluation = -self.negamax(move, depth - 1, -beta, -alpha, self.opposite_color(color))[0]
            if evaluation > best_value:
                best_value = evaluation
                best_move = move

            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break

        # Store evaluated position in transposition table
        self.cache.transposition_table[board_hash] = (best_value, depth)
        return best_value, best_move


    def opposite_color(self, color):
        return WHITE if color == BLACK else BLACK

    def simulate_piece_move(self, piece, move, board):
        board.move_piece(piece, move[0], move[1])

        return board


    def simulate_wall(self, wall, board, color):
        board.place_wall(wall)
        if color == BLACK:
            board.black_walls -= 1
        else:
            board.white_walls -= 1

        return board


    def get_all_moves(self, board, color):
        moves = []

        piece = board.get_piece_by_color(color)
        valid_moves = board.get_valid_moves(piece)

        for move in valid_moves:
            temp_board = self.partial_deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = self.simulate_piece_move(temp_piece, move, temp_board)
            moves.append(new_board)

        walls = board.black_walls if color == BLACK else board.white_walls
        if walls == 0:
            return moves

        valid_walls = board.get_valid_walls()
        walls_to_consider = self.filter_walls(board, valid_walls, color)

        for wall in walls_to_consider:
            if not board.is_valid_wall(wall):
                continue

            temp_board = self.partial_deepcopy(board)
            new_board = self.simulate_wall(wall, temp_board, color)
            moves.append(new_board)

        return moves


    def filter_walls(self, board, valid_walls, color):
        opponent_color = BLACK if color == WHITE else WHITE
        player_piece = board.get_piece_by_color(color)
        opponent_piece = board.get_piece_by_color(opponent_color)

        filtered_walls = []

        for wall in valid_walls:
            row, col, orientation = wall.row, wall.col, wall.orientation

            # Heuristic 1: Walls near the opponent’s or player’s pawn (radius 3)
            if abs(row - player_piece.row) + abs(col - player_piece.col) <= 3 or \
            abs(row - opponent_piece.row) + abs(col - opponent_piece.col) <= 3:
                filtered_walls.append(wall)
                continue  # Prioritize walls near pawns

            # Heuristic 2: Walls adjacent to existing walls
            if (row, col - 1, orientation) in board.valid_walls or (row, col + 1, orientation) in board.valid_walls or \
            (row - 1, col, orientation) in board.valid_walls or (row + 1, col, orientation) in board.valid_walls:
                filtered_walls.append(wall)
                continue  # Prioritize walls that extend an existing structure

            # Heuristic 3: Avoid unnecessary edge walls
            if orientation == "horizontal" and (col == 0 or col == COLS - 2):
                continue
            if orientation == "vertical" and (row == 0 or row == ROWS - 2):
                continue

        return filtered_walls


    def partial_deepcopy(self, board):
        new_board = Board()

        new_board.board = [
            [cell if isinstance(cell, int) else deepcopy(cell) for cell in row]
            for row in board.board
        ]
        new_board.horizontal_walls = board.horizontal_walls.copy()
        new_board.vertical_walls = board.vertical_walls.copy()
        new_board.valid_walls = board.valid_walls.copy()
        new_board.white_walls = board.white_walls
        new_board.black_walls = board.black_walls

        return new_board





