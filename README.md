# REasy AI Assistant 🤖

> Assistant IA hors-ligne dédié à la préparation des opérations de paiements internationaux

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)](https://streamlit.io/)
[![Mistral](https://img.shields.io/badge/LLM-Mistral%20via%20Ollama-orange)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Description

REasy AI Assistant est un prototype fonctionnel d'assistant basé sur l'intelligence artificielle générative, conçu pour accompagner les équipes financières dans la **préparation des opérations de paiements internationaux**.

L'application fonctionne entièrement **hors-ligne** grâce à l'intégration de Mistral via Ollama, garantissant la confidentialité des données sensibles.

### Ce que fait l'assistant

- Guide l'utilisateur à travers **12 questions structurées** couvrant tous les aspects d'une opération de paiement international
- Génère automatiquement un **résumé professionnel** de l'opération
- Produit une **checklist personnalisée** des documents requis selon le pays du fournisseur
- Exporte les résultats en **PDF** prêt à l'emploi
- Conserve un **historique des simulations** effectuées

---

## Technologies utilisées

| Composant | Technologie |
|-----------|-------------|
| Interface graphique | Streamlit |
| Modèle de langage | Mistral 7B (via Ollama) |
| Export PDF | ReportLab / FPDF |
| Langage | Python 3.10+ |
| Données pays | JSON (country_rules.json) |

---

## Architecture du projet

```
REasy_AI_Assistant/
├── app.py                        # Point d'entrée Streamlit
├── Config/
│   ├── prompts.py                # Prompts système pour le LLM
│   └── settings.py               # Configuration globale
├── core/
│   ├── checklist_generator.py    # Génération de checklists par pays
│   ├── logic.py                  # Logique métier principale
│   └── summary_generator.py      # Génération des résumés IA
├── Data/
│   ├── country_rules.json        # Règles documentaires par pays
│   └── questions.json            # Banque de 12 questions structurées
├── llm/
│   ├── llm_client.py             # Client Ollama/Mistral
│   └── prompt_builder.py         # Construction dynamique des prompts
├── models/
│   └── payment_service.py        # Modèles de données
├── services/
│   └── payment_service.py        # Services métier
├── ui/
│   ├── result_display.py         # Affichage des résultats
│   └── chat_interface.py         # Interface de chat
├── utils/
│   ├── validators.py             # Validation des entrées
│   ├── pdf_exporter.py           # Export PDF
│   ├── simulation_store.py       # Historique des simulations
│   └── formatter.py              # Formatage des données
├── docs/
│   └── documentation_utilisateur.md
├── tests/
└── requirements.txt
```

---

## Prérequis

- Python 3.10+
- [Ollama](https://ollama.ai/) installé et en cours d'exécution
- Modèle Mistral téléchargé via Ollama

```bash
# Installer Ollama (https://ollama.ai)
ollama pull mistral
```

---

## Installation

```bash
# 1. Cloner le repository
git clone https://github.com/TON_USERNAME/REasy_AI_Assistant.git
cd REasy_AI_Assistant

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Lancement

```bash
# S'assurer qu'Ollama est lancé, puis :
streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur à l'adresse `http://localhost:8501`

---

## Fonctionnement

```
Démarrage
    │
    ▼
Questionnaire structuré (12 questions)
    │   • Montant et devise
    │   • Pays du fournisseur
    │   • Nature de l'opération
    │   • ...
    ▼
Traitement par Mistral (hors-ligne)
    │
    ├──► Résumé professionnel de l'opération
    └──► Checklist documents personnalisée
              │
              ▼
         Export PDF + Historique
```

---

## Exemple de résultat

L'assistant génère pour chaque simulation :

**Résumé automatique :** Description structurée de l'opération (bénéficiaire, montant, devise, justification économique, risques identifiés)

**Checklist personnalisée :** Liste des documents requis selon la réglementation du pays fournisseur (facture proforma, déclaration douanière, certificats, etc.)

---

## Auteur

Développé dans le cadre d'un projet de prototypage IA appliqué aux opérations financières internationales.

---

## Licence

Ce projet est sous licence MIT — voir le fichier [LICENSE](LICENSE) pour plus de détails.
