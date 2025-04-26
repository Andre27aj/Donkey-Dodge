import pygame

pygame.init()
# Get screen resolution
info = pygame.display.Info()
SCREEN_WIDTH = int(info.current_w * 0.9)
SCREEN_HEIGHT = int(info.current_h * 0.9)

# Calculate scale factors
REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080
SCALE_X = SCREEN_WIDTH / REFERENCE_WIDTH
SCALE_Y = SCREEN_HEIGHT / REFERENCE_HEIGHT
SCALE_FACTOR = min(SCALE_X, SCALE_Y)

# Game settings
MAX_BANANAS = 4
FIRING_COOLDOWN = 500
LAUNCHER_SPEED = 10
GRAVITY = 9.81
DT = 0.05