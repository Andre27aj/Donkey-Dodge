import pygame
pygame.init()

class Joueur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.lifePoints = 3
        self.maxLifePoints = 3
        self.speed = 5
        self.image = pygame.image.load('Perso1.png')
        self.image.get_rect( )