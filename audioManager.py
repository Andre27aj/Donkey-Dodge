import pygame
import os


class AudioManager:
    """Gère tous les sons du jeu, y compris la musique et les effets sonores"""

    def __init__(self):
        # Initialise le mixer de pygame
        pygame.mixer.init()
        # Dictionnaire pour stocker les effets sonores
        self.sound_effects = {}
        # Volumes par défaut
        self.music_volume = 0.5
        self.effects_volume = 0.7

    def load_music(self, path):
        """
        Charge la musique de fond

        Arguments :
            path (str) : Chemin vers le fichier musical
        """
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
        else:
            print(f"Warning: Music file not found at {path}")

    def play_music(self, loop=-1):
        """
        Joue la musique actuellement chargée

        Arguments :
            loop (int) : Nombre de répétitions (-1 pour infini)
        """
        pygame.mixer.music.play(loop)

    def stop_music(self):
        """Arrête la musique en cours de lecture"""
        pygame.mixer.music.stop()

    def pause_music(self):
        """Met en pause la musique en cours"""
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Reprend la musique mise en pause"""
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        """
        Définit le volume de la musique

        Arguments :
            volume (float) : Niveau de volume (de 0.0 à 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def load_sound(self, name, path):
        """
        Charge un effet sonore et l'associe à un nom

        Arguments :
            name (str) : Nom de référence pour ce son
            path (str) : Chemin vers le fichier sonore
        """
        if os.path.exists(path):
            self.sound_effects[name] = pygame.mixer.Sound(path)
            self.sound_effects[name].set_volume(self.effects_volume)
        else:
            print(f"Warning: Sound effect not found at {path}")

    def play_sound(self, name):
        """
        Joue un effet sonore chargé

        Arguments :
            name (str) : Nom de l'effet sonore à jouer
        """
        if name in self.sound_effects:
            self.sound_effects[name].play()
        else:
            print(f"Warning: Sound effect '{name}' not loaded")

    def set_effects_volume(self, volume):
        """
        Définit le volume pour tous les effets sonores

        Arguments :
            volume (float) : Niveau de volume (de 0.0 à 1.0)
        """
        self.effects_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(self.effects_volume)