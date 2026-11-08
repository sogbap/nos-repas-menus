# Menus de « Nos repas »

Le fichier `menus.json` que l'app iOS « Nos repas » lit toute seule. Une routine claude.ai le met à jour chaque lundi matin à partir
des menus de la semaine ; l'app le télécharge à l'ouverture et en arrière-plan, puis ajoute les nouveaux plats.

`publish.py` ajoute au fichier les nouveautés de la semaine ; `python3 test_publish.py` le vérifie. Le fichier ne contient que des
recettes et des prix estimés : rien sur le foyer (couverts, notes, soirs prévus, réglages, poids, commandes, placard, bilans), et le
script refuse de publier s'il trouve un nom, une recette incomplète ou une semaine plus ancienne que celle déjà en ligne.

Les étapes des nouvelles recettes sont réécrites pour quelqu'un qui n'a jamais cuisiné : `GUIDE-ETAPES.md` dit comment, et
`python3 publish.py --verifier export` relit le résultat.

`picard.json` : le prix de toutes les fiches produits de picard.fr, relevé chaque lundi vers 3 h par l'action GitHub « Relevé des prix
Picard » (`releve_picard.py`, testé par `test_releve_picard.py`). Le robot respecte robots.txt, s'annonce sous son vrai nom, lit une
page à la fois et s'arrête au premier refus. L'app met à jour avec lui les prix Picard des produits qu'elle connaît. Le drive Leclerc,
lui, interdit tout robot (robots.txt) : ses prix ne sont pas relevés automatiquement.
