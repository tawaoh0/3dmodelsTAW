# Style guide — squelettes démoniaques Roblox

Ce guide vient d'itérations réelles avec l'utilisateur. Chaque règle a une raison : elle
corrige un rendu qui a été refusé.

## Ce qui a été validé

- **Toujours un squelette**, os par os : crâne, mâchoire articulée, vertèbres, côtes,
  bassin, os longs, phalanges. Pas de chair, pas de peau.
- **Formes nettes et lisibles** façon « boss Roblox » : os épais, articulations renflées
  (condyles), arêtes franches, gros volumes qui se lisent de loin.
- **Palette** : os ivoire (`#ddd0b8` / ombre `#a8977c`), dents plus claires (`#f4eee0`),
  cornes et griffes presque noires (`#231a20`), pointes de corne teintées de la lueur,
  disques intervertébraux sombres teintés de la lueur.
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

## Le crâne : la pièce la plus importante

Un bon crâne combine :

1. **Un profil qui ondule** (ligne du dessus vue de côté) : dôme crânien → arcade au-dessus
   des yeux → creux nasal → bosse des narines → bout de museau arrondi ou carré. Jamais une
   ligne droite qui finit en pointe. Concrètement : 7 à 9 sections `SKULL` dont le `z dessus`
   monte et descend.
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

## Silhouette générale

- Proportions « jeu » : tête un peu grosse (≈ 20 % de la longueur hors queue), pattes et
  griffes généreuses, queue longue qui s'affine.
- Colonne continue (vertèbres + disques), épines de dos plus hautes au milieu, pointes noires
  une épine sur deux (ou toutes, pour un dragon).
- Cage thoracique bombée, côtes ventrales (gastralia) pour les reptiles, sternum.
- Les pattes posent au sol (z = 0), la créature regarde vers -Y.

## Contrôle qualité (à vérifier sur les images à chaque itération)

- [ ] Rien ne flotte : yeux dans les orbites, cornes ancrées au crâne, griffes au bout des
      doigts (un objet `ico` créé avec `location` se tourne autour de `(0, 0, 0)`, pas de sa
      position monde).
- [ ] Pas de face noire ni de trou non voulu.
- [ ] Le crâne a un profil ondulé et ≥ 4 pièces en relief ; il ne ressemble à aucune
      créature déjà faite dans le projet.
- [ ] La pose de test montre la gueule ouverte, une patte avancée, etc., et chaque pièce
      suit son os sans se détacher.
- [ ] Les ailes (s'il y en a) sont visibles de face sur l'aperçu, pas par la tranche
      (ajuster `VIEW`), et la membrane s'étire dans la pose.
- [ ] Chaque mesh ≤ 20 000 triangles.
- [ ] La lueur est visible : yeux, cœur, au moins une rune, pointe de queue ou équivalent.
