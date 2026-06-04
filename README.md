# 🔥 Estimation des Limites d'Inflammabilité (Branche : python-old)

Cette branche contient la première version locale (en ligne de commande) du projet de portage de ChemkinPro vers Python/Cantera. Elle permet de calculer la Limite Inférieure d'Explosivité (LIE) et la Limite Supérieure d'Explosivité (LSE) de mélanges gazeux.

⚠️ **Note :** Il s'agit d'une version de développement initiale. Elle ne contient pas d'interface graphique et prend en charge seulement les 13 premières espèces de gaz.

---

## 📂 1. Architecture du projet

Le projet est structuré de la manière suivante :

```text
├── data/                  # Dossier contenant les fichiers d'entrée utilisateur
│   ├── d1.txt             # Exemple de fichier d'entrée complet 
│   └── d1.yaml            # Exemple de fichier d'entrée au format Cantera
├── src/                   # Code source de l'application
│   ├── main.py            # Point d'entrée principal (orchestrateur)
│   ├── utils.py           # Fonctions utilitaires et variables globales
│   ├── Mixture.py         # Gestion et traitement des fichiers d'entrée
│   ├── Critere_T.py       # Algorithme de calcul des températures critiques
│   ├── LIE_LSE_V2.py      # Moteur de recherche par dichotomie
│   └── format_yaml.py     # Script de formatage dynamique des fichiers YAML
├── env.yml                # Configuration de l'environnement Conda
└── README.md              # Documentation (ce fichier)
```

---

## 🛠️ 2. Prérequis et Installation

### Prérequis
- **Python 3.14+**
- Un gestionnaire d'environnements (**Miniforge**, Anaconda ou Miniconda)

### Installation
1. Si vous avez reçu ce projet sous forme d'archive (`.zip`), décompressez-la dans le dossier de votre choix. Si vous utilisez Git, placez-vous sur la branche `python-old`.
2. Ouvrez votre terminal (ou l'invite de commande Anaconda/Miniforge) et placez-vous à la racine du dossier décompressé.
3. Créez et activez l'environnement virtuel à l'aide du fichier `env.yml` fourni :
   ```bash
   conda env create -f env.yml
   conda activate reaction-sim
   ```

---

## 🚀 3. Guide d'utilisation

Dans cette version locale, les calculs sont déclenchés en exécutant le fichier `main.py`. Vous pouvez utiliser la console ou votre Environnement de Développement Intégré (IDE) habituel.

### Étape 1 : Préparer les données d'entrée
Placez votre fichier de configuration (`.txt` ou `.yaml`) dans le dossier `data/`.
*Note : Si vous utilisez un fichier `.yaml`, la gestion des gaz inertes n'est pas prise en compte automatiquement par le fichier. Le programme vous demandera de les saisir manuellement dans la console lors de l'exécution.*

### Étape 2 : Lancer le calcul
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

### Étape 3 : Interaction
1. Le programme s'interrompra pour vous demander : `Input file (with extension):`.
2. Tapez le nom de votre fichier (ex: `d1.txt`) dans la console ou le terminal de l'IDE. Si vous appuyez directement sur "Entrée", le fichier par défaut `d1.txt` sera chargé.
3. Le programme lira le fichier, appliquera les conversions thermodynamiques nécessaires (Pa vers bar, Celsius vers Kelvin) et vérifiera la composition du gaz.

### Étape 4 : Lecture des résultats
Le programme exécutera des boucles de calcul sur des plages prédéfinies :
- Pression : incrémentation de 1 à 21 bar.
- Température : incrémentation de 25°C à 160°C (convertie en Kelvin pour Cantera).

Les résultats de la LIE et de la LSE s'afficheront directement dans votre console de commande pour chaque point thermodynamique testé.

---
**Développé par :** Antoine Fortin (Stage L3 MIASHS) au LRGP.
