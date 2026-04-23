import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.prompt_builder import (
    construire_prompt_resume,
    construire_prompt_checklist,
    _formater_checklist_pour_prompt
)
from models.payment_model import PaymentOperation


# Opération de test réutilisée dans tous les tests
def creer_operation_test() -> PaymentOperation:
    op = PaymentOperation()
    op.nom_entreprise        = "REasy SAS"
    op.pays_acheteur         = "France"
    op.nom_fournisseur       = "Shenzhen Electronics Co."
    op.pays_fournisseur      = "Chine"
    op.type_marchandise      = "Électronique"
    op.description_marchandise = "500 unités de smartphones Android"
    op.montant               = 15000.0
    op.devise                = "USD"
    op.mode_paiement         = "Virement SWIFT"
    op.banque_fournisseur    = "Bank of China"
    op.swift_bic             = "BKCHCNBJ"
    return op


CHECKLIST_TEST = [
    {"nom": "Facture commerciale",    "obligatoire": True,  "description": "Émise par le fournisseur."},
    {"nom": "Certificat d'origine",   "obligatoire": True,  "description": "Prouve l'origine des marchandises."},
    {"nom": "Packing list",           "obligatoire": True,  "description": "Détail du contenu des colis."},
    {"nom": "Certificat d'inspection","obligatoire": False, "description": "Délivré par un organisme tiers."},
]


def test_construire_prompt_resume_contenu():
    print("=== Test 1 : construire_prompt_resume() — contenu ===")
    op = creer_operation_test()
    prompt = construire_prompt_resume(op)

    assert isinstance(prompt, str), "Le prompt doit être une chaîne"
    assert len(prompt) > 100, "Le prompt doit être substantiel"

    # Les données de l'opération doivent être présentes
    assert "REasy SAS" in prompt,              "Le nom de l'entreprise doit apparaître"
    assert "Chine" in prompt,                  "Le pays fournisseur doit apparaître"
    assert "USD" in prompt,                    "La devise doit apparaître"
    assert "Virement SWIFT" in prompt,         "Le mode de paiement doit apparaître"
    assert "Électronique" in prompt,           "Le type de marchandise doit apparaître"

    print(f"  Longueur du prompt : {len(prompt)} caractères")
    print(f"  Données vérifiées : REasy SAS, Chine, USD, Virement SWIFT, Électronique")
    print("  OK\n")


def test_construire_prompt_resume_format_montant():
    print("=== Test 2 : construire_prompt_resume() — montant formaté ===")
    op = creer_operation_test()
    prompt = construire_prompt_resume(op)

    # Le montant doit être formaté lisiblement, pas brut
    assert "15 000" in prompt or "15000" in prompt, \
        "Le montant doit apparaître dans le prompt"
    assert "15000.0" not in prompt, \
        "Le montant brut float ne doit pas apparaître — il doit être formaté"

    print(f"  Montant correctement formaté dans le prompt")
    print("  OK\n")


def test_construire_prompt_checklist_contenu():
    print("=== Test 3 : construire_prompt_checklist() — contenu ===")
    op = creer_operation_test()
    prompt = construire_prompt_checklist(op, CHECKLIST_TEST)

    assert isinstance(prompt, str), "Le prompt doit être une chaîne"
    assert len(prompt) > 100, "Le prompt doit être substantiel"

    # Les données de l'opération
    assert "REasy SAS" in prompt,     "Le nom de l'entreprise doit apparaître"
    assert "Chine" in prompt,         "Le pays fournisseur doit apparaître"

    # Les documents de la checklist
    assert "Facture commerciale" in prompt,  "La facture doit apparaître dans le prompt"
    assert "Certificat d'origine" in prompt, "Le certificat d'origine doit apparaître"
    assert "obligatoire" in prompt,          "La mention obligatoire doit apparaître"

    print(f"  Longueur du prompt : {len(prompt)} caractères")
    print(f"  Données opération + checklist correctement injectées")
    print("  OK\n")


def test_construire_prompt_checklist_vide():
    print("=== Test 4 : construire_prompt_checklist() — checklist vide ===")
    op = creer_operation_test()
    prompt = construire_prompt_checklist(op, [])

    assert isinstance(prompt, str)
    assert "Aucun document" in prompt, \
        "Un message doit indiquer qu'aucun document n'a été identifié"

    print(f"  Checklist vide → message 'Aucun document' présent dans le prompt")
    print("  OK\n")


def test_formater_checklist_pour_prompt():
    print("=== Test 5 : _formater_checklist_pour_prompt() ===")
    resultat = _formater_checklist_pour_prompt(CHECKLIST_TEST)

    assert "Facture commerciale" in resultat
    assert "obligatoire" in resultat
    assert "recommandé" in resultat
    assert "Certificat d'inspection" in resultat

    # Vérifier que le format est sobre (pas de markdown lourd)
    assert "**" not in resultat, "Pas de markdown bold dans le prompt — trop lourd pour le LLM"

    print("  Checklist formatée pour le LLM :")
    for ligne in resultat.split("\n"):
        print(f"    {ligne}")
    print("  OK\n")


def test_prompt_resume_apercu():
    print("=== Test 6 : aperçu complet du prompt résumé ===")
    op = creer_operation_test()
    prompt = construire_prompt_resume(op)

    print(f"  {'='*45}")
    for ligne in prompt.split("\n")[:20]:
        print(f"  {ligne}")
    print(f"  ... ({len(prompt)} caractères au total)")
    print(f"  {'='*45}")
    print("  OK\n")


def test_prompt_checklist_apercu():
    print("=== Test 7 : aperçu complet du prompt checklist ===")
    op = creer_operation_test()
    prompt = construire_prompt_checklist(op, CHECKLIST_TEST)

    print(f"  {'='*45}")
    for ligne in prompt.split("\n")[:20]:
        print(f"  {ligne}")
    print(f"  ... ({len(prompt)} caractères au total)")
    print(f"  {'='*45}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — llm/prompt_builder.py")
    print("=" * 55 + "\n")
    try:
        test_construire_prompt_resume_contenu()
        test_construire_prompt_resume_format_montant()
        test_construire_prompt_checklist_contenu()
        test_construire_prompt_checklist_vide()
        test_formater_checklist_pour_prompt()
        test_prompt_resume_apercu()
        test_prompt_checklist_apercu()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)