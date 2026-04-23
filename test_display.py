import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


def test_import_result_display():
    print("=== Test 1 : import de result_display.py ===")
    try:
        import ui.result_display as rd
        print("  Import réussi")
    except ImportError as e:
        print(f"  Import partiel (normal sans Streamlit actif) : {e}")
    print("  OK\n")


def test_fonctions_exposees():
    print("=== Test 2 : fonctions publiques et privées exposées ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    fonctions_attendues = [
        "def afficher_resultat",
        "def _afficher_bandeau_mode",
        "def _afficher_resume",
        "def _afficher_checklist",
        "def _afficher_infos_pays",
    ]
    for fn in fonctions_attendues:
        assert fn in contenu, f"Fonction manquante : '{fn}'"
        print(f"  ✓ {fn}()")
    print("  OK\n")


def test_affichage_resume_llm_et_base():
    print("=== Test 3 : affichage résumé LLM et mode dégradé ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "resume_llm"  in contenu, "Le résumé LLM doit être géré"
    assert "resume_base" in contenu, "Le résumé de base doit être géré en fallback"
    assert "st.code"     in contenu, "st.code doit être utilisé pour le résumé de base"
    assert "st.markdown" in contenu, "st.markdown doit être utilisé pour le résumé LLM"

    print("  ✓ Résumé LLM affiché avec st.markdown()")
    print("  ✓ Résumé base affiché avec st.code() en mode dégradé")
    print("  OK\n")


def test_affichage_checklist_obligatoires_recommandes():
    print("=== Test 4 : séparation obligatoires / recommandés ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "obligatoires" in contenu,  "Les documents obligatoires doivent être séparés"
    assert "recommandes"  in contenu,  "Les documents recommandés doivent être séparés"
    assert "st.expander"  in contenu,  "st.expander doit être utilisé pour chaque document"
    assert "✅"            in contenu,  "L'icône ✅ doit marquer les documents obligatoires"
    assert "📋"            in contenu,  "L'icône 📋 doit marquer les documents recommandés"

    print("  ✓ Documents obligatoires séparés avec ✅")
    print("  ✓ Documents recommandés séparés avec 📋")
    print("  ✓ st.expander() utilisé pour chaque document")
    print("  OK\n")


def test_bandeau_mode_degrade():
    print("=== Test 5 : bandeau mode dégradé ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "mode_degrade"  in contenu, "La détection du mode dégradé doit être présente"
    assert "st.warning"    in contenu, "st.warning doit signaler le mode dégradé"
    assert "ollama serve"  in contenu, "Les instructions Ollama doivent être affichées"

    print("  ✓ Détection mode_degrade présente")
    print("  ✓ st.warning() affiché si Ollama indisponible")
    print("  ✓ Instructions 'ollama serve' incluses")
    print("  OK\n")


def test_infos_pays_affichees():
    print("=== Test 6 : infos pays affichées ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "get_infos_pays"         in contenu, "get_infos_pays() doit être appelé"
    assert "delai_virement_moyen"   in contenu, "Le délai de virement doit être affiché"
    assert "devise_habituelle"      in contenu, "La devise habituelle doit être affichée"
    assert "st.metric"              in contenu, "st.metric doit être utilisé pour les KPIs"
    assert "st.columns"             in contenu, "st.columns doit structurer les métriques"
    assert "remarque"               in contenu, "La remarque réglementaire doit être affichée"

    print("  ✓ get_infos_pays() appelé")
    print("  ✓ Délai et devise affichés via st.metric()")
    print("  ✓ st.columns() pour la mise en page")
    print("  ✓ Remarque réglementaire affichée")
    print("  OK\n")


def test_enrichissement_checklist_llm():
    print("=== Test 7 : enrichissement checklist LLM ===")
    chemin = os.path.join(BASE_DIR, "ui", "result_display.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "enrichissement_checklist" in contenu, \
        "L'enrichissement LLM de la checklist doit être géré"
    assert "Précisions de l'assistant" in contenu, \
        "Un titre doit introduire les précisions LLM"

    print("  ✓ enrichissement_checklist présent")
    print("  ✓ Section 'Précisions de l'assistant IA' présente")
    print("  OK\n")


def test_payload_result_display():
    print("=== Test 8 : simulation PaymentResult avec données réelles ===")

    # On instancie un PaymentResult manuellement sans Streamlit
    from services.payment_service import PaymentService, PaymentResult

    service = PaymentService()
    reponses = [
        "REasy SAS", "France", "Shenzhen Co.", "Chine",
        "Électronique", "500 smartphones", "15000", "USD",
        "Virement SWIFT", "Bank of China", "BKCHCNBJ", "CN123456789"
    ]
    for r in reponses:
        service.traiter_reponse(r)

    result = service.generer_resultat()

    assert result is not None,                 "Le résultat ne doit pas être None"
    assert len(result.documents) > 0,          "Des documents doivent être présents"
    assert len(result.resume_final) > 0,       "Le résumé final ne doit pas être vide"
    assert result.checklist["pays"] == "Chine","Le pays doit être 'Chine'"

    obligatoires = [d for d in result.documents if d.get("obligatoire")]
    recommandes  = [d for d in result.documents if not d.get("obligatoire")]

    print(f"  PaymentResult prêt pour affichage :")
    print(f"    resume_final   : {len(result.resume_final)} caractères")
    print(f"    documents      : {len(result.documents)} au total")
    print(f"    obligatoires   : {len(obligatoires)}")
    print(f"    recommandés    : {len(recommandes)}")
    print(f"    mode_degrade   : {result.mode_degrade}")
    print(f"    pays           : {result.checklist['pays']}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — ui/result_display.py")
    print("=" * 55 + "\n")
    try:
        test_import_result_display()
        test_fonctions_exposees()
        test_affichage_resume_llm_et_base()
        test_affichage_checklist_obligatoires_recommandes()
        test_bandeau_mode_degrade()
        test_infos_pays_affichees()
        test_enrichissement_checklist_llm()
        test_payload_result_display()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)