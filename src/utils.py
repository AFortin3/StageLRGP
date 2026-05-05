import numpy as np
from numpy.typing import NDArray
import cantera as ct
from pathlib import Path

global pression, temperature, composition, species, add_inertes
species = ['H2','H2O', 'B2CO', 'CO2', 'C2H2T', 'C2H4Z', 'CH4', 'C2H6', 'C3H8','C4H10','C5H12-1', 'O2', 'N2']
add_inertes = dict() # dictionnaire pour stocker les gaz inertes ajoutés par l'utilisateur et leurs quantités respectives (en fraction molaire)


# Cette fonction récupère la composition d'un mélange
def get_composition(gas: ct.Solution) -> NDArray[np.float64]:
    composition = gas.X.copy()  # tableau de 172 éléments
    composition = np.insert(composition, 0, np.nan)  # ajoute None en position 0
            
    return np.array(composition, dtype=float) # on convertit la composition en tableau numpy pour faciliter les calculs et on la retourne


# Cette fonction appelle Cantera pour calculer la température d'équilibre du mélange de gaz à partir du ratio de l'air/carburant (equivalence_ratio) 
# et des propriétés du gaz (température, pression, composition) stockées dans les variables globales. 
# Elle retourne la température d'équilibre calculée par Cantera.
def equilibrium(gas: ct.Solution, equivalence_ratio: float, fuel: dict) -> float: 
    
    # on définit la température, la pression et la composition du mélange de gaz à partir des variables globales
    gas.TPX = temperature, pression * 101325, composition[1:] 

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


# Cette fonction crée un fichier (nom du fichier d'entrée ou results.txt par défaut) et y écrit les résultats des calculs de limites d'explosivité (LIE/LSE).
def write_results(limites_list: list, fichier: str = "results.txt") -> None:
    src = Path(__file__).resolve().parent
    chemin = src.parent / 'data' / fichier # on construit le chemin vers le fichier de résultats à partir du dossier actuel et du dossier "data"
    
    with open(chemin, "w") as f: # on ouvre le fichier en mode écriture (il sera créé s'il n'existe pas ou écrasé s'il existe déjà)
        for limites in limites_list:
            f.write(f"\nLimites d'explosivité à P = {limites['LIE'][1]} bar et T = {limites['LIE'][2]} °C :\n"
                    f"LIE = {limites['LIE'][4]} pour un ratio d'équivalence de Phi_Low  = {limites['LIE'][0]} et une température critique T_Low  = {limites['LIE'][3]} °C\n"
                    f"LSE = {limites['LSE'][4]} pour un ratio d'équivalence de Phi_High = {limites['LSE'][0]} et une température critique T_High = {limites['LSE'][3]} °C\n")


