import pygame
import numpy as np
import random

from PIL.ImageChops import offset

pygame.init()

# Obtenir la résolution de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.8)
SCREEN_HEIGHT = int(info.current_h * 0.8)

# Initialisation de l'écran avec une fenêtre de 80% de la taille de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mon Jeu avec Intro Vidéo")x

# Couleurs
# Classe Joueur
class Joueur:
    def __init__(self, image_path, position):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (88, 256))
        self.rect = self.image.get_rect(topleft=position)
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.5
        self.max_speed = 7
        self.friction = 0.2
        self.gravity = 1
        self.on_ground = False
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - 90, SCREEN_WIDTH, 20)
        self.ignore_platforms = []
        self.platform_touching = None
        self.previous_y = position[1]  # Stocker la position Y précédente
        self.base_jump_force = -20  # Base jump force
        self.speed_jump_bonus = 0.5  # Multiplier for speed-based jump bonus
        self.jump_force = self.base_jump_force
        self.jump_charging = False
        self.jump_charge = 0
        self.max_jump_charge = 30  # Maximum frames for charge
        self.charge_bonus = 0.6  # Bonus multiplier for charging
        self.normal_acceleration = 0.5  # Store original acceleration
        self.normal_max_speed = 7  # Store original max speed
        self.sprint_acceleration = 1.0  # Higher acceleration when sprinting
        self.sprint_max_speed = 12  # Higher max speed when sprinting
        self.sprint_jump_bonus = 1.2  # Additional jump boost while sprinting
        self.direction = 0  # 0 = none, -1 = left, 1 = right
        self.movement_time = 0  # Tracks how long player moves in same direction
        self.sprint_threshold = 20  # Frames before sprinting activates
        self.max_sprint_time = 60  # Maximum sprint acceleration
        self.min_speed = 3  # Starting speed
        self.max_speed = 12  # Maximum sprint speed

    def update(self, platforms):
        # Stocker la position Y précédente pour déterminer la direction du mouvement
        self.previous_y = self.rect.y

        keys = pygame.key.get_pressed()

        # Gestion des déplacements horizontaux avec accélération
        if keys[pygame.K_LEFT]:
            self.velocity_x -= self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.velocity_x += self.acceleration
        else:
            # Appliquer le frottement si aucune touche n'est pressée
            if self.velocity_x > 0:
                self.velocity_x -= self.friction
            elif self.velocity_x < 0:
                self.velocity_x += self.friction

        # Limiter la vitesse maximale
        self.velocity_x = max(-self.max_speed, min(self.max_speed, self.velocity_x))
        # Determine direction
        old_direction = self.direction
        if keys[pygame.K_LEFT]:
            self.direction = -1
        elif keys[pygame.K_RIGHT]:
            self.direction = 1
        else:
            self.direction = 0

        # Reset movement timer if direction changed or stopped
        if self.direction != old_direction:
            self.movement_time = 0
            self.velocity_x *= 0.5  # Slow down when changing direction

        # Increment movement time if moving in a direction
        if self.direction != 0:
            self.movement_time = min(self.max_sprint_time, self.movement_time + 1)

            # Calculate speed based on movement time
            sprint_factor = min(1.0, self.movement_time / self.sprint_threshold)
            current_max_speed = self.min_speed + (self.max_speed - self.min_speed) * sprint_factor
            self.sprinting = sprint_factor > 0.8  # Consider sprinting at 80% speed

            # Apply acceleration in current direction
            self.velocity_x += self.direction * self.acceleration
        else:
            # Apply friction when not pressing movement keys
            if self.velocity_x > 0:
                self.velocity_x -= self.friction
            elif self.velocity_x < 0:
                self.velocity_x += self.friction
            self.sprinting = False
            self.movement_time = 0

        # Cap maximum speed based on current sprint state
        max_current_speed = self.min_speed + (self.max_speed - self.min_speed) * (min(1.0, self.movement_time / self.sprint_threshold))
        self.velocity_x = max(-max_current_speed, min(max_current_speed, self.velocity_x))

        # Sauter si on est sur le sol avec la flèche du haut
        if keys[pygame.K_UP] and self.on_ground:
            if self.on_ground and not self.jump_charging:
                # Start charging jump
                self.jump_charging = True
                self.jump_charge = 0
            elif self.jump_charging and self.on_ground:
                # Continue charging up to max
                if self.jump_charge < self.max_jump_charge:
                    self.jump_charge += 1
        else:
            # Release jump button - execute the jump if charging
            if self.jump_charging and self.on_ground:
                # Calculate jump force based on horizontal speed AND charge
                speed_bonus = abs(self.velocity_x) * self.speed_jump_bonus
                charge_bonus = (self.jump_charge / self.max_jump_charge) * self.charge_bonus * self.base_jump_force
                self.velocity_y = self.base_jump_force - speed_bonus - charge_bonus
                self.on_ground = False
                self.platform_touching = None

            # Reset charging state
            self.jump_charging = False
            self.jump_charge = 0

        # Descendre de la plateforme si on appuie sur la flèche du bas
        if keys[
            pygame.K_DOWN] and self.on_ground and self.platform_touching and self.platform_touching != self.floor_rect:
            self.ignore_platforms.append(self.platform_touching)
            self.on_ground = False
            self.velocity_y = 1
            self.platform_touching = None

        # Appliquer la gravité
        self.velocity_y += self.gravity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Gestion des collisions avec les plateformes
        self.on_ground = False
        self.platform_touching = None

        for platform in platforms:
            # Ignorer les plateformes dans la liste d'ignore
            if platform in self.ignore_platforms:
                continue

            if self.rect.colliderect(platform):
                # Direction du mouvement (montant ou descendant)
                moving_up = self.velocity_y < 0
                moving_down = self.velocity_y > 0

                if moving_down and self.previous_y + self.rect.height <= platform.top:
                    # Collision par le haut de la plateforme
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.velocity_y = 0
                    self.platform_touching = platform
                # Ne pas bloquer le joueur lorsqu'il saute à travers une plateforme (pas de collision par le bas)

        # Nettoyer la liste des plateformes ignorées
        if self.velocity_y >= 0:  # Le joueur est en train de tomber ou est au sol
            self.ignore_platforms = []

        # Gérer la collision avec le sol
        if self.rect.colliderect(self.floor_rect):
            self.rect.bottom = self.floor_rect.top
            self.on_ground = True
            self.velocity_y = 0
            self.platform_touching = self.floor_rect
            # Sauter si on est sur le sol avec la flèche du haut
        if keys[pygame.K_UP] and self.on_ground:
            # Calculate jump force based on horizontal speed
            speed_bonus = abs(self.velocity_x) * self.speed_jump_bonus
            self.velocity_y = self.base_jump_force - speed_bonus
            self.on_ground = False
            self.platform_touching = None


