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
Lire `references/anatomy-api.md` pour les fonctions disponibles et **sa section « Pièges »**,
qui liste toutes les erreurs déjà commises : les éviter dès le premier jet fait gagner
plusieurs itérations.

Créer `models/skeleton_<nom>.py` en partant de l'exemple le plus proche dans
`toolkit/models/` (`skeleton_trex.py` bipède massif, `skeleton_raptor.py` bipède agile thème
acide, `skeleton_dragon.py` quadrupède ailé multi-pièces, `skeleton_triceratops.py` quadrupède
trapu à collerette percée et très détaillée, `skeleton_hydra.py` rampant à 3 têtes dans des
repères locaux, multi-pièces).
S'en inspirer pour la structure (rig → crâne → détails de tête → colonne → cage → membres),
mais **concevoir un crâne neuf** : c'est la partie que l'utilisateur regarde en premier.

Viser dès le premier jet la **densité de détails** décrite dans le style guide : l'utilisateur
a demandé à deux reprises « plus de détails » sur la tête et la collerette. Une fonction
`build_<zone>_details(rig)` séparée par grande surface (crâne, collerette, crête, ailes) aide
à ne rien oublier.

Le module définit :
- `COLORS` : `bone`, `bone_shade`, `tooth`, `horn`, `horn_tip`, `disc`, éventuellement
  `membrane` ou une couleur de thème (`ice`, `quill`…), et obligatoirement `glow` + `glow_hot`
  (utilisées par le script d'effets) ;
- `TEST_POSE` : rotations (degrés) d'os qui montrent que le rig marche (gueule ouverte,
  cou levé, une patte avancée, queue fléchie, aile repliée) ;
- `EFFECT_THEME` : `fire`, `acid`, `souls`, `frost` ou `gold` (particules du script Roblox) ;
- `VIEW` : direction de caméra des aperçus, choisie pour qu'aucune grande pièce n'en cache
  une autre (ailes vues de face, collerette pas masquée par les cornes) ;
- `build(pal)` qui renvoie le `Rig`.

## 4. Contrôler (boucle obligatoire)

**a. Contrôle automatique d'abord** (rapide, sans rendu) :

```bash
<python> <chemin-de-cette-skill>/scripts/check_model.py skeleton_<nom>
```

Il signale les pièces qui flottent (avec leur position), les os ou couleurs inconnus, le
budget de triangles par pièce Roblox et une tête trop peu détaillée. Corriger jusqu'à
« Contrôle OK ». Les « info » sur des lueurs suspendues (œil au centre d'une orbite, éclats
autour du cœur) sont acceptables si c'est voulu.

**b. Rendus**, puis **regarder chaque image** avec l'outil de lecture d'image :

```bash
<python> build.py skeleton_<nom>
<python> <chemin-de-cette-skill>/scripts/closeup.py skeleton_<nom> Head <prefixe> trio
```

`build.py` produit `previews/skeleton_<nom>.png` et `_pose.png`. `closeup.py … trio` produit
3 gros plans de la tête (`<prefixe>_profil.png`, `_face.png`, `_dessus.png`) en un seul
passage. Le contrôle automatique ne voit pas tout : un détail posé sur la **mauvaise face**
d'une plaque (derrière la collerette au lieu de devant), une pièce masquée par l'angle de vue,
un crâne trop simple. Les 3 angles servent à ça.

**c. Checklist** de `references/style-guide.md` (« Contrôle qualité »), puis corriger et
recommencer. Avec les pièges évités dès le départ, 2 à 3 itérations suffisent en général.

Chaque mesh doit rester ≤ 20 000 triangles (limite Roblox par MeshPart). Sinon : alléger
(voir anatomy-api.md, « Budget ») ou répartir sur plusieurs pièces avec `part="Head"`,
`part="Wings"`, etc.

## 5. Livrer

1. Ajouter la créature au `README.md` (aperçu repos + pose) si le projet en a un.
2. Committer code + exports + aperçus si le projet est un dépôt git (et pousser si c'est
   la pratique du projet).
3. Montrer les aperçus à l'utilisateur (outil d'envoi de fichiers s'il existe) : repos, pose,
   et 2 gros plans de la tête (profil et face) copiés dans `previews/`. Puis résumer
   en quelques puces : ce qu'il y a sur la créature (surtout le crâne), triangles par pièce,
   nombre d'os, comment l'importer (Import 3D, *File Dimensions : Studs*, glisser le script
   d'effets dans le Model). Dire clairement que l'import Roblox Studio n'a pas été testé.
4. Demander validation avant d'enchaîner sur une autre créature : l'utilisateur aime
   avancer une créature à la fois.
