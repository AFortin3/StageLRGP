import cantera as ct
from pathlib import Path

import utils
from Critere_T import critere_T
from LIE_LSE_V2 import lie_lse

# Cette fonction est le point d'entrée principal de l'application Streamlit. 
# Elle prend en entrée un dictionnaire "data" contenant les paramètres de la simulation (température, pression, composition du carburant, gaz inertes) fournis par l'utilisateur
# Elle renvoie les premières LIE/LSE déterminées à partir des données fournies.
def main_streamlit(data: dict): 
    # on ajoute le dossier actuel à la liste des répertoires de données de Cantera 
    src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel
    ct.add_data_directory(str(src)) # Ajoute le dossier à la liste des répertoires de données de Cantera
    
    # on essaie de charger les données de la réaction de combustion à partir du fichier "output_convert.yaml" et de créer un objet "gas" à partir de ces données.
    try: 
        gas = ct.Solution("output_convert.yaml") # crée un objet "gas" par défaut à partir du fichier "output_convert.yaml"
    except Exception as e:
        print(f"Error loading data: {e}")
            
    # on met à jour la composition du gaz puis la température et la pression à partir des données fournies par l'utilisateur via Streamlit
    composition = gas.X.copy()  # # tableau contenant tous les éléments du gaz
    for sp, value in data["FUEL"].items(): # data[FUEL] est un dictionnaire contenant les espèces utilisées et leurs pourcentages respectifs dans le carburant
        idx = gas.species_index(sp) # index de l'espèce dans l'objet "gas" de Cantera
        composition[idx] = value / 100 # on convertit les pourcentages en fractions molaires
    t = data["TEMP"] # température en K
    p = data["PRES"] * 101300 # conversion de la pression de "atm" à "Pa"
    gas.TPX = t, p, composition # on met à jour la température, la pression et la composition du gaz, Cantera recalcule le reste des valeurs
            
    # On initialise les variables globales
    utils.temperature = gas.T
    utils.pression = gas.P / 100000 # conversion de la pression de "Pa" à "bar"
    utils.composition = utils.get_composition(gas)
    utils.add_inertes = data["INERTES"]
    
    temperatures = critere_T() # on récupère les températures critiques à partir des données chargées
    
    # On renvoie les premières LIE/LSE déterminées à partir des résultats des calculs précédents
    return lie_lse(gas, temperatures[0], temperatures[1])
