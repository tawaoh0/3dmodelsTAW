# API de modélisation (toolkit)

Conventions : 1 unité = 1 stud Roblox, Z vers le haut, la créature regarde vers **-Y**,
pieds à z = 0, côté gauche = x > 0 (`s = 1`, suffixe `_L`), droit = x < 0 (`s = -1`, `_R`).
On écrit les deux côtés avec `for s, side in ((1, "L"), (-1, "R")):`.

## Squelette d'animation (`lib/creature.py`)

```python
from lib import creature as c
rig = c.Rig(pal)
rig.bone("Root", (0, 0, 0), (0, 0, 1))                  # toujours un Root à l'origine
rig.bone("Hips", tête, queue, "Root")                   # nom, tête, queue, parent
rig.fx("EyeL", position, "Head")                        # crée l'os FX_EyeL (flammes)
rig.add(obj, "Head", "bone")                            # peint + attache rigidement à un os
rig.add(obj, "Head", "glow", glow=True)                 # partie lumineuse (mesh _Glow)
rig.add(obj, "Head", "bone", part="Head")               # range dans la pièce <nom>_Head
c.Chain(points).at(t) -> (point, tangente)              # t de 0 à 1 le long d'une polyligne
```

- Chaque pièce est rigide sur UN os (parfait pour un squelette). Exception : `membrane`, qui
  porte des poids par sommet.
- Os `FX_*` : le script d'effets y accroche flammes et braises. En mettre aux yeux, à la
  gueule, au cœur, au bout de queue.
- `EFFECT_THEME` (module) : thème des particules du script Roblox — `fire`, `acid` (bulles
  + gouttes qui tombent), `souls` (volutes), `frost` (brume qui retombe + flocons), `abyss`
  (lueurs qui dérivent + bulles), `blood` (nuage rouge qui retombe + bulles), `gold`. Un nouveau thème = une entrée dans `THEMES` de
  `lib/CreatureEffects.server.lua`.
- `TEST_POSE` : `{"Jaw": (30, 0, 0), ...}` rotations XYZ en degrés dans l'espace de l'os.
  X ouvre une mâchoire / plie une patte, Z balance une queue ou une aile.

## Pièces anatomiques (`lib/anatomy.py`, importé `as a`)

| Fonction | Usage |
|---|---|
| `loft_profile(name, sections, tip="round", droop=0.15)` | Crâne / mâchoire. Sections `(y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)` de l'arrière vers l'avant (y décroissant). Termine par un bout de museau arrondi ; `droop` > 0 le fait plonger (nez busqué), < 0 le relève (menton). `tip=None` = face plate (à éviter). |
| `hole_along(centre, axe, side, ra, rb, depth)` | Cutter selon un axe quelconque : naseaux creusés dans le bout du museau, fenêtres d'une plaque inclinée. |
| `width_at(sections, y, idx)` / `side_width(sections, y, z)` | Largeur / hauteur d'un crâne à la profondeur y ; `side_width` donne la demi-largeur **réelle à la hauteur z** pour poser anneaux, bosses et veines sur la paroi. |
| `hole_x(center, ry, rz)` | Cutter tunnel elliptique selon X (traverse les 2 côtés). |
| `cut(obj, [cutters])` | Booléen : perce l'objet, supprime les cutters. |
| `rotate_obj(obj, axe, angle, pivot)` | Tourne les **sommets** autour de `pivot`. Pour un objet créé avec `location=`, le pivot est `(0, 0, 0)`. Pour un cutter `hole_x`, son centre monde. |
| `long_bone(name, a, b, rayon, knob=1.6, condyles=True)` | Fémur, tibia, humérus… `condyles=False` pour les petits os. |
| `vertebra(name, centre, tangente, taille, spine=1.6, lean=0.35, transverse=True)` | Vertèbre avec épine en lame. Pour la queue passer la tangente directe ; pour dos/cou `-tangente`. |
| `disc(name, centre, tangente, taille)` | Disque entre deux vertèbres (couleur `disc`). |
| `rib(name, racine, demi_largeur, profondeur, côté, sweep, radius)` | Côte. |
| `blade(name, a, b, largeur, épaisseur, width_end, normal, bevel, mid)` | Os plat : omoplate, ilium, arcade, crête, collerette, chevrons. `normal` = direction de l'épaisseur. |
| `claw(name, base, direction, longueur, rayon, curl=0.35, segments=6)` | Griffe, croc, petite corne, épine. `curl` > 0 recourbe vers le bas, < 0 vers le haut. |
| `claw_point(base, direction, longueur, curl, t)` | Point + tangente à la fraction `t` d'une `claw` courbée : pour poser une pointe lumineuse, une goutte ou un anneau **sur** la courbe. |
| `smooth_path(points, n)` | Courbe lisse passant par des points de contrôle → `n` points réguliers : tentacules, queues souples, cous de serpent. |
| `oriented(obj, position, normale)` | Oriente un objet modélisé selon +Z vers `normale` et le pose : balanes, ventouses, pièces, gemmes posées sur une surface. |
| `ridged_horn(name, points, rayon, ridges=6)` | Grande corne annelée qui suit un chemin. |
| `spiral_points(base, side, back, up, coil, turns, spread)` | Chemin d'une corne de bélier (liste de points) : pour y poser bagues et gemmes. Rayon de la corne à la fraction t ≈ `rayon × (1 − t)^0.9`. |
| `ring_around(name, centre, axe, rayon, épaisseur)` | Anneau autour d'un axe : bague de corne, collier de cou, sertissage de gemme, boucle d'oreille. |
| `spiral_horn(name, base, side, back, up, rayon, coil, turns, spread)` | Corne de bélier enroulée (monte, part vers `back`, redescend, revient) ; `back=(0,-1,0)` l'enroule vers l'avant. |
| `crystal(name, centre, rayon, hauteur, sides=6)` | Cristal facetté (cœur, éclats). |
| `membrane(name, [(pos, {os: poids})], thickness)` | Membrane 2 faces (aile, collerette) ; triangulée en éventail depuis le 1er point. Peindre avec `rig.pal.paint(m, "membrane")` puis `m["part"] = "Wings"`. |
| `tattered_edge(a, b, poids_a, poids_b, vers, depth, notches, seed)` | Points d'un bord déchiré festonné entre deux pointes, creusé vers `vers`. |
| `band(name, points, heights, thickness, up=(0,0,1), offset=0.5)` | Plaque épaisse qui suit un chemin, hauteur variable selon `up` (`offset` 0 = monte depuis le chemin, 1 = descend). Mâchoires de requin, crêtes, visières sus-orbitaires, maxillaires/dentaires. Plus « os » qu'un tube. |

