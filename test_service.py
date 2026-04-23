import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.payment_service import PaymentService, PaymentResult


REPONSES_COMPLETES = [
    "REasy SAS",         # nom_entreprise
    "France",            # pays_acheteur
    "Shenzhen Co.",      # nom_fournisseur
    "Chine",             # pays_fournisseur
    "Électronique",      # type_marchandise
    "500 smartphones",   # description_marchandise
    "15000",             # montant
    "USD",               # devise
    "Virement SWIFT",    # mode_paiement
    "Bank of China",     # banque_fournisseur
    "BKCHCNBJ",         # swift_bic
    "CN1234567890",      # iban_fournisseur
]


def test_initialisation():
    print("=== Test 1 : initialisation du service ===")
    service = PaymentService()

    assert service.operation is not None,  "L'opération doit être initialisée"
    assert service.manager is not None,    "Le manager doit être initialisé"
    assert not service.is_complete(),      "Le questionnaire ne doit pas être complet au départ"

    question = service.get_question_courante()
    assert question is not None,           "La première question doit être disponible"

    print(f"  Service initialisé")
    print(f"  Première question : '{question['texte']}'")
    print(f"  is_complete()     : {service.is_complete()}")
    print("  OK\n")


def test_traiter_reponse_valide():
    print("=== Test 2 : traiter_reponse() — réponse valide ===")
    service = PaymentService()

    resultat = service.traiter_reponse("REasy SAS")

    assert resultat["succes"],          "Une réponse valide doit retourner succes=True"
    assert resultat["erreur"] == "",    "Pas d'erreur pour une réponse valide"
    assert not resultat["complete"],    "Le questionnaire ne doit pas être complet après Q1"
    assert service.operation.nom_entreprise == "REasy SAS", \
        "La réponse doit être enregistrée dans l'opération"

    print(f"  Réponse 'REasy SAS' → succes={resultat['succes']}, erreur='{resultat['erreur']}'")
    print(f"  op.nom_entreprise = '{service.operation.nom_entreprise}'")
    print("  OK\n")


def test_traiter_reponse_invalide():
    print("=== Test 3 : traiter_reponse() — réponse invalide ===")
    service = PaymentService()

    # Q1 est obligatoire — réponse vide doit être rejetée
    resultat = service.traiter_reponse("")
    assert not resultat["succes"],      "Une réponse vide doit être rejetée"
    assert resultat["erreur"] != "",    "Un message d'erreur doit être retourné"
    assert service.manager.index_courant == 0, \
        "L'index ne doit pas avancer après une réponse invalide"

    print(f"  Réponse vide → succes={resultat['succes']}")
    print(f"  Message erreur : '{resultat['erreur']}'")
    print("  OK\n")


def test_traiter_montant_invalide():
    print("=== Test 4 : traiter_reponse() — montant invalide ===")
    service = PaymentService()

    # Avancer jusqu'à la question montant (Q7)
    for reponse in REPONSES_COMPLETES[:6]:
        service.traiter_reponse(reponse)

    # Tenter un montant invalide
    resultat = service.traiter_reponse("abc")
    assert not resultat["succes"], "Un montant invalide doit être rejeté"
    print(f"  Montant 'abc' → rejeté : {resultat['erreur']}")

    # Tenter un montant négatif
    resultat = service.traiter_reponse("-500")
    assert not resultat["succes"], "Un montant négatif doit être rejeté"
    print(f"  Montant '-500' → rejeté : {resultat['erreur']}")

    # Montant valide
    resultat = service.traiter_reponse("15000")
    assert resultat["succes"], "Un montant valide doit être accepté"
    print(f"  Montant '15000' → accepté")
    print("  OK\n")


def test_flux_complet():
    print("=== Test 5 : flux complet de bout en bout ===")
    service = PaymentService()

    for i, reponse in enumerate(REPONSES_COMPLETES):
        question = service.get_question_courante()
        assert question is not None, f"Question {i+1} ne doit pas être None"
        resultat = service.traiter_reponse(reponse)
        assert resultat["succes"], \
            f"Réponse '{reponse}' refusée à Q{i+1} : {resultat['erreur']}"

    assert service.is_complete(), "Le questionnaire doit être complet"
    assert service.operation.est_complete, "op.est_complete doit être True"
    assert service.get_question_courante() is None, \
        "get_question_courante() doit retourner None en fin de flux"

    print(f"  {len(REPONSES_COMPLETES)} réponses traitées sans erreur")
    print(f"  is_complete()        : {service.is_complete()}")
    print(f"  op.est_complete      : {service.operation.est_complete}")
    print(f"  op.nom_entreprise    : {service.operation.nom_entreprise}")
    print(f"  op.pays_fournisseur  : {service.operation.pays_fournisseur}")
    print(f"  op.montant           : {service.operation.montant} {service.operation.devise}")
    print("  OK\n")


