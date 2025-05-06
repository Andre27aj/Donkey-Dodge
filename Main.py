from menu import *

def run_game():
    running = True
    current_screen = None

    while running:
        # Afficher le menu principal
        from menu import menu_principal
        menu_screen = menu_principal()
        current_screen = menu_screen

        # Lancer le jeu
        from jeu import main_game
        result = main_game(current_screen)

        # Traiter le résultat
        if result == "menu":
            # On continue la boucle pour revenir au menu
            continue
        elif result == "quit":
            running = False


# Appel de la fonction principale
if __name__ == "__main__":
    run_game()