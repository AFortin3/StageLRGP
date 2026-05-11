import numpy as np
from numpy.typing import NDArray
from cantera import Solution
from scipy.optimize import brentq

import utils

# On calcule les LIE/LSE du mélange (subroutine LIE_LSE_V2.f90)
def lie_lse_brentq(gas: Solution, T_Low: float, T_High: float) -> dict:
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
    
    
    
    
    # On définit la fonction objective que brentq va tenter de "nullifier"
    def objective_function(phi, gas, fuel, T_target):
        print(f"\nCalcul pour phi = {phi:.4f}...")
        """
        Cette fonction est appelée par brentq. 
        Elle renvoie la différence entre la température d'équilibre et la cible.
        """
        T_calc = utils.equilibrium(gas, phi, fuel)
        return T_calc - T_target
    
        
    # --- PHASE 1 - RECHERCHE DE LA LIE ---
    print("############################### PHASE 1 - RECHERCHE DE LA LIE #################################")

    # Bornes initiales
    phi_down = 0.01
    phi_up = 1.0
    T_target = T_Low

    print(f"\nRecherche de la LIE :")
    print(f"Température cible : {T_target:.2f} K")
    print(f"Intervalle de recherche de phi : [{phi_down}, {phi_up}]")

    try:
        # Appel à brentq
        # args=(...) permet de passer les paramètres supplémentaires à la fonction objective
        # xtol est la précision souhaitée sur l'équivalence ratio (phi)
        phi_lie = brentq(objective_function, phi_down, phi_up, args=(gas, fuel, T_target), xtol=1e-4)
        
        print(f"Convergence réussie ! Equivalence ratio trouvé : {phi_lie:.4f}")
        
        # Calcul final de la composition 
        # On utilise le phi_lie trouvé pour fixer l'état final du gaz
        if sum(utils.add_inertes.values()) > 0.0:
            gas.set_equivalence_ratio(phi=phi_lie, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76}, 
                                    diluent=utils.add_inertes, fraction={"diluent": sum(utils.add_inertes.values())})
        else:
            gas.set_equivalence_ratio(phi=phi_lie, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76})
        
        gas()
        
        composition_1 = utils.get_composition(gas)
        tableau = composition_1.copy()
        
        # Calcul de la LIE (Somme des combustibles + inertes pondérés)
        indices_combustibles = [1, 3, 5, 6, 7, 8, 9, 10, 11]
        lie_sum = sum(tableau[i] for i in indices_combustibles)
        
        print(f"Contribution des combustibles : {lie_sum:.4f}")
        
        contrib_inertes = (ratio_N2 + ratio_O2 + ratio_CO2 + ratio_H2O) * tableau[repere]
        print(f"Contribution des inertes : {contrib_inertes:.4f}")
        
        lie_final = 100. * (lie_sum + contrib_inertes)
        print(f"Limite inférieure d'explosivité (LIE) : {lie_final:.4f}")
        
        resultat['LIE'] = (round(phi_lie, 4), utils.pression, utils.temperature - 273.15, float(T_Low), float(lie_final))

    except ValueError as e:
        print(f"Erreur de convergence : {e}")
        print("L'intervalle choisi ne permet pas de trouver un zéro (les signes aux bornes sont peut-être identiques).")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
            
    
    
    # --- PHASE 2 - RECHERCHE DE LA LSE ---
    print("############################### PHASE 2 - RECHERCHE DE LA LSE #################################")

    # Bornes initiales pour la LSE (zone riche)
    phi_down = 1.0
    phi_up = 50.0
    T_target_high = T_High

    print(f"\nRecherche de la LSE :")
    print(f"Température cible : {T_target_high:.2f} K")
    print(f"Intervalle de recherche de phi : [{phi_down}, {phi_up}]")

    try:
        # Appel à brentq
        # On cherche phi tel que T_calc(phi) - T_High = 0
        phi_lse = brentq(objective_function, phi_down, phi_up, args=(gas, fuel, T_target_high), xtol=1e-2)
        
        print(f"Convergence réussie ! Equivalence ratio trouvé : {phi_lse:.4f}")
        
        # Calcul final de la composition
        if sum(utils.add_inertes.values()) > 0.0:
            gas.set_equivalence_ratio(phi=phi_lse, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76}, 
                                    diluent=utils.add_inertes, fraction={"diluent": sum(utils.add_inertes.values())})
        else:
            gas.set_equivalence_ratio(phi=phi_lse, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76})

        gas() 
        
        composition_1 = utils.get_composition(gas)
        tableau = composition_1.copy()
        
        # Calcul de la LSE (Même logique de sommation que pour la LIE)
        indices_combustibles = [1, 3, 5, 6, 7, 8, 9, 10, 11]
        lse_sum = sum(tableau[i] for i in indices_combustibles)
        
        print(f"Contribution des combustibles : {lse_sum:.4f}")
        
        contrib_inertes = (ratio_N2 + ratio_O2 + ratio_CO2 + ratio_H2O) * tableau[repere]
        print(f"Contribution des inertes : {contrib_inertes:.4f}")
        
        lse_final = 100. * (lse_sum + contrib_inertes)
        print(f"Limite supérieure d'explosivité (LSE) : {lse_final:.4f}")
        
        resultat['LSE'] = (round(phi_lse, 4), utils.pression, utils.temperature - 273.15, float(T_High), float(lse_final))

    except ValueError as e:
        print(f"Erreur de convergence LSE : {e}")
        print("Vérifiez que T_High est bien compris entre la température à phi=1 et phi=50.")
    except Exception as e:
        print(f"Une erreur est survenue lors du calcul de la LSE : {e}")

    # Enfin, on retourne le dictionnaire complet
    return resultat





