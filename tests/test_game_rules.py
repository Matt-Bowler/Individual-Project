import pytest
from quoridor.game import Game
from quoridor.wall import Wall
from quoridor.constants import BLACK, WHITE, ROWS, COLS

@pytest.fixture
def game():
    return Game(None)

@pytest.fixture
def board(game):
    return game.get_board()

def test_white_is_first(game):
    assert game.turn == WHITE

def test_invalid_selection(game, board):
    piece = board.get_piece_by_color(WHITE)
    row, col = piece.row, piece.col
    result = game.select_square(row, col + 1)
    assert result is False


def test_valid_move(game, board):
    piece = board.get_piece_by_color(WHITE)
    row, col = piece.row, piece.col
    
    # Select the white piece
    result = game.select_square(row, col)
    assert result is True
    # Move the piece to col + 1 (valid move in beginning)
    result = game.select_square(row, col + 1)
    assert result is True

    assert board.get_piece(row, col + 1) == piece
    assert board.get_piece(row, col) == 0
    assert game.turn == BLACK


def test_invalid_move_distance(game, board):
    piece = board.get_piece_by_color(WHITE)
    row, col = piece.row, piece.col

    result = game.select_square(row, col)
    assert result is True

    # Attempt to move the piece to col + 2 (not valid unless adjacent to opponent)
    result = game.select_square(row, col + 2)
    assert result is False
    
    assert board.get_piece(row, col + 2) == 0
    assert board.get_piece(row, col) == piece
    assert game.turn == WHITE  # Turn should not change

def test_invalid_move_occupied(game, board):
    white_piece = board.get_piece_by_color(WHITE)
    white_row, white_col = white_piece.row, white_piece.col

    black_piece = board.get_piece_by_color(BLACK)
    black_row, black_col = black_piece.row, black_piece.col

    # Occupy the space to the right of the white piece
    board.board[white_row][white_col + 1] = black_piece  
    board.board[black_row][black_col] = 0
    
    result = game.select_square(white_row, white_col)
    assert result is True

    # Attempt to move to the occupied space
    result = game.select_square(white_row, white_col + 1) 
    assert result is False

    assert board.get_piece(white_row, white_col + 1) == black_piece  # The space should still be occupied by the black piece
    assert board.get_piece(white_row, white_col) == white_piece  # The white piece should not have moved
    assert game.turn == WHITE  

def test_valid_jump_move(game, board):
    white_piece = board.get_piece_by_color(WHITE)
    white_row, white_col = white_piece.row, white_piece.col

    black_piece = board.get_piece_by_color(BLACK)
    black_row, black_col = black_piece.row, black_piece.col

    board.board[white_row][white_col + 1] = black_piece 
    board.board[black_row][black_col] = 0
    
    result = game.select_square(white_row, white_col)
    assert result is True

    result = game.select_square(white_row, white_col + 2) # Attempt to jump over the black piece
    assert result is True

    assert board.get_piece(white_row, white_col + 2) == white_piece 
    assert board.get_piece(white_row, white_col + 1) == black_piece  
    assert board.get_piece(white_row, white_col) == 0  
    assert game.turn == BLACK  

def test_invalid_jump_blocked(game, board):
    white_piece = board.get_piece_by_color(WHITE)
    white_row, white_col = white_piece.row, white_piece.col

    black_piece = board.get_piece_by_color(BLACK)
    black_row, black_col = black_piece.row, black_piece.col

    board.board[white_row][white_col + 1] = black_piece 
    board.place_wall(Wall(white_row, white_col + 2, "vertical"))  # Block the jump
    board.board[black_row][black_col] = 0
    
    result = game.select_square(white_row, white_col)
    assert result is True

    result = game.select_square(white_row, white_col + 2) # Attempt to jump over the black piece
    assert result is False

    assert board.get_piece(white_row, white_col) == white_piece  # The white piece should not have moved
    assert board.get_piece(white_row, white_col + 2) == 0  # The space should still be empty
    assert game.turn == WHITE  


