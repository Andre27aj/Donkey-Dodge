import pygame
from jeu import main_game
from constante import SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR


def main():
    # Initialize pygame
    pygame.init()

    # Set up the display

    # Create and run the game
    main_game()


    pygame.quit()


if __name__ == "__main__":
    main()