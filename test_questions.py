import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "questions.json")

def test_chargement():
    print("=== Test 1 : chargement du fichier ===")
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        questions = json.load(f)
    print(f"  {len(questions)} questions chargées")
    assert len(questions) > 0, "Le fichier est vide"
    print("  OK\n")
    return questions

def test_structure(questions):
    print("=== Test 2 : structure de chaque question ===")
    champs_requis = {"id", "ordre", "texte", "type", "champ_modele", "obligatoire"}
    for q in questions:
        manquants = champs_requis - q.keys()
        assert not manquants, f"Champs manquants dans question '{q.get('id')}' : {manquants}"
    print(f"  Toutes les {len(questions)} questions ont les champs requis")
    print("  OK\n")

def test_types_valides(questions):
    print("=== Test 3 : types de réponse valides ===")
    types_autorises = {"texte_libre", "choix_multiple", "nombre"}
    for q in questions:
        assert q["type"] in types_autorises, \
            f"Type invalide '{q['type']}' pour la question '{q['id']}'"
    print(f"  Tous les types sont valides parmi {types_autorises}")
    print("  OK\n")

def test_choix_multiples(questions):
    print("=== Test 4 : questions à choix multiple ont des options ===")
    for q in questions:
        if q["type"] == "choix_multiple":
            assert "options" in q and len(q["options"]) > 0, \
                f"Question '{q['id']}' est choix_multiple mais n'a pas d'options"
            print(f"  '{q['id']}' → {len(q['options'])} options : {q['options']}")
    print("  OK\n")

def test_ordre_et_unicite(questions):
    print("=== Test 5 : ordre séquentiel et IDs uniques ===")
    ordres = [q["ordre"] for q in questions]
    ids = [q["id"] for q in questions]
    assert ordres == sorted(ordres), "Les questions ne sont pas dans l'ordre croissant"
    assert len(ids) == len(set(ids)), f"IDs en doublon détectés : {[i for i in ids if ids.count(i) > 1]}"
    print(f"  Ordre séquentiel de 1 à {max(ordres)} : OK")
    print(f"  {len(ids)} IDs tous uniques : OK")
    print("  OK\n")

def test_correspondance_modele(questions):
    print("=== Test 6 : correspondance avec PaymentOperation ===")
    from models.payment_model import PaymentOperation
    import dataclasses
    champs_modele = {f.name for f in dataclasses.fields(PaymentOperation)}
    for q in questions:
        champ = q["champ_modele"]
        assert champ in champs_modele, \
            f"Le champ '{champ}' (question '{q['id']}') n'existe pas dans PaymentOperation"
    print(f"  Tous les champ_modele correspondent à PaymentOperation")
    print("  OK\n")

def test_affichage_premiere_question(questions):
    print("=== Test 7 : aperçu de la première question ===")
    q = questions[0]
    print(f"  ID       : {q['id']}")
    print(f"  Texte    : {q['texte']}")
    print(f"  Type     : {q['type']}")
    print(f"  Champ    : {q['champ_modele']}")
    print(f"  Exemple  : {q.get('exemple', '—')}")
    print("  OK\n")

if __name__ == "__main__":
    print("=" * 50)
    print("  TESTS — data/questions.json")
    print("=" * 50 + "\n")
    try:
        questions = test_chargement()
        test_structure(questions)
        test_types_valides(questions)
        test_choix_multiples(questions)
        test_ordre_et_unicite(questions)
        test_correspondance_modele(questions)
        test_affichage_premiere_question(questions)
        print("=" * 50)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)