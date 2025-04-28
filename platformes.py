import pygame
from constante import SCALE_FACTOR


class Platform:
    def __init__(self, x, y, width, height, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.display_rect = self.image.get_rect(topleft=(x, y))

        # Créer un rectangle de collision (plus petit que le rectangle d'affichage)
        offset_y = 27*SCALE_FACTOR
        self.rect = pygame.Rect(x, y + offset_y, width, int(20*SCALE_FACTOR))

    def draw(self, screen):
        screen.blit(self.image, self.display_rect)
        # pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)