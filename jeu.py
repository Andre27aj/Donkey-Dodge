import pygame
from constante import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR
from lanceur import Launcher  # Votre classe de lanceurs
from bananeManager import BananeManager  # Gestionnaire de bananes
from joueur import Joueur  # Votre classe joueur
from fonctions import game_over
from score import ScoreManager

def main_game(existing_screen=None):
    global screen

    # Initialisez-le au début du jeu
    score_manager = ScoreManager()

    # Utilisation de l'écran existant, sinon en créer un nouveau
    if existing_screen:
        screen = existing_screen
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()
    else:
        # Initialiser pygame si ce n'est pas déjà fait
        if not pygame.get_init():
            pygame.init()

        # Obtenir la taille de l'écran
        info = pygame.display.Info()
        SCREEN_WIDTH = int(info.current_w * 0.8)
        SCREEN_HEIGHT = int(info.current_h * 0.8)
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Corriger la position d'apparition du joueur
    joueur = Joueur("Image/Idle/Idle1.png",
                    (SCREEN_WIDTH // 2 - 65, SCREEN_HEIGHT - 300))

    heart_img = pygame.image.load("Image/heart.png")
    heart_img = pygame.transform.scale(heart_img, (int(30 * SCALE_FACTOR), int(30 * SCALE_FACTOR)))

    # Chargement et redimensionnement des images
    back = pygame.image.load("Image/Back.png")
    back = pygame.transform.scale(back, (SCREEN_WIDTH, SCREEN_HEIGHT))

    platform = pygame.image.load("Image/Plateforme.png")
    platform = pygame.transform.scale(platform, (150 * SCALE_FACTOR, 150 * SCALE_FACTOR))

    platformeH = pygame.transform.scale(platform, (300 * SCALE_FACTOR, 300 * SCALE_FACTOR))
    platform2 = pygame.transform.scale(platform, (300 * SCALE_FACTOR, 300 * SCALE_FACTOR))
    platform3 = pygame.transform.scale(platform, (300 * SCALE_FACTOR, 300 * SCALE_FACTOR))

    platformeH_display = platformeH.get_rect(topleft=(
        SCREEN_WIDTH // 2 - int(170 * SCALE_FACTOR),
        SCREEN_HEIGHT // 2 - int(50 * SCALE_FACTOR)  # Position ajustée
    ))
    platform2_display = platform2.get_rect(topleft=(
        int(SCREEN_WIDTH * 0.75) - int(150 * SCALE_FACTOR),
        int(SCREEN_HEIGHT * 0.65) - int(20 * SCALE_FACTOR)
    ))
    platform3_display = platform3.get_rect(topleft=(
        int(SCREEN_WIDTH * 0.25) - int(150 * SCALE_FACTOR),
        int(SCREEN_HEIGHT * 0.65) - int(20 * SCALE_FACTOR)
    ))

    # Créer des boîtes de collision décalées vers le bas
    offset_y = 27 * SCALE_FACTOR  # Décalage pour la boîte de collision
    platformeH_rect = pygame.Rect(platformeH_display.x, platformeH_display.y + offset_y, 300 * SCALE_FACTOR,
                                  20 * SCALE_FACTOR)
    platform2_rect = pygame.Rect(platform2_display.x, platform2_display.y + offset_y, 300 * SCALE_FACTOR,
                                 20 * SCALE_FACTOR)
    platform3_rect = pygame.Rect(platform3_display.x, platform3_display.y + offset_y, 300 * SCALE_FACTOR,
                                 20 * SCALE_FACTOR)

    # Positions des lanceurs
    x_gauche = -int(30 * SCALE_FACTOR)
    x_droite = SCREEN_WIDTH - int(170 * SCALE_FACTOR)
    y_lanceur_gauche = 0
    y_lanceur_droite = 0

    # Création des objets Launcher au lieu des rectangles
    lanceur_gauche = Launcher(x_gauche, y_lanceur_gauche, is_left=True, scale_factor=SCALE_FACTOR)
    lanceur_droite = Launcher(x_droite, y_lanceur_droite, is_left=False, scale_factor=SCALE_FACTOR)

    # Initialisation du gestionnaire de bananes
    banane_manager = BananeManager(SCALE_FACTOR, max_bananes=1)

    # Limites de hauteur pour les balles
    y_min = 50
    y_max = SCREEN_HEIGHT - 4

    y_median = (y_min + y_max - lanceur_gauche.height) / 2

    g = 9.81 * SCALE_FACTOR
    dt = 0.05

    y_lanceur_gauche = y_median
    y_lanceur_droite = y_median

    # Création des objets Launcher au lieu des rectangles
    lanceur_gauche = Launcher(x_gauche, y_lanceur_gauche, is_left=True, scale_factor=SCALE_FACTOR)
    lanceur_droite = Launcher(x_droite, y_lanceur_droite, is_left=False, scale_factor=SCALE_FACTOR)

    # Puis, au lieu d'avoir des positions cibles aléatoires, utilisez aussi la position médiane
    dernier_tir_gauche = y_median
    dernier_tir_droite = y_median

    # Variables pour suivre l'état des touches
    key_a_pressed = False
    key_d_pressed = False

    clock = pygame.time.Clock()
    run = True

    while run:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Gestion de la pause avec la touche espace
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = banane_manager.toggle_pause()
                # Si on active la pause, on arrête tout mouvement du joueur
                if paused:
                    joueur.velocity_x = 0
                    joueur.velocity_y = 0

            # Ne traiter les autres commandes que si le jeu n'est pas en pause
            if not banane_manager.paused:
                # Gestion des événements de touche pour le système de visée
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        key_a_pressed = True
                        banane_manager.start_aiming_left(current_time)
                    if event.key == pygame.K_d:
                        key_d_pressed = True
                        banane_manager.start_aiming_right(current_time)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a and key_a_pressed:
                        key_q_pressed = False
                        banane_manager.release_shot_left(lanceur_gauche.rect, current_time)
                    if event.key == pygame.K_d and key_d_pressed:
                        key_d_pressed = False
                        banane_manager.release_shot_right(lanceur_droite.rect, current_time)

        # Ne mettre à jour la logique du jeu que si le jeu n'est pas en pause
        if not banane_manager.paused:
            # Mise à jour du joueur
            joueur.update([platformeH_rect, platform2_rect, platform3_rect])

            # Vérification des limites de l'écran
            if joueur.rect.left < 0:
                joueur.rect.left = 0
                joueur.velocity_x = 0
            if joueur.rect.right > SCREEN_WIDTH:
                joueur.rect.right = SCREEN_WIDTH
                joueur.velocity_x = 0

            # Gestion des contrôles des lanceurs avec les méthodes de la classe
            keys = pygame.key.get_pressed()
            if keys[pygame.K_z]:
                lanceur_gauche.move_up()
                lanceur_droite.move_up()
            if keys[pygame.K_s]:
                lanceur_gauche.move_down()
                lanceur_droite.move_down()

            # Vérification des collisions avec les lanceurs
            if joueur.rect.colliderect(lanceur_gauche.rect):
                joueur.rect.x = lanceur_gauche.rect.right  # Renvoyer le joueur en arrière
            if joueur.rect.colliderect(lanceur_droite.rect):
                joueur.rect.x = lanceur_droite.rect.left - joueur.rect.width  # Renvoyer le joueur en arrière

            # Mise à jour des lanceurs avec interpolation fluide
            lanceur_gauche.set_target_y(dernier_tir_gauche)
            lanceur_droite.set_target_y(dernier_tir_droite)
            lanceur_gauche.update()
            lanceur_droite.update()
            lanceur_gauche.constrain_to_screen(y_min, joueur.floor_rect.top)
            lanceur_droite.constrain_to_screen(y_min, joueur.floor_rect.top)

            # Mise à jour des bananes avec le gestionnaire
            banane_manager.update(dt, g, SCREEN_HEIGHT)
            if banane_manager.check_collisions(joueur) :
                pass



        # Affichage (toujours effectué, même en pause)
        screen.blit(back, (0, 0))

        # Affichage des plateformes
        screen.blit(platformeH, platformeH_display)
        screen.blit(platform2, platform2_display)
        screen.blit(platform3, platform3_display)

        # Affichage des lanceurs avec leur méthode draw
        lanceur_gauche.draw(screen)
        lanceur_droite.draw(screen)

        # Affichage des bananes et UI de pause
        banane_manager.draw(screen)

        # Gestion de l'affichage du joueur (avec invincibilité)
        if not joueur.invincible or joueur.invincibility_timer % 18 >= 9:
            screen.blit(joueur.image, joueur.rect.topleft)

        # Affiche les coeurs mis à l'échelle
        heart_margin = int(20 * SCALE_FACTOR)
        heart_size = int(30 * SCALE_FACTOR)
        heart_spacing = int(10 * SCALE_FACTOR)
        for i in range(joueur.lives):
            screen.blit(heart_img, (heart_margin + i * (heart_size + heart_spacing), heart_margin))

        # Affichage du joueur qui dash
        if joueur.dash_ghosts:
            # Calcule alpha en fonction du temps restant
            alpha_factor = 1 - (joueur.dash_ghost_timer / joueur.dash_ghost_duration)

            for i, ghost_pos in enumerate(joueur.dash_ghosts):
                # rendre le dash transparent
                ghost_alpha = int(200 * alpha_factor * (1 - i / len(joueur.dash_ghosts)))
                ghost_img = joueur.image.copy()
                ghost_img.set_alpha(ghost_alpha)
                screen.blit(ghost_img, ghost_pos)

        # Cooldown du dash
        if not joueur.dash_available:
            cooldown_width = int(50 * SCALE_FACTOR)
            cooldown_height = int(10 * SCALE_FACTOR)
            cooldown_fill = int((joueur.dash_cooldown / joueur.dash_cooldown_max) * cooldown_width)
            pygame.draw.rect(screen, (100, 100, 100),
                             (joueur.rect.centerx - cooldown_width // 2,
                              joueur.rect.top - 20,
                              cooldown_width, cooldown_height))
            pygame.draw.rect(screen, (0, 200, 255),
                             (joueur.rect.centerx - cooldown_width // 2,
                              joueur.rect.top - 20,
                              cooldown_fill, cooldown_height))

        pygame.display.flip()
        clock.tick(60)  # Limiter à 60 FPS

        if joueur.lives <= 0:

            action = game_over(screen, banane_manager.score)

            if action == "rematch":
                # Reset player
                joueur.lives = joueur.max_lives
                joueur.invincible = False
                joueur.rect.x = SCREEN_WIDTH // 2 - 65
                joueur.rect.y = SCREEN_HEIGHT - 300

                # Reset game state
                banane_manager.bananes = []
                banane_manager.score = 0
                banane_manager.reset_launch_states()  # Add this line

                # Reset launchers
                lanceur_gauche.reset()
                lanceur_droite.reset()

                # Reset any targeting variables
                dernier_tir_gauche = y_median
                dernier_tir_droite = y_median

            elif action == "menu":
                return "menu"
            else:
                run = False
        if not run :
            return "quit"
    pygame.quit()
