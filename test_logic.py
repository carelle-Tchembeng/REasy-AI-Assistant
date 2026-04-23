import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logic import ConversationManager
from models.payment_model import PaymentOperation


def test_chargement_questions():
    print("=== Test 1 : chargement des questions au démarrage ===")
    op = PaymentOperation()
    manager = ConversationManager(op)
    assert len(manager.questions) > 0, "Aucune question chargée"
    assert manager.questions[0]["ordre"] == 1, "La première question doit avoir l'ordre 1"
    print(f"  {len(manager.questions)} questions chargées et triées par ordre")
    print(f"  Première question : '{manager.questions[0]['texte']}'")
    print("  OK\n")


def test_get_question_courante():
    print("=== Test 2 : get_question_courante() ===")
    op = PaymentOperation()
    manager = ConversationManager(op)
    question = manager.get_question_courante()
    assert question is not None, "La première question ne doit pas être None"
    assert "texte" in question, "La question doit avoir un champ 'texte'"
    assert "type" in question, "La question doit avoir un champ 'type'"
    print(f"  Question courante (index 0) : '{question['texte']}'")
    print(f"  Type : {question['type']} | Champ modèle : {question['champ_modele']}")
    print("  OK\n")


def test_enregistrer_reponse_texte():
    print("=== Test 3 : enregistrement d'une réponse texte ===")
    op = PaymentOperation()
    manager = ConversationManager(op)

    # Question 1 : nom_entreprise (texte_libre)
    succes = manager.enregistrer_reponse("REasy SAS")
    assert succes, "L'enregistrement doit retourner True"
    assert op.nom_entreprise == "REasy SAS", \
        f"Valeur attendue 'REasy SAS', obtenu '{op.nom_entreprise}'"
    assert manager.index_courant == 1, "L'index doit avancer à 1 après la première réponse"
    print(f"  Réponse enregistrée → op.nom_entreprise = '{op.nom_entreprise}'")
    print(f"  Index courant : {manager.index_courant}")
    print("  OK\n")


def test_enregistrer_reponse_nombre():
    print("=== Test 4 : enregistrement d'une réponse nombre ===")
    op = PaymentOperation()
    manager = ConversationManager(op)

    # Avancer jusqu'à la question montant (ordre 7)
    reponses = [
        "REasy SAS",        # nom_entreprise
        "France",           # pays_acheteur
        "Shenzhen Co.",     # nom_fournisseur
        "Chine",            # pays_fournisseur
        "Electronique",     # type_marchandise
        "500 smartphones",  # description_marchandise
    ]
    for r in reponses:
        manager.enregistrer_reponse(r)

    # Question 7 : montant (nombre)
    manager.enregistrer_reponse("15000")
    assert op.montant == 15000.0, f"Montant attendu 15000.0, obtenu {op.montant}"
    print(f"  Réponse '15000' convertie → op.montant = {op.montant} ({type(op.montant).__name__})")

    # Test avec virgule et espaces
    op2 = PaymentOperation()
    manager2 = ConversationManager(op2)
    for r in reponses:
        manager2.enregistrer_reponse(r)
    manager2.enregistrer_reponse("15 000,50")
    assert op2.montant == 15000.50, f"Montant attendu 15000.50, obtenu {op2.montant}"
    print(f"  Réponse '15 000,50' convertie → op2.montant = {op2.montant}")
    print("  OK\n")


def test_progression():
    print("=== Test 5 : get_progression() ===")
    op = PaymentOperation()
    manager = ConversationManager(op)
    total = len(manager.questions)

    prog = manager.get_progression()
    assert prog["etape_courante"] == 1
    assert prog["total"] == total
    assert prog["pourcentage"] == 0
    print(f"  Début     → étape {prog['etape_courante']}/{prog['total']} ({prog['pourcentage']}%)")

    manager.enregistrer_reponse("REasy SAS")
    prog = manager.get_progression()
    print(f"  Après Q1  → étape {prog['etape_courante']}/{prog['total']} ({prog['pourcentage']}%)")
    print("  OK\n")


def test_is_complete():
    print("=== Test 6 : is_complete() et est_complete sur le modèle ===")
    op = PaymentOperation()
    manager = ConversationManager(op)

    assert not manager.is_complete(), "Ne doit pas être complet au départ"
    assert not op.est_complete, "op.est_complete doit être False au départ"

    # Répondre à toutes les questions
    reponses_completes = [
        "REasy SAS", "France", "Shenzhen Co.", "Chine",
        "Electronique", "500 smartphones", "15000", "USD",
        "Virement SWIFT", "Bank of China", "BKCHCNBJ", "CN123456789"
    ]
    for r in reponses_completes:
        manager.enregistrer_reponse(r)

    assert manager.is_complete(), "Doit être complet après toutes les réponses"
    assert op.est_complete, "op.est_complete doit être True après toutes les réponses"
    print(f"  Après {len(reponses_completes)} réponses → is_complete() = {manager.is_complete()}")
    print(f"  op.est_complete = {op.est_complete}")
    print("  OK\n")


def test_flux_complet():
    print("=== Test 7 : simulation d'un flux complet question par question ===")
    op = PaymentOperation()
    manager = ConversationManager(op)

    reponses = [
        "REasy SAS", "France", "Shenzhen Co.", "Chine",
        "Electronique", "500 smartphones", "15000", "USD",
        "Virement SWIFT", "Bank of China", "BKCHCNBJ", "CN123456789"
    ]

    for i, reponse in enumerate(reponses):
        question = manager.get_question_courante()
        assert question is not None, f"Question {i+1} ne doit pas être None"
        manager.enregistrer_reponse(reponse)

    assert manager.get_question_courante() is None, \
        "get_question_courante() doit retourner None en fin de flux"
    assert op.nom_entreprise == "REasy SAS"
    assert op.pays_fournisseur == "Chine"
    assert op.montant == 15000.0
    assert op.devise == "USD"
    print(f"  Flux complet simulé en {len(reponses)} étapes")
    print(f"  op.nom_entreprise  : {op.nom_entreprise}")
    print(f"  op.pays_fournisseur: {op.pays_fournisseur}")
    print(f"  op.montant         : {op.montant} {op.devise}")
    print(f"  op.mode_paiement   : {op.mode_paiement}")
    print("  OK\n")


def test_reinitialiser():
    print("=== Test 8 : reinitialiser() ===")
    op = PaymentOperation()
    manager = ConversationManager(op)
    manager.enregistrer_reponse("REasy SAS")
    manager.enregistrer_reponse("France")
    assert manager.index_courant == 2

    manager.reinitialiser()
    assert manager.index_courant == 0, "L'index doit revenir à 0"
    assert manager.operation.nom_entreprise is None, "Le modèle doit être réinitialisé"
    print(f"  Après réinitialisation → index = {manager.index_courant}")
    print(f"  op.nom_entreprise = {manager.operation.nom_entreprise}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — core/logic.py")
    print("=" * 55 + "\n")
    try:
        test_chargement_questions()
        test_get_question_courante()
        test_enregistrer_reponse_texte()
        test_enregistrer_reponse_nombre()
        test_progression()
        test_is_complete()
        test_flux_complet()
        test_reinitialiser()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)