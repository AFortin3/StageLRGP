import streamlit as st
import pandas as pd

import utils

st.title("Mélange de gaz")


# --- SIDEBAR ---
with st.sidebar:
    st.header("Paramètres d'entrée")
    
    # Section Physical Property
    st.subheader("Physical Properties")
    pres = st.number_input("Pressure (atm)", value=20.0, step=1.0)
    temp = st.number_input("Temperature (°C)", value=200.0, step=20.0)
    
    # Section Added Species
    st.subheader("Added Species (mole fraction)")
    add_co2 = st.number_input("Added CO2", value=0.0, min_value=0.0, max_value=1.0, step=0.1)
    add_h2o = st.number_input("Added H2O", value=0.0, min_value=0.0, max_value=1.0, step=0.1)
    add_n2 = st.number_input("Added N2", value=0.0, min_value=0.0, max_value=1.0, step=0.1)
    
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
        fuel_values[fuel] = st.number_input(f"FUEL {fuel}", value=default_val, step=10)
        
    # normalisation des carburants (pour bien avoir 100% au total)
    fuel_total = sum(fuel_values.values())
    if fuel_total > 0:
        for fuel in utils.species:
            fuel_values[fuel] = (fuel_values[fuel] / fuel_total) * 100


# --- ZONE PRINCIPALE ---
st.write("### Résumé des paramètres choisis :")

# Exemple d'affichage des données collectées
data = {
    "PRES": pres,
    "TEMP": temp + 273.15,  # Convertir en Kelvin pour les calculs
    "INERTES": {"CO2": add_co2, "H2O": add_h2o, "N2": add_n2},
    "FUEL": fuel_values
}

# Affichage des propriétés physiques en colonnes pour un rendu plus propre
col_a, col_b = st.columns(2)
col_a.metric("Pressure", f"{pres:.2f} atm")
col_b.metric("Temperature", f"{temp:.2f} °C")

# Préparation des DataFrames pour un affichage élégant 
df_inertes = pd.DataFrame([data["INERTES"]])
df_fuel = pd.DataFrame(list(data["FUEL"].items()), columns=["Espèce", "Valeur"])

# Affichage avec column_config (pour le formatage .2f et l'esthétique)
st.write("### Added Species (mole fraction)")
st.dataframe(
    df_inertes, 
    hide_index=True, 
    use_container_width=True,
    column_config={
        col: st.column_config.NumberColumn(col, format="%.2f") 
        for col in df_inertes.columns
    }
)

st.write("### Fuel Composition (%)")
st.dataframe(
    df_fuel, 
    hide_index=True, 
    use_container_width=True,
    height="content",
    column_config={
        "Valeur": st.column_config.NumberColumn("Valeur (%)", format="%.2f")
    }
)


# Exemple d'affichage des résultats
# Titre principal
st.divider()
st.subheader("Résultats de la Simulation")

try:
    limites = utils.main_streamlit(data)
except Exception as e:
    st.error(f"Erreur: {e}")
    st.stop()

# Informations de contexte en bas
st.write(f"Calculé à P = {limites['LIE'][1]:.2f} bar et T = {limites['LIE'][2]:.2f} °C")

# Création de deux colonnes pour séparer LIE et LSE
col1, col2 = st.columns(2)

with col1:
    st.info("**Limite Inférieure d'Explosivité (LIE)**")
    st.metric("LIE", f"{limites['LIE'][4]:.4f} %")
    st.write(f"**Phi Low:** {limites['LIE'][0]:.3f}")
    st.write(f"**T_Low:** {limites['LIE'][3]:.2f} °C")

with col2:
    st.error("**Limite Supérieure d'Explosivité (LSE)**")
    st.metric("LSE", f"{limites['LSE'][4]:.4f} %")
    st.write(f"**Phi High:** {limites['LSE'][0]:.3f}")
    st.write(f"**T_High:** {limites['LSE'][3]:.2f} °C")
    
    
    
# Création d'un expander pour étendre les calculs à une plage de température / pression
st.divider()
st.subheader("Analyse détaillée (plage de T et P)")

with st.expander("Configurer une plage de calcul", expanded=False):
    st.write("Définissez les bornes pour effectuer une étude paramétrique.")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    t_min = col_t1.number_input("T min (°C)", value=20.0, step=5.0)
    t_max = col_t2.number_input("T max (°C)", value=100.0, step=5.0)
    dt = col_t3.number_input("Pas T (°C)", value=10.0, min_value=1.0, step=5.0)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    p_min = col_p1.number_input("P min (atm)", value=1.0, step=1.0)
    p_max = col_p2.number_input("P max (atm)", value=10.0, step=1.0)
    dp = col_p3.number_input("Pas P (atm)", value=1.0, min_value=0.1, step=1.0)
    
    # Calcul du nombre de points pour prévenir l'utilisateur
    nb_t = int((t_max - t_min) / dt) + 1
    nb_p = int((p_max - p_min) / dp) + 1
    total_runs = nb_t * nb_p
    
    placeholder_avertissement = st.empty() # Placeholder pour afficher le message d'avertissement
    placeholder_avertissement.warning(f"⚠️ Attention : {total_runs} simulations seront lancées. Cela peut prendre du temps.") # Affiche un avertissement avant de lancer les calculs

    # affichage des résultats  
    c1, c2, c3 = st.columns([8, 8, 7.5])   
    placeholder_btn = c2.empty() # Placeholder pour le bouton, afin de le désactiver pendant les calculs
    if placeholder_btn.button("Lancer les calculs de plage"):
        # Effacer le bouton et l'avertissement immédiatement
        placeholder_btn.empty()
        placeholder_avertissement.empty()
        
        # On utilise une disposition colonnes pour créer un centrage
        col_spinner1, col_spinner2, col_spinner3 = st.columns([3, 2, 3])
        with col_spinner2:
            with st.spinner("Calcul en cours..."):
                resultats_plage = utils.calcul_plage(t_min, t_max, dt, p_min, p_max, dp) # Appel de la fonction de calcul pour la plage de T et P 
                
        st.success("Calculs terminés !")
        st.dataframe(resultats_plage)


 
