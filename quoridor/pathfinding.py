from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
from .constants import ROWS, COLS, BLACK, WHITE


def path_exists(board, horizontal_walls, vertical_walls):
    black_pos = None
    white_pos = None
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != 0:
                if piece.color == BLACK:
                    black_pos = (row, col)
                if piece.color == WHITE:
                    white_pos = (row, col)  

    class QuoridorGrid(Grid):
        def neighbors(self, node, diagonal_movement=DiagonalMovement.never):
            x, y = node.x, node.y
            board_row, board_col = y , x

            neighbors = []

            # upwards neighbours 
            if board_row > 0 and (board_row - 1, board_col) not in horizontal_walls and (board_row - 1, board_col - 1) not in horizontal_walls:
                neighbors.append(self.node(x, y - 1))
            # downwards neighbours
            if board_row < self.height - 1 and (board_row, board_col) not in horizontal_walls and (board_row, board_col - 1) not in horizontal_walls:
                neighbors.append(self.node(x, y + 1))
            # left neighbours
            if board_col > 0 and (board_row, board_col) not in vertical_walls and (board_row + 1, board_col) not in vertical_walls:
                neighbors.append(self.node(x - 1, y))
            # right neighbours
            if board_col < self.width - 1 and (board_row, board_col + 1) not in vertical_walls and (board_row + 1,  board_col + 1) not in vertical_walls:
                neighbors.append(self.node(x + 1, y))

            return neighbors

    grid_obj = QuoridorGrid(matrix=grid)

    finder = AStarFinder(diagonal_movement=DiagonalMovement.never)

    black_start = grid_obj.node(black_pos[1], black_pos[0])
    black_goal_nodes = [grid_obj.node(x, ROWS - 1) for x in range(COLS)]

    white_start = grid_obj.node(white_pos[1], white_pos[0])
    white_goal_nodes = [grid_obj.node(x, 0) for x in range(COLS)]

    black_has_path = any(finder.find_path(black_start, goal, grid_obj)[0] for goal in black_goal_nodes)

    white_has_path = any(finder.find_path(white_start, goal, grid_obj)[0] for goal in white_goal_nodes)

    return black_has_path and white_has_path