import pygame
pygame.init()

class Joueur(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.lifePoints = 3
        self.maxLifePoints = 3
        self.speed = 5
        self.image = pygame.image.load('Perso1.png')
        self.rect = self.image.get_rect()
        self.isJumping = False
        self.jumpSpeed = 10
        self.gravity = 0.5
        self.velocityY = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if not self.isJumping:
            if keys[pygame.K_SPACE]:
                self.isJumping = True
                self.velocityY = -self.jumpSpeed
        else:
            self.velocityY += self.gravity
            self.rect.y += self.velocityY
            if self.rect.y >= 300:  # Assuming 300 is the ground level
                self.rect.y = 300
                self.isJumping = False
                self.velocityY = 0