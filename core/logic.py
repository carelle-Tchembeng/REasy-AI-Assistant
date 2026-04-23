import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import QUESTIONS_FILE
from models.payment_model import PaymentOperation


class ConversationManager:
    """
    Gère le flux de conversation question par question.
    Charge les questions depuis questions.json, enregistre les réponses
    dans le PaymentOperation et détecte la fin du questionnaire.
    """

    def __init__(self, operation: PaymentOperation):
        self.operation = operation
        self.questions = self._charger_questions()
        self.index_courant = 0

    # Chargement

    def _charger_questions(self) -> list:
        """Charge et retourne la liste des questions depuis le fichier JSON."""
        with open(QUESTIONS_FILE, encoding="utf-8") as f:
            questions = json.load(f)
        return sorted(questions, key=lambda q: q["ordre"])

    # Navigation

    def get_question_courante(self) -> dict | None:
        """Retourne la question courante, ou None si toutes les questions sont posées."""
        if self.index_courant < len(self.questions):
            return self.questions[self.index_courant]
        return None

    def get_progression(self) -> dict:
        """Retourne la progression actuelle : étape courante et total."""
        return {
            "etape_courante" : self.index_courant + 1,
            "total"          : len(self.questions),
            "pourcentage"    : round((self.index_courant / len(self.questions)) * 100)
        }

    def is_complete(self) -> bool:
        """Retourne True si toutes les questions ont été posées."""
        return self.index_courant >= len(self.questions)

    
    # Enregistrement des réponses
    

    def enregistrer_reponse(self, reponse: str) -> bool:
        """
        Enregistre la réponse de l'utilisateur dans le PaymentOperation
        et avance à la question suivante.
        Retourne True si l'enregistrement a réussi, False sinon.
        """
        question = self.get_question_courante()
        if question is None:
            return False

        champ = question["champ_modele"]
        valeur = self._convertir_reponse(reponse, question["type"])

        if hasattr(self.operation, champ):
            setattr(self.operation, champ, valeur)
            self.index_courant += 1
            self.operation.etape_courante = self.index_courant

            if self.is_complete():
                self.operation.est_complete = True
            return True

        return False

    def _convertir_reponse(self, reponse: str, type_question: str):
        """Convertit la réponse brute dans le bon type Python selon le type de question."""
        reponse = reponse.strip()
        if type_question == "nombre":
            try:
                return float(reponse.replace(",", ".").replace(" ", ""))
            except ValueError:
                return None
        return reponse if reponse else None

    
    # Réinitialisation


    def reinitialiser(self):
        """Remet le gestionnaire à zéro pour une nouvelle conversation."""
        self.operation = PaymentOperation()
        self.index_courant = 0