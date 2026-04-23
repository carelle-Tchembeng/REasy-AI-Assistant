# Documentation d'utilisation — Assistant IA de simulation de paiement international

## 1. Présentation du projet

Ce prototype a été développé dans le cadre d'un stage chez **REasy SAS**.

L'objectif du projet est de concevoir un **assistant intelligent fonctionnant hors ligne**, capable de guider un utilisateur dans la préparation d'une opération de paiement international.

L'assistant permet de :

- collecter les informations nécessaires à un paiement international
- générer un **résumé structuré de l'opération**
- produire une **checklist des documents nécessaires**
- exporter un **dossier de paiement au format PDF**

Le prototype utilise un **modèle d'intelligence artificielle open source exécuté localement** via Ollama.

---

# 2. Technologies utilisées

Le prototype repose sur les technologies suivantes :

- Python 3.10+
- Streamlit (interface utilisateur)
- Ollama (exécution locale du modèle IA)
- Modèle LLM : Mistral
- ReportLab (génération de PDF)

---

# 3. Prérequis techniques

Avant d'installer le projet, vérifier que les éléments suivants sont installés :

- Python 3.10 ou supérieur
- pip
- Ollama installé sur la machine

Télécharger Ollama :

https://ollama.com

---

# 4. Installation du projet

## 4.1 Cloner ou copier le projet

Placer le dossier du projet sur votre machine.

Exemple :

assistant_ai/

## 4.2 Créer un environnement virtuel

Dans le terminal :

python -m venv venv

Activer l'environnement :

Windows :

venv\Scripts\activate

Mac/Linux :

source venv/bin/activate

---

## 4.3 Installer les dépendances

pip install streamlit requests reportlab

---

# 5. Installation du modèle IA

Le prototype utilise le modèle **Mistral** exécuté via Ollama.

Télécharger le modèle :

ollama pull mistral

Vérifier que le modèle fonctionne :

ollama run mistral

---

# 6. Lancer l'application

Dans le terminal :

streamlit run app.py

L'application s'ouvre automatiquement dans le navigateur.

---

# 7. Utilisation de l'assistant

L'utilisateur est guidé à travers une série de questions :

- montant du paiement
- devise du paiement
- pays du fournisseur
- devise acceptée
- moyen de réception des fonds
- compte REasy du fournisseur
- identifiant de paiement
- numéro de facture
- type de marchandise

Une fois toutes les informations saisies :

1. un résumé structuré de l'opération est généré
2. une checklist des documents nécessaires est affichée
3. l'utilisateur peut exporter le dossier en **PDF**

---

# 8. Scénarios de test réalisés

## Scénario 1 — Paiement vers la Chine

Montant : 15000
Devise : USD
Pays fournisseur : Chine
Marchandise : électronique

Résultat :

- résumé généré par l'IA
- checklist incluant les documents spécifiques à la Chine
- export PDF fonctionnel

---

## Scénario 2 — Paiement vers le Maroc

Montant : 5000
Devise : EUR
Pays fournisseur : Maroc
Marchandise : textile

Résultat :

- checklist adaptée
- génération correcte du résumé

---

## Scénario 3 — Paiement vers les États-Unis

Montant : 80000
Devise : USD
Pays fournisseur : USA
Marchandise : logiciel

Résultat :

- résumé généré correctement
- checklist des documents standards

---

# 9. Architecture du projet

assistant_ai/

config/ → paramètres globaux et prompts
core/ → logique métier principale
data/ → questions et règles documentaires
llm/ → connexion au modèle IA
models/ → structure des données métier
services/ → orchestration des opérations
ui/ → interface Streamlit
utils/ → outils utilitaires (validation, PDF)

---

# 10. Limites du prototype

Ce prototype présente certaines limites :

- base de règles documentaires limitée
- validation simplifiée des données
- modèle IA exécuté localement sans optimisation
- absence d'intégration avec les systèmes réels de REasy

Ces éléments pourraient être améliorés dans une future version du projet.

---

# 11. Perspectives d'amélioration

Améliorations possibles :

- enrichissement des règles documentaires par pays
- détection automatique des risques de paiement
- génération automatique de dossiers complets
- intégration avec les services REasy
- amélioration de l'interface utilisateur

---

# Conclusion

Ce prototype démontre la faisabilité d'un **assistant intelligent permettant d'accompagner les PME dans la préparation de paiements internationaux**, tout en offrant une base technique pouvant être étendue dans les solutions futures proposées par REasy SAS.
