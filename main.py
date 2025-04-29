import pygame
import pygame_gui
from quoridor.constants import *
from quoridor.game import Game
from quoridor.wall import Wall
from quoridor.ai import AI
from ui import render_main_menu, game_over_screen

import time

pygame.init()
pygame.display.set_caption("Quoridor")

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((BACKGROUND_COLOR))
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT), "theme.json")
progress_bar = pygame_gui.elements.UIProgressBar(pygame.Rect((WIDTH - 220, HEIGHT - 40, 200, 30)), 
                                                 manager, 
                                                 visible=False)
                                                 
thinking_text = pygame_gui.elements.UILabel(pygame.Rect((WIDTH - 220, HEIGHT - 70, 200, 30)), 
                                            "AI is thinking...", 
                                            manager, 
                                            visible=False)

# Handles when selected part of screen is a divider
class WallSelection:
    def __init__(self, row, col, orientation):
        self.row = row
        self.col = col
        self.orientation = orientation

# Handles when selected part of screen is a square
class SquareSelection:
    def __init__(self, row, col):
        self.row = row
        self.col = col

def get_selection_from_mouse(pos):
    x, y = pos

    # Calculate row and column of square
    row = int(y // SQUARE_SIZE)
    col = int(x // SQUARE_SIZE)

    # If selection is out of bounds, return None
    if(row >= ROWS or col >= COLS):
        return None
    
    # Calculate remainder to determine proximity to a wall
    x_remainder = x % SQUARE_SIZE
    y_remainder = y % SQUARE_SIZE

    # Check for horizontal wall selection (between rows)
    if WALL_THICKNESS <= x_remainder <= SQUARE_SIZE - WALL_THICKNESS:
        # Horizontal wall selection above the square
        if y_remainder < WALL_THICKNESS:
            return WallSelection(row - 1, col, "horizontal")
        # Horizontal wall selection below the square
        elif y_remainder > SQUARE_SIZE - WALL_THICKNESS:  
            return WallSelection(row, col, "horizontal")

    # Check for vertical wall selection (between columns)
    if WALL_THICKNESS <= y_remainder <= SQUARE_SIZE - WALL_THICKNESS:
        # Vertical wall selection to the left
        if x_remainder < WALL_THICKNESS:  
            return WallSelection(row, col, "vertical")
        # Vertical wall selection to the right
        elif x_remainder > SQUARE_SIZE - WALL_THICKNESS:  
            return WallSelection(row, col + 1, "vertical") 

    # If no wall detected return square selection
    return SquareSelection(row, col)


def main():
    # Get whether any AI players are selected in the main menu
    white_is_ai, black_is_ai = render_main_menu()

    run = True
    game = Game(WIN)
    if black_is_ai or white_is_ai:
        ai = AI(depth=2)

    print("\n--- New Game ---")
    while run:
        time_delta = clock.tick(FPS) / 1000.0

        # Progress callback function to update the progress bar when AI is making a move
        def update_progress(progress):
            progress_bar.set_current_progress(progress)
            manager.update(time_delta)
            manager.draw_ui(WIN)
            pygame.display.update()

        if game.turn == WHITE and white_is_ai:
            thinking_text.show()
            progress_bar.show()
            
            # Get the best move the AI evaluated
            _, new_board, move = ai.negamax(game.get_board(), ai.depth, float("-inf"), float("inf"), WHITE, progress_callback=update_progress)
            thinking_text.hide()
            progress_bar.hide()

            if new_board is not None and move is not None:
                # Make the AI move
                game.ai_move(new_board)
                game.print_move(move)
        
        if game.turn == BLACK and black_is_ai:
            progress_bar.show()
            thinking_text.show()

            _, new_board, move = ai.negamax(game.get_board(), ai.depth, float("-inf"), float("inf"), BLACK, progress_callback=update_progress)
            thinking_text.hide()
            progress_bar.hide()

            if new_board is not None and move is not None:
                game.ai_move(new_board)
                game.print_move(move)

        if game.winner() != None:
            winner = "White" if game.winner() == WHITE else "Black"
            # Display game over screen and determine if user wants to play again
            play_again = game_over_screen(winner)
            if play_again:
                main()
            else:
                exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Only allow interaction with the board if current player is human
            if (game.turn == WHITE and not white_is_ai) or (game.turn == BLACK and not black_is_ai):
                # Handles mouse clicks i.e. placing walls and selecting squares
                if event.type == pygame.MOUSEBUTTONDOWN:
                    selection = get_selection_from_mouse(pos)
                    if isinstance(selection, WallSelection):
                        wall = Wall(selection.row, selection.col, selection.orientation)
                        game.place_wall(wall)
                    if isinstance(selection, SquareSelection):
                        game.select_square(selection.row, selection.col)
                
                # Handles mouse motion i.e. hovering over dividers, which shows a preview of the wall if valid
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    selection =  get_selection_from_mouse(pos)
                    if isinstance(selection, WallSelection):
                        wall = Wall(selection.row, selection.col, selection.orientation)
                        game.wall_hovered = wall
                    if isinstance(selection, SquareSelection):
                        game.wall_hovered = None

        
        WIN.blit(background, (0, 0))
        game.update()
        manager.update(time_delta)
        manager.draw_ui(WIN)
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()
    
    # import cProfile
    # cProfile.run('main()', 'profile_output')

    # import pstats
    # profile = pstats.Stats('profile_output')
    # profile.sort_stats('cumulative').print_stats()