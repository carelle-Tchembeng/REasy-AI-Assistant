import sys
import os
import json
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)


def creer_resultat_test(entreprise="REasy SAS", pays="Chine", montant=15000.0):
    """Cree un PaymentResult sans appeler Ollama."""
    from models.payment_model import PaymentOperation
    from services.payment_service import PaymentResult
    from core.checklist_generator import _generer_checklist_base
    from core.summary_generator import _generer_resume_base

    op = PaymentOperation()
    op.nom_entreprise   = entreprise
    op.pays_acheteur    = "France"
    op.nom_fournisseur  = "Fournisseur Test"
    op.pays_fournisseur = pays
    op.montant          = montant
    op.devise           = "USD"
    op.mode_paiement    = "Virement SWIFT"
    op.type_marchandise = "Electronique"
    op.banque_fournisseur = "Bank of China"
    op.swift_bic        = "BKCHCNBJ"
    op.est_complete     = True

    resume    = {"resume_base": _generer_resume_base(op), "resume_llm": None, "mode_degrade": True}
    documents = _generer_checklist_base(op)
    checklist = {"documents": documents, "enrichissement": None, "pays": pays, "mode_degrade": True}
    return PaymentResult(op, resume, checklist)


def utiliser_fichier_temporaire(func):
    """
    Decorateur : redirige FICHIER_SIMULATIONS vers un fichier temporaire
    pour que les tests ne polluent pas les vraies donnees.
    """
    import utils.simulation_store as store

    def wrapper():
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as f:
            json.dump([], f)
            chemin_tmp = f.name
        chemin_original = store.FICHIER_SIMULATIONS
        store.FICHIER_SIMULATIONS = chemin_tmp
        try:
            func()
        finally:
            store.FICHIER_SIMULATIONS = chemin_original
            if os.path.exists(chemin_tmp):
                os.remove(chemin_tmp)
    return wrapper


@utiliser_fichier_temporaire
def test_sauvegarder_simulation():
    print("=== Test 1 : sauvegarder_simulation() ===")
    from utils.simulation_store import sauvegarder_simulation, charger_simulations

    resultat = creer_resultat_test()
    entree   = sauvegarder_simulation(resultat)

    assert "id"               in entree, "L'entree doit avoir un id"
    assert "date"             in entree, "L'entree doit avoir une date"
    assert entree["entreprise"]       == "REasy SAS", "Entreprise incorrecte"
    assert entree["pays_fournisseur"] == "Chine",     "Pays incorrect"
    assert entree["montant"]          == 15000.0,     "Montant incorrect"
    assert entree["devise"]           == "USD",       "Devise incorrecte"
    assert entree["nb_documents"]     > 0,            "Aucun document"

    simulations = charger_simulations()
    assert len(simulations) == 1, "Une simulation doit etre sauvegardee"

    print(f"  Simulation sauvegardee : id={entree['id']}")
    print(f"  Entreprise : {entree['entreprise']}")
    print(f"  Pays       : {entree['pays_fournisseur']}")
    print(f"  Montant    : {entree['montant']} {entree['devise']}")
    print(f"  Documents  : {entree['nb_documents']}")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_charger_simulations_vide():
    print("=== Test 2 : charger_simulations() - fichier vide ===")
    from utils.simulation_store import charger_simulations

    simulations = charger_simulations()
    assert isinstance(simulations, list), "Doit retourner une liste"
    assert len(simulations) == 0,         "Doit etre vide"

    print(f"  Liste vide retournee : {simulations}")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_charger_plusieurs_simulations():
    print("=== Test 3 : sauvegarder et charger plusieurs simulations ===")
    from utils.simulation_store import sauvegarder_simulation, charger_simulations

    cas = [
        ("REasy SAS",      "Chine",         15000.0),
        ("PME Dupont",     "Maroc",          8500.0),
        ("Industrie SARL", "Etats-Unis",    75000.0),
    ]
    for entreprise, pays, montant in cas:
        sauvegarder_simulation(creer_resultat_test(entreprise, pays, montant))

    simulations = charger_simulations()
    assert len(simulations) == 3, f"Attendu 3, obtenu {len(simulations)}"

    entreprises = [s["entreprise"] for s in simulations]
    assert "REasy SAS"      in entreprises
    assert "PME Dupont"     in entreprises
    assert "Industrie SARL" in entreprises

    print(f"  {len(simulations)} simulations sauvegardees et relues :")
    for s in simulations:
        print(f"    - {s['entreprise']} / {s['pays_fournisseur']} / {s['montant']} {s['devise']}")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_supprimer_simulation():
    print("=== Test 4 : supprimer_simulation() ===")
    from utils.simulation_store import sauvegarder_simulation, charger_simulations, supprimer_simulation

    e1 = sauvegarder_simulation(creer_resultat_test("REasy SAS", "Chine",  15000.0))
    e2 = sauvegarder_simulation(creer_resultat_test("PME Dupont", "Maroc",  8500.0))

    assert len(charger_simulations()) == 2

    ok = supprimer_simulation(e1["id"])
    assert ok, "La suppression doit retourner True"

    simulations = charger_simulations()
    assert len(simulations) == 1, "Il doit rester 1 simulation"
    assert simulations[0]["entreprise"] == "PME Dupont"

    # Suppression id inexistant
    ok_faux = supprimer_simulation("id_inexistant_999")
    assert not ok_faux, "Doit retourner False si id inexistant"

    print(f"  Simulation {e1['id']} supprimee")
    print(f"  Reste : {simulations[0]['entreprise']}")
    print(f"  ID inexistant -> False")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_effacer_historique():
    print("=== Test 5 : effacer_historique() ===")
    from utils.simulation_store import sauvegarder_simulation, charger_simulations, effacer_historique

    for i in range(4):
        sauvegarder_simulation(creer_resultat_test(f"Entreprise {i}", "Chine", 1000.0 * i))

    assert len(charger_simulations()) == 4

    nb = effacer_historique()
    assert nb == 4,                        "Doit retourner le nombre supprime"
    assert len(charger_simulations()) == 0,"La liste doit etre vide apres effacement"

    print(f"  {nb} simulations effacees")
    print(f"  Liste apres effacement : {charger_simulations()}")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_get_stats():
    print("=== Test 6 : get_stats() ===")
    from utils.simulation_store import sauvegarder_simulation, get_stats

    # Stats sur liste vide
    stats_vide = get_stats()
    assert stats_vide["total"] == 0
    print(f"  Stats vides : {stats_vide}")

    # Ajouter des simulations
    sauvegarder_simulation(creer_resultat_test("REasy SAS",  "Chine",  15000.0))
    sauvegarder_simulation(creer_resultat_test("PME Dupont", "Chine",   8500.0))
    sauvegarder_simulation(creer_resultat_test("Industrie",  "Maroc",   5000.0))

    stats = get_stats()
    assert stats["total"]          == 3
    assert stats["pays"]["Chine"]  == 2
    assert stats["pays"]["Maroc"]  == 1
    assert stats["montant_total"]  == 28500.0

    print(f"  Total         : {stats['total']}")
    print(f"  Pays          : {stats['pays']}")
    print(f"  Montant total : {stats['montant_total']:,.0f}")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_construire_entree():
    print("=== Test 7 : _construire_entree() - structure complete ===")
    from utils.simulation_store import _construire_entree

    resultat = creer_resultat_test()
    entree   = _construire_entree(resultat)

    champs_requis = [
        "id", "date", "entreprise", "pays_acheteur", "fournisseur",
        "pays_fournisseur", "montant", "devise", "mode_paiement",
        "type_marchandise", "banque", "swift_bic",
        "nb_documents", "mode_degrade", "resume_base"
    ]
    for champ in champs_requis:
        assert champ in entree, f"Champ manquant : '{champ}'"
        print(f"  v {champ} = {str(entree[champ])[:40]}")
    print("  OK\n")


