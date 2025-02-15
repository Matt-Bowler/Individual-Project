import pygame

from quoridor.wall import Wall
from .constants import BAIGE, BROWN, WHITE, BLACK, ROWS, COLS, SQUARE_SIZE, WALL_THICKNESS, GREY
from .piece import Piece
from .pathfinding import path_exists, get_cached_path

class Board:
    def __init__(self):
        self.board = []
        self.horizontal_walls = set()
        self.vertical_walls = set()
        self.valid_walls = set()
        self.black_walls = self.white_walls = 10
        self.create_board()
        self.precompute_valid_walls()
    
    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                self.board[row].append(0)

        self.board[0][COLS // 2] = Piece(0, COLS // 2, BLACK)
        self.board[ROWS - 1][COLS // 2] = Piece(ROWS - 1, COLS // 2, WHITE)

    def precompute_valid_walls(self):
        for row in range(ROWS - 1):
            for col in range(COLS - 1):
                self.valid_walls.add(Wall(row, col, "horizontal"))
        
        for row in range(1, ROWS):
            for col in range(1, COLS):
                self.valid_walls.add(Wall(row, col, "vertical"))
        
    def draw_squares(self, win):
        for row in range(ROWS):
            for col in range(COLS):
                if(row + col) % 2 == 0:
                    pygame.draw.rect(win, BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(win, BAIGE, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_dividers(self, win):
        for row in range(ROWS + 1): 
            pygame.draw.line(win, GREY, (0, row * SQUARE_SIZE), (COLS * SQUARE_SIZE, row * SQUARE_SIZE), WALL_THICKNESS)
        for col in range(COLS + 1):  
            pygame.draw.line(win, GREY, (col * SQUARE_SIZE, 0), (col * SQUARE_SIZE, ROWS * SQUARE_SIZE), WALL_THICKNESS)
    
    def draw_walls(self, win):
        for row, col in self.horizontal_walls:
            start_pos = (col * SQUARE_SIZE + (WALL_THICKNESS // 2) + 1 , (row + 1) * SQUARE_SIZE)
            end_pos = ((col + 2) * SQUARE_SIZE - (WALL_THICKNESS // 2), (row + 1) * SQUARE_SIZE)
            pygame.draw.line(win, BLACK, start_pos, end_pos, WALL_THICKNESS)
        for row, col in self.vertical_walls:
            start_pos = (col * SQUARE_SIZE, (row - 1) * SQUARE_SIZE + (WALL_THICKNESS // 2) + 1)
            end_pos = (col  * SQUARE_SIZE, (row + 1) * SQUARE_SIZE - (WALL_THICKNESS // 2))
            pygame.draw.line(win, BLACK, start_pos, end_pos, WALL_THICKNESS)
        
    def draw(self, win):
        self.draw_squares(win)
        self.draw_dividers(win)
        self.draw_walls(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    piece.draw(win)

    def move_piece(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

    def place_wall(self, wall):
        if wall.orientation == "horizontal":
            self.horizontal_walls.add((wall.row, wall.col))
        else:
            self.vertical_walls.add((wall.row, wall.col))
        
        self.remove_invalid_walls(wall)

    def remove_invalid_walls(self, wall):
        self.valid_walls.remove(wall)

        if wall.orientation == "horizontal":
            self.valid_walls.discard(Wall(wall.row, wall.col + 1, "horizontal"))
            self.valid_walls.discard(Wall(wall.row, wall.col - 1, "horizontal"))
            self.valid_walls.discard(Wall(wall.row + 1, wall.col + 1, "vertical"))
        else:
            self.valid_walls.discard(Wall(wall.row + 1, wall.col, "vertical"))
            self.valid_walls.discard(Wall(wall.row - 1, wall.col, "vertical"))
            self.valid_walls.discard(Wall(wall.row - 1, wall.col - 1, "horizontal"))

    def get_piece(self, row, col):
        return self.board[row][col]
    
    def get_piece_by_color(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    return piece

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
    
    def is_valid_wall(self, wall):
        if wall not in self.valid_walls:
            return False
                
        if wall.orientation == "horizontal":
            self.horizontal_walls.add((wall.row, wall.col))
            if not path_exists(self.board, self.horizontal_walls, self.vertical_walls):
                self.horizontal_walls.remove((wall.row, wall.col))
                return False
            self.horizontal_walls.remove((wall.row, wall.col)) 
        else:  
            self.vertical_walls.add((wall.row, wall.col))
            if not path_exists(self.board, self.horizontal_walls, self.vertical_walls):
                self.vertical_walls.remove((wall.row, wall.col))
                return False
            self.vertical_walls.remove((wall.row, wall.col))
       
        return True
    
    def get_valid_walls(self):
        return self.valid_walls

    def get_valid_moves(self, piece):
        moves = set()
        row = piece.row
        col = piece.col
        
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_row = row + dx
            new_col = col + dy
            
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if not self.is_wall_between(row, col, new_row, new_col):
                    next_piece = self.get_piece(new_row, new_col)
                    
                    # Empty square
                    if next_piece == 0:  
                        moves.add((new_row, new_col))
                    # Square has opponent
                    else:  
                        jump_row = new_row + dx
                        jump_col = new_col + dy
                        
                        # Check if jump is possible
                        if (0 <= jump_row < ROWS and 0 <= jump_col < COLS and
                            not self.is_wall_between(new_row, new_col, jump_row, jump_col) and
                            self.get_piece(jump_row, jump_col) == 0):
                            moves.add((jump_row, jump_col))
                        # Check diagonal moves if jump blocked
                        else:

                            # if jump_row < 0 or jump_row >= ROWS or jump_col < 0 or jump_col >= COLS:
                            #     continue

                            diagonals = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                            for diag_dx, diag_dy in diagonals:
                                diag_row = new_row + diag_dx
                                diag_col = new_col + diag_dy
                                if (0 <= diag_row < ROWS and 0 <= diag_col < COLS and
                                    not self.is_wall_between(new_row, new_col, diag_row, diag_col) and
                                    self.get_piece(diag_row, diag_col) == 0):
                                    moves.add((diag_row, diag_col))
        return moves

    def is_wall_between(self, row1, col1, row2, col2):
        # Move is horizontal
        if row1 == row2:
            # Move is to right
            if col1 < col2:
                return (row2, col2) in self.vertical_walls or (row2 + 1, col2) in self.vertical_walls
            elif col1 > col2:
                return (row1, col1) in self.vertical_walls or (row1 + 1, col1) in self.vertical_walls
        # Move is vertical
        elif col1 == col2:
            # Move is downwards
            if row1 < row2:
                return (row1, col1) in self.horizontal_walls or (row1, col1 - 1) in self.horizontal_walls
            # Move is upwards
            elif row1 > row2:
                return (row2, col2) in self.horizontal_walls or (row2, col2 - 1) in self.horizontal_walls
        return False

    def evaluate(self, color):
        white_piece = self.get_piece_by_color(WHITE)
        black_piece = self.get_piece_by_color(BLACK)
        opponent_piece = white_piece if color == BLACK else black_piece

        white_shortest_path = get_cached_path(self, white_piece, self.horizontal_walls, self.vertical_walls)
        black_shortest_path = get_cached_path(self, black_piece, self.horizontal_walls, self.vertical_walls)
 
        if self.winner() == color:
            return 10000  
        if self.winner() == opponent_piece.color:
            return -10000  

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

        eval_score = (9.35 * path_diff) + (7 * wall_bonus) + (5 * blockade_bonus) + (3 * forward_bonus)

        return eval_score


    def __repr__(self):
            board_str = ""
            for row in self.board:
                for cell in row:
                    if cell == 0:
                        board_str += ". "
                    else:
                        board_str += "B " if cell.color == BLACK else "W "
                board_str += "\n"
            return board_str
    
    

            