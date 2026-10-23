# Style guide — squelettes démoniaques Roblox

Ce guide vient d'itérations réelles avec l'utilisateur. Chaque règle a une raison : elle
corrige un rendu qui a été refusé.

## Ce qui a été validé

- **Toujours un squelette**, os par os : crâne, mâchoire articulée, vertèbres, côtes,
  bassin, os longs, phalanges. Pas de chair, pas de peau.
- **Formes nettes et lisibles** façon « boss Roblox » : os épais, articulations renflées
  (condyles), arêtes franches, gros volumes qui se lisent de loin.
- **Palette de base** : os clairs, dents plus claires, cornes et griffes presque noires,
  pointes teintées de la lueur, disques intervertébraux sombres teintés de la lueur. La
  teinte exacte des os change d'une créature à l'autre (voir « Identité »).
- **Une teinte de lueur par créature** (rouge braise, violet, vert toxique, bleu glacé,
  or…) sur : yeux au fond des orbites, cœur de cristal dans la cage thoracique, runes
  (crâne, fémurs, avant-bras), gorge, pointe de queue.
- **Détails démoniaques** : grandes cornes annelées (`ridged_horn`), pointes noires sur les
  épines dorsales, griffes recourbées, ergots, cristaux.

## Ce qui a été rejeté (et pourquoi)

| Rejeté | Ce que l'utilisateur a dit | À faire à la place |
|---|---|---|
| Os fins, sombres, petits | « moche » | Os épais, ivoire, contrastés avec les cornes noires |
| Voxels | « moche… pas forcément voxel » | Géométrie lisse à arêtes nettes |
| Metaballs / corps en chair | « grosse boule de pâte à modeler » | Pièces osseuses distinctes, découpes booléennes |
| Crâne du dragon = crâne du T-Rex | « la tête est trop la même » | Un crâne conçu pour chaque créature |
| Crâne en coin droit et pointu | « manque de grand relief / de parties, toute droite et pointue » | Profil ondulé + grosses pièces en relief (voir ci-dessous) |
| T-Rex, dragon, raptor tous ivoire + cornes noires annelées balayées + cœur cristal | « ils se ressemblent trop tous entre eux » | Une identité complète par créature (section suivante) |
| Mégalodon et Léviathan v1 : têtes lisses, nageoires plates à 4 rayons, crête en bande continue | « pas assez détaillé, je ne veux pas voir le gros trait rouge tout le long » | `lib/marine.py` : nageoires riches (`fin`), orbites hérissées, écailles, cicatrices ; **jamais de longue bande de membrane d'une seule couleur** sur le corps, des éléments espacés à la place |
| Mégalodon et Léviathan v2 : crâne = un seul loft lisse couvert de petites pièces (300 pièces !) | « les corps sont bien mais les têtes sont trop simples » | Le nombre de pièces ne suffit pas : **le crâne doit être ajouré et fait d'os séparés** (voir « Crâne ajouré » ci-dessous) |
| Mégalodon v3 : mâchoires en fer à cheval plat (seau carré), rostre long et pointu, dents en lames fines | « mâchoire trop carrée, nez trop pointu, je veux beaucoup de grosses dents, pas des squelettes de dent » | Mâchoires en U arrondi (`jaw_arc`), plaques inclinées en bol, ligne de gueule courbe et profil bombé ; museau court, large et arrondi ; dents **pleines** `mr.tooth` (épaisses, dentelées), 3 rangées nombreuses dans une pièce `Teeth` |
| Salamandre v1 : crâne plat en bloc lisse avec fenêtres « lunettes », dents plates | (auto-correction) | Crâne plat = **cadre osseux** aux immenses fenêtres (œil suspendu dedans, barre au fond) ; dents coniques épaisses (`mr.tooth` largeur ≈ 0,42 × taille, épaisseur ≈ 0,36 × taille) |
| Démon taureau v1 : face longue et horizontale (crocodile), tête trop basse | (auto-correction) | Crâne bovin : face courte, très inclinée vers le bas (tangage ≈ 0,9 rad), tête au-dessus des épaules ; chanfrein ajouré |
| Phénix v1 : plumes fines vues de profil (« peigne »), petites flammes | (auto-correction) | Plumes larges (vexille ≈ 0,4) orientées dans le **plan de l'aile** (`normal = envergure × direction`), nombreuses et qui se chevauchent, grosses flammes ; bec inférieur en plaque inclinée et courbe |
| Golem v1 : poings entiers détachés des avant-bras, museau de singe | (auto-correction ; `check_model` ne voyait pas un groupe détaché) | `check_model` signale maintenant les **groupes détachés** ; relier mains et pieds par carpe / métacarpes ; crâne humain = face plate (`tip_length` court) |
| Cerbère v1 : 3 têtes grosses et collées, cous et colliers invisibles | (auto-correction) | Multi-têtes : cous longs et **écartés** (les crânes ne se touchent pas, lacet ±0,6 rad), têtes à l'échelle ~0,75, colliers posés sur la partie visible du cou ; chaînes : nombre de maillons calculé sur la longueur (pas de maillon qui flotte) |
| Loup-garou v1 : mâchoire du bas fermée et plate, oreilles géantes (effet lapin), arcades en planches droites | (auto-correction avant livraison) | Gueule entrouverte, bord de mâchoire courbe et bombé avec arête ; oreilles courtes inclinées vers l'arrière avec arête ; arcades lissées (`smooth_path`) |
| Baudroie v1 : crâne étroit, prémaxillaire et dentaire qui « flottent » devant, reliés par de simples tiges | « la mâchoire est trop séparée du crâne » | Le crâne doit être **aussi large que la gueule** et venir se poser sur la mâchoire du haut ; joues en plaques (`band` du bord de la mâchoire jusque sous le crâne, ajourées) ; grande plaque hyomandibulaire du flanc du crâne à la charnière ; tendons entre joue et dentaire. Jamais de vide entre crâne et mâchoires vu de profil |
| Museaux qui finissent sur une face plate ; crânes « reptile standard » | « les visages sont encore trop génériques, le nez se coupe net » | Bout de museau arrondi (`loft_profile` le fait par défaut) + crâne inspiré d'un **vrai animal** lié au thème |
| Hydre avec 3 crânes différents (royal, serpent, brute) | « je veux que les 3 têtes soient les mêmes, travaille-les plus » | Différencier les **créatures** entre elles, pas les têtes d'une même créature ; une seule tête très détaillée, répétée |

