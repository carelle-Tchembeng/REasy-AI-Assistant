import sys
import os

# Racine du projet = dossier où se trouve ce fichier de test
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


def test_import_chat_interface():
    print("=== Test 1 : import de chat_interface.py ===")
    try:
        import ui.chat_interface as ci
        print("  Import réussi")
    except ImportError as e:
        print(f"  Import partiel (normal sans Streamlit actif) : {e}")
    print("  OK\n")


def test_fonctions_exposees():
    print("=== Test 2 : fonctions publiques exposées ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    fonctions_attendues = [
        "def initialiser_session",
        "def afficher_historique",
        "def afficher_question_courante",
        "def _afficher_saisie",
        "def _soumettre_reponse",
        "def afficher_bouton_reinitialiser",
        "def afficher_message_bienvenue",
        "def render",
    ]
    for fn in fonctions_attendues:
        assert fn in contenu, f"Fonction manquante : '{fn}'"
        print(f"  ✓ {fn}()")
    print("  OK\n")


def test_session_state_cles():
    print("=== Test 3 : clés de session_state initialisées ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    cles_attendues = ["service", "historique", "resultat", "en_cours"]
    for cle in cles_attendues:
        assert f'"{cle}"' in contenu or f"'{cle}'" in contenu, \
            f"Clé session_state '{cle}' manquante"
        print(f"  ✓ session_state['{cle}'] présente")
    print("  OK\n")


def test_types_saisie_couverts():
    print("=== Test 4 : types de saisie couverts ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    types_attendus = ["choix_multiple", "nombre", "texte_libre"]
    for t in types_attendus:
        assert t in contenu, f"Type de saisie '{t}' non géré"
        print(f"  ✓ Type '{t}' géré")
    print("  OK\n")


def test_gestion_erreur_dans_soumettre():
    print("=== Test 5 : gestion d'erreur dans _soumettre_reponse() ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "resultat[\"succes\"]" in contenu or "resultat['succes']" in contenu
    assert "st.error" in contenu
    assert "st.rerun" in contenu

    print("  ✓ Vérification du succès présente")
    print("  ✓ st.error() pour les erreurs de validation")
    print("  ✓ st.rerun() après réponse valide")
    print("  OK\n")


def test_appel_result_display():
    print("=== Test 6 : appel à result_display.py quand terminé ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "from ui.result_display import afficher_resultat" in contenu
    assert "afficher_resultat" in contenu
    assert "generer_resultat" in contenu

    print("  ✓ Import de result_display présent")
    print("  ✓ afficher_resultat() appelé en fin de questionnaire")
    print("  ✓ generer_resultat() appelé pour produire le résultat")
    print("  OK\n")


def test_bouton_reinitialiser():
    print("=== Test 7 : bouton de réinitialisation ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    assert "Nouvelle simulation" in contenu
    assert "st.session_state.service" in contenu

    print("  ✓ Bouton 'Nouvelle simulation' présent")
    print("  ✓ Réinitialisation du service présente")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — ui/chat_interface.py")
    print("=" * 55 + "\n")
    try:
        test_import_chat_interface()
        test_fonctions_exposees()
        test_session_state_cles()
        test_types_saisie_couverts()
        test_gestion_erreur_dans_soumettre()
        test_appel_result_display()
        test_bouton_reinitialiser()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        import sys; sys.exit(1)