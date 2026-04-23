from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class PaymentOperation:
    """
    structure de données centrale représentant une opération de paiement international.
    Représente une opération de paiement international.
    C'est l'objet central manipulé par tous les modules de l'application.
    """

    # --- Informations sur l'acheteur ---
    nom_entreprise: Optional[str] = None
    pays_acheteur: Optional[str] = None

    # --- Informations sur le fournisseur ---
    nom_fournisseur: Optional[str] = None
    pays_fournisseur: Optional[str] = None
    banque_fournisseur: Optional[str] = None
    iban_fournisseur: Optional[str] = None
    swift_bic: Optional[str] = None

    # --- Informations sur le paiement ---
    montant: Optional[float] = None
    devise: Optional[str] = None
    mode_paiement: Optional[str] = None      # Ex: virement SWIFT, lettre de crédit, remise documentaire

    # --- Informations sur la marchandise ---
    type_marchandise: Optional[str] = None   # Ex: électronique, textile, alimentaire
    description_marchandise: Optional[str] = None

    # --- Métadonnées de session ---
    etape_courante: int = 0
    est_complete: bool = False
    date_creation: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y %H:%M"))

    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour le LLM et les générateurs."""
        return {
            "nom_entreprise": self.nom_entreprise,
            "pays_acheteur": self.pays_acheteur,
            "nom_fournisseur": self.nom_fournisseur,
            "pays_fournisseur": self.pays_fournisseur,
            "banque_fournisseur": self.banque_fournisseur,
            "iban_fournisseur": self.iban_fournisseur,
            "swift_bic": self.swift_bic,
            "montant": self.montant,
            "devise": self.devise,
            "mode_paiement": self.mode_paiement,
            "type_marchandise": self.type_marchandise,
            "description_marchandise": self.description_marchandise,
            "date_creation": self.date_creation,
        }

    def est_pret_pour_generation(self) -> bool:
        """Vérifie que les champs obligatoires sont remplis avant de générer le résumé."""
        champs_obligatoires = [
            self.montant,
            self.devise,
            self.pays_fournisseur,
            self.type_marchandise,
            self.mode_paiement,
        ]
        return all(champ is not None for champ in champs_obligatoires)

    def __str__(self) -> str:
        return (
            f"PaymentOperation("
            f"montant={self.montant} {self.devise}, "
            f"fournisseur={self.nom_fournisseur} ({self.pays_fournisseur}), "
            f"marchandise={self.type_marchandise}, "
            f"mode={self.mode_paiement}, "
            f"complete={self.est_complete})"
        )