import cantera as ct
from pathlib import Path
from format_yaml import format_desc, format_species

import utils

# on analyse le fichier d'entrée pour récupérer les données dans un objet Cantera (subroutine Mixture.f90)
def mixture(fichier: str) -> ct.Solution:    
    extension = fichier.split(".")[-1] # on récupère l'extension du fichier 
    
    if extension in ['yaml', 'yml', 'cti']: # si le fichier est dans un format reconnaissable par Cantera, on utilise directement Cantera pour le charger
        gas = ct.Solution(fichier)
        ajouter_inertes() # TODO demander à l'utilisateur s'il souhaite ajouter des gaz inertes et les stocker dans utils.add_inertes 
                    
    elif extension == 'txt':
        gas = create_from_txt(fichier) # si le fichier est au format txt, on utilise une fonction personnalisée pour créer un objet gas à partir des données du fichier
        
    else: 
        raise ValueError("Unsupported file format. Please provide a yaml/yml, cti, or txt file.")
    
    return gas


# cette fonction ajoute les gaz inertes spécifiés par l'utilisateur dans utils.add_inertes
def ajouter_inertes():
    inertes = ['CO2', 'H2O', 'N2'] # liste des gaz inertes reconnus
    
    rep = input("Voulez-vous ajouter des gaz inertes ? (y/n) ") # TODO remplacer par une interface plus propre que la console
    
    if rep == "y":
        while True:
            if len(inertes) == 0:
                print("Tous les gaz inertes disponibles ont été ajoutés.")
                break
            
            nom = input("Nom du gaz inerte ('stop' pour terminer) : ")
            
            if nom == "stop":
                if len(utils.add_inertes) == 0:
                    print("Aucun gaz inerte ajouté.")
                else:
                    print(f"Gaz inertes ajoutés : {utils.add_inertes}")
                break
            elif nom not in inertes:
                print(f"{nom} n'est pas une espèce reconnue. Veuillez choisir un gaz valide non encore ajouté ({inertes}).") 
                continue
            elif nom in utils.add_inertes:
                print(f"{nom} est déjà ajouté avec une quantité de {utils.add_inertes[nom]}. Veuillez choisir un autre gaz à ajouter ({inertes}).")
                continue
            
            
            while True:
                quantite = 0
                try:
                    quantite = float(input(f"Quantité de {nom} (en fraction molaire) : "))
                except ValueError:
                    print("Quantité invalide. Veuillez entrer un nombre.")
                    continue
                    
                if quantite + sum(utils.add_inertes.values()) > 1.0: # seuil 0.9 ? au dessus le mélange devient trop dilué pour être explosif
                    print(f"Quantité totale des gaz inertes dépasse 1.0 (actuellement {sum(utils.add_inertes.values())}). Veuillez entrer une quantité plus petite.")
                    continue
                elif quantite < 0:
                    print("Quantité invalide. Veuillez entrer un nombre positif.")
                    continue
                
                utils.add_inertes[nom] = quantite
                inertes.remove(nom) # on retire le gaz ajouté de la liste des gaz disponibles pour éviter les doublons
                break
    else: 
        print("Aucun gaz inerte ajouté.")
    
    
# cette fonction lit un fichier txt contenant les données de pression, température, espèces de carburant et gaz inertes, 
# et écrit un fichier yaml à partir de ces données pour pouvoir les charger dans Cantera. 
# Elle retourne ensuite l'objet gas créé à partir du fichier yaml.
def create_from_txt(fichier: str) -> ct.Solution:
    src = Path(__file__).resolve().parent # Récupère le chemin du dossier actuel (src) pour construire le chemin vers le fichier txt dans le dossier data
    chemin_txt = src.parent / "data" / fichier # Construit le chemin vers le fichier txt à partir du dossier actuel et du nom de fichier fourni par l'utilisateur
    
    with open(chemin_txt, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    
    # le fichier txt a une structure spécifique, avec des lignes pour la pression, la température, les gas inertes et les espèces de carburant.    
    pres, temp = 1, 300 # on initialise la pression et la température à des valeurs par défaut au cas où elles ne seraient pas spécifiées dans le fichier txt
    inertes = dict()
    species = dict()
    
    for line in lines:
        line = line.strip() # retire les espaces/sauts en début et fin de ligne
        if not line or line.startswith('!'): # évite les lignes vides ou les commentaires (commençant par '!')
            continue
        
        parts = line.split() # divise la ligne en parties séparées par des espaces (même de multiples espaces seront traités comme un seul séparateur)
        cmd = parts[0] # le premier mot de la ligne indique le type de donnée (PRES, TEMP, ADD pour les inertes, FUEL pour les espèces de carburant)
        
        if cmd == 'PRES':
            pres = float(parts[1])
        elif cmd == 'TEMP':
            temp = float(parts[1])
        elif cmd == 'ADD':
            inertes[parts[1]] = float(parts[2]) 
        elif cmd == 'FUEL':
            species[parts[1]] = float(parts[2])
            
    # vérification des quantités pour les combustibles 
    total = sum(species.values())

    if total == 0:
        raise ValueError("Aucun carburant spécifié (somme = 0).")
    elif total != 100.0:
        print(f"Attention : la somme des carburants n'est pas égale à 100 (somme = {total}). Les valeurs seront normalisées.")
        # normalisation : on redimensionne chaque valeur pour que la somme fasse 100
        for name in species:
            species[name] = species[name] * 100.0 / total
            
    # vérification des quantités pour les gaz inertes
    total_inertes = sum(inertes.values())
    if total_inertes > 1.0: # seuil 0.9 ? au dessus le mélange devient trop dilué pour être explosif
        raise ValueError(f"La somme des gaz inertes dépasse 1.0 (somme = {total_inertes}). Veuillez corriger les quantités dans le fichier txt.")
    
    utils.add_inertes = inertes # on stocke les gaz inertes dans une variable globale (utils.add_inertes) et on les ajoutera lors du set_equivalence_ratio dans LIE_LSE_V2.py
            
    chemin_yaml = write_yaml_from_data(chemin_txt, pres, temp, species, inertes) # après avoir extrait les données du fichier txt, on crée un fichier yaml à partir de ces données 
    
    gas = ct.Solution(chemin_yaml) # on charge ensuite le fichier yaml créé dans Cantera pour obtenir un objet gas utilisable dans les calculs
    return gas
    

# cette fonction crée un fichier yaml à partir des données extraites du fichier txt, en respectant la structure attendue par Cantera.
def write_yaml_from_data(chemin_txt: Path, pres: float, temp: float, species: dict, inertes: dict) -> Path:
    chemin_yaml = chemin_txt.with_suffix(".yaml") # on change l'extension du fichier txt en yaml pour créer le chemin du fichier yaml à écrire

    contenu = format_desc(str(chemin_txt), temp, pres, species) # on utilise la fonction format_desc pour créer la partie description du fichier yaml
    contenu += format_species() # on ajoute ensuite la partie species du fichier yaml (format_species)

    with open(chemin_yaml, "w", encoding="utf-8") as f: 
        f.write(contenu)
    
    return chemin_yaml

