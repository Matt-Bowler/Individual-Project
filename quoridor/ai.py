from copy import deepcopy

from quoridor.board import Board
from quoridor.pathfinding import get_cached_path
from quoridor.wall import Wall
from .constants import BLACK, WHITE, ROWS, COLS

evaluated_boards = {}

def minimax(board, depth, alpha, beta, max_player, game):    
    if depth == 0 or board.winner() is not None:
        player_color = WHITE if max_player else BLACK
        return board.evaluate(player_color), board

    board_hash = hash(board) 
    if board_hash in evaluated_boards and depth in evaluated_boards[board_hash]:
        return evaluated_boards[board_hash][depth], board

    best_move = None

    if max_player:
        maxEval = float("-inf")
        moves = get_all_moves(board, WHITE)
        moves.sort(key=lambda x: move_ordering_heuristic(board, x[1], WHITE), reverse=True)

        for move, _ in moves:
            evaluation = minimax(move, depth-1, alpha, beta, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta pruning
        evaluated_boards.setdefault(board_hash, {})[depth] = maxEval  # Store evaluation for this depth

        return maxEval, best_move

    else:
        minEval = float("inf")
        moves = get_all_moves(board, BLACK)
        moves.sort(key=lambda x: move_ordering_heuristic(board, x[1], BLACK), reverse=False)

        for move, _ in moves:
            evaluation = minimax(move, depth-1, alpha, beta, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alpha pruning
        evaluated_boards.setdefault(board_hash, {})[depth] = minEval  # Store evaluation for this depth
        return minEval, best_move

def negamax(board, depth, alpha, beta, color, game):
    if depth == 0 or board.winner() is not None:
        return board.evaluate(color), board
    
    board_hash = hash(board)
    if board_hash in evaluated_boards and depth in evaluated_boards[board_hash]:
        return evaluated_boards[board_hash][depth], board
    
    best_move = None
    best_value = float("-inf")

    moves = get_all_moves(board, color)
    moves.sort(key=lambda x: move_ordering_heuristic(board, x[1], color), reverse=True)

    for move, _ in moves:
        evaluation = -negamax(move, depth-1, -beta, -alpha, opposite_color(color), game)[0]
        if evaluation > best_value:
            best_value = evaluation
            best_move = move

        alpha = max(alpha, evaluation)
        if beta <= alpha:
            break 
    
    evaluated_boards.setdefault(board_hash, {})[depth] = best_value
    return best_value, best_move

def opposite_color(color):
    return WHITE if color == BLACK else BLACK

def simulate_piece_move(piece, move, board):
    board.move_piece(piece, move[0], move[1])
    return board

def simulate_wall(wall, board, color):
    board.place_wall(wall)
    if color == BLACK:
        board.black_walls -= 1
    else:
        board.white_walls -= 1
    return board

def get_all_moves(board, color):
    moves = []

    piece = board.get_piece_by_color(color)
    valid_moves = board.get_valid_moves(piece)

    for move in valid_moves:
        temp_board = partial_deepcopy(board)
        temp_piece = temp_board.get_piece(piece.row, piece.col)
        new_board = simulate_piece_move(temp_piece, move, temp_board)

        moves.append((new_board, move))

    walls = board.black_walls if color == BLACK else board.white_walls
    if walls == 0:
        return moves
    
    valid_walls = board.get_valid_walls()
    walls_to_consider = filter_walls(board, valid_walls, color)

    for wall in walls_to_consider:
        if not board.is_valid_wall(wall):
            continue

        temp_board = partial_deepcopy(board)
        new_board = simulate_wall(wall, temp_board, color)
        moves.append((new_board, wall))

    return moves

def move_ordering_heuristic(board, move, color):

    if isinstance(move, tuple):  # Piece move
        row, col = move
        return -row if color == BLACK else row  # Moves forward


    return 0  # Default


def filter_walls(board, valid_walls, color):
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
            continue  # Skip leftmost and rightmost horizontal walls
        if orientation == "vertical" and (row == 0 or row == ROWS - 2):
            continue  # Skip topmost and bottommost vertical walls

    return filtered_walls


def partial_deepcopy(board):
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