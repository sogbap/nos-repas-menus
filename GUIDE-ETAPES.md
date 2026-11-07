# Écrire les étapes d'une recette

Les recettes de l'app s'adressent à quelqu'un qui n'a jamais cuisiné. Il peut y avoir beaucoup d'étapes : ce qui compte, c'est que rien ne soit sous-entendu et qu'on puisse réussir le plat du premier coup. On garde le plat tel qu'il est : mêmes ingrédients, mêmes quantités, même technique, mêmes temps de cuisson. On réécrit seulement la façon de l'expliquer.

## Les règles

1. **Une seule action par étape**, dans l'ordre réel du travail : d'abord préchauffer, couper et préparer, ensuite cuire. Le riz, les pâtes ou la semoule se lancent au moment où ils seront prêts en même temps que le reste, et le texte le dit.
2. **Un titre court** à l'infinitif, de 2 à 5 mots : « Couper les légumes ».
3. **Un texte à l'impératif avec « vous »**, en mots simples. Il dit :
   - quel ustensile (« dans la grande poêle ») ;
   - comment couper, avec la taille en cm ou en mm (« en rondelles de 1 cm ») ;
   - quel feu : doux, moyen ou vif ;
   - combien de temps, et ce qu'on fait pendant ce temps.
4. **Aucun mot de cuisinier.** On dit ce qu'il faut faire réellement :
   - émincer : couper en fines lamelles ou lanières, avec l'épaisseur ;
   - ciseler : hacher, ou couper en petits dés ;
   - réserver : mettre dans une assiette ;
   - saisir : faire dorer à feu vif ;
   - déglacer : verser le liquide et gratter le fond ;
   - faire revenir, faire suer : faire cuire en remuant, avec le résultat attendu ;
   - mijoter : laisser cuire à feu doux, de petites bulles doivent monter ;
   - délayer : mélanger jusqu'à ce qu'il n'y ait plus de grumeaux ;
   - blanchir, nacrer, torréfier, égrener, napper, concasser, effilocher, julienne : même principe.
5. **Un repère pour chaque cuisson** (`p`) : ce qu'on voit, sent ou entend quand c'est prêt. Une couleur, une texture, un test au couteau. Il complète la phrase « C'est prêt quand… », commence par une majuscule et finit par un point. Une étape avec minuteur a toujours un repère.
6. **Une mise en garde quand ça peut rater** (`a`) : ce qui brûle vite, ce qui gicle, que faire si c'est trop sec, se laver les mains après la volaille ou la viande crue.
7. **Aucune quantité liée au nombre de personnes dans le texte** : l'app les calcule et les affiche dans `i`. On écrit « la moitié de l'huile », « le reste du beurre », jamais « 20 g de beurre ». Les règles sans rapport avec le nombre de personnes restent permises : « 1 cm d'eau », « une pincée de sel », « 1 cuillère à soupe d'eau par personne ».
8. **La sécurité d'abord** : volaille et porc cuits à cœur (jus clair, plus de rose), viande hachée sans rose, moules jetées si elles restent fermées, poisson opaque au cœur.

Secret, veille, batch et texte du lendemain midi suivent les mêmes règles de vocabulaire.

## Les gestes qui reviennent

Ces formulations ont fait leurs preuves : reprends-les, en les adaptant au plat.

