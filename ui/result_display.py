import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.checklist_generator import get_infos_pays
from utils.pdf_exporter import generer_pdf, generer_nom_fichier


def afficher_resultat(resultat):
    """
    Point d'entrée principal — appelé par chat_interface.py.
    Orchestre l'affichage complet du résultat final.
    """
    st.success(" Simulation terminée ! Voici votre résumé complet.")

    # Bouton export PDF — visible immédiatement en haut
    _afficher_bouton_pdf(resultat)

    st.divider()
    _afficher_bandeau_mode(resultat)
    _afficher_resume(resultat)
    st.divider()
    _afficher_checklist(resultat)
    st.divider()
    _afficher_infos_pays(resultat)


def _afficher_bouton_pdf(resultat):
    """
    Génère le PDF en mémoire et affiche le bouton de téléchargement Streamlit.
    Gère proprement le cas où fpdf2 n'est pas installé.
    """
    try:
        pdf_bytes = generer_pdf(resultat)
        nom       = generer_nom_fichier(resultat)

        st.download_button(
            label               = "📄 Télécharger le résumé en PDF",
            data                = pdf_bytes,
            file_name           = nom,
            mime                = "application/pdf",
            use_container_width = True,
        )
    except ImportError:
        st.info(
            " Pour activer l'export PDF, installez fpdf2 : `pip install fpdf2`",
            
        )
    except Exception as e:
        st.warning(f" Export PDF indisponible : {e}")


def _afficher_bandeau_mode(resultat):
    """Affiche un bandeau si on est en mode dégradé (Ollama indisponible)."""
    #if resultat.mode_degrade
    if resultat.resume.get("mode_degrade"):
        st.warning(
            " **Mode hors-ligne** : Ollama n'est pas disponible. "
            "Le résumé et la checklist sont générés sans enrichissement IA. ",
            
        )

def _afficher_resume(resultat):
    """Affiche le résumé de l'opération."""
    st.subheader(" Résumé de l'opération")
    if resultat.resume.get("resume_llm"):
        st.markdown(resultat.resume["resume_llm"])
    else:
        st.code(resultat.resume["resume_base"], language=None)

def _afficher_checklist(resultat):
    """Affiche la checklist des documents nécessaires."""
    st.subheader(" Documents nécessaires")

    documents    = resultat.documents
    obligatoires = [d for d in documents if d.get("obligatoire")]
    recommandes  = [d for d in documents if not d.get("obligatoire")]

    st.markdown(f"**Documents obligatoires** ({len(obligatoires)})")
    for doc in obligatoires:
        with st.expander(f" {doc['nom']}", expanded=False):
            st.markdown(doc.get("description", ""))
            if "base" in doc.get("source", ""):
                st.caption(" Requis pour tout paiement international")
            else:
                st.caption(f" Spécifique au pays : {resultat.checklist.get('pays', '')}")

    if recommandes:
        st.markdown(f"**Documents recommandés** ({len(recommandes)})")
        for doc in recommandes:
            with st.expander(f" {doc['nom']}", expanded=False):
                st.markdown(doc.get("description", ""))

    if resultat.enrichissement_checklist:
        st.divider()
        st.markdown("** Précisions de l'assistant IA**")
        st.markdown(resultat.enrichissement_checklist)


def _afficher_infos_pays(resultat):
    """Affiche les informations contextuelles du pays fournisseur."""
    pays = resultat.checklist.get("pays")
    if not pays:
        return
    infos = get_infos_pays(pays)
    if not infos:
        return

    st.subheader(f" Informations sur le pays fournisseur : {pays}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(" Délai de virement estimé", infos.get("delai_virement_moyen", "N/A"))
    with col2:
        st.metric(" Devise habituelle", infos.get("devise_habituelle", "N/A"))

    if infos.get("remarque"):
        st.info(f" {infos['remarque']}")