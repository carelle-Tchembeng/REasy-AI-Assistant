import json
import sys
import os

RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "country_rules.json")
QUESTIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "questions.json")


def test_chargement():
    print("=== Test 1 : chargement du fichier ===")
    with open(RULES_PATH, encoding="utf-8") as f:
        rules = json.load(f)
    assert len(rules) > 0, "Le fichier est vide"
    pays = [k for k in rules.keys() if not k.startswith("_")]
    print(f"  {len(pays)} pays chargés : {pays}")
    print("  OK\n")
    return rules


def test_documents_base(rules):
    print("=== Test 2 : présence des documents de base ===")
    assert "_documents_base" in rules, "Clé '_documents_base' manquante"
    docs_base = rules["_documents_base"]["documents"]
    assert len(docs_base) > 0, "Aucun document de base défini"
    obligatoires = [d["nom"] for d in docs_base if d["obligatoire"]]
    print(f"  {len(docs_base)} documents de base dont {len(obligatoires)} obligatoires :")
    for nom in obligatoires:
        print(f"    - {nom}")
    print("  OK\n")


def test_structure_par_pays(rules):
    print("=== Test 3 : structure de chaque pays ===")
    champs_requis = {"devise_habituelle", "delai_virement_moyen", "remarque", "documents_specifiques"}
    pays_list = [k for k in rules.keys() if not k.startswith("_")]
    for pays in pays_list:
        manquants = champs_requis - rules[pays].keys()
        assert not manquants, f"Champs manquants pour '{pays}' : {manquants}"
        docs = rules[pays]["documents_specifiques"]
        assert isinstance(docs, list), f"'documents_specifiques' doit être une liste pour '{pays}'"
        assert len(docs) > 0, f"Aucun document spécifique pour '{pays}'"
        print(f"  {pays} → {len(docs)} documents spécifiques")
    print("  OK\n")


def test_structure_documents(rules):
    print("=== Test 4 : structure de chaque document spécifique ===")
    champs_doc = {"nom", "description", "obligatoire"}
    pays_list = [k for k in rules.keys() if not k.startswith("_")]
    for pays in pays_list:
        for doc in rules[pays]["documents_specifiques"]:
            manquants = champs_doc - doc.keys()
            assert not manquants, \
                f"Champs manquants dans un document de '{pays}' : {manquants}"
            assert isinstance(doc["obligatoire"], bool), \
                f"'obligatoire' doit être un booléen pour '{doc['nom']}' ({pays})"
    print(f"  Tous les documents ont les champs : {champs_doc}")
    print("  OK\n")


def test_correspondance_questions(rules):
    print("=== Test 5 : correspondance avec les options de questions.json ===")
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        questions = json.load(f)
    options_pays = next(
        q["options"] for q in questions if q["id"] == "pays_fournisseur"
    )
    pays_rules = set(k for k in rules.keys() if not k.startswith("_"))
    print(f"  Options dans questions.json : {options_pays}")
    print(f"  Pays dans country_rules.json : {sorted(pays_rules)}")
    for option in options_pays:
        assert option in pays_rules, \
            f"Le pays '{option}' est dans questions.json mais absent de country_rules.json"
    print("  Tous les pays de questions.json sont couverts dans country_rules.json")
    print("  OK\n")


def test_acces_par_pays(rules):
    print("=== Test 6 : accès direct aux documents d'un pays ===")
    pays_test = ["Chine", "Maroc", "États-Unis"]
    for pays in pays_test:
        docs = rules[pays]["documents_specifiques"]
        obligatoires = [d["nom"] for d in docs if d["obligatoire"]]
        print(f"  {pays} → {len(obligatoires)} doc(s) obligatoire(s) :")
        for nom in obligatoires:
            print(f"    - {nom}")
    print("  OK\n")


def test_remarques_non_vides(rules):
    print("=== Test 7 : remarques et délais renseignés ===")
    pays_list = [k for k in rules.keys() if not k.startswith("_")]
    for pays in pays_list:
        assert rules[pays]["remarque"].strip(), f"Remarque vide pour '{pays}'"
        assert rules[pays]["delai_virement_moyen"].strip(), f"Délai vide pour '{pays}'"
        print(f"  {pays} → délai : {rules[pays]['delai_virement_moyen']}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — data/country_rules.json")
    print("=" * 55 + "\n")
    try:
        rules = test_chargement()
        test_documents_base(rules)
        test_structure_par_pays(rules)
        test_structure_documents(rules)
        test_correspondance_questions(rules)
        test_acces_par_pays(rules)
        test_remarques_non_vides(rules)
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)