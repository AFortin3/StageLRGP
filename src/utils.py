import numpy as np
from numpy.typing import NDArray
import cantera as ct
from pathlib import Path

global pression, temperature, species #, add_inertes
species = ['H2','H2O', 'B2CO', 'CO2', 'C2H2T', 'C2H4Z', 'CH4', 'C2H6', 'C3H8','C4H10','C5H12-1', 'O2', 'N2']


# Cette fonction récupère la composition d'un mélange
def get_composition(gas: ct.Solution) -> NDArray[np.float64]:
    composition = [None] # initialisation de la liste de composition (avec composition[0] = None pour éviter les erreurs d'indexation)
    
    for sp in species: 
        if sp in gas.species_names:
            composition.append(gas.X[gas.species_index(sp)]) # on ajoute la fraction molaire de chaque espèce à la composition
            
    return np.array(composition, dtype=float) # on convertit la composition en tableau numpy pour faciliter les calculs et on la retourne


# Cette fonction appelle Cantera pour calculer la température d'équilibre du mélange de gaz à partir du ratio de l'air/carburant (equivalence_ratio) 
# et des propriétés du gaz (température, pression, composition) stockées dans la variable gas. 
# Elle retourne la température d'équilibre calculée par Cantera.
def equilibrium(gas: ct.Solution, equivalence_ratio: float) -> float: 
    # on crée une copie du gaz pour ne pas modifier les données originales et on replace les propriétés du gaz (température, pression, composition) dans la copie  
    gas_copy = ct.Solution(gas.source) 
    gas_copy.TP = gas.TP
    gas_copy.X = gas.X
    composition = get_composition(gas_copy) # on récupère la composition du mélange à partir de la copie du gaz 

    # on parcoure les espèces pour trouver les combustibles dominants
    fuel = dict() # initialisation d'un dictionnaire pour stocker le nom du combustible dominant et sa fraction molaire
    
    for i, sp in enumerate(species):
        if composition[i+1] >= 1.0e-6: # on considère qu'une espèce est présente en quantité significative si sa fraction molaire est supérieure ou égale à 1.0e-6
            if sp in ['H2', 'CH4', 'C2H6', 'B2CO', 'C3H8', 'C4H10', 'C5H12-1', 'C2H2T', 'C2H4Z']: # on ignore les espèces inertes (O2, N2, CO2, H2O) 
                fuel[sp] = composition[i+1]

    if len(fuel) == 0:
        raise ValueError("Aucun combustible dominant détecté.")
    
    # on normalise les fractions molaires des combustibles dominants pour que leur somme soit égale à 1 (pour que Cantera puisse les utiliser correctement)
    s = sum(fuel.values())
    fuel = {key: value / s for key, value in fuel.items()}
    
    gas_copy.set_equivalence_ratio(phi=equivalence_ratio, fuel=fuel, oxidizer={'O2': 0.21, 'N2': 0.79}) # on définit le ratio de l'air/carburant pour le mélange de gaz
    
    gas_copy.equilibrate('HP') # on calcule l'état d'équilibre à température et pression constantes
    
    # on retourne la température d'équilibre
    return gas_copy.T

# Cette fonction crée un fichier (nom du fichier d'entrée ou results.txt par défaut) et y écrit les résultats des calculs de limites d'explosivité (LIE/LSE).
def write_results(limites_list: list, fichier: str = "results.txt") -> None:
    src = Path(__file__).resolve().parent
    chemin = src.parent / 'data' / fichier # on construit le chemin vers le fichier de résultats à partir du dossier actuel et du dossier "data"
    
    with open(chemin, "w") as f: # on ouvre le fichier en mode écriture (il sera créé s'il n'existe pas ou écrasé s'il existe déjà)
        for limites in limites_list:
            f.write(f"\nLimites d'explosivité à P = {limites['LIE'][1]} bar et T = {limites['LIE'][2]} °C :\n"
                    f"LIE = {limites['LIE'][4]} pour un ratio d'équivalence de Phi_Low  = {limites['LIE'][0]} et une température critique T_Low  = {limites['LIE'][3]} °C\n"
                    f"LSE = {limites['LSE'][4]} pour un ratio d'équivalence de Phi_High = {limites['LSE'][0]} et une température critique T_High = {limites['LSE'][3]} °C\n")


