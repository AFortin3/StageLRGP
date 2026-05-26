import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Affichage des propriétés physiques du mélange (pression, température, composition du carburant et gaz inertes) 
def show_gas_properties(data: dict):
    st.write("### Résumé des paramètres choisis :")

    # Préparation des DataFrames pour affichage avec column_config
    df_inertes = pd.DataFrame([data["INERTES"]])
    df_fuel = pd.DataFrame(list(data["FUEL"].items()), columns=["Espèce", "Valeur"])

    # Affichage des propriétés physiques en colonnes
    pres, temp = st.columns([1, 6.2])
    pres.metric("Pressure", f"{data["PRES"]:.2f} bar")
    temp.metric("Temperature", f"{data["TEMP"]:.2f} °C")
        
    # Premier menu déroulant pour les espèces inertes
    with st.expander("Added Species (mole fraction)"):
        st.dataframe(
            df_inertes, 
            hide_index=True, 
            use_container_width=True, # Prend toute la largeur de l'expander
            height="stretch",
            column_config={
                col: st.column_config.NumberColumn(col, format="%.2f") 
                for col in df_inertes.columns
            }
        )
    
    # Deuxième menu déroulant pour la composition du carburant
    with st.expander("Fuel Composition (%)"):
        st.dataframe(
            df_fuel, 
            hide_index=True, 
            use_container_width=True, # Prend toute la largeur de l'expander
            column_config={
                "Valeur": st.column_config.NumberColumn("Valeur (%)", format="%.2f")
            }
        )
    
    
# Affichage des résultats de la simulation (LIE et LSE) avec des messages d'avertissement si les limites n'ont pas pu être calculées pour les conditions données, et explications possibles
def show_limites_results(limites: dict):
    st.divider()
    st.subheader("Résultats de la Simulation")
    
    lie, lse = st.columns(2) # pour afficher la LIE et la LSE côte à côte
    
    if limites.get("LIE") is None and limites.get("LSE") is None:
        st.warning("""Les limites d'explosivité n'ont pas pu être calculées pour les conditions données.
                   Note : Cela peut arriver si les conditions sont en dehors des plages de validité du modèle 
                   ou si le mélange est trop dilué/riche pour que les limites soient définies 
                   (ex. Phi > 1 pour la LIE ou > 50 pour la LSE).""")
    
    elif limites.get("LIE")  is None:
        with lie:
            st.warning("""La LIE n'a pas pu être calculée pour les conditions données.
                    Note : Cela peut arriver si les conditions sont en dehors des plages de validité du modèle 
                    ou si le mélange est trop dilué/riche pour que la LIE soit définie 
                    (ex. Phi > 1 ou < 0.01).""")
        
        # affichage de la LSE  
        with lse:
            st.error("**Limite Supérieure d'Explosivité (LSE)**")
            st.metric("LSE", f"{limites['LSE'][4]:.4f} %")
            st.write(f"**Phi:** {limites['LSE'][0]:.3f}")
            st.write(f"**T_High:** {limites['LSE'][3]:.2f} °C")
        
    elif limites.get("LSE")  is None:
        with lse:
            st.warning("""La LSE n'a pas pu être calculée pour les conditions données.
                    Note : Cela peut arriver si les conditions sont en dehors des plages de validité du modèle 
                    ou si le mélange est trop dilué/riche pour que la LSE soit définie 
                    (ex. Phi > 50 ou < 1).""")
            
        # affichage de la LIE
        with lie:
            st.info("**Limite Inférieure d'Explosivité (LIE)**")
            st.metric("LIE", f"{limites['LIE'][4]:.4f} %")
            st.write(f"**Phi:** {limites['LIE'][0]:.3f}")
            st.write(f"**T_Low:** {limites['LIE'][3]:.2f} °C")
        
    else:       
        with lie:
            st.info("**Limite Inférieure d'Explosivité (LIE)**")
            st.metric("LIE", f"{limites['LIE'][4]:.4f} %")
            st.write(f"**Phi:** {limites['LIE'][0]:.3f}")
            st.write(f"**T_Low:** {limites['LIE'][3]:.2f} °C")
        
        with lse:
            st.error("**Limite Supérieure d'Explosivité (LSE)**")
            st.metric("LSE", f"{limites['LSE'][4]:.4f} %")
            st.write(f"**Phi:** {limites['LSE'][0]:.3f}")
            st.write(f"**T_High:** {limites['LSE'][3]:.2f} °C")
    
    
        
