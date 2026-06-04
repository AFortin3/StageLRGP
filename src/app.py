import streamlit as st

import core.GasSimulator as gsim
from components.sidebar import render_sidebar
from components.dashboard import show_gas_properties, show_limites_results, render_analysis_expander
from components.guide import GUIDE_MD 

def main():
    if "gsim" not in st.session_state:
        st.session_state.gsim = gsim.GasSimulator() 
            
    st.set_page_config(layout="wide") # pour prendre toute la largeur de l'écran

    # On aligne le titre et le bouton pour afficher le guide utilisateur avec des colonnes
    title, guide = st.columns([5, 1]) 

    # On définit la fenêtre pop-up (guide utilisateur)
    @st.dialog("📖 Guide d'Utilisation", width="large")
    def afficher_guide():
        st.markdown(GUIDE_MD)

    # Titre de la page
    with title:
        st.title("Simulateur des Limites d'Inflammabilité")

    with guide:
        st.write("") # Petit espace vide pour aligner verticalement le bouton
        if st.button("❓ Aide / Guide"):
            afficher_guide() # Ouvre la fenêtre quand on clique

    # Sidebar
    data = render_sidebar()
    if data == 0:  # Cas où aucun carburant n'est sélectionné
        st.warning("⚠️ la somme des carburants est nulle. Veuillez sélectionner au moins un carburant.")
        st.stop()

    # On affiche les propriétés du gaz
    show_gas_properties(data)

    try:
        limites = st.session_state.gsim.start(data)
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.stop()

    # On affiche les résultats
    show_limites_results(limites)

    # Analyse en profondeur
    render_analysis_expander()    


if __name__ == "__main__":
    main()
