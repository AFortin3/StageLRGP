import cantera as ct
from pathlib import Path

import utils
from Mixture import mixture
from Critere_T import critere_T
from LIE_LSE_V2 import lie_lse

def main_streamlit(data: dict):    
    src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel
    dossier = src.parent / 'data' # Construit le chemin vers le dossier "data" à partir du dossier actuel
    ct.add_data_directory(str(dossier)) # Ajoute le dossier à la liste des répertoires de données de Cantera
    
    fichier = "d1.txt"
    
    try: 
        gas = ct.Solution("output_convert.yaml") # on crée un objet "gas" par défaut à partir du fichier "output_convert.yaml" qui contient les données de la réaction de combustion
    except Exception as e:
        print(f"Error loading data: {e}")
            
    # on met à jour la température, la pression et la composition du gaz à partir des données fournies par l'utilisateur via Streamlit
    gas.TP = data["TEMP"], data["PRES"] * 101300
    composition = gas.X.copy()  # tableau de 172 éléments
    for sp, value in data["FUEL"].items():
        idx = gas.species_index(sp)
        composition[idx] = value / 100 # on convertit les pourcentages en fractions molaires
    gas.X = composition # on met à jour la composition du gaz dans Cantera
    
    # On initialise les variables globales
    utils.pression = gas.P / 100000 # conversion de la pression de "Pa" à "bar"
    utils.temperature = gas.T
    utils.composition = utils.get_composition(gas)
    utils.add_inertes = data["INERTES"]
    
    temperatures = critere_T() # on récupère les températures critiques à partir des données chargées
    
    # On renvoie les premières LIE/LSE déterminées à partir des résultats des calculs précédents
    return lie_lse(gas, temperatures[0], temperatures[1])
