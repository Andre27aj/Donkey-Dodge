import pygame
from constante import SCALE_FACTOR

class Launcher:
    def __init__(self, x, y, is_left=True, scale_factor=SCALE_FACTOR):
        # Position et taille
        self.x = x
        self.y = y
        self.scale_factor = scale_factor
        self.is_left = is_left
        self.width = int(200 * scale_factor)
        self.height = int(200 * scale_factor)

        # Rectangle pour les collisions
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Chargement et mise à l'échelle de l'image
        self.orig_image = pygame.image.load("Image/lanceur.png")
        self.orig_image = pygame.transform.scale(self.orig_image, (self.width, self.height))

        # Retourner l'image si c'est le lanceur gauche
        if is_left:
            self.image = pygame.transform.flip(self.orig_image, True, False)
        else:
            self.image = self.orig_image

        # Interpolation fluide
        self.target_y = y
        self.interpolation_factor = 0.05
        self.speed = 10 * scale_factor
        self.last_fire_time = 0

    def move_up(self):
        self.y -= self.speed
        self.rect.y = self.y

    def move_down(self):
        self.y += self.speed
        self.rect.y = self.y

    def set_target_y(self, target_y):
        self.target_y = target_y

    def update(self):
        # Interpolation fluide vers la position cible
        self.y += (self.target_y - self.y) * self.interpolation_factor
        self.rect.y = self.y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def constrain_to_screen(self, min_y, max_y):
        if self.y < min_y:
            self.y = min_y
        elif self.y > max_y - self.height:
            self.y = max_y - self.height
        self.rect.y = self.y

