import pygame
import pygame_gui
from quoridor.constants import * 

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((BACKGROUND_COLOR))
clock = pygame.time.Clock()

def render_main_menu():
    manager = pygame_gui.UIManager((WIDTH, HEIGHT), "theme.json")
    PADDING = 30

    white_is_ai = black_is_ai = None

    title_font_size = 60
    title_font = pygame.font.SysFont(None, title_font_size)
    title = title_font.render("Quoridor", True, WHITE)
    title_pos = (WIDTH // 2 - title.get_width() // 2, PADDING)

    menu_rect = (PADDING, 2 * PADDING + title.get_height(), WIDTH - 2 * PADDING, HEIGHT - 3 * PADDING - title.get_height())

    select_text_font_size = 30
    select_text_font = pygame.font.SysFont(None, select_text_font_size)
    select_text = select_text_font.render("Select what game you want to play:", True, WHITE)
    select_text_pos = (WIDTH // 2 - select_text.get_width() // 2, menu_rect[1] + PADDING)

    human_vs_human_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 2 * PADDING + select_text.get_height(), 200, 50)), 
                                                            text='Human vs Human', 
                                                            manager=manager)
    ai_vs_human_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 3 * PADDING + select_text.get_height() + human_vs_human_button.rect.height, 200, 50)), 
                                                        text='AI vs Human', 
                                                        manager=manager)
    ai_vs_ai_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 4 * PADDING + select_text.get_height() + human_vs_human_button.rect.height + ai_vs_human_button.rect.height, 200, 50)), 
                                                    text='AI vs AI', 
                                                    manager=manager) 


    white_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 6 * PADDING, 200, 50)), 
                                                text='Play as White', 
                                                manager=manager,
                                                visible=False)
    
    black_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, menu_rect[1] + 7 * PADDING + white_button.rect.height, 200, 50)), 
                                                text='Play as Black', 
                                                manager=manager,
                                                visible=False)

    game_mode_selected = False 
    selecting_color = False  

    run = True
    while run:
        time_delta = clock.tick(FPS) / 1000.0

        WIN.blit(background, (0, 0))
        WIN.blit(title, title_pos)
        pygame.draw.rect(WIN, (117, 92, 72), menu_rect)
        WIN.blit(select_text, select_text_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if not game_mode_selected: 
                    if event.ui_element == human_vs_human_button:
                        white_is_ai = black_is_ai = False
                        run = False  

                    elif event.ui_element == ai_vs_human_button:
                        game_mode_selected = True 
                        selecting_color = True  
                        white_button.show()
                        black_button.show()
                        ai_vs_human_button.hide()
                        human_vs_human_button.hide()
                        ai_vs_ai_button.hide()

                    elif event.ui_element == ai_vs_ai_button:
                        white_is_ai = black_is_ai = True
                        run = False  

                elif selecting_color:  
                    if event.ui_element == white_button:
                        white_is_ai = False
                        black_is_ai = True
                        run = False  

                    elif event.ui_element == black_button:
                        white_is_ai = True
                        black_is_ai = False
                        run = False  

            manager.process_events(event)
        manager.update(time_delta)
        manager.draw_ui(WIN)
        pygame.display.update()

    return white_is_ai, black_is_ai


#TODO: add game over screen and back button to menu above
    