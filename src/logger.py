import streamlit as st

def log(message: str):
    if 'initialized' not in st.session_state:
        st.session_state['initialized'] = False
    elif st.session_state['initialized']:
        with open("resultats_debug.txt", "a", encoding="utf8") as f:
            f.write(message)