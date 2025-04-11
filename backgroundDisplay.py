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
        # Base attributes
        self.velocity_x = 0
        self.velocity_y = 0
        self.previous_y = position[1]
        self.rect = pygame.Rect(
            position[0] + 30,  # Offset from left to center the hitbox
            position[1] + 60,  # Slight offset from top to exclude character's head
            100,  # Narrower width
            200  # Slightly shorter height
        )

        # Lives system
        self.max_lives = 3
        self.lives = self.max_lives
        self.invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = int(60 * SCALE_FACTOR)

        # UI elements
        self.heart_size = int(30 * SCALE_FACTOR)
        self.heart_spacing = int(10 * SCALE_FACTOR)

        # Load animation images
        self.load_animation_images()

        # Animation state tracking
        self.current_state = "idle"  # Can be "idle", "running", "jumping"
        self.image = self.idle_images[0] if self.idle_images else pygame.Surface((100, 200))
        self.facing_right = True

        # Animation timing
        self.idle_timer = 0
        self.idle_threshold = 60  # 1 second at 60fps
        self.current_frame = 0
        self.animation_speed = 8  # Change frame every 8 game ticks
        self.animation_counter = 0
        self.is_idle = False

        # Scaled physics values
        self.acceleration = 0.3 * SCALE_FACTOR
        self.max_speed = 7 * SCALE_FACTOR
        self.friction = 0.2 * SCALE_FACTOR
        self.gravity = 0.7 * SCALE_FACTOR

        # Platform collision
        self.on_ground = False
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - 90, SCREEN_WIDTH, 20)
        self.ignore_platforms = []
        self.platform_touching = None

        # Jump physics
        self.base_jump_force = -25 * SCALE_FACTOR * 1.2
        self.speed_jump_bonus = 0.5 * SCALE_FACTOR
        self.jump_force = self.base_jump_force
        self.jump_charging = False
        self.jump_charge = 0
        self.max_jump_charge = 20
        self.charge_bonus = 0.8 * SCALE_FACTOR

        # Sprint mechanics
        self.normal_acceleration = 0.5 * SCALE_FACTOR
        self.normal_max_speed = 7 * SCALE_FACTOR
        self.sprint_acceleration = 1.0 * SCALE_FACTOR
        self.sprint_max_speed = 12 * SCALE_FACTOR
        self.sprint_jump_bonus = 1.2 * SCALE_FACTOR
        self.direction = 0
        self.movement_time = 0
        self.sprint_threshold = 20
        self.max_sprint_time = 60
        self.min_speed = 3 * SCALE_FACTOR
        self.max_speed = 12 * SCALE_FACTOR
        self.sprinting = False

        # Dash mechanics
        self.dash_available = True
        self.dash_cooldown = 0
        self.dash_cooldown_max = int(45 * SCALE_FACTOR)
        self.dash_distance = 200 * SCALE_FACTOR
        self.dash_ghost_frames = 5
        self.dash_ghosts = []
        self.dash_ghost_timer = 0
        self.dash_ghost_duration = 15

    def load_animation_images(self):
        # Load idle images
        self.idle_images = self.load_image_set("Image/Idle/Idle", 6)

        # Load running images
        self.run_images = self.load_image_set("Image/Course/Course", 6)

        # Load jumping images
        self.jump_images = self.load_image_set("Image/Jump/Jump", 6)

        # Fallback if any set is empty
        if not self.idle_images:
            fallback = pygame.Surface((100, 200))
            fallback.fill((255, 0, 0))
            self.idle_images = [fallback, fallback.copy()]

        if not self.run_images:
            self.run_images = self.idle_images.copy()

        if not self.jump_images:
            self.jump_images = self.idle_images.copy()

def load_image_set(self, base_path, count):
        images = []
        for i in range(1, count + 1):
            try:
                img_path = f"{base_path}{i}.png"
                # Print the path to help debug
                print(f"Trying to load: {img_path}")
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (100, 200))
                images.append(img)
            except pygame.error as e:
                print(f"Could not load image {base_path}{i}.png: {e}")
                continue


        if not images:
            print(f"No images found for path: {base_path}")
            fallback = pygame.Surface((100, 200))
            fallback.fill((255, 0, 0))  # Red fallback image
            images = [fallback]

        return images
