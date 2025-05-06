import csv
import os
from datetime import datetime


class ScoreManager:
    def __init__(self, fichier='scores.csv'):
        self.fichier = fichier
        self._verifier_fichier()

    def _verifier_fichier(self):
        """Vérifie si le fichier existe, sinon le crée avec les en-têtes"""
        if not os.path.exists(self.fichier):
            with open(self.fichier, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Pseudo', 'Score'])

    def enregistrer_score(self, score):
        """Enregistre un nouveau score dans le fichier CSV"""
        date_actuelle = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.fichier, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([date_actuelle, score])

    def obtenir_meilleurs_scores(self, nombre=10):
        """Récupère les meilleurs scores triés"""
        scores = []
        try:
            with open(self.fichier, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Sauter l'en-tête
                for row in reader:
                    try:
                        date, score = row
                        scores.append((date, int(score)))
                    except (ValueError, IndexError):
                        continue
        except FileNotFoundError:
            return []

        # Trier par score, du plus grand au plus petit
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:nombre]