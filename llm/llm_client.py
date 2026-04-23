import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import MODEL_NAME, OLLAMA_HOST, MAX_TOKENS, TEMPERATURE


def verifier_disponibilite() -> tuple[bool, str]:
    """
    Vérifie qu'Ollama est lancé et que le modèle Mistral est disponible.
    Retourne (True, "") si tout est ok, (False, message_erreur) sinon.
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, f"Ollama répond mais avec le statut {response.status_code}."

        modeles = [m["name"] for m in response.json().get("models", [])]
        modeles_base = [m.split(":")[0] for m in modeles]

        if MODEL_NAME not in modeles_base:
            return False, (
                f"Le modèle '{MODEL_NAME}' n'est pas disponible. "
                f"Modèles installés : {', '.join(modeles) if modeles else 'aucun'}. "
                f"Lancez : ollama pull {MODEL_NAME}"
            )
        return True, ""

    except requests.exceptions.ConnectionError:
        return False, (
            f"Impossible de joindre Ollama sur {OLLAMA_HOST}. "
            f"Assurez-vous qu'Ollama est lancé avec : ollama serve"
        )
    except requests.exceptions.Timeout:
        return False, "Ollama ne répond pas (timeout). Vérifiez qu'il est bien lancé."


def demander_mistral(prompt: str, system_prompt: str = "") -> tuple[bool, str]:
    """
    Envoie un prompt à Mistral via Ollama et retourne la réponse.
    Retourne (True, reponse) si succès, (False, message_erreur) sinon.
    """
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model"   : MODEL_NAME,
        "messages": messages,
        "stream"  : False,
        "options" : {
            "temperature" : TEMPERATURE,
            "num_predict" : MAX_TOKENS,
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            return False, f"Erreur Ollama (statut {response.status_code}) : {response.text}"

        data = response.json()
        contenu = data.get("message", {}).get("content", "")

        if not contenu.strip():
            return False, "Mistral a retourné une réponse vide."

        return True, contenu.strip()

    except requests.exceptions.ConnectionError:
        return False, (
            "Connexion perdue avec Ollama pendant la génération. "
            "Vérifiez qu'Ollama est toujours actif."
        )
    except requests.exceptions.Timeout:
        return False, (
            "Mistral a mis trop de temps à répondre (timeout 120s). "
            "Essayez avec un prompt plus court."
        )
    except Exception as e:
        return False, f"Erreur inattendue lors de l'appel à Mistral : {str(e)}"