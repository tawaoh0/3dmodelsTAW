# 3dmodelsTAW

Modèles 3D pour mes jeux Roblox, générés **par code** avec Blender en mode headless (sans interface).

| Arbre | Coffre au trésor | Épée |
|---|---|---|
| ![tree](previews/tree.png) | ![chest](previews/treasure_chest.png) | ![sword](previews/sword.png) |

## Installation

Au choix :

- **Blender** (4.x ou 5.x) installé normalement, ou
- **module Python** : `pip install bpy` (Python 3.13 pour bpy 5.x)

## Générer les modèles

```bash
# Tous les modèles
blender -b -P build.py
# ou
python build.py

# Seulement certains, sans rendu d'aperçu (plus rapide)
python build.py sword tree --no-preview
```

Résultats :

- `exports/<modele>/<modele>.fbx` : à importer dans Roblox (texture embarquée)
- `exports/<modele>/<modele>.obj` + `.mtl` + `_palette.png` : alternative OBJ
- `previews/<modele>.png` : aperçu rendu

## Importer dans Roblox Studio

1. **Avatar → Import 3D** (ou *Home → Import 3D*), choisir le `.fbx`.
2. Dans les options, **File Dimensions : Studs** (1 unité Blender = 1 stud).
3. Le modèle arrive en un seul `MeshPart` avec sa texture, origine posée au sol.

## Créer un nouveau modèle

1. Copier `models/_template.py` en `models/mon_modele.py`.
2. Définir la palette `COLORS` et la fonction `build(pal)` avec les primitives de
   `lib/roblox.py` :
   - formes : `box` (avec `bevel_width`), `cylinder`, `cone`, `ico`, `torus`
   - formes libres : `loft` (relie des sections), `tube` (suit un chemin, rayon variable), `ring`
   - retouches : `bevel`, `smooth` (ombrage lisse), `cut_below`, `jitter`
3. Peindre chaque pièce : `pal.paint(objet, "nom_couleur")`.
4. `python build.py mon_modele`

Conventions :

- Z vers le haut dans Blender (converti automatiquement en Y pour Roblox).
- Style low-poly détaillé (biseaux, rivets, planches…), une seule texture palette par modèle → léger et performant.
- Limite Roblox : 20 000 triangles par MeshPart (vérifiée au build).

## Créatures animables (squelettes mythiques)

| T-Rex squelette démoniaque | Pose de test (rig) |
|---|---|
| ![trex](previews/skeleton_trex.png) | ![trex pose](previews/skeleton_trex_pose.png) |

| Dragon squelette ailé | Pose de test (rig) |
|---|---|
| ![dragon](previews/skeleton_dragon.png) | ![dragon pose](previews/skeleton_dragon_pose.png) |

![dragon tête](previews/skeleton_dragon_head.png) ![dragon tête face](previews/skeleton_dragon_head_front.png)

| Raptor squelette rongé d'acide | Pose de test (rig) |
|---|---|
| ![raptor](previews/skeleton_raptor.png) | ![raptor pose](previews/skeleton_raptor_pose.png) |

![raptor tête](previews/skeleton_raptor_head.png) ![raptor tête face](previews/skeleton_raptor_head_front.png)

| Tricératops squelette givré | Pose de test (rig) |
|---|---|
| ![triceratops](previews/skeleton_triceratops.png) | ![triceratops pose](previews/skeleton_triceratops_pose.png) |

![triceratops tête](previews/skeleton_triceratops_head.png) ![triceratops tête face](previews/skeleton_triceratops_head_front.png)

| Hydre squelette dorée à 3 têtes identiques | Pose de test (rig) |
|---|---|
| ![hydre](previews/skeleton_hydra.png) | ![hydre pose](previews/skeleton_hydra_pose.png) |

![hydre tête](previews/skeleton_hydra_head.png) ![hydre tête face](previews/skeleton_hydra_head_front.png)

Les créatures sont des **squelettes démoniaques** construits os par os avec `lib/anatomy.py` :
crâne en sections avec de vraies ouvertures (booléens), os longs à condyles, vertèbres à épines
en lame, côtes, os plats, griffes et cornes annelées, cristaux. Chaque pièce est rigide et
rattachée à un os du rig.

Un modèle de créature renvoie un `Rig` depuis `build(pal)` (voir `models/skeleton_trex.py`,
`lib/creature.py`).

Le build produit dans `exports/<creature>/` :

- `<creature>.fbx` : armature (os `Root` à la racine) + meshes skinnés :
  `<creature>` (corps), éventuellement des pièces en plus (`<creature>_Head`,
  `<creature>_Wings`… pour rester sous 20 000 triangles par MeshPart), et
  `<creature>_Glow` (yeux, runes, cristaux).
- `<creature>_effects.server.lua` : script d'effets avec la couleur de la créature.
- `previews/<creature>_pose.png` : rendu dans une pose de test, pour vérifier que
  chaque pièce suit bien son os.

### Dans Roblox Studio

1. **Import 3D** du `.fbx`, **File Dimensions : Studs**, rig type *Custom* : Studio
   crée un Model avec les MeshParts, les `Bone` et un `AnimationController`.
