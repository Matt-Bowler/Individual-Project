from copy import deepcopy
from .constants import BLACK, WHITE, ROWS, COLS

import pygame

def minimax(board, depth, max_player, game):
    if depth == 0 or board.winner() != None:
        return board.evaluate(), board

    if max_player:
        maxEval = float("-inf")
        best_move = None
        for move in get_all_moves(board, WHITE, game):
            evaluation = minimax(move, depth-1, False, game)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_move = move
        return maxEval, best_move
    else:
        minEval = float("inf")
        best_move = None
        for move in get_all_moves(board, BLACK, game):
            evaluation = minimax(move, depth-1, True, game)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_move = move
        return minEval, best_move

def simulate_move(piece, move, board):
    board.move_piece(piece, move[0], move[1])
    return board

def get_all_moves(board, color, game):
    moves = []

    for row in range(ROWS):
        for col in range(COLS):
            piece = board.get_piece(row, col)
            if piece != 0 and piece.color == color:
                valid_moves = game.valid_moves
                for move in valid_moves:
                    temp_board = deepcopy(board)
                    new_board = simulate_move(piece, move, temp_board)
                    moves.append(new_board)
    return moves