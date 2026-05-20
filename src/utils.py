import numpy as np
from numpy.typing import NDArray
import pandas as pd
import cantera as ct
from pathlib import Path

from core.Critere_T import critere_T
from core.LIE_LSE_V2 import lie_lse

global pression, temperature, composition, species, add_inertes, gas
pression = 20.0 # pression initiale en bar (~20 atm)
temperature = 473.15 # température initiale en K (200 °C) 
composition = dict() # dictionnaire pour stocker la composition du mélange de gaz (en fraction molaire)
species = [
    'H2', 'H2O', 'B2CO', 'CO2', 'C2H2T', 'C2H4Z', 
    'CH4', 'C2H6', 'C3H8', 'C4H10', 'C5H12-1', 'O2', 'N2', 
    'C3H6Y', 'nC4H8Y', 'C6H14-1', 'C10H22-1', 'C12H26-1'
]
add_inertes = dict() # dictionnaire pour stocker les gaz inertes ajoutés par l'utilisateur et leurs quantités respectives (en fraction molaire)

# on ajoute le dossier actuel à la liste des répertoires de données de Cantera 
src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel
dossier = src / 'data' # Construit le chemin vers le dossier "data" à partir du dossier actuel
ct.add_data_directory(str(dossier)) # Ajoute le dossier à la liste des répertoires de données de Cantera

# on essaie de charger les données de la réaction de combustion à partir du fichier "output_convert.yaml" et de créer un objet "gas" par défaut à partir de ces données.
try: 
    gas = ct.Solution("output_convert.yaml") # crée un objet "gas" par défaut à partir du fichier "output_convert.yaml"
except Exception as e:
    print(f"Error loading data: {e}")



# Cette fonction est le point d'entrée principal de l'application Streamlit. 
# Elle prend en entrée un dictionnaire "data" contenant les paramètres de la simulation (température, pression, composition du carburant, gaz inertes) fournis par l'utilisateur
# Elle renvoie les premières LIE/LSE déterminées à partir des données fournies.
def main_streamlit(data: dict): 
    global pression, temperature, composition, add_inertes # On déclare qu'on va modifier les globales
            
    # on met à jour la composition du gaz puis la température et la pression à partir des données fournies par l'utilisateur via Streamlit
    c = gas.X.copy()  # # tableau contenant tous les éléments du gaz
    for sp, value in data["FUEL"].items(): # data[FUEL] est un dictionnaire contenant les espèces utilisées et leurs pourcentages respectifs dans le carburant
        idx = gas.species_index(sp) # index de l'espèce dans l'objet "gas" de Cantera
        c[idx] = value / 100 # on convertit les pourcentages en fractions molaires
    t = data["TEMP"] # température en K
    p = data["PRES"] * 100000 # conversion de la pression de "bar" à "Pa"
    gas.TPX = t, p, c # on met à jour la température, la pression et la composition du gaz, Cantera recalcule le reste des valeurs
            
    # On initialise les variables globales
    pression = gas.P / 100000 # conversion de la pression de "Pa" à "bar"
    temperature = gas.T
    composition = get_composition(gas)
    add_inertes = data["INERTES"]
    
    # on récupère les températures critiques à partir des données chargées
    temperatures = critere_T() 
    
    # On renvoie les premières LIE/LSE déterminées à partir des résultats des calculs précédents
    return lie_lse(gas, temperatures[0], temperatures[1])


# Cette fonction récupère la composition d'un mélange
def get_composition(gas: ct.Solution) -> NDArray[np.float64]:
    composition = gas.X.copy()  # tableau contenant tous les éléments du gaz
    composition = np.insert(composition, 0, np.nan)  # ajoute None en position 0
            
    return np.array(composition, dtype=float) # on convertit la composition en tableau numpy pour faciliter les calculs et on la retourne


# Cette fonction appelle Cantera pour calculer la température d'équilibre du mélange de gaz à partir du ratio de l'air/carburant (equivalence_ratio) 
# et des propriétés du gaz (température, pression, composition) stockées dans les variables globales. 
# Elle retourne la température d'équilibre calculée par Cantera.
def equilibrium(gas: ct.Solution, equivalence_ratio: float, fuel: dict) -> float: 
    
    # on définit la température, la pression et la composition du mélange de gaz à partir des variables globales
    gas.TPX = temperature, pression * 100000, composition[1:] 

    # on définit le ratio de l'air/carburant pour le mélange de gaz en ajoutant les gaz inertes (s'il y en a) à l'oxydant (air) dans la fonction set_equivalence_ratio de Cantera
    if sum(add_inertes.values()) > 0.0:
        gas.set_equivalence_ratio(
            phi=equivalence_ratio,
            fuel=fuel,
            oxidizer={'O2': 1, 'N2': 3.76},
            diluent=add_inertes,
            fraction={"diluent": sum(add_inertes.values())}
        )
    else:
        gas.set_equivalence_ratio(
            phi=equivalence_ratio,
            fuel=fuel,
            oxidizer={'O2': 1, 'N2': 3.76}
        )       
        
    # on calcule l'état d'équilibre à température et pression constantes
    gas.equilibrate('HP') 
    
    # on retourne la température d'équilibre
    return gas.T 


# Cette fonction calcule les limites d'explosivité (LIE et LSE) pour un mélange de gaz en fonction de différentes températures et pressions.            
def calcul_plage(t_min: float, t_max: float, dt: float, p_min: float, p_max: float, dp: float) -> pd.DataFrame:
    global pression, temperature
    
    results =[]
    
    # Création des plages
    p_range = np.arange(p_min, p_max + dp, dp)
    t_range = np.arange(t_min, t_max + dt, dt)
    
    for p_val in p_range:
        for t_val in t_range:
            # Mise à jour des variables globales
            pression = p_val
            temperature = t_val + 273.15
            
            # Mise à jour du gaz
            gas.TP = temperature, pression * 100000 
            
            # Calcul
            temperatures = critere_T()
            res = lie_lse(gas, temperatures[0], temperatures[1])
            
            # Stockage
            results.append({
                "T (°C)": t_val,
                "P (bar)": p_val,
                "LIE": res['LIE'][4],
                "LSE": res['LSE'][4]
            })
            
    return pd.DataFrame(results)


