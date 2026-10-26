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

## Pack 3 — Enfers volcaniques

| Cerbère squelette | Pose de test (rig) |
|---|---|
| ![cerbere](previews/hell_cerberus.png) | ![cerbere pose](previews/hell_cerberus_pose.png) |

3 crânes de loup identiques à cornes annelées, colliers de fer à pointes reliés par des
chaînes brisées à l'anneau du poitrail, crinières de flammes, os calcinés fendus de lave,
cœur de braise, queue de serpent à tête de vipère (thème `fire`). Pièces : corps,
HeadA/HeadB/HeadC, Legs.

![cerbere profil](previews/hell_cerberus_head.png) ![cerbere face](previews/hell_cerberus_head_front.png)

| Phénix squelette | Pose de test (rig) |
|---|---|
| ![phenix](previews/hell_phoenix.png) | ![phenix pose](previews/hell_phoenix_pose.png) |

Crâne d'aigle à anneaux sclérotiques, bec crochu à dents tomiales, crête de plumes d'os,
ailes déployées en plumes d'os aux pointes de feu, éventail de queue et traînes, cœur-œuf de
feu (thème `phoenix`). Pièces : corps, Head, Wings.

![phenix profil](previews/hell_phoenix_head.png) ![phenix face](previews/hell_phoenix_head_front.png)

| Golem de magma squelette | Pose de test (rig) |
|---|---|
| ![golem](previews/hell_golem.png) | ![golem pose](previews/hell_golem_pose.png) |

Crâne de géant au bourrelet massif, couronne d'orgues basaltiques, larmes et bave de lave,
os d'obsidienne fendus de veines de lave, cœur de magma, poings hérissés de basalte (thème
`magma`). Pièces : corps, Head, Arms, Legs.

![golem profil](previews/hell_golem_head.png) ![golem face](previews/hell_golem_head_front.png)

| Salamandre géante squelette | Pose de test (rig) |
|---|---|
| ![salamandre](previews/hell_salamander.png) | ![salamandre pose](previews/hell_salamander_pose.png) |

Crâne plat de salamandre géante en cadre ajouré (yeux suspendus dans les fenêtres), gueule en
U à dents coniques + rangée au palais, branchies de feu, glandes de poison lumineuses, os
ocre tachetés de noir, crête de flammes espacée jusqu'au bout de la queue (thème `sulfur`).
Pièces : corps, Head, Tail, Legs.

![salamandre profil](previews/hell_salamander_head.png) ![salamandre face](previews/hell_salamander_head_front.png)

| Démon taureau squelette | Pose de test (rig) |
|---|---|
| ![taureau](previews/hell_bull.png) | ![taureau pose](previews/hell_bull_pose.png) |

Crâne d'aurochs (chignon, orbites en manchon, chanfrein ajouré), cornes énormes cerclées
d'or, anneau d'or dans le nez, défenses, bosse de garrot enflammée, chaînes brisées, sabots
fendus, queue à touffe de feu (thème `hellfire`). Pièces : corps, Head, Arms, Legs.

![taureau profil](previews/hell_bull_head.png) ![taureau face](previews/hell_bull_head_front.png)

## Pack 4 — Royaume de glace éternelle

| Mammouth squelette | Pose de test (rig) |
|---|---|
| ![mammouth](previews/ice_mammoth.png) | ![mammouth pose](previews/ice_mammoth_pose.png) |

Crâne en dôme alvéolé (sinus traversants), grande ouverture nasale, fourreaux de défenses,
molaires en lamelles, défenses spirales en glace couvertes de givre et de stalactites,
trompe en anneaux d'os autour d'un cœur lumineux, bosse de garrot givrée, cœur-aurore
(thème `aurora`). Pièces : corps, Head, Tusks, Legs.

![mammouth profil](previews/ice_mammoth_head.png) ![mammouth face](previews/ice_mammoth_head_front.png)

| Tigre à dents de sabre squelette | Pose de test (rig) |
|---|---|
| ![tigre](previews/ice_sabertooth.png) | ![tigre pose](previews/ice_sabertooth_pose.png) |

Vrai tigre à quatre pattes : grand crâne au long museau, sabres démesurés aplatis et
dentelés, grande gueule ouverte avec bride mentonnière, os gris argent rayés de glace bleu
nuit, longue queue, cœur de glace (thème `blizzard`). Pièces : corps, Head, Legs.

![tigre profil](previews/ice_sabertooth_head.png) ![tigre face](previews/ice_sabertooth_head_front.png)