# Création d'un expander pour étendre les calculs à une plage de température / pression
def render_analysis_expander():
    # Injection de CSS pour personnaliser les couleurs des boutons (Lancer en vert)
    st.markdown("""
        <style>
        /* Couleur du bouton Lancer (Vert) */
        div.stButton > button:first-child {
            background-color: #28a745;
            color: white;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)
    st.divider()
    st.subheader("Analyse détaillée (plage de T et P)")

    with st.expander("Configurer une plage de calcul", expanded=False):
        # Utilisation de session_state pour garder les résultats en mémoire
        if "resultats_plage" not in st.session_state:
            st.session_state.resultats_plage = None
        
        col_title, col_precision_temp, col_precision_phi = st.columns([3, 1, 1]) # Colonne pour le titre, et une colonne plus petite pour les précisions
        with col_title:
            st.subheader("Définissez les bornes pour effectuer une étude paramétrique.")
            
        # Permet à l'utilisateur de définir la précision des calculs (pour la température et le ratio d'équivalence)
        precision_temp = col_precision_temp.number_input("Précision Température", value=0.05, min_value=0.001, step=0.05, format="%.2f", on_change=reset_results)
        precision_phi = col_precision_phi.number_input("Précision Phi", value=0.005, min_value=0.001, step=0.005, format="%.3f", on_change=reset_results)
            
        # Inputs pour définir la plage de température et de pression à analyser
        col_t1, col_t2, col_t3 = st.columns(3)
        t_min = col_t1.number_input("T min (°C)", value=20.0, step=5.0, on_change=reset_results, key="t_min_input")
        t_max = col_t2.number_input("T max (°C)", value=100.0, step=5.0, on_change=reset_results, key="t_max_input")
        dt = col_t3.number_input("Pas T (°C)", value=10.0, min_value=0.001, step=5.0, key="dt_input")

        col_p1, col_p2, col_p3 = st.columns(3)
        p_min = col_p1.number_input("P min (bar)", value=1.0, step=1.0, on_change=reset_results, key="p_min_input")
        p_max = col_p2.number_input("P max (bar)", value=10.0, step=1.0, on_change=reset_results, key="p_max_input")
        dp = col_p3.number_input("Pas P (bar)", value=1.0, min_value=0.001, step=1.0, key="dp_input")
        
        # Calcul du nombre de points pour prévenir l'utilisateur
        nb_t = int((t_max - t_min) / dt) + 1
        nb_p = int((p_max - p_min) / dp) + 1
        total_runs = nb_t * nb_p
        
        placeholder_avertissement = st.empty() # Placeholder pour afficher le message d'avertissement (nombre de simulations)
        if st.session_state.resultats_plage is None:
            # Affiche un avertissement avant de lancer les calculs
            placeholder_avertissement.warning(f"""⚠️ Attention : {total_runs} simulations seront lancées. Cela peut prendre du temps. 
                                              Note : le degré de précision joue beaucoup sur le temps de calcul.""")            
            
            placeholder_btn = st.empty() # Placeholder pour le bouton, afin de le désactiver pendant les calculs
            if placeholder_btn.button("Lancer les calculs de plage"):
                # Effacer le bouton et l'avertissement immédiatement
                placeholder_btn.empty()
                placeholder_avertissement.empty()
            
                with st.spinner("Calcul en cours..."):
                    # On stocke le résultat dans le session_state
                    st.session_state.resultats_plage = st.session_state.calculateur.calcul_plage(t_min, t_max, dt, p_min, p_max, dp, precision_temp, precision_phi)
                
                st.success("Calculs terminés !")
                

        # On affiche les graphiques si les résultats existent
        if st.session_state.resultats_plage is not None:
            resultats_plage = st.session_state.resultats_plage
            
            if resultats_plage.empty:
                st.warning("Aucun résultat à afficher pour la plage sélectionnée. Veuillez ajuster les paramètres.")
                st.stop()
            
            # On vérifie s'il y a des points où la LIE ou la LSE n'ont pas pu être calculées (NaN)
            # Listes pour stocker les points qui ont posé problème
            points_lie_manquants = []
            points_lse_manquants = []

            # On parcourt le tableau et on collecte les points
            for index, row in resultats_plage.iterrows():
                
                # Formatage du point (ex: "19.0 bar / 190.0 °C")
                texte_point = f"{row['P (bar)']:.1f} bar / {row['T (°C)']:.1f} °C"
                
                if pd.isna(row["LIE"]):
                    points_lie_manquants.append(texte_point)
                    
                if pd.isna(row["LSE"]):
                    points_lse_manquants.append(texte_point)

            # Affichage des alertes pour la LIE
            if points_lie_manquants:
                st.warning(f"⚠️ **LIE non définie pour {len(points_lie_manquants)} point(s).**")
                with st.expander("Voir le détail des points non définis (LIE)"):
                    # Génère une liste à puces en Markdown
                    liste_lie_md = "\n".join([f"- P = {pt}" for pt in points_lie_manquants])
                    st.markdown(liste_lie_md)

            # Affichage des alertes pour la LSE
            if points_lse_manquants:
                st.warning(f"⚠️ **LSE non définie pour {len(points_lse_manquants)} point(s).**")
                with st.expander("Voir le détail des points non définis (LSE)"):
                    # Génère une liste à puces en Markdown
                    liste_lse_md = "\n".join([f"- P = {pt}" for pt in points_lse_manquants])
                    st.markdown(liste_lse_md)
            
            
            
            # Affichage des points dans des onglets
            graph, heatmap, table = st.tabs(["📈 Graphiques", "🌡️ Heatmap", "📊 Données"])
            
            
            # Graphiques de LIE et LSE en fonction de T ou P, avec possibilité de filtrer pour éviter d'avoir 10000 points d'un coup
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
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.warning("Sélectionnez des données pour afficher le graphique.")
                      
                              
            # Heatmap des limites d'explosivité en fonction de T et P  
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

                st.plotly_chart(fig, width='stretch')
                
                
            # Affichage du tableau complet des résultats (avec possibilité de filtrer pour éviter d'avoir 10000 points d'un coup)
            with table:
                st.dataframe(resultats_plage, width='stretch')
       
                
# Fonction pour réinitialiser les résultats de la plage d'analyse
def reset_results():
    st.session_state.resultats_plage = None
 