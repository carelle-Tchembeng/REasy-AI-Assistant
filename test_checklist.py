import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.checklist_generator import (
    generer_checklist,
    _generer_checklist_base,
    get_infos_pays
)
from models.payment_model import PaymentOperation


def creer_operation_test(pays="Chine") -> PaymentOperation:
    op = PaymentOperation()
    op.nom_entreprise        = "REasy SAS"
    op.pays_acheteur         = "France"
    op.nom_fournisseur       = "Shenzhen Electronics Co."
    op.pays_fournisseur      = pays
    op.type_marchandise      = "Électronique"
    op.description_marchandise = "500 smartphones Android"
    op.montant               = 15000.0
    op.devise                = "USD"
    op.mode_paiement         = "Virement SWIFT"
    return op


def test_checklist_base_contient_documents_communs():
    print("=== Test 1 : documents de base présents pour tous les pays ===")
    op = creer_operation_test("Chine")
    documents = _generer_checklist_base(op)

    noms = [d["nom"] for d in documents]
    assert "Facture commerciale" in noms, "La facture commerciale doit toujours être présente"
    assert "Bon de commande" in noms,     "Le bon de commande doit toujours être présent"
    assert "Contrat commercial" in noms,  "Le contrat commercial doit toujours être présent"

    docs_base = [d for d in documents if d["source"] == "base"]
    print(f"  {len(docs_base)} documents de base présents :")
    for d in docs_base:
        print(f"    - {d['nom']}")
    print("  OK\n")


def test_checklist_base_chine():
    print("=== Test 2 : documents spécifiques à la Chine ===")
    op = creer_operation_test("Chine")
    documents = _generer_checklist_base(op)

    docs_specifiques = [d for d in documents if "chine" in d["source"].lower() or "Chine" in d["source"]]
    noms = [d["nom"] for d in documents]

    assert any("Certificat d'origine" in n for n in noms), \
        "Le certificat d'origine doit être présent pour la Chine"
    assert any("Packing list" in n for n in noms), \
        "La packing list doit être présente pour la Chine"
    assert any("Bill of Lading" in n for n in noms), \
        "Le Bill of Lading doit être présent pour la Chine"

    print(f"  {len(docs_specifiques)} documents spécifiques à la Chine :")
    for d in docs_specifiques:
        statut = "obligatoire" if d["obligatoire"] else "recommandé"
        print(f"    - {d['nom']} ({statut})")
    print("  OK\n")


def test_checklist_base_maroc():
    print("=== Test 3 : documents spécifiques au Maroc ===")
    op = creer_operation_test("Maroc")
    documents = _generer_checklist_base(op)

    noms = [d["nom"] for d in documents]
    assert any("EUR.1" in n or "Form A" in n for n in noms), \
        "Le certificat EUR.1 ou Form A doit être présent pour le Maroc"
    assert any("DUM" in n or "Déclaration unique" in n for n in noms), \
        "La DUM doit être présente pour le Maroc"

    total = len(documents)
    obligatoires = len([d for d in documents if d["obligatoire"]])
    print(f"  {total} documents au total dont {obligatoires} obligatoires pour le Maroc")
    print("  OK\n")


def test_checklist_pays_inconnu():
    print("=== Test 4 : pays non répertorié → règles 'Autre' appliquées ===")
    op = creer_operation_test("Japon")
    documents = _generer_checklist_base(op)

    assert len(documents) > 0, "Des documents doivent être retournés même pour un pays inconnu"
    docs_autre = [d for d in documents if d["source"] == "specifique_autre"]
    assert len(docs_autre) > 0, "Les règles 'Autre' doivent s'appliquer pour un pays inconnu"

    print(f"  Pays 'Japon' non répertorié → {len(docs_autre)} document(s) de la règle 'Autre' appliqué(s)")
    for d in docs_autre:
        print(f"    - {d['nom']}")
    print("  OK\n")


