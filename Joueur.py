# Classe Joueur
class Joueur:
    def __init__(self, image_path, position):
        # Chargement et redimensionnement de l'image du joueur
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (88, 256))

        # Création du rectangle de collision basé sur l'image
        self.rect = self.image.get_rect(topleft=position)

        # Vitesse verticale et état de contact avec le sol
        self.velocity_y = 0
        self.on_ground = False

        # Boîte de collision du sol
        self.floor_rect = pygame.Rect(0, SCREEN_HEIGHT - 90, SCREEN_WIDTH, 20)  # Sol abaissé de 100px

    def update(self, platforms):
        # Gestion des déplacements et des actions du joueur
        keys = pygame.key.get_pressed()

        # Déplacements horizontaux
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5

        # Sauter si on est sur le sol
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -20  # Augmenter la force du saut
            self.on_ground = False

        # Appliquer la gravité
        self.velocity_y += 1  # Appliquer la gravité
        self.rect.y += self.velocity_y

        # Gestion des collisions avec les plateformes
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0 and self.rect.bottom <= platform.top:  # Si le joueur tombe et n'est pas en dessous
                    self.rect.bottom = platform.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Si le joueur saute
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

        # Gérer la collision avec le sol
        if self.rect.colliderect(self.floor_rect):
            self.rect.bottom = self.floor_rect.top
            self.on_ground = True
            self.velocity_y = 0