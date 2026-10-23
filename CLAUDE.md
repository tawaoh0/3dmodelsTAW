# 3dmodelsTAW

Modèles 3D low-poly pour Roblox, générés en Python avec Blender headless.

- Lancer : `python build.py [modele ...] [--no-preview]` (module pip `bpy`) ou `blender -b -P build.py -- ...`.
- Un modèle = `models/<nom>.py` avec `COLORS` (dict nom -> hex) et `build(pal)`. Partir de `models/_template.py`.
- Utiliser les primitives de `lib/roblox.py`. 1 unité = 1 stud, Z vers le haut.
- Créatures : lancer d'abord `python .claude/skills/roblox-skeleton-monster/scripts/check_model.py <nom>` (pièces flottantes, budget, densité de la tête), puis `closeup.py <nom> Head <prefixe> trio` pour 3 gros plans.
- Après chaque modification, regénérer et regarder `previews/<nom>.png` pour vérifier le rendu (faces noires = normales inversées, pièces qui se chevauchent sur une même face, etc.).
- Committer les exports et les aperçus avec le code.
- Rester sous 20 000 triangles par modèle.
- Créatures : **toujours des squelettes** démoniaques, détaillés et nets (pas de formes molles/pâte à modeler). Construire os par os avec `lib/anatomy.py` : `loft_profile` + `cut`/`hole_x` (crâne aux ouvertures booléennes), `long_bone` (condyles), `vertebra` + `disc`, `rib`, `blade` (os plats), `claw`, `ridged_horn`, `crystal`. Os ivoire, cornes/griffes noires, lueur d'une teinte par créature. Le budget de 20 000 triangles est serré : `condyles=False` pour les petits os, pas de biseau sur les petites lames, dents en `segments=4`. Si ça ne tient pas, répartir sur plusieurs MeshParts avec `rig.add(..., part="Head")` (ex. dragon : corps / Head / Wings). Ailes : `anatomy.membrane` + `tattered_edge` (poids par sommet sur les os des doigts). `VIEW` dans le module pour changer l'angle de l'aperçu.
- Créatures animables : `build(pal)` renvoie un `lib.creature.Rig`. Chaque voxel/pièce porte un os du rig. Couleurs `glow*` = mesh lumineux. Les couleurs `glow` et `glow_hot` sont obligatoires (script d'effets). Os `FX_*` = points d'émission de flammes. Définir `TEST_POSE` et vérifier `previews/<nom>_pose.png`.
- Les créatures regardent vers -Y, pieds à z=0.
- Nageoires, couronnes, voiles : `lib/marine.py` (`fin` riche, `spiky_orbit`, `scutes`, `scar`, `hook`). Jamais de longue bande de membrane d'une couleur sur le corps.
- Crânes : partir d'un vrai animal lié au thème (bélier, loup, vipère…), bout de museau arrondi (`loft_profile` le fait par défaut ; les 4 premières créatures gardent `tip=None` car validées ainsi).
- Skill partageable `.claude/skills/roblox-skeleton-monster/` (description de monstre → squelette Roblox). Après toute modif de `lib/` ou `build.py`, lancer `bash tools/sync_skill_toolkit.sh` pour mettre à jour sa copie de la boîte à outils, et y reporter les nouvelles leçons de style dans `references/style-guide.md`.