def test_structure_document():
    print("=== Test 5 : structure de chaque document retourné ===")
    op = creer_operation_test("Chine")
    documents = _generer_checklist_base(op)

    champs_requis = {"nom", "description", "obligatoire", "source"}
    for doc in documents:
        manquants = champs_requis - doc.keys()
        assert not manquants, f"Champs manquants dans {doc.get('nom')} : {manquants}"
        assert isinstance(doc["obligatoire"], bool), \
            f"'obligatoire' doit être un booléen pour '{doc['nom']}'"

    print(f"  {len(documents)} documents vérifiés — tous ont les champs {champs_requis}")
    print("  OK\n")


def test_get_infos_pays():
    print("=== Test 6 : get_infos_pays() ===")
    pays_testes = ["Chine", "Maroc", "États-Unis", "Allemagne"]

    for pays in pays_testes:
        infos = get_infos_pays(pays)
        assert "devise_habituelle" in infos
        assert "delai_virement_moyen" in infos
        assert "remarque" in infos
        assert infos["devise_habituelle"] != "N/A", \
            f"La devise habituelle ne doit pas être N/A pour {pays}"
        print(f"  {pays} → délai : {infos['delai_virement_moyen']} | devise : {infos['devise_habituelle']}")

    # Pays inconnu
    infos_inconnu = get_infos_pays("Neptuneland")
    assert infos_inconnu["devise_habituelle"] == "N/A"
    print(f"  Pays inconnu → devise : {infos_inconnu['devise_habituelle']}")
    print("  OK\n")


def test_generer_checklist_structure_retour():
    print("=== Test 7 : generer_checklist() — structure du retour ===")
    op = creer_operation_test("Chine")
    resultat = generer_checklist(op)

    assert "documents" in resultat,      "Clé 'documents' manquante"
    assert "enrichissement" in resultat, "Clé 'enrichissement' manquante"
    assert "pays" in resultat,           "Clé 'pays' manquante"
    assert "mode_degrade" in resultat,   "Clé 'mode_degrade' manquante"

    assert isinstance(resultat["documents"], list), "'documents' doit être une liste"
    assert len(resultat["documents"]) > 0,          "'documents' ne doit pas être vide"
    assert resultat["pays"] == "Chine",              "Le pays doit être 'Chine'"

    print(f"  Structure du retour validée :")
    print(f"    documents      : {len(resultat['documents'])} documents")
    print(f"    enrichissement : {'présent' if resultat['enrichissement'] else 'absent (mode dégradé)'}")
    print(f"    pays           : {resultat['pays']}")
    print(f"    mode_degrade   : {resultat['mode_degrade']}")
    print("  OK\n")


def test_comparaison_pays():
    print("=== Test 8 : comparaison checklist Chine vs Maroc ===")
    op_chine = creer_operation_test("Chine")
    op_maroc = creer_operation_test("Maroc")

    docs_chine = _generer_checklist_base(op_chine)
    docs_maroc = _generer_checklist_base(op_maroc)

    noms_chine = {d["nom"] for d in docs_chine}
    noms_maroc = {d["nom"] for d in docs_maroc}

    communs = noms_chine & noms_maroc
    specifiques_chine = noms_chine - noms_maroc
    specifiques_maroc = noms_maroc - noms_chine

    assert len(specifiques_chine) > 0, "La Chine doit avoir des documents spécifiques"
    assert len(specifiques_maroc) > 0, "Le Maroc doit avoir des documents spécifiques"

    print(f"  Documents communs ({len(communs)}) :")
    for n in sorted(communs):
        print(f"    - {n}")
    print(f"  Spécifiques Chine ({len(specifiques_chine)}) :")
    for n in sorted(specifiques_chine):
        print(f"    - {n}")
    print(f"  Spécifiques Maroc ({len(specifiques_maroc)}) :")
    for n in sorted(specifiques_maroc):
        print(f"    - {n}")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — core/checklist_generator.py")
    print("=" * 55 + "\n")
    try:
        test_checklist_base_contient_documents_communs()
        test_checklist_base_chine()
        test_checklist_base_maroc()
        test_checklist_pays_inconnu()
        test_structure_document()
        test_get_infos_pays()
        test_generer_checklist_structure_retour()
        test_comparaison_pays()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)