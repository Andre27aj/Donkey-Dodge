import pygame

pygame.init()
# Obtenir la résolution de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.9)
SCREEN_HEIGHT = int(info.current_h * 0.9)

# Calculer les facteurs d'échelle
REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080
SCALE_X = SCREEN_WIDTH / REFERENCE_WIDTH
SCALE_Y = SCREEN_HEIGHT / REFERENCE_HEIGHT
SCALE_FACTOR = min(SCALE_X, SCALE_Y)

# Paramètres du jeu
MAX_BANANAS = 6
FIRING_COOLDOWN = 500
LAUNCHER_SPEED = 10
GRAVITY = 9.81
DT = 0.05