| Wendigo squelette | Pose de test (rig) |
|---|---|
| ![wendigo](previews/ice_wendigo.png) | ![wendigo pose](previews/ice_wendigo_pose.png) |

Crâne de cerf (fossettes lacrymales, longs os nasaux) aux grands bois givrés, gueule pleine de
crocs fins, corps immense et décharné, côte brisée, doigts interminables, sabots fendus, cœur
gelé (thème `wraith`). Pièces : corps, Head, Arms, Legs.

![wendigo profil](previews/ice_wendigo_head.png) ![wendigo face](previews/ice_wendigo_head_front.png)

| Ours polaire titan squelette | Pose de test (rig) |
|---|---|
| ![ours](previews/ice_bear.png) | ![ours pose](previews/ice_bear_pose.png) |

Crâne d'ours large et massif (front plat, museau court et carré, petits yeux, molaires
broyeuses), tête portée bas sous une bosse de garrot, armure de plaques de glacier, crinière
de pics de glace, pattes plantigrades à griffes de glace géantes, cœur de nuit polaire
(thème `polar`). Pièces : corps, Head, Legs.

![ours profil](previews/ice_bear_head.png) ![ours face](previews/ice_bear_head_front.png)

| Dragon de givre squelette (wyverne) | Pose de test (rig) |
|---|---|
| ![dragon de givre](previews/ice_dragon.png) | ![dragon de givre pose](previews/ice_dragon_pose.png) |

Crâne de varan à couronne de cornes de cristal, dents recourbées dentelées, buste massif
(grande cage, énorme bréchet, plastron de cristal), ailes de cristal incrustées d'éclats,
dressé sur ses pattes arrière, massue de cristaux au bout de la queue (thème `crystal`).
Pièces : corps, Head, Wings, Tail.

![dragon de givre profil](previews/ice_dragon_head.png) ![dragon de givre face](previews/ice_dragon_head_front.png)

## Pack 5 — Ruines de la jungle maudite

| Gorille titan squelette | Pose de test (rig) |
|---|---|
| ![gorille](previews/jungle_gorilla.png) | ![gorille pose](previews/jungle_gorilla_pose.png) |

Crâne de gorille (énorme crête sagittale, bourrelet sus-orbitaire massif, face courte,
canines géantes), glyphes mayas lumineux incrustés, ornements d'oreille en jade, lianes et
mousse, marche sur les phalanges avec des poings énormes cerclés de pierre gravée, idole de
jade comme cœur (thème `jungle`). Pièces : corps, Head, Arms, Legs.

![gorille profil](previews/jungle_gorilla_head.png) ![gorille face](previews/jungle_gorilla_head_front.png)

| Serpent à plumes (Quetzalcoatl) squelette | Pose de test (rig) |
|---|---|
| ![serpent à plumes](previews/jungle_serpent.png) | ![serpent pose](previews/jungle_serpent_pose.png) |

Crâne de vipère (crochets dressés pour la frappe, gouttes de venin, fossettes thermiques,
écailles sus-oculaires à cornes), collerette de plumes d'os en éventail, touffes de plumes
espacées, bagues d'or et glyphes mayas, enroulé au sol, crécelle de pierre (thème `quetzal`).
Pièces : corps, Tail, Head.

![serpent profil](previews/jungle_serpent_head.png) ![serpent face](previews/jungle_serpent_head_front.png)

| Jaguar squelette | Pose de test (rig) |
|---|---|
| ![jaguar](previews/jungle_jaguar.png) | ![jaguar pose](previews/jungle_jaguar_pose.png) |

Jaguar noir : crâne rond et court aux arcades énormes, canines épaisses, os noirs tachetés de
rosettes-runes dorées, lames d'obsidienne sur la colonne, collier rituel de jade et d'or,
plumes de jade, cœur-soleil d'or, posture de traque (thème `ruins`). Pièces : corps, Head, Legs.

![jaguar profil](previews/jungle_jaguar_head.png) ![jaguar face](previews/jungle_jaguar_head_front.png)

| Mante religieuse géante squelette | Pose de test (rig) |
|---|---|
| ![mante](previews/jungle_mantis.png) | ![mante pose](previews/jungle_mantis_pose.png) |

Mante-orchidée : tête triangulaire aux yeux composés lumineux cerclés d'or, longues antennes
annelées, pattes ravisseuses à épines et griffes noires, élytres-pétales roses, abdomen en
anneaux, lianes et mousse sur les pattes (thème `orchid`). Pièces : corps, Head, Arms, Legs, Wings.

