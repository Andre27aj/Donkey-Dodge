# Module définissant la classe Banane utilisée dans le jeu Donkey Dodge
import pygame

class Banane:
    """Classe représentant une banane qui est lancée et peut tourner, tomber et détecter des collisions."""
    def __init__(self, pos_x, pos_y, velocity_x, velocity_y, scale_factor, image_path="Image/balle.png"):
        self.pos = [pos_x, pos_y]
        self.vel = [velocity_x, velocity_y]
        self.rotation = 0
        self.rotation_speed = 5
        self.scale_factor = scale_factor

        # Chargement et redimensionnement de l'image
        self.original_image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.original_image,
                                          (int(80 * scale_factor), int(80 * scale_factor)))
        self.rect = pygame.Rect(
            pos_x - 40 * scale_factor,
            pos_y - 40 * scale_factor,
            80 * scale_factor,
            80 * scale_factor
        )

    def update(self, dt, gravity):
        # Mise à jour des coordonnées selon la physique
        self.vel[1] += gravity * dt
        self.pos[0] += self.vel[0] * dt * 50
        self.pos[1] += self.vel[1] * dt * 50

        # Mise à jour de la rotation de l'image
        self.rotation += self.rotation_speed

        # Mise à jour de la hitbox (rectangle de collision)
        self.rect.x = self.pos[0] - 40 * self.scale_factor
        self.rect.y = self.pos[1] - 40 * self.scale_factor

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        new_rect = rotated_image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        screen.blit(rotated_image, new_rect.topleft)

    def is_out_of_bounds(self, screen_height):
        return self.pos[1] > screen_height

    def collides_with(self, player):
        return self.rect.colliderect(player.rect)
