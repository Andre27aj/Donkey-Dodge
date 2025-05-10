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
        # Mute state
        self.muted = False
        # Store original volumes for unmuting
        self.original_music_volume = self.music_volume
        self.original_effects_volume = self.effects_volume

    def toggle_mute(self):
        """Toggle mute/unmute for all audio"""
        if self.muted:
            # Unmute - restore previous volumes
            self.set_music_volume(self.original_music_volume)
            self.set_effects_volume(self.original_effects_volume)
            self.muted = False
        else:
            # Mute - save current volumes and set to 0
            self.original_music_volume = self.music_volume
            self.original_effects_volume = self.effects_volume
            self.set_music_volume(0)
            self.set_effects_volume(0)
            self.muted = True
        return self.muted

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

class SoundButton:
    def __init__(self, x, y, size, audio_manager):
        self.x = x
        self.y = y
        self.size = size
        self.audio_manager = audio_manager

        # Load sound on/off icons
        try:
            self.sound_on_img = pygame.image.load('Image/soundOn.png')
            self.sound_off_img = pygame.image.load('Image/soundOff.png')

            # Scale images to requested size
            self.sound_on_img = pygame.transform.scale(self.sound_on_img, (size, size))
            self.sound_off_img = pygame.transform.scale(self.sound_off_img, (size, size))
        except pygame.error:
            # Fallback to text if images aren't found
            self.sound_on_img = None
            self.sound_off_img = None
            self.font = pygame.font.SysFont('Arial', size)
            self.sound_on_text = self.font.render("🔊", True, (255, 255, 255))
            self.sound_off_text = self.font.render("🔇", True, (255, 255, 255))

        # Create rect for collision detection
        self.rect = pygame.Rect(x, y, size, size)

    def draw(self, screen):
        if self.audio_manager.muted:
            if self.sound_off_img:
                screen.blit(self.sound_off_img, (self.x, self.y))
            else:
                screen.blit(self.sound_off_text, (self.x, self.y))
        else:
            if self.sound_on_img:
                screen.blit(self.sound_on_img, (self.x, self.y))
            else:
                screen.blit(self.sound_on_text, (self.x, self.y))

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.audio_manager.toggle_mute()
            return True
        return False