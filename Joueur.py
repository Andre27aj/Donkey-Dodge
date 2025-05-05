import pygame
from constante import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR

class Joueur:
    def __init__(self, image_path, position):
        # Attributs du joueur
        self.velocity_x = 0
        self.velocity_y = 0
        self.previous_y = position[1]
        self.rect = pygame.Rect(
            position[0] + int(30*SCALE_FACTOR),
            position[1] + int(60*SCALE_FACTOR),
            70*SCALE_FACTOR,
            110*SCALE_FACTOR
        )
        # Limite de la map
        self.left_boundary = pygame.Rect(-10, 0, 10, SCREEN_HEIGHT)
        self.right_boundary = pygame.Rect(SCREEN_WIDTH - 10, 0, 10, SCREEN_HEIGHT)

        # Point de vie
        self.max_lives = 3
        self.lives = self.max_lives
        self.invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = int(60 * SCALE_FACTOR)

        # Interface de l'utilisateur
        self.heart_size = int(30 * SCALE_FACTOR)
        self.heart_spacing = int(10 * SCALE_FACTOR)

        # Image loader
        self.load_animation_images()

        # Tracking des animations
        self.current_state = "idle"
        self.image = self.idle_images[0] if self.idle_images else pygame.Surface((100, 200))
        self.facing_right = True

        # tempo des animations
        self.idle_timer = 0
        self.idle_threshold = 60
        self.current_frame = 0
        self.animation_speed = 8
        self.animation_counter = 0
        self.is_idle = False

        # Valeur physique a l'echelle
        self.acceleration = 0.3 * SCALE_FACTOR
        self.max_speed = 7 * SCALE_FACTOR
        self.friction = 0.2 * SCALE_FACTOR
        self.gravity = 0.7 * SCALE_FACTOR

        # Colision des platformez
        self.on_ground = False
        floor_offset = int(270 * SCALE_FACTOR)
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - floor_offset + 40, SCREEN_WIDTH, int(20 * SCALE_FACTOR))
        self.ignore_platforms = []
        self.platform_touching = None

        # Physique du saut
        self.base_jump_force = -18 * SCALE_FACTOR
        self.speed_jump_bonus = 0.3 * SCALE_FACTOR
        self.jump_force = self.base_jump_force
        self.jump_charging = False
        self.jump_charge = 0
        self.max_jump_charge = 20
        self.charge_bonus = 0.5 * SCALE_FACTOR

        # Principe du sprint
        self.normal_acceleration = 0.5 * SCALE_FACTOR
        self.normal_max_speed = 7 * SCALE_FACTOR
        self.sprint_acceleration = 1.0 * SCALE_FACTOR
        self.sprint_max_speed = 12 * SCALE_FACTOR
        self.sprint_jump_bonus = 1.1 * SCALE_FACTOR
        self.direction = 0
        self.movement_time = 0
        self.sprint_threshold = 20
        self.max_sprint_time = 60
        self.min_speed = 3 * SCALE_FACTOR
        self.max_speed = 12 * SCALE_FACTOR
        self.sprinting = False

        # Le dash
        self.dash_available = True
        self.dash_cooldown = 0
        self.dash_cooldown_max = int(45 * SCALE_FACTOR)
        self.dash_distance = 200 * SCALE_FACTOR
        self.dash_ghost_frames = 5
        self.dash_ghosts = []
        self.dash_ghost_timer = 0
        self.dash_ghost_duration = 15

    def load_animation_images(self):
        # Chargement des images de l'état immobile
        self.idle_images = self.load_image_set("Image/Idle/Idle", 5)
        # Chargement des images de la course
        self.run_images = self.load_image_set("Image/Course/Course", 5)
        # Chargement des images du saut
        self.jump_images = self.load_image_set("Image/Jump/Jump", 2)

        # Valeur par defaut si ensemble d'images vide
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
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (80*SCALE_FACTOR, 130*SCALE_FACTOR))
                images.append(img)
            except pygame.error as e:
                print(f"Could not load image {base_path}{i}.png: {e}")
                continue
        if not images:
            fallback = pygame.Surface((100*SCALE_FACTOR, 200*SCALE_FACTOR))
            fallback.fill((255, 0, 0))
            images = [fallback]
        return images

    def update_player_image(self):
        # Sélectionne les images en fonction de l'état actuel du joueur
        if self.current_state == "idle":
            current_images = self.idle_images
        elif self.current_state == "running":
            current_images = self.run_images
        else:
            # Si l'état ne correspond ni à "idle" ni à "running", on considère que le joueur est en train de sauter
            current_images = self.jump_images

        # Si l'indice d'image dépasse le nombre d'images disponibles, on le remet à 0
        if self.current_frame >= len(current_images):
            self.current_frame = 0

        # Récupère l'image courante à afficher
        current_img = current_images[self.current_frame]

        # Si le joueur fait face à droite, on affiche l'image telle quelle, sinon on la retourne horizontalement
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
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.invincibility_timer = 0

    def update(self, platforms):
        self.update_invincibility()
        keys = pygame.key.get_pressed()

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

        # Sauvegarde de la position précédente
        self.previous_y = self.rect.y

        # Détermine l'état d'animation du joueur
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

        # Met à jour les images d'animation
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame = (self.current_frame + 1) % len(
                self.idle_images if self.current_state == "idle" else
                self.run_images if self.current_state == "running" else
                self.jump_images
            )
            self.update_player_image()

        # Met à jour la direction dans laquelle le joueur regarde
        if self.velocity_x > 0.5 and not self.facing_right:
            self.facing_right = True
        elif self.velocity_x < -0.5 and self.facing_right:
            self.facing_right = False

        # Gère l'activation du dash
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
                # Stocke la position actuelle pour créer l'effet fantôme
                old_pos = self.rect.topleft

                # Calcule la distance du dash
                dash_x = dash_direction * self.dash_distance

                # Enregistre les positions intermédiaires pour l'effet de traînée du dash
                self.dash_ghosts = []
                for i in range(1, self.dash_ghost_frames + 1):
                    ghost_x = old_pos[0] + (dash_x * i / self.dash_ghost_frames)
                    self.dash_ghosts.append((ghost_x, old_pos[1]))

                # Applique le déplacement instantané
                self.rect.x += dash_x

                # Réinitialise le temps de recharge du dash
                self.dash_available = False
                self.dash_cooldown = 0
                self.dash_ghost_timer = 0

                # Conserve la vitesse verticale mais réduit l'élan horizontal
                self.velocity_x *= 0.3

        # Mouvement horizontal
        if keys[pygame.K_LEFT]:
            self.velocity_x -= self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.velocity_x += self.acceleration
        else:
            # Applique la friction
            if self.velocity_x > 0:
                self.velocity_x -= self.friction
            elif self.velocity_x < 0:
                self.velocity_x += self.friction

        # Détermine la direction du joueur
        old_direction = self.direction
        if keys[pygame.K_LEFT]:
            self.direction = -1
        elif keys[pygame.K_RIGHT]:
            self.direction = 1
        else:
            self.direction = 0

        # Réinitialise le temps de déplacement si la direction a changé
        if self.direction != old_direction:
            self.movement_time = 0
            self.velocity_x *= 0.5  # Slow down when changing direction

        # Gère le sprint
        if self.direction != 0:
            self.movement_time = min(self.max_sprint_time, self.movement_time + 1)
            sprint_factor = min(1.0, self.movement_time / self.sprint_threshold)
            current_max_speed = self.min_speed + (self.max_speed - self.min_speed) * sprint_factor
            self.sprinting = sprint_factor > 0.8
            self.velocity_x += self.direction * self.acceleration
        else:
            if self.velocity_x > 0:
                self.velocity_x -= self.friction
            elif self.velocity_x < 0:
                self.velocity_x += self.friction
            self.sprinting = False
            self.movement_time = 0

        # Limite la vitesse maximale
        max_current_speed = self.min_speed + (self.max_speed - self.min_speed) * (
            min(1.0, self.movement_time / self.sprint_threshold))
        self.velocity_x = max(-max_current_speed, min(max_current_speed, self.velocity_x))

        # Saut
        if keys[pygame.K_UP]:
            if self.on_ground:
                # Force de saut immédiate quand on est au sol
                horizontal_speed = abs(self.velocity_x)
                speed_bonus = horizontal_speed * self.speed_jump_bonus
                self.velocity_y = self.base_jump_force - speed_bonus

                # Empêche un saut trop faible
                if self.velocity_y > -10 * SCALE_FACTOR:
                    self.velocity_y = -10 * SCALE_FACTOR

                self.on_ground = False
                self.jump_charging = False
                self.jump_charge = 0
        else:
            # Reset des variables de saut si la touche est relâchée
            self.jump_charging = False
            self.jump_charge = 0





        # Descend d'une plateforme
        if keys[
            pygame.K_DOWN] and self.on_ground and self.platform_touching and self.platform_touching != self.floor_rect:
            self.ignore_platforms.append(self.platform_touching)
            self.on_ground = False
            self.velocity_y = 1
            self.platform_touching = None

        # Applique la gravité et déplace le joueur
        self.velocity_y += self.gravity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Vérifie les collisions avec les bords de l'écran
        if self.rect.colliderect(self.left_boundary):
            self.rect.left = 0
            self.velocity_x = 0

        if self.rect.colliderect(self.right_boundary):
            self.rect.right = SCREEN_WIDTH
            self.velocity_x = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

        # Gère les collisions avec les plateformes
        self.on_ground = False
        self.platform_touching = None

        for platform in platforms:
            if platform in self.ignore_platforms:
                continue

            if self.rect.colliderect(platform):
                moving_down = self.velocity_y > 0
                if moving_down and self.previous_y + self.rect.height >= platform.top:
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.velocity_y = 0
                    self.jumping = False
                    self.platform_touching = platform

        # Réinitialise les plateformes ignorées
        if self.velocity_y >= 0:
            self.ignore_platforms = []

        # Gère la collision avec le sol
        if self.rect.colliderect(self.floor_rect):
            self.rect.bottom = self.floor_rect.top
            self.on_ground = True
            self.velocity_y = 0
            self.platform_touching = self.floor_rect