2. Glisser `<creature>_effects.server.lua` comme **Script** dans ce Model :
   les pièces `_Glow` passent en Neon avec une lumière qui pulse, et des flammes et
   braises apparaissent sur chaque os `FX_*` (yeux, cœur, bout de queue…).
3. Animer avec l'**Animation Editor** (marche, morsure, rugissement…).

## Pack 2 — Abysses

| Kraken squelette | Pose de test (rig) |
|---|---|
| ![kraken](previews/abyss_kraken.png) | ![kraken pose](previews/abyss_kraken_pose.png) |

![kraken profil](previews/abyss_kraken_head.png) ![kraken face](previews/abyss_kraken_head_front.png)

| Mégalodon squelette | Pose de test (rig) |
|---|---|
| ![megalodon](previews/abyss_megalodon.png) | ![megalodon pose](previews/abyss_megalodon_pose.png) |

![megalodon tête](previews/abyss_megalodon_head_front.png)

| Léviathan squelette | Pose de test (rig) |
|---|---|
| ![leviathan](previews/abyss_leviathan.png) | ![leviathan pose](previews/abyss_leviathan_pose.png) |

![leviathan tête](previews/abyss_leviathan_head_front.png)

| Crabe titan squelette | Pose de test (rig) |
|---|---|
| ![crabe](previews/abyss_crab.png) | ![crabe pose](previews/abyss_crab_pose.png) |

Exosquelette d'obsidienne fissuré de lave, carapace ajourée sur un cœur de lave, 3 cheminées
hydrothermales qui fument (thème `vent`), pinces asymétriques à grosses dents, bouche à double
couronne de dents. Pièces : corps, Head, Legs, Claws.

![crabe profil](previews/abyss_crab_head.png) ![crabe face](previews/abyss_crab_head_front.png)

| Baudroie des abysses squelette | Pose de test (rig) |
|---|---|
| ![baudroie](previews/abyss_angler.png) | ![baudroie pose](previews/abyss_angler_pose.png) |

Gueule géante en prognathie avec ~60 crocs vitreux, canne-appât articulée à esca lumineuse,
proie squelettique qui brille dans le ventre (thème `lure`). Pièces : corps, Head, Teeth, Fins.

![baudroie profil](previews/abyss_angler_head.png) ![baudroie face](previews/abyss_angler_head_front.png)

## Pack 2 bis — Enfers volcaniques

| Cerbère squelette | Pose de test (rig) |
|---|---|
| ![cerbere](previews/hell_cerberus.png) | ![cerbere pose](previews/hell_cerberus_pose.png) |

3 crânes de loup identiques à cornes annelées, colliers de fer à pointes reliés par des
chaînes brisées à l'anneau du poitrail, crinières de flammes, os calcinés fendus de lave,
cœur de braise, queue de serpent à tête de vipère (thème `fire`). Pièces : corps,
HeadA/HeadB/HeadC, Legs.

![cerbere profil](previews/hell_cerberus_head.png) ![cerbere face](previews/hell_cerberus_head_front.png)

## Bonus — Forêt maudite

| Loup-garou squelette | Pose de test (rig) |
|---|---|
| ![loup-garou](previews/forest_werewolf.png) | ![loup-garou pose](previews/forest_werewolf_pose.png) |

Crâne de loup (stop marqué, crête sagittale, arcades très larges, canines et carnassières),
os cendre envahis de mousse et de racines, crinière de piquants, fers brisés aux poignets,
flèches d'argent dans le dos, cœur en croissant de lune (thème `moon`). Pièces : corps, Head,
Arms, Legs.

![loup-garou profil](previews/forest_werewolf_head.png) ![loup-garou face](previews/forest_werewolf_head_front.png)

## Skill Claude : un monstre à partir d'une description

La skill `roblox-skeleton-monster` permet à Claude de générer un squelette démoniaque
animable à partir d'une simple phrase (« un raptor squelette vert toxique », « une hydre à
3 têtes dorée »…), avec le même style et les mêmes contrôles que le T-Rex et le dragon.

- Dans ce repo, elle est déjà active (`.claude/skills/roblox-skeleton-monster/`).
- Pour la partager : envoyer `dist/roblox-skeleton-monster.skill` (bouton « Save skill »
  dans Claude), ou copier le dossier dans `~/.claude/skills/` d'un autre ordinateur.
  Elle embarque sa boîte à outils et l'installe toute seule dans un projet vide
  (`scripts/setup_project.sh`, Python 3.13 requis pour `pip install bpy`).
- Elle contrôle elle-même son travail : `scripts/check_model.py` (pièces flottantes, budget de
  triangles, densité de détails de la tête) et `scripts/closeup.py … trio` (3 gros plans).
- Après une modification de `lib/` ou `build.py` : `bash tools/sync_skill_toolkit.sh`, puis
  ré-empaqueter.

## Structure

```
build.py           # point d'entrée : génère, exporte, rend les aperçus
lib/roblox.py      # primitives, palette, export FBX/OBJ, rendu
lib/creature.py    # rig, os, export animable, script d'effets
lib/CreatureEffects.server.lua  # modèle du script d'effets Roblox
models/*.py        # un fichier par modèle
exports/           # fichiers prêts pour Roblox
previews/          # aperçus PNG
```
