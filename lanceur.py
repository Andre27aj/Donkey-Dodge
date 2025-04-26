import pygame
import random
import numpy as np
from constante import SCREEN_WIDTH,SCALE_FACTOR,GRAVITY,DT


class Launcher:
    def __init__(self, x, y, is_left=True):
        self.rect = pygame.Rect(x, y, 200, 200)
        self.is_left = is_left
        self.last_fire_time = 0

        # Load image
        self.orig_image = pygame.image.load("Image/lanceur.png")
        self.orig_image = pygame.transform.scale(self.orig_image, (200, 200))

        # Flip image if it's the left launcher
        if is_left:
            self.image = pygame.transform.flip(self.orig_image, True, False)
        else:
            self.image = self.orig_image


def creer_balle(x0, y0, angle_min=10, angle_max=50):
    vitesse_min, vitesse_max = 5, 20
    v0 = random.uniform(vitesse_min, vitesse_max)
    angle = random.uniform(angle_min, angle_max)
    angle_rad = np.radians(angle)

    # Calculate velocities
    vx = v0 * np.cos(angle_rad)
    vy = -v0 * np.sin(angle_rad)

    return {
        "pos": [x0, y0],
        "vel": [vx, vy],
        "start_time": pygame.time.get_ticks(),
        "rotation": 0
    }


def update_balle(bananas):
    for banana in bananas:
        banana["vel"][1] += GRAVITY * DT
        banana["pos"][0] += banana["vel"][0] * DT * 50
        banana["pos"][1] += banana["vel"][1] * DT * 50
        banana["rotation"] += 5

    # Remove bananas that are off-screen
    return [b for b in bananas if b["pos"][1] <= pygame.display.get_surface().get_height()]