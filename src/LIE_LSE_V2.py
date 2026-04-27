import numpy as np
from numpy.typing import NDArray
from cantera import Solution

import utils

# On calcule les LIE/LSE du mélange (subroutine LIE_LSE_V2.f90)
def lie_lse(gas: Solution, composition: NDArray[np.float64], T_Low: float, T_High: float) -> dict:
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
    
    if composition[1] >= 1.0e-6:          # H2
        repere = 1
    elif composition[7] >= 1.0e-6:        # CH4
        repere = 7
    elif composition[8] >= 1.0e-6:        # C2H6
        repere = 8
    elif composition[3] >= 1.0e-6:        # B2CO
        repere = 3
    elif composition[9] >= 1.0e-6:        # C3H8
        repere = 9
    elif composition[10] >= 1.0e-6:       # C4H10
        repere = 10
    elif composition[11] >= 1.0e-6:       # C5H12-1
        repere = 11
    elif composition[5] >= 1.0e-6:        # C2H2T
        repere = 5
    elif composition[6] >= 1.0e-6:        # C2H4Z
        repere = 6
    else:
        raise ValueError("Aucun combustible dominant détecté.")

    if composition[13] >= 1.0e-8:
        ratio_N2 = composition[13] / composition[repere]
    if composition[12] >= 1.0e-8:
        ratio_O2 = composition[12] / composition[repere]
    if composition[4] >= 1.0e-8:
        ratio_CO2 = composition[4] / composition[repere]
    if composition[2] >= 1.0e-8:
        ratio_H2O = composition[2] / composition[repere]
    
    
    # décalage pour prendre en compte la temperature
    # repere = repere + 1 
    # inutile en python, la température est stockée en tableau[0] qui vaut None au départ
    # évidemment, cela a demandé d'adapter les indexations dans la suite du calcul
        
        
    # Phase 1 - Recherche de la LIE
    equivalence_ratio_up    = 1.0
    equivalence_ratio_down  = 0.01
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
     
    tableau = composition.copy()
    tableau[0] = 2000.0 # on place la température dans l'index 0 du tableau (qui contenait la valeur None de composition[0])
    precision = 2.0
    val_OK = 0
    
    while ( abs( T_Low - tableau[0] ) >= precision ):
        
        tableau[0] = utils.equilibrium(gas, equivalence_ratio) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
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
        lie = tableau[1] + tableau[3] + tableau[5] + tableau[6] + tableau[7] + tableau[8] + tableau[9] + tableau[10] + tableau[11]
        lie = lie + ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]
        lie = 100. * lie
        resultat['LIE'] = round(equivalence_ratio, 4) , utils.pression , utils.temperature - 273.15 , float(T_Low) , float(lie) #, 100.*Add_CO2 , 100.*Add_N2 , 100.*Add_H2O 
        
    
    # Phase 2 - Recherche de la LSE
    equivalence_ratio_up    = 50.0
    equivalence_ratio_down  = 1.0
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
    
    tableau[0] = 100.0
    precision = 2.0
    val_OK = 0
    
    while ( abs( T_High - tableau[0] ) >= precision ):
        
        tableau[0] = utils.equilibrium(gas, equivalence_ratio) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
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
        lse = tableau[1] + tableau[3] + tableau[5] + tableau[6] + tableau[7] + tableau[8] + tableau[9] + tableau[10] + tableau[11]
        lse = lse + ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]
        lse = 100. * lse
        resultat['LSE'] = round(equivalence_ratio, 4) , utils.pression , utils.temperature - 273.15 , float(T_High) , float(lse) #, 100.*Add_CO2 , 100.*Add_N2 , 100.*Add_H2O     
        
    # on retourne le dictionnaire contenant les résultats des calculs
    return resultat 