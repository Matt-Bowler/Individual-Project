import pygame

from quoridor.wall import Wall
from .board import Board
from .constants import *

class Game:
    # Game can be initalised with None to run without a window
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        # Player selected piece
        self.selected_piece = None
        # Divider that player is hovering over
        self.wall_hovered = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = set()

    # Used to update the window rendering
    def update(self):
        self.board.draw(self.win)
        # Draws the valid moves for the selected piece
        if self.selected_piece:
            self.draw_valid_moves()
        # Draws if a wall can be placed in the divider hovered over by the player
        if self.wall_hovered and self.board.is_valid_wall(self.wall_hovered) and self.player_has_walls():
            self.draw_hovered_wall()
            
        pygame.display.update()
    
    def reset(self):
        self._init()

    def get_board(self):
        return self.board
    
    def winner(self):
        return self.board.winner()

    # Used for handling square selection by player on the board
    def select_square(self, row, col):
        # If player has already selected a piece, try to move it to new selected square
        if self.selected_piece:
            result = self._move_piece(row, col)
            # If move was invalid
            if not result:
                self.selected_piece = None
                self.select_square(row, col)
                return False
            else:
                return True
            
        # If player has not selected a piece, try to select a new piece
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected_piece = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        
        return False
    
    def _move_piece(self, row, col):
        piece = self.board.get_piece(row, col)
        # If player has selected a piece and is trying to do a valid move
        if self.selected_piece and piece == 0 and (row, col) in self.valid_moves:
            self.board.move_piece(self.selected_piece, row, col)
            self.change_turn()
        else:
            return False
        
        self.print_move((row, col))
        return True
    
    def player_has_walls(self):
        if self.turn == BLACK:
            return self.board.black_walls > 0
        else:
            return self.board.white_walls > 0

    def place_wall(self, wall):
        # If wall placement is valid and player has walls leftS
        if self.board.is_valid_wall(wall) and self.player_has_walls():
            self.board.place_wall(wall)
            if self.turn == BLACK:
                self.board.black_walls -= 1
            else:
                self.board.white_walls -= 1
            self.change_turn()
        else:
            return False
        
        self.print_move(wall)
        return True
    
    def change_turn(self):
        self.valid_moves = {}
        if self.turn == BLACK:
            self.turn = WHITE
        else:
            self.turn = BLACK

    def draw_valid_moves(self):
        for move in self.valid_moves:
            row, col = move
            pygame.draw.circle(self.win, YELLOW, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def draw_hovered_wall(self):
        wall = self.wall_hovered

        if wall.orientation == "horizontal":
            start_pos = (wall.col * SQUARE_SIZE + (WALL_THICKNESS // 2) + 1 , (wall.row + 1) * SQUARE_SIZE)
            end_pos = ((wall.col + 2) * SQUARE_SIZE - (WALL_THICKNESS // 2), (wall.row + 1) * SQUARE_SIZE)
        else:
            start_pos = (wall.col * SQUARE_SIZE, (wall.row - 1) * SQUARE_SIZE + (WALL_THICKNESS // 2) + 1)
            end_pos = (wall.col * SQUARE_SIZE, (wall.row + 1) * SQUARE_SIZE - (WALL_THICKNESS // 2))
        
        pygame.draw.line(self.win, RED, start_pos, end_pos, WALL_THICKNESS)
    
    def ai_move(self, board):
        # Update board state to one evaluated best by AI
        self.board = board
        self.change_turn()

    def print_move(self, move):
        # Since is called after a move is made, the turn has already changed
        # So we need to get the player who just made the move
        player = "White" if self.turn == BLACK else "Black"

        if isinstance(move, Wall):
            row_coord = self.translate_row_coord(move.col + 1)
            orientation = "h" if move.orientation == "horizontal" else "v"
            print(f"{player}: {row_coord}{9 - move.row}{orientation}")
        else:
            row_coord = self.translate_row_coord(move[1] + 1)
            print(f"{player}: {row_coord}{9 - move[0]}")

    def translate_row_coord(self, row):
        return chr(row + 96)

