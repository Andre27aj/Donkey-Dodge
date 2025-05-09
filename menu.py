import pygame
import sys
from constante import SCALE_FACTOR
from jeu import main_game
from fonctions import afficher_classement


class Button:
    def __init__(self, x, y, width, height, text, action, border_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.text_color = (255, 255, 255)
        # Smaller font size to fit in square buttons
        self.font = pygame.font.SysFont('Arial', int(24 * SCALE_FACTOR))

        # Rest of the code remains the same
        self.color = (80, 80, 180)
        self.hover_color = (120, 120, 220)
        self.border_radius = int(border_radius * SCALE_FACTOR)
        self.border_width = int(2 * SCALE_FACTOR)

        try:
            self.button_img = pygame.image.load("Image/button.png")
            self.button_img = pygame.transform.scale(self.button_img, (width, height))
            self.use_image = True
        except pygame.error:
            self.use_image = False

    def draw(self, screen, mouse_pos):
        if self.use_image:
            # Use image button
            screen.blit(self.button_img, self.rect.topleft)
        else:
            # Fallback to drawn button
            color = self.hover_color if self.is_hovered(mouse_pos) else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
            pygame.draw.rect(screen, (255, 255, 255), self.rect,
                             width=self.border_width, border_radius=self.border_radius)

        # Display text on top of button
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered(mouse_pos)

class Screen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.background = self.load_background()
        self.clock = pygame.time.Clock()

    def load_background(self):
        try:
            background = pygame.image.load("Image/Back.png")
            return pygame.transform.scale(background, (self.width, self.height))
        except:
            background = pygame.Surface((self.width, self.height))
            background.fill((50, 120, 200))
            return background

    def get_surface(self):
        return self.screen


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.buttons = self.create_buttons()
        self.title = self.create_title()

    def create_buttons(self):
        # Button parameters
        button_width = int(150 * SCALE_FACTOR)
        button_height = button_width
        button_spacing = int(20 * SCALE_FACTOR)  # Reduced spacing

        # Center buttons horizontally
        x_pos = self.screen.width // 2 - button_width // 2

        # Position buttons below the title - using a fixed position instead
        # Leave space at the top for the title (approximately 1/3 of the screen height)
        y_start = int(self.screen.height * 0.33)

        # Create buttons
        return [
            Button(x_pos, y_start, button_width, button_height, "Jouer", "jouer"),
            Button(x_pos, y_start + (button_height + button_spacing),
                   button_width, button_height, "Règles", "regles"),
            Button(x_pos, y_start + (button_height + button_spacing) * 2,
                   button_width, button_height, "Scores", "classement"),
            Button(x_pos, y_start + (button_height + button_spacing) * 3,
                   button_width, button_height, "Quitter", "quitter")
        ]

    def create_title(self):
        try:
            # Load the title image
            title_img = pygame.image.load("Image/titre.png")

            # Scale the image if needed (adjust width/height as necessary)
            img_width = int(890 * SCALE_FACTOR)  # Adjust size as needed
            img_height = int(117 * SCALE_FACTOR)  # Adjust size as needed
            title_img = pygame.transform.scale(title_img, (img_width, img_height))

            # Position the image
            y_start = self.screen.height // 2 - (int(70 * SCALE_FACTOR) * 2 + int(30 * SCALE_FACTOR) * 1.5)
            title_rect = title_img.get_rect(center=(self.screen.width // 2, y_start - int(100 * SCALE_FACTOR)))

            return (title_img, title_rect)
        except pygame.error:
            # Fallback to text if image can't be loaded
            title_font = pygame.font.SysFont('Arial', int(72 * SCALE_FACTOR), bold=True)
            title_surf = title_font.render("Donkey Dodge", True, (255, 220, 0))

            y_start = self.screen.height // 2 - (int(70 * SCALE_FACTOR) * 2 + int(30 * SCALE_FACTOR) * 1.5)
            title_rect = title_surf.get_rect(center=(self.screen.width // 2, y_start - int(100 * SCALE_FACTOR)))

            return (title_surf, title_rect)

    def handle_events(self, mouse_pos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for button in self.buttons:
                if button.is_clicked(mouse_pos, event):
                    if button.action == "jouer":
                        main_game(self.screen.get_surface())
                    elif button.action == "regles":
                        rules_screen = RulesScreen(self.screen)
                        rules_screen.run()
                    elif button.action == "classement":
                        leaderboard_screen = LeaderboardScreen(self.screen)
                        leaderboard_screen.run()
                    elif button.action == "quitter":
                        pygame.quit()
                        sys.exit()

    def draw(self, mouse_pos):
        # Afficher le fond
        self.screen.get_surface().blit(self.screen.background, (0, 0))

        # Afficher le titre
        self.screen.get_surface().blit(self.title[0], self.title[1])

        # Afficher les boutons
        for button in self.buttons:
            button.draw(self.screen.get_surface(), mouse_pos)

        pygame.display.flip()

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_events(mouse_pos)
            self.draw(mouse_pos)
            self.screen.clock.tick(60)


class RulesScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.title = self.create_title()
        self.back_button = self.create_back_button()
        self.rules = [
            "Bienvenue dans Donkey Dodge !",
            "Choisissez votre camp, soit Singe soit Guerrier !",
            "Les Guerriers :",
            "Evitez les bananes lancées par les singes sur les côtés.",
            "Utilisez les flèches directionnelles pour vous déplacer.",
            "Appuyez sur la flèche du haut pour sauter.",
            "Utilisez SHIFT droit pour effectuer un dash.",
            "Les Singes :",
            "Touche A pour viser et tirer depuis le singe de gauche, D pour la droite.",
            "Vous pouvez bouger de haut en bas avec W et S.",
            "Vous avez 3 vies. Chaque collision avec une banane vous fait perdre une vie.",
            "Appuyez sur ESPACE pour mettre le jeu en pause."
        ]
        self.text_font = pygame.font.SysFont('Arial', int(24 * SCALE_FACTOR))

    def create_title(self):
        title_font = pygame.font.SysFont('Arial', int(48 * SCALE_FACTOR), bold=True)
        title_surf = title_font.render("Règles du jeu", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen.width // 2, int(100 * SCALE_FACTOR)))
        return (title_surf, title_rect)

    def create_back_button(self):
        # Create a square button for consistency with other buttons
        button_size = int(150 * SCALE_FACTOR)

        return Button(
            self.screen.width // 2 - button_size // 2,  # Center horizontally
            self.screen.height - button_size - int(40 * SCALE_FACTOR),  # Position at bottom with margin
            button_size, button_size,  # Square button
            "Retour", "back"  # Shorter text to fit in square button
        )
    def handle_events(self, mouse_pos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.back_button.is_clicked(mouse_pos, event):
                self.running = False

    def draw(self, mouse_pos):
        # Afficher le fond
        self.screen.get_surface().blit(self.screen.background, (0, 0))

        # Afficher le titre
        self.screen.get_surface().blit(self.title[0], self.title[1])

        # Afficher les règles
        for i, rule in enumerate(self.rules):
            text = self.text_font.render(rule, True, (255, 255, 255))
            self.screen.get_surface().blit(text, (
                int(100 * SCALE_FACTOR),
                int(200 * SCALE_FACTOR) + i * int(40 * SCALE_FACTOR)
            ))

        # Afficher le bouton de retour
        self.back_button.draw(self.screen.get_surface(), mouse_pos)

        pygame.display.flip()

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            (self.handle_events(mouse_pos))
            self.draw(mouse_pos)
            self.screen.clock.tick(60)


class LeaderboardScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        # Ces attributs sont nécessaires pour éviter les erreurs mais ne seront pas utilisés
        self.title = self.create_title()
        self.back_button = self.create_back_button()
        self.text_font = pygame.font.SysFont('Arial', int(24 * SCALE_FACTOR))

        # Appel direct à la fonction d'affichage du classement
        self.result =afficher_classement(self.screen.get_surface(), Button, SCALE_FACTOR)

        # Gestion du résultat
        if self.result == "quit":
            pygame.quit()
            sys.exit()
        elif self.result == "menu":
            self.running = False

    def create_title(self):
        # Cette méthode est définie mais n'est pas utilisée
        title_font = pygame.font.SysFont('Arial', int(48 * SCALE_FACTOR), bold=True)
        title_surf = title_font.render("Classement", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen.width // 2, int(100 * SCALE_FACTOR)))
        return (title_surf, title_rect)

    def create_back_button(self):
        # Create a square button for consistency with other buttons
        button_size = int(150 * SCALE_FACTOR)

        return Button(
            self.screen.width // 2 - button_size // 2,  # Center horizontally
            self.screen.height - button_size - int(40 * SCALE_FACTOR),  # Position at bottom with margin
            button_size, button_size,  # Square button
            "Retour", "back"  # Shorter text to fit in square button
        )

    def handle_events(self, mouse_pos):
        # Cette méthode est définie mais n'est pas utilisée
        pass

    def draw(self, mouse_pos):
        # Cette méthode est définie mais n'est pas utilisée
        pass

    def run(self):
        # Cette méthode est simplifiée car tout est traité dans __init__
        return self.result

def menu_principal():
    pygame.init()

    # Configuration de l'écran
    info = pygame.display.Info()
    width = int(info.current_w * 0.8)
    height = int(info.current_h * 0.8)
    pygame.display.set_caption("Menu Principal")

    # Création de la surface d'assombrissement pour le menu
    overlay = pygame.Surface((width, height))
    overlay.fill((0, 0, 0))  # Surface noire
    overlay.set_alpha(128)  # Valeur alpha semi-transparente

    screen = Screen(width, height)

    # Ajouter l'overlay à l'objet screen pour y accéder plus tard
    screen.overlay = overlay

    # Modification de la méthode draw de MainMenu
    original_draw_menu = MainMenu.draw
    original_draw_rules = RulesScreen.draw
    original_draw_leaderboard = LeaderboardScreen.draw
    # Initialize audio manager
    from audioManager import AudioManager
    audio_manager = AudioManager()

    # Load and play background music
    audio_manager.load_music("Audio/theme.mp3")
    audio_manager.play_music()


    # Nouvelle méthode draw pour MainMenu
    def new_draw_menu(self, mouse_pos):
        # Afficher le fond
        self.screen.get_surface().blit(self.screen.background, (0, 0))

        # Appliquer l'overlay semi-transparent
        self.screen.get_surface().blit(self.screen.overlay, (0, 0))

        # Afficher le titre
        self.screen.get_surface().blit(self.title[0], self.title[1])

        # Afficher les boutons
        for button in self.buttons:
            button.draw(self.screen.get_surface(), mouse_pos)

        pygame.display.flip()

    # Nouvelle méthode draw pour RulesScreen
    def new_draw_rules(self, mouse_pos):
        # Afficher le fond
        self.screen.get_surface().blit(self.screen.background, (0, 0))

        # Appliquer l'overlay semi-transparent
        self.screen.get_surface().blit(self.screen.overlay, (0, 0))

        # Afficher le titre
        self.screen.get_surface().blit(self.title[0], self.title[1])

        # Utiliser une police plus grande pour les règles
        rules_font = pygame.font.SysFont('Arial', int(36 * SCALE_FACTOR))  # Augmenter la taille (était 24 avant)

        # Ajuster l'espacement vertical pour la nouvelle taille de police
        line_spacing = int(50 * SCALE_FACTOR)  # Augmenter l'espacement entre les lignes (était 40 avant)

        # Centrer les règles horizontalement et verticalement
        total_rules_height = len(self.rules) * line_spacing
        starting_y = (self.screen.height - total_rules_height) // 2  # Position Y pour centrer verticalement

        # Afficher les règles centrées avec une police plus grande
        for i, rule in enumerate(self.rules):
            text = rules_font.render(rule, True, (244, 210, 34))
            text_rect = text.get_rect(center=(self.screen.width // 2, starting_y + i * line_spacing))
            self.screen.get_surface().blit(text, text_rect)

        # Afficher le bouton de retour
        self.back_button.draw(self.screen.get_surface(), mouse_pos)

        pygame.display.flip()

    # Nouvelle méthode draw pour LeaderboardScreen
    def new_draw_leaderboard(self, mouse_pos):
        # Afficher le fond
        self.screen.get_surface().blit(self.screen.background, (0, 0))

        # Appliquer l'overlay semi-transparent
        self.screen.get_surface().blit(self.screen.overlay, (0, 0))

        # Afficher le titre
        self.screen.get_surface().blit(self.title[0], self.title[1])

        # Afficher le message temporaire
        message = self.text_font.render("Fonctionnalité à venir prochainement!", True, (255, 255, 255))
        message_rect = message.get_rect(center=(self.screen.width // 2, self.screen.height // 2))
        self.screen.get_surface().blit(message, message_rect)

        # Afficher le bouton de retour
        self.back_button.draw(self.screen.get_surface(), mouse_pos)

        pygame.display.flip()

    # Remplacer temporairement les méthodes draw
    MainMenu.draw = new_draw_menu
    RulesScreen.draw = new_draw_rules
    LeaderboardScreen.draw = new_draw_leaderboard

    main_menu = MainMenu(screen)
    main_menu.run()

    # Restaurer les méthodes originales (bonne pratique)
    MainMenu.draw = original_draw_menu
    RulesScreen.draw = original_draw_rules
    LeaderboardScreen.draw = original_draw_leaderboard

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_events(mouse_pos)
            self.draw(mouse_pos)
            self.screen.clock.tick(60)

        return self.result  # Renvoie l'action à effectuer

