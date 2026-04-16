import utils as utils
import pandas as pd

pd.options.display.float_format = '{:.2f}'.format # pour afficher les float avec seulement 2 décimales dans le DataFrame

# valeurs par défaut
fuel = 'C3H8' 
p = 5 
t = 300 

def main():
    fuel = 'C3H8' #input("Entrez le carburant (ex: C3H8) : ")
    p = 5 #float(input("Entrez la pression (en atm) : "))
    t = 300 #float(input("Entrez la température (en K) : "))
        
    gas = utils.equilibrium(1, fuel, t, p) # On calcule l'équilibre chimique du mélange de gaz à la température et à la pression données (pour phi = 1, c'est à dire pour un mélange stoechiométrique)
    print("Propriétés du gaz à l'équilibre :")
    gas()
    print(f"Température adiabatique : {gas.T:.2f} K")
    
    print("Maintenant, nous allons calculer la température adiabatique pour différents ratios d'équivalence (phi) :")
    data: dict = list_phi({})

    df = pd.DataFrame({
        "phi": list(data.keys()),
        "T_ad": list(data.values())
    })

    print(df)
        
        
def list_phi(data: dict) -> dict:
    if len(data) >= 30: # on s'arrête si il y a déjà 30 points dans le dictionnaire 
        return(data)
    else: # sinon, on continue en incrémentant de 0.1
        if len(data) == 0: # si le dictionnaire est vide, on commence à 0.1
            phi = 0.1
        else: 
            phi = max(data.keys()) + 0.1
        t_ad = utils.t_adiabatique(phi, fuel, t, p)
        data[phi] = t_ad
        return list_phi(data)
        
    
if __name__ == "__main__":
    main()
