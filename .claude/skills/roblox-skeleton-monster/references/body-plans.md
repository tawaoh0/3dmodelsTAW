# Plans de corps

Choisir le plan le plus proche de la description, puis l'adapter. Les cotes sont en studs,
pour une créature « boss » de 15-20 studs de long. Mettre à l'échelle si besoin.

## Bipède théropode (T-Rex, raptor, allosaure…) — exemple : `skeleton_trex.py`

Colonne quasi horizontale à z ≈ 4.8, hanches à y ≈ +0.6, épaules y ≈ -2.2, crâne de y -3 à -7.
Os : `Root, Hips, Spine, Neck, Head, Jaw, Tail1-4, Thigh/Shin/Foot_L/R, UpperArm/Forearm_L/R`.
Pattes : hanche → genou (vers l'avant, plus bas) → cheville (vers l'arrière, z ≈ 1) → 3 orteils.
Raptor : plus petit (≈ 10 studs), cou en S, bras longs à 3 doigts griffus, grande griffe
faucille relevée sur le 2e orteil, queue raide et droite.

## Quadrupède (loup, tricératops, chien des enfers…) — base : `skeleton_dragon.py` sans ailes

Colonne z ≈ 5, épaules y ≈ -2, hanches y ≈ +1.5.
Os : `Root, Hips, Chest, Neck1-2, Head, Jaw, Tail1-5, UpperArm/Forearm/Hand_L/R,
Thigh/Shin/Foot_L/R`. Patte avant : omoplate (blade) → humérus → radius + cubitus → 4 doigts.
Patte arrière : ilium (blade) + fémur → tibia → 3-4 orteils + ergot.

## Quadrupède ailé (dragon, wyverne, griffon…) — exemple : `skeleton_dragon.py`

Comme le quadrupède, plus par aile : `Wing1` (épaule → coude), `Wing2` (coude → poignet),
`WingFinger1-4` (poignet → pointes). Membrane : un panneau entre chaque paire de doigts, un
panneau intérieur doigt 4 → hanche → dos → épaule → coude, un propatagium épaule → poignet.
Bords avec `tattered_edge`. Wyverne : pas de pattes avant, les ailes servent de bras.
Pièces : corps / `Head` / `Wings` pour tenir le budget. `VIEW = (0.4, -1, 0.8)`.

## Serpent / naga / ver géant

Pas de pattes. Colonne longue en S posée au sol (z ≈ 0.5-1.5) avec 30-40 vertèbres réparties
sur 8-10 os `Body1…BodyN` (une `Chain` sinueuse), côtes sur presque toute la longueur, tête
levée. Naga : torse humanoïde dressé à l'avant. Budget : `part="Tail"` pour l'arrière.

## Multi-têtes (hydre, cerbère) — exemple : `skeleton_hydra.py`

Corps bas (rampant ou quadrupède), puis N cous partant de l'avant du thorax en éventail.
Os : `Neck{A,B,C}1-2`, `Head{A,B,C}`, `Jaw{A,B,C}` (le contrôle compte les détails par tête).

Méthode qui marche :
- Modéliser **chaque tête dans son repère local** (articulation à l'origine, museau vers -Y),
  puis la placer avec une matrice `Translation(bout du cou) @ Rotation(lacet, Z) @
  Rotation(tangage, X) @ Scale(HEAD_SCALE)` appliquée aux nouveaux objets (`place()`), et aux
  os / os FX avec la même matrice.
- Têtes à ≈ 80 % de la taille d'une tête unique, cous longs et bien écartés (lacet ±0.5),
  à des hauteurs différentes, pour qu'aucune tête n'en masque une autre.
- **Les têtes sont identiques** (préférence explicite de l'utilisateur : une version avec
  3 crânes différents a été refusée). Une seule fonction `build_head(rig, key)` appelée pour
  chaque cou ; y mettre tout l'effort de détail. Une pièce Roblox par tête
  (`part="HeadA"`…) avec son cou : chaque tête dispose ainsi de 20 000 triangles.
- Un ornement en haut de chaque cou (collier) relie visuellement tête et corps ; le placer
  avec `Chain(cou).at(0.7)` pour qu'il ne soit pas caché dans la mâchoire.
- `VIEW` de face plongeant, ex. `(0.35, -1, 0.75)`, pour montrer l'éventail.

## Céphalopode (kraken, calmar, pieuvre) — exemple : `abyss_kraken.py`

Tête (capsule `loft_profile` le long de Y) avec deux yeux géants sur les flancs, bec de
perroquet dessous, siphon devant. Au-dessus, le **manteau** dressé : plume dorsale (gladius)
+ **côtes qui partent du dos et s'ouvrent devant** (une cage fermée régulière fait « cage à
oiseaux »), nageoires en membrane à rayons. 8 bras étalés au sol (`smooth_path` sur 6 points de
contrôle, 13 segments, 4 os chacun) reliés à la base par une **membrane** (calmar-vampire),
2 longs tentacules dressés **sur les côtés** (pas devant le visage) avec massue à crochets.
Os : `Head`, `Mantle`, `Jaw`, `Arm{0-7}_1-4`, `Tentacle_{L,R}_1-5`. Pièces : corps / `Arms` /
`Tentacles`.

## Arthropode (araignée, scorpion, mante)

Céphalothorax + abdomen en `blade`/`loft_profile`, pattes à 4 segments (`long_bone` sans
condyles) avec os `Leg1_L…Leg4_R` (+ `Leg1b_L` pour le segment suivant), chélicères / pinces
en `claw` épais, dard de queue segmenté. Exosquelette « os » ivoire, yeux multiples lumineux.

## Humanoïde (liche, démon, chevalier squelette)

Os type R15 pour réutiliser des animations : `Root, LowerTorso, UpperTorso, Head, Jaw,
LeftUpperArm, LeftLowerArm, LeftHand, RightUpperArm…, LeftUpperLeg, LeftLowerLeg, LeftFoot…`
Ajouter cornes, couronne, ailes ou arme selon la description.
