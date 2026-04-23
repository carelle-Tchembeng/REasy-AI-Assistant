import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.payment_service import PaymentService
from config.settings import APP_NAME


def initialiser_session():
    """Initialise les variables de session Streamlit si elles n'existent pas."""
    if "service"    not in st.session_state:
        st.session_state.service    = PaymentService()
    if "historique" not in st.session_state:
        st.session_state.historique = []
    if "resultat"   not in st.session_state:
        st.session_state.resultat   = None
    if "en_cours"   not in st.session_state:
        st.session_state.en_cours   = True
    if "onglet"     not in st.session_state:
        st.session_state.onglet     = "assistant"


def afficher_historique_chat():
    """Affiche toutes les bulles de conversation de l'historique."""
    for message in st.session_state.historique:
        role    = message["role"]
        contenu = message["contenu"]
        if role == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(contenu)
        else:
            with st.chat_message("user", avatar="👤"):
                st.markdown(contenu)


def afficher_question_courante():
    """Affiche la question courante et le composant de saisie adapte."""
    service  = st.session_state.service
    question = service.get_question_courante()
    if question is None:
        return

    progression = service.get_progression()
    st.progress(
        progression["pourcentage"] / 100,
        text=f"Question {progression['etape_courante']} / {progression['total']}"
    )

    with st.chat_message("assistant", avatar="🤖"):
        mention = "" if question.get("obligatoire") else " *(optionnel)*"
        st.markdown(f"{question['texte']}{mention}")
        if question.get("exemple"):
            st.caption(question["exemple"])

    _afficher_saisie(question)


def _afficher_saisie(question: dict):
    """Affiche le bon composant de saisie selon le type de question."""
    type_question = question["type"]
    cle           = f"saisie_{question['id']}"

    if type_question == "choix_multiple":
        choix = st.radio(
            label      = "Choisissez une option :",
            options    = question.get("options", []),
            key        = f"radio_{cle}",
            horizontal = True,
        )
        if st.button("Confirmer", key=f"btn_{cle}", type="primary"):
            _soumettre_reponse(str(choix), question)
    else:
        valeur = st.text_input(
            label       = "Votre reponse :",
            placeholder = question.get("exemple", ""),
            key         = f"input_{cle}",
        )
        if st.button("Confirmer", key=f"btn_{cle}", type="primary"):
            _soumettre_reponse(valeur, question)


def _soumettre_reponse(reponse: str, question: dict):
    """Valide, enregistre la reponse et fait avancer la conversation."""
    service  = st.session_state.service
    resultat = service.traiter_reponse(reponse)

    if not resultat["succes"]:
        st.error(f" {resultat['erreur']}")
        return

    st.session_state.historique.append({
        "role": "assistant", "contenu": f"**{question['texte']}**"
    })
    st.session_state.historique.append({
        "role": "user", "contenu": reponse
    })

    if resultat["complete"]:
        with st.spinner("Generation du resume et de la checklist..."):
            st.session_state.resultat = service.generer_resultat()
            st.session_state.en_cours = False

    st.rerun()


def afficher_sidebar():
    """Affiche la barre laterale avec navigation et bouton reinitialiser."""
    with st.sidebar:
        st.markdown(f"## {APP_NAME}")
        st.markdown("---")

        # Navigation entre onglets
        st.markdown("### Navigation")
        if st.button(" Assistant", use_container_width=True,
                      type="primary" if st.session_state.onglet == "assistant" else "secondary"):
            st.session_state.onglet = "assistant"
            st.rerun()

        if st.button(" Historique", use_container_width=True,
                      type="primary" if st.session_state.onglet == "historique" else "secondary"):
            st.session_state.onglet = "historique"
            st.rerun()

        st.markdown("---")
        st.markdown("### Actions")
        if st.button(" Nouvelle simulation", use_container_width=True):
            st.session_state.service    = PaymentService()
            st.session_state.historique = []
            st.session_state.resultat   = None
            st.session_state.en_cours   = True
            st.session_state.onglet     = "assistant"
            st.rerun()

        st.markdown("---")
        st.markdown("### A propos")
        st.markdown(
            "Cet assistant vous guide dans la preparation "
            "d'un paiement international etape par etape."
        )


