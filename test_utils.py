import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import (
    valider_reponse, valider_montant, valider_devise,
    valider_choix, valider_swift, valider_texte_libre
)
from utils.formatter import (
    formater_montant, formater_nom_champ,
    formater_operation_pour_llm, formater_checklist_pour_affichage
)
from models.payment_model import PaymentOperation


# ============================================================
# TESTS validators.py
# ============================================================

def test_valider_montant():
    print("=== Test 1 : valider_montant() ===")

    # Cas valides
    ok, msg = valider_montant("15000")
    assert ok, f"Attendu True, obtenu False : {msg}"

    ok, msg = valider_montant("15 000,50")
    assert ok, f"Attendu True pour '15 000,50' : {msg}"

    # Cas invalides
    ok, msg = valider_montant("abc")
    assert not ok, "Doit rejeter 'abc'"
    print(f"  'abc'     → rejeté : {msg}")

    ok, msg = valider_montant("-500")
    assert not ok, "Doit rejeter un montant négatif"
    print(f"  '-500'    → rejeté : {msg}")

    ok, msg = valider_montant("99999999999")
    assert not ok, "Doit rejeter un montant trop élevé"
    print(f"  '99999999999' → rejeté : {msg}")

    print("  Cas valides acceptés, cas invalides rejetés")
    print("  OK\n")


def test_valider_devise():
    print("=== Test 2 : valider_devise() ===")

    ok, _ = valider_devise("USD")
    assert ok, "USD doit être accepté"

    ok, _ = valider_devise("eur")
    assert ok, "eur (minuscule) doit être accepté"

    ok, msg = valider_devise("XYZ")
    assert not ok, "XYZ doit être rejeté"
    print(f"  'XYZ' → rejeté : {msg}")

    ok, _ = valider_devise("Autre")
    assert ok, "'Autre' doit être accepté"

    print("  USD, EUR acceptés — XYZ rejeté — 'Autre' accepté")
    print("  OK\n")


def test_valider_choix():
    print("=== Test 3 : valider_choix() ===")
    options = ["Chine", "Maroc", "États-Unis", "Autre"]

    ok, _ = valider_choix("Chine", options)
    assert ok, "Chine doit être accepté"

    ok, _ = valider_choix("chine", options)
    assert ok, "chine (minuscule) doit être accepté"

    ok, msg = valider_choix("Japon", options)
    assert not ok, "Japon doit être rejeté"
    print(f"  'Japon' → rejeté : {msg}")

    print("  Choix valides acceptés (insensible à la casse) — invalides rejetés")
    print("  OK\n")


def test_valider_swift():
    print("=== Test 4 : valider_swift() ===")

    ok, _ = valider_swift("BKCHCNBJ")
    assert ok, "BKCHCNBJ (8 car.) doit être accepté"

    ok, _ = valider_swift("BKCHCNBJ123")
    assert ok, "BKCHCNBJ123 (11 car.) doit être accepté"

    ok, msg = valider_swift("BK CH")
    assert not ok, "Code avec espace doit être rejeté"
    print(f"  'BK CH'   → rejeté : {msg}")

    ok, msg = valider_swift("BK")
    assert not ok, "Code trop court doit être rejeté"
    print(f"  'BK'      → rejeté : {msg}")

    print("  Codes 8 et 11 car. acceptés — formats invalides rejetés")
    print("  OK\n")


def test_valider_champ_obligatoire_vide():
    print("=== Test 5 : champ obligatoire vide ===")
    question = {"obligatoire": True, "type": "texte_libre", "champ_modele": "nom_entreprise"}

    ok, msg = valider_reponse("", question)
    assert not ok, "Un champ obligatoire vide doit être rejeté"
    print(f"  Champ obligatoire vide → rejeté : {msg}")

    question_opt = {"obligatoire": False, "type": "texte_libre", "champ_modele": "description_marchandise"}
    ok, _ = valider_reponse("", question_opt)
    assert ok, "Un champ optionnel vide doit être accepté"
    print(f"  Champ optionnel vide  → accepté")
    print("  OK\n")


# ============================================================
# TESTS formatter.py
# ============================================================

def test_formater_montant():
    print("=== Test 6 : formater_montant() ===")

    resultat = formater_montant(15000.0, "USD")
    assert "USD" in resultat, "La devise doit apparaître"
    assert "15" in resultat, "Le montant doit apparaître"
    print(f"  15000.0, 'USD'  → '{resultat}'")

    resultat = formater_montant(1500000.0, "EUR")
    print(f"  1500000.0, 'EUR' → '{resultat}'")

    resultat = formater_montant(None, "USD")
    assert resultat == "Non renseigné"
    print(f"  None, 'USD'     → '{resultat}'")

    print("  OK\n")


def test_formater_nom_champ():
    print("=== Test 7 : formater_nom_champ() ===")
    cas = {
        "nom_entreprise"   : "Nom de l'entreprise (acheteur)",
        "pays_fournisseur" : "Pays du fournisseur",
        "swift_bic"        : "Code SWIFT / BIC",
        "montant"          : "Montant",
    }
    for champ, attendu in cas.items():
        resultat = formater_nom_champ(champ)
        assert resultat == attendu, f"'{champ}' → attendu '{attendu}', obtenu '{resultat}'"
        print(f"  '{champ}' → '{resultat}'")
    print("  OK\n")


def test_formater_operation_pour_llm():
    print("=== Test 8 : formater_operation_pour_llm() ===")
    op = PaymentOperation()
    op.nom_entreprise   = "REasy SAS"
    op.pays_fournisseur = "Chine"
    op.montant          = 15000.0
    op.devise           = "USD"
    op.mode_paiement    = "Virement SWIFT"
    op.type_marchandise = "Électronique"

    resultat = formater_operation_pour_llm(op)
    assert "REasy SAS" in resultat
    assert "Chine" in resultat
    assert "USD" in resultat
    assert "Virement SWIFT" in resultat

    print("  Bloc texte généré pour le LLM :")
    for ligne in resultat.split("\n"):
        print(f"    {ligne}")
    print("  OK\n")


def test_formater_checklist_pour_affichage():
    print("=== Test 9 : formater_checklist_pour_affichage() ===")
    documents = [
        {"nom": "Facture commerciale", "obligatoire": True,  "description": "Émise par le fournisseur."},
        {"nom": "Certificat d'origine", "obligatoire": True,  "description": "Prouve l'origine des marchandises."},
        {"nom": "Certificat d'inspection", "obligatoire": False, "description": "Délivré par un organisme tiers."},
    ]
    resultat = formater_checklist_pour_affichage(documents)
    assert "✅" in resultat, "Les documents obligatoires doivent avoir ✅"
    assert "📋" in resultat, "Les documents recommandés doivent avoir 📋"
    assert "Facture commerciale" in resultat

    print("  Checklist formatée :")
    for ligne in resultat.split("\n"):
        print(f"    {ligne}")

    # Test liste vide
    resultat_vide = formater_checklist_pour_affichage([])
    assert resultat_vide == "Aucun document identifié."
    print(f"\n  Liste vide → '{resultat_vide}'")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — utils/validators.py + utils/formatter.py")
    print("=" * 55 + "\n")
    try:
        test_valider_montant()
        test_valider_devise()
        test_valider_choix()
        test_valider_swift()
        test_valider_champ_obligatoire_vide()
        test_formater_montant()
        test_formater_nom_champ()
        test_formater_operation_pour_llm()
        test_formater_checklist_pour_affichage()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)