- **Riz** : « Rincez le riz dans une passoire et mettez-le dans une casserole avec l'eau et une pincée de sel. Portez à ébullition à feu vif, puis passez à feu doux, couvrez et lancez le minuteur. À la fin, coupez le feu et laissez 5 minutes à couvert. » Repère : « Toute l'eau est absorbée et les grains se séparent à la fourchette. »
- **Pâtes** : d'abord « Remplissez une grande casserole d'eau (au moins 1 litre pour 100 g de pâtes), couvrez et mettez à feu vif. », puis « Quand l'eau bout à gros bouillons, salez-la, versez les pâtes et remuez une fois. Vérifiez le temps sur le paquet. Avant d'égoutter, gardez une petite tasse d'eau de cuisson. » Repère : « Les pâtes sont tendres mais encore un peu fermes sous la dent. »
- **Semoule** : « Mettez la semoule dans un saladier avec une pincée de sel. Faites bouillir l'eau, versez-la dessus et couvrez avec une assiette. À la fin du minuteur, séparez les grains à la fourchette. »
- **Bouillon** : « Faites chauffer l'eau, émiettez le cube dedans et remuez jusqu'à ce qu'il soit fondu. »
- **Poisson surgelé** : « Le mieux est de le mettre la veille au frigo. Sinon, gardez les filets dans un sachet bien fermé et plongez-le 15 à 20 minutes dans un grand bol d'eau froide. Séchez-les ensuite avec du papier absorbant. »
- **Viande à dorer** : « Posez les morceaux sans qu'ils se touchent et laissez-les 3 minutes sans y toucher avant de les retourner. » Repère : « L'intérieur n'est pas encore cuit, c'est normal. », si la cuisson continue ensuite.
- **Laisser cuire** : « Quand ça bout, passez à feu doux et couvrez : de petites bulles doivent monter doucement. »
- **Moules** : « Rincez les moules sous l'eau froide, frottez ce qui colle à la coquille et tirez le petit fil qui dépasse. Tapotez celles qui sont ouvertes : si elles ne se referment pas en une minute, jetez-les. »

Une cuisson qui demande un geste à mi-parcours (retourner, remuer, ajouter) se coupe en deux étapes, chacune avec son minuteur : personne ne pense à regarder l'heure.

## Le format

Une recette garde tous ses champs. On change `etapes`, et on ajoute :

- `etapesVersion` : 1 ;
- `ustensiles` : le matériel à sortir, par exemple `["Cocotte avec couvercle", "planche et couteau"]`.

Chaque étape :

| Clé | Contenu |
| --- | --- |
| `n` | le titre court |
| `t` | le texte |
| `r` | `chef`, `commis` ou `ensemble`, comme à l'origine, pour pouvoir cuisiner à deux |
| `m` | les minutes de minuteur, s'il y en a un |
| `i` | ce qui sert à cette étape, avec les noms exacts des ingrédients |
| `p` | le repère |
| `a` | la mise en garde |
| `g` | les gestes expliqués dans l'app |

Dans `i` :

- `"Carotte"` : toute la carotte prévue par la recette ;
- `"Huile d'olive|0.5"` : la moitié de ce qui est prévu. Les parts d'un même ingrédient font 1 au total, et chaque ingrédient apparaît au moins une fois ;
- `"Eau=2*Riz basmati"` : 2 ml d'eau par gramme de riz. Riz basmati : 2. Riz rond : 1,5. Semoule : 1,4. Boulgour : 2. Farine de sarrasin (pâte à galette) : 2.

Gestes disponibles dans `g` : `mesures`, `sel`, `feu`, `four`, `coupes`, `oignon`, `ail`, `gingembre`, `citron`, `herbes`, `courge`, `poireau`, `chou`, `champignons`, `pommes-de-terre`, `frites`, `riz`, `pates`, `semoule`, `oeufs`, `volaille`, `dorer`, `sucs`, `reduire`, `poisson`, `moules`, `epinards`, `bouillon`, `boites`.

## Un exemple

```json
{
  "n": "Dorer les pilons",
  "t": "Séchez les pilons avec du papier absorbant et salez-les. Faites chauffer l'huile dans la cocotte à feu assez vif. Posez les pilons sans qu'ils se touchent et tournez-les toutes les 2 minutes. Mettez-les ensuite dans une assiette.",
  "r": "chef",
  "m": 8,
  "i": ["Pilons de poulet", "Huile d'olive|0.75"],
  "p": "Ils sont bien bruns de tous les côtés. L'intérieur n'est pas encore cuit, c'est normal.",
  "a": "Lavez-vous les mains au savon après avoir touché le poulet cru.",
  "g": ["volaille", "dorer"]
}
```

`python3 publish.py --verifier export` relit le résultat et liste ce qui reste à corriger.
