import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION
from llm.llm_client import verifier_disponibilite
from ui.chat_interface import render



# Configuration Streamlit — doit être le premier appel st.*


st.set_page_config(
    page_title = APP_NAME,
    layout     = "centered",
)



# Vérification Ollama au démarrage (une seule fois par session)


if "ollama_verifie" not in st.session_state:
    ok, msg = verifier_disponibilite()
    st.session_state.ollama_verifie     = True
    st.session_state.ollama_disponible  = ok
    st.session_state.ollama_message     = msg

if not st.session_state.ollama_disponible:
    st.sidebar.warning(
        f"⚠️ Ollama indisponible\n\n"
        f"{st.session_state.ollama_message}",
    )
else:
    st.sidebar.success("✅ Mistral connecté")

st.sidebar.caption(f"v{APP_VERSION}")



# Point d'entrée principal


render()