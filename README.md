# 🔥 Estimation des Limites d'Inflammabilité (Branche : app)

Cette branche contient la version finale et déployable de l'application Web d'estimation des limites d'inflammabilité (LIE et LSE). Développée avec Streamlit et propulsée par le moteur thermochimique Cantera, elle permet l'étude de mélanges complexes incluant de nombreuses espèces de combustibles et quelques gaz inertes.

✨ **Nouveautés de cette version :**
- **Architecture Orientée Objet (POO) :** Le code a été réécrit avec une classe `GasSimulator` (`src/core/GasSimulator.py`) pour supprimer les variables globales, permettant un déploiement cloud multi-utilisateurs sans conflits de session.
- **Déploiement Cloud Ready :** Utilisation d'un fichier `requirements.txt` standardisé.
- **Ajout d'espèces :** Prise en charge des nouveaux hydrocarbures demandés par le laboratoire.
- **Interface modulaire :** Séparation du code de l'interface en composants (`sidebar.py`, `dashboard.py`).

---

## 📂 1. Architecture du projet

Le projet est structuré selon les standards des applications web Python :

```text
├── src/
│   ├── components/             # Composants de l'interface graphique (UI)
│   │   ├── dashboard.py        # Affichage principal des résultats et graphiques
│   │   └── sidebar.py          # Panneau latéral de configuration des paramètres
│   ├── core/                   # Moteur logique et calculs thermochimiques
│   │   ├── Critere_T.py        # Algorithme des températures critiques
│   │   ├── GasSimulator.py     # Classe principale de simulation Cantera
│   │   └── LIE_LSE_V2.py       # Algorithme de dichotomie pour trouver les limites
│   └── data/                   # Données statiques
│       └── output_convert.yaml # Modèle de données YAML requis par Cantera
├── app.py                      # Point d'entrée principal de l'application Streamlit
├── requirements.txt            # Liste des dépendances 
└── README.md                   # Documentation technique (ce fichier)
```

---

## 🛠️ 2. Installation en Local (Mode Développement)

Pour exécuter et tester l'application sur votre propre machine, vous devez configurer un environnement virtuel local.

### Prérequis
- Python 3.14 ou supérieur.
- Un gestionnaire d'environnement (Conda, Miniforge ou `venv`).

### Installation avec Conda / Miniforge (Recommandé)
```bash
# 1. Créez un environnement virtuel vierge
conda create --name reaction-sim python=3.14

# 2. Activez l'environnement
conda activate reaction-sim

# 3. Installez les dépendances via le fichier requirements.txt
pip install -r requirements.txt
```

### Installation classique avec Python (`venv`)
```bash
# 1. Créez l'environnement virtuel
python -m venv venv

# 2. Activez-le (Windows)
venv\Scripts\activate
# OU Activez-le (Mac/Linux)
source venv/bin/activate

# 3. Installez les dépendances
pip install -r requirements.txt
```

### Lancement de l'application en local
Une fois les dépendances installées, placez-vous à la racine du projet et lancez le serveur Streamlit :
```bash
streamlit run app.py
```
L'application s'ouvrira automatiquement dans votre navigateur web par défaut (généralement à l'adresse `http://localhost:8501`).

---
**Développé par :** Antoine Fortin (Stage L3 MIASHS) au Laboratoire Réactions et Génie des Procédés (LRGP).
