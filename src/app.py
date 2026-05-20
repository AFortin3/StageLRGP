import streamlit as st

import utils as utils
from components.sidebar import render_sidebar
from components.dashboard import show_gas_properties, show_limites_results, render_analysis_expander

def main():
    st.title("Mélange de gaz")

    data = render_sidebar()

    show_gas_properties(data)

    try:
        limites = utils.main_streamlit(data)
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.stop()
        
    show_limites_results(limites)
    
    render_analysis_expander()    


if __name__ == "__main__":
    main()