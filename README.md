# Menus de « Nos repas »

Le fichier `menus.json` que l'app iOS « Nos repas » lit toute seule. Une routine claude.ai le met à jour chaque lundi matin à partir
des menus de la semaine ; l'app le télécharge à l'ouverture et en arrière-plan, puis ajoute les nouveaux plats.

`publish.py` ajoute au fichier les nouveautés de la semaine ; `python3 test_publish.py` le vérifie. Le fichier ne contient que des
recettes et des prix estimés : rien sur le foyer (couverts, notes, soirs prévus, réglages, poids, commandes, placard, bilans), et le
script refuse de publier s'il trouve un nom, une recette incomplète ou une semaine plus ancienne que celle déjà en ligne.
