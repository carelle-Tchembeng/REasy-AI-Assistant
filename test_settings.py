import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_settings():
    print("=== Test 1 : import de settings.py ===")
    from config.settings import (
        MODEL_NAME, OLLAMA_HOST, MAX_TOKENS, TEMPERATURE,
        APP_NAME, APP_VERSION, LANGUE,
        BASE_DIR, DATA_DIR, OUTPUTS_DIR,
        QUESTIONS_FILE, COUNTRY_RULES_FILE,
        MONTANT_MIN, MONTANT_MAX, DEVISES_ACCEPTEES
    )
    print(f"  MODEL_NAME        : {MODEL_NAME}")
    print(f"  OLLAMA_HOST       : {OLLAMA_HOST}")
    print(f"  MAX_TOKENS        : {MAX_TOKENS}")
    print(f"  TEMPERATURE       : {TEMPERATURE}")
    print(f"  APP_NAME          : {APP_NAME}")
    print(f"  APP_VERSION       : {APP_VERSION}")
    print(f"  LANGUE            : {LANGUE}")
    print(f"  MONTANT_MIN       : {MONTANT_MIN}")
    print(f"  MONTANT_MAX       : {MONTANT_MAX}")
    print(f"  DEVISES_ACCEPTEES : {DEVISES_ACCEPTEES}")
    print("  OK\n")


def test_valeurs_settings():
    print("=== Test 2 : validité des valeurs de settings.py ===")
    from config.settings import (
        MODEL_NAME, MAX_TOKENS, TEMPERATURE,
        MONTANT_MIN, MONTANT_MAX, DEVISES_ACCEPTEES
    )
    assert MODEL_NAME == "mistral", f"MODEL_NAME incorrect : {MODEL_NAME}"
    assert MAX_TOKENS > 0, "MAX_TOKENS doit être positif"
    assert 0.0 <= TEMPERATURE <= 1.0, "TEMPERATURE doit être entre 0 et 1"
    assert MONTANT_MIN > 0, "MONTANT_MIN doit être positif"
    assert MONTANT_MAX > MONTANT_MIN, "MONTANT_MAX doit etre superieur a MONTANT_MIN"
    assert isinstance(DEVISES_ACCEPTEES, list), "DEVISES_ACCEPTEES doit etre une liste"
    assert len(DEVISES_ACCEPTEES) > 0, "DEVISES_ACCEPTEES ne doit pas etre vide"
    print("  Toutes les valeurs sont valides")
    print("  OK\n")


def test_chemins_existent():
    print("=== Test 3 : existence des chemins critiques ===")
    from config.settings import (
        BASE_DIR, DATA_DIR, OUTPUTS_DIR,
        QUESTIONS_FILE, COUNTRY_RULES_FILE
    )
    chemins = {
        "BASE_DIR"           : BASE_DIR,
        "DATA_DIR"           : DATA_DIR,
        "OUTPUTS_DIR"        : OUTPUTS_DIR,
        "QUESTIONS_FILE"     : QUESTIONS_FILE,
        "COUNTRY_RULES_FILE" : COUNTRY_RULES_FILE,
    }
    for nom, chemin in chemins.items():
        existe = os.path.exists(chemin)
        statut = "OK" if existe else "MANQUANT"
        print(f"  [{statut}]  {nom} -> {chemin}")
        assert existe, f"Chemin manquant : {nom} = {chemin}"
    print("  OK\n")


def test_devises_coherentes():
    print("=== Test 4 : coherence devises settings <-> questions.json ===")
    import json
    from config.settings import DEVISES_ACCEPTEES, QUESTIONS_FILE

    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    options_devises = next(
        q["options"] for q in questions if q["id"] == "devise"
    )
    options_devises_reelles = [d for d in options_devises if d != "Autre"]

    for devise in options_devises_reelles:
        assert devise in DEVISES_ACCEPTEES, \
            f"Devise '{devise}' dans questions.json absente de DEVISES_ACCEPTEES"
    print(f"  Devises dans questions.json : {options_devises_reelles}")
    print(f"  Devises dans settings.py    : {DEVISES_ACCEPTEES}")
    print("  Coherence parfaite")
    print("  OK\n")