def test_generer_resultat():
    print("=== Test 6 : generer_resultat() — structure du PaymentResult ===")
    service = PaymentService()
    for reponse in REPONSES_COMPLETES:
        service.traiter_reponse(reponse)

    resultat = service.generer_resultat()

    assert resultat is not None,                    "Le résultat ne doit pas être None"
    assert isinstance(resultat, PaymentResult),     "Doit retourner un PaymentResult"
    assert isinstance(resultat.resume_final, str),  "resume_final doit être une chaîne"
    assert len(resultat.resume_final) > 0,          "resume_final ne doit pas être vide"
    assert isinstance(resultat.documents, list),    "documents doit être une liste"
    assert len(resultat.documents) > 0,             "La liste de documents ne doit pas être vide"
    assert isinstance(resultat.mode_degrade, bool), "mode_degrade doit être un booléen"

    print(f"  PaymentResult généré :")
    print(f"    resume_final         : {len(resultat.resume_final)} caractères")
    print(f"    documents            : {len(resultat.documents)} documents")
    print(f"    enrichissement       : {'présent' if resultat.enrichissement_checklist else 'absent'}")
    print(f"    mode_degrade         : {resultat.mode_degrade}")
    print(f"    str(result)          : {resultat}")
    print("  OK\n")


def test_generer_resultat_sans_donnees():
    print("=== Test 7 : generer_resultat() sans données suffisantes ===")
    service = PaymentService()

    # Sans répondre aux questions — l'opération n'est pas prête
    resultat = service.generer_resultat()
    assert resultat is None, \
        "generer_resultat() doit retourner None si l'opération n'est pas prête"

    print(f"  Sans données → generer_resultat() retourne None")
    print("  OK\n")


def test_get_infos_pays():
    print("=== Test 8 : get_infos_pays() via le service ===")
    service = PaymentService()

    # Sans pays renseigné
    infos_vides = service.get_infos_pays()
    assert infos_vides == {}, "Sans pays renseigné, get_infos_pays() doit retourner {}"
    print(f"  Sans pays → {infos_vides}")

    # Avec pays renseigné après réponses
    for reponse in REPONSES_COMPLETES[:4]:
        service.traiter_reponse(reponse)

    infos = service.get_infos_pays()
    assert "delai_virement_moyen" in infos, "Les infos pays doivent contenir le délai"
    assert "remarque" in infos,             "Les infos pays doivent contenir la remarque"
    print(f"  Pays 'Chine' → délai : {infos['delai_virement_moyen']}")
    print(f"  Remarque : {infos['remarque'][:80]}...")
    print("  OK\n")


def test_reinitialiser():
    print("=== Test 9 : reinitialiser() ===")
    service = PaymentService()

    for reponse in REPONSES_COMPLETES[:5]:
        service.traiter_reponse(reponse)

    assert service.manager.index_courant == 5
    assert service.operation.nom_entreprise == "REasy SAS"

    service.reinitialiser()

    assert service.manager.index_courant == 0, \
        "L'index doit revenir à 0 après réinitialisation"
    assert service.operation.nom_entreprise is None, \
        "L'opération doit être réinitialisée"
    assert not service.is_complete(), \
        "Le questionnaire ne doit plus être complet après réinitialisation"

    print(f"  Après 5 réponses puis reinitialiser() :")
    print(f"    index_courant      : {service.manager.index_courant}")
    print(f"    nom_entreprise     : {service.operation.nom_entreprise}")
    print(f"    is_complete()      : {service.is_complete()}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — services/payment_service.py")
    print("=" * 55 + "\n")
    try:
        test_initialisation()
        test_traiter_reponse_valide()
        test_traiter_reponse_invalide()
        test_traiter_montant_invalide()
        test_flux_complet()
        test_generer_resultat()
        test_generer_resultat_sans_donnees()
        test_get_infos_pays()
        test_reinitialiser()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)