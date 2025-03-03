import pygame
import numpy as np
import random

pygame.init()

# Initialisation de l'écran
screen = pygame.display.set_mode((1792, 1024))

# Chargement des images
back = pygame.image.load("Back.png")
back = pygame.transform.scale(back, (1792, 1024))

carlo = pygame.image.load("Carlo.png")
carlo = pygame.transform.scale(carlo, (288, 288))

perso1 = pygame.image.load("Perso1.png")
perso1 = pygame.transform.scale(perso1, (88, 256))

balle_img = pygame.image.load("balle.png")
balle_img = pygame.transform.scale(balle_img, (80, 80))

lanceur_img = pygame.image.load("lanceur.png")
lanceur_img = pygame.transform.scale(lanceur_img, (200, 200))

# Retourner le lanceur de gauche
lanceur_gauche_img = pygame.transform.flip(lanceur_img, True, False)
lanceur_droite_img = lanceur_img

# Positions des lanceurs (encore plus proches du bord)
x_gauche = -30  # Lanceur gauche plus proche du bord
x_droite = 1792 - 200 + 30  # Lanceur droit plus proche du bord
y_lanceur_gauche = 750
y_lanceur_droite = 750

# Interpolation fluide
interpolation_factor = 0.05

# Limites de hauteur pour les balles
y_min = 50
y_max = 1020  # Limite de hauteur pour la balle

# Paramètres des balles
vitesse_min, vitesse_max = 10, 25
angle_min, angle_max = 30, 75

g = 9.81
dt = 0.05

# Temps pour les tirs des lanceurs (plus rapide)
next_launch_gauche = pygame.time.get_ticks() + random.randint(500, 1000)  # Tir plus fréquent
next_launch_droite = pygame.time.get_ticks() + random.randint(500, 1000)  # Tir plus fréquent

balles = []
dernier_tir_gauche = random.randint(y_min, y_max)
dernier_tir_droite = random.randint(y_min, y_max)

# Variables pour la rafale
mode_rafale_gauche = False
mode_rafale_droite = False
rafale_delay = 250  # Délai plus court entre les balles en rafale
rafale_timer_gauche = 0
rafale_timer_droite = 0
rafale_duration_gauche = 0
rafale_duration_droite = 0

# Déphaser les tirs
dephasage_gauche = random.randint(500, 1000)
dephasage_droite = random.randint(500, 1000)


def creer_balle(x0, y0):
    """Crée une balle lancée depuis x0 et y0."""
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
        "rotation": 0  # Ajouter une variable pour la rotation de la balle
    }


def nouvelle_hauteur(ancienne_hauteur):
    """Génère une nouvelle hauteur différente de la précédente."""
    while True:
        nouvelle = random.randint(y_min, y_max)
        if abs(nouvelle - ancienne_hauteur) > 50:
            return nouvelle


run = True
while run:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Déplacement fluide des lanceurs
    y_lanceur_gauche += (dernier_tir_gauche - y_lanceur_gauche) * interpolation_factor
    y_lanceur_droite += (dernier_tir_droite - y_lanceur_droite) * interpolation_factor

    # Vérifier s'il faut lancer en rafale (plus fréquent)
    if random.randint(1, 3000) == 1:  # Probabilité augmentée
        mode_rafale_gauche = True
        mode_rafale_droite = True
        rafale_duration_gauche = current_time
        rafale_duration_droite = current_time

    # Tir du lanceur gauche
    if current_time >= next_launch_gauche + dephasage_gauche and abs(y_lanceur_gauche - dernier_tir_gauche) < 2:
        balles.append(creer_balle(x_gauche, y_lanceur_gauche + 50))
        dernier_tir_gauche = nouvelle_hauteur(dernier_tir_gauche)
        next_launch_gauche = current_time + random.randint(500, 1000)  # Tir plus fréquent

    # Tir du lanceur droit
    if current_time >= next_launch_droite + dephasage_droite and abs(y_lanceur_droite - dernier_tir_droite) < 2:
        balles.append(creer_balle(x_droite, y_lanceur_droite + 50))
        dernier_tir_droite = nouvelle_hauteur(dernier_tir_droite)
        next_launch_droite = current_time + random.randint(500, 1000)  # Tir plus fréquent

    # Gestion de la rafale pour le lanceur gauche
    if mode_rafale_gauche and current_time - rafale_timer_gauche >= rafale_delay:
        balles.append(creer_balle(x_gauche, y_lanceur_gauche + 50))
        rafale_timer_gauche = current_time
        if current_time - rafale_duration_gauche >= 4000:  # Rafale dure 4 secondes
            mode_rafale_gauche = False

    # Gestion de la rafale pour le lanceur droit
    if mode_rafale_droite and current_time - rafale_timer_droite >= rafale_delay:
        balles.append(creer_balle(x_droite, y_lanceur_droite + 50))
        rafale_timer_droite = current_time
        if current_time - rafale_duration_droite >= 4000:  # Rafale dure 4 secondes
            mode_rafale_droite = False

    # Supprimer les balles après 30 secondes
    balles = [b for b in balles if current_time - b["start_time"] <= 30000]

    # Mise à jour des balles
    for balle in balles:
        balle["vel"][1] += g * dt  # Appliquer la gravité
        balle["pos"][0] += balle["vel"][0] * dt * 50
        balle["pos"][1] += balle["vel"][1] * dt * 50

        # Faire tourner la balle pendant son mouvement
        balle["rotation"] += 5  # Ajouter une petite valeur pour la rotation continue

        # Limiter la position de la balle pour qu'elle ne sorte pas par le haut
        if balle["pos"][1] < y_min:  # Si la balle dépasse le haut de l'écran
            balle["pos"][1] = y_min  # La balle reste à la hauteur minimale
            balle["vel"][1] = 0  # Arrêter la balle (elle reste au même niveau)

        # Supprimer la balle quand elle dépasse les limites du bas
        if balle["pos"][1] > y_max:  # Si la balle dépasse le bas de l'écran
            balles.remove(balle)

    # Affichage
    screen.blit(back, (0, 0))

    # Affichage des lanceurs rapprochés du bord
    screen.blit(lanceur_gauche_img, (x_gauche, int(y_lanceur_gauche)))
    screen.blit(lanceur_droite_img, (x_droite, int(y_lanceur_droite)))

    # Affichage du joueur
    screen.blit(perso1, (896, 685))

    # Affichage des balles avec rotation
    for balle in balles:
        rotated_balle = pygame.transform.rotate(balle_img, balle["rotation"])  # Rotation de la balle
        new_rect = rotated_balle.get_rect(center=(int(balle["pos"][0]), int(balle["pos"][1])))
        screen.blit(rotated_balle, new_rect.topleft)

    pygame.display.flip()

pygame.quit()