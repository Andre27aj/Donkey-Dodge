import pygame

class Banane:
    def __init__(self, pos_x, pos_y, velocity_x, velocity_y, scale_factor, image_path="Image/balle.png"):
        self.pos = [pos_x, pos_y]
        self.vel = [velocity_x, velocity_y]
        # Initialisation de l'angle de rotation
        self.rotation = 0
        # Vitesse de rotation de la banane
        self.rotation_speed = 5
        self.scale_factor = scale_factor

        # Chargement de l'image d'origine de la banane
        self.original_image = pygame.image.load(image_path)
        # Redimensionnement de l'image selon le facteur d'échelle
        self.image = pygame.transform.scale(self.original_image,
                                          (int(80 * scale_factor), int(80 * scale_factor)))
        # Définition du rectangle de collision autour de la banane
        self.rect = pygame.Rect(
            pos_x - 40 * scale_factor,
            pos_y - 40 * scale_factor,
            80 * scale_factor,
            80 * scale_factor
        )

    def update(self, dt, gravity):
        # Mise à jour de la vélocité verticale avec la gravité
        self.vel[1] += gravity * dt
        # Mise à jour de la position selon la vitesse et le temps écoulé
        self.pos[0] += self.vel[0] * dt * 50
        self.pos[1] += self.vel[1] * dt * 50

        # Mise à jour de la rotation
        self.rotation += self.rotation_speed

        # Mise à jour de la position du rectangle de collision
        self.rect.x = self.pos[0] - 40 * self.scale_factor
        self.rect.y = self.pos[1] - 40 * self.scale_factor

    def draw(self, screen):
        # Rotation de l'image pour l'affichage
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        # Récupération du nouveau rectangle centré pour l'affichage
        new_rect = rotated_image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        # Affichage de l'image pivotée sur l'écran
        screen.blit(rotated_image, new_rect.topleft)

    def is_out_of_bounds(self, screen_height):
        # Vérifie si la banane est sortie de l'écran (en bas)
        return self.pos[1] > screen_height

    def collides_with(self, player):
        # Vérifie la collision entre la banane et le joueur
        return self.rect.colliderect(player.rect)