# Fonction pour générer une nouvelle hauteur
def nouvelle_hauteur(ancienne_hauteur, y_min, y_max):
    while True:
        nouvelle = random.randint(y_min, y_max)
        if abs(nouvelle - ancienne_hauteur) > 50:
            return nouvelle

def creer_balle(x0, y0, angle_min=10, angle_max=50):
    # Génération de la vitesse et de l'angle de tir
    vitesse_min, vitesse_max = 15, 50
    v0 = random.uniform(vitesse_min, vitesse_max)
    angle = random.uniform(angle_min, angle_max)
    angle_rad = np.radians(angle)

    # Calcul des vitesses de la balle
    vx = v0 * np.cos(angle_rad)  # Vitesse horizontale
    vy = -v0 * np.sin(angle_rad)  # Vitesse verticale

    return {"pos": [x0, y0], "vel": [vx, vy], "start_time": pygame.time.get_ticks(), "rotation": 0}

# Fonction pour le lanceur gauche
def lancer_gauche(balles, max_bananes, lanceur_gauche_rect):
    if len(balles) < max_bananes:
        balle = creer_balle(lanceur_gauche_rect.centerx, lanceur_gauche_rect.bottom)
        balle["vel"][0] = abs(balle["vel"][0])  # Faire en sorte que la balle parte vers la droite
        balles.append(balle)

# Fonction pour le lanceur droit
def lancer_droit(balles, max_bananes, lanceur_droite_rect):
    if len(balles) < max_bananes:
        balle = creer_balle(lanceur_droite_rect.centerx, lanceur_droite_rect.bottom)
        balle["vel"][0] = -abs(balle["vel"][0])  # Faire en sorte que la balle parte vers la gauche
        balles.append(balle)