`membrane` sert aussi aux **lames fines** (crêtes dentelées, voiles dorsales, nageoires) :
un contour de points tous pondérés `{"Head": 1}` donne une plaque nette et fine, bien plus
élégante qu'un `blade` épais qui fait « couvercle ».

## Pièces détaillées (`lib/marine.py`, importé `as mr`) — posent directement sur le rig

| Fonction | Usage |
|---|---|
| `fin(rig, name, root, edge, bone, part, rays=8)` | Nageoire / voile / couronne riche : membrane au bord déchiré, rayons articulés à nœuds, épine d'attaque à piques, radiaux à la racine, pointes lumineuses. `root` = points sur le corps, `edge` = bord libre (de l'avant vers l'arrière). |
| `tooth(name, base, tip, width, thickness, out, curl=0.06)` | Grosse dent **pleine** (renvoie l'objet) : triangle épais à section lenticulaire, bords dentelés, courbée vers `-out`. `out` = normale extérieure de la mâchoire. ~80 triangles : prévoir une pièce `Teeth` pour 90 dents. |
| `spiky_orbit(rig, name, centre, axe, rayon, bone)` | Orbite à double anneau + couronne de piques. |
| `scutes(rig, name, points, normales, bone)` | Rangée d'écailles osseuses en losange posées sur une surface. |
| `scar(rig, name, a, b, bone)` | Cicatrice / fissure lumineuse en zigzag. |
| `hook(rig, name, base, direction, bone)` | Hameçon rouillé + maillons de chaîne. |
| `along(polyligne, f)` | Point à la fraction f d'une polyligne. |

## Primitives (`lib/roblox.py`, importé `as r`)

`r.ico(name, rayon, subdivisions, location, scale)`, `r.box(name, taille, location, rotation,
bevel_width)`, `r.tube(name, points, rayons, segments)`, `r.loft(name, anneaux)`,
`r.cylinder(...)`, `r.smooth(obj, angle)`, `r.join(objs, name)`.

## Budget de triangles (≤ 20 000 par mesh)

Ordres de grandeur mesurés : vertèbre ≈ 300, os long à condyles ≈ 250, sans condyles ≈ 110,
dent `segments=4` ≈ 40, griffe ≈ 70, corne annelée ≈ 450, crâne percé ≈ 500-900.

Si ça dépasse : `condyles=False` sur phalanges / métatarses / doigts, `bevel=0` sur les petites
lames (chevrons, apophyses), dents en `segments=4`, moins de vertèbres de queue (14-16),
`subdivisions=1` sur les petites boules. Si ça ne suffit pas (créature ailée, multi-têtes),
répartir : `part="Head"` (tête + cou), `part="Wings"`, `part="Tail"`… Chaque pièce devient un
MeshPart distinct qui partage le même squelette.

## Pièges connus (toutes les erreurs déjà commises)

Chacune a coûté au moins une itération. `check_model.py` détecte celles marquées (auto).

- **Pièce qui flotte loin du modèle** (auto) : rotation d'un `ico` créé avec `location=`
  autour de sa position monde. Ses sommets sont locaux : pivot `(0, 0, 0)`.
- **Détails posés derrière une plaque** au lieu de devant (collerette, crête) : la normale
  avant d'un plan engendré par `X` (largeur) et `U` (hauteur) vaut `X.cross(U)`, pas
  `U.cross(X)`. Vérifier sur le gros plan de face : si on voit les détails à travers les
  trous, ils sont derrière.
- **Points lumineux « ligne latérale » qui flottent** (auto) : les poser au bout des
  apophyses transverses (`p + side·size·1.0 + up·size·0.5`), seulement là où elles existent.
- **Cou trop fin sous une grosse tête** : le profil de taille d'un serpent doit rester épais
  jusqu'au cou (ne pas le faire retomber à zéro au bout avant de la colonne).
- **Tête qui regarde le ciel** au bout d'un cou qui monte : ne pas orienter la tête selon la
  tangente du cou ; mélanger avec l'horizontale, ex. `f = (tangente * 0.25 + (0, -1, -0.15))`.
- **Côtes de serpent qui ressemblent à des pattes** : les enrouler autour du corps (4 points,
  le dernier revient sous la colonne), pas vers le sol.
- **Index de vertèbres codés en dur** (`SPINE[25]`) : dès qu'on change le nombre de vertèbres
  (pour boucher les trous), tout se décale. Exprimer les positions en fraction de la colonne.
- **Longs membres qui passent devant le visage** (tentacules, cous, bras levés) : les faire
  partir des côtés et s'écarter avant de monter ; vérifier sur le gros plan de face.
- **Structure trop régulière** (cage de cerceaux et barreaux identiques) : préférer une
  forme anatomique (côtes qui partent d'une colonne et s'ouvrent), avec variations.
- **Anneau d'orbite ou bosse qui dépasse dans le vide** : posé à la largeur max des joues
  alors que le crâne est plus étroit à cette hauteur. Utiliser `side_width(sections, y, z)`.
- **Pièce volontairement suspendue** (pièces d'or en orbite, runes flottantes non
  lumineuses) : `obj["float_ok"] = True` avant `rig.add`, sinon `check_model.py` la refuse.
- **Écarts entre vertèbres en bout de queue** (auto) : la queue s'affine mais l'espacement
  reste constant. Prendre `n ≥ longueur / (0.8 × taille moyenne)` vertèbres, et une taille
  minimale en bout (≈ 0.15) ; s'y prendre dès le premier jet (c'est l'erreur la plus
  fréquente des créatures longues : requin, serpent, hydre).
