import streamlit as st

import utils
from logger import log

from components.sidebar import render_sidebar
from components.dashboard import show_gas_properties, show_limites_results, render_analysis_expander

if 'initialized' not in st.session_state or not st.session_state['initialized']:
    # Mode 'w' écrase le contenu existant
    with open("resultats_debug.txt", "w", encoding="utf-8") as f:
        f.write("=== Nouveau démarrage de l'application ===\n")
    
    st.session_state['initialized'] = False

def main():
    st.title("Mélange de gaz")
    
    log("----------------Calcul 1 : LIE et LSE pour les conditions par défaut----------------\n")
    data = render_sidebar()

    show_gas_properties(data)

    try:
        limites = utils.main_streamlit(data)
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.stop()
        
    show_limites_results(limites)
    log("----------------FIN calcul 1 : LIE et LSE pour les conditions par défaut----------------\n")
    
    log("----------------Calcul 2 : Plage de LIE et LSE pour différentes températures et pressions----------------\n")
    render_analysis_expander()    
    log("----------------FIN calcul 2 : Plage de LIE et LSE pour différentes températures et pressions----------------\n")


if __name__ == "__main__":
    main()