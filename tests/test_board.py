import pytest
from quoridor.board import Board
from quoridor.wall import Wall
from quoridor.constants import BLACK, WHITE, ROWS, COLS

white_start_row = ROWS - 1
start_col = COLS // 2

@pytest.fixture
def board():
    return Board()

def test_initial_board_setup(board):
    assert board.black_walls == 10
    assert board.white_walls == 10
    assert board.get_piece(0, start_col).color == BLACK
    assert board.get_piece(white_start_row, start_col).color == WHITE
    assert len(board.valid_walls) == ((ROWS - 1)**2) + ((COLS - 1)**2)

@pytest.mark.parametrize("row,col,color", [
    (0, start_col, BLACK),  
    (white_start_row, start_col, WHITE),  
])
def test_get_piece_by_color(board, row, col, color):
    piece = board.get_piece_by_color(color)
    assert piece.row == row
    assert piece.col == col
    assert piece.color == color

def test_move_piece(board):
    piece = board.get_piece(0, start_col)
    board.move_piece(piece, 1, start_col)
    
    assert board.get_piece(1, start_col) == piece
    assert board.get_piece(0, start_col) == 0

def test_wall_placement(board):
    wall = Wall(0, start_col, "horizontal")
    
    assert board.is_valid_wall(wall)
    board.place_wall(wall)
    
    assert (0, start_col) in board.horizontal_walls  
    assert wall not in board.valid_walls

@pytest.mark.parametrize("color", [
    (BLACK),  
    (WHITE),  
])
def test_winner_detection(board, color):
    if color == BLACK:
        black_piece = board.get_piece(0, start_col)
        board.board[white_start_row][(start_col) + 1] = black_piece
    if color == WHITE:
        white_piece = board.get_piece(white_start_row, start_col)
        board.board[0][(start_col) + 1] = white_piece
    board.board[0][start_col] = 0
    board.board[white_start_row][start_col] = 0 

    assert board.winner() == color

@pytest.mark.parametrize("row,col,expected_moves", [
    (0, start_col, {(1, start_col), (0, start_col - 1), (0, start_col + 1)}),  
    (white_start_row, start_col, {(white_start_row - 1, start_col), (white_start_row, start_col - 1), (white_start_row, start_col + 1)}),  
])
def test_get_valid_moves(board, row, col, expected_moves):
    piece = board.get_piece(row, col)
    moves = board.get_valid_moves(piece)
    assert moves == expected_moves

@pytest.mark.parametrize("row,col,orientation", [
    (0, start_col, "horizontal"),
    (1, start_col, "vertical"),
])
def test_is_wall_between(board, row , col, orientation):
    wall = Wall(row, col, orientation)
    board.place_wall(wall)
    
    if orientation == "horizontal":
        assert board.is_wall_between(row, col, row + 1, col)
        assert board.is_wall_between(row + 1, col, row, col)
        assert board.is_wall_between(row, col + 1, row + 1, col + 1)
        assert board.is_wall_between(row + 1, col + 1, row, col + 1)

    if orientation == "vertical":
        assert board.is_wall_between(row, col, row, col - 1)
        assert board.is_wall_between(row, col - 1, row, col)
        assert board.is_wall_between(row - 1, col - 1, row - 1, col)
        assert board.is_wall_between(row - 1, col, row - 1, col - 1)

def test_evaluation_function(board):    
    assert isinstance(board.evaluate(WHITE), float)
    assert isinstance(board.evaluate(BLACK), float)
