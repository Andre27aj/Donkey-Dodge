import random
import math
from banane import Banane

class BananeManager:
    def __init__(self, scale_factor, max_bananes=2):
        self.bananes = []
        self.bananes_gauche = []
        self.bananes_droite = []
        self.scale_factor = scale_factor
        self.max_bananes_par_lanceur = max_bananes
        self.firing_cooldown = 500  # millisecondes
        self.last_left_fire_time = 0
        self.last_right_fire_time = 0
        self.score = 0
        self.bananes_a_compter = []
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

        aim_duration = min(current_time - self.left_aim_start_time, self.max_aim_time)
        aim_factor = aim_duration / self.max_aim_time  # Entre 0 et 1

        # Angle plus élevé pour trajectoire plus courbe à mesure que aim_factor augmente
        angle = self.min_angle + (self.max_angle - self.min_angle) * aim_factor
        power = self.min_power + (self.max_power - self.min_power) * aim_factor

        self.aiming_left = False
        return self._shoot_with_params(lanceur_rect, current_time, angle - 10, angle + 5, power, 1)

    def release_shot_right(self, lanceur_rect, current_time):
        """Relâcher le tir depuis la droite"""
        if self.paused or not self.aiming_right:
            return False

        aim_duration = min(current_time - self.right_aim_start_time, self.max_aim_time)
        aim_factor = aim_duration / self.max_aim_time  # Entre 0 et 1

        # Angle plus élevé pour trajectoire plus courbe à mesure que aim_factor augmente
        angle = self.min_angle + (self.max_angle - self.min_angle) * aim_factor
        power = self.min_power + (self.max_power - self.min_power) * aim_factor

        self.aiming_right = False
        return self._shoot_with_params(lanceur_rect, current_time, angle - 10, angle + 5, power, -1)

    def _shoot_with_params(self, lanceur_rect, current_time, angle_min, angle_max, power, direction):
        """Méthode interne pour tirer avec des paramètres spécifiques"""
        if self.paused:
            return False

        # Vérifier le cooldown pour chaque lanceur
        if direction == 1 and current_time - self.last_left_fire_time < self.firing_cooldown:
            return False
        if direction == -1 and current_time - self.last_right_fire_time < self.firing_cooldown:
            return False

        # Vérifier le nombre de bananes pour chaque lanceur
        if direction == 1 and len(self.bananes_gauche) >= self.max_bananes_par_lanceur :
            return False
        if direction == -1 and len(self.bananes_droite) >= self.max_bananes_par_lanceur:
            return False

        # Une seule banane par tir
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
            # Ajouter à la liste correspondante selon la direction
            if direction == 1:
                self.bananes_gauche.append(banane)
            else:
                self.bananes_droite.append(banane)

        # Mettre à jour le temps de tir
        if direction == 1:
            self.last_left_fire_time = current_time
        else:
            self.last_right_fire_time = current_time

        return True

    def shoot_from_left(self, lanceur_rect, current_time, angle_min=10, angle_max=50, variation=True):
        if self.paused:
            return False
        if not self.aiming_left:
            self.start_aiming_left(current_time)
        return False  # Ne rien faire - le tir sera déclenché au relâchement

    def shoot_from_right(self, lanceur_rect, current_time, angle_min=10, angle_max=50, variation=True):
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

            # Supprimer les bananes qui sortent de l'écran
            if banane.is_out_of_bounds(screen_height):
                if banane not in self.bananes_a_compter :
                    self.score += 1

                self.bananes.remove(banane)
                # Supprimer également des listes spécifiques
                if banane in self.bananes_gauche:
                    self.bananes_gauche.remove(banane)
                elif banane in self.bananes_droite:
                    self.bananes_droite.remove(banane)

    def check_collisions(self, joueur):
        if self.paused:
            return False

        # Si le joueur est déjà invincible, ne pas vérifier les collisions
        if joueur.invincible:
            return False

        # On vérifie d'abord s'il y a une collision
        collision_detected = False
        bananes_to_remove = []

        # Stocker toutes les bananes qui entrent en collision
        for banane in self.bananes:
            if banane.collides_with(joueur):
                collision_detected = True
                bananes_to_remove.append(banane)
                self.bananes_a_compter.append(banane)

        # Appliquer les dégâts une seule fois si collision détectée
        if collision_detected:
            # Enlever un seul coeur
            joueur.take_damage()

            # Activer immédiatement l'invincibilité
            joueur.invincible = True
            joueur.invincibility_timer = 60  # Durée d'invincibilité (60 frames ≈ 1 seconde)

            # Supprimer toutes les bananes qui ont touché le joueur
            for banane in bananes_to_remove:
                if banane in self.bananes:
                    self.bananes.remove(banane)
                    # Supprimer des listes spécifiques
                    if banane in self.bananes_gauche:
                        self.bananes_gauche.remove(banane)
                    elif banane in self.bananes_droite:
                        self.bananes_droite.remove(banane)

            return True

        return False

    def draw(self, screen):
        # Dessiner les bananes
        for banane in self.bananes:
            banane.draw(screen)

        # Dessiner les indicateurs de visée si nécessaire
        import pygame
        current_time = pygame.time.get_ticks()

        # Position Y plus basse pour les jauges de chargement
        gauge_y = 50  # Changé de 20 à 50 pour positionner plus bas

        if self.aiming_left and not self.paused:
            aim_duration = min(current_time - self.left_aim_start_time, self.max_aim_time)
            aim_percentage = aim_duration / self.max_aim_time
            power_color = (255, int(255 * (1 - aim_percentage)), 0)  # Jaune vers rouge
            pygame.draw.rect(screen, power_color,
                             (50, gauge_y, 100 * aim_percentage, 10))

        if self.aiming_right and not self.paused:
            aim_duration = min(current_time - self.right_aim_start_time, self.max_aim_time)
            aim_percentage = aim_duration / self.max_aim_time
            power_color = (255, int(255 * (1 - aim_percentage)), 0)  # Jaune vers rouge
            screen_width = pygame.display.get_surface().get_width()
            pygame.draw.rect(screen, power_color,
                             (screen_width - 150, gauge_y, 100 * aim_percentage, 10))

        # Afficher l'écran de pause si nécessaire
        if self.paused:
            self._draw_pause_screen(screen)

        # Afficher le score
        font = pygame.font.SysFont('Arial', 48)
        score_text = font.render(f"Score: {self.score}", True, (244, 210, 34))

        score_rect = score_text.get_rect()
        score_rect.centerx = screen.get_width() // 2
        score_rect.top = 20  # Distance depuis le haut de l'écran

        screen.blit(score_text, score_rect)

    def _draw_pause_screen(self, screen):
        """Dessine l'écran de pause"""
        import pygame

        # Obtenir les dimensions de l'écran
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()

        # Créer une surface semi-transparente
        pause_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 128))  # Noir semi-transparent

        # Dessiner le texte "PAUSE"
        font = pygame.font.SysFont('Arial', 48)
        pause_text = font.render("PAUSE", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))

        # Dessiner la notice "Appuyez sur ESPACE pour reprendre"
        font_small = pygame.font.SysFont('Arial', 24)
        resume_text = font_small.render("Appuyez sur ESPACE pour reprendre", True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=(screen_width // 2, screen_height // 2 + 50))

        # Appliquer à l'écran
        screen.blit(pause_surface, (0, 0))
        screen.blit(pause_text, text_rect)
        screen.blit(resume_text, resume_rect)

    def toggle_pause(self):
        """Activer ou désactiver la pause"""
        self.paused = not self.paused
        return self.paused

    def reset_launch_states(self):
        """Reset all launch-related states to their initial values"""
        self.aiming_left = False
        self.aiming_right = False
        self.left_aim_start_time = 0
        self.right_aim_start_time = 0
        self.last_left_fire_time = 0
        self.last_right_fire_time = 0
        self.bananes_gauche = []
        self.bananes_droite = []
        self.bananes_a_compter = []