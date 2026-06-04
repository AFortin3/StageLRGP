# 🔥 Estimation des Limites d'Inflammabilité (Branche : python)

Cette branche contient la version locale stabilisée et optimisée du projet d'estimation des limites d'inflammabilité. Elle permet de calculer la Limite Inférieure d'Explosivité (LIE) et la Limite Supérieure d'Explosivité (LSE) de mélanges gazeux en utilisant Cantera.

⚠️ **Spécificités de cette branche :**
- Version console (sans interface web Streamlit).
- **Incorpore les nouvelles espèces d'hydrocarbures** ajoutées à la demande du laboratoire.
- Inclut un système de sauvegarde personnalisée des résultats générés.

---

## 📂 1. Architecture du projet

Le projet est structuré de la manière suivante :

```text
├── data/                   # Dossier contenant les fichiers d'entrée utilisateur
│   └── d1.txt              # Exemple de fichier d'entrée complet
├── src/                    # Code source de l'application
│   ├── main.py             # Point d'entrée principal (orchestrateur interactif)
│   ├── utils.py            # Fonctions utilitaires et variables globales
│   ├── Mixture.py          # Gestion et traitement des fichiers d'entrée
│   ├── Critere_T.py        # Algorithme de calcul des températures critiques
│   ├── LIE_LSE_V2.py       # Moteur de recherche par dichotomie
│   └── output_convert.yaml # Fichier de structure YAML par défaut 
├── env.yml                 # Configuration de l'environnement Conda
└── README.md               # Documentation (ce fichier)
```

---

## 🛠️ 2. Prérequis et Installation

### Prérequis
- **Python 3.14+**
- Un gestionnaire d'environnements (**Miniforge**, Anaconda ou Miniconda)

### Installation
1. Si vous avez reçu ce projet sous forme d'archive (`.zip`), décompressez-la dans le dossier de votre choix. Si vous utilisez Git, placez-vous sur la branche `python`.
2. Ouvrez votre terminal (ou l'invite de commande Anaconda/Miniforge) et placez-vous à la racine du dossier décompressé.
3. Créez et activez l'environnement virtuel à l'aide du fichier `env.yml` fourni :
   ```bash
   conda env create -f env.yml
   conda activate reaction-sim
   ```

---

## 🚀 3. Guide d'utilisation

Dans cette version locale, les calculs sont déclenchés de manière interactive en exécutant le fichier `main.py`. Vous pouvez utiliser la console ou votre Environnement de Développement Intégré (IDE) habituel.

### Étape 1 : Préparer les données d'entrée
Placez votre fichier de configuration initial (`.txt` ou `.yaml`) dans le dossier `data/`. 
*Note : Si vous utilisez un fichier `.yaml`, la gestion des gaz inertes n'est pas prise en compte automatiquement par le fichier. Le programme vous demandera de les saisir manuellement dans la console lors de l'exécution.*

### Étape 2 : Lancer le programme
**Via un IDE (VS Code, PyCharm, Spyder...) :**
1. Ouvrez le dossier du projet dans votre IDE.
2. Assurez-vous que l'interpréteur Python sélectionné est bien celui de l'environnement `reaction-sim`.
3. Ouvrez le fichier `src/main.py` et lancez l'exécution (bouton "Run").

**Via la console (Terminal) :**
Placez-vous dans le répertoire `src/` et exécutez le script :
```bash
cd src
python main.py
```

### Étape 3 : Déroulement de la simulation
1. **Chargement des données :** Le programme vous demandera : `Input file (with extension):`. Tapez le nom de votre fichier (ex: `d1.txt`) ou appuyez sur "Entrée" pour utiliser le fichier par défaut. Le script lira le fichier, appliquera les conversions thermodynamiques (Pa vers bar, Celsius vers Kelvin) et vérifiera la composition.
2. **Calcul initial :** Le programme affiche les températures critiques et les premières limites d'explosivité pour les paramètres initiaux.
3. **Calcul sur plage dynamique :** Le programme vous propose de lancer des simulations sur une plage étendue (Pression de 1 à 21 bar, Température de 25°C à 160°C).
   - Appuyez sur "Entrée" pour lancer les calculs approfondis.
   - Saisissez n'importe quel caractère pour interrompre le programme.
4. **Sauvegarde :** Une fois les boucles de calculs terminées, le programme vous proposera d'enregistrer les résultats : `Voulez-vous enregistrer les résultats dans un fichier texte ? (y/n)`. En tapant `y`, vous pourrez nommer votre fichier (par défaut `results.txt`), qui contiendra l'historique complet des LIE/LSE générées.

---
**Développé par :** Antoine Fortin (Stage L3 MIASHS) au LRGP.
