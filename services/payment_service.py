import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.payment_model import PaymentOperation
from core.logic import ConversationManager
from core.checklist_generator import generer_checklist, get_infos_pays
from core.summary_generator import generer_resume
from utils.validators import valider_reponse


class PaymentResult:
    """
    Objet retourné par PaymentService à la fin d'une simulation complète.
    Contient toutes les données nécessaires à l'affichage final.
    """

    def __init__(self, operation, resume, checklist):
        self.operation   = operation
        self.resume      = resume       # dict : {resume_base, resume_llm, mode_degrade}
        self.checklist   = checklist    # dict : {documents, enrichissement, pays, mode_degrade}

    @property
    def resume_final(self) -> str:
        """Retourne le meilleur résumé disponible : LLM si dispo, base sinon."""
        return self.resume.get("resume_llm") or self.resume.get("resume_base", "")

    @property
    def documents(self) -> list:
        """Retourne la liste des documents de la checklist."""
        return self.checklist.get("documents", [])

    @property
    def enrichissement_checklist(self) -> str | None:
        """Retourne l'enrichissement LLM de la checklist si disponible."""
        return self.checklist.get("enrichissement")

    @property
    def mode_degrade(self) -> bool:
        """True si au moins un des deux générateurs est en mode dégradé."""
        return self.resume.get("mode_degrade", False) or \
               self.checklist.get("mode_degrade", False)

    def __str__(self) -> str:
        return (
            f"PaymentResult("
            f"operation={self.operation.nom_entreprise}, "
            f"documents={len(self.documents)}, "
            f"mode_degrade={self.mode_degrade})"
        )


class PaymentService:
    """
    Chef d'orchestre de l'application.
    Coordonne le flux de conversation, la validation,
    et la génération des outputs.
    """

    def __init__(self):
        self.operation = PaymentOperation()
        self.manager   = ConversationManager(self.operation)

    # --------------------------------------------------------
    # Gestion du flux de conversation
    # --------------------------------------------------------

    def get_question_courante(self) -> dict | None:
        """Retourne la question courante à poser à l'utilisateur."""
        return self.manager.get_question_courante()

    def get_progression(self) -> dict:
        """Retourne la progression actuelle du questionnaire."""
        return self.manager.get_progression()

    def is_complete(self) -> bool:
        """Retourne True si toutes les questions ont été répondues."""
        return self.manager.is_complete()

    # --------------------------------------------------------
    # Traitement d'une réponse utilisateur
    # --------------------------------------------------------

    def traiter_reponse(self, reponse: str) -> dict:
        """
        Valide et enregistre la réponse de l'utilisateur.
        Retourne un dict :
        {
            "succes"  : bool,
            "erreur"  : str (vide si succes),
            "complete": bool (True si toutes les questions sont répondues)
        }
        """
        question = self.manager.get_question_courante()
        if question is None:
            return {"succes": False, "erreur": "Aucune question en cours.", "complete": True}

        # Validation
        est_valide, message_erreur = valider_reponse(reponse, question)
        if not est_valide:
            return {"succes": False, "erreur": message_erreur, "complete": False}

        # Enregistrement
        self.manager.enregistrer_reponse(reponse)

        return {
            "succes"  : True,
            "erreur"  : "",
            "complete": self.manager.is_complete()
        }

    # --------------------------------------------------------
    # Génération du résultat final
    # --------------------------------------------------------

    def generer_resultat(self) -> PaymentResult | None:
        """
        Génère le résultat final une fois le questionnaire terminé.
        Retourne un PaymentResult ou None si l'opération n'est pas prête.
        """
        if not self.operation.est_pret_pour_generation():
            return None

        resume    = generer_resume(self.operation)
        checklist = generer_checklist(self.operation)

        result = PaymentResult(self.operation, resume, checklist)

        # Sauvegarde automatique — import local pour eviter
        # les faux avertissements de VS Code sur sys.path
        try:
            from utils.simulation_store import sauvegarder_simulation
            sauvegarder_simulation(result)
        except Exception:
            pass  # La sauvegarde ne doit jamais bloquer l'application

        return result

    # --------------------------------------------------------
    # Informations contextuelles
    # --------------------------------------------------------

    def get_infos_pays(self) -> dict:
        """
        Retourne les infos contextuelles du pays fournisseur
        (délai, devise habituelle, remarque réglementaire).
        """
        pays = self.operation.pays_fournisseur
        if not pays:
            return {}
        return get_infos_pays(pays)

    # --------------------------------------------------------
    # Réinitialisation
    # --------------------------------------------------------

    def reinitialiser(self):
        """Remet le service à zéro pour une nouvelle simulation."""
        self.operation = PaymentOperation()
        self.manager   = ConversationManager(self.operation)


    # --------------------------------------------------------
    # Export PDF
    # --------------------------------------------------------

    def exporter_pdf(self, payment_result) -> bytes | None:
        """
        Génère et retourne les bytes du PDF d'un PaymentResult.
        Retourne None si la génération échoue.
        """
        try:
            from utils.pdf_exporter import generer_pdf
            return generer_pdf(payment_result)
        except Exception as e:
            print(f"Erreur export PDF : {e}")
            return None

    # --------------------------------------------------------
    # Sauvegarde des simulations
    # --------------------------------------------------------

    def sauvegarder(self, payment_result) -> str | None:
        """
        Sauvegarde le PaymentResult dans le fichier de simulations.
        Retourne l'id de la simulation ou None si échec.
        """
        try:
            from utils.simulation_store import sauvegarder_simulation
            return sauvegarder_simulation(payment_result)
        except Exception as e:
            print(f"Erreur sauvegarde : {e}")
            return None