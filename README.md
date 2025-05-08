# Donkey Dodge

HEBRAUT Clément & HADJ ISA Adam & MARTINS-SILVA Lisa & ALBUQUERQUE JOAQUIM André & DELPORTE Roman

Donkey Dodge est un jeu de plateforme développé en Python avec Pygame. Le joueur incarne un personnage qui doit éviter des bananes qu'il contrôle tombant de singes en sautant de plateforme en plateforme. L'objectif est de survivre le plus longtemps possible sans perdre toutes ses vies (3) .

## Principe du jeu

Le joueur contrôle un personnage qui peut se déplacer et sauter entre différentes plateformes. Des bananes tombent depuis les singes des deux côtés de l’écran et doivent être évitées. Si le personnage touche une banane, il perd une vie. Le jeu se termine lorsque toutes les vies sont perdues. Un écran "Game Over" propose alors de rejouer ou de quitter.


## Pour lancer le jeu


1. **Assurez-vous d’avoir Python installé**  
   Téléchargez et installez Python si ce n’est pas déjà fait.

2. **Installez les dépendances nécessaires (pygame)**  
   Ouvrez un terminal ou une invite de commande et exécutez :
      pip install pygame

3. **Placez-vous dans le dossier du projet**  
    Utilisez la commande cd pour vous placer dans le bon dossier.
   
4. **Lancez le jeu**  
    Exécutez le fichier main.py avec python.

## Fichiers du projet

### `main.py`
Lance le jeu et gère la boucle principale. Il initialise les objets du jeu, traite les événements clavier, met à jour l'affichage et vérifie les collisions grâce aux autres fichiers du projet.

### `lanceur.py`
Fichier d'entrée du programme. Il affiche un menu de démarrage et lance la partie en appelant `main.py`.

### `menu.py`
Affiche un menu avec les options "Jouer" et "Quitter", utilisant des boutons interactifs avec effets visuels au survol.

### `platformes.py`
Contient la classe 'Platform'. Gère l'affichage et la collision des plateformes sur lesquelles le joueur peut marcher ou sauter.

### `banane.py`
Définit la classe `Banane`. Chaque banane tombe verticalement et peut entrer en collision avec le joueur.

### `banane_manager.py`
Crée et met à jour les bananes au fil du jeu. Gère leur apparition, leur mouvement et leur suppression lorsqu'elles sortent de l'écran.

### `fonc.py`
Fonctions annexes pour l'affichage de l'interface.

### `constante.py`
Fichier de configuration qui contient les constantes importantes du projet.

### `jeu.py`
Fichier qui contient le jeu principal pygame, appelé par le main.

### `joueur.py`
Contient la classe 'joueur', il gère les mouvements et les autres caractéristiques du personnage.


