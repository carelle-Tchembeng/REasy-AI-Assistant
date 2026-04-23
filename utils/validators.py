import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DEVISES_ACCEPTEES, MONTANT_MIN, MONTANT_MAX


def valider_reponse(reponse: str, question: dict) -> tuple[bool, str]:
    """
    Point d'entrée principal. Valide une réponse selon le type de question.
    Retourne un tuple (est_valide: bool, message_erreur: str).
    Le message est vide si la réponse est valide.
    """
    # Champ obligatoire vide
    if question.get("obligatoire") and not reponse.strip():
        return False, "Ce champ est obligatoire. Merci de fournir une réponse."

    # Champ optionnel vide — on accepte
    if not reponse.strip():
        return True, ""

    type_question = question.get("type")

    if type_question == "nombre":
        return valider_montant(reponse)

    if type_question == "choix_multiple":
        return valider_choix(reponse, question.get("options", []))

    if question.get("champ_modele") == "devise":
        return valider_devise(reponse)

    if question.get("champ_modele") == "swift_bic":
        return valider_swift(reponse)

    # texte_libre — on accepte tout texte non vide
    return valider_texte_libre(reponse)


def valider_montant(valeur: str) -> tuple[bool, str]:
    """Vérifie que le montant est un nombre positif dans les limites acceptées."""
    try:
        montant = float(valeur.replace(",", ".").replace(" ", ""))
    except ValueError:
        return False, f"Montant invalide : '{valeur}'. Veuillez entrer un nombre (ex: 15000)."

    if montant < MONTANT_MIN:
        return False, f"Le montant doit être supérieur à {MONTANT_MIN}."

    if montant > MONTANT_MAX:
        return False, f"Le montant dépasse le maximum autorisé ({MONTANT_MAX:,.0f})."

    return True, ""


def valider_devise(valeur: str) -> tuple[bool, str]:
    """Vérifie que la devise est dans la liste des devises acceptées."""
    valeur = valeur.strip().upper()
    if valeur not in DEVISES_ACCEPTEES and valeur != "AUTRE":
        return False, (
            f"Devise '{valeur}' non reconnue. "
            f"Devises acceptées : {', '.join(DEVISES_ACCEPTEES)}."
        )
    return True, ""


def valider_choix(valeur: str, options: list) -> tuple[bool, str]:
    """Vérifie que la valeur fait partie des options proposées."""
    options_lower = [o.lower() for o in options]
    if valeur.strip().lower() not in options_lower:
        return False, (
            f"Choix invalide : '{valeur}'. "
            f"Options disponibles : {', '.join(options)}."
        )
    return True, ""


def valider_swift(valeur: str) -> tuple[bool, str]:
    """Vérifie le format basique d'un code SWIFT/BIC (8 ou 11 caractères alphanumériques)."""
    valeur = valeur.strip().upper()
    if not valeur.isalnum():
        return False, "Le code SWIFT/BIC ne doit contenir que des lettres et des chiffres."
    if len(valeur) not in (8, 11):
        return False, f"Le code SWIFT/BIC doit contenir 8 ou 11 caractères (reçu : {len(valeur)})."
    return True, ""


def valider_texte_libre(valeur: str) -> tuple[bool, str]:
    """Vérifie qu'un texte libre n'est pas trop court."""
    if len(valeur.strip()) < 2:
        return False, "La réponse est trop courte. Merci d'être plus précis."
    return True, ""