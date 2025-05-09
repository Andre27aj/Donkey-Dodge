import pygame
import os


class AudioManager:
    """Manages all audio for the game including music and sound effects"""

    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        # Dictionary to store sound effects
        self.sound_effects = {}
        # Default volumes
        self.music_volume = 0.5
        self.effects_volume = 0.7

    def load_music(self, path):
        """
        Load background music

        Args:
            path (str): Path to the music file
        """
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
        else:
            print(f"Warning: Music file not found at {path}")

    def play_music(self, loop=-1):
        """
        Play the currently loaded music

        Args:
            loop (int): Number of times to loop (-1 for infinite)
        """
        pygame.mixer.music.play(loop)

    def stop_music(self):
        """Stop the currently playing music"""
        pygame.mixer.music.stop()

    def pause_music(self):
        """Pause the currently playing music"""
        pygame.mixer.music.pause()

    def unpause_music(self):
        """Resume the paused music"""
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        """
        Set music volume

        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def load_sound(self, name, path):
        """
        Load a sound effect and store with a name

        Args:
            name (str): Name to reference this sound
            path (str): Path to the sound file
        """
        if os.path.exists(path):
            self.sound_effects[name] = pygame.mixer.Sound(path)
            self.sound_effects[name].set_volume(self.effects_volume)
        else:
            print(f"Warning: Sound effect not found at {path}")

    def play_sound(self, name):
        """
        Play a loaded sound effect

        Args:
            name (str): Name of the sound effect to play
        """
        if name in self.sound_effects:
            self.sound_effects[name].play()
        else:
            print(f"Warning: Sound effect '{name}' not loaded")

    def set_effects_volume(self, volume):
        """
        Set volume for all sound effects

        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.effects_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(self.effects_volume)