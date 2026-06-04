# 🔥 Estimation des Limites d'Inflammabilité (Branche : app-old)

Cette branche contient l'ébauche de l'interface graphique (Web) développée avec Streamlit pour le calcul de la Limite Inférieure d'Explosivité (LIE) et de la Limite Supérieure d'Explosivité (LSE) via Cantera.

⚠️ **Spécificités et limites de cette branche :**
- Cette version est **strictement locale**. En raison de l'utilisation de variables globales dans l'architecture (`utils.py`), elle ne supporte pas l'accès simultané par plusieurs utilisateurs. Elle ne doit donc **pas** être déployée sur le Cloud.
- Elle correspond à une étape intermédiaire du développement et ne prend pas encore en charge les 5 nouvelles espèces d'hydrocarbures.

---

## 📂 1. Architecture du projet

Le projet est structuré de la manière suivante :

```text
├── src/                    # Code source de l'application
│   ├── app.py              # Interface graphique Streamlit (Sidebar et affichage)
│   ├── main.py             # Point d'entrée des calculs (appelé par app.py)
│   ├── utils.py            # Fonctions utilitaires (utilise des variables globales)
│   ├── Mixture.py          # Gestion de la composition et des gaz inertes
│   ├── Critere_T.py        # Algorithme de calcul des températures critiques
│   ├── LIE_LSE_V2.py       # Moteur de recherche par dichotomie
│   └── output_convert.yaml # Fichier de structure YAML par défaut 
├── env.yml                 # Configuration de l'environnement Conda
└── README.md               # Documentation (ce fichier)
```

---

## 🛠️ 2. Prérequis et Installation

Bien que l'application s'affiche dans votre navigateur Web, elle doit être hébergée localement sur votre ordinateur.

### Prérequis
- **Python 3.14+**
- Un gestionnaire d'environnements (**Miniforge**, Anaconda ou Miniconda)

### Installation
1. Si vous avez reçu ce projet sous forme d'archive (`.zip`), décompressez-la dans le dossier de votre choix. Si vous utilisez Git, placez-vous sur la branche `app-old`.
2. Ouvrez votre terminal (ou l'invite de commande Anaconda/Miniforge) et placez-vous à la racine du dossier décompressé.
3. Créez et activez l'environnement virtuel à l'aide du fichier `env.yml` fourni :
   ```bash
   conda env create -f env.yml
   conda activate reaction-sim
   ```

---

## 🚀 3. Guide d'utilisation

Une fois l'environnement activé, lancez le serveur local Streamlit en exécutant la commande suivante depuis le dossier racine :

```bash
cd src
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur web par défaut (généralement à l'adresse `http://localhost:8501`).

### Saisie des paramètres
L'ensemble des paramètres se renseigne directement via le panneau latéral de l'interface graphique :
1. **Propriétés Physiques :** Ajustez la Pression (en atm) et la Température initiale (en Kelvin).
2. **Gaz Inertes :** Ajoutez les fractions molaires de CO2, H2O ou N2 (la somme ne doit pas dépasser 1.0).
3. **Composition du combustible :** Ajustez le pourcentage de chaque élément. Le total est automatiquement normalisé sur 100%.

### Lecture des résultats
Dès qu'un paramètre est modifié, l'application recalcule les données en temps réel :
- Le résumé des propriétés physiques et de la composition s'affiche sous forme de tableaux propres (`DataFrames` Pandas).
- Les limites calculées (LIE et LSE), les ratios d'équivalence (Phi) et les températures critiques s'affichent de manière distincte dans le tableau de bord des résultats de la simulation.

---
**Développé par :** Antoine Fortin (Stage L3 MIASHS) au LRGP.