def update_player_image(self):
        # Select the correct animation set based on state
        if self.current_state == "idle":
            current_images = self.idle_images
        elif self.current_state == "running":
            current_images = self.run_images
        else:  # jumping
            current_images = self.jump_images

        # Ensure we don't go out of bounds
        if self.current_frame >= len(current_images):
            self.current_frame = 0

        # Get the current frame from the appropriate animation set
        current_img = current_images[self.current_frame]

        # Apply direction
        if self.facing_right:
            self.image = current_img
        else:
            self.image = pygame.transform.flip(current_img, True, False)

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
    keys = pygame.key.get_pressed()

    # REMOVED: Don't create a new player here
    # joueur = Joueur("Image/Idle/Idle1.png", ...)

    # Update ghost positions for dash effect
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

    # Store previous position
    self.previous_y = self.rect.y

    # Determine animation state based on movement
    if not self.on_ground:
        self.current_state = "jumping"
    elif abs(self.velocity_x) > 0.5:
        self.current_state = "running"
        self.idle_timer = 0
    else:
        self.current_state = "idle"
        self.idle_timer += 1
        if self.idle_timer >= self.idle_threshold:
            self.is_idle = True
        else:
            self.is_idle = False

    # Update animation frames
    self.animation_counter += 1
    if self.animation_counter >= self.animation_speed:
        self.animation_counter = 0
        self.current_frame = (self.current_frame + 1) % len(
            self.idle_images if self.current_state == "idle" else
            self.run_images if self.current_state == "running" else
            self.jump_images
        )
        self.update_player_image()

    # Update facing direction based on velocity
    if self.velocity_x > 0.5 and not self.facing_right:
        self.facing_right = True
    elif self.velocity_x < -0.5 and self.facing_right:
        self.facing_right = False

    # Handle dash activation
    if keys[pygame.K_RSHIFT] and self.dash_available:
        dash_direction = 0
        if self.velocity_x > 0.5:
            dash_direction = 1
        elif self.velocity_x < -0.5:
            dash_direction = -1
        elif keys[pygame.K_RIGHT]:
            dash_direction = 1
        elif keys[pygame.K_LEFT]:
            dash_direction = -1
        elif self.facing_right:
            dash_direction = 1
        else:
            dash_direction = -1

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

    # Horizontal movement with acceleration
    if keys[pygame.K_LEFT]:
        self.velocity_x -= self.acceleration
    elif keys[pygame.K_RIGHT]:
        self.velocity_x += self.acceleration
    else:
        # Apply friction if no keys pressed
        if self.velocity_x > 0:
            self.velocity_x -= self.friction
        elif self.velocity_x < 0:
            self.velocity_x += self.friction

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

    # Cap maximum speed
    max_current_speed = self.min_speed + (self.max_speed - self.min_speed) * (
        min(1.0, self.movement_time / self.sprint_threshold))
    self.velocity_x = max(-max_current_speed, min(max_current_speed, self.velocity_x))

    # Jumping with UP key
    if keys[pygame.K_UP] and self.on_ground:
        if not self.jump_charging:
            # Start charging jump
            self.jump_charging = True
            self.jump_charge = 0
        elif self.jump_charging:
            # Continue charging up to max
            if self.jump_charge < self.max_jump_charge:
                self.jump_charge += 2.0
    else:
        # Release jump button - execute the jump if charging
        if self.jump_charging and self.on_ground:
            # Calculate jump force based on horizontal speed
            horizontal_speed = abs(self.velocity_x)
            speed_bonus = horizontal_speed * self.speed_jump_bonus * 2.0

            # Sprint bonus
            if self.sprinting:
                speed_bonus *= 1.5

            # Charge bonus calculation
            charge_factor = self.jump_charge / self.max_jump_charge
            charge_bonus = charge_factor * self.charge_bonus * self.base_jump_force

            # Apply final jump velocity with all bonuses
            final_jump_force = self.base_jump_force - speed_bonus - charge_bonus

            # Ensure minimum jump height even without charging
            if final_jump_force > -15 * SCALE_FACTOR:
                final_jump_force = -15 * SCALE_FACTOR

            self.velocity_y = final_jump_force

            # Give an immediate boost upward to clear platforms
            self.rect.y -= 8

            self.on_ground = False
            self.platform_touching = None

        # Reset charging state
        self.jump_charging = False
        self.jump_charge = 0

    # Drop from platform with DOWN key
    if keys[
        pygame.K_DOWN] and self.on_ground and self.platform_touching and self.platform_touching != self.floor_rect:
        self.ignore_platforms.append(self.platform_touching)
        self.on_ground = False
        self.velocity_y = 1
        self.platform_touching = None

    # Apply gravity and movement
    self.velocity_y += self.gravity
    self.rect.x += self.velocity_x
    self.rect.y += self.velocity_y

    # Platform collision handling
    self.on_ground = False
    self.platform_touching = None

    for platform in platforms:
        # Skip ignored platforms
        if platform in self.ignore_platforms:
            continue

        if self.rect.colliderect(platform):
            # Movement direction (up or down)
            moving_down = self.velocity_y > 0

            if moving_down and self.previous_y + self.rect.height <= platform.top:
                # Collision from top of platform
                self.rect.bottom = platform.top
                self.on_ground = True
                self.velocity_y = 0
                self.platform_touching = platform

    # Clean up ignored platforms list
    if self.velocity_y >= 0:  # Player is falling or on ground
        self.ignore_platforms = []

    # Handle floor collision
    if self.rect.colliderect(self.floor_rect):
        self.rect.bottom = self.floor_rect.top
        self.on_ground = True
        self.velocity_y = 0
        self.platform_touching = self.floor_rect



