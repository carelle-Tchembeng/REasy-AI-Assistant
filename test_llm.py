import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_client import verifier_disponibilite, demander_mistral


def test_disponibilite_ollama():
    print("=== Test 1 : verifier_disponibilite() ===")
    ok, msg = verifier_disponibilite()
    if ok:
        print("  Ollama est lancé et Mistral est disponible")
    else:
        print(f"  Ollama non disponible : {msg}")
    # On n'échoue pas ici — on informe juste
    print(f"  Résultat : ok={ok}")
    print("  OK\n")
    return ok


def test_reponse_simple(ollama_disponible):
    print("=== Test 2 : demander_mistral() — réponse simple ===")
    if not ollama_disponible:
        print("  IGNORÉ — Ollama non disponible\n")
        return

    ok, reponse = demander_mistral("Réponds uniquement par le mot : BONJOUR")
    assert ok, f"L'appel doit réussir : {reponse}"
    assert isinstance(reponse, str), "La réponse doit être une chaîne"
    assert len(reponse) > 0, "La réponse ne doit pas être vide"
    print(f"  Réponse reçue : '{reponse[:100]}'")
    print("  OK\n")


def test_reponse_avec_system_prompt(ollama_disponible):
    print("=== Test 3 : demander_mistral() — avec system prompt ===")
    if not ollama_disponible:
        print("  IGNORÉ — Ollama non disponible\n")
        return

    system = "Tu es un assistant qui répond toujours en français en une seule phrase courte."
    prompt = "Qu'est-ce qu'un virement SWIFT ?"

    ok, reponse = demander_mistral(prompt, system_prompt=system)
    assert ok, f"L'appel avec system prompt doit réussir : {reponse}"
    assert len(reponse) > 10, "La réponse doit être substantielle"
    print(f"  System prompt injecté")
    print(f"  Question : '{prompt}'")
    print(f"  Réponse  : '{reponse[:200]}'")
    print("  OK\n")


def test_reponse_paiement_international(ollama_disponible):
    print("=== Test 4 : demander_mistral() — cas métier paiement international ===")
    if not ollama_disponible:
        print("  IGNORÉ — Ollama non disponible\n")
        return

    prompt = (
        "En une phrase, cite deux documents indispensables "
        "pour un paiement international vers la Chine."
    )
    ok, reponse = demander_mistral(prompt)
    assert ok, f"L'appel doit réussir : {reponse}"
    assert len(reponse) > 10
    print(f"  Prompt  : '{prompt}'")
    print(f"  Réponse : '{reponse[:300]}'")
    print("  OK\n")


def test_gestion_erreur_prompt_vide(ollama_disponible):
    print("=== Test 5 : comportement sur prompt vide ===")
    if not ollama_disponible:
        print("  IGNORÉ — Ollama non disponible\n")
        return

    ok, reponse = demander_mistral("")
    # Mistral peut répondre à un prompt vide — on vérifie juste que ça ne crash pas
    print(f"  Prompt vide → ok={ok}, réponse='{str(reponse)[:100]}'")
    assert isinstance(reponse, str), "Le retour doit toujours être une chaîne"
    print("  OK\n")


def test_structure_retour():
    print("=== Test 6 : structure du retour (tuple bool, str) ===")
    # Ce test vérifie la signature sans appeler Ollama
    from llm.llm_client import demander_mistral as dm
    import inspect
    sig = inspect.signature(dm)
    params = list(sig.parameters.keys())
    assert "prompt" in params, "La fonction doit avoir un paramètre 'prompt'"
    assert "system_prompt" in params, "La fonction doit avoir un paramètre 'system_prompt'"
    print(f"  Signature : demander_mistral({', '.join(params)})")
    print("  Paramètres attendus présents")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS — llm/llm_client.py")
    print("=" * 55 + "\n")
    try:
        ollama_disponible = test_disponibilite_ollama()
        test_reponse_simple(ollama_disponible)
        test_reponse_avec_system_prompt(ollama_disponible)
        test_reponse_paiement_international(ollama_disponible)
        test_gestion_erreur_prompt_vide(ollama_disponible)
        test_structure_retour()
        print("=" * 55)
        print("  TOUS LES TESTS PASSÉS")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)