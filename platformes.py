import pygame
from constante import SCALE_FACTOR


class Platform:
    def __init__(self, x, y, width, height, image_path):
        # Chargement de l'image de la plateforme depuis le chemin fourni
        self.image = pygame.image.load(image_path)
        # Redimensionnement de l'image selon les dimensions spécifiées
        self.image = pygame.transform.scale(self.image, (width, height))
        # Création du rectangle d'affichage à la position (x, y)
        self.display_rect = self.image.get_rect(topleft=(x, y))

        # Création d'un rectangle de collision plus petit pour mieux coller à la plateforme réelle
        # Décalage vertical pour ajuster la position du rectangle de collision
        offset_y = 27*SCALE_FACTOR
        # Définition du rectangle de collision avec les dimensions réduites
        self.rect = pygame.Rect(x, y + offset_y, width, int(20*SCALE_FACTOR))

    # Méthode pour dessiner la plateforme à l'écran
    def draw(self, screen):
        screen.blit(self.image, self.display_rect)
        # Décommenter pour visualiser le rectangle de collision (utile pour le debug)
        ## pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)