import pygame
import numpy as np
import random

pygame.init()

# Obtenir la résolution de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.8)
SCREEN_HEIGHT = int(info.current_h * 0.8)

# Initialisation de l'écran avec une fenêtre de 80% de la taille de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Chargement et redimensionnement des images
back = pygame.image.load("Back.png")
back = pygame.transform.scale(back, (SCREEN_WIDTH, SCREEN_HEIGHT))

carlo = pygame.image.load("Carlo.png")
carlo = pygame.transform.scale(carlo, (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 6))

perso1 = pygame.image.load("Perso1.png")
perso1 = pygame.transform.scale(perso1, (SCREEN_WIDTH // 20, SCREEN_HEIGHT // 4))

balle_img = pygame.image.load("balle.png")
balle_img = pygame.transform.scale(balle_img, (SCREEN_WIDTH // 22, SCREEN_HEIGHT // 12))

lanceur_img = pygame.image.load("lanceur.png")
lanceur_img = pygame.transform.scale(lanceur_img, (SCREEN_WIDTH // 9, SCREEN_HEIGHT // 5))

# Retourner le lanceur de gauche
lanceur_gauche_img = pygame.transform.flip(lanceur_img, True, False)
lanceur_droite_img = lanceur_img

# Positions des lanceurs
y_lanceur_gauche = int(SCREEN_HEIGHT * 0.75)
y_lanceur_droite = int(SCREEN_HEIGHT * 0.75)
x_gauche = -30
x_droite = SCREEN_WIDTH - (SCREEN_WIDTH // 9) + 30

# Interpolation fluide
interpolation_factor = 0.05

# Limites de hauteur pour les balles
y_min = SCREEN_HEIGHT // 20
y_max = SCREEN_HEIGHT - 100

# Paramètres des balles
vitesse_min, vitesse_max = 10, 25
angle_min, angle_max = 30, 75

g = 9.81
dt = 0.05

# Temps pour les tirs des lanceurs
next_launch_gauche = pygame.time.get_ticks() + random.randint(500, 1000)
next_launch_droite = pygame.time.get_ticks() + random.randint(500, 1000)

balles = []
dernier_tir_gauche = random.randint(y_min, y_max)
dernier_tir_droite = random.randint(y_min, y_max)


# Fonction pour créer une balle
def creer_balle(x0, y0):
    v0 = random.uniform(vitesse_min, vitesse_max)
    angle = random.uniform(angle_min, angle_max)
    angle_rad = np.radians(angle)

    vx = v0 * np.cos(angle_rad)
    vy = -v0 * np.sin(angle_rad)

    if x0 == x_droite:
        vx = -vx

    return {
        "pos": [x0, y0],
        "vel": [vx, vy],
        "start_time": pygame.time.get_ticks(),
        "rotation": 0
    }


run = True
while run:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Lancer les balles
    if current_time >= next_launch_gauche:
        balles.append(creer_balle(x_gauche, y_lanceur_gauche))
        next_launch_gauche = current_time + random.randint(500, 1000)

    if current_time >= next_launch_droite:
        balles.append(creer_balle(x_droite, y_lanceur_droite))
        next_launch_droite = current_time + random.randint(500, 1000)

    # Mise à jour des balles
    for balle in balles:
        balle["vel"][1] += g * dt
        balle["pos"][0] += balle["vel"][0] * dt * 50
        balle["pos"][1] += balle["vel"][1] * dt * 50
        balle["rotation"] += 5

    balles = [b for b in balles if b["pos"][1] < y_max]

    # Affichage
    screen.blit(back, (0, 0))
    screen.blit(lanceur_gauche_img, (x_gauche, y_lanceur_gauche))
    screen.blit(lanceur_droite_img, (x_droite, y_lanceur_droite))
    screen.blit(perso1, (SCREEN_WIDTH // 2 - perso1.get_width() // 2, SCREEN_HEIGHT - perso1.get_height() - 20))

    for balle in balles:
        rotated_balle = pygame.transform.rotate(balle_img, balle["rotation"])
        new_rect = rotated_balle.get_rect(center=(int(balle["pos"][0]), int(balle["pos"][1])))
        screen.blit(rotated_balle, new_rect.topleft)

    pygame.display.flip()

pygame.quit()
