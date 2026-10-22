# 3dmodelsTAW

Modèles 3D low-poly pour Roblox, générés en Python avec Blender headless.

- Lancer : `python build.py [modele ...] [--no-preview]` (module pip `bpy`) ou `blender -b -P build.py -- ...`.
- Un modèle = `models/<nom>.py` avec `COLORS` (dict nom -> hex) et `build(pal)`. Partir de `models/_template.py`.
- Utiliser les primitives de `lib/roblox.py`. 1 unité = 1 stud, Z vers le haut.
- Après chaque modification, regénérer et regarder `previews/<nom>.png` pour vérifier le rendu (faces noires = normales inversées, pièces qui se chevauchent sur une même face, etc.).
- Committer les exports et les aperçus avec le code.
- Rester sous 20 000 triangles par modèle.
