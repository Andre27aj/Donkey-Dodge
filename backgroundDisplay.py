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
vitesse_min, vitesse_max = 10, 25
angle_min, angle_max = 30, 75

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

    for balle in balles:
        rotated_balle = pygame.transform.rotate(balle_img, balle["rotation"])
        new_rect = rotated_balle.get_rect(center=(int(balle["pos"][0]), int(balle["pos"][1])))
        screen.blit(rotated_balle, new_rect.topleft)

    pygame.display.flip()

pygame.quit()
