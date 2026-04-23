import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.summary_generator import generer_resume, _generer_resume_base
from models.payment_model import PaymentOperation


def creer_operation_complete() -> PaymentOperation:
    op = PaymentOperation()
    op.nom_entreprise          = "REasy SAS"
    op.pays_acheteur           = "France"
    op.nom_fournisseur         = "Shenzhen Electronics Co."
    op.pays_fournisseur        = "Chine"
    op.type_marchandise        = "Électronique"
    op.description_marchandise = "500 smartphones Android"
    op.montant                 = 15000.0
    op.devise                  = "USD"
    op.mode_paiement           = "Virement SWIFT"
    op.banque_fournisseur      = "Bank of China"
    op.swift_bic               = "BKCHCNBJ"
    op.iban_fournisseur        = "CN1234567890"
    return op


def creer_operation_minimale() -> PaymentOperation:
    """Opération avec uniquement les champs obligatoires."""
    op = PaymentOperation()
    op.nom_entreprise   = "PME Dupont"
    op.pays_fournisseur = "Maroc"
    op.montant          = 5000.0
    op.devise           = "EUR"
    op.mode_paiement    = "Lettre de crédit (L/C)"
    op.type_marchandise = "Textile"
    return op


def test_resume_base_contenu():
    print("=== Test 1 : _generer_resume_base() — contenu ===")
    op = creer_operation_complete()
    resume = _generer_resume_base(op)

    assert isinstance(resume, str), "Le résumé doit être une chaîne"
    assert len(resume) > 100,       "Le résumé doit être substantiel"

    assert "REasy SAS"               in resume, "Le nom de l'entreprise doit apparaître"
    assert "Chine"                   in resume, "Le pays fournisseur doit apparaître"
    assert "15 000"                  in resume, "Le montant formaté doit apparaître"
    assert "USD"                     in resume, "La devise doit apparaître"
    assert "Virement SWIFT"          in resume, "Le mode de paiement doit apparaître"
    assert "Bank of China"           in resume, "La banque doit apparaître"
    assert "BKCHCNBJ"               in resume, "Le SWIFT/BIC doit apparaître"

    print(f"  Longueur du résumé : {len(resume)} caractères")
    print("  Toutes les données clés sont présentes")
    print("  OK\n")


def test_resume_base_sections():
    print("=== Test 2 : _generer_resume_base() — sections structurées ===")
    op = creer_operation_complete()
    resume = _generer_resume_base(op)

    sections = [
        "IDENTIFICATION DE L'OPÉRATION",
        "DÉTAILS FINANCIERS",
        "NATURE DE LA MARCHANDISE",
        "COORDONNÉES BANCAIRES",
        "INFORMATIONS DE SESSION",
    ]
    for section in sections:
        assert section in resume, f"Section '{section}' manquante dans le résumé"
        print(f"  ✓ Section '{section}' présente")
    print("  OK\n")


def test_resume_base_champs_vides():
    print("=== Test 3 : _generer_resume_base() — champs optionnels vides ===")
    op = creer_operation_minimale()
    resume = _generer_resume_base(op)

    assert isinstance(resume, str)
    assert len(resume) > 0
    # Les champs vides doivent afficher N/A
    assert "N/A" in resume, "Les champs vides doivent afficher 'N/A'"

    print(f"  Opération minimale → résumé généré ({len(resume)} caractères)")
    print(f"  Champs vides affichent 'N/A'")
    print("  OK\n")


def test_resume_base_montant_formate():
    print("=== Test 4 : _generer_resume_base() — montant formaté ===")
    op = creer_operation_complete()
    resume = _generer_resume_base(op)

    assert "15000.0" not in resume, \
        "Le montant brut float ne doit pas apparaître"
    assert "15 000" in resume, \
        "Le montant doit être formaté avec séparateur de milliers"

    print(f"  Montant '15000.0' → affiché formaté avec séparateur de milliers")
    print("  OK\n")


def test_generer_resume_structure_retour():
    print("=== Test 5 : generer_resume() — structure du retour ===")
    op = creer_operation_complete()
    resultat = generer_resume(op)

    assert "resume_base"  in resultat, "Clé 'resume_base' manquante"
    assert "resume_llm"   in resultat, "Clé 'resume_llm' manquante"
    assert "mode_degrade" in resultat, "Clé 'mode_degrade' manquante"

    assert isinstance(resultat["resume_base"], str), \
        "'resume_base' doit être une chaîne"
    assert len(resultat["resume_base"]) > 0, \
        "'resume_base' ne doit pas être vide"
    assert isinstance(resultat["mode_degrade"], bool), \
        "'mode_degrade' doit être un booléen"

    print(f"  Structure du retour validée :")
    print(f"    resume_base  : {len(resultat['resume_base'])} caractères")
    print(f"    resume_llm   : {'présent' if resultat['resume_llm'] else 'absent (mode dégradé)'}")
    print(f"    mode_degrade : {resultat['mode_degrade']}")
    print("  OK\n")


def test_generer_resume_mode_degrade():
    print("=== Test 6 : generer_resume() — mode dégradé sans Ollama ===")
    op = creer_operation_complete()
    resultat = generer_resume(op)

    # Sans Ollama disponible, resume_base doit toujours être présent
    assert resultat["resume_base"] is not None, \
        "Le résumé de base doit toujours être disponible même sans Ollama"

    if resultat["mode_degrade"]:
        assert resultat["resume_llm"] is None, \
            "En mode dégradé, resume_llm doit être None"
        print("  Mode dégradé actif (Ollama absent)")
        print("  resume_base disponible comme filet de sécurité")
    else:
        print("  Ollama disponible — resume_llm présent")
        print(f"  Aperçu resume_llm : '{resultat['resume_llm'][:100]}...'")

    print("  OK\n")


def test_apercu_resume_base():
    print("=== Test 7 : aperçu complet du résumé de base ===")
    op = creer_operation_complete()
    resume = _generer_resume_base(op)

    print(f"  {'='*45}")
    for ligne in resume.split("\n"):
        print(f"  {ligne}")
    print(f"  {'='*45}")
    print("  OK\n")


def test_deux_operations_distinctes():
    print("=== Test 8 : deux opérations différentes → deux résumés distincts ===")
    op1 = creer_operation_complete()
    op2 = creer_operation_minimale()

    resume1 = _generer_resume_base(op1)
    resume2 = _generer_resume_base(op2)

    assert resume1 != resume2, "Deux opérations différentes doivent produire des résumés différents"
    assert "REasy SAS"  in resume1, "Le nom de l'opération 1 doit être dans résumé 1"
    assert "PME Dupont" in resume2, "Le nom de l'opération 2 doit être dans résumé 2"
    assert "REasy SAS"  not in resume2, "Le nom de l'opération 1 ne doit pas être dans résumé 2"

    print(f"  Résumé opération 1 : {len(resume1)} caractères (REasy SAS, Chine, 15 000 USD)")
    print(f"  Résumé opération 2 : {len(resume2)} caractères (PME Dupont, Maroc, 5 000 EUR)")
    print("  Les deux résumés sont bien distincts")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — core/summary_generator.py")
    print("=" * 55 + "\n")
    try:
        test_resume_base_contenu()
        test_resume_base_sections()
        test_resume_base_champs_vides()
        test_resume_base_montant_formate()
        test_generer_resume_structure_retour()
        test_generer_resume_mode_degrade()
        test_apercu_resume_base()
        test_deux_operations_distinctes()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)