from copy import deepcopy
from .constants import BLACK, WHITE

import pygame

def minimax(board, depth, alpha, beta, max_player, game):    
    if depth == 0 or board.winner() != None:
        return board.evaluate(), board

    if max_player:
        maxEval = float("-inf")
        best_move = None
        for move in get_all_moves(board, WHITE):
            evaluation = minimax(move, depth-1, alpha, beta, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return maxEval, best_move
    else:
        minEval = float("inf")
        best_move = None
        for move in get_all_moves(board, BLACK):
            evaluation = minimax(move, depth-1, alpha, beta, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return minEval, best_move

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
        temp_board = deepcopy(board)
        temp_piece = temp_board.get_piece(piece.row, piece.col)
        new_board = simulate_piece_move(temp_piece, move, temp_board)
        moves.append(new_board)

    walls = board.black_walls if color == BLACK else board.white_walls
    if walls == 0:
        return moves
    
    valid_walls = board.get_valid_walls()
    for wall in valid_walls:
        temp_board = deepcopy(board)
        new_board = simulate_wall(wall, temp_board, color)
        moves.append(new_board)

    return moves