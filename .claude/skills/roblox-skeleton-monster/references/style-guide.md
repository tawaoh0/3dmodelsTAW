# Style guide — squelettes démoniaques Roblox

Ce guide vient d'itérations réelles avec l'utilisateur. Chaque règle a une raison : elle
corrige un rendu qui a été refusé.

## Ce qui a été validé

- **Toujours un squelette**, os par os : crâne, mâchoire articulée, vertèbres, côtes,
  bassin, os longs, phalanges. Pas de chair, pas de peau.
- **Formes nettes et lisibles** façon « boss Roblox » : os épais, articulations renflées
  (condyles), arêtes franches, gros volumes qui se lisent de loin.
- **Palette de base** : os clairs, dents plus claires, cornes et griffes presque noires,
  pointes teintées de la lueur, disques intervertébraux sombres teintés de la lueur. La
  teinte exacte des os change d'une créature à l'autre (voir « Identité »).
- **Une teinte de lueur par créature** (rouge braise, violet, vert toxique, bleu glacé,
  or…) sur : yeux au fond des orbites, cœur de cristal dans la cage thoracique, runes
  (crâne, fémurs, avant-bras), gorge, pointe de queue.
- **Détails démoniaques** : grandes cornes annelées (`ridged_horn`), pointes noires sur les
  épines dorsales, griffes recourbées, ergots, cristaux.

## Ce qui a été rejeté (et pourquoi)

| Rejeté | Ce que l'utilisateur a dit | À faire à la place |
|---|---|---|
| Os fins, sombres, petits | « moche » | Os épais, ivoire, contrastés avec les cornes noires |
| Voxels | « moche… pas forcément voxel » | Géométrie lisse à arêtes nettes |
| Metaballs / corps en chair | « grosse boule de pâte à modeler » | Pièces osseuses distinctes, découpes booléennes |
| Crâne du dragon = crâne du T-Rex | « la tête est trop la même » | Un crâne conçu pour chaque créature |
| Crâne en coin droit et pointu | « manque de grand relief / de parties, toute droite et pointue » | Profil ondulé + grosses pièces en relief (voir ci-dessous) |
| T-Rex, dragon, raptor tous ivoire + cornes noires annelées balayées + cœur cristal | « ils se ressemblent trop tous entre eux » | Une identité complète par créature (section suivante) |
| Museaux qui finissent sur une face plate ; crânes « reptile standard » | « les visages sont encore trop génériques, le nez se coupe net » | Bout de museau arrondi (`loft_profile` le fait par défaut) + crâne inspiré d'un **vrai animal** lié au thème |
| Hydre avec 3 crânes différents (royal, serpent, brute) | « je veux que les 3 têtes soient les mêmes, travaille-les plus » | Différencier les **créatures** entre elles, pas les têtes d'une même créature ; une seule tête très détaillée, répétée |

## Identité : chaque créature doit se distinguer sur 4 axes

Avant de modéliser, lister les créatures déjà présentes dans `models/` et remplir ce tableau
pour la nouvelle, en choisissant pour **chaque ligne** une valeur qu'aucune autre n'utilise :

| Axe | T-Rex | Dragon | Raptor | Tricératops | Hydre | Idées libres |
|---|---|---|---|---|---|---|
| Matière / couleur des os | ivoire `#ddd0b8` | ivoire froid `#dcd3c8` | vert-gris rongé `#c4c9a0` + cratères lumineux | givré blanc-bleuté `#d6e4ec` + grappes de cristaux | dorés `#e3c068` + pièces d'or incrustées | os calcinés noirs fissurés de lave, obsidienne, os dorés, os rouges sanglants, os translucides |
| Cornes / pointes | 2 grandes cornes annelées noires recourbées | couronne : 2 cornes plaquées + collerette palmée | **aucune corne** : éventails de piquants-plumes + crêtes jumelles dentelées | 3 cornes de **glace facettée** + collerette percée bordée d'éclats | **cornes de bélier en spirale** (bronze sombre) baguées d'or, 3 têtes identiques |  ramures, lames, couronne de piques, épines dorsales en voile |
| Silhouette / posture | massif bipède, tête énorme | quadrupède ailé, cou en S dressé | petit bipède ramassé prêt à bondir | quadrupède trapu et bas, tête baissée pour charger, sabots | corps rampant, pattes de crocodile, 3 cous en éventail | dressé sur 2 pattes, rampant au sol, enroulé, voûté, multi-têtes |
| Thème d'effets (`EFFECT_THEME`) | `fire` + cœur cristal | `fire` violet + cœur cristal | `acid` + poche d'acide, gouttes | `frost` + cœur en grappe de glace, stalactites | `gold` + idole de cristal, pièces en orbite, gemmes | `souls`, lave, sang, ombre |

