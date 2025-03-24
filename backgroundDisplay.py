import pygame
import numpy as np
import random
import moviepy as mp


pygame.init()

# Obtenir la résolution de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.8)
SCREEN_HEIGHT = int(info.current_h * 0.8)

# Initialisation de l'écran avec une fenêtre de 80% de la taille de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mon Jeu avec Intro Vidéo")


# Fonction pour jouer la vidéo d'introduction avec fondu d'entrée
def play_intro_video(video_path):
    # Charger la vidéo
    try:
        video = mp.VideoFileClip(video_path)

        # Redimensionner la vidéo pour correspondre à l'écran
        video = video.resize((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Obtenir la durée totale de la vidéo
        duration = video.duration

        # Préparer la surface pour le fondu d'entrée
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_surface.fill((0, 0, 0))

        # Variables pour le timing
        start_time = pygame.time.get_ticks() / 1000  # Convertir en secondes
        current_time = 0

        clock = pygame.time.Clock()
        running = True

        # Fondu d'entrée
        first_frame = video.get_frame(0)
        first_frame_surface = pygame.surfarray.make_surface(first_frame.swapaxes(0, 1))

        for alpha in range(255, -1, -5):
            screen.blit(first_frame_surface, (0, 0))
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

        # Lecture de la vidéo
        while running and current_time <= duration:
            # Mettre à jour le temps actuel
            current_time = pygame.time.get_ticks() / 1000 - start_time

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False  # Indiquer que le jeu devrait se terminer
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        running = False  # Permettre de sauter l'intro

            # Obtenir l'image actuelle de la vidéo
            if current_time <= duration:
                try:
                    frame = video.get_frame(current_time)

                    # Convertir l'image numpy en surface pygame
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

                    # Afficher l'image
                    screen.blit(frame_surface, (0, 0))
                    pygame.display.flip()
                except:
                    pass  # Si une frame ne peut pas être affichée, continuer

            clock.tick(30)  # Limiter à 30 FPS

        # Fermer la vidéo
        video.close()
        return True  # Indiquer que le jeu peut continuer
    except Exception as e:
        print(f"Erreur lors de la lecture de la vidéo: {e}")
        return True  # En cas d'erreur, continuer avec le jeu


# Fonction principale du jeu
def main_game():
    # Chargement et redimensionnement des images
    back = pygame.image.load("Image/Back.png")
    back = pygame.transform.scale(back, (SCREEN_WIDTH, SCREEN_HEIGHT))

    carlo = pygame.image.load("Image/Carlo.png")
    carlo = pygame.transform.scale(carlo, (288, 288))

    perso1 = pygame.image.load("Image/Perso1.png")
    perso1 = pygame.transform.scale(perso1, (88, 256))

    balle_img = pygame.image.load("Image/balle.png")
    balle_img = pygame.transform.scale(balle_img, (80, 80))

    lanceur_img = pygame.image.load("Image/lanceur.png")
    lanceur_img = pygame.transform.scale(lanceur_img, (200, 200))

    # Retourner le lanceur de gauche
    lanceur_gauche_img = pygame.transform.flip(lanceur_img, True, False)
    lanceur_droite_img = lanceur_img

    platform = pygame.image.load("Image/Plateforme.png")
    platform = pygame.transform.scale(platform, (500, 500))


    platformeH = pygame.transform.scale(platform, (300, 300))
    platform2 = pygame.transform.scale(platform, (300, 300))
    platform3 = pygame.transform.scale(platform, (300, 300))
    #
    # # Positions des plateformes
    platformeH_rect = platformeH.get_rect(topleft=(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2-100))
    platform2_rect = platform2.get_rect(topleft=(SCREEN_WIDTH/3+500, SCREEN_HEIGHT - 400))
    platform3_rect = platform3.get_rect(topleft=(SCREEN_WIDTH/3-300, SCREEN_HEIGHT - 400))

    # Positions des lanceurs (encore plus proches du bord)

    x_gauche = -30  # Lanceur gauche plus proche du bord
    x_droite = SCREEN_WIDTH - 200 + 30  # Lanceur droit plus proche du bord
    y_lanceur_gauche = SCREEN_HEIGHT * 0.75
    y_lanceur_droite = SCREEN_HEIGHT * 0.75

    # Interpolation fluide
    interpolation_factor = 0.05

    # Limites de hauteur pour les balles
    y_min = 50
    y_max = SCREEN_HEIGHT - 4  # Limite de hauteur pour la balle

    # Paramètres des balles
    vitesse_min, vitesse_max = 15, 35
    angle_min, angle_max = 10, 50

    g = 9.81
    dt = 0.05

    # Temps pour les tirs des lanceurs (plus rapide)
    next_launch_gauche = pygame.time.get_ticks() + random.randint(500, 1000)
    next_launch_droite = pygame.time.get_ticks() + random.randint(500, 1000)

    balles = []
    dernier_tir_gauche = random.randint(y_min, y_max)
    dernier_tir_droite = random.randint(y_min, y_max)

    # Fonction pour générer une nouvelle hauteur
    def nouvelle_hauteur(ancienne_hauteur):
        while True:
            nouvelle = random.randint(y_min, y_max)
            if abs(nouvelle - ancienne_hauteur) > 50:
                return nouvelle

    def creer_balle(x0, y0):
        v0 = random.uniform(vitesse_min, vitesse_max)
        angle = random.uniform(angle_min, angle_max)
        angle_rad = np.radians(angle)
        vx = v0 * np.cos(angle_rad)
        vy = -v0 * np.sin(angle_rad)
        if x0 == x_droite:
            vx = -vx
        return {"pos": [x0, y0], "vel": [vx, vy], "start_time": pygame.time.get_ticks(), "rotation": 0}


    clock = pygame.time.Clock()
    run = True
    while run:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Déplacement fluide des lanceurs
        y_lanceur_gauche += (dernier_tir_gauche - y_lanceur_gauche) * interpolation_factor
        y_lanceur_droite += (dernier_tir_droite - y_lanceur_droite) * interpolation_factor

        # Tir du lanceur gauche
        if current_time >= next_launch_gauche and abs(y_lanceur_gauche - dernier_tir_gauche) < 2:
            balles.append(creer_balle(x_gauche, y_lanceur_gauche + 50))
            dernier_tir_gauche = nouvelle_hauteur(dernier_tir_gauche)
            next_launch_gauche = current_time + random.randint(500, 1000)

        # Tir du lanceur droit
        if current_time >= next_launch_droite and abs(y_lanceur_droite - dernier_tir_droite) < 2:
            balles.append(creer_balle(x_droite, y_lanceur_droite + 50))
            dernier_tir_droite = nouvelle_hauteur(dernier_tir_droite)
            next_launch_droite = current_time + random.randint(500, 1000)

        # Mise à jour des balles
        for balle in balles:
            balle["vel"][1] += g * dt
            balle["pos"][0] += balle["vel"][0] * dt * 50
            balle["pos"][1] += balle["vel"][1] * dt * 50
            balle["rotation"] += 5

        # Supprimer les balles qui sortent de l'écran
        balles = [b for b in balles if b["pos"][1] <= SCREEN_HEIGHT]

        # Affichage
        screen.blit(back, (0, 0))
        screen.blit(lanceur_gauche_img, (x_gauche, int(y_lanceur_gauche)))
        screen.blit(lanceur_droite_img, (x_droite, int(y_lanceur_droite)))
        screen.blit(perso1, (SCREEN_WIDTH // 2 - perso1.get_width() // 2, SCREEN_HEIGHT - perso1.get_height() - 20))

        # Affichage des plateformes
        screen.blit(platformeH, platformeH_rect)
        screen.blit(platform2, platform2_rect)
        screen.blit(platform3, platform3_rect)

        for balle in balles:
            rotated_balle = pygame.transform.rotate(balle_img, balle["rotation"])
            new_rect = rotated_balle.get_rect(center=(int(balle["pos"][0]), int(balle["pos"][1])))
            screen.blit(rotated_balle, new_rect.topleft)

        pygame.display.flip()
        clock.tick(60)  # Limiter à 60 FPS


# Fonction de transition avec fondu
def transition_fade(screen, clock):
    # Créer une surface noire transparente
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))

    # Fondu au noir
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

    # Pause brève à fond noir
    pygame.time.delay(300)

    return True


# Lancer le jeu avec introduction
if __name__ == "__main__":
    clock = pygame.time.Clock()

    # Jouer la vidéo d'introduction (remplacez par le chemin de votre fichier vidéo)
    continue_game = play_intro_video("Video/intro.mp4")

    # Transition vers le jeu principal
    if continue_game:
        if transition_fade(screen, clock):
            main_game()

    pygame.quit()