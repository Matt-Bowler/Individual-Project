from pathfinding.core.grid import Grid
from pathfinding.finder.bi_a_star import BiAStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

from .constants import ROWS, COLS, BLACK, WHITE

grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

class QuoridorGrid(Grid):
    def __init__(self, *args, horizontal_walls, vertical_walls, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontal_walls = set(horizontal_walls)
        self.vertical_walls = set(vertical_walls) 
    
    def neighbors(self, node, diagonal_movement=DiagonalMovement.never):
        x, y = node.x, node.y
        board_row, board_col = y , x

        neighbors = []

        # upwards neighbours 
        if board_row > 0 and (board_row - 1, board_col) not in self.horizontal_walls and (board_row - 1, board_col - 1) not in self.horizontal_walls:
            neighbors.append(self.node(x, y - 1))
        # downwards neighbours
        if board_row < self.height - 1 and (board_row, board_col) not in self.horizontal_walls and (board_row, board_col - 1) not in self.horizontal_walls:
            neighbors.append(self.node(x, y + 1))
        # left neighbours
        if board_col > 0 and (board_row, board_col) not in self.vertical_walls and (board_row + 1, board_col) not in self.vertical_walls:
            neighbors.append(self.node(x - 1, y))
        # right neighbours
        if board_col < self.width - 1 and (board_row, board_col + 1) not in self.vertical_walls and (board_row + 1,  board_col + 1) not in self.vertical_walls:
            neighbors.append(self.node(x + 1, y))

        return neighbors
    

def path_exists(board, horizontal_walls, vertical_walls):
    black_pos = None
    white_pos = None

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != 0:
                if piece.color == BLACK:
                    black_pos = (row, col)
                if piece.color == WHITE:
                    white_pos = (row, col)  
    

    grid_obj = QuoridorGrid(matrix=grid, horizontal_walls=horizontal_walls, vertical_walls=vertical_walls)
    finder = BiAStarFinder(diagonal_movement=DiagonalMovement.never)

    black_start = grid_obj.node(black_pos[1], black_pos[0])
    black_goal_nodes = [grid_obj.node(x, ROWS - 1) for x in range(COLS)]

    white_start = grid_obj.node(white_pos[1], white_pos[0])
    white_goal_nodes = [grid_obj.node(x, 0) for x in range(COLS)]

    for goal in black_goal_nodes:
        if finder.find_path(black_start, goal, grid_obj)[0]:
            break
    else:
        return False

    for goal in white_goal_nodes:
        if finder.find_path(white_start, goal, grid_obj)[0]:
            break
    else:
        return False 

    return True

def get_cached_path(board, piece, horizontal_walls, vertical_walls):
    path = shortest_path(board, horizontal_walls, vertical_walls, piece)
    return path

def shortest_path(board, horizontal_walls, vertical_walls, piece):
    grid_obj = QuoridorGrid(matrix=grid, horizontal_walls=horizontal_walls, vertical_walls=vertical_walls)
    finder = BiAStarFinder(diagonal_movement=DiagonalMovement.never)

    start = grid_obj.node(piece.col, piece.row)
    
    if piece.color == BLACK:
        goals = [grid_obj.node(x, ROWS - 1) for x in range(COLS)]   
    else:
        goals = [grid_obj.node(x, 0) for x in range(COLS)]
    
    min_path = None
    min_path_length = float('inf')

    for goal in goals:
        path, _ = finder.find_path(start, goal, grid_obj)
        if path and len(path) < min_path_length:
            min_path = path
            min_path_length = len(path)    

    return min_path