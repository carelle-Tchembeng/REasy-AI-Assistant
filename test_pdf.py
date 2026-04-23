import sys
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


def creer_resultat_test():
    """
    Cree un PaymentResult SANS appeler Ollama.
    Construction manuelle pour eviter tout appel reseau.
    """
    from models.payment_model import PaymentOperation
    from services.payment_service import PaymentResult
    from core.checklist_generator import _generer_checklist_base
    from core.summary_generator import _generer_resume_base

    op = PaymentOperation()
    op.nom_entreprise          = "REasy SAS"
    op.pays_acheteur           = "France"
    op.nom_fournisseur         = "Shenzhen Electronics Co."
    op.pays_fournisseur        = "Chine"
    op.type_marchandise        = "Electronique"
    op.description_marchandise = "500 smartphones Android"
    op.montant                 = 15000.0
    op.devise                  = "USD"
    op.mode_paiement           = "Virement SWIFT"
    op.banque_fournisseur      = "Bank of China"
    op.swift_bic               = "BKCHCNBJ"
    op.iban_fournisseur        = "CN1234567890"
    op.est_complete            = True

    resume = {
        "resume_base"  : _generer_resume_base(op),
        "resume_llm"   : None,
        "mode_degrade" : True,
    }
    documents = _generer_checklist_base(op)
    checklist = {
        "documents"     : documents,
        "enrichissement": None,
        "pays"          : op.pays_fournisseur,
        "mode_degrade"  : True,
    }
    return PaymentResult(op, resume, checklist)


def test_fonctions_exposees():
    print("=== Test 1 : fonctions presentes dans pdf_exporter.py ===")
    chemin = os.path.join(BASE_DIR, "utils", "pdf_exporter.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    fonctions = [
        "def generer_pdf",
        "def generer_nom_fichier",
        "def _creer_pdf",
        "def _ajouter_page_titre",
        "def _ajouter_resume",
        "def _ajouter_checklist",
        "def _ajouter_infos_pays",
        "def _nettoyer_texte",
        "def _titre_section",
        "def _item_document",
    ]
    for fn in fonctions:
        assert fn in contenu, f"Fonction manquante : '{fn}'"
        print(f"  v {fn}()")
    print("  OK\n")


def test_nettoyer_texte():
    print("=== Test 2 : _nettoyer_texte() ===")
    from utils.pdf_exporter import _nettoyer_texte

    cas = [
        ("**texte gras**",       "texte gras"),
        ("*italique*",           "italique"),
        ("## Titre",             "Titre"),
        ("`code`",               "code"),
        ("**Montant** : 15 000", "Montant : 15 000"),
        ("tiret long \u2014 ok", "tiret long - ok"),
        ("apostrophe \u2019 ok", "apostrophe ' ok"),
    ]
    for entree, attendu in cas:
        resultat = _nettoyer_texte(entree)
        assert resultat == attendu, \
            f"'{entree}' -> attendu '{attendu}', obtenu '{resultat}'"
        print(f"  OK : '{entree}' -> '{resultat}'")
    print("  OK\n")


def test_generer_nom_fichier():
    print("=== Test 3 : generer_nom_fichier() ===")
    from utils.pdf_exporter import generer_nom_fichier

    resultat = creer_resultat_test()
    nom      = generer_nom_fichier(resultat)

    assert nom.endswith(".pdf"),  "Doit se terminer par .pdf"
    assert "REasy" in nom,        "Prefixe REasy manquant"
    assert "Chine" in nom,        "Le pays doit apparaitre dans le nom"
    assert " " not in nom,        "Pas d'espaces dans le nom de fichier"

    print(f"  Nom genere : '{nom}'")
    print("  OK\n")


def test_generer_nom_cas_limites():
    print("=== Test 4 : generer_nom_fichier() - cas limites ===")
    from utils.pdf_exporter import generer_nom_fichier
    from models.payment_model import PaymentOperation
    from services.payment_service import PaymentResult

    resume    = {"resume_base": "Test", "resume_llm": None, "mode_degrade": True}
    checklist = {"documents": [], "enrichissement": None, "pays": "Maroc", "mode_degrade": True}

    # Nom None
    op1 = PaymentOperation()
    nom1 = generer_nom_fichier(PaymentResult(op1, resume, checklist))
    assert "operation" in nom1
    assert " " not in nom1
    print(f"  Nom None -> '{nom1}'")

    # Nom avec espaces
    op2 = PaymentOperation()
    op2.nom_entreprise   = "PME Dupont"
    op2.pays_fournisseur = "Maroc"
    nom2 = generer_nom_fichier(PaymentResult(op2, resume, checklist))
    assert "PME_Dupont" in nom2
    assert " " not in nom2
    print(f"  Avec espaces -> '{nom2}'")
    print("  OK\n")


