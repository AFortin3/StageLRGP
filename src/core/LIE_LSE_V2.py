# On calcule les LIE/LSE du mélange (subroutine LIE_LSE_V2.f90)
def lie_lse(gsim, T_Low: float, T_High: float, temp_precision=0.05, phi_precision=0.005) -> dict:
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
        
    # on parcoure les espèces pour trouver les combustibles dominants
    fuel = dict() # initialisation d'un dictionnaire pour stocker le nom du combustible dominant et sa fraction molaire
    
    for i, sp in enumerate(gsim.species):
        if gsim.composition[i+1] >= 1.0e-6: # on considère qu'une espèce est présente en quantité significative si sa fraction molaire est supérieure ou égale à 1.0e-6
            if sp not in ['O2', 'N2', 'CO2', 'H2O']: # on ignore les espèces inertes (O2, N2, CO2, H2O)
                fuel[sp] = gsim.composition[i+1]                

    if len(fuel) == 0:
        raise ValueError("Aucun combustible dominant détecté.")
    
    
    fuel_quantity = sum(fuel.values()) # on calcule la quantité totale de combustible en sommant les fractions molaires des espèces dominantes
    
    # on calcule les ratios d'inertes par rapport au combustible dominant (repere) pour les espèces inertes présentes en quantité significative
    if gsim.composition[13] >= 1.0e-8:
        ratio_N2 = gsim.composition[13] / fuel_quantity
    if gsim.composition[12] >= 1.0e-8:
        ratio_O2 = gsim.composition[12] / fuel_quantity
    if gsim.composition[4] >= 1.0e-8:
        ratio_CO2 = gsim.composition[4] / fuel_quantity
    if gsim.composition[2] >= 1.0e-8:
        ratio_H2O = gsim.composition[2] / fuel_quantity
            
            
    # Phase 1 - Recherche de la LIE
    equivalence_ratio_up    = 1.0
    equivalence_ratio_down  = 0.01
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
     
    tableau = gsim.composition.copy()
    tableau[0] = 2000.0 # on place la température dans l'index 0 du tableau (qui contenait la valeur None de composition[0])
    val_OK = 0
    
    while ( abs( T_Low - tableau[0] ) >= temp_precision ):
        
        tableau[0] = gsim.equilibrium(equivalence_ratio, fuel) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
        if ( ( T_Low - tableau[0] ) <= 0.0 ):
            equivalence_ratio_up = equivalence_ratio
        else:
            equivalence_ratio_down = equivalence_ratio
        
        if ( abs( equivalence_ratio_down - 1.0 ) <= 0.03 or abs( equivalence_ratio_up - 0.01 ) <= 0.03 ):
            val_OK = 1
            break
        
        equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
        
        if ( abs( equivalence_ratio_up - equivalence_ratio_down ) <= phi_precision ):
            break
        
    if ( val_OK != 1 ):
        # on appelle la fonction de calcul de la limite d'explosivité pour calculer la LIE à partir du ratio d'équivalence trouvé et des propriétés du gaz
        resultat["LIE"] = calcul_limite(gsim, equivalence_ratio, fuel, tableau, T_Low, ratio_N2, ratio_O2, ratio_CO2, ratio_H2O, fuel_quantity) 
        
    
    # Phase 2 - Recherche de la LSE
    equivalence_ratio_up    = 50.0
    equivalence_ratio_down  = 1.0
    equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
    
    tableau[0] = 100.0
    val_OK = 0
    
    while ( abs( T_High - tableau[0] ) >= temp_precision ):
        
        tableau[0] = gsim.equilibrium(equivalence_ratio, fuel) # au lieu d'appeler Chemkin, on utilise directement le calcul de l'équilibre de Cantera (via la fonction equilibrate)
        
        if ( ( T_High - tableau[0] ) >= 0.0 ):
            equivalence_ratio_up = equivalence_ratio
        else:
            equivalence_ratio_down = equivalence_ratio
        
        if ( abs( equivalence_ratio_up - 1.0 ) <= 0.03 or abs( equivalence_ratio_down - 20.0 ) <= 0.03 ):
            val_OK = 1
            break
        
        equivalence_ratio = ( equivalence_ratio_up + equivalence_ratio_down ) / 2.0
        
        if ( abs( equivalence_ratio_up - equivalence_ratio_down ) <= phi_precision ):
            break
        
    if ( val_OK != 1 ):
        # on appelle la fonction de calcul de la limite d'explosivité pour calculer la LSE à partir du ratio d'équivalence trouvé et des propriétés du gaz
        resultat["LSE"] = calcul_limite(gsim, equivalence_ratio, fuel, tableau, T_High, ratio_N2, ratio_O2, ratio_CO2, ratio_H2O, fuel_quantity) 
    
        
    # on retourne le dictionnaire contenant les résultats des calculs
    return resultat 


def calcul_limite(calculateur, phi, fuel, tableau, T_ref, ratio_N2, ratio_O2, ratio_CO2, ratio_H2O, fuel_quantity):
    # on ajuste la composition du mélange de gaz à partir du ratio de l'air/carburant en vérifiant la présence de gaz inertes
    gas = calculateur.gas
    if sum(calculateur.add_inertes.values()) > 0.0:
        gas.set_equivalence_ratio(phi=phi, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76}, diluent=calculateur.add_inertes, fraction={"diluent": sum(calculateur.add_inertes.values())})
    else:
        gas.set_equivalence_ratio(phi=phi, fuel=fuel, oxidizer={'O2': 1, 'N2': 3.76})
    composition_avec_air = calculateur.get_composition() 
    composition_avec_air[0] = tableau[0] # on place la température dans l'index 0 de la composition
    tableau = composition_avec_air.copy() # on copie la composition ajustée dans le tableau pour les calculs suivants
    
    # on calcule la limite d'explosivité à partir de la composition ajustée du mélange de gaz 
    limite = sum(tableau[1:]) - (tableau[2] + tableau[4] + tableau[12] + tableau[13]) # on soustrait les gaz inertes pour ne garder que les combustibles
    limite = limite + ratio_N2 * fuel_quantity + ratio_O2 * fuel_quantity + ratio_CO2 * fuel_quantity + ratio_H2O * fuel_quantity 
    limite = 100. * limite
    return round(phi, 4) , calculateur.pression , calculateur.temperature - 273.15 , float(T_ref) , float(limite) #, 100.*Add_CO2 , 100.*Add_N2 , 100.*Add_H2O 
    