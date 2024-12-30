import pygame
from .constants import BAIGE, BROWN, WHITE, BLACK, ROWS, COLS, SQUARE_SIZE
from .piece import Piece

class Board:
    def __init__(self):
        self.board = [[]]
        self.create_board()

    def draw_squares(self, win):
        win.fill(BROWN)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, BAIGE, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                self.board[row].append(0)

        self.board[0][COLS // 2] = Piece(0, COLS // 2, BLACK)
        self.board[ROWS - 1][COLS // 2] = Piece(ROWS - 1, COLS // 2, WHITE)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    piece.draw(win)

    def winner(self):
        for col in range(COLS):
            piece = self.board[0][col]
            if piece != 0 and piece.color == WHITE:
                return WHITE
                
        for col in range(COLS):
            piece = self.board[ROWS-1][col]
            if piece != 0 and piece.color == BLACK:
                return BLACK
        
        return None

    def get_valid_moves(self, piece):
        moves = {}
        row = piece.row
        col = piece.col
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_row = row + dx
            new_col = col + dy
            
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if not self.is_wall_between(row, col, new_row, new_col):
                    next_piece = self.get_piece(new_row, new_col)
                    
                    if next_piece == 0:  # Empty square
                        moves[(new_row, new_col)] = []
                    else:  # Square has opponent
                        jump_row = new_row + dx
                        jump_col = new_col + dy
                        
                        # Check if jump is possible
                        if (0 <= jump_row < ROWS and 0 <= jump_col < COLS and
                            not self.is_wall_between(new_row, new_col, jump_row, jump_col) and
                            self.get_piece(jump_row, jump_col) == 0):
                            moves[(jump_row, jump_col)] = []
                        else:
                            # Check diagonal moves if jump blocked
                            diagonals = [(dx+1, dy), (dx-1, dy), (dx, dy+1), (dx, dy-1)]
                            for diag_dx, diag_dy in diagonals:
                                diag_row = new_row + diag_dx
                                diag_col = new_col + diag_dy
                                if (0 <= diag_row < ROWS and 0 <= diag_col < COLS and
                                    not self.is_wall_between(new_row, new_col, diag_row, diag_col) and
                                    self.get_piece(diag_row, diag_col) == 0):
                                    moves[(diag_row, diag_col)] = []
        
        return moves

    def is_wall_between(self, row1, col1, row2, col2):
        return False
