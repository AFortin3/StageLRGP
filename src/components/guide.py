GUIDE_MD = """
## 1. Accéder à l'application
L'application est divisée en deux parties : 
- **Le panneau latéral (à gauche) :** dédié à la saisie de vos paramètres.
- **Le tableau de bord (au centre) :** dédié à l'affichage en temps réel.

## 2. Configurer une simulation
### A. Propriétés Physiques
Définissez les conditions initiales (Pression en atm, Température en K).

### B. Ajout de Gaz Inertes
Ajoutez les fractions molaires (CO2, H2O, N2). 
⚠️ **Attention :** La somme ne doit pas dépasser 1.0.

### C. Composition du Combustible
Saisissez les valeurs de votre choix pour chaque gaz. L'application normalise automatiquement vos valeurs sur 100%.

## 3. Lire les résultats
- 🔵 **LIE :** Limite Inférieure d'Explosivité (mélange trop pauvre en deçà).
- 🟠 **LSE :** Limite Supérieure d'Explosivité (mélange trop riche au-delà).
"""
