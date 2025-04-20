import pytest
from quoridor.ai import AI 
from quoridor.board import Board
from quoridor.constants import BLACK, WHITE, ROWS, COLS
from quoridor.wall import Wall

@pytest.fixture
def ai():
    return AI(depth=2)

@pytest.fixture
def board():
    return Board()

def test_opposite_color(ai):
    assert ai.opposite_color(BLACK) == WHITE
    assert ai.opposite_color(WHITE) == BLACK

def test_get_all_moves(ai,board):
    white_moves = ai.get_all_moves(board, WHITE)
    black_moves = ai.get_all_moves(board, BLACK)

    assert len(white_moves) > 0
    assert len(black_moves) > 0

def test_filter_walls(ai, board):
    valid_walls = board.get_valid_walls()
    filtered_walls = ai.filter_walls(board, valid_walls, WHITE)

    assert len(filtered_walls) > 0
    assert len(filtered_walls) < len(valid_walls) # Should filter out a majority of "improbable" walls
    assert Wall(0, 0, "horizontal") not in filtered_walls # Edge wall should be filtered out

def test_simulate_piece_move(ai, board):
    piece = board.get_piece_by_color(WHITE)
    temp_board = ai.partial_deepcopy(board)
    temp_piece = temp_board.get_piece(piece.row, piece.col)

    valid_moves = board.get_valid_moves(piece)
    move = valid_moves.pop()
    new_board = ai.simulate_piece_move(temp_piece, move, temp_board)

    assert new_board.get_piece(move[0], move[1]) == temp_piece
    assert new_board.get_piece(piece.row, piece.col) == 0

def test_simulate_wall(ai, board):
    walls = board.get_valid_walls()

    wall = None
    for wall in walls:
        if board.is_valid_wall(wall):
            wall = wall
            break

    temp_board = ai.partial_deepcopy(board)
    new_board = ai.simulate_wall(wall, temp_board, WHITE)

    assert (wall.row, wall.col) in new_board.horizontal_walls or (wall.row, wall.col) in new_board.vertical_walls
    assert wall not in new_board.valid_walls


def test_negamax(ai, board):
    value, move, action = ai.negamax(board, 2, float("-inf"), float("inf"), WHITE)

    assert move is not None
    assert isinstance(value, float)
    assert value != float("-inf")
    assert isinstance(action, tuple) or isinstance(action, Wall)

    if isinstance(action, Wall):
        assert board.is_valid_wall(action)
    if isinstance(action, tuple):
        assert action in board.get_valid_moves(board.get_piece_by_color(WHITE))


def test_partial_deepcopy(ai, board):
    new_board = ai.partial_deepcopy(board)

    assert new_board is not board
    assert new_board.horizontal_walls == board.horizontal_walls
    assert new_board.vertical_walls == board.vertical_walls
    assert new_board.white_walls == board.white_walls
    assert new_board.black_walls == board.black_walls 
    
    for i in range(len(board.board)):
        for j in range(len(board.board[i])):
            assert new_board.board[i][j] == board.board[i][j]