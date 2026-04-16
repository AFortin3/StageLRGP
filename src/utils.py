import cantera as ct
import numpy as np
import os

def load_data() -> ct.Solution:
    # on charge le fichier output_convert.yaml qui contient les données converties des fichiers V1_Meca_GE_LIE_LSE.txt et V1_Thermo_GE_LIE_LSE.txt
    dossier = os.path.dirname(os.path.abspath(__file__)) # Récupère le chemin du dossier actuel
    dossier = dossier.replace('src', 'tests') # Remplace l'emplacement actuel par 'data' pour accéder au dossier contenant les fichiers de données
    ct.add_data_directory(dossier) # Ajoute le dossier à la liste des répertoires de données de Cantera
    gas = ct.Solution('output_convert.yaml') # Charge le fichier output_convert.yaml dans Cantera 
    return gas



def equilibrium(phi, fuel, t, p) -> ct.Solution:
    gas = load_data() # On charge les données 
    system_ratio(gas, phi, fuel) # On calcule le ratio de l'air/carburant pour le mélange de gaz
    gas.TP = t, p # On définit la température et la pression du gaz dans le modèle
    gas.equilibrate('HP') # On calcule l'équilibre chimique à enthalpie et pression constantes
    return gas

def t_adiabatique(phi, fuel, t, p) -> float:
    gas = equilibrium(phi, fuel, t, p) # On calcule l'équilibre chimique du mélange de gaz à la température et à la pression données
    return gas.T # On retourne la température adiabatique du gaz à l'équilibre


    


# différents moyens de calculer le ratio de l'air/carburant
def system_ratio(gas: ct.Solution, phi_, fuel_): # marche pour tout type de carburant
    gas.set_equivalence_ratio(phi=phi_, fuel=fuel_, oxidizer={'O2': 0.21, 'N2': 0.79}) # Le ratio est par défaut calculé pour un mélange de 21% d'oxygène et 79% d'azote
    
def system_ratio_old(gas: ct.Solution, phi, fuel): # que pour les hydrocarbures
    # Trouve le nombre d'atomes de chaque élément dans le carburant
    nC = gas.n_atoms(fuel, 'C')
    nH = gas.n_atoms(fuel, 'H')

    N2_ratio = 3.76 # ratio de l'air
    stoich_O2 = nC + 0.25*nH # calcul stoechiométrique de l'oxygène nécessaire pour brûler complètement le carburant
    
    X = np.zeros(gas.n_species) # On crée un tableau de zéros pour stocker les fractions molaires des espèces
    X[gas.species_index(fuel)] = phi # On définit la fraction molaire du carburant à 1 (100%)
    X[gas.species_index('O2')] = stoich_O2 # On définit la fraction molaire de l'oxygène selon le calcul stoechiométrique
    X[gas.species_index('N2')] = stoich_O2 * N2_ratio # On définit la fraction molaire de l'azote selon le ratio de l'air (3.76 fois celui de l'oxygène)
    
    gas.X = X # On met à jour les fractions molaires du gaz dans le modèle