import pygame
import pygame_gui
from quoridor.constants import *
from quoridor.game import Game
from quoridor.wall import Wall
from quoridor.ai import AI


pygame.init()
FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quoridor")
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((BACKGROUND_COLOR))
clock = pygame.time.Clock()


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
    row = int(y // SQUARE_SIZE)
    col = int(x // SQUARE_SIZE)

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


def render_menu():
    manager = pygame_gui.UIManager((WIDTH, HEIGHT), "theme.json")
    PADDING = 30

    white_is_ai = black_is_ai = False

    run = True
    while run:
        time_delta = clock.tick(FPS) / 1000.0


        WIN.blit(background, (0, 0))

        title_font_size = 60
        title_font = pygame.font.SysFont(None, title_font_size)
        title = title_font.render("Quoridor", True, WHITE)
        title_pos = (WIDTH // 2 - title.get_width() // 2, PADDING)
        WIN.blit(title, title_pos)

        menu_rect = (PADDING, 2 * PADDING + title.get_height(), WIDTH - 2 * PADDING, HEIGHT - 3 * PADDING - title.get_height())
        pygame.draw.rect(WIN, (117, 92, 72), menu_rect)

        select_text_font_size = 30
        select_text_font = pygame.font.SysFont(None, select_text_font_size)
        select_text = select_text_font.render("Select what game you want to play:", True, WHITE)
        select_text_pos = (WIDTH // 2 - select_text.get_width() // 2, menu_rect[1] + PADDING)
        WIN.blit(select_text, select_text_pos)
        #need to move a lot of this before while loop
        human_vs_human_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 2 * PADDING + select_text.get_height(), 200, 50)), 
                                                             text='Human vs Human', 
                                                             manager=manager)
        ai_vs_human_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 3 * PADDING + select_text.get_height() + human_vs_human_button.rect.height, 200, 50)), 
                                                          text='AI vs Human', 
                                                          manager=manager)
        ai_vs_ai_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 4 * PADDING + select_text.get_height() + human_vs_human_button.rect.height + ai_vs_human_button.rect.height, 200, 50)), 
                                                       text='AI vs AI', 
                                                       manager=manager) 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
              if event.ui_element == human_vs_human_button:
                  print('Hello World!')

            manager.process_events(event)
        manager.update(time_delta)



        manager.draw_ui(WIN)
        pygame.display.update()
    return white_is_ai, black_is_ai



def main():
    white_is_ai, black_is_ai = render_menu()

    run = True
    game = Game(WIN)
    ai = AI()

    while run:
        time_delta = clock.tick(FPS) / 1000.0

        if game.turn == WHITE and white_is_ai:
            _, new_board = ai.negamax(game.get_board(), 2, float("-inf"), float("inf"), WHITE)

            if new_board is not None:
                game.ai_move(new_board)
        
        if game.turn == BLACK and black_is_ai:
            _, new_board = ai.negamax(game.get_board(), 2, float("-inf"), float("inf"), BLACK)

            if new_board is not None:
                game.ai_move(new_board)

        if game.winner() != None:
            print(f"Player {'Black' if game.winner() == BLACK else 'White'} wins!")
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if (game.turn == WHITE and not white_is_ai) or (game.turn == BLACK and not black_is_ai):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if event.button == 3:
                        print(pos)

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

        
        WIN.blit(background, (0, 0))
        game.update()
    pygame.quit()


if __name__ == "__main__":
    main()
    
    # import cProfile
    # cProfile.run('main()', 'profile_output')

    # import pstats
    # profile = pstats.Stats('profile_output')
    # profile.sort_stats('cumulative').print_stats()