- **Ergot, sternum ou petite pièce décollés** (auto) : les décaler d'une distance inférieure
  à leur propre rayon par rapport à l'os porteur.

- **Pièce qui flotte loin du modèle** : rotation d'un `ico` créé avec `location=` autour de sa
  position monde. Pivot `(0, 0, 0)`.
- **Pointe / goutte à côté d'une corne courbée** : ne pas la placer sur la ligne droite
  `base + d·L·t` ; utiliser `claw_point` (la courbe s'écarte de la droite de `curl·L·t²`).
- **Membrane percée par booléen qui perd des faces** : le contour doit être convexe et ne pas
  se recouper (ex. centre + demi-ovale), sinon `cut` interprète mal l'intérieur.
- **Élément qui semble flotter sur l'aperçu** alors que `check_model.py` est OK : sa base est
  cachée par une autre pièce sous cet angle. Corriger `VIEW` ou supprimer l'élément mal placé
  (ex. pointes horizontales au bas d'une collerette).
- **Partie d'une surface qui « disparaît » sur l'aperçu** : vérifier avec `scene.ray_cast`
  avant de chercher un bug de géométrie ; souvent c'est une autre pièce devant (cornes devant
  la collerette). L'éclairage des aperçus inclut une lumière depuis la caméra, donc une zone
  à l'ombre ne se confond plus avec le fond.
- **Pièce invisible** : un os plat dont `normal` est parallèle à `b - a` (largeur nulle).
- **Aile vue par la tranche** dans l'aperçu : changer `VIEW` (ex. `(0.4, -1, 0.8)`).
- **Mâchoire qui ne s'ouvre pas bien** : la tête de l'os `Jaw` doit être à l'articulation
  (arrière de la mâchoire), sa queue vers le menton.
- **Couleur inconnue** : toute couleur passée à `rig.add` doit exister dans `COLORS`.
