import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import OUTPUTS_DIR

FICHIER_SIMULATIONS = os.path.join(OUTPUTS_DIR, "simulations.json")


def sauvegarder_simulation(resultat) -> dict:
    """
    Sauvegarde une simulation terminee dans simulations.json.
    Retourne l'entree sauvegardee.
    """
    simulations = charger_simulations()

    entree = _construire_entree(resultat)
    simulations.append(entree)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(FICHIER_SIMULATIONS, "w", encoding="utf-8") as f:
        json.dump(simulations, f, ensure_ascii=False, indent=2)

    return entree


def charger_simulations() -> list:
    """
    Charge et retourne toutes les simulations sauvegardees.
    Retourne une liste vide si le fichier n'existe pas encore.
    """
    if not os.path.exists(FICHIER_SIMULATIONS):
        return []
    try:
        with open(FICHIER_SIMULATIONS, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def supprimer_simulation(sim_id: str) -> bool:
    """
    Supprime une simulation par son id.
    Retourne True si supprimee, False si introuvable.
    """
    simulations = charger_simulations()
    nouvelles   = [s for s in simulations if s.get("id") != sim_id]

    if len(nouvelles) == len(simulations):
        return False

    with open(FICHIER_SIMULATIONS, "w", encoding="utf-8") as f:
        json.dump(nouvelles, f, ensure_ascii=False, indent=2)
    return True


def effacer_historique() -> int:
    """
    Supprime toutes les simulations sauvegardees.
    Retourne le nombre de simulations supprimees.
    """
    simulations = charger_simulations()
    nb = len(simulations)

    with open(FICHIER_SIMULATIONS, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    return nb


def get_stats() -> dict:
    """
    Retourne des statistiques sur les simulations sauvegardees.
    """
    simulations = charger_simulations()
    if not simulations:
        return {"total": 0, "pays": {}, "devises": {}, "montant_total": 0.0}

    pays    = {}
    devises = {}
    montant_total = 0.0

    for s in simulations:
        p = s.get("pays_fournisseur", "Inconnu")
        pays[p] = pays.get(p, 0) + 1

        d = s.get("devise", "N/A")
        devises[d] = devises.get(d, 0) + 1

        m = s.get("montant") or 0
        montant_total += float(m)

    return {
        "total"        : len(simulations),
        "pays"         : pays,
        "devises"      : devises,
        "montant_total": montant_total,
    }


# ============================================================
# Construction de l'entrée à sauvegarder
# ============================================================

def _construire_entree(resultat) -> dict:
    """Construit le dictionnaire a sauvegarder depuis un PaymentResult."""
    op   = resultat.operation
    now  = datetime.now()

    return {
        "id"              : now.strftime("%Y%m%d_%H%M%S") + f"_{now.microsecond:06d}",
        "date"            : now.strftime("%d/%m/%Y %H:%M"),
        "entreprise"      : op.nom_entreprise       or "N/A",
        "pays_acheteur"   : op.pays_acheteur         or "N/A",
        "fournisseur"     : op.nom_fournisseur       or "N/A",
        "pays_fournisseur": op.pays_fournisseur      or "N/A",
        "montant"         : op.montant               or 0.0,
        "devise"          : op.devise                or "N/A",
        "mode_paiement"   : op.mode_paiement         or "N/A",
        "type_marchandise": op.type_marchandise      or "N/A",
        "banque"          : op.banque_fournisseur    or "N/A",
        "swift_bic"       : op.swift_bic             or "N/A",
        "nb_documents"    : len(resultat.documents),
        "mode_degrade"    : resultat.mode_degrade,
        "resume_base"     : resultat.resume.get("resume_base", ""),
    }