## Identité : chaque créature doit se distinguer sur 4 axes

Avant de modéliser, lister les créatures déjà présentes dans `models/` et remplir ce tableau
pour la nouvelle, en choisissant pour **chaque ligne** une valeur qu'aucune autre n'utilise :

| Axe | T-Rex | Dragon | Raptor | Tricératops | Hydre | Kraken | Mégalodon | Léviathan | Crabe titan | Baudroie | Loup-garou | Cerbère | Phénix | Golem de magma | Salamandre | Démon taureau | Idées libres |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Matière / couleur des os | ivoire `#ddd0b8` | ivoire froid `#dcd3c8` | vert-gris rongé `#c4c9a0` + cratères lumineux | givré blanc-bleuté `#d6e4ec` + grappes de cristaux | dorés `#e3c068` + pièces d'or incrustées | blanchis vert d'eau `#c9d8cf` + balanes et coraux rouges | ardoise sombre `#56616c`, dents claires | nacre lavande `#e7e1ef` | obsidienne `#3a3230` fissurée de lave, rebords rouille | brun tourbe `#7d6a55`, crocs vitreux | gris cendre `#a39a88` + mousse et racines | calcinés gris-noir `#4d4440` fendus de lave | ivoire cendré `#e2d3bd` qui vire au brûlé, bec noir | obsidienne `#2f2826` + veines de lave | ocre-ambre `#b4772c` tacheté de noir | rouge brûlé `#7a4038`, or | os calcinés noirs fissurés de lave, obsidienne, os dorés, os rouges sanglants, os translucides |
| Cornes / pointes | 2 grandes cornes annelées noires recourbées | couronne : 2 cornes plaquées + collerette palmée | **aucune corne** : éventails de piquants-plumes + crêtes jumelles dentelées | 3 cornes de **glace facettée** + collerette percée bordée d'éclats | **cornes de bélier en spirale** (bronze sombre) baguées d'or, 3 têtes identiques | pas de cornes : crochets noirs sur bras et massues, crête frontale | harpons rouillés + chaînes plantés dans le dos | couronne et crête de rayons, moustaches | pas de cornes : 3 cheminées hydrothermales soufrées + dents de carapace | canne-appât articulée + esca, épines sphénotiques | oreilles en lames noires + crinière de piquants, flèches d'argent | cornes annelées sur 3 têtes, colliers de fer à pointes + chaînes | crête de plumes d'os enflammées, ailes en plumes d'os | couronne et grappes d'orgues basaltiques | crête de flammes espacée, branchies de feu | cornes d'aurochs énormes cerclées d'or, anneau de nez, défenses |  ramures, lames, couronne de piques, épines dorsales en voile |
| Silhouette / posture | massif bipède, tête énorme | quadrupède ailé, cou en S dressé | petit bipède ramassé prêt à bondir | quadrupède trapu et bas, tête baissée pour charger, sabots | corps rampant, pattes de crocodile, 3 cous en éventail | manteau-cage dressé, 8 bras au sol, 2 tentacules levés | horizontale en nage, dorsale, queue en croissant | serpent, queue au sol, avant dressé | large et bas sur 8 longues pattes, pinces asymétriques | boule, tout en gueule, prognathe | bipède voûté, bras démesurés, pattes digitigrades | molosse quadrupède, 3 cous en éventail, queue de serpent | oiseau dressé sur ses serres, ailes levées | colosse voûté, avant-bras et poings énormes | rampante, pattes écartées, longue queue | bipède massif, bosse de garrot, sabots fendus | dressé sur 2 pattes, rampant au sol, enroulé, voûté, multi-têtes |
| Thème d'effets (`EFFECT_THEME`) | `fire` + cœur cristal | `fire` violet + cœur cristal | `acid` + poche d'acide, gouttes | `frost` + cœur en grappe de glace, stalactites | `gold` + idole de cristal, pièces en orbite, gemmes | `abyss` + photophores cyan partout, organe lumineux, bulles | `blood` rouge, branchies rougeoyantes | `souls` magenta, seconde mâchoire lumineuse | `vent` orange, cœur de lave vu par les fenêtres | `lure` citron vert, proie lumineuse dans le ventre | `moon` bleu lunaire, cœur en croissant | `fire` rouge-orange, crinières de flammes, cœur de braise | `phoenix` or, cœur-œuf de feu | `magma` (fumée + gouttes de lave), cœur de magma | `sulfur` rouge, glandes de poison lumineuses | `hellfire` cramoisi, fumée des naseaux | `souls`, lave, sang, ombre |

