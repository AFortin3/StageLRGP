import streamlit as st

import core.calculateur as calc
from components.sidebar import render_sidebar
from components.dashboard import show_gas_properties, show_limites_results, render_analysis_expander

def main():
    if "calculateur" not in st.session_state:
        st.session_state.calculateur = calc.Calculateur()
    
    st.set_page_config(layout="wide")
        
    st.title("Mélange de gaz")

    data = render_sidebar()
    if data == 0:  # Cas où aucun carburant n'est sélectionné
        st.warning("⚠️ la somme des carburants est nulle. Veuillez sélectionner au moins un carburant.")
        st.stop()
        
    show_gas_properties(data)

    try:
        limites = st.session_state.calculateur.start(data)
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.stop()
        
    show_limites_results(limites)
    
    render_analysis_expander()    


if __name__ == "__main__":
    main()