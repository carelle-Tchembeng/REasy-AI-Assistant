import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.prompts import SUMMARY_PROMPT_TEMPLATE, CHECKLIST_PROMPT_TEMPLATE
from utils.formatter import formater_operation_pour_llm


def construire_prompt_resume(operation) -> str:
    """
    Construit le prompt complet pour la génération du résumé.
    Injecte les données formatées de l'opération dans SUMMARY_PROMPT_TEMPLATE.
    """
    donnees_formatees = formater_operation_pour_llm(operation)
    return SUMMARY_PROMPT_TEMPLATE.format(donnees_operation=donnees_formatees)


def construire_prompt_checklist(operation, checklist_base: list) -> str:
    """
    Construit le prompt complet pour l'enrichissement de la checklist.
    Injecte les données de l'opération ET la checklist de base
    dans CHECKLIST_PROMPT_TEMPLATE.
    """
    donnees_formatees = formater_operation_pour_llm(operation)
    checklist_formatee = _formater_checklist_pour_prompt(checklist_base)

    return CHECKLIST_PROMPT_TEMPLATE.format(
        donnees_operation=donnees_formatees,
        checklist_base=checklist_formatee
    )


def _formater_checklist_pour_prompt(documents: list) -> str:
    """
    Formate la liste de documents en texte simple pour injection dans le prompt.
    Format volontairement sobre pour ne pas perturber la lecture par Mistral.
    Ex : '- Facture commerciale (obligatoire)\n- Certificat d'origine (obligatoire)'
    """
    if not documents:
        return "Aucun document identifié pour l'instant."

    lignes = []
    for doc in documents:
        mention = "obligatoire" if doc.get("obligatoire") else "recommandé"
        lignes.append(f"- {doc['nom']} ({mention})")
        if doc.get("description"):
            lignes.append(f"  → {doc['description']}")

    return "\n".join(lignes)