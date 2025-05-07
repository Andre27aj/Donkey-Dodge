import pygame
import sys
from constante import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR
from jeu import main_game


class Button:
    def __init__(self, x, y, width, height, text, action, border_radius=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = (80, 80, 180)
        self.hover_color = (120, 120, 220)
        self.text_color = (255, 255, 255)
        self.border_radius = int(border_radius * SCALE_FACTOR)
        self.border_width = int(2 * SCALE_FACTOR)
        self.font = pygame.font.SysFont('Arial', int(36 * SCALE_FACTOR))

    def draw(self, screen, mouse_pos):
        # Changer la couleur au survol
        color = self.hover_color if self.is_hovered(mouse_pos) else self.color

        # Dessiner le bouton
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, (255, 255, 255), self.rect,
                         width=self.border_width, border_radius=self.border_radius)

        # Afficher le texte
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
        # Paramètres des boutons
        button_width = int(300 * SCALE_FACTOR)
        button_height = int(70 * SCALE_FACTOR)
        button_spacing = int(30 * SCALE_FACTOR)

        # Position des boutons
        x_pos = self.screen.width // 2 - button_width // 2
        y_start = self.screen.height // 2 - (button_height * 2 + button_spacing * 1.5)

        # Création des boutons
        return [
            Button(x_pos, y_start, button_width, button_height, "Jouer", "jouer"),
            Button(x_pos, y_start + (button_height + button_spacing),
                   button_width, button_height, "Règles du jeu", "regles"),
            Button(x_pos, y_start + (button_height + button_spacing) * 2,
                   button_width, button_height, "Classement", "classement"),
            Button(x_pos, y_start + (button_height + button_spacing) * 3,
                   button_width, button_height, "Quitter", "quitter")
        ]

    def create_title(self):
        title_font = pygame.font.SysFont('Arial', int(72 * SCALE_FACTOR), bold=True)
        title_surf = title_font.render("Donkey Dodge", True, (255, 220, 0))

        # Position du titre au-dessus des boutons
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
            "Évitez les bananes lancées par les singes sur les côtés.",
            "Utilisez les flèches directionnelles pour vous déplacer.",
            "Appuyez sur la flèche du haut pour sauter.",
            "Utilisez SHIFT droit pour effectuer un dash.",
            "Touche A pour viser et tirer depuis la gauche, D pour la droite.",
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
        return Button(
            self.screen.width // 2 - int(150 * SCALE_FACTOR),
            self.screen.height - int(100 * SCALE_FACTOR),
            int(300 * SCALE_FACTOR), int(60 * SCALE_FACTOR),
            "Retour au menu", "back"
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
            self.handle_events(mouse_pos)
            self.draw(mouse_pos)
            self.screen.clock.tick(60)


class LeaderboardScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.title = self.create_title()
        self.back_button = self.create_back_button()
        self.text_font = pygame.font.SysFont('Arial', int(24 * SCALE_FACTOR))

    def create_title(self):
        title_font = pygame.font.SysFont('Arial', int(48 * SCALE_FACTOR), bold=True)
        title_surf = title_font.render("Classement", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen.width // 2, int(100 * SCALE_FACTOR)))
        return (title_surf, title_rect)

    def create_back_button(self):
        return Button(
            self.screen.width // 2 - int(150 * SCALE_FACTOR),
            self.screen.height - int(100 * SCALE_FACTOR),
            int(300 * SCALE_FACTOR), int(60 * SCALE_FACTOR),
            "Retour au menu", "back"
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

        # Afficher le message temporaire
        message = self.text_font.render("Fonctionnalité à venir prochainement!", True, (255, 255, 255))
        message_rect = message.get_rect(center=(self.screen.width // 2, self.screen.height // 2))
        self.screen.get_surface().blit(message, message_rect)

        # Afficher le bouton de retour
        self.back_button.draw(self.screen.get_surface(), mouse_pos)

        pygame.display.flip()

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_events(mouse_pos)
            self.draw(mouse_pos)
            self.screen.clock.tick(60)

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
    original_draw = MainMenu.draw

    def new_draw(self, mouse_pos):
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

    # Remplacer temporairement la méthode draw
    MainMenu.draw = new_draw

    main_menu = MainMenu(screen)
    main_menu.run()

    # Restaurer la méthode originale
    MainMenu.draw = original_draw

    def create_title(self):
        title_font = pygame.font.SysFont('Arial', int(48 * SCALE_FACTOR), bold=True)
        title_surf = title_font.render("Pause", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen.width // 2, int(100 * SCALE_FACTOR)))
        return (title_surf, title_rect)

    def create_buttons(self):
        button_width = int(300 * SCALE_FACTOR)
        button_height = int(70 * SCALE_FACTOR)
        button_spacing = int(30 * SCALE_FACTOR)

        x_pos = self.screen.width // 2 - button_width // 2
        y_start = self.screen.height // 2 - button_height // 2

        return [
            Button(x_pos, y_start - button_height - button_spacing,
                   button_width, button_height, "Continuer", "continue"),
            Button(x_pos, y_start,
                   button_width, button_height, "Retour au menu", "menu"),
            Button(x_pos, y_start + button_height + button_spacing,
                   button_width, button_height, "Quitter", "quit")
        ]

    def handle_events(self, mouse_pos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.result = "continue"
                    self.running = False

            for button in self.buttons:
                if button.is_clicked(mouse_pos, event):
                    self.result = button.action
                    self.running = False

    def draw(self, mouse_pos):
        # Appliquer l'overlay semi-transparent
        self.screen.get_surface().blit(self.overlay, (0, 0))

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

        return self.result  # Renvoie l'action à effectuer

if __name__ == "__main__":
    menu_principal()