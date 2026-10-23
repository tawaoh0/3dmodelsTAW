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
- `TEST_POSE` : `{"Jaw": (30, 0, 0), ...}` rotations XYZ en degrés dans l'espace de l'os.
  X ouvre une mâchoire / plie une patte, Z balance une queue ou une aile.

## Pièces anatomiques (`lib/anatomy.py`, importé `as a`)

| Fonction | Usage |
|---|---|
| `loft_profile(name, sections)` | Crâne / mâchoire. Sections `(y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)` de l'arrière vers l'avant (y décroissant). |
| `hole_x(center, ry, rz)` | Cutter tunnel elliptique selon X (traverse les 2 côtés). |
| `cut(obj, [cutters])` | Booléen : perce l'objet, supprime les cutters. |
| `rotate_obj(obj, axe, angle, pivot)` | Tourne les **sommets** autour de `pivot`. Pour un objet créé avec `location=`, le pivot est `(0, 0, 0)`. Pour un cutter `hole_x`, son centre monde. |
| `long_bone(name, a, b, rayon, knob=1.6, condyles=True)` | Fémur, tibia, humérus… `condyles=False` pour les petits os. |
| `vertebra(name, centre, tangente, taille, spine=1.6, lean=0.35, transverse=True)` | Vertèbre avec épine en lame. Pour la queue passer la tangente directe ; pour dos/cou `-tangente`. |
| `disc(name, centre, tangente, taille)` | Disque entre deux vertèbres (couleur `disc`). |
| `rib(name, racine, demi_largeur, profondeur, côté, sweep, radius)` | Côte. |
| `blade(name, a, b, largeur, épaisseur, width_end, normal, bevel, mid)` | Os plat : omoplate, ilium, arcade, crête, collerette, chevrons. `normal` = direction de l'épaisseur. |
| `claw(name, base, direction, longueur, rayon, curl=0.35, segments=6)` | Griffe, croc, petite corne, épine. `curl` > 0 recourbe vers le bas, < 0 vers le haut. |
| `ridged_horn(name, points, rayon, ridges=6)` | Grande corne annelée qui suit un chemin. |
| `crystal(name, centre, rayon, hauteur, sides=6)` | Cristal facetté (cœur, éclats). |
| `membrane(name, [(pos, {os: poids})], thickness)` | Membrane 2 faces (aile, collerette) ; triangulée en éventail depuis le 1er point. Peindre avec `rig.pal.paint(m, "membrane")` puis `m["part"] = "Wings"`. |
| `tattered_edge(a, b, poids_a, poids_b, vers, depth, notches, seed)` | Points d'un bord déchiré festonné entre deux pointes, creusé vers `vers`. |

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

## Pièges connus

- **Pièce qui flotte loin du modèle** : rotation d'un `ico` créé avec `location=` autour de sa
  position monde. Pivot `(0, 0, 0)`.
- **Pièce invisible** : un os plat dont `normal` est parallèle à `b - a` (largeur nulle).
- **Aile vue par la tranche** dans l'aperçu : changer `VIEW` (ex. `(0.4, -1, 0.8)`).
- **Mâchoire qui ne s'ouvre pas bien** : la tête de l'os `Jaw` doit être à l'articulation
  (arrière de la mâchoire), sa queue vers le menton.
- **Couleur inconnue** : toute couleur passée à `rig.add` doit exister dans `COLORS`.
