from copy import deepcopy
from quoridor.board import Board
from quoridor.game import Game
from quoridor.pathfinding import get_cached_path
from quoridor.ai import AI
from quoridor.constants import BLACK, WHITE, ROWS

class TrainingBoard(Board):
    def __init__(self, weights):
        super().__init__()
        self.weights = weights

    def evaluate(self, color):
        if color == WHITE:
            path_weight_total, wall_weight, blockade_weight, forward_weight = self.weights[0]
        else:
            path_weight_total, wall_weight, blockade_weight, forward_weight = self.weights[1]

        white_piece = self.get_piece_by_color(WHITE)
        black_piece = self.get_piece_by_color(BLACK)
        opponent_piece = white_piece if color == BLACK else black_piece

        white_shortest_path = get_cached_path(self, white_piece, self.horizontal_walls, self.vertical_walls)
        black_shortest_path = get_cached_path(self, black_piece, self.horizontal_walls, self.vertical_walls)
 
        if self.winner() == color:
            return float('inf')  
        if self.winner() == opponent_piece.color:
            return float('-inf')  

        if color == BLACK:
            path_diff = (1.2 * len(white_shortest_path)) - (1.8 * len(black_shortest_path))
        else:
            path_diff = (1.2 * len(black_shortest_path)) - (1.8 * len(white_shortest_path))

        wall_bonus = (self.white_walls - self.black_walls) if color == WHITE else (self.black_walls - self.white_walls)

        blockade_bonus = 0
        for wall in self.horizontal_walls | self.vertical_walls:
            if abs(wall[0] - opponent_piece.row) <= 1 and abs(wall[1] - opponent_piece.col) <= 1:
                blockade_bonus += 2.5

        black_progress = black_piece.row  
        white_progress = ROWS - white_piece.row  

        if color == WHITE:
            forward_bonus = white_progress - black_progress  
        else:
            forward_bonus = black_progress - white_progress  

        eval_score = (path_weight_total * path_diff) + (wall_weight * wall_bonus) + (blockade_weight * blockade_bonus) + (forward_weight * forward_bonus)

        return eval_score
    

class TrainingGame(Game):
    def __init__(self, win, weights):
        self.weights = weights
        super().__init__(win)

    def _init(self):
        super()._init()
        self.board = TrainingBoard(self.weights)


class TrainingAI(AI):
    def partial_deepcopy(self, board):
        new_board = TrainingBoard(board.weights)

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



