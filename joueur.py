import pygame
from constante import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR

class Joueur:
    def __init__(self, image_path, position):
        # Base attributes
        self.velocity_x = 0
        self.velocity_y = 0
        self.previous_y = position[1]
        self.rect = pygame.Rect(
            position[0] + int(30*SCALE_FACTOR),
            position[1] + int(60*SCALE_FACTOR),
            80*SCALE_FACTOR,
            130*SCALE_FACTOR
        )
        # Add boundaries
        self.left_boundary = pygame.Rect(-10, 0, 10, SCREEN_HEIGHT)
        self.right_boundary = pygame.Rect(SCREEN_WIDTH - 10, 0, 10, SCREEN_HEIGHT)

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
        self.current_state = "idle"
        self.image = self.idle_images[0] if self.idle_images else pygame.Surface((100, 200))
        self.facing_right = True

        # Animation timing
        self.idle_timer = 0
        self.idle_threshold = 60
        self.current_frame = 0
        self.animation_speed = 8
        self.animation_counter = 0
        self.is_idle = False

        # Scaled physics values
        self.acceleration = 0.3 * SCALE_FACTOR
        self.max_speed = 7 * SCALE_FACTOR
        self.friction = 0.2 * SCALE_FACTOR
        self.gravity = 0.7 * SCALE_FACTOR

        # Platform collision
        self.on_ground = False
        floor_offset = int(270 * SCALE_FACTOR)
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - floor_offset + 40, SCREEN_WIDTH, int(20 * SCALE_FACTOR))
        self.ignore_platforms = []
        self.platform_touching = None

        # Jump physics
        self.base_jump_force = -18 * SCALE_FACTOR
        self.speed_jump_bonus = 0.3 * SCALE_FACTOR
        self.jump_force = self.base_jump_force
        self.jump_charging = False
        self.jump_charge = 0
        self.max_jump_charge = 20
        self.charge_bonus = 0.5 * SCALE_FACTOR

        # Sprint mechanics
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
        self.idle_images = self.load_image_set("Image/Idle/Idle", 5)
        # Load running images
        self.run_images = self.load_image_set("Image/Course/Course", 5)
        # Load jumping images
        self.jump_images = self.load_image_set("Image/Jump/Jump", 2)

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
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (80*SCALE_FACTOR, 130*SCALE_FACTOR))
                images.append(img)
            except pygame.error as e:
                print(f"Could not load image {base_path}{i}.png: {e}")
                continue
        if not images:
            fallback = pygame.Surface((80*SCALE_FACTOR, 130*SCALE_FACTOR))
            fallback.fill((255, 0, 0))
            images = [fallback]
        return images

    def update_player_image(self):
        if self.current_state == "idle":
            current_images = self.idle_images
        elif self.current_state == "running":
            current_images = self.run_images
        else:  # jumping
            current_images = self.jump_images

        if self.current_frame >= len(current_images):
            self.current_frame = 0

        current_img = current_images[self.current_frame]

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

        # Store previous position
        self.previous_y = self.rect.y

        # Determine animation state
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

        # Update facing direction
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

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.velocity_x -= self.acceleration
        elif keys[pygame.K_RIGHT]:
            self.velocity_x += self.acceleration
        else:
            # Apply friction
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

        # Reset movement timer if direction changed
        if self.direction != old_direction:
            self.movement_time = 0
            self.velocity_x *= 0.5  # Slow down when changing direction

        # Handle sprinting
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

        # Cap maximum speed
        max_current_speed = self.min_speed + (self.max_speed - self.min_speed) * (
            min(1.0, self.movement_time / self.sprint_threshold))
        self.velocity_x = max(-max_current_speed, min(max_current_speed, self.velocity_x))

        # Jumping
        if keys[pygame.K_UP]:
            if self.on_ground:
                # Immediate jump force when on the ground
                horizontal_speed = abs(self.velocity_x)
                speed_bonus = horizontal_speed * self.speed_jump_bonus
                self.velocity_y = self.base_jump_force - speed_bonus

                # Prevents a jump that's too weak
                if self.velocity_y > -10 * SCALE_FACTOR:
                    self.velocity_y = -10 * SCALE_FACTOR

                self.on_ground = False
                self.jump_charging = False
                self.jump_charge = 0
        else:
            # Reset jump variables if key is released
            self.jump_charging = False
            self.jump_charge = 0

        # Drop from platform
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

        # Check boundary collisions
        if self.rect.colliderect(self.left_boundary):
            self.rect.left = 0
            self.velocity_x = 0

        if self.rect.colliderect(self.right_boundary):
            self.rect.right = SCREEN_WIDTH
            self.velocity_x = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

        # Platform collision
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

        # Clean up ignored platforms
        if self.velocity_y >= 0:
            self.ignore_platforms = []

        # Handle floor collision
        if self.rect.colliderect(self.floor_rect):
            self.rect.bottom = self.floor_rect.top
            self.on_ground = True
            self.velocity_y = 0
            self.platform_touching = self.floor_rect
