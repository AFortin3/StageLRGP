import numpy as np
from numpy.typing import NDArray

import utils

# On récupère les seuils de température critiques (T_low et T_high) pour le mélange (subroutine Critere_T.f90)
def critere_T() -> tuple[float, float]:
    critere_P = np.zeros((19, 3), dtype=float) # initialisation du tableau des critères de température (avec ligne et colonne 0 nulles pour éviter les erreurs d'indexation)

    # Critere Low_T
    critere_P[1,1] = 629.  # H2
    critere_P[2,1] = 0.    # H2O
    critere_P[3,1] = 1417. # B2CO
    critere_P[4,1] = 0.    # CO2
    critere_P[5,1] = 1603. # C2H2T
    critere_P[6,1] = 1514. # C2H4Z
    critere_P[7,1] = 1480. # CH4
    critere_P[8,1] = 1602. # C2H6
    critere_P[9,1] = 1509. # C3H8
    critere_P[10,1] = 1706.# C4H10
    critere_P[11,1] = 1670.# C5H12-1
    critere_P[12,1] = 0.   # O2
    critere_P[13,1] = 0.   # N2
    critere_P[14,1] = 1514. # C3H6Y
    critere_P[15,1] = 1509. # nC4H8Y
    critere_P[16,1] = 1511. # C6H14-1
    critere_P[17,1] = 1710. # C10H22-1
    critere_P[18,1] = 1912. # C12H26-1
    
    # Critere Up_T - 1 Bar
    critere_P[1,2] = 1124. # H2    *** correctif avant 1192
    critere_P[2,2] = 0.    # H2O
    critere_P[3,2] = 1259. # B2CO
    critere_P[4,2] = 0.    # CO2
    critere_P[5,2] = 764.  # C2H2T
    critere_P[6,2] = 1210. # C2H4Z
    critere_P[7,2] = 1730. # CH4
    critere_P[8,2] = 1413. # C2H6
    critere_P[9,2] = 1226. # C3H8
    critere_P[10,2] = 1144.# C4H10
    critere_P[11,2] = 1040.# C5H12-1
    critere_P[12,2] = 0.   # O2
    critere_P[13,2] = 0.   # N2 
    critere_P[14,2] = 1413. # C3H6Y
    critere_P[15,2] = 1226. # nC4H8Y
    critere_P[16,2] = 1024. # C6H14-1
    critere_P[17,2] = 1021. # C10H22-1
    critere_P[18,2] = 1007. # C12H26-1
    
    
    # correction critère pour des pressions de 1 à 100 bar
    correction_P = np.zeros((7, 8), dtype=float) # initialisation du tableau des corrections de température (avec ligne et colonne 0 nulles pour éviter les erreurs d'indexation)
    
    # CH4
    correction_P[1,1] = critere_P[7,2]
    correction_P[1,2] = 1160. 
    correction_P[1,3] = 1100. 
    correction_P[1,4] = 1060. 
    correction_P[1,5] = 1010. 
    correction_P[1,6] = 1000. 
    correction_P[1,7] = 1000. 
    
    # C2H6
    correction_P[2,1] = critere_P[8,2] 
    correction_P[2,2] = 1100. 
    correction_P[2,3] = 1070. 
    correction_P[2,4] = 1030. 
    correction_P[2,5] = 1005. 
    correction_P[2,6] = 1000. 
    correction_P[2,7] = 1000. 
    
    # C3H8
    correction_P[3,1] = critere_P[9,2] 
    correction_P[3,2] = 1060. 
    correction_P[3,3] = 1040. 
    correction_P[3,4] = 990. 
    correction_P[3,5] = 1000. 
    correction_P[3,6] = 1000. 
    correction_P[3,7] = 1000. 
    
    # C4H10
    correction_P[4,1] = critere_P[10,2]
    correction_P[4,2] = 1040. 
    correction_P[4,3] = 1000. 
    correction_P[4,4] = 1000. 
    correction_P[4,5] = 1000. 
    correction_P[4,6] = 1000. 
    correction_P[4,7] = 1000. 
    
    # C3H6Y (Index 5)
    correction_P[5,1] = 1413. # 1 bar
    correction_P[5,2] = 1413. # 1-5 bar (linéaire entre 1 et 5)
    correction_P[5,3] = 1100. # 5-10 bar
    correction_P[5,4] = 1070. # 10-20 bar
    correction_P[5,5] = 1030. # 20-40 bar
    correction_P[5,6] = 1000. # 40-50 bar
    correction_P[5,7] = 1000. # > 50 bar

    # nC4H8Y (Index 6)
    correction_P[6,1] = 1226. # 1 bar
    correction_P[6,2] = 1226. # 1-5 bar
    correction_P[6,3] = 1040. # 5-10 bar
    correction_P[6,4] = 1000. # 10-20 bar
    correction_P[6,5] = 1000. # > 20 bar
    correction_P[6,6] = 1000. 
    correction_P[6,7] = 1000.
    
    
    # Effet de la pression pour C1 - C2 - C3 - C4 (+ C3H6Y et nC4H8Y) 
    plage_P = np.array([0., 1., 5., 10., 20., 40., 50., 100.]) # en bar
           
    if ( utils.pression <= plage_P[2] ):
        indice = 1
    elif ( utils.pression > plage_P[2] and utils.pression <= plage_P[3] ):
        indice = 2
    elif ( utils.pression > plage_P[3] and utils.pression <= plage_P[4] ):
        indice = 3
    elif ( utils.pression > plage_P[4] and utils.pression <= plage_P[5] ):
        indice = 4
    elif ( utils.pression > plage_P[5] and utils.pression <= plage_P[6] ):
        indice = 5
    elif ( utils.pression > plage_P[6] and utils.pression <= plage_P[7] ):
        indice = 6
    else:
    # pour les pressions > 100 bar, on considère que les critères de température sont ceux à 50 bar (température = 1000 de toute façon)
    # sinon cela causerait un problème d'indice (array out of bounds) pour l'indice = 7 (il cherche l'indice 7+1 = 8 qui n'existe pas dans le tableau)
        indice = 6 # 6 au lieu de 7
        
    critere_P[7,2] = correction_P[1,indice] + ( correction_P[1,indice+1] - correction_P[1,indice] ) / ( plage_P[indice+1] - plage_P[indice] ) * ( utils.pression - plage_P[indice] ) # CH4
    critere_P[8,2] = correction_P[2,indice] + ( correction_P[2,indice+1] - correction_P[2,indice] ) / ( plage_P[indice+1] - plage_P[indice] ) * ( utils.pression - plage_P[indice] ) # C2H6
    critere_P[9,2] = correction_P[3,indice] + ( correction_P[3,indice+1] - correction_P[3,indice] ) / ( plage_P[indice+1] - plage_P[indice] ) * ( utils.pression - plage_P[indice] ) # C3H8
    critere_P[10,2]= correction_P[4,indice] + ( correction_P[4,indice+1] - correction_P[4,indice] ) / ( plage_P[indice+1] - plage_P[indice] ) * ( utils.pression - plage_P[indice] ) # C4H10
    critere_P[14,2] = correction_P[5,indice] + ( correction_P[5,indice+1] - correction_P[5,indice] ) / ( plage_P[indice+1] - plage_P[indice] ) * ( utils.pression - plage_P[indice] ) # C3H6Y
    critere_P[15,2] = correction_P[6,indice] + ( correction_P[6,indice+1] - correction_P[6,indice] ) / ( plage_P[indice+1] - plage_P[indice] ) * ( utils.pression - plage_P[indice] ) # nC4H8Y
    
    
    # H2
	# Pour H2 selon qu'il est seul ou pas on adapte la methode
	# Cas 1 pas seul
	# 1124	1 bar
    # 850	3 bar
    # 950	6 bar
    # 980	10 bar
    # j'ai fait un polynome d'ordre 3 sur excel pour ces criteres
	# y = -1.8143x3 + 35.543x2 - 205.59x + 1295.9
	# 1 <= pression <= 10.
	# cas H2 seul : y = -44.833x3 + 421x2 - 1323.2x + 2071

    if ( np.sum(utils.composition[2:13]) <= 1.0e-5 ): 
        # cas de H2 seul
        if ( utils.temperature <= 25. + 273.15 ):
            critere_P[1,2] = -44.833 * utils.pression**3 + 421 * utils.pression**2 - 1323.2 * utils.pression**1 + 2071 # 30°
        else:
            critere_P[1,2] = 25. * utils.pression**2 - 205. * utils.pression + 1025  # 90°C  + 60°C  + 40°C

        if ( utils.pression < 1.2 and utils.temperature <= 42. + 273.15):  critere_P[1,2] = ( critere_P[1,2] + 1124. ) / 2.
        
        if ( utils.pression > 4. ): critere_P[1,2] = 600.0
    else:   
		# cas H2 en mélange
		# 1 bar : 1124
		# 3 bar : 850
		# 6 bar : 950
		# 10 bar : 1000
        if ( utils.pression <= 6 ):
            critere_P[1,2] = 34.067 * utils.pression**2 - 273.27 * utils.pression + 1363.2
        elif ( utils.pression > 6 and utils.pression <= 10 ):
            critere_P[1,2] = 12.5 * utils.pression + 875 
        else:
            critere_P[1,2] = 1000.
            
    
    # Somme totale sans les inertes
    composition_1 = utils.composition.copy() # on duplique la composition pour ne pas modifier les données originales
    composition_1[0] = 0. # pour éviter les erreurs de calcul sur un objet None
    
    Sum1 = np.sum(composition_1) - composition_1[2] - composition_1[4] - composition_1[12] - composition_1[13]
    composition_1 = 100. * composition_1 / Sum1
    
    composition_1[2] = 0.
    composition_1[4] = 0.
    composition_1[12] = 0.
    composition_1[13] = 0.
    
    T_Low  = np.sum( composition_1[1:19] * critere_P[1:,1] ) / 100.
    T_High = np.sum( composition_1[1:19] * critere_P[1:,2] ) / 100. 
    
    return (T_Low, T_High)