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
    else:
        raise ValueError("Aucun combustible dominant détecté.")
    
    print(f"Repère choisi pour les calculs : {utils.species[repere-1]} (repère {repere}) avec une fraction molaire de {utils.composition[repere]:.2e}")

    if utils.composition[13] >= 1.0e-8:
        ratio_N2 = utils.composition[13] / utils.composition[repere]
    if utils.composition[12] >= 1.0e-8:
        ratio_O2 = utils.composition[12] / utils.composition[repere]
    if utils.composition[4] >= 1.0e-8:
        ratio_CO2 = utils.composition[4] / utils.composition[repere]
    if utils.composition[2] >= 1.0e-8:
        ratio_H2O = utils.composition[2] / utils.composition[repere]
    
    
    # décalage pour prendre en compte la temperature
    # repere = repere + 1 
    # inutile en python, la température est stockée en tableau[0] qui vaut None au départ
    # évidemment, cela a demandé d'adapter les indexations dans la suite du calcul
    
    
    
    # --------------------------------------! PARTIE AJOUTEE !--------------------------------------
    # on parcoure les espèces pour trouver les combustibles dominants
    fuel = dict() # initialisation d'un dictionnaire pour stocker le nom du combustible dominant et sa fraction molaire
    
    for i, sp in enumerate(utils.species):
        if utils.composition[i+1] >= 1.0e-6: # on considère qu'une espèce est présente en quantité significative si sa fraction molaire est supérieure ou égale à 1.0e-6
            if sp in ['H2', 'CH4', 'C2H6', 'B2CO', 'C3H8', 'C4H10', 'C5H12-1', 'C2H2T', 'C2H4Z']: # on ignore les espèces inertes (O2, N2, CO2, H2O) 
                fuel[sp] = utils.composition[i+1]

    if len(fuel) == 0:
        raise ValueError("Aucun combustible dominant détecté.")
    # --------------------------------------! PARTIE AJOUTEE !--------------------------------------
    
    
    
        
    # Phase 1 - Recherche de la LIE
    print("###############################PHASE 1 - RECHERCHE DE LA LIE#################################")
    
    equivalence_ratio_up    = 1.0
    equivalence_ratio_down  = 0.01
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
    
    print(f"\nRecherche de la LIE :\nEquivalence ratio initial : {equivalence_ratio:.4f} (entre {equivalence_ratio_down:.4f} et {equivalence_ratio_up:.4f})")
     
    tableau = utils.composition.copy()
    tableau[0] = 2000.0 # on place la température dans l'index 0 du tableau (qui contenait la valeur None de composition[0])
    precision = 2.0
    val_OK = 0
    
    print(f"Température cible pour la LIE : {T_Low:.2f} K")
    
    while ( abs( T_Low - tableau[0] ) >= precision ):
        
        print("=============================================================================================")
        print(f"Equivalence ratio : {equivalence_ratio:.4f} (entre {equivalence_ratio_down:.4f} et {equivalence_ratio_up:.4f})")
        
        
        tableau[0] = utils.equilibrium(gas, equivalence_ratio, fuel) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
        if ( ( T_Low - tableau[0] ) <= 0.0 ):
            equivalence_ratio_up = equivalence_ratio
            print(f"Température calculée {tableau[0]:.2f} K est supérieure ou égale à la température cible {T_Low:.2f} K, on ajuste la borne supérieure de l'équivalence ratio à {equivalence_ratio_up:.4f}")
        else:
            equivalence_ratio_down = equivalence_ratio
            print(f"Température calculée {tableau[0]:.2f} K est inférieure à la température cible {T_Low:.2f} K, on ajuste la borne inférieure de l'équivalence ratio à {equivalence_ratio_down:.4f}")
        
        if ( abs( equivalence_ratio_down - 1.0 ) <= 0.03 or abs( equivalence_ratio_up - 0.01 ) <= 0.03 ):
            print("fin chelou")
            print("=============================================================================================")
            val_OK = 1
            break
        
        equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
        print(f"Nouvelle équivalence ratio : {equivalence_ratio:.4f} (entre {equivalence_ratio_down:.4f} et {equivalence_ratio_up:.4f})")
                
        if ( abs( equivalence_ratio_up - equivalence_ratio_down ) <= 0.05 ):
            print("Différence entre les bornes d'équivalence ratio inférieure et supérieure inférieure ou égale à 0.05, on arrête la recherche de la LIE.")
            print("=============================================================================================")
            break
        
        print("=============================================================================================")
        
    if ( val_OK != 1 ):
        print("Calcul de la LIE :")
        
        # on ajuste la composition du mélange de gaz à partir du ratio de l'air/carburant et on la récupère
        gas.set_equivalence_ratio(phi=equivalence_ratio, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76})        
        composition_avec_air = utils.get_composition(gas) 
        composition_avec_air[0] = tableau[0] # on place la température dans l'index 0 de la composition
        tableau = composition_avec_air.copy() # on copie la composition ajustée dans le tableau pour les calculs suivants
        
        # on calcule la LIE 
        lie = tableau[1] + tableau[3] + tableau[5] + tableau[6] + tableau[7] + tableau[8] + tableau[9] + tableau[10] + tableau[11]
        print(f"Contribution des combustibles : {lie:.4f}")
        lie = lie + ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]
        print(f"Contribution des inertes : {ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]:.4f}")
        lie = 100. * lie
        print(f"Limite inférieure d'explosivité (LIE) : {lie:.4f}")
        resultat['LIE'] = round(equivalence_ratio, 4) , utils.pression , utils.temperature - 273.15 , float(T_Low) , float(lie) #, 100.*Add_CO2 , 100.*Add_N2 , 100.*Add_H2O 
        
    
    # Phase 2 - Recherche de la LSE
    print("###############################PHASE 2 - RECHERCHE DE LA LSE#################################")
    
    equivalence_ratio_up    = 50.0
    equivalence_ratio_down  = 1.0
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
    
    print(f"\nRecherche de la LSE :\nEquivalence ratio initial : {equivalence_ratio:.4f} (entre {equivalence_ratio_down:.4f} et {equivalence_ratio_up:.4f})")
    
    tableau[0] = 100.0
    precision = 2.0
    val_OK = 0
    
    print(f"Température cible pour la LSE : {T_High:.2f} K")
    
    while ( abs( T_High - tableau[0] ) >= precision ):
        
        print("=============================================================================================")
        print(f"Equivalence ratio : {equivalence_ratio:.4f} (entre {equivalence_ratio_down:.4f} et {equivalence_ratio_up:.4f})")
        
        tableau[0] = utils.equilibrium(gas, equivalence_ratio, fuel) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
        if ( ( T_High - tableau[0] ) >= 0.0 ):
            equivalence_ratio_up = equivalence_ratio
            print(f"Température calculée {tableau[0]:.2f} K est inférieure ou égale à la température cible {T_High:.2f} K, on ajuste la borne supérieure de l'équivalence ratio à {equivalence_ratio_up:.4f}")
        else:
            equivalence_ratio_down = equivalence_ratio
            print(f"Température calculée {tableau[0]:.2f} K est supérieure à la température cible {T_High:.2f} K, on ajuste la borne inférieure de l'équivalence ratio à {equivalence_ratio_down:.4f}")
        
        if ( abs( equivalence_ratio_up - 1.0 ) <= 0.03 or abs( equivalence_ratio_down - 20.0 ) <= 0.03 ):
            print("fin chelou")
            print("=============================================================================================")
            val_OK = 1
            break
        
        equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
        print(f"Nouvelle équivalence ratio : {equivalence_ratio:.4f} (entre {equivalence_ratio_down:.4f} et {equivalence_ratio_up:.4f})")

        
        if ( abs( equivalence_ratio_up - equivalence_ratio_down ) <= 0.05 ):
            print("Différence entre les bornes d'équivalence ratio inférieure et supérieure inférieure ou égale à 0.05, on arrête la recherche de la LIE.")
            print("=============================================================================================")
            break
        
        print("=============================================================================================")
        
    if ( val_OK != 1 ):
        print("Calcul de la LSE :")
        
        # on ajuste la composition du mélange de gaz à partir du ratio de l'air/carburant et on la récupère
        gas.set_equivalence_ratio(phi=equivalence_ratio, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76})
        composition_avec_air = utils.get_composition(gas) 
        composition_avec_air[0] = tableau[0] # on place la température dans l'index 0 de la composition
        tableau = composition_avec_air.copy() # on copie la composition ajustée dans le tableau pour les calculs suivants
        
        # on calcule la LSE
        lse = tableau[1] + tableau[3] + tableau[5] + tableau[6] + tableau[7] + tableau[8] + tableau[9] + tableau[10] + tableau[11]
        print(f"Contribution des combustibles : {lse:.4f}")
        lse = lse + ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]
        print(f"Contribution des inertes : {ratio_N2 * tableau[repere] + ratio_O2 * tableau[repere] + ratio_CO2 * tableau[repere] + ratio_H2O * tableau[repere]:.4f}")
        lse = 100. * lse
        print(f"Limite supérieure d'explosivité (LSE) : {lse:.4f}")
        resultat['LSE'] = round(equivalence_ratio, 4) , utils.pression , utils.temperature - 273.15 , float(T_High) , float(lse) #, 100.*Add_CO2 , 100.*Add_N2 , 100.*Add_H2O     
        
    # on retourne le dictionnaire contenant les résultats des calculs
    return resultat 