Le cœur lumineux, les runes et la pointe de queue prennent aussi la forme du thème : cristal
pour le feu, poche à bulles pour l'acide, flamme spectrale pour les âmes, stalactites pour le
givre, lingots / pièces pour l'or. Vérifier sur les aperçus côte à côte que la nouvelle
créature se reconnaît **en silhouette** (sans les couleurs) et **en couleur** (sans la forme).

## Le crâne : la pièce la plus importante

Un bon crâne combine :

0. **Un vrai animal comme modèle**, choisi pour aller avec le thème de la créature, puis
   exagéré. Ne pas partir d'un « crâne de reptile » générique. Exemples :
   - cornes de bélier → crâne de **bélier** : nez busqué (le dessus du profil s'arrondit
     vers le bas jusqu'au museau), front large et plat, orbites saillantes en manchon,
     tubercules sous les yeux, naseaux creusés dans le bout du museau ;
   - loup / chien des enfers → crâne de **loup** : stop marqué entre front et museau,
     crête sagittale haute, arcades zygomatiques très larges, canines énormes ;
   - serpent → crâne de **vipère** : tête en triangle plat, crochets repliés, écailles
     sus-orbitaires ;
   - oiseau / griffon → crâne de **rapace** : bec crochu, grandes orbites cerclées d'os.
   Écrire en commentaire au-dessus de `SKULL` l'animal choisi et ses 3-4 traits clés.

1. **Un profil qui ondule** (ligne du dessus vue de côté) : dôme crânien → arcade au-dessus
   des yeux → creux nasal → bosse des narines → bout de museau arrondi ou carré. Jamais une
   ligne droite qui finit en pointe. Concrètement : 7 à 9 sections `SKULL` dont le `z dessus`
   monte et descend.
   Le bout du museau ne doit **jamais** être une face plate : `loft_profile` ajoute un
   dôme arrondi par défaut (`tip="round"`, `droop` pour faire plonger le nez).
2. **De vraies ouvertures** découpées (`hole_x` + `cut`) : orbites, fenêtres temporales et
   antorbitales, narines. Inclinées (`rotate_obj` sur le cutter) pour un regard mauvais.
   L'œil lumineux est placé au fond de l'orbite.
3. **Au moins 4 pièces en relief** posées sur le crâne : arcades sourcilières en corniche
   (`blade` épais), pommettes en arche (`tube` épais + piques), bourrelets nasaux, bosses de
   narines, crête sagittale ou pariétale, collerette (piques + `membrane`), cornes de nez,
   ergot de menton, apophyses de mâchoire.
4. **Une signature unique par créature**, choisie selon l'animal :
   - T-Rex : crâne haut et massif, grandes fenêtres, cornes recourbées, rune frontale ;
   - dragon : dôme + corniches sourcilières + pommettes à piques + collerette palmée +
     deux longues cornes plaquées ;
   - raptor : crâne bas et long, museau effilé mais **bosselé**, crête nasale en scie,
     dents en dents de scie, grande griffe faucille au pied ;
   - tricératops : collerette osseuse géante percée de trous, trois cornes, bec ;
   - hydre / serpent : crânes plats en losange, crochets à venin, capuchon de côtes ;
   - loup / chien des enfers : museau court et haut, crocs énormes, crête dorsale de flammes.
5. **Deux paires de crocs plus longs** à l'avant et une rangée plus courte derrière.
   Les dents sont **pleines et épaisses** (`mr.tooth` : section lenticulaire, bords dentelés),
   jamais des lames fines (« squelettes de dent »). Gueule de prédateur : beaucoup de dents
   (requin : 3 rangées de 17/15/13 par mâchoire, rangées arrière couchées vers l'intérieur) ;
   si le budget déborde, les mettre dans une pièce `part="Teeth"`.
   Mâchoires : jamais un arc plat de hauteur constante (effet « seau carré ») ; ligne de gueule
   courbe, plaques inclinées, profil bombé, plus profondes vers la charnière. Museau : court
   et arrondi, pas une pointe.

6. **Crâne ajouré, fait d'os séparés** (leçon Mégalodon / Léviathan v2) : un gros loft lisse
   reste « trop simple » même couvert de 300 petites pièces. Le loft ne sert qu'à la **boîte
   crânienne** (courte) ; tout le reste est en os séparés avec du **vide visible** entre eux :
   - orbites et fenêtres **traversantes** (`hole_x` assez grand pour voir le fond à travers) ;
   - museau / rostre en **barres** (`tube`) qui convergent vers un nœud arrondi, reliées
     par des entretoises (requin : 3 barres rostrales ; murène : barre ethmoïde) ;
   - mâchoires en **plaques** (`a.band`, plus hautes à l'arrière) et non en tubes-boudins,
     avec arête externe, alvéoles, pores ; dentaires gauche/droit séparés en V (on voit à
     travers la gueule) ;
   - os de liaison visibles : hyomandibulaire / carré vers la charnière, piliers pré- et
     post-orbitaires, processus coronoïde, rétro-articulaire, opercule en éventail strié ;
   - grosses masses en relief : visières sus-orbitaires (`band` horizontale à piques),
     capsules nasales bombées, crête sus-occipitale haute et **percée**.
   Requin : chondrocrâne + rostre tripode + palatocarré/Meckel. Poisson osseux : boîte
   crânienne + crête + maxillaire/dentaire + opercule + 2e mâchoire pharyngienne.

## Densité de détails (demandé deux fois par l'utilisateur)

Une grande surface lisse et vide fait « pas fini ». Règle : aucune zone plate de plus
d'environ 1 stud² sans détail. Pour chaque grande surface, combiner au moins 3 de ces couches :

| Couche | Exemples | Outils |
|---|---|---|
| Bourrelets autour des ouvertures | anneau d'os autour des orbites et des fenêtres de collerette | `r.tube(..., closed=True)` sur un anneau de points |
| Nervures / arêtes | baleines d'éventail sur une collerette, arête nasale, crête de mâchoire | `r.tube` sur 2-3 points posés sur la surface |
| Bord découpé | nodules osseux alternés avec des éclats, festons, dents | `r.ico` aplatis + `claw` le long du bord |
| Excroissances du thème | cristaux de glace, piquants-plumes, cratères d'acide, flammèches | grappes de `claw`, `ico` lumineux |
| Lignes lumineuses | veines de givre, fissures de lave, runes | `r.tube` fin (rayon ≈ 0.03) en zigzag, couleur `glow` |
| Anneaux sur les cornes | fourreau d'os, bagues | anneaux placés avec `claw_point` |
| Bosses et rugosités | bosses sus-orbitaires, bosses de pommettes, nodules sur le museau | `r.ico(subdivisions=1)` aplatis |
| Éléments du milieu de vie | balanes, coraux (créatures marines), lianes et mousse (jungle), stalactites (glace), chaînes (gothique) | `barnacle`/`coral` dans `abyss_kraken.py`, `a.oriented` pour poser selon une normale |
| Ornements « éléments supplémentaires » | bagues d'or sur les cornes, diadème avec gemme sertie, boucles d'oreille, couronne de piques à gemmes, collier hérissé, barbe d'épines | `ring_around`, `spiral_points` / `claw_point` pour poser sur une corne, `crystal` + anneau de sertissage |

Repères chiffrés (ce que l'utilisateur a validé) : tête **≥ 150 pièces** pour une créature
du pack Abysses (mégalodon 299, léviathan 192), nageoire = **membrane + 8-14 rayons articulés +
épine d'attaque + radiaux + pointes lumineuses** (`marine.fin`), corps = au moins 3 rangées
d'éléments répétés le long de la colonne (épines dorsales, ligne latérale lumineuse, plaques
ventrales, côtes à piques…).

Quand l'utilisateur demande « plus de détails / d'éléments supplémentaires », ajouter une
couche d'**ornements** en plus des détails osseux : c'est ce qui a fait la différence sur
l'hydre (125 pièces par tête).

Repère : une tête réussie compte **plus de 100 pièces** (crâne + mâchoire + détails), le
tricératops final en a 131 pour 6 000 triangles. `check_model.py` prévient sous 45.

## Silhouette générale

- Proportions « jeu » : tête un peu grosse (≈ 20 % de la longueur hors queue), pattes et
  griffes généreuses, queue longue qui s'affine.
- Colonne continue (vertèbres + disques), épines de dos plus hautes au milieu, pointes noires
  une épine sur deux (ou toutes, pour un dragon).
- Cage thoracique bombée, côtes ventrales (gastralia) pour les reptiles, sternum.
- Les pattes posent au sol (z = 0), la créature regarde vers -Y.

## Contrôle qualité (à vérifier sur les images à chaque itération)

- [ ] `check_model.py` affiche « Contrôle OK » (rien ne flotte, budget respecté).
- [ ] **Dents** pleines, épaisses, dentelées (`mr.tooth`), couleur `tooth` distincte des os,
      nombreuses et de tailles variées, dans des gencives / alvéoles. Si elles ressemblent à
      des piques ou à des lames d'os fines → à refaire (« pas des dents en os »).
- [ ] Sur les 3 gros plans : les détails sont sur la face visible des plaques, rien n'est
      masqué par l'angle de vue, aucune grande surface n'est vide.
- [ ] Pas de face noire ni de trou non voulu.
- [ ] Le museau se termine en bout arrondi (pas de face plate) et le crâne évoque l'animal
      choisi comme modèle.
- [ ] Le crâne a un profil ondulé et ≥ 4 pièces en relief ; il ne ressemble à aucune
      créature déjà faite dans le projet.
- [ ] Le tableau « Identité » est rempli : couleur des os, cornes, posture et thème
      d'effets différents de toutes les créatures existantes.
- [ ] La pose de test montre la gueule ouverte, une patte avancée, etc., et chaque pièce
      suit son os sans se détacher.
- [ ] Les ailes (s'il y en a) sont visibles de face sur l'aperçu, pas par la tranche
      (ajuster `VIEW`), et la membrane s'étire dans la pose.
- [ ] Chaque mesh ≤ 20 000 triangles.
- [ ] La lueur est visible : yeux, cœur, au moins une rune, pointe de queue ou équivalent.
