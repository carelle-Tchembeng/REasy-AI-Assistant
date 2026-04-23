import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import COUNTRY_RULES_FILE
from config.prompts import SYSTEM_PROMPT
from llm.prompt_builder import construire_prompt_checklist
from llm.llm_client import demander_mistral


def generer_checklist(operation) -> dict:
    """
    Point d'entrée principal.
    Génère une checklist complète en deux temps :
    1. Checklist de base (logique pure, sans LLM)
    2. Enrichissement par Mistral (optionnel, mode dégradé si indisponible)

    Retourne un dictionnaire structuré :
    {
        "documents"       : liste des documents,
        "enrichissement"  : texte enrichi par Mistral (ou None),
        "pays"            : pays du fournisseur,
        "mode_degrade"    : True si Mistral était indisponible
    }
    """
    # Temps 1 — checklist de base sans LLM
    documents = _generer_checklist_base(operation)

    # Temps 2 — enrichissement par Mistral
    enrichissement = None
    mode_degrade = False

    prompt = construire_prompt_checklist(operation, documents)
    ok, reponse = demander_mistral(prompt, system_prompt=SYSTEM_PROMPT)

    if ok:
        enrichissement = reponse
    else:
        mode_degrade = True

    return {
        "documents"     : documents,
        "enrichissement": enrichissement,
        "pays"          : operation.pays_fournisseur,
        "mode_degrade"  : mode_degrade,
    }


def _generer_checklist_base(operation) -> list:
    """
    Génère la checklist de base sans LLM.
    Combine les documents communs à tous les pays avec
    les documents spécifiques au pays du fournisseur.
    """
    with open(COUNTRY_RULES_FILE, encoding="utf-8") as f:
        regles = json.load(f)

    documents = []

    # Documents de base — communs à tout paiement international
    docs_base = regles.get("_documents_base", {}).get("documents", [])
    for doc in docs_base:
        documents.append({
            "nom"        : doc["nom"],
            "description": doc.get("description", ""),
            "obligatoire": doc.get("obligatoire", True),
            "source"     : "base",
        })

    # Documents spécifiques au pays du fournisseur
    pays = operation.pays_fournisseur
    if pays and pays in regles:
        regle_pays = regles[pays]
        for doc in regle_pays.get("documents_specifiques", []):
            documents.append({
                "nom"        : doc["nom"],
                "description": doc.get("description", ""),
                "obligatoire": doc.get("obligatoire", False),
                "source"     : f"specifique_{pays}",
            })
    elif pays:
        # Pays non répertorié — on utilise les règles "Autre"
        for doc in regles.get("Autre", {}).get("documents_specifiques", []):
            documents.append({
                "nom"        : doc["nom"],
                "description": doc.get("description", ""),
                "obligatoire": doc.get("obligatoire", False),
                "source"     : "specifique_autre",
            })

    return documents


def get_infos_pays(pays: str) -> dict:
    """
    Retourne les informations contextuelles d'un pays :
    devise habituelle, délai virement moyen, remarque réglementaire.
    """
    with open(COUNTRY_RULES_FILE, encoding="utf-8") as f:
        regles = json.load(f)

    if pays in regles:
        regle = regles[pays]
        return {
            "devise_habituelle"    : regle.get("devise_habituelle", "N/A"),
            "delai_virement_moyen" : regle.get("delai_virement_moyen", "N/A"),
            "remarque"             : regle.get("remarque", ""),
        }
    return {
        "devise_habituelle"    : "N/A",
        "delai_virement_moyen" : "N/A",
        "remarque"             : "Pays non répertorié. Consultez votre banque.",
    }