Le cœur lumineux, les runes et la pointe de queue prennent aussi la forme du thème : cristal
pour le feu, poche à bulles pour l'acide, flamme spectrale pour les âmes, stalactites pour le
givre, lingots / pièces pour l'or. Vérifier sur les aperçus côte à côte que la nouvelle
créature se reconnaît **en silhouette** (sans les couleurs) et **en couleur** (sans la forme).

## Le crâne : la pièce la plus importante

Un bon crâne combine :

0. **Un vrai animal comme modèle**, choisi pour aller avec le thème de la créature, puis
   exagéré. Ne pas partir d'un « crâne de reptile » générique. Exemples :
   - cornes de bélier → crâne de **bélier** : nez busqué (le dessus du profil s'arrondit
     vers le bas jusqu'au museau), front large et plat, orbites saillantes en manchon,
     tubercules sous les yeux, naseaux creusés dans le bout du museau ;
   - loup / chien des enfers → crâne de **loup** : stop marqué entre front et museau,
     crête sagittale haute, arcades zygomatiques très larges, canines énormes ;
   - serpent → crâne de **vipère** : tête en triangle plat, crochets repliés, écailles
     sus-orbitaires ;
   - oiseau / griffon → crâne de **rapace** : bec crochu, grandes orbites cerclées d'os.
   Écrire en commentaire au-dessus de `SKULL` l'animal choisi et ses 3-4 traits clés.

1. **Un profil qui ondule** (ligne du dessus vue de côté) : dôme crânien → arcade au-dessus
   des yeux → creux nasal → bosse des narines → bout de museau arrondi ou carré. Jamais une
   ligne droite qui finit en pointe. Concrètement : 7 à 9 sections `SKULL` dont le `z dessus`
   monte et descend.
   Le bout du museau ne doit **jamais** être une face plate : `loft_profile` ajoute un
   dôme arrondi par défaut (`tip="round"`, `droop` pour faire plonger le nez).
2. **De vraies ouvertures** découpées (`hole_x` + `cut`) : orbites, fenêtres temporales et
   antorbitales, narines. Inclinées (`rotate_obj` sur le cutter) pour un regard mauvais.
   L'œil lumineux est placé au fond de l'orbite.
3. **Au moins 4 pièces en relief** posées sur le crâne : arcades sourcilières en corniche
   (`blade` épais), pommettes en arche (`tube` épais + piques), bourrelets nasaux, bosses de
   narines, crête sagittale ou pariétale, collerette (piques + `membrane`), cornes de nez,
   ergot de menton, apophyses de mâchoire.
4. **Une signature unique par créature**, choisie selon l'animal :
   - T-Rex : crâne haut et massif, grandes fenêtres, cornes recourbées, rune frontale ;
   - dragon : dôme + corniches sourcilières + pommettes à piques + collerette palmée +
     deux longues cornes plaquées ;
   - raptor : crâne bas et long, museau effilé mais **bosselé**, crête nasale en scie,
     dents en dents de scie, grande griffe faucille au pied ;
   - tricératops : collerette osseuse géante percée de trous, trois cornes, bec ;
   - hydre / serpent : crânes plats en losange, crochets à venin, capuchon de côtes ;
   - loup / chien des enfers : museau court et haut, crocs énormes, crête dorsale de flammes.
5. **Deux paires de crocs plus longs** à l'avant et une rangée plus courte derrière.

## Densité de détails (demandé deux fois par l'utilisateur)

Une grande surface lisse et vide fait « pas fini ». Règle : aucune zone plate de plus
d'environ 1 stud² sans détail. Pour chaque grande surface, combiner au moins 3 de ces couches :

| Couche | Exemples | Outils |
|---|---|---|
| Bourrelets autour des ouvertures | anneau d'os autour des orbites et des fenêtres de collerette | `r.tube(..., closed=True)` sur un anneau de points |
| Nervures / arêtes | baleines d'éventail sur une collerette, arête nasale, crête de mâchoire | `r.tube` sur 2-3 points posés sur la surface |
| Bord découpé | nodules osseux alternés avec des éclats, festons, dents | `r.ico` aplatis + `claw` le long du bord |
| Excroissances du thème | cristaux de glace, piquants-plumes, cratères d'acide, flammèches | grappes de `claw`, `ico` lumineux |
| Lignes lumineuses | veines de givre, fissures de lave, runes | `r.tube` fin (rayon ≈ 0.03) en zigzag, couleur `glow` |
| Anneaux sur les cornes | fourreau d'os, bagues | anneaux placés avec `claw_point` |
| Bosses et rugosités | bosses sus-orbitaires, bosses de pommettes, nodules sur le museau | `r.ico(subdivisions=1)` aplatis |
| Ornements « éléments supplémentaires » | bagues d'or sur les cornes, diadème avec gemme sertie, boucles d'oreille, couronne de piques à gemmes, collier hérissé, barbe d'épines | `ring_around`, `spiral_points` / `claw_point` pour poser sur une corne, `crystal` + anneau de sertissage |

Quand l'utilisateur demande « plus de détails / d'éléments supplémentaires », ajouter une
couche d'**ornements** en plus des détails osseux : c'est ce qui a fait la différence sur
l'hydre (125 pièces par tête).

Repère : une tête réussie compte **plus de 100 pièces** (crâne + mâchoire + détails), le
tricératops final en a 131 pour 6 000 triangles. `check_model.py` prévient sous 45.

## Silhouette générale

- Proportions « jeu » : tête un peu grosse (≈ 20 % de la longueur hors queue), pattes et
  griffes généreuses, queue longue qui s'affine.
- Colonne continue (vertèbres + disques), épines de dos plus hautes au milieu, pointes noires
  une épine sur deux (ou toutes, pour un dragon).
- Cage thoracique bombée, côtes ventrales (gastralia) pour les reptiles, sternum.
- Les pattes posent au sol (z = 0), la créature regarde vers -Y.

## Contrôle qualité (à vérifier sur les images à chaque itération)

- [ ] `check_model.py` affiche « Contrôle OK » (rien ne flotte, budget respecté).
- [ ] Sur les 3 gros plans : les détails sont sur la face visible des plaques, rien n'est
      masqué par l'angle de vue, aucune grande surface n'est vide.
- [ ] Pas de face noire ni de trou non voulu.
- [ ] Le museau se termine en bout arrondi (pas de face plate) et le crâne évoque l'animal
      choisi comme modèle.
- [ ] Le crâne a un profil ondulé et ≥ 4 pièces en relief ; il ne ressemble à aucune
      créature déjà faite dans le projet.
- [ ] Le tableau « Identité » est rempli : couleur des os, cornes, posture et thème
      d'effets différents de toutes les créatures existantes.
- [ ] La pose de test montre la gueule ouverte, une patte avancée, etc., et chaque pièce
      suit son os sans se détacher.
- [ ] Les ailes (s'il y en a) sont visibles de face sur l'aperçu, pas par la tranche
      (ajuster `VIEW`), et la membrane s'étire dans la pose.
- [ ] Chaque mesh ≤ 20 000 triangles.
- [ ] La lueur est visible : yeux, cœur, au moins une rune, pointe de queue ou équivalent.