![mante profil](previews/jungle_mantis_head.png) ![mante face](previews/jungle_mantis_head_front.png)

| Crocodile ancien squelette | Pose de test (rig) |
|---|---|
| ![crocodile](previews/jungle_crocodile.png) | ![crocodile pose](previews/jungle_crocodile_pose.png) |

Deinosuchus de 11 studs : crâne plat ajouré (fenêtres, fosses du museau, orbites sur le dessus),
mandibule courbe à fenêtre et symphyse arrondie, dents coniques entrecroisées, dos en
ostéodermes de pierre gravés de glyphes lumineux, double crête caudale, gastralia, cœur de jade,
lianes et mousse (thème `swamp`). Pièces : corps, Head, Tail, Legs.

![crocodile profil](previews/jungle_crocodile_head.png) ![crocodile face](previews/jungle_crocodile_head_front.png)

## Pack 6 — Cimetière gothique / nécromancie

| Liche dragon squelette | Pose de test (rig) |
|---|---|
| ![liche dragon](previews/grave_lich_dragon.png) | ![liche dragon pose](previews/grave_lich_dragon_pose.png) |

Wyverne-liche au crâne de markhor : cornes noires en tire-bouchon, couronne de fer à bougies
coulantes, orbites lumineuses violettes, ailes en lambeaux tombant en cape, cercueil-phylactère
à gemme d'âme enchaîné au poitrail, bougies sur le dos, lanterne d'âme pendue au bout de
la queue (thème `necro`). Pièces : corps, Head, Wings, Tail.

![liche profil](previews/grave_lich_dragon_head.png) ![liche face](previews/grave_lich_dragon_head_front.png)

| Cheval cauchemar squelette | Pose de test (rig) |
|---|---|
| ![cheval cauchemar](previews/grave_horse.png) | ![cheval pose](previews/grave_horse_pose.png) |

Crâne de cheval (orbites cerclées très en arrière, encoche naso-incisive, crête faciale,
mandibule à angle arrondi, crocs à la place des incisives), crinière et queue de flammes
spectrales vert poison, sabots en feu ferrés, fers brisés aux paturons, cercueil-selle sanglé
de chaînes avec bougies (thème `nightmare`). Pièces : corps, Head, Legs.

![cheval profil](previews/grave_horse_head.png) ![cheval face](previews/grave_horse_head_front.png)

| Corbeau géant squelette | Pose de test (rig) |
|---|---|
| ![corbeau](previews/grave_raven.png) | ![corbeau pose](previews/grave_raven_pose.png) |

Grand corbeau voûté : bec crochu noir à dents en scie, anneaux sclérotiques autour des yeux
rouges, huppe de plumes, carène et côtes à processus uncinés, ailes repliées, perché sur une
tombe brisée aux runes rouges avec bougie, anneau de fer brisé à la patte (thème `ravens`).
Pièces : corps, Head, Wings.

![corbeau profil](previews/grave_raven_head.png) ![corbeau face](previews/grave_raven_head_front.png)

| Chauve-souris vampire squelette | Pose de test (rig) |
|---|---|
| ![chauve-souris](previews/grave_bat.png) | ![chauve-souris pose](previews/grave_bat_pose.png) |

Vampire commun : crâne rond à crête sagittale, feuille nasale, incisives en lames de rasoir et
canines énormes gouttant de sang, oreilles immenses à armature d'os, marche sur les poignets
ailes repliées en cape, collier de fer clouté à camée, chaînes brisées aux poignets (thème
`vampire`). Pièces : corps, Head, Wings.

![chauve-souris profil](previews/grave_bat_head.png) ![chauve-souris face](previews/grave_bat_head_front.png)

| Araignée tisseuse d'âmes squelette | Pose de test (rig) |
|---|---|
| ![araignée](previews/grave_spider.png) | ![araignée pose](previews/grave_spider_pose.png) |

Mygale : carapace ajourée à fovéa et sillons, 8 yeux lumineux cerclés, chélicères à dents et
crochets noirs (venin), pédipalpes, 8 pattes coudées épineuses, abdomen en cage d'os où
flottent des âmes prisonnières, toile d'âmes lumineuse sur piquets d'os, cocon-cercueil pendu
aux filières (thème `soulweb`). Pièces : corps, Head, Legs.

![araignée profil](previews/grave_spider_head.png) ![araignée face](previews/grave_spider_head_front.png)

