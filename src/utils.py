import numpy as np
from numpy.typing import NDArray
import cantera as ct

global pression, temperature, composition, species, add_inertes
pression = 20.265 # pression initiale en bar (20 atm)
temperature = 473.15 # température initiale en K (200 °C) 
composition = dict() # dictionnaire pour stocker la composition du mélange de gaz (en fraction molaire)
species = ['H2','H2O', 'B2CO', 'CO2', 'C2H2T', 'C2H4Z', 'CH4', 'C2H6', 'C3H8','C4H10','C5H12-1', 'O2', 'N2']
add_inertes = dict() # dictionnaire pour stocker les gaz inertes ajoutés par l'utilisateur et leurs quantités respectives (en fraction molaire)


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



