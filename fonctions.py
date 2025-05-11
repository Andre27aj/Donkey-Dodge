import pygame
from constante import SCALE_FACTOR
import csv
import os

def draw_hearts(screen, lives, heart_img):
    heart_margin = int(20 * SCALE_FACTOR)
    heart_size = int(30 * SCALE_FACTOR)
    heart_spacing = int(10 * SCALE_FACTOR)

    for i in range(lives):
        screen.blit(heart_img, (heart_margin + i * (heart_size + heart_spacing), heart_margin))


def game_over(screen, score=0):
    # Obtenir la taille de l'écran
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Charger l'image de fond ou appliquer un fond noir semi-transparent
    try:
        back = pygame.image.load("Image/Back.png").convert_alpha()
        back = pygame.transform.scale(back, (screen_width, screen_height))
    except pygame.error:
        # Fallback si l'image n'est pas trouvée
        back = None
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Noir avec 50% de transparence

    # Afficher le fond
    if back:
        screen.blit(back, (0, 0))

        # Créer une surface semi-transparente noire pour assombrir l'image
        dim_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        dim_overlay.fill((0, 0, 0, 128))  # Noir avec 50% de transparence
        screen.blit(dim_overlay, (0, 0))
    else:
        screen.fill((0, 0, 0))  # Fond noir si l'image n'est pas trouvée

    # Demander d'abord le pseudo
    font = pygame.font.SysFont('Arial', 32)
    clock = pygame.time.Clock()

    # Textes pour la saisie du pseudo
    titre = font.render(f"Votre score: {score}", True, (244, 210, 34))
    instruction = font.render("Entrez votre pseudo:", True, (244, 210, 34))

    # Variables pour la saisie
    pseudo = ""
    input_rect = pygame.Rect(screen_width // 4, screen_height // 2, screen_width // 2, 50)
    input_active = True

    # Boucle de saisie du pseudo avec validation
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # Le joueur ferme la fenêtre

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False  # Sortir de la boucle de saisie
                    if not pseudo:
                        pseudo = "Anonyme"
                elif event.key == pygame.K_BACKSPACE:
                    pseudo = pseudo[:-1]
                elif len(pseudo) < 15:  # Limite de longueur
                    if event.unicode.isalnum() or event.unicode in ['-', '_']:
                        pseudo += event.unicode

        # Réafficher le fond
        if back:
            screen.blit(back, (0, 0))
            dim_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            dim_overlay.fill((0, 0, 0, 128))
            screen.blit(dim_overlay, (0, 0))
        else:
            screen.blit(overlay, (0, 0))

        # Afficher les textes
        screen.blit(titre, (screen_width // 2 - titre.get_width() // 2, screen_height // 3))
        screen.blit(instruction, (screen_width // 2 - instruction.get_width() // 2, screen_height // 2 - 70))

        # Dessiner la zone de saisie
        pygame.draw.rect(screen, (244, 210, 34), input_rect, 2)
        text_surface = font.render(pseudo, True, (244, 210, 34))
        screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))

        # Afficher la touche pour valider
        valid_text = font.render("Appuyez sur Entrée pour valider", True, (244, 210, 34))
        screen.blit(valid_text, (screen_width // 2 - valid_text.get_width() // 2, input_rect.bottom + 20))

        pygame.display.flip()
        clock.tick(30)

    # Enregistrer le score avec le pseudo
    from score import ScoreManager
    score_manager = ScoreManager()
    score_manager.enregistrer_score(pseudo, score)

    # Création et affichage des boutons Rematch et Menu
    button_width = int(200 * SCALE_FACTOR)
    button_height = int(200 * SCALE_FACTOR)
    button_spacing = int(30 * SCALE_FACTOR)

    # Load button background image - ADD THIS SECTION
    try:
        button_background = pygame.image.load("Image/button.png").convert_alpha()
        button_background = pygame.transform.scale(button_background, (button_width, button_height))
    except pygame.error:
        button_background = None
        print("Could not load button background image")

    # Police des boutons
    button_font_size = int(36 * SCALE_FACTOR)
    button_font = pygame.font.Font(None, button_font_size)

    # Position des boutons (centrés verticalement)
    vertical_position = screen_height // 2 + int(100 * SCALE_FACTOR)

    # Bouton rejouer
    rematch_button = pygame.Rect(
        screen_width // 2 - button_width - button_spacing // 2,
        vertical_position,
        button_width,
        button_height
    )
    rematch_text = button_font.render("Rejouer", True, (255, 255, 255))
    rematch_text_x = rematch_button.centerx - rematch_text.get_width() // 2
    rematch_text_y = rematch_button.centery - rematch_text.get_height() // 2

    # Bouton menu
    menu_button = pygame.Rect(
        screen_width // 2 + button_spacing // 2,
        vertical_position,
        button_width,
        button_height
    )
    menu_text = button_font.render("Menu", True, (255, 255, 255))
    menu_text_x = menu_button.centerx - menu_text.get_width() // 2
    menu_text_y = menu_button.centery - menu_text.get_height() // 2

    # Réafficher le fond pour l'écran de choix
    if back:
        screen.blit(back, (0, 0))
        dim_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        dim_overlay.fill((0, 0, 0, 128))
        screen.blit(dim_overlay, (0, 0))
    else:
        screen.blit(overlay, (0, 0))

    # Inserted code to load and display "Game Over" image
    try:
        game_over_img = pygame.image.load("Image/gameOver.png").convert_alpha()
        game_over_img = pygame.transform.scale(game_over_img, (int(820 * SCALE_FACTOR), int(110 * SCALE_FACTOR)))
        game_over_rect = game_over_img.get_rect(center=(screen_width // 2, int(100 * SCALE_FACTOR)))
        screen.blit(game_over_img, game_over_rect)
    except pygame.error:
        print("Impossible de charger l'image de Game Over")

    # Afficher le message de remerciement avec le pseudo
    thank_you_text = font.render(f"Merci {pseudo} ! Votre score de {score} a été enregistré", True, (244, 210, 34))
    thank_you_rect = thank_you_text.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(thank_you_text, thank_you_rect)

    # Dessiner les boutons
    if button_background:
        # Draw buttons with background images
        screen.blit(button_background, rematch_button)
        screen.blit(button_background, menu_button)
    else:
        # Fallback to colored buttons if image not available
        pygame.draw.rect(screen, (50, 120, 200), rematch_button, border_radius=10)
        pygame.draw.rect(screen, (200, 50, 50), menu_button, border_radius=10)

    # Always draw the borders
    # Removed white border drawing around buttons as per instructions

    # Dessiner le texte des boutons
    screen.blit(rematch_text, (rematch_text_x, rematch_text_y))
    screen.blit(menu_text, (menu_text_x, menu_text_y))

    pygame.display.flip()

    # Attendre un clic sur un bouton
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rematch_button.collidepoint(event.pos):
                    return "rejouer"
                if menu_button.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_RETURN:
                    return "rejouer"

        # Gérer les effets de survol des boutons
        mouse_pos = pygame.mouse.get_pos()
        if rematch_button.collidepoint(mouse_pos):
            if button_background:
                screen.blit(button_background, rematch_button)
                # Removed border drawing on hover
            else:
                pygame.draw.rect(screen, (80, 150, 230), rematch_button, border_radius=10)
                # Removed border drawing on hover
            screen.blit(rematch_text, (rematch_text_x, rematch_text_y))

        if menu_button.collidepoint(mouse_pos):
            if button_background:
                screen.blit(button_background, menu_button)
                # Removed border drawing on hover
            else:
                pygame.draw.rect(screen, (230, 80, 80), menu_button, border_radius=10)
                # Removed border drawing on hover
            screen.blit(menu_text, (menu_text_x, menu_text_y))

        pygame.display.flip()
        pygame.time.delay(10)


def afficher_classement(screen, Button_class=None, scale_factor=None):
    # Use the provided scale factor or use the imported one
    if scale_factor is None:
        scale_factor = SCALE_FACTOR

    # Couleurs
    TEXT_COLOR = (255, 255, 255)  # Blanc
    TITLE_COLOR = (255, 215, 0)  # Or
    OVERLAY_COLOR = (0, 0, 0, 128)  # Noir semi-transparent

    # Dimensions
    screen_width, screen_height = screen.get_size()

    # Chargement de l'image de fond
    try:
        background = pygame.image.load("Image/Back.png")
        background = pygame.transform.scale(background, (screen_width, screen_height))
    except pygame.error:
        background = pygame.Surface((screen_width, screen_height))
        background.fill((25, 25, 112))  # Fallback en bleu foncé

    # Overlay semi-transparent
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)

    # Create button details
    button_size = int(150 * scale_factor)
    button_x = screen_width // 2 - button_size // 2
    button_y = screen_height - button_size - int(40 * scale_factor)

    # Create button rect for collision detection if Button_class is not provided
    button_rect = pygame.Rect(button_x, button_y, button_size, button_size)

    # Create button object if Button_class is provided
    back_button = None
    if Button_class:
        back_button = Button_class(
            button_x, button_y,
            button_size, button_size,
            "Retour", "back"
        )

    # Chargement et tri des scores
    scores = []
    try:
        if os.path.exists('scores.csv'):
            try:
                # Try UTF-8 first as it's most comprehensive
                with open('scores.csv', 'r', newline='', encoding='utf-8') as fichier:
                    lecteur = csv.reader(fichier)
                    next(lecteur, None)  # Skip header
                    for ligne in lecteur:
                        if len(ligne) >= 3:  # Format: Date, Pseudo, Score
                            try:
                                date, nom, score = ligne[0], ligne[1], int(ligne[2])
                                scores.append((nom, score))
                            except (ValueError, IndexError):
                                continue
            except UnicodeDecodeError:
                # Fallback to other encodings if UTF-8 fails
                encodings = ['latin1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        with open('scores.csv', 'r', newline='', encoding=encoding) as fichier:
                            lecteur = csv.reader(fichier)
                            next(lecteur, None)  # Skip header
                            for ligne in lecteur:
                                if len(ligne) >= 3:
                                    try:
                                        date, nom, score = ligne[0], ligne[1], int(ligne[2])
                                        scores.append((nom, score))
                                    except (ValueError, IndexError):
                                        continue
                        break  # We found a working encoding, so stop trying
                    except UnicodeDecodeError:
                        continue
        else:
            # Create empty file if it doesn't exist
            with open('scores.csv', 'w', newline='', encoding='utf-8') as fichier:
                writer = csv.writer(fichier)
                writer.writerow(["Date", "Pseudo", "Score"])  # Add headers
    except IOError as e:
        print(f"Error accessing scores file: {e}")

    # Trier les scores par ordre décroissant
    scores.sort(key=lambda x: x[1], reverse=True)
    top_scores = scores[:5]  # Top 5

    # Initialiser les polices
    pygame.font.init()
    titre_font = pygame.font.SysFont('Arial', 48, bold=True)
    score_font = pygame.font.SysFont('Arial', 36)
    button_font = pygame.font.SysFont('Arial', 32)

    run = True
    while run:
        mouse_pos = pygame.mouse.get_pos()

        # Dessiner l'arrière-plan et l'overlay
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))

        # Dessiner le titre
        titre = titre_font.render("TOP 5 DES MEILLEURS SCORES", True, TITLE_COLOR)
        titre_rect = titre.get_rect(center=(screen_width // 2, 80))
        screen.blit(titre, titre_rect)

        # Dessiner les scores
        if top_scores:
            y_pos = 180
            for i, (nom, score) in enumerate(top_scores):
                rang = score_font.render(f"{i + 1}.", True, TEXT_COLOR)
                screen.blit(rang, (screen_width // 4 - 40, y_pos))

                nom_texte = score_font.render(f"{nom}", True, TEXT_COLOR)
                screen.blit(nom_texte, (screen_width // 4, y_pos))

                score_texte = score_font.render(f"{score}", True, TEXT_COLOR)
                screen.blit(score_texte, (screen_width * 3 // 4 - 50, y_pos))

                y_pos += 70
        else:
            message = score_font.render("Aucun score enregistré", True, TEXT_COLOR)
            message_rect = message.get_rect(center=(screen_width // 2, 250))
            screen.blit(message, message_rect)

        # Draw the back button
        if back_button:
            # Use the Button class if provided
            back_button.draw(screen, mouse_pos)
        else:
            # Draw a simple button if Button class is not provided
            button_color = (80, 150, 230) if button_rect.collidepoint(mouse_pos) else (50, 120, 200)
            pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, width=2, border_radius=10)

            # Add text to button
            button_text = button_font.render("Retour", True, (255, 255, 255))
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button and hasattr(back_button, 'is_clicked'):
                    if back_button.is_clicked(mouse_pos, event):
                        return "menu"
                elif button_rect.collidepoint(mouse_pos):
                    return "menu"

        pygame.display.flip()

    return "menu"