# Ce fichier contient des fonctions pour formater les données extraites d'un fichier texte en un format yaml compatible avec Cantera 

# description du fichier
def format_desc(chemin_txt: str, temp: float, pres: float, species: dict, inertes: dict) -> str:
    # conversion en chaîne de la composition (X)
    x_str = ", ".join(
        f"{name}: {val}" for name, val in species.items()
    )
    
    return (
        f"description: Donnees generees depuis le fichier texte ({chemin_txt})\n"
        "\n"
        "phases:\n"
        "- name: gas\n"
        "  thermo: ideal-gas\n"
        '  species: ["H2", "H2O", "B2CO", "CO2", "C2H2T", "C2H4Z", '
        '"CH4", "C2H6", "C3H8", "C4H10", "C5H12-1", "O2", "N2"]\n'
        f"  state: {{T: {temp}, P: {pres} atm, X: {{{x_str}}}}}\n"
    )

# espèces de gaz
def format_species():
    species = """
species:
- name: H2
  composition: {H: 2}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [3.43853, 1.44314e-04, -1.08191e-07, 2.16839e-10, -5.54307e-14, 
        -1037.49, -3.92682]
    - [2.4971474, 1.78083e-03, -7.80013e-07, 1.48437e-10, -1.03401e-14,
      -682.34235, 1.2869436]
- name: H2O
  composition: {H: 2, O: 1}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [3.97559, -4.41834e-04, 2.45596e-06, -1.24431e-09, 2.26702e-13, 
        -3.0281e+04, 0.0771523]
    - [2.6801061, 3.09623e-03, -9.31393e-07, 1.34865e-10, -7.70007e-15,
      -2.9923344e+04, 6.7805263]
- name: B2CO
  composition: {C: 1, O: 1}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [3.262452, 1.511941e-03, -3.881755e-06, 5.581944e-09, 
        -2.474951e-12, -1.431054e+04, 4.848897]
    - [3.0250777, 1.442689e-03, -5.630828e-07, 1.018581e-10, 
        -6.910952e-15, -1.426835e+04, 6.1082221]
- name: CO2
  composition: {C: 1, O: 2}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1005.0, 5000.0]
    data:
    - [2.2576122, 9.5094619e-03, -7.3198071e-06, 2.0577067e-09, 
        1.032053e-14, -4.837159e+04, 10.295759]
    - [4.1987613, 3.490279e-03, -1.4128319e-06, 2.5480168e-10, 
        -1.7105678e-14, -4.8815924e+04, 0.56029982]
- name: C2H2T
  composition: {C: 2, H: 2}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [2.013562, 0.01519045, -1.616319e-05, 9.078992e-09, 
        -1.912746e-12, 2.612444e+04, 8.805378]
    - [4.4367752, 5.376039e-03, -1.912817e-06, 3.286379e-10, 
        -2.15671e-14, 2.5667661e+04, -2.8003713]
- name: C2H4Z
  composition: {C: 2, H: 4}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1090.0, 5000.0]
    data:
    - [1.3181, 0.014446, -2.74335e-06, -3.10835e-09, 1.52772e-12, 
        5268.17, 14.7233]
    - [0.31468137, 0.0167299, -6.80909e-06, 1.22922e-09, -8.23928e-14, 
        5724.9924, 20.36272]
- name: CH4
  composition: {C: 1, H: 4}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1015.0, 5000.0]
    data:
    - [2.31954, 6.54738e-03, -7.48051e-07, 2.60912e-09, -1.95537e-12, 
        -9997.64, 7.24965]
    - [1.6080835, 0.010308, -3.71228e-06, 6.14185e-10, -3.86748e-14, 
        -1.0063071e+04, 10.071468]
- name: C2H6
  composition: {C: 2, H: 6}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1250.0, 5000.0]
    data:
    - [0.975454, 0.018811, -1.46453e-06, -6.38247e-09, 2.84067e-12, 
        -1.13111e+04, 16.5514]
    - [0.31208901, 0.0211928, -8.0856e-06, 1.39339e-09, -9.03005e-14, 
        -1.0989168e+04, 20.203763]
- name: C3H8
  composition: {C: 3, H: 8}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [-0.31831896, 0.034746405, -1.2885018e-05, -3.5057037e-09, 
        3.0165358e-12, -1.3851594e+04, 24.514595]
    - [5.4507892, 0.022160569, -7.7296281e-06, 1.2495476e-09, 
        -7.7377605e-14, -1.5616278e+04, -6.140457]
    note: '0'
- name: C4H10
  composition: {C: 4, H: 10}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [0.059979584, 0.04400558, -1.5532127e-05, -5.2806315e-09, 
        4.0442116e-12, -1.7040045e+04, 24.565849]
    - [7.6947071, 0.027767614, -9.6156327e-06, 1.5456056e-09, 
        -9.5281279e-14, -1.9406615e+04, -16.1338]
    note: '0'
- name: C5H12-1
  composition: {C: 5, H: 12}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [0.33723104, 0.051184896, -8.8964271e-06, -1.9731004e-08, 
        1.061695e-11, -1.9916924e+04, 25.221468]
    - [3.0289578, 0.044837728, -1.7129876e-05, 2.9687475e-09, 
        -1.9391142e-13, -2.020335e+04, 12.227702]
- name: O2
  composition: {O: 2}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [3.08809, 1.60342e-03, -5.3455e-07, 2.80793e-11, 2.98899e-15, 
        -993.828, 6.61069]
    - [3.1892691, 1.56657e-03, -6.90657e-07, 1.32082e-10, -9.23577e-15,
      -1048.1021, 5.9950619]
- name: N2
  composition: {N: 2}
  thermo:
    model: NASA7
    temperature-ranges: [300.0, 1000.0, 5000.0]
    data:
    - [3.298677, 1.4082399e-03, -3.9632218e-06, 5.6415148e-09, 
        -2.444854e-12, -1020.9, 3.950372]
    - [2.9266379, 1.487977e-03, -5.6847603e-07, 1.009704e-10, 
        -6.7533509e-15, -922.79538, 5.9805402]
    note: Ranzi          0
    """
    
    return species