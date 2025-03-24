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
pygame.display.set_caption("Mon Jeu avec Intro Vidéo")

# Classe Joueur
class Joueur:
    def __init__(self, image_path, position):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (88, 256))
        self.rect = self.image.get_rect(topleft=position)
        self.velocity_y = 0
        self.on_ground = False
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - 90, SCREEN_WIDTH, 20)  # Sol abaissé de 100px

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -20  # Augmenter la force du saut
            self.on_ground = False

        self.velocity_y += 1  # Appliquer la gravité
        self.rect.y += self.velocity_y

        # Gérer les collisions avec les plateformes
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0 and self.rect.bottom <= platform.top:  # Si le joueur tombe et n'est pas en dessous
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Si le joueur saute
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

        # Gérer la collision avec le sol
        if self.rect.colliderect(self.floor_rect):
            self.rect.bottom = self.floor_rect.top
            self.on_ground = True
            self.velocity_y = 0

# Fonction principale du jeu
def main_game():
    # Chargement et redimensionnement des images
    back = pygame.image.load("Image/Back.png")
    back = pygame.transform.scale(back, (SCREEN_WIDTH, SCREEN_HEIGHT))

    carlo = pygame.image.load("Image/Carlo.png")
    carlo = pygame.transform.scale(carlo, (288, 288))

    balle_img = pygame.image.load("Image/balle.png")
    balle_img = pygame.transform.scale(balle_img, (80, 80))

    lanceur_img = pygame.image.load("Image/lanceur.png")  # Changer l'image du lanceur
    lanceur_img = pygame.transform.scale(lanceur_img, (200, 200))

    # Retourner le lanceur de gauche
    lanceur_gauche_img = pygame.transform.flip(lanceur_img, True, False)
    lanceur_droite_img = lanceur_img

    platform = pygame.image.load("Image/Plateforme.png")
    platform = pygame.transform.scale(platform, (150, 150))

    platformeH = pygame.transform.scale(platform, (300, 300))
    platform2 = pygame.transform.scale(platform, (300, 300))
    platform3 = pygame.transform.scale(platform, (300, 300))

    # Positions des plateformes
    platformeH_rect = platformeH.get_rect(topleft=(SCREEN_WIDTH/2-150, SCREEN_HEIGHT/2-100))
    platform2_rect = platform2.get_rect(topleft=(SCREEN_WIDTH/3+500, SCREEN_HEIGHT - 370))  # Position abaissée
    platform3_rect = platform3.get_rect(topleft=(SCREEN_WIDTH/3-300, SCREEN_HEIGHT - 370))  # Position abaissée

    # Mettre à jour les dimensions des boîtes de collision des plateformes
    platformeH_rect = pygame.Rect(platformeH_rect.topleft, (300, 50))  # Boîte de collision abaissée
    platform2_rect = pygame.Rect(platform2_rect.topleft, (300, 50))  # Boîte de collision abaissée
    platform3_rect = pygame.Rect(platform3_rect.topleft, (300, 50))  # Boîte de collision abaissée

    # Positions des lanceurs (ajustés pour ne pas être au milieu de l'image)
    x_gauche = -30  # Lanceur gauche plus proche du bord
    x_droite = SCREEN_WIDTH - 200 + 30  # Lanceur droit plus proche du bord
    y_lanceur_gauche = 0  # Position du lanceur gauche ajustée
    y_lanceur_droite = 0  # Position du lanceur droit ajustée

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
    next_launch_gauche = pygame.time.get_ticks() + random.randint(1000, 2000)
    next_launch_droite = pygame.time.get_ticks() + random.randint(1000, 2000)

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

        # Trajectoire pour le lanceur gauche
        if x0 == x_gauche:
            angle = random.uniform(10, 30)  # Angle plus petit pour un lancer plus bas
            v0 = random.uniform(15, 25)  # Vitesse plus faible pour une trajectoire plus douce
            angle_rad = np.radians(angle)
            vx = v0 * np.cos(angle_rad)  # vx positif pour aller vers la droite
            vy = -v0 * np.sin(angle_rad)
        # Trajectoire pour le lanceur droit
        elif x0 == x_droite:
            angle = random.uniform(30, 50)  # Angle plus grand pour un lancer plus haut
            v0 = random.uniform(25, 35)  # Vitesse plus élevée pour une trajectoire plus rapide
            angle_rad = np.radians(angle)
            vx = -v0 * np.cos(angle_rad)  # vx négatif pour aller vers la gauche
            vy = -v0 * np.sin(angle_rad)
        else:
            angle_rad = np.radians(angle)
            vx = v0 * np.cos(angle_rad)
            vy = -v0 * np.sin(angle_rad)

        # Debug : Afficher la direction de la balle pour vérifier
        print(f"Position lanceur: {x0}, Direction de la balle: {vx}, {vy}")

        return {"pos": [x0, y0], "vel": [vx, vy], "start_time": pygame.time.get_ticks(), "rotation": 0}

    # Création du joueur
    joueur = Joueur("Image/Perso1.png", (SCREEN_WIDTH // 2 - 44, SCREEN_HEIGHT - 356 - 150))  # Position du joueur montée de 100px

    # Création des rectangles pour les lanceurs
    lanceur_gauche_rect = pygame.Rect(x_gauche, y_lanceur_gauche, 200, 200)
    lanceur_droite_rect = pygame.Rect(x_droite, y_lanceur_droite, 200, 200)

    # Ajout de la variable pour la vitesse de déplacement des lanceurs
    lanceur_speed = 5

    clock = pygame.time.Clock()
    run = True
    max_bananes = 5  # Limite de bananes à l'écran
    while run:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # Mise à jour du joueur
        joueur.update([platformeH_rect, platform2_rect, platform3_rect])

        # Gestion des contrôles des lanceurs
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            lanceur_gauche_rect.y -= lanceur_speed
            lanceur_droite_rect.y -= lanceur_speed
        if keys[pygame.K_s]:
            lanceur_gauche_rect.y += lanceur_speed
            lanceur_droite_rect.y += lanceur_speed
        if keys[pygame.K_e]:
            if len(balles) < max_bananes:
                balles.append(creer_balle(lanceur_gauche_rect.centerx, lanceur_gauche_rect.bottom))
                balles.append(creer_balle(lanceur_droite_rect.centerx, lanceur_droite_rect.bottom))

        # Vérification des collisions avec les lanceurs
        if joueur.rect.colliderect(lanceur_gauche_rect):
            joueur.rect.x = lanceur_gauche_rect.right  # Renvoyer le joueur en arrière
        if joueur.rect.colliderect(lanceur_droite_rect):
            joueur.rect.x = lanceur_droite_rect.left - joueur.rect.width  # Renvoyer le joueur en arrière

        # Déplacement fluide des lanceurs
        y_lanceur_gauche += (dernier_tir_gauche - y_lanceur_gauche) * interpolation_factor
        y_lanceur_droite += (dernier_tir_droite - y_lanceur_droite) * interpolation_factor

        # Vérification pour ne pas dépasser la boîte de collision du sol
        if y_lanceur_gauche < joueur.floor_rect.top:
            y_lanceur_gauche = joueur.floor_rect.top
        if y_lanceur_droite < joueur.floor_rect.top:
            y_lanceur_droite = joueur.floor_rect.top

        # Tir du lanceur gauche
        if current_time >= next_launch_gauche and abs(y_lanceur_gauche - dernier_tir_gauche) < 2 and len(balles) < max_bananes:
            balles.append(creer_balle(x_gauche, y_lanceur_gauche + 50))
            dernier_tir_gauche = nouvelle_hauteur(dernier_tir_gauche)
            next_launch_gauche = current_time + random.randint(1000, 2000)

        # Tir du lanceur droit
        if current_time >= next_launch_droite and abs(y_lanceur_droite - dernier_tir_droite) < 2 and len(balles) < max_bananes:
            balles.append(creer_balle(x_droite, y_lanceur_droite + 50))
            dernier_tir_droite = nouvelle_hauteur(dernier_tir_droite)
            next_launch_droite = current_time + random.randint(1000, 2000)

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
        screen.blit(lanceur_gauche_img, lanceur_gauche_rect.topleft)
        screen.blit(lanceur_droite_img, lanceur_droite_rect.topleft)

        # Affichage des plateformes
        screen.blit(platformeH, platformeH_rect)
        screen.blit(platform2, platform2_rect)
        screen.blit(platform3, platform3_rect)

        for balle in balles:
            rotated_balle = pygame.transform.rotate(balle_img, balle["rotation"])
            new_rect = rotated_balle.get_rect(center=(int(balle["pos"][0]), int(balle["pos"][1])))
            screen.blit(rotated_balle, new_rect.topleft)

        # Dessiner les boîtes de collision des plateformes
        pygame.draw.rect(screen, (255, 0, 0), platformeH_rect, 2)  # Rouge
        pygame.draw.rect(screen, (255, 0, 0), platform2_rect, 2)  # Rouge
        pygame.draw.rect(screen, (255, 0, 0), platform3_rect, 2)  # Rouge
        pygame.draw.rect(screen, (0, 255, 0), joueur.floor_rect, 2)  # Dessiner la boîte de collision du sol en vert

        # Afficher les boîtes de collision des lanceurs
        pygame.draw.rect(screen, (0, 0, 255), lanceur_gauche_rect, 2)  # Bleu
        pygame.draw.rect(screen, (0, 0, 255), lanceur_droite_rect, 2)  # Bleu

        # Afficher le joueur après tous les autres éléments
        screen.blit(joueur.image, joueur.rect.topleft)

        pygame.display.flip()
        clock.tick(60)  # Limiter à 60 FPS

# Lancer le jeu sans introduction
if __name__ == "__main__":
    main_game()

    pygame.quit()