# 3dmodelsTAW

Modèles 3D low-poly pour Roblox, générés en Python avec Blender headless.

- Lancer : `python build.py [modele ...] [--no-preview]` (module pip `bpy`) ou `blender -b -P build.py -- ...`.
- Un modèle = `models/<nom>.py` avec `COLORS` (dict nom -> hex) et `build(pal)`. Partir de `models/_template.py`.
- Utiliser les primitives de `lib/roblox.py`. 1 unité = 1 stud, Z vers le haut.
- Après chaque modification, regénérer et regarder `previews/<nom>.png` pour vérifier le rendu (faces noires = normales inversées, pièces qui se chevauchent sur une même face, etc.).
- Committer les exports et les aperçus avec le code.
- Rester sous 20 000 triangles par modèle.
- Créatures : style **boss Roblox massif** sculpté en metaballs (`lib/sculpt.py`) : corps continu skinné, plaques/cornes grises, griffes claires, yeux lumineux. Peaux par (`group`, couleur), `group` séparé pour ce qui ne doit pas fusionner (mâchoire, plaques). Pièces pointues via `creature.spike` + `rig.add`. Fin de build : `sc.build(budget)`. (`lib/voxel.py` existe encore pour un style voxel.)
- Créatures animables : `build(pal)` renvoie un `lib.creature.Rig`. Chaque voxel/pièce porte un os du rig. Couleurs `glow*` = mesh lumineux. Les couleurs `glow` et `glow_hot` sont obligatoires (script d'effets). Os `FX_*` = points d'émission de flammes. Définir `TEST_POSE` et vérifier `previews/<nom>_pose.png`.
- Les créatures regardent vers -Y, pieds à z=0.
