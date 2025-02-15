import pygame
from quoridor.constants import WIDTH, HEIGHT, SQUARE_SIZE, WALL_THICKNESS, ROWS, COLS, BLACK, WHITE
from quoridor.game import Game
from quoridor.wall import Wall
from quoridor.ai import AI
import time

FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quoridor")

class WallSelection:
    def __init__(self, row, col, orientation):
        self.row = row
        self.col = col
        self.orientation = orientation

class SquareSelection:
    def __init__(self, row, col):
        self.row = row
        self.col = col

def get_selection_from_mouse(pos):
    x, y = pos

    # Calculate row and column of square
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE

    if(row >= ROWS or col >= COLS):
        return None
    
    # Calculate remainder to determine proximity to a wall
    x_remainder = x % SQUARE_SIZE
    y_remainder = y % SQUARE_SIZE

    # Check for horizontal wall (between rows)
    if WALL_THICKNESS <= x_remainder <= SQUARE_SIZE - WALL_THICKNESS:
        # Horizontal wall above the square
        if y_remainder < WALL_THICKNESS:
            return WallSelection(row - 1, col, "horizontal")
        # Horizontal wall below the square
        elif y_remainder > SQUARE_SIZE - WALL_THICKNESS:  
            return WallSelection(row, col, "horizontal")

    # Check for vertical wall (between columns)
    if WALL_THICKNESS <= y_remainder <= SQUARE_SIZE - WALL_THICKNESS:
        # Vertical wall to the left
        if x_remainder < WALL_THICKNESS:  
            return WallSelection(row, col, "vertical")
        # Vertical wall to the right
        elif x_remainder > SQUARE_SIZE - WALL_THICKNESS:  
            return WallSelection(row, col + 1, "vertical") 

    # If no wall detected return square selection
    return SquareSelection(row, col)

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)
    ai = AI()

    while run:
        clock.tick(FPS)

        # if game.turn == WHITE:
        #     start = time.time()
        #     _, new_board = ai.negamax(game.get_board(), 2, float("-inf"), float("inf"), WHITE)
        #     end = time.time()

        #     print(f"Time taken: {end - start}")
        #     if new_board is not None:
        #         game.ai_move(new_board)
        
        if game.turn == BLACK:
            start = time.time()
            _, new_board = ai.negamax(game.get_board(), 2, float("-inf"), float("inf"), BLACK)
            end = time.time()

            print(f"Time taken: {end - start}")
            if new_board is not None:
                game.ai_move(new_board)

        if game.winner() != None:
            print(f"Player {'Black' if game.winner() == BLACK else 'White'} wins!")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                selection = get_selection_from_mouse(pos)
                if isinstance(selection, WallSelection):
                    wall = Wall(selection.row, selection.col, selection.orientation)
                    game.place_wall(wall)
                if isinstance(selection, SquareSelection):
                    game.select_square(selection.row, selection.col)
            
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                selection =  get_selection_from_mouse(pos)
                if isinstance(selection, WallSelection):
                    wall = Wall(selection.row, selection.col, selection.orientation)
                    game.wall_hovered = wall
                if isinstance(selection, SquareSelection):
                    game.wall_hovered = None
        
        game.update()
    pygame.quit()


if __name__ == "__main__":
    main()
    
    # import cProfile
    # cProfile.run('main()', 'profile_output')

    # import pstats
    # profile = pstats.Stats('profile_output')
    # profile.sort_stats('cumulative').print_stats()
