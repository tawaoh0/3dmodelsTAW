---
name: roblox-skeleton-monster
description: Génère, à partir d'une simple description de monstre, un squelette démoniaque 3D animable pour Roblox (FBX avec armature + parties lumineuses + script d'effets Luau), modélisé os par os en Python avec Blender headless. Utilise cette skill dès que l'utilisateur demande une créature, un monstre, un boss, un dinosaure, un dragon, une bête mythique, un mort-vivant ou un « squelette » pour Roblox ou un jeu, même s'il ne dit ni « Blender » ni « squelette » (ex. « fais-moi un raptor vert toxique », « un boss araignée géante », « un kraken mort-vivant pour mon jeu »).
---

# Monstres squelettes démoniaques pour Roblox

Transforme une description courte (« un raptor squelette vert toxique », « hydre à 3 têtes
dorée ») en créature prête pour Roblox Studio :

- `exports/<nom>/<nom>.fbx` : armature + meshes skinnés (corps, éventuelles pièces en plus,
  `_Glow` pour tout ce qui brille) ;
- `exports/<nom>/<nom>_effects.server.lua` : script qui passe le `_Glow` en Neon, ajoute une
  lumière pulsante et des flammes sur les os `FX_*` ;
- `previews/<nom>.png` (repos) et `previews/<nom>_pose.png` (pose de test du rig).

Le style a été validé par l'utilisateur après plusieurs essais ratés. Lire
`references/style-guide.md` avant de modéliser : il résume ce qui a plu et ce qui a été rejeté
(formes molles « pâte à modeler », voxels, têtes droites et pointues, têtes qui se ressemblent).

## 1. Préparer le projet

Le projet doit contenir la boîte à outils (`build.py`, `lib/roblox.py`, `lib/creature.py`,
`lib/anatomy.py`, `lib/CreatureEffects.server.lua`). Si `lib/anatomy.py` est absent, ou si
`bpy` n'est pas installé :

```bash
bash <chemin-de-cette-skill>/scripts/setup_project.sh <dossier-du-projet>
```

Le script copie `toolkit/` (sans écraser l'existant), crée `.venv-blender` et installe `bpy`
(le module Python de Blender, aucun Blender graphique requis). Ensuite on lance tout avec
`<python> build.py <nom>`, où `<python>` est celui du venv ou `blender -b -P build.py -- <nom>`.

## 2. Comprendre la demande

Extraire de la description : l'animal / la créature de base, la couleur de lueur, les traits
marquants (ailes, plusieurs têtes, cornes, carapace…), la taille approximative. Compléter le
reste avec les conventions du style guide plutôt que de poser des questions. Ne demander que
si un choix change vraiment le modèle (ex. « araignée » : 8 pattes réalistes ou boss démon
debout ?). Une question groupée maximum, avec une proposition par défaut.

Regarder les créatures déjà présentes dans `models/` (et leurs aperçus) : la nouvelle doit
s'en distinguer sur **4 axes** — couleur/matière des os, type de cornes et pointes,
silhouette/posture, thème d'effets. Remplir le tableau « Identité » du style guide.

Annoncer en 4-5 lignes le plan : silhouette et posture, signature du crâne, matière des os,
cornes, thème d'effets, pièces Roblox.

## 3. Choisir un plan de corps et écrire le modèle

Lire `references/body-plans.md` : plans types (bipède théropode, quadrupède, ailé, serpent,
multi-têtes, arthropode, humanoïde) avec la liste d'os du rig et les ordres de grandeur.
Lire `references/anatomy-api.md` pour les fonctions disponibles et leurs pièges.

Créer `models/skeleton_<nom>.py` en partant de l'exemple le plus proche dans
`toolkit/models/` (`skeleton_trex.py` bipède massif, `skeleton_raptor.py` bipède agile thème
acide, `skeleton_dragon.py` quadrupède ailé multi-pièces).
S'en inspirer pour la structure (rig → crâne → colonne → cage → membres), mais **concevoir
un crâne neuf** : c'est la partie que l'utilisateur regarde en premier, et deux créatures au
crâne semblable ont été rejetées.

Le module définit :
- `COLORS` : `bone`, `bone_shade`, `tooth`, `horn`, `horn_tip`, `disc`, éventuellement
  `membrane`, et obligatoirement `glow` + `glow_hot` (utilisées par le script d'effets) ;
- `TEST_POSE` : rotations (degrés) d'os qui montrent que le rig marche (gueule ouverte,
  cou levé, une patte avancée, queue fléchie, aile repliée) ;
- `EFFECT_THEME` : `fire`, `acid`, `souls`, `frost` ou `gold` (particules du script Roblox) ;
- `VIEW` (optionnel) : direction de caméra des aperçus, ex. `(0.4, -1, 0.8)` pour voir des ailes ;
- `build(pal)` qui renvoie le `Rig`.

## 4. Générer et contrôler (boucle obligatoire)

```bash
<python> build.py skeleton_<nom>
```

La sortie console donne, pour chaque mesh, le nombre de triangles (`OK` / `TROP DE TRIANGLES`)
et le nombre d'os. Puis **regarder les images** avec l'outil de lecture d'image :
`previews/skeleton_<nom>.png`, `previews/skeleton_<nom>_pose.png`, et un gros plan de la tête :

```bash
<python> <chemin-de-cette-skill>/scripts/closeup.py skeleton_<nom> Head <sortie.png> 1 -0.6 0.35
```

(`Head` = nom de la pièce ; `Body` pour le corps principal ; les 3 nombres = direction caméra.)

Passer la checklist de `references/style-guide.md` (section « Contrôle qualité »). Les défauts
typiques : pièce flottante hors du crâne (rotation autour du mauvais pivot), faces noires,
os qui ne suivent pas leur articulation dans la pose, aile vue par la tranche, tête trop
simple. Corriger et regénérer jusqu'à ce que tout passe. Compter 3 à 6 itérations, c'est normal.

Chaque mesh doit rester ≤ 20 000 triangles (limite Roblox par MeshPart). Sinon : alléger
(voir anatomy-api.md, « Budget ») ou répartir sur plusieurs pièces avec `part="Head"`,
`part="Wings"`, etc.

## 5. Livrer

1. Ajouter la créature au `README.md` (aperçu repos + pose) si le projet en a un.
2. Committer code + exports + aperçus si le projet est un dépôt git (et pousser si c'est
   la pratique du projet).
3. Montrer les aperçus à l'utilisateur (outil d'envoi de fichiers s'il existe), puis résumer
   en quelques puces : ce qu'il y a sur la créature (surtout le crâne), triangles par pièce,
   nombre d'os, comment l'importer (Import 3D, *File Dimensions : Studs*, glisser le script
   d'effets dans le Model). Dire clairement que l'import Roblox Studio n'a pas été testé.
4. Demander validation avant d'enchaîner sur une autre créature : l'utilisateur aime
   avancer une créature à la fois.
