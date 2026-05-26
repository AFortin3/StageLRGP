import streamlit as st

import utils
from utils import reset_results

def render_sidebar():
    # sidebar pour les paramètres d'entrée
    with st.sidebar:
        st.header("Paramètres d'entrée")
        
        # Section Physical Property
        st.subheader("Physical Properties")
        pres = st.number_input("Pressure (bar)", value=20.0, step=1.0, on_change=reset_results)
        temp = st.number_input("Temperature (°C)", value=200.0, step=20.0, on_change=reset_results)
        
        # Section Added Species
        st.subheader("Added Species (mole fraction)")
        add_co2 = st.number_input("Added CO2", value=0.0, min_value=0.0, max_value=1.0, step=0.1, on_change=reset_results)
        add_h2o = st.number_input("Added H2O", value=0.0, min_value=0.0, max_value=1.0, step=0.1, on_change=reset_results)
        add_n2 = st.number_input("Added N2", value=0.0, min_value=0.0, max_value=1.0, step=0.1, on_change=reset_results)
        
        # Calcul du total
        total_inertes = add_co2 + add_h2o + add_n2
        
        # Vérification
        if total_inertes > 1.0:
            st.error(f"⚠️ Somme invalide : {total_inertes:.2f} (doit être ≤ 1.0)")
        else:
            st.success(f"Somme des inertes : {total_inertes:.2f}")
        
        # Section Fuel
        st.subheader("Fuel Composition (%)")    
        
        # Création d'un dictionnaire pour stocker les valeurs
        fuel_values = {}
        for fuel in utils.species:
            default_val = 100 if fuel == "C3H8" else 0
            fuel_values[fuel] = st.number_input(f"FUEL {fuel}", value=float(default_val), min_value=0.0, max_value=100.0, step=10.0, on_change=reset_results)
            
        # Normalisation des carburants (pour bien avoir 100% au total)
        fuel_total = sum(fuel_values.values())
        
        if fuel_total == 0: # dans le cas ou il n'y a pas de carburant, on retourne 0 (pour faire passer l'erreur)
            return 0
            
        for fuel in utils.species:
            fuel_values[fuel] = (fuel_values[fuel] / fuel_total) * 100 
                            
    data = {
        "PRES": pres,
        "TEMP": temp + 273.15,  # Convertir en Kelvin pour les calculs
        "INERTES": {"CO2": add_co2, "H2O": add_h2o, "N2": add_n2},
        "FUEL": fuel_values
    }
    
    return data
