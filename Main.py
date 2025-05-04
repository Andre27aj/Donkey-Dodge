from menu import *

def main():
    # Initialiser pygame
    pygame.init()

    # Lancer le jeu
    menu_principal()

    # Quitter proprement pygame après la fin du jeu
    pygame.quit()


if __name__ == "__main__":
    main()