def test_pawn_diagonal_move(game, board):
    white_piece = board.get_piece_by_color(WHITE)
    white_row, white_col = white_piece.row, white_piece.col

    black_piece = board.get_piece_by_color(BLACK)
    black_row, black_col = black_piece.row, black_piece.col

    board.board[white_row][white_col + 1] = black_piece 
    board.place_wall(Wall(white_row, white_col + 2, "vertical"))  # Block the jump
    board.board[black_row][black_col] = 0
    
    result = game.select_square(white_row, white_col)
    assert result is True

    result = game.select_square(white_row - 1, white_col + 1) # Attempt to move diagonally
    assert result is True

    assert board.get_piece(white_row - 1, white_col + 1) == white_piece  
    assert game.turn == BLACK


def test_valid_wall_placement(game, board):
    original_white_walls = board.white_walls
    wall = Wall(1, 1, "horizontal")
    
    result = game.place_wall(wall)
    assert result is True

    assert (wall.row, wall.col) in board.horizontal_walls  
    assert wall not in board.valid_walls
    assert board.white_walls == original_white_walls - 1  # One wall should be placed
    assert game.turn == BLACK  # Turn should change

@pytest.mark.parametrize("row,col,orientation", [
    (0, COLS - 1, "horizontal"),
    (0, 0, "vertical"),
    (ROWS, COLS - 1, "horizontal"),
    (ROWS, COLS, "vertical"),
])
def test_invalid_wall_out_of_bounds(game, board, row, col, orientation):
    original_white_walls = board.white_walls
    wall = Wall(row, col, orientation)

    result = game.place_wall(wall)
    assert result is False

    assert (wall.row, wall.col) not in board.horizontal_walls
    assert board.white_walls == original_white_walls  # No walls should be placed
    assert game.turn == WHITE  # Turn should not change


@pytest.mark.parametrize("row,col,orientation,overlap_row,overlap_col,overlap_orientation", [
    (1, 1, "horizontal", 1, 1, "horizontal"),
    (1, 1, "horizontal", 1, 2, "horizontal"),  
    (1, 1, "horizontal", 1, 0, "horizontal"),
    (1, 1, "horizontal", 2, 2, "vertical"),  
    (1, 1, "vertical", 1, 1, "vertical"), 
    (1, 1, "vertical", 0, 1, "vertical"),   
    (1, 1, "vertical", 2, 1, "vertical"),
    (2, 2, "vertical", 1, 1, "horizontal"), 
])
def test_invalid_wall_overlap(game, row, col, orientation, overlap_row, overlap_col, overlap_orientation):
    wall = Wall(row, col, orientation)
    overlapping_wall = Wall(overlap_row, overlap_col, overlap_orientation)

    result = game.place_wall(wall)
    assert result is True

    result = game.place_wall(overlapping_wall)
    assert result is False

def test_invalid_wall_placement_no_walls(game, board):
    board.white_walls = 0
    wall = Wall(1, 1, "horizontal")
    
    result = game.place_wall(wall)
    assert result is False

    assert (wall.row, wall.col) not in board.horizontal_walls  
    assert board.white_walls == 0 
    assert game.turn == WHITE  

def test_invalid_wall_placement_blocking_path(game, board):
    white_piece = board.get_piece_by_color(WHITE)
    row, col = white_piece.row, white_piece.col

    wall_1 = Wall(row, col, "vertical")
    result = game.place_wall(wall_1)
    assert result is True
    assert (wall_1.row, wall_1.col) in board.vertical_walls


    wall_2 = Wall(row - 1, col, "horizontal")
    result = game.place_wall(wall_2)
    assert result is True
    assert (wall_2.row, wall_2.col) in board.horizontal_walls

    # Block whites path by boxing them in
    blocking_wall = Wall(row, col + 2, "vertical")
    result = game.place_wall(blocking_wall)
    assert result is False
    assert (blocking_wall.row, blocking_wall.col) not in board.vertical_walls 