def afficher_message_bienvenue():
    """Affiche le message de bienvenue au debut de la conversation."""
    if not st.session_state.historique:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(
                f" Bonjour ! Je suis **{APP_NAME}**, votre assistant "
                "specialise en paiements internationaux.\n\n"
                "Je vais vous guider a travers une serie de questions pour "
                "preparer votre operation de paiement. "
                "A la fin, je genererai un **resume complet** et une "
                "**checklist des documents** necessaires.\n\n"
                "*Commençons !*"
            )


def afficher_onglet_historique():
    """Affiche l'onglet historique des simulations sauvegardees."""
    from utils.simulation_store import charger_simulations, supprimer_simulation, effacer_historique, get_stats

    st.subheader(" Historique des simulations")

    simulations = charger_simulations()

    if not simulations:
        st.info("Aucune simulation sauvegardee pour l'instant. "
                "Completez une simulation pour la voir apparaitre ici.")
        return

    # Statistiques globales
    stats = get_stats()
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total simulations", stats["total"])
    with col2:
        pays_top = max(stats["pays"], key=stats["pays"].get) if stats["pays"] else "N/A"
        st.metric("Pays le plus frequent", pays_top)
    with col3:
        montant_fmt = f"{stats['montant_total']:,.0f}"
        st.metric("Montant cumule", montant_fmt)

    st.markdown("---")

    # Bouton effacer tout
    col_titre, col_btn = st.columns([3, 1])
    with col_titre:
        st.markdown(f"**{len(simulations)} simulation(s) sauvegardee(s)**")
    with col_btn:
        if st.button(" Tout effacer", type="secondary"):
            nb = effacer_historique()
            st.success(f"{nb} simulation(s) supprimee(s).")
            st.rerun()

    # Liste des simulations (plus recente en premier)
    for sim in reversed(simulations):
        _afficher_carte_simulation(sim)


def _afficher_carte_simulation(sim: dict):
    """Affiche une carte pour une simulation sauvegardee."""
    from utils.simulation_store import supprimer_simulation

    titre = (
        f" {sim.get('entreprise', 'N/A')}  →  "
        f" {sim.get('pays_fournisseur', 'N/A')}  |  "
        f" {sim.get('montant', 0):,.0f} {sim.get('devise', '')}  |  "
        f" {sim.get('date', 'N/A')}"
    )

    with st.expander(titre, expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Details de l'operation**")
            st.markdown(f"- **Fournisseur** : {sim.get('fournisseur', 'N/A')}")
            st.markdown(f"- **Mode paiement** : {sim.get('mode_paiement', 'N/A')}")
            st.markdown(f"- **Marchandise** : {sim.get('type_marchandise', 'N/A')}")
            st.markdown(f"- **Banque** : {sim.get('banque', 'N/A')}")
            st.markdown(f"- **SWIFT/BIC** : {sim.get('swift_bic', 'N/A')}")

        with col2:
            st.markdown("**Informations complementaires**")
            st.markdown(f"- **Documents identifies** : {sim.get('nb_documents', 0)}")
            mode = "Mode degrade (sans IA)" if sim.get("mode_degrade") else "Mode IA actif"
            st.markdown(f"- **Mode** : {mode}")
            st.markdown(f"- **ID** : `{sim.get('id', 'N/A')}`")

        # Resume sauvegarde
        resume = sim.get("resume_base", "")
        if resume:
            st.markdown("**Resume sauvegarde**")
            st.code(resume, language=None)

        # Bouton supprimer
        if st.button(
            f"🗑️ Supprimer cette simulation",
            key=f"del_{sim.get('id')}",
            type="secondary"
        ):
            supprimer_simulation(sim.get("id"))
            st.success("Simulation supprimee.")
            st.rerun()


def render():
    """Point d'entree principal — appele par app.py."""
    from ui.result_display import afficher_resultat

    initialiser_session()
    afficher_sidebar()

    if st.session_state.onglet == "historique":
        afficher_onglet_historique()
        return

    # Onglet assistant (defaut)
    st.title(f" {APP_NAME}")
    st.markdown("*Assistant de paiement international*")
    st.divider()

    afficher_message_bienvenue()
    afficher_historique_chat()

    if st.session_state.en_cours:
        afficher_question_courante()
    else:
        if st.session_state.resultat:
            afficher_resultat(st.session_state.resultat)