def test_import_prompts():
    print("=== Test 5 : import de prompts.py ===")
    from config.prompts import (
        SYSTEM_PROMPT,
        SUMMARY_PROMPT_TEMPLATE,
        CHECKLIST_PROMPT_TEMPLATE
    )
    print(f"  SYSTEM_PROMPT             : {len(SYSTEM_PROMPT)} caracteres")
    print(f"  SUMMARY_PROMPT_TEMPLATE   : {len(SUMMARY_PROMPT_TEMPLATE)} caracteres")
    print(f"  CHECKLIST_PROMPT_TEMPLATE : {len(CHECKLIST_PROMPT_TEMPLATE)} caracteres")
    print("  OK\n")


def test_contenu_prompts():
    print("=== Test 6 : contenu des prompts ===")
    from config.prompts import (
        SYSTEM_PROMPT,
        SUMMARY_PROMPT_TEMPLATE,
        CHECKLIST_PROMPT_TEMPLATE
    )
    assert "REasy" in SYSTEM_PROMPT, "SYSTEM_PROMPT ne mentionne pas REasy"
    assert "francais" in SYSTEM_PROMPT.lower() or "français" in SYSTEM_PROMPT.lower(), \
        "SYSTEM_PROMPT ne precise pas la langue"
    assert "{donnees_operation}" in SUMMARY_PROMPT_TEMPLATE, \
        "SUMMARY_PROMPT_TEMPLATE manque le placeholder {donnees_operation}"
    assert "{donnees_operation}" in CHECKLIST_PROMPT_TEMPLATE, \
        "CHECKLIST_PROMPT_TEMPLATE manque le placeholder {donnees_operation}"
    assert "{checklist_base}" in CHECKLIST_PROMPT_TEMPLATE, \
        "CHECKLIST_PROMPT_TEMPLATE manque le placeholder {checklist_base}"
    print("  SYSTEM_PROMPT         : role et langue presents")
    print("  SUMMARY_PROMPT        : placeholder {donnees_operation} present")
    print("  CHECKLIST_PROMPT      : placeholders {donnees_operation} et {checklist_base} presents")
    print("  OK\n")


def test_injection_template():
    print("=== Test 7 : injection de donnees dans les templates ===")
    from config.prompts import SUMMARY_PROMPT_TEMPLATE, CHECKLIST_PROMPT_TEMPLATE

    donnees_test = """
    - Acheteur     : REasy SAS (France)
    - Fournisseur  : Shenzhen Electronics Co. (Chine)
    - Montant      : 15000 USD
    - Marchandise  : Electronique
    - Mode         : Virement SWIFT
    """

    prompt_summary = SUMMARY_PROMPT_TEMPLATE.format(donnees_operation=donnees_test)
    assert "REasy SAS" in prompt_summary
    assert "15000 USD" in prompt_summary

    checklist_test = "- Facture commerciale\n- Certificat d'origine"
    prompt_checklist = CHECKLIST_PROMPT_TEMPLATE.format(
        donnees_operation=donnees_test,
        checklist_base=checklist_test
    )
    assert "REasy SAS" in prompt_checklist
    assert "Facture commerciale" in prompt_checklist

    print(f"  SUMMARY_PROMPT apres injection   : {len(prompt_summary)} caracteres")
    print(f"  CHECKLIST_PROMPT apres injection : {len(prompt_checklist)} caracteres")
    print("  Injections reussies")
    print("  OK\n")


def test_apercu_system_prompt():
    print("=== Test 8 : apercu du SYSTEM_PROMPT ===")
    from config.prompts import SYSTEM_PROMPT
    lignes = SYSTEM_PROMPT.strip().split("\n")
    for ligne in lignes[:6]:
        print(f"  {ligne}")
    print("  ...")
    print("  OK\n")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTS - config/settings.py + config/prompts.py")
    print("=" * 55 + "\n")
    try:
        test_import_settings()
        test_valeurs_settings()
        test_chemins_existent()
        test_devises_coherentes()
        test_import_prompts()
        test_contenu_prompts()
        test_injection_template()
        test_apercu_system_prompt()
        print("=" * 55)
        print("  TOUS LES TESTS PASSES")
        print("=" * 55)
    except AssertionError as e:
        print(f"\n  ECHEC : {e}")
        sys.exit(1)