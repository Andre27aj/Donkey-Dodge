import pygame
from constante import SCALE_FACTOR


def draw_hearts(screen, lives, heart_img):
    heart_margin = int(20 * SCALE_FACTOR)
    heart_size = int(30 * SCALE_FACTOR)
    heart_spacing = int(10 * SCALE_FACTOR)

    for i in range(lives):
        screen.blit(heart_img, (heart_margin + i * (heart_size + heart_spacing), heart_margin))


def game_over(screen):
    # Obtenir les dimensions actuelles de l'écran
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Créer une superposition semi-transparente
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
    screen.blit(overlay, (0, 0))

    # Adapter la taille de la police à l'écran
    font_size = int(74 * SCALE_FACTOR)
    font = pygame.font.Font(None, font_size)

    # Générer le texte
    text = font.render("Game Over", True, (255, 0, 0))

    # Centrer le texte à l'écran
    text_x = screen_width // 2 - text.get_width() // 2
    text_y = screen_height // 2 - text.get_height() // 2 - int(50 * SCALE_FACTOR)

    # Dessiner le texte centré
    screen.blit(text, (text_x, text_y))

    # Créer les boutons
    button_width = int(200 * SCALE_FACTOR)
    button_height = int(50 * SCALE_FACTOR)
    button_spacing = int(30 * SCALE_FACTOR)

    # Police des boutons
    button_font_size = int(36 * SCALE_FACTOR)
    button_font = pygame.font.Font(None, button_font_size)

    # Bouton rejouer
    rematch_button = pygame.Rect(
        screen_width // 2 - button_width - button_spacing // 2,
        text_y + text.get_height() + int(50 * SCALE_FACTOR),
        button_width,
        button_height
    )
    rematch_text = button_font.render("Rematch", True, (255, 255, 255))
    rematch_text_x = rematch_button.centerx - rematch_text.get_width() // 2
    rematch_text_y = rematch_button.centery - rematch_text.get_height() // 2

    # Bouton quitter
    quit_button = pygame.Rect(
        screen_width // 2 + button_spacing // 2,
        text_y + text.get_height() + int(50 * SCALE_FACTOR),
        button_width,
        button_height
    )
    quit_text = button_font.render("Quit", True, (255, 255, 255))
    quit_text_x = quit_button.centerx - quit_text.get_width() // 2
    quit_text_y = quit_button.centery - quit_text.get_height() // 2

    # Dessiner les boutons
    pygame.draw.rect(screen, (50, 120, 200), rematch_button, border_radius=10)
    pygame.draw.rect(screen, (200, 50, 50), quit_button, border_radius=10)

    # Dessiner les bordures des boutons
    pygame.draw.rect(screen, (255, 255, 255), rematch_button, width=2, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), quit_button, width=2, border_radius=10)

    # Dessiner le texte des boutons
    screen.blit(rematch_text, (rematch_text_x, rematch_text_y))
    screen.blit(quit_text, (quit_text_x, quit_text_y))

    pygame.display.flip()

    # Attendre un clic sur un bouton
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rematch_button.collidepoint(event.pos):
                    return "rematch"
                if quit_button.collidepoint(event.pos):
                    return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                if event.key == pygame.K_RETURN:
                    return "rematch"

        # Effets de survol
        mouse_pos = pygame.mouse.get_pos()
        if rematch_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (80, 150, 230), rematch_button, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), rematch_button, width=3, border_radius=10)
            screen.blit(rematch_text, (rematch_text_x, rematch_text_y))
        if quit_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (230, 80, 80), quit_button, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), quit_button, width=3, border_radius=10)
            screen.blit(quit_text, (quit_text_x, quit_text_y))

        pygame.display.flip()
        pygame.time.delay(10)