def test_generer_pdf_bytes():
    print("=== Test 5 : generer_pdf() retourne des bytes valides ===")
    try:
        from fpdf import FPDF
    except ImportError:
        print("  IGNORE - fpdf2 non installe (pip install fpdf2)")
        print("  OK\n")
        return

    from utils.pdf_exporter import generer_pdf
    resultat  = creer_resultat_test()
    pdf_bytes = generer_pdf(resultat)

    assert isinstance(pdf_bytes, bytes),  "Doit retourner des bytes"
    assert len(pdf_bytes) > 1000,          "PDF trop petit"
    assert pdf_bytes[:4] == b"%PDF",       "Signature PDF manquante"

    print(f"  Type   : {type(pdf_bytes).__name__}")
    print(f"  Taille : {len(pdf_bytes):,} bytes ({len(pdf_bytes) // 1024} Ko)")
    print(f"  En-tete : {pdf_bytes[:4]}")
    print("  OK\n")


def test_pdf_mode_degrade():
    print("=== Test 6 : generer_pdf() fonctionne en mode degrade ===")
    try:
        from fpdf import FPDF
    except ImportError:
        print("  IGNORE - fpdf2 non installe")
        print("  OK\n")
        return

    from utils.pdf_exporter import generer_pdf
    resultat = creer_resultat_test()

    assert resultat.resume["resume_llm"] is None
    assert resultat.mode_degrade is True

    pdf_bytes = generer_pdf(resultat)
    assert isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 1000

    print(f"  Mode degrade actif")
    print(f"  PDF genere : {len(pdf_bytes):,} bytes")
    print("  OK\n")


def test_pdf_plusieurs_pays():
    print("=== Test 7 : generer_pdf() pour differents pays ===")
    try:
        from fpdf import FPDF
    except ImportError:
        print("  IGNORE - fpdf2 non installe")
        print("  OK\n")
        return

    from utils.pdf_exporter import generer_pdf
    from models.payment_model import PaymentOperation
    from services.payment_service import PaymentResult
    from core.checklist_generator import _generer_checklist_base
    from core.summary_generator import _generer_resume_base

    for pays in ["Chine", "Maroc", "Etats-Unis", "Allemagne"]:
        op = PaymentOperation()
        op.nom_entreprise   = "Test SA"
        op.pays_fournisseur = pays
        op.montant          = 5000.0
        op.devise           = "EUR"
        op.mode_paiement    = "Virement SWIFT"
        op.type_marchandise = "Electronique"

        resume    = {"resume_base": _generer_resume_base(op), "resume_llm": None, "mode_degrade": True}
        checklist = {"documents": _generer_checklist_base(op), "enrichissement": None, "pays": pays, "mode_degrade": True}
        resultat  = PaymentResult(op, resume, checklist)

        pdf_bytes = generer_pdf(resultat)
        assert isinstance(pdf_bytes, bytes) and len(pdf_bytes) > 1000
        print(f"  {pays} -> {len(pdf_bytes):,} bytes OK")

    print("  OK\n")


def test_result_display_modifie():
    print("=== Test 8 : result_display.py modifie correctement ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    verifications = [
        ("from utils.pdf_exporter import generer_pdf, generer_nom_fichier", "Import pdf_exporter"),
        ("def _afficher_bouton_pdf",  "Fonction _afficher_bouton_pdf()"),
        ("st.download_button",        "st.download_button()"),
        ("application/pdf",           "MIME type PDF"),
        ("ImportError",               "Gestion fpdf2 absent"),
    ]
    for code, description in verifications:
        assert code in contenu, f"Manquant : {description}"
        print(f"  v {description}")
    print("  OK\n")


def test_requirements_contient_fpdf2():
    print("=== Test 9 : requirements.txt contient fpdf2 ===")
    chemin = os.path.join(BASE_DIR, "requirements.txt")

    # Essai avec plusieurs encodages pour compatibilite Windows
    contenu = None
    for enc in ("utf-8-sig", "utf-16", "utf-8", "latin-1"):
        try:
            with open(chemin, encoding=enc) as f:
                contenu = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    assert contenu is not None, "Impossible de lire requirements.txt"
    assert "fpdf2" in contenu,  "fpdf2 manquant dans requirements.txt"
    print("  requirements.txt contient fpdf2 OK")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS - Export PDF (utils/pdf_exporter.py)")
    print("=" * 55 + "\n")
    try:
        test_fonctions_exposees()
        test_nettoyer_texte()
        test_generer_nom_fichier()
        test_generer_nom_cas_limites()
        test_generer_pdf_bytes()
        test_pdf_mode_degrade()
        test_pdf_plusieurs_pays()
        test_result_display_modifie()
        test_requirements_contient_fpdf2()
        print("=" * 55)
        print("  TOUS LES TESTS PASSES")
        print("  Tests 5-7 actifs apres : pip install fpdf2")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)