# Fonction pour générer une nouvelle hauteur
def nouvelle_hauteur(ancienne_hauteur, y_min, y_max):
    while True:
        nouvelle = random.randint(y_min, y_max)
        if abs(nouvelle - ancienne_hauteur) > 50:
            return nouvelle

def creer_balle(x0, y0, angle_min=10, angle_max=50):
    # Higher velocity ranges for more challenging gameplay
    vitesse_min, vitesse_max = 5, 20  # Increased from 5, 25
    v0 = random.uniform(vitesse_min, vitesse_max)
    angle = random.uniform(angle_min, angle_max)
    angle_rad = np.radians(angle)

    # Calculate banana velocities
    vx = v0 * np.cos(angle_rad)  # Horizontal velocity
    vy = -v0 * np.sin(angle_rad)  # Vertical velocity

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
    joueur = Joueur("Image/Idle/Idle1.png",
                    (SCREEN_WIDTH // 2 - 65, SCREEN_HEIGHT - 400 - 150))

    heart_img = pygame.image.load("Image/heart.png")
    heart_img = pygame.transform.scale(heart_img, (int(30 * SCALE_FACTOR), int(30 * SCALE_FACTOR)))

    # Chargement et redimensionnement des images
    back = pygame.image.load("Image/Back.png")
    back = pygame.transform.scale(back, (SCREEN_WIDTH, SCREEN_HEIGHT))
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
    # Ajout de la variable pour la vitesse de déplacement des lanceurs
    lanceur_speed = 10

    clock = pygame.time.Clock()
    run = True
    max_bananes = 4
    firing_cooldown = 500  # Milliseconds between shots
    last_left_fire_time = 0
    last_right_fire_time = 0
    # Limite de bananes à l'écran
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
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_a]:
            if current_time - last_left_fire_time >= firing_cooldown:
                # Fire multiple bananas at once
                num_bananas = 3  # Number of bananas to fire at once
                for _ in range(num_bananas):
                    if len(balles) < max_bananes:
                        # Add slight variation to each banana
                        angle_variation = random.uniform(-10, 10)
                        speed_variation = random.uniform(0.9, 1.1)
                        balle = creer_balle(
                            lanceur_gauche_rect.centerx,
                            lanceur_gauche_rect.bottom,
                            angle_min + angle_variation,
                            angle_max + angle_variation
                        )
                        balle["vel"][0] = abs(balle["vel"][0]) * speed_variation  # Make sure banana goes right
                        balles.append(balle)
                last_left_fire_time = current_time

        # For right launcher
        if keys[pygame.K_d]:
            if current_time - last_right_fire_time >= firing_cooldown:
                # Fire multiple bananas at once
                num_bananas = 3  # Number of bananas to fire at once
                for _ in range(num_bananas):
                    if len(balles) < max_bananes:
                        # Add slight variation to each banana
                        angle_variation = random.uniform(-10, 10)
                        speed_variation = random.uniform(0.9, 1.1)
                        balle = creer_balle(
                            lanceur_droite_rect.centerx,
                            lanceur_droite_rect.bottom,
                            angle_min + angle_variation,
                            angle_max + angle_variation
                        )
                        balle["vel"][0] = -abs(balle["vel"][0]) * speed_variation  # Make sure banana goes left
                        balles.append(balle)
                last_right_fire_time = current_time

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