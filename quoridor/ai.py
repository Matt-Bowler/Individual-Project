from copy import deepcopy

from quoridor.board import Board
from .constants import BLACK, WHITE, ROWS, COLS

class AI:
    def __init__(self, depth=2):
        self.depth = depth
    
    # Recursive minimax function optimised for two players
    def negamax(self, board, depth, alpha, beta, color, progress_callback=None):
        if depth == 0 or board.winner() is not None:
            evaluation = board.evaluate(color)
            return evaluation, board, None

        # Best move is the board state returned after the move
        # Best action is the action (piece move or wall placement) taken to get to that board state
        best_move = None
        best_action = None
        best_value = float("-inf")

        moves = self.get_all_moves(board, color)
        num_moves = len(moves)
                
        for i, (move, action) in enumerate(moves):
            evaluation = -self.negamax(move, depth - 1, -beta, -alpha, self.opposite_color(color))[0]
            if evaluation > best_value:
                best_value = evaluation
                best_move = move
                best_action = action

            # Alpha-beta pruning
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
            
            # Used to update the progress bar if callback function is passed in
            if progress_callback:
                progress = ((i + 1) / num_moves) * 100
                progress_callback(progress)

        return best_value, best_move, best_action

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
            moves.append((new_board, move))

        # Dont consider wall placement if no walls left
        walls = board.black_walls if color == BLACK else board.white_walls
        if walls == 0:
            return moves

        valid_walls = board.get_valid_walls()
        # Only consider subset of walls based on heuristics
        walls_to_consider = self.filter_walls(board, valid_walls, color)

        for wall in walls_to_consider:
            if not board.is_valid_wall(wall):
                continue

            temp_board = self.partial_deepcopy(board)
            new_board = self.simulate_wall(wall, temp_board, color)
            moves.append((new_board, wall))

        return moves


    def filter_walls(self, board, valid_walls, color):
        opponent_color = BLACK if color == WHITE else WHITE
        player_piece = board.get_piece_by_color(color)
        opponent_piece = board.get_piece_by_color(opponent_color)

        filtered_walls = []

        for wall in valid_walls:
            row, col, orientation = wall.row, wall.col, wall.orientation

            # Heuristic 1: Walls near the opponent or player (radius 3)
            if abs(row - player_piece.row) + abs(col - player_piece.col) <= 3 or \
            abs(row - opponent_piece.row) + abs(col - opponent_piece.col) <= 3:
                filtered_walls.append(wall)
                continue  # Prioritize walls near pawns

            # Heuristic 2: Walls adjacent to existing walls
            if (row, col - 1, orientation) in board.valid_walls or (row, col + 1, orientation) in board.valid_walls or \
            (row - 1, col, orientation) in board.valid_walls or (row + 1, col, orientation) in board.valid_walls:
                filtered_walls.append(wall)
                continue  # Prioritize walls that extend an existing structure
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

    