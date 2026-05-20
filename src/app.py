import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import utils

def main():
    st.title("Mélange de gaz")


    # sidebar pour les paramètres d'entrée
    with st.sidebar:
        st.header("Paramètres d'entrée")
        
        # Section Physical Property
        st.subheader("Physical Properties")
        pres = st.number_input("Pressure (bar)", value=20.0, step=1.0)
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
            
        # Normalisation des carburants (pour bien avoir 100% au total)
        fuel_total = sum(fuel_values.values())
        if fuel_total > 0:
            for fuel in utils.species:
                fuel_values[fuel] = (fuel_values[fuel] / fuel_total) * 100



    st.write("### Résumé des paramètres choisis :")

    # Exemple d'affichage des données collectées
    data = {
        "PRES": pres,
        "TEMP": temp + 273.15,  # Convertir en Kelvin pour les calculs
        "INERTES": {"CO2": add_co2, "H2O": add_h2o, "N2": add_n2},
        "FUEL": fuel_values
    }

    # Affichage des propriétés physiques en colonnes
    col_a, col_b = st.columns(2)
    col_a.metric("Pressure", f"{pres:.2f} bar")
    col_b.metric("Temperature", f"{temp:.2f} °C")

    # Préparation des DataFrames 
    df_inertes = pd.DataFrame([data["INERTES"]])
    df_fuel = pd.DataFrame(list(data["FUEL"].items()), columns=["Espèce", "Valeur"])

    # Affichage avec column_config
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
    col_LIE, col_LSE = st.columns(2)

    with col_LIE:
        st.info("**Limite Inférieure d'Explosivité (LIE)**")
        st.metric("LIE", f"{limites['LIE'][4]:.4f} %")
        st.write(f"**Phi Low:** {limites['LIE'][0]:.3f}")
        st.write(f"**T_Low:** {limites['LIE'][3]:.2f} °C")

    with col_LSE:
        st.error("**Limite Supérieure d'Explosivité (LSE)**")
        st.metric("LSE", f"{limites['LSE'][4]:.4f} %")
        st.write(f"**Phi High:** {limites['LSE'][0]:.3f}")
        st.write(f"**T_High:** {limites['LSE'][3]:.2f} °C")
        
        
        
    # Création d'un expander pour étendre les calculs à une plage de température / pression
    st.divider()
    st.subheader("Analyse détaillée (plage de T et P)")

    with st.expander("Configurer une plage de calcul", expanded=False):
        # Utilisation de session_state pour garder les résultats en mémoire
        if "resultats_plage" not in st.session_state:
            st.session_state.resultats_plage = None
        
        st.write("Définissez les bornes pour effectuer une étude paramétrique.")
        
        col_t1, col_t2, col_t3 = st.columns(3)
        t_min = col_t1.number_input("T min (°C)", value=20.0, step=5.0, on_change=reset_results)
        t_max = col_t2.number_input("T max (°C)", value=100.0, step=5.0, on_change=reset_results)
        dt = col_t3.number_input("Pas T (°C)", value=10.0, min_value=1.0, step=5.0, on_change=reset_results)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        p_min = col_p1.number_input("P min (bar)", value=1.0, step=1.0, on_change=reset_results)
        p_max = col_p2.number_input("P max (bar)", value=10.0, step=1.0, on_change=reset_results)
        dp = col_p3.number_input("Pas P (bar)", value=1.0, min_value=0.1, step=1.0, on_change=reset_results)
        
        # Calcul du nombre de points pour prévenir l'utilisateur
        nb_t = int((t_max - t_min) / dt) + 1
        nb_p = int((p_max - p_min) / dp) + 1
        total_runs = nb_t * nb_p
        
        placeholder_avertissement = st.empty() # Placeholder pour afficher le message d'avertissement
        if st.session_state.resultats_plage is None:
            placeholder_avertissement.warning(f"⚠️ Attention : {total_runs} simulations seront lancées. Cela peut prendre du temps.") # Affiche un avertissement avant de lancer les calculs

            c1, col_btn, c3 = st.columns([8, 8, 7.5]) # pour centrer le bouton
            placeholder_btn = col_btn.empty() # Placeholder pour le bouton, afin de le désactiver pendant les calculs
            if placeholder_btn.button("Lancer les calculs de plage"):
                # Effacer le bouton et l'avertissement immédiatement
                placeholder_btn.empty()
                placeholder_avertissement.empty()
                
                c1, col_spinner, c3 = st.columns([3, 2, 3])
                with col_spinner:
                    with st.spinner("Calcul en cours..."):
                        # On stocke le résultat dans le session_state
                        st.session_state.resultats_plage = utils.calcul_plage(t_min, t_max, dt, p_min, p_max, dp)
                
                st.success("Calculs terminés !")

        # On affiche les graphiques si les résultats existent
        if st.session_state.resultats_plage is not None:
            resultats_plage = st.session_state.resultats_plage
            
            graph, heatmap, table = st.tabs(["📈 Graphiques", "🌡️ Heatmap", "📊 Données"])
            
            with graph:
                st.write("### 📈 Analyse des Limites")
                
                # Choix du mode d'affichage
                heatmap_col1, heatmap_col2 = st.columns(2)
                mode = heatmap_col1.radio("Variable X :", ["Température", "Pression"], horizontal=True)
                type_limite = heatmap_col2.radio("Limite à afficher :",["LIE", "LSE", "Les deux"], horizontal=True)
                
                # Sélecteurs de filtrage (pour éviter d'afficher 10000 points d'un coup)
                # Si l'axe x du graphe est la température, on veut pouvoir filtrer sur une pression précise (ou plusieurs)
                val_x = "T (°C)" if mode == "Température" else "P (bar)"
                val_filter = "P (bar)" if mode == "Température" else "T (°C)"
                
                # On récupère les valeurs uniques disponibles pour filtrer
                valeurs_dispo = sorted(resultats_plage[val_filter].unique())
                
                # Multi-select pour permettre de comparer quelques courbes sans surcharger l'affichage
                selection = st.multiselect(
                    f"Sélectionnez les valeurs de {val_filter} à afficher :",
                    options=valeurs_dispo,
                    default=valeurs_dispo[:3] if len(valeurs_dispo) > 3 else valeurs_dispo
                )
                
                # Filtrage des données
                df_filtre = resultats_plage[resultats_plage[val_filter].isin(selection)].copy()
                
                # Préparation pour Plotly (Melt)
                cols_to_melt =[]
                if type_limite in ["LIE", "Les deux"]: cols_to_melt.append("LIE")
                if type_limite in ["LSE", "Les deux"]: cols_to_melt.append("LSE")
                
                df_plot = df_filtre.melt(
                    id_vars=[val_x, val_filter], 
                    value_vars=cols_to_melt, 
                    var_name="Type", 
                    value_name="Valeur"
                )
                
                # On transforme la colonne de filtrage en string pour que Plotly les traite comme des catégories
                df_plot[val_filter] = df_plot[val_filter].astype(str)
                
                # Graphique
                if not df_plot.empty:
                    fig = px.line(
                        df_plot, 
                        x=val_x, 
                        y="Valeur", 
                        color="Type",
                        line_dash=val_filter,
                        markers=len(df_plot) < 100, # Désactive les points si trop de données
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Sélectionnez des données pour afficher le graphique.")
                                
            with heatmap:
                st.write("### 🌡️ Carte de chaleur (Heatmap) des limites d'explosivité")

                # Création de deux sous-graphiques (1 ligne, 2 colonnes)
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("LIE (%)", "LSE (%)"),
                    horizontal_spacing=0.3,
                )

                # Heatmap LIE
                fig.add_trace(
                    go.Heatmap(
                        x=st.session_state.resultats_plage["T (°C)"],
                        y=st.session_state.resultats_plage["P (bar)"],
                        z=st.session_state.resultats_plage["LIE"],
                        colorscale="Blues",
                        colorbar=dict(x=0.35, len=0.8), # Positionner la barre de couleur
                        name="LIE"
                    ),
                    row=1, col=1
                )

                # Heatmap LSE
                fig.add_trace(
                    go.Heatmap(
                        x=st.session_state.resultats_plage["T (°C)"],
                        y=st.session_state.resultats_plage["P (bar)"],
                        z=st.session_state.resultats_plage["LSE"],
                        colorscale="Reds",
                        colorbar=dict(x=1.0, len=0.8),
                        name="LSE"
                    ),
                    row=1, col=2
                )

                fig.update_layout(
                    height=600,
                    title_text="Répartition des limites d'explosivité (P/T)",
                    xaxis_title="Température (°C)",
                    xaxis2_title="Température (°C)",
                    yaxis_title="Pression (bar)"
                )

                st.plotly_chart(fig, use_container_width=True)
                
            
            with table:
                st.dataframe(resultats_plage, use_container_width=True)
                

def reset_results():
    st.session_state.resultats_plage = None


if __name__ == "__main__":
    main()
