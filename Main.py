import pygame
from jeu import main_game
from constante import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR


def main():
    # Initialiser pygame
    pygame.init()
    # Créer et lancer le jeu
    main_game()
    pygame.quit()
if __name__ == "__main__":
    main()