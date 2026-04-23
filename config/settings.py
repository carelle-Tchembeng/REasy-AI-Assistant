import os

# CHEMINS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR             = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR          = os.path.join(BASE_DIR, "outputs")

QUESTIONS_FILE       = os.path.join(DATA_DIR, "questions.json")
COUNTRY_RULES_FILE   = os.path.join(DATA_DIR, "country_rules.json")

# MODÈLE LLM (Ollama + Mistral)

MODEL_NAME           = "mistral"
OLLAMA_HOST          = "http://localhost:11434"
MAX_TOKENS           = 1024
TEMPERATURE          = 0.3        # Faible pour des réponses précises et stables

# APPLICATION

APP_NAME             = "REasy AI Assistant"
APP_VERSION          = "1.0.0"
LANGUE               = "fr"

# SEUILS MÉTIER

MONTANT_MIN          = 1.0
MONTANT_MAX          = 10_000_000
DEVISES_ACCEPTEES    = ["USD", "EUR", "GBP", "CNY", "MAD", "TRY"]