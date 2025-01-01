import pygame
from quoridor.constants import WIDTH, HEIGHT, SQUARE_SIZE, WALL_THICKNESS, ROWS, COLS
from quoridor.game import Game

FPS = 60
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quoridor")

def get_selection_from_mouse(pos):
    x, y = pos

    # Calculate row and column of the clicked square
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE

    if(row >= ROWS or col >= COLS):
        raise Exception("Invalid selection")

    # Calculate remainder to determine proximity to a wall
    x_remainder = x % SQUARE_SIZE
    y_remainder = y % SQUARE_SIZE

    # Check for vertical wall (between columns)
    if WALL_THICKNESS <= x_remainder <= SQUARE_SIZE - WALL_THICKNESS:
        if y_remainder < WALL_THICKNESS:  # Horizontal wall above the square
            return "wall", "horizontal", row, col
        elif y_remainder > SQUARE_SIZE - WALL_THICKNESS:  # Horizontal wall below
            return "wall", "horizontal", row + 1, col

    # Check for horizontal wall (between rows)
    if WALL_THICKNESS <= y_remainder <= SQUARE_SIZE - WALL_THICKNESS:
        if x_remainder < WALL_THICKNESS:  # Vertical wall to the left
            return "wall", "vertical", row, col
        elif x_remainder > SQUARE_SIZE - WALL_THICKNESS:  # Vertical wall to the right
            return "wall", "vertical", row, col + 1

    # If no wall detected, return square selection
    return "square", None, row, col



def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        if game.winner() != None:
            print(game.winner())
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                try:
                    selection_type, wall_type, row, col = get_selection_from_mouse(pos)
                    if selection_type == "wall":
                        print("wall", wall_type, row, col)
                    elif selection_type == "square":
                        game.select(row, col)
                except Exception as e:
                    print(e)
            
            if event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                try:
                    selection_type, wall_type, row, col = get_selection_from_mouse(pos)
                    if selection_type == "wall":
                        game.wall_hovered = (row, col, wall_type)
                    if selection_type == "square":
                        game.wall_hovered = None
                except Exception as e:
                    print(e)
    
        game.update()

    pygame.quit()


if __name__ == "__main__":
    main()

