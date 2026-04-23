import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def formater_montant(montant: float, devise: str) -> str:
    """
    Formate un montant avec séparateurs de milliers et devise.
    Ex : 15000.5, 'USD' → '15 000,50 USD'
    """
    if montant is None:
        return "Non renseigné"
    try:
        montant_formate = f"{montant:,.2f}".replace(",", " ").replace(".", ",")
        return f"{montant_formate} {devise.upper()}"
    except (ValueError, AttributeError):
        return f"{montant} {devise}"


def formater_nom_champ(champ: str) -> str:
    """
    Transforme un nom de champ snake_case en libellé lisible.
    Ex : 'pays_fournisseur' → 'Pays du fournisseur'
    """
    correspondances = {
        "nom_entreprise"         : "Nom de l'entreprise (acheteur)",
        "pays_acheteur"          : "Pays de l'acheteur",
        "nom_fournisseur"        : "Nom du fournisseur",
        "pays_fournisseur"       : "Pays du fournisseur",
        "banque_fournisseur"     : "Banque du fournisseur",
        "iban_fournisseur"       : "IBAN / Numéro de compte",
        "swift_bic"              : "Code SWIFT / BIC",
        "montant"                : "Montant",
        "devise"                 : "Devise",
        "mode_paiement"          : "Mode de paiement",
        "type_marchandise"       : "Type de marchandise",
        "description_marchandise": "Description de la marchandise",
        "date_creation"          : "Date de l'opération",
    }
    return correspondances.get(champ, champ.replace("_", " ").capitalize())


def formater_operation_pour_llm(operation) -> str:
    """
    Convertit un PaymentOperation en bloc texte structuré
    prêt à être injecté dans un prompt Mistral.
    """
    data = operation.to_dict()
    lignes = []

    for champ, valeur in data.items():
        if valeur is None:
            continue
        libelle = formater_nom_champ(champ)
        if champ == "montant":
            devise = data.get("devise", "")
            valeur_affichee = formater_montant(valeur, devise)
        else:
            valeur_affichee = str(valeur)
        lignes.append(f"- {libelle} : {valeur_affichee}")

    return "\n".join(lignes) if lignes else "Aucune donnée disponible."


def formater_checklist_pour_affichage(documents: list) -> str:
    """
    Formate une liste de documents en texte structuré pour l'affichage.
    Ex : [{"nom": "Facture", "obligatoire": True}] → '✅ Facture (obligatoire)'
    """
    if not documents:
        return "Aucun document identifié."

    lignes = []
    for doc in documents:
        statut = "✅" if doc.get("obligatoire") else "📋"
        mention = "obligatoire" if doc.get("obligatoire") else "recommandé"
        lignes.append(f"{statut} **{doc['nom']}** — {mention}")
        if doc.get("description"):
            lignes.append(f"   _{doc['description']}_")

    return "\n".join(lignes)