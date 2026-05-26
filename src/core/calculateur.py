import numpy as np
from numpy.typing import NDArray
import pandas as pd
import cantera as ct
import streamlit as st
from pathlib import Path

from core.Critere_T import critere_T
from core.LIE_LSE_V2 import lie_lse

class Calculateur:
    def __init__(self, yaml_filename: str = "output_convert.yaml"):
        """
        Initialise une nouvelle instance d'analyse avec son propre objet Cantera 
        et ses propres variables d'état (indépendantes des autres utilisateurs).
        """
        self.pression = 20.0       # en bar
        self.temperature = 473.15  # en K
        self.composition = np.array([]) 
        self.add_inertes = dict()
        self.species = [
            'H2', 'H2O', 'B2CO', 'CO2', 'C2H2T', 'C2H4Z', 
            'CH4', 'C2H6', 'C3H8', 'C4H10', 'C5H12-1', 'O2', 'N2', 
            'C3H6Y', 'nC4H8Y', 'C6H14-1', 'C10H22-1', 'C12H26-1'
        ]

        # on ajoute le dossier actuel à la liste des répertoires de données de Cantera 
        src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel
        dossier = src / 'data' # Construit le chemin vers le dossier "data" à partir du dossier actuel
        ct.add_data_directory(str(dossier)) # Ajoute le dossier à la liste des répertoires de données de Cantera

        # on essaie de charger les données de la réaction de combustion à partir du fichier "output_convert.yaml" et de créer un objet "gas" par défaut à partir de ces données.        
        try: 
            self.gas = ct.Solution(yaml_filename) # crée un objet "gas" par défaut à partir du fichier "output_convert.yaml"
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement des données Cantera: {e}")
        
        
        
    # Cette fonction est le point d'entrée principal de l'application Streamlit. 
    # Elle prend en entrée un dictionnaire "data" contenant les paramètres de la simulation (température, pression, composition du carburant, gaz inertes) fournis par l'utilisateur
    # Elle renvoie les premières LIE/LSE déterminées à partir des données fournies.
    def start(self, data: dict): 
        """
        Met à jour l'état à partir des entrées de l'utilisateur et calcule la première LIE/LSE.
        """
        c = self.gas.X.copy() # tableau contenant tous les éléments du gaz
        
        for sp, value in data["FUEL"].items(): # data[FUEL] est un dictionnaire contenant les espèces utilisées et leurs pourcentages respectifs dans le carburant
            idx = self.gas.species_index(sp) # index de l'espèce dans l'objet "gas" de Cantera
            c[idx] = value / 100 # on convertit les pourcentages en fractions molaires
            
        self.temperature = data["TEMP"]
        self.pression = data["PRES"]
        p_pa = self.pression * 100000 # conversion de la pression de "bar" à "Pa"
        
        # Mise à jour de l'objet Cantera
        self.gas.TPX = self.temperature, p_pa, c 
        
        # Enregistrement dans l'état de l'instance
        self.composition = self.get_composition()
        self.add_inertes = data.get("INERTES", {})
        
        temperatures = critere_T(self) # calcul des températures critiques à partir des données chargées
        
        return lie_lse(self, temperatures[0], temperatures[1]) # calcul des LIE/LSE à partir des températures critiques et de l'état actuel du gaz, et retour des résultats



    # Cette fonction récupère la composition du mélange
    def get_composition(self) -> NDArray[np.float64]:
        """Récupère la composition du mélange courant."""
        composition = self.gas.X.copy()  # tableau contenant tous les éléments du gaz
        composition = np.insert(composition, 0, np.nan)  # ajoute None en position 0
                
        return np.array(composition, dtype=float) # on convertit la composition en tableau numpy pour faciliter les calculs et on la retourne


    # Cette fonction appelle Cantera pour calculer la température d'équilibre du mélange de gaz à partir du ratio de l'air/carburant (equivalence_ratio) 
    # et des propriétés du gaz (température, pression, composition) stockées dans les variables globales. 
    # Elle retourne la température d'équilibre calculée par Cantera.
    def equilibrium(self, equivalence_ratio: float, fuel: dict) -> float: 
        """Calcule la température d'équilibre du mélange de gaz."""
        
        # On définit les conditions initiales avant l'équilibre
        self.gas.TPX = self.temperature, self.pression * 100000, self.composition[1:] 

        # on définit le ratio de l'air/carburant pour le mélange de gaz en ajoutant les gaz inertes (s'il y en a) à l'oxydant (air) dans la fonction set_equivalence_ratio de Cantera
        somme_inertes = sum(self.add_inertes.values())
        if somme_inertes > 0.0:
            self.gas.set_equivalence_ratio(
                phi=equivalence_ratio,
                fuel=fuel,
                oxidizer={'O2': 1, 'N2': 3.76},
                diluent=self.add_inertes,
                fraction={"diluent": somme_inertes}
            )
        else:
            self.gas.set_equivalence_ratio(
                phi=equivalence_ratio,
                fuel=fuel,
                oxidizer={'O2': 1, 'N2': 3.76}
            )           
            
        # on calcule l'état d'équilibre à température et pression constantes
        self.gas.equilibrate('HP')       
          
        # on retourne la température d'équilibre
        return self.gas.T 


    def calcul_plage(self, t_min: float, t_max: float, dt: float, p_min: float, p_max: float, dp: float, precision_temp: float, precision_phi: float) -> pd.DataFrame:
            """Calcule les limites d'explosivité sur une plage de température et pression."""
            results = []
            
            # Génération des plages de température et de pression
            p_range = np.arange(p_min, p_max + dp, dp)
            t_range = np.arange(t_min, t_max + dt, dt)
            
            for p_val in p_range:
                for t_val in t_range:
                    
                    # Mise à jour des variables d'instance
                    self.pression = p_val
                    self.temperature = t_val + 273.15
                    
                    # Calcul des températures critiques et des limites d'explosivité pour chaque combinaison de température et de pression
                    temperatures = critere_T(self)
                    res = lie_lse(self, temperatures[0], temperatures[1], precision_temp, precision_phi)
                    
                    # si la limite d'explosivité n'est pas déterminée (val_OK != 1), on retourne NaN pour la LIE ou la LSE
                    val_lie = res["LIE"][4] if res and res.get("LIE") is not None else np.nan
                    val_lse = res["LSE"][4] if res and res.get("LSE") is not None else np.nan   
                    
                    results.append({
                        "T (°C)": t_val,
                        "P (bar)": p_val,
                        "LIE": val_lie,
                        "LSE": val_lse
                    })
                    
            return pd.DataFrame(results)


