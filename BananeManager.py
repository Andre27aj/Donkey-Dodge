import random
import math
from Banane import Banane


class BananeManager:
    def __init__(self, scale_factor, max_bananes=2):
        self.bananes = []
        self.scale_factor = scale_factor
        self.max_bananes = max_bananes
        self.firing_cooldown = 500  # millisecondes entre chaque tir
        self.last_left_fire_time = 0
        self.last_right_fire_time = 0

        # Système de visée indépendant pour chaque côté
        self.aiming_left = False
        self.aiming_right = False
        self.left_aim_start_time = 0
        self.right_aim_start_time = 0
        self.max_aim_time = 2000  # 2 secondes pour charge complète
        self.min_angle = 10
        self.max_angle = 70
        self.min_power = 7
        self.max_power = 15

        # Facteur de réduction de la gravité pour les bananes
        self.gravity_reduction = 0.35  # Réduire davantage la gravité pour des trajectoires plus hautes

        # État de pause
        self.paused = False

    def create_banane(self, pos_x, pos_y, angle_min, angle_max, power, direction=1):
        """
        Crée une nouvelle banane avec une trajectoire plus haute et plus longue
        direction: 1 pour droite, -1 pour gauche
        """
        if len(self.bananes) >= self.max_bananes:
            return None

        # Augmenter l'angle pour une trajectoire plus haute
        angle = random.uniform(angle_min * 0.7, angle_max * 0.7)  # Augmente l'angle pour une trajectoire plus haute
        angle_rad = math.radians(angle)

        # Conserver une vitesse modérée
        speed = power * self.scale_factor * 0.7

        # Ajuster les composantes de vitesse pour une trajectoire plus haute
        vel_x = direction * (speed * math.cos(angle_rad))
        vel_y = -speed * math.sin(angle_rad) * 1  # Composante verticale à 1 pour plus de hauteur

        # Créer une banane avec une référence au facteur de gravité très réduit
        banane = Banane(pos_x, pos_y, vel_x, vel_y, self.scale_factor)
        banane.gravity_factor = self.gravity_reduction  # Réduire davantage la gravité

        return banane

    def start_aiming_left(self, current_time):
        """Commencer à viser depuis la gauche"""
        if self.paused:
            return
        self.aiming_left = True
        self.left_aim_start_time = current_time

    def start_aiming_right(self, current_time):
        """Commencer à viser depuis la droite"""
        if self.paused:
            return
        self.aiming_right = True
        self.right_aim_start_time = current_time

    def release_shot_left(self, lanceur_rect, current_time):
        """Relâcher le tir depuis la gauche"""
        if self.paused or not self.aiming_left:
            return False

        # Calculer la durée de visée pour déterminer la puissance et l'angle
        aim_duration = min(current_time - self.left_aim_start_time, self.max_aim_time)
        aim_factor = aim_duration / self.max_aim_time  # Entre 0 et 1

        # Angle plus élevé pour trajectoire plus courbe à mesure que aim_factor augmente
        angle = self.min_angle + (self.max_angle - self.min_angle) * aim_factor
        power = self.min_power + (self.max_power - self.min_power) * aim_factor

        self.aiming_left = False
        # Tirer avec des paramètres ajustés, en décalant légèrement l'angle pour plus de variation
        return self._shoot_with_params(lanceur_rect, current_time, angle - 10, angle + 5, power, 1)

    def release_shot_right(self, lanceur_rect, current_time):
        """Relâcher le tir depuis la droite"""
        if self.paused or not self.aiming_right:
            return False

        # Calculer la durée de visée pour déterminer la puissance et l'angle
        aim_duration = min(current_time - self.right_aim_start_time, self.max_aim_time)
        aim_factor = aim_duration / self.max_aim_time  # Entre 0 et 1

        # Angle plus élevé pour trajectoire plus courbe à mesure que aim_factor augmente
        angle = self.min_angle + (self.max_angle - self.min_angle) * aim_factor
        power = self.min_power + (self.max_power - self.min_power) * aim_factor

        self.aiming_right = False
        # Tirer avec des paramètres ajustés, en décalant légèrement l'angle pour plus de variation
        return self._shoot_with_params(lanceur_rect, current_time, angle - 10, angle + 5, power, -1)

    def _shoot_with_params(self, lanceur_rect, current_time, angle_min, angle_max, power, direction):
        """Méthode interne pour tirer avec des paramètres spécifiques"""
        if self.paused:
            return False

        # Vérifier le cooldown de tir selon la direction
        if current_time - self.last_left_fire_time < self.firing_cooldown and direction == 1:
            return False
        if current_time - self.last_right_fire_time < self.firing_cooldown and direction == -1:
            return False

        # Tirer plusieurs bananes (ici 2) avec une légère variation d'angle pour plus de réalisme
        num_bananas = 2
        for _ in range(num_bananas):
            if len(self.bananes) < self.max_bananes:
                angle_variation = random.uniform(-5, 5)
                banane = self.create_banane(
                    lanceur_rect.centerx,
                    lanceur_rect.bottom,
                    angle_min + angle_variation,
                    angle_max + angle_variation,
                    power,
                    direction
                )
                if banane:
                    self.bananes.append(banane)

        # Mettre à jour le temps du dernier tir selon la direction
        if direction == 1:
            self.last_left_fire_time = current_time
        else:
            self.last_right_fire_time = current_time

        return True

    def shoot_from_left(self, lanceur_rect, current_time, angle_min=10, angle_max=50, variation=True):
        # Démarrer la visée si elle n'est pas déjà active, le tir sera déclenché au relâchement
        if self.paused:
            return False
        if not self.aiming_left:
            self.start_aiming_left(current_time)
        return False  # Ne rien faire - le tir sera déclenché au relâchement

    def shoot_from_right(self, lanceur_rect, current_time, angle_min=10, angle_max=50, variation=True):
        # Démarrer la visée si elle n'est pas déjà active, le tir sera déclenché au relâchement
        if self.paused:
            return False
        if not self.aiming_right:
            self.start_aiming_right(current_time)
        return False  # Ne rien faire - le tir sera déclenché au relâchement

    def update(self, dt, gravity, screen_height):
        if self.paused:
            return

        # Mettre à jour toutes les bananes
        for banane in self.bananes[:]:
            # Appliquer une gravité réduite pour les bananes
            reduced_gravity = gravity * (
                banane.gravity_factor if hasattr(banane, 'gravity_factor') else self.gravity_reduction)
            banane.update(dt, reduced_gravity)

            # Supprimer les bananes qui sortent de l'écran (en bas)
            if banane.is_out_of_bounds(screen_height):
                self.bananes.remove(banane)

    def check_collisions(self, joueur):
        if self.paused:
            return False

        # Si le joueur est déjà invincible, ne pas vérifier les collisions pour éviter dégâts multiples
        if joueur.invincible:
            return False

        # On vérifie d'abord s'il y a une collision avec une ou plusieurs bananes
        collision_detected = False
        bananes_to_remove = []

        # Stocker toutes les bananes qui entrent en collision
        for banane in self.bananes:
            if banane.collides_with(joueur):
                collision_detected = True
                bananes_to_remove.append(banane)

        # Appliquer les dégâts une seule fois si collision détectée
        if collision_detected:
            # Enlever un seul coeur (ou vie)
            joueur.take_damage()

            # Activer immédiatement l'invincibilité pour éviter dégâts répétés
            joueur.invincible = True
            joueur.invincibility_timer = 60  # Durée d'invincibilité (60 frames ≈ 1 seconde)

            # Supprimer toutes les bananes qui ont touché le joueur
            for banane in bananes_to_remove:
                if banane in self.bananes:
                    self.bananes.remove(banane)

            return True

        return False

    def draw(self, screen):
        # Dessiner les bananes à l'écran
        for banane in self.bananes:
            banane.draw(screen)

        # Dessiner les indicateurs de visée si nécessaire
        import pygame
        current_time = pygame.time.get_ticks()

        # Position Y plus basse pour les jauges de chargement
        gauge_y = 50  # Changé de 20 à 50 pour positionner plus bas

        # Affichage de la jauge de puissance pour la visée gauche
        if self.aiming_left and not self.paused:
            aim_duration = min(current_time - self.left_aim_start_time, self.max_aim_time)
            aim_percentage = aim_duration / self.max_aim_time
            power_color = (255, int(255 * (1 - aim_percentage)), 0)  # Jaune vers rouge selon charge
            pygame.draw.rect(screen, power_color,
                             (50, gauge_y, 100 * aim_percentage, 10))

        # Affichage de la jauge de puissance pour la visée droite
        if self.aiming_right and not self.paused:
            aim_duration = min(current_time - self.right_aim_start_time, self.max_aim_time)
            aim_percentage = aim_duration / self.max_aim_time
            power_color = (255, int(255 * (1 - aim_percentage)), 0)  # Jaune vers rouge selon charge
            screen_width = pygame.display.get_surface().get_width()
            pygame.draw.rect(screen, power_color,
                             (screen_width - 150, gauge_y, 100 * aim_percentage, 10))

        # Afficher l'écran de pause si nécessaire
        if self.paused:
            self._draw_pause_screen(screen)

    def _draw_pause_screen(self, screen):
        """Dessine l'écran de pause"""
        import pygame

        # Obtenir les dimensions de l'écran
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()

        # Créer une surface semi-transparente pour assombrir l'écran
        pause_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 128))  # Noir semi-transparent

        # Dessiner le texte "PAUSE" centré à l'écran
        font = pygame.font.SysFont('Arial', 48)
        pause_text = font.render("PAUSE", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))

        # Dessiner la notice "Appuyez sur ESPACE pour reprendre" sous le texte principal
        font_small = pygame.font.SysFont('Arial', 24)
        resume_text = font_small.render("Appuyez sur ESPACE pour reprendre", True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

        # Appliquer les surfaces et textes à l'écran
        screen.blit(pause_surface, (0, 0))
        screen.blit(pause_text, text_rect)
        screen.blit(resume_text, resume_rect)

    def toggle_pause(self):
        """Activer ou désactiver la pause"""
        self.paused = not self.paused
        return self.paused