# Fonction principale du jeu
def main_game():
    # Définir les limites de vitesse pour les balles
    vitesse_min, vitesse_max = 15, 35

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
    platformeH_display = platformeH.get_rect(topleft=(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 100))
    platform2_display = platform2.get_rect(topleft=(int(SCREEN_WIDTH * 0.75) - 150, int(SCREEN_HEIGHT * 0.65)))
    platform3_display = platform3.get_rect(topleft=(int(SCREEN_WIDTH * 0.25) - 150, int(SCREEN_HEIGHT * 0.65)))

    # Créer des boîtes de collision décalées vers le bas
    offset_y = 27  # Décalage pour la boîte de collision
    platformeH_rect = pygame.Rect(platformeH_display.x, platformeH_display.y + offset_y, 300, 20)
    platform2_rect = pygame.Rect(platform2_display.x, platform2_display.y + offset_y, 300, 20)
    platform3_rect = pygame.Rect(platform3_display.x, platform3_display.y + offset_y, 300, 20)

    # Positions des lanceurs (ajustés pour ne pas être au milieu de l'image)
    x_gauche = -30  # Lanceur gauche plus proche du bord
    x_droite = SCREEN_WIDTH - 200 + 30  # Lanceur droit plus proche du bord
    y_lanceur_gauche = 0  # Position du lanceur gauche ajustée
    y_lanceur_droite = 0  # Position du lanceur droit ajustée

    # Création des rectangles pour les lanceurs (déplacé ici)
    lanceur_gauche_rect = pygame.Rect(x_gauche, y_lanceur_gauche, 200, 200)
    lanceur_droite_rect = pygame.Rect(x_droite, y_lanceur_droite, 200, 200)

    # Interpolation fluide
    interpolation_factor = 0.05

    # Limites de hauteur pour les balles
    y_min = 50
    y_max = SCREEN_HEIGHT - 4  # Limite de hauteur pour la balle

    angle_min, angle_max = 10, 50

    g = 9.81
    dt = 0.05

    balles = []
    dernier_tir_gauche = random.randint(y_min, y_max)
    dernier_tir_droite = random.randint(y_min, y_max)

    # Création du joueur
    joueur = Joueur("Image/Perso1.png", (SCREEN_WIDTH // 2 - 44, SCREEN_HEIGHT - 356 - 150))  # Position du joueur montée de 100px

    # Ajout de la variable pour la vitesse de déplacement des lanceurs
    lanceur_speed = 10

    clock = pygame.time.Clock()
    run = True
    max_bananes = 4  # Limite de bananes à l'écran
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
        # Vérification de la touche 'E' pour tirer avec le lanceur gauche
        if keys[pygame.K_q]:
            lancer_gauche(balles, max_bananes, lanceur_gauche_rect)

        # Vérification de la touche 'Q' pour tirer avec le lanceur droit
        if keys[pygame.K_e]:
            lancer_droit(balles, max_bananes, lanceur_droite_rect)

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

        # Affichage des plateformes (UNIQUEMENT avec les rectangles d'affichage)
        screen.blit(platformeH, platformeH_display)
        screen.blit(platform2, platform2_display)
        screen.blit(platform3, platform3_display)

        for balle in balles:
            rotated_balle = pygame.transform.rotate(balle_img, balle["rotation"])
            new_rect = rotated_balle.get_rect(center=(int(balle["pos"][0]), int(balle["pos"][1])))
            screen.blit(rotated_balle, new_rect.topleft)

        # Draw collision boxes (for debugging)
        pygame.draw.rect(screen, (255, 0, 0), platformeH_rect, 2)
        pygame.draw.rect(screen, (255, 0, 0), platform2_rect, 2)
        pygame.draw.rect(screen, (255, 0, 0), platform3_rect, 2)

        # Afficher les boîtes de collision des lanceurs
        pygame.draw.rect(screen, (0, 0, 255), lanceur_gauche_rect, 2)  # Bleu
        pygame.draw.rect(screen, (0, 0, 255), lanceur_droite_rect, 2)  # Bleu

        # Afficher le joueur après tous les autres éléments
        screen.blit(joueur.image, joueur.rect.topleft)
        pygame.draw.rect(screen, (0, 255, 0), joueur.rect, 2)  # Boîte de collision du joueur

        pygame.display.flip()
        clock.tick(60)  # Limiter à 60 FPS

# Lancer le jeu sans introduction
if __name__ == "__main__":
    main_game()

    pygame.quit()