@utiliser_fichier_temporaire
def test_persistance_json():
    print("=== Test 8 : persistance JSON verifiee ===")
    from utils.simulation_store import sauvegarder_simulation, FICHIER_SIMULATIONS
    import utils.simulation_store as store

    resultat = creer_resultat_test("REasy SAS", "Chine", 15000.0)
    sauvegarder_simulation(resultat)

    # Relire directement le fichier JSON
    with open(store.FICHIER_SIMULATIONS, encoding="utf-8") as f:
        donnees = json.load(f)

    assert isinstance(donnees, list),          "Le JSON doit etre une liste"
    assert len(donnees) == 1,                  "Une entree doit etre dans le fichier"
    assert donnees[0]["entreprise"] == "REasy SAS"
    assert donnees[0]["montant"]    == 15000.0

    print(f"  Fichier JSON lu directement : {len(donnees)} entree(s)")
    print(f"  Contenu : {donnees[0]['entreprise']} / {donnees[0]['montant']}")
    print("  OK\n")


def test_chat_interface_modifie():
    print("=== Test 9 : chat_interface.py modifie avec onglet historique ===")
    chemin = os.path.join(BASE_DIR, "ui", "chat_interface.py")
    with open(chemin, encoding="utf-8") as f:
        contenu = f.read()

    verifications = [
        ("def afficher_onglet_historique",  "Fonction afficher_onglet_historique()"),
        ("def _afficher_carte_simulation",  "Fonction _afficher_carte_simulation()"),
        ("charger_simulations",             "Appel charger_simulations()"),
        ("supprimer_simulation",            "Appel supprimer_simulation()"),
        ("effacer_historique",              "Appel effacer_historique()"),
        ("onglet",                          "Gestion des onglets"),
        ("Historique",                      "Bouton Historique dans sidebar"),
    ]
    for code, description in verifications:
        assert code in contenu, f"Manquant : {description}"
        print(f"  v {description}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS - Sauvegarde des simulations")
    print("=" * 55 + "\n")
    try:
        test_sauvegarder_simulation()
        test_charger_simulations_vide()
        test_charger_plusieurs_simulations()
        test_supprimer_simulation()
        test_effacer_historique()
        test_get_stats()
        test_construire_entree()
        test_persistance_json()
        test_chat_interface_modifie()
        print("=" * 55)
        print("  TOUS LES TESTS PASSES")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)