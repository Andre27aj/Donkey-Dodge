import pygame
import numpy as np
import random

from PIL.ImageChops import offset

pygame.init()

# Obtenir la résolution de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.8)
SCREEN_HEIGHT = int(info.current_h * 0.8)
# After getting SCREEN_WIDTH and SCREEN_HEIGHT
REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080
SCALE_X = SCREEN_WIDTH / REFERENCE_WIDTH
SCALE_Y = SCREEN_HEIGHT / REFERENCE_HEIGHT
SCALE_FACTOR = min(SCALE_X, SCALE_Y)  # Use smaller scale for consistency

# Initialisation de l'écran avec une fenêtre de 80% de la taille de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mon Jeu avec Intro Vidéo")

# Couleurs
# Classe Joueur
class Joueur:
    def __init__(self, image_path, position):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (88, 256))
        self.rect = self.image.get_rect(topleft=position)
        self.velocity_x = 0
        self.velocity_y = 0
        self.previous_y = position[1]  # Store previous Y position

        # Lives system
        self.max_lives = 3
        self.lives = self.max_lives
        self.invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = int(60 * SCALE_FACTOR)

        # UI elements
        self.heart_size = int(30 * SCALE_FACTOR)
        self.heart_spacing = int(10 * SCALE_FACTOR)

        # Scaled physics values
        self.acceleration = 0.2 * SCALE_FACTOR
        self.max_speed = 7 * SCALE_FACTOR
        self.friction = 0.2 * SCALE_FACTOR
        self.gravity = 1 * SCALE_FACTOR

        # Platform collision
        self.on_ground = False
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - 90, SCREEN_WIDTH, 20)
        self.ignore_platforms = []
        self.platform_touching = None

        # Jump physics
        self.base_jump_force = -20 * SCALE_FACTOR * 1.2  # Increased by 30%
        self.speed_jump_bonus = 0.3 * SCALE_FACTOR
        self.jump_force = self.base_jump_force
        self.jump_charging = False
        self.jump_charge = 0
        self.max_jump_charge = 23  # Maximum frames for charge
        self.charge_bonus = 0.6 * SCALE_FACTOR

        # Sprint mechanics
        self.normal_acceleration = 0.5 * SCALE_FACTOR
        self.normal_max_speed = 7 * SCALE_FACTOR
        self.sprint_acceleration = 1.0 * SCALE_FACTOR
        self.sprint_max_speed = 12 * SCALE_FACTOR
        self.sprint_jump_bonus = 1.2 * SCALE_FACTOR
        self.direction = 0  # 0 = none, -1 = left, 1 = right
        self.movement_time = 0  # Tracks how long player moves in same direction
        self.sprint_threshold = 20  # Frames before sprinting activates
        self.max_sprint_time = 60  # Maximum sprint acceleration
        self.min_speed = 3 * SCALE_FACTOR  # Starting speed
        self.max_speed = 12 * SCALE_FACTOR  # Maximum sprint speed
        # Add these dash-related attributes after existing attributes
        self.dash_available = True
        self.dash_cooldown = 0
        self.dash_cooldown_max = int(45 * SCALE_FACTOR)  # Longer cooldown for teleport
        self.dash_distance = 200 * SCALE_FACTOR  # Distance to teleport
        self.dash_ghost_frames = 5  # Number of ghost images to show
        self.dash_ghosts = []  # Store positions for ghost effects
        self.dash_ghost_timer = 0
        self.dash_ghost_duration = 15  # How long ghosts remain visible

    def take_damage(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincibility_timer = 0
            return True
        return False

    def update_invincibility(self):
        if self.invincible:
            self.invincibility_timer += 1
            if self.invincibility_timer >= self.invincibility_duration:
                self.invincible = False
                self.invincibility_timer = 0

    def update(self, platforms):
        self.update_invincibility()
        # Stocker la position Y précédente pour déterminer la direction du mouvement
        self.previous_y = self.rect.y

        keys = pygame.key.get_pressed()

        # Update ghost positions if we have any
        if self.dash_ghosts:
            self.dash_ghost_timer += 1
            if self.dash_ghost_timer >= self.dash_ghost_duration:
                self.dash_ghosts = []
                self.dash_ghost_timer = 0

        # Dash cooldown management
        if not self.dash_available:
            self.dash_cooldown += 1
            if self.dash_cooldown >= self.dash_cooldown_max:
                self.dash_available = True
                self.dash_cooldown = 0

        # Stocker la position Y précédente pour déterminer la direction du mouvement
        self.previous_y = self.rect.y

        keys = pygame.key.get_pressed()

        # Dash activation with LSHIFT key - teleport version
        if keys[pygame.K_RSHIFT] and self.dash_available:
            # Get direction for dash (use current direction or movement keys)
            dash_direction = 0
            if self.velocity_x > 0.5:
                dash_direction = 1
            elif self.velocity_x < -0.5:
                dash_direction = -1
            elif keys[pygame.K_RIGHT]:
                dash_direction = 1
            elif keys[pygame.K_LEFT]:
                dash_direction = -1

            # Only dash if we have a direction
            if dash_direction != 0:
                # Store current position for ghost effect
                old_pos = self.rect.topleft

                # Calculate dash distance
                dash_x = dash_direction * self.dash_distance

                # Store intermediate positions for ghost trail
                self.dash_ghosts = []
                for i in range(1, self.dash_ghost_frames + 1):
                    ghost_x = old_pos[0] + (dash_x * i / self.dash_ghost_frames)
                    self.dash_ghosts.append((ghost_x, old_pos[1]))

                # Apply teleport
                self.rect.x += dash_x

                # Reset dash cooldown
                self.dash_available = False
                self.dash_cooldown = 0
                self.dash_ghost_timer = 0

                # Maintain vertical velocity but reduce horizontal momentum
                self.velocity_x *= 0.3

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
            # For normal jumps


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

def game_over():
            font_size = int(74 * SCALE_FACTOR)
            font = pygame.font.Font(None, font_size)
            text = font.render("Game Over", True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
# Fonction principale du jeu
def main_game():
    # Définir les limites de vitesse pour les balles
    vitesse_min, vitesse_max = 15, 35
    # Add near the beginning of main_game()
    heart_img = pygame.image.load("Image/heart.png")
    heart_img = pygame.transform.scale(heart_img, (int(30 * SCALE_FACTOR), int(30 * SCALE_FACTOR)))

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

    platformeH_display = platformeH.get_rect(topleft=(
        SCREEN_WIDTH // 2 - 170,
        SCREEN_HEIGHT // 2 - 50 + (50 * SCALE_FACTOR)  # Adjust based on scale
    ))
    platform2_display = platform2.get_rect(topleft=(
        int(SCREEN_WIDTH * 0.75) - 150,
        int(SCREEN_HEIGHT * 0.65) - (20 * SCALE_FACTOR)
    ))
    platform3_display = platform3.get_rect(topleft=(
        int(SCREEN_WIDTH * 0.25) - 150,
        int(SCREEN_HEIGHT * 0.65) - (20 * SCALE_FACTOR)
    ))
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
            # Check collision with player
        for balle in balles[:]:
            balle_rect = pygame.Rect(
                balle["pos"][0] - 40 * SCALE_FACTOR,
                balle["pos"][1] - 40 * SCALE_FACTOR,
                80 * SCALE_FACTOR,
                80 * SCALE_FACTOR
            )
            if joueur.rect.colliderect(balle_rect) and not joueur.invincible:
                joueur.take_damage()
                balles.remove(balle)
                if joueur.lives <= 0:
                    game_over()
                    run = False

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
        # Display scaled hearts
        heart_margin = int(20 * SCALE_FACTOR)
        heart_size = int(30 * SCALE_FACTOR)
        heart_spacing = int(10 * SCALE_FACTOR)
        for i in range(joueur.lives):
            screen.blit(heart_img, (heart_margin + i * (heart_size + heart_spacing), heart_margin))
        if joueur.invincible:
            if joueur.invincibility_timer % 6 < 3:  # Flash effect
                screen.blit(joueur.image, joueur.rect.topleft)
        # Draw dash ghost trail if it exists
        if joueur.dash_ghosts:
            # Calculate alpha based on remaining time
            alpha_factor = 1 - (joueur.dash_ghost_timer / joueur.dash_ghost_duration)

            for i, ghost_pos in enumerate(joueur.dash_ghosts):
                # Make ghosts progressively more transparent
                ghost_alpha = int(200 * alpha_factor * (1 - i / len(joueur.dash_ghosts)))
                ghost_img = joueur.image.copy()
                ghost_img.set_alpha(ghost_alpha)
                screen.blit(ghost_img, ghost_pos)

        # Show dash cooldown indicator
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

# Lancer le jeu sans introduction
if __name__ == "__main__":
    main_game()

    pygame.quit()