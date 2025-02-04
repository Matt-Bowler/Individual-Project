import pygame
from .board import Board
from .constants import BLACK, WHITE, YELLOW, SQUARE_SIZE, RED, WALL_THICKNESS
from .wall import Wall

class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        self.selected_piece = None
        self.wall_hovered = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = set()

    def update(self):
        self.board.draw(self.win)
        if self.selected_piece:
            self.draw_valid_moves()
        if self.wall_hovered and self.wall_hovered in self.board.get_valid_walls() and self.player_has_walls():
            self.draw_hovered_wall()
            
        pygame.display.update()

    def reset(self):
        self._init()

    def get_board(self):
        return self.board
    
    def winner(self):
        return self.board.winner()

    def select_square(self, row, col):
        if self.selected_piece:
            result = self._move_piece(row, col)
            if not result:
                self.selected_piece = None
                self.select_square(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected_piece = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        
        return False
    
    def _move_piece(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected_piece and piece == 0 and (row, col) in self.valid_moves:
            self.board.move_piece(self.selected_piece, row, col)
            self.change_turn()
        else:
            return False
        
        return True
    
    def player_has_walls(self):
        if self.turn == BLACK:
            return self.board.black_walls > 0
        else:
            return self.board.white_walls > 0

    def place_wall(self, wall):
        if wall in self.board.get_valid_walls() and self.player_has_walls():
            self.board.place_wall(wall)
            if self.turn == BLACK:
                self.board.black_walls -= 1
            else:
                self.board.white_walls -= 1
            print(f"Wall placed: {str(wall)} {'Black' if self.turn == BLACK else 'White'} has {self.board.black_walls if self.turn == BLACK else self.board.white_walls} walls left")
            self.change_turn()
        else:
            print("Invalid wall placement")
            return False
        
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
        self.board = board
        self.change_turn()