## Pack 7 — Mythologie

| Minotaure squelette | Pose de test (rig) |
|---|---|
| ![minotaure](previews/myth_minotaur.png) | ![minotaure pose](previews/myth_minotaur_pose.png) |

Crâne de buffle du Cap (bouclier frontal de corne, cornes tombantes en crochet à pointes de
bronze), os de marbre, debout poitrail bombé et jambes écartées, labrys minoenne (lames en
croissant à tranchant lumineux, douille, manche gainé) posée sur l'épaule et tenue à pleine
main (doigts enroulés autour du manche), épaulière à plaques, large ceinture de bronze à
méandres et boucle-labyrinthe lumineuse, jupe de ptéryges en deux rangs rivetés (thème `labyrinth`). Pièces : corps, Head, Arms, Legs.

![minotaure profil](previews/myth_minotaur_head.png) ![minotaure face](previews/myth_minotaur_head_front.png)

| Fenrir squelette | Pose de test (rig) |
|---|---|
| ![fenrir](previews/myth_fenrir.png) | ![fenrir pose](previews/myth_fenrir_pose.png) |

Loup colossal de 14 studs : crâne massif de loup (crête sagittale, arcades très écartées, os
nasaux, foramens, épines jugales, canines et carnassières énormes), collerette de piques d'os
derrière le crâne, gueule béante à mandibule courbe et fenêtrée, flammes de givre aux yeux, os
gravés de runes lumineuses (front, joues, côtes, omoplates, pattes), fraise et crinière de
piques, piques aux épaules, coudes et poignets, Gleipnir brisé : fragments de ruban lumineux
déchirés qui pendent du collier runique et des entraves (thème `ragnarok`). Pièces : corps, Head, Legs, Tail.

![fenrir profil](previews/myth_fenrir_head.png) ![fenrir face](previews/myth_fenrir_head_front.png)

| Anubis squelette | Pose de test (rig) |
|---|---|
| ![anubis](previews/myth_anubis.png) | ![anubis pose](previews/myth_anubis_pose.png) |

Dieu guerrier massif (épaules très larges, épaulières à plaques or et lapis, os épais) au
crâne de chacal fin, aux oreilles immenses de lapis-lazuli bordées d'or, os d'obsidienne,
coiffe némès rayée or / lapis (pans jusqu'aux épaules, rabat arrière), diadème à
uraeus, barbe postiche tressée, arcades d'or, museau clouté, plaques de joue incrustées,
trait de khôl d'or, collier ousekh de perles or / lapis / turquoise, pagne
de lin plissé à tablier d'hiéroglyphes lumineux, bracelets, sceptre ouas tenu à pleine main et
planté au sol, ankh pendue à l'autre main (thème `duat`). Pièces : corps, Head, Arms, Legs.

![anubis profil](previews/myth_anubis_head.png) ![anubis face](previews/myth_anubis_head_front.png)

| Kitsune à neuf queues squelette | Pose de test (rig) |
|---|---|
| ![kitsune](previews/myth_kitsune.png) | ![kitsune pose](previews/myth_kitsune_pose.png) |

Renard de porcelaine blanche au crâne peint de marques vermillon comme un masque de kitsune,
oreilles triangulaires laquées, neuf queues d'os à « fourrure » de lames déployées en éventail,
chacune terminée par un kitsunebi (feu de renard), perle hoshi no tama au bout de la queue
centrale, shimenawa tressée au cou avec papiers shide et clochette (thème `foxfire`).
Pièces : corps, Head, Legs, Tails.

![kitsune profil](previews/myth_kitsune_head.png) ![kitsune face](previews/myth_kitsune_head_front.png)

| Basilic squelette | Pose de test (rig) |
|---|---|
| ![basilic](previews/myth_basilisk.png) | ![basilic pose](previews/myth_basilisk_pose.png) |

Roi des serpents médiéval : tête de coq couronnée (couronne d'or à pointes d'os, crête rouge,
barbillons), bec crochu à crochets venimeux et dents en scie, regard pétrifiant vert-jaune
cerclé de plaquettes, camail et ailes vestigiales de plumes d'os, corps de vipère dressé en S
sur deux pattes de coq à ergots, côtes et écailles ventrales, bout de queue pétrifié fissuré
de lueurs (thème `petrify`). Pièces : corps, Head, Tail, Legs.

![basilic profil](previews/myth_basilisk_head.png) ![basilic face](previews/myth_basilisk_head_front.png)

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
