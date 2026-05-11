import cantera as ct
from pathlib import Path

import utils
from Mixture import mixture
from Critere_T import critere_T
from LIE_LSE_V2 import lie_lse
from LIE_LSE_brentq import lie_lse_brentq


def main():
    src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel
    dossier = src.parent / 'data' # Construit le chemin vers le dossier "data" à partir du dossier actuel
    ct.add_data_directory(str(dossier)) # Ajoute le dossier à la liste des répertoires de données de Cantera
    
    # On demande à l'utilisateur de saisir le nom du fichier à charger
    while True:
        #fichier = input("Input file (with extension): ")
        fichier = "M27_50.txt"
        
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
    limites = lie_lse_brentq(gas, temperatures[0], temperatures[1])
    print("\nPremières limites d'explosivité :"
        "\nLIE = ", (limites["LIE"]),
        "\nLSE = ", (limites["LSE"]))
        
    #utils.write_results(limites_list) # on écrit les résultats dans un fichier texte
    
    
if __name__ == "__main__":
    main()