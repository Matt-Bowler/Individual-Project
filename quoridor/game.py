import pygame
from .board import Board
from .constants import BLACK, WHITE, YELLOW, SQUARE_SIZE, RED, WALL_THICKNESS

class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        self.selected = None
        self.wall_hovered = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = {}

    def update(self):
        self.board.draw(self.win)
        if self.selected:
            self.draw_valid_moves(self.valid_moves)
        if self.wall_hovered and self.wall_hovered in self.board.get_valid_walls():
            self.draw_hovered_wall(self.wall_hovered)
            
        pygame.display.update()

    def reset(self):
        self._init()
    
    def winner(self):
        return self.board.winner()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            self.change_turn()
        else:
            return False
        
        return True
    
    def change_turn(self):
        self.valid_moves = {}
        if self.turn == BLACK:
            self.turn = WHITE
        else:
            self.turn = BLACK

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, YELLOW, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def draw_hovered_wall(self, wall):
        row, col, wall_type = wall
 
        if wall_type == "horizontal":
            start_pos = (col * SQUARE_SIZE + (WALL_THICKNESS // 2) + 1 , row * SQUARE_SIZE)
            end_pos = ((col + 2) * SQUARE_SIZE - (WALL_THICKNESS // 2), row * SQUARE_SIZE)
        else:
            start_pos = (col * SQUARE_SIZE, (row - 1) * SQUARE_SIZE + (WALL_THICKNESS // 2) + 1)
            end_pos = (col * SQUARE_SIZE, (row + 1) * SQUARE_SIZE - (WALL_THICKNESS // 2))
        
        pygame.draw.line(self.win, RED, start_pos, end_pos, WALL_THICKNESS)