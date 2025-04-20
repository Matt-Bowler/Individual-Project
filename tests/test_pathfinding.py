import pytest
from pathfinding.core.grid import GridNode 
from quoridor.pathfinding import QuoridorGrid, path_exists, shortest_path
from quoridor.constants import BLACK, WHITE, ROWS, COLS
from quoridor.board import Board
from quoridor.wall import Wall


@pytest.fixture
def grid():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

@pytest.fixture
def board():
    return Board()

def test_wall_blocks_neighbours_horizontal(grid, board):
    white_piece = board.get_piece_by_color(WHITE)
    row, col = white_piece.row, white_piece.col

    board.place_wall(Wall(row - 1, col, "horizontal"))

    grid_obj = QuoridorGrid(matrix=grid, horizontal_walls=board.horizontal_walls, vertical_walls=board.vertical_walls)
    white_node = grid_obj.node(col, row)
    neighbors = grid_obj.neighbors(white_node)

    neighbors_as_tupels = [(n.x, n.y) for n in neighbors]
    
    assert len(neighbors_as_tupels) == 2  # Only two neighbors should be available
    assert (col - 1, row) in neighbors_as_tupels # Left neighbor should be available  
    assert (col + 1, row) in neighbors_as_tupels  # Right neighbor should be available
    assert (col, row - 1) not in neighbors_as_tupels # Up neighbor should be blocked

def test_wall_blocks_neighbours_vertical(grid, board):
    black_piece = board.get_piece_by_color(BLACK)
    row, col = black_piece.row, black_piece.col

    board.place_wall(Wall(row + 1, col, "vertical"))

    grid_obj = QuoridorGrid(matrix=grid, horizontal_walls=board.horizontal_walls, vertical_walls=board.vertical_walls)
    black_node = grid_obj.node(col, row)
    neighbors = grid_obj.neighbors(black_node)

    neighbors_as_tupels = [(n.x, n.y) for n in neighbors]
    
    assert len(neighbors_as_tupels) == 2  # Only two neighbors should be available
    assert (col, row + 1) in neighbors_as_tupels # Down neighbor should be available
    assert (col + 1, row) in neighbors_as_tupels # Right neighbor should be available
    assert (col - 1, row) not in neighbors_as_tupels  # Left neighbor should be blocked


def test_path_exists_empty_board(board):
    assert path_exists(board.board, board.horizontal_walls, board.vertical_walls) is True

def test_path_exists_blocked_board(board):
    white_piece = board.get_piece_by_color(WHITE)
    row, col = white_piece.row, white_piece.col

    wall_1 = Wall(row, col, "vertical")
    board.place_wall(wall_1)
    assert path_exists(board.board, board.horizontal_walls, board.vertical_walls) is True


    wall_2 = Wall(row - 1, col, "horizontal")
    board.place_wall(wall_2)
    assert path_exists(board.board, board.horizontal_walls, board.vertical_walls) is True

    # Block whites path by boxing them in
    blocking_wall = Wall(row, col + 2, "vertical")
    board.place_wall(blocking_wall)
    assert path_exists(board.board, board.horizontal_walls, board.vertical_walls) is False  # Path should be blocked

def test_shortest_path_empty_board(board):
    black_piece = board.get_piece_by_color(BLACK)
    path = shortest_path(board.horizontal_walls, board.vertical_walls, black_piece)
    
    assert len(path) > 0  # There should be a path available
    assert len(path) == ROWS  # The path should be the length of the board height
    assert path[0].x == black_piece.col and path[0].y == black_piece.row  # Start position should match the piece's position

    board.place_wall(Wall(black_piece.row, black_piece.col, "horizontal"))
    path = shortest_path(board.horizontal_walls, board.vertical_walls, black_piece)
    assert len(path) == ROWS + 1