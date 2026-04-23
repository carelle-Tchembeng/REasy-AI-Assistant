import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.prompts import SYSTEM_PROMPT
from llm.prompt_builder import construire_prompt_resume
from llm.llm_client import demander_mistral
from utils.formatter import formater_montant, formater_nom_champ


def generer_resume(operation) -> dict:
    """
    Point d'entrée principal.
    Génère un résumé complet en deux temps :
    1. Résumé de base (formatage pur, sans LLM)
    2. Résumé enrichi par Mistral (optionnel, mode dégradé si indisponible)

    Retourne un dictionnaire structuré :
    {
        "resume_base"   : texte structuré sans LLM,
        "resume_llm"    : texte rédigé par Mistral (ou None),
        "mode_degrade"  : True si Mistral était indisponible
    }
    """
    # Temps 1 — résumé de base sans LLM
    resume_base = _generer_resume_base(operation)

    # Temps 2 — résumé enrichi par Mistral
    resume_llm  = None
    mode_degrade = False

    prompt = construire_prompt_resume(operation)
    ok, reponse = demander_mistral(prompt, system_prompt=SYSTEM_PROMPT)
    prompt = construire_prompt_resume(operation)

    #print("=== DEBUG STREAMLIT ===")
    #print("Prompt envoyé :", prompt)

    #ok, reponse = demander_mistral(prompt, system_prompt=SYSTEM_PROMPT)

    #print("Résultat LLM :", ok, str(reponse))

    if ok:
        resume_llm = reponse
    else:
        mode_degrade = True

    return {
        "resume_base"  : resume_base,
        "resume_llm"   : resume_llm,
        "mode_degrade" : mode_degrade,
    }


def _generer_resume_base(operation) -> str:
    """
    Génère un résumé structuré sans LLM à partir des données du PaymentOperation.
    Utilisé comme filet de sécurité si Mistral est indisponible.
    """
    lignes = []

    lignes.append("=" * 50)
    lignes.append("  RÉSUMÉ DE L'OPÉRATION DE PAIEMENT INTERNATIONAL")
    lignes.append("=" * 50)

    # Section 1 — Identification
    lignes.append("\n1. IDENTIFICATION DE L'OPÉRATION")
    lignes.append("-" * 35)
    lignes.append(f"  • {formater_nom_champ('nom_entreprise')}   : {operation.nom_entreprise or 'N/A'}")
    lignes.append(f"  • {formater_nom_champ('pays_acheteur')}    : {operation.pays_acheteur or 'N/A'}")
    lignes.append(f"  • {formater_nom_champ('nom_fournisseur')}  : {operation.nom_fournisseur or 'N/A'}")
    lignes.append(f"  • {formater_nom_champ('pays_fournisseur')} : {operation.pays_fournisseur or 'N/A'}")

    # Section 2 — Détails financiers
    lignes.append("\n2. DÉTAILS FINANCIERS")
    lignes.append("-" * 35)
    montant_formate = formater_montant(operation.montant, operation.devise or "")
    lignes.append(f"  • Montant          : {montant_formate}")
    lignes.append(f"  • Mode de paiement : {operation.mode_paiement or 'N/A'}")

    # Section 3 — Marchandise
    lignes.append("\n3. NATURE DE LA MARCHANDISE")
    lignes.append("-" * 35)
    lignes.append(f"  • Type        : {operation.type_marchandise or 'N/A'}")
    lignes.append(f"  • Description : {operation.description_marchandise or 'N/A'}")

    # Section 4 — Coordonnées bancaires
    lignes.append("\n4. COORDONNÉES BANCAIRES DU FOURNISSEUR")
    lignes.append("-" * 35)
    lignes.append(f"  • Banque       : {operation.banque_fournisseur or 'N/A'}")
    lignes.append(f"  • SWIFT / BIC  : {operation.swift_bic or 'N/A'}")
    lignes.append(f"  • IBAN / Compte: {operation.iban_fournisseur or 'N/A'}")

    # Section 5 — Métadonnées
    lignes.append("\n5. INFORMATIONS DE SESSION")
    lignes.append("-" * 35)
    lignes.append(f"  • Date de l'opération : {operation.date_creation}")

    lignes.append("\n" + "=" * 50)

    return "\n".join(lignes)

