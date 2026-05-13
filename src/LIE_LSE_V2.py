import numpy as np
from numpy.typing import NDArray
from cantera import Solution

import utils

# On calcule les LIE/LSE du mélange (subroutine LIE_LSE_V2.f90)
def lie_lse(gas: Solution, T_Low: float, T_High: float) -> dict:
    resultat = dict() # les résultats seront stockés dans un dictionnaire avec les clés 'LIE' et 'LSE'
    
    # Presence d'inerte ds le fuel de départ
    # on part du principe qu'il y en aura tjrs au moins = 1.0e-10
    ratio_N2 = 0.0
    ratio_O2 = 0.0
    ratio_CO2 = 0.0
    ratio_H2O = 0.0

    # Ordre des species
    # H2
    # H2O
    # B2CO
    # CO2
    # C2H2T
    # C2H4Z
    # CH4
    # C2H6
    # C3H8
    # C4H10
    # C5H12-1
    # O2
    # N2

    # Recherche de l'indice compositionnel non nul
    repere = 0
    
    if utils.composition[1] >= 1.0e-6:          # H2
        repere = 1
    elif utils.composition[7] >= 1.0e-6:        # CH4
        repere = 7
    elif utils.composition[8] >= 1.0e-6:        # C2H6
        repere = 8
    elif utils.composition[3] >= 1.0e-6:        # B2CO
        repere = 3
    elif utils.composition[9] >= 1.0e-6:        # C3H8
        repere = 9
    elif utils.composition[10] >= 1.0e-6:       # C4H10
        repere = 10
    elif utils.composition[11] >= 1.0e-6:       # C5H12-1
        repere = 11
    elif utils.composition[5] >= 1.0e-6:        # C2H2T
        repere = 5
    elif utils.composition[6] >= 1.0e-6:        # C2H4Z
        repere = 6
    # --- Ajout des nouveaux gaz ---
    elif utils.composition[14] >= 1.0e-6:       # C3H6Y
        repere = 14
    elif utils.composition[15] >= 1.0e-6:       # nC4H8Y
        repere = 15
    elif utils.composition[16] >= 1.0e-6:       # C6H14-1
        repere = 16
    elif utils.composition[17] >= 1.0e-6:       # C10H22-1
        repere = 17
    elif utils.composition[18] >= 1.0e-6:       # C12H26-1
        repere = 18
    else:
        raise ValueError("Aucun combustible dominant détecté.")
    
    if utils.composition[13] >= 1.0e-8:
        ratio_N2 = utils.composition[13] / utils.composition[repere]
    if utils.composition[12] >= 1.0e-8:
        ratio_O2 = utils.composition[12] / utils.composition[repere]
    if utils.composition[4] >= 1.0e-8:
        ratio_CO2 = utils.composition[4] / utils.composition[repere]
    if utils.composition[2] >= 1.0e-8:
        ratio_H2O = utils.composition[2] / utils.composition[repere]
       
        
    # on parcoure les espèces pour trouver les combustibles dominants
    fuel = dict() # initialisation d'un dictionnaire pour stocker le nom du combustible dominant et sa fraction molaire
    
    for i, sp in enumerate(utils.species):
        if utils.composition[i+1] >= 1.0e-6: # on considère qu'une espèce est présente en quantité significative si sa fraction molaire est supérieure ou égale à 1.0e-6
            if sp in ['H2', 'CH4', 'C2H6', 'B2CO', 'C3H8', 'C4H10', 'C5H12-1', 'C2H2T', 'C2H4Z', 'C3H6Y', 'nC4H8Y', 'C6H14-1', 'C10H22-1', 'C12H26-1']: # on ignore les espèces inertes (O2, N2, CO2, H2O) 
                fuel[sp] = utils.composition[i+1]

    if len(fuel) == 0:
        raise ValueError("Aucun combustible dominant détecté.")
    
        
    # Phase 1 - Recherche de la LIE
    equivalence_ratio_up    = 1.0
    equivalence_ratio_down  = 0.01
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
     
    tableau = utils.composition.copy()
    tableau[0] = 2000.0 # on place la température dans l'index 0 du tableau (qui contenait la valeur None de composition[0])
    precision = 2.0
    val_OK = 0
    
    while ( abs( T_Low - tableau[0] ) >= precision ):
        
        tableau[0] = utils.equilibrium(gas, equivalence_ratio, fuel) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
        if ( ( T_Low - tableau[0] ) <= 0.0 ):
            equivalence_ratio_up = equivalence_ratio
        else:
            equivalence_ratio_down = equivalence_ratio
        
        if ( abs( equivalence_ratio_down - 1.0 ) <= 0.03 or abs( equivalence_ratio_up - 0.01 ) <= 0.03 ):
            val_OK = 1
            break
        
        equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
        
        if ( abs( equivalence_ratio_up - equivalence_ratio_down ) <= 0.05 ):
            break
        
    if ( val_OK != 1 ):
        # on appelle la fonction de calcul de la limite d'explosivité pour calculer la LIE à partir du ratio d'équivalence trouvé et des propriétés du gaz
        resultat["LIE"] = calcul_limite(gas, equivalence_ratio, fuel, tableau, T_Low, ratio_N2, ratio_O2, ratio_CO2, ratio_H2O, repere) 
        
    
    # Phase 2 - Recherche de la LSE
    equivalence_ratio_up    = 50.0
    equivalence_ratio_down  = 1.0
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
    
    tableau[0] = 100.0
    precision = 2.0
    val_OK = 0
    
    while ( abs( T_High - tableau[0] ) >= precision ):
        
        tableau[0] = utils.equilibrium(gas, equivalence_ratio, fuel) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
        if ( ( T_High - tableau[0] ) >= 0.0 ):
            equivalence_ratio_up = equivalence_ratio
        else:
            equivalence_ratio_down = equivalence_ratio
        
        if ( abs( equivalence_ratio_up - 1.0 ) <= 0.03 or abs( equivalence_ratio_down - 20.0 ) <= 0.03 ):
            val_OK = 1
            break
        
        equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
        
        if ( abs( equivalence_ratio_up - equivalence_ratio_down ) <= 0.05 ):
            break
        
    if ( val_OK != 1 ):
        # on appelle la fonction de calcul de la limite d'explosivité pour calculer la LSE à partir du ratio d'équivalence trouvé et des propriétés du gaz
        resultat["LSE"] = calcul_limite(gas, equivalence_ratio, fuel, tableau, T_High, ratio_N2, ratio_O2, ratio_CO2, ratio_H2O, repere) 
    
        
    # on retourne le dictionnaire contenant les résultats des calculs
    return resultat 


def calcul_limite(gas, phi, fuel, tableau, T_ref, ratio_N2, ratio_O2, ratio_CO2, ratio_H2O, repere):
    # on ajuste la composition du mélange de gaz à partir du ratio de l'air/carburant en vérifiant la présence de gaz inertes
    if sum(utils.add_inertes.values()) > 0.0:
        gas.set_equivalence_ratio(phi=phi, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76}, diluent=utils.add_inertes, fraction={"diluent": sum(utils.add_inertes.values())})
    else:
        gas.set_equivalence_ratio(phi=phi, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76})
    composition_avec_air = utils.get_composition(gas) 
    composition_avec_air[0] = tableau[0] # on place la température dans l'index 0 de la composition
    tableau = composition_avec_air.copy() # on copie la composition ajustée dans le tableau pour les calculs suivants
    
    limite = sum(tableau[1:]) - (tableau[2] + tableau[4] + tableau[12] + tableau[13]) # on soustrait les gaz inertes pour ne garder que les combustibles
    limite = limite + ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]
    limite = 100. * limite
    return round(phi, 4) , utils.pression , utils.temperature - 273.15 , float(T_ref) , float(limite) #, 100.*Add_CO2 , 100.*Add_N2 , 100.*Add_H2O 
    