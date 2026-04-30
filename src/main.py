import cantera as ct
from pathlib import Path

import utils
from Mixture import mixture
from Critere_T import critere_T
from LIE_LSE_V2 import lie_lse


def main():
    src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel
    dossier = src.parent / 'data' # Construit le chemin vers le dossier "data" à partir du dossier actuel
    ct.add_data_directory(str(dossier)) # Ajoute le dossier à la liste des répertoires de données de Cantera
    
    # On demande à l'utilisateur de saisir le nom du fichier à charger
    while True:
        #fichier = input("Input file (with extension): ")
        fichier = "d1.txt"
        
        try: 
            gas = mixture(fichier) # on tente de récupérer les données du fichier spécifié par l'utilisateur
        except Exception as e:
            print(f"Error loading data: {e}")
            continue
        
        print("Data loaded successfully.")
        break
    
    # On initialise la pression et la température à partir des données chargées
    utils.pression = gas.P / 100000 # conversion de la pression de Pa à bar
    utils.temperature = gas.T   
    print(f" \nPression initiale : {utils.pression} bar"
        f"\nTempérature initiale : {utils.temperature - 273.15} °C")
    
    # On récupère la composition du mélange à partir des données chargées
    utils.composition = utils.get_composition(gas)
    print("\nComposition initiale :")
    for i, fraction in enumerate(utils.composition[1:14]): # on ignore composition[0] qui est None
        print(f"{utils.species[i]}: {fraction:.2f}")
    
    # On ajuste les températures critiques à partir des données chargées
    temperatures = critere_T()
    print("\nPremières températures critiques :"
        "\nT_Low  = ", float(temperatures[0]),
        "\nT_High = ", float(temperatures[1]))
    
    # On détermine les premières LIE/LSE à partir des résultats des calculs précédents
    limites = lie_lse(gas, temperatures[0], temperatures[1])
    print("\nPremières limites d'explosivité :"
        "\nLIE = ", (limites["LIE"]),
        "\nLSE = ", (limites["LSE"]))
    
    
    
    # On calcule maintenant selon plusieurs températures et pressions les LIE/LSE : 
    limites_list = []
    
    for i in range(1, 22, 2):
        utils.pression = i # on incrémente la pression de 1 à 21 bar par pas de 2 bar
        for j in range(25, 180, 20):
            utils.temperature = j + 273.15 # on incrémente la température de 25 (et pas 5) à 160 °C par pas de 20 °C, convertie en K
            gas.TP = utils.temperature, utils.pression * 100000 # on met à jour la température et la pression du gaz dans Cantera
            
            temperatures = critere_T() # on calcule les températures critiques pour la composition actuelle du mélange
            limites_list.append(lie_lse(gas, temperatures[0], temperatures[1])) # on calcule les limites d'explosivité pour la situation actuelle
    
    for limites in limites_list:
        print("\nLimites d'explosivité à P =", limites["LIE"][1], "bar et T =", limites["LIE"][2], "°C :"
              "\nLIE = ", limites["LIE"][4], " pour un ratio d'équivalence de Phi_Low  = ", limites["LIE"][0], " et une température critique T_Low  = ", limites["LIE"][3], "°C",
              "\nLSE = ", limites["LSE"][4], " pour un ratio d'équivalence de Phi_High = ", limites["LSE"][0], " et une température critique T_High = ", limites["LSE"][3], "°C")
        
    #utils.write_results(limites_list) # on écrit les résultats dans un fichier texte
    
    
if __name__ == "__main__":
    main()