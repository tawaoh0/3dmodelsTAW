"""Minotaure squelette (≈ 7,5 studs de haut, bipède voûté) — créature animable.
Pack « Mythologie », créature 1 (mythe grec).

Animal modèle : le **buffle du Cap** — énorme **bouclier frontal** (les bases des cornes
soudées en casque sur le front, sillon au milieu), cornes qui tombent sur les côtés puis
remontent en crochet vers l'avant ; long chanfrein, mufle large. Très différent du démon
taureau (aurochs, cornes cerclées d'or, anneau au nez, feu).

Identité : os de marbre veiné ; **casque de cornes** de buffle à pointes de bronze ; voûté et
massif, épaules énormes ; **armure grecque en bronze** (épaulière, brassards à méandres,
ceinture et jupe de lanières de cuir) ; **labrys** (double hache) en main droite ; **fil
d'Ariane** rouge lumineux enroulé au bras gauche et traînant au sol ; médaillon-labyrinthe
lumineux sur le cœur ; thème d'effets « labyrinth » (poussière d'or + éclats de pierre).

4 pièces Roblox : corps, Head, Arms, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, Tail1-2, UpperArm/ForeArm/Hand_{L,R},
Thigh/Shin/Foot_{L,R}, + FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#e6e1d6",
    "bone_shade": "#8b8579",
    "tooth": "#fbf7ec",
    "horn": "#17140f",
    "disc": "#5b554b",
    "gold": "#b8783a",
    "leather": "#5a3a24",
    "gum": "#6a2a2a",
    "ink": "#0c0a08",
    "glow": "#ffc54a",
    "glow_hot": "#fff2c4",
    "glow_thread": "#ff2a45",
}

EFFECT_THEME = "labyrinth"

TEST_POSE = {
    "Jaw": (20, 0, 0),
    "Head": (15, 0, 0),
    "UpperArm_L": (-60, 0, 0),
    "ForeArm_L": (-45, 0, 0),
    "Thigh_R": (30, 0, 0),
    "Tail1": (0, 0, 30),
}

VIEW = (0.9, -1.0, 0.3)

SPINE = a.smooth_path([(0, 0.35, 3.6), (0, 0.15, 4.5), (0, -0.3, 5.25), (0, -0.85, 5.7)], 16)
TAIL = a.smooth_path([(0, 0.6, 3.55), (0, 1.15, 3.1), (0.2, 1.45, 2.4), (0.05, 1.55, 1.7)], 12)
# Crâne d'aurochs en repère canonique : chignon (sommet entre les cornes) à l'origine,
# mufle vers -Y. (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(0.0, 0.55, 0.6, 0.45, 0.12, -0.55), (-0.4, 0.6, 0.66, 0.5, 0.15, -0.6),
         (-0.8, 0.45, 0.52, 0.42, 0.08, -0.62), (-1.25, 0.34, 0.4, 0.35, 0.0, -0.6),
         (-1.65, 0.33, 0.4, 0.36, -0.06, -0.6), (-1.95, 0.4, 0.46, 0.42, -0.1, -0.6)]
EYE = (-0.55, -0.12)
HINGE = (0.42, -0.35, -0.6)
CHIN = (0.0, -1.95, -0.86)
HEAD_AT = Vector((0, -1.55, 6.4))
HEAD_PITCH = 0.7        # tête basse, cornes en avant (charge)
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")


def head_matrix():
    return Matrix.Translation(HEAD_AT) @ Matrix.Rotation(HEAD_PITCH, 4, "X")


def place(objs, m):
    for o in objs:
        o.data.transform(m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


def new_objects(before):
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def arm_points(s):
    return (Vector((s * 1.3, -0.75, 5.5)), Vector((s * 1.8, -0.55, 4.15)),
            Vector((s * 1.8, -1.45, 3.0)), Vector((s * 1.85, -1.65, 2.55)))


def leg_points(s):
    return (Vector((s * 0.55, 0.35, 3.55)), Vector((s * 0.7, -0.45, 2.4)),
            Vector((s * 0.72, 0.45, 1.15)), Vector((s * 0.74, 0.1, 0.32)))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    m = head_matrix()
    rig.bone("Neck", SPINE[-1], m @ Vector((0, 0.05, -0.35)), "Spine3")
    rig.bone("Head", m @ Vector((0, 0.05, -0.35)), m @ Vector((0, -2.0, -0.3)), "Neck")
    rig.bone("Jaw", m @ Vector((0, HINGE[1], HINGE[2])), m @ Vector(CHIN), "Head")
    rig.bone("Tail1", TAIL[0], TAIL[6], "Spine1")
    rig.bone("Tail2", TAIL[6], TAIL[-1], "Tail1")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd = arm_points(s)
        rig.bone(f"UpperArm_{side}", sh, el, "Spine3")
        rig.bone(f"ForeArm_{side}", el, wr, f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", wr, hd, f"ForeArm_{side}")
        hp, kn, hk, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Spine1")
        rig.bone(f"Shin_{side}", kn, hk, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", hk, ft, f"Shin_{side}")
        rig.fx(f"Eye{side}", m @ Vector((s * 0.55, EYE[0], EYE[1])), "Head")
        rig.fx(f"Nostril{side}", m @ Vector((s * 0.15, -2.3, -0.3)), "Head")
        rig.fx(f"HornTip{side}", m @ Vector((s * 1.35, -0.95, 0.7)), "Head")
    rig.fx("Heart", (0, -0.4, 4.6), "Spine2")
    rig.fx("Labrys", (-1.9, -1.55, 5.0), "Hand_R")
    rig.fx("Thread", (1.6, -2.4, 0.1), "Hand_L")


# ---------------------------------------------------------------- tête (repère canonique)

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.17, 0.15),
                  a.hole_x((0, -1.1, -0.38), 0.2, 0.09),
                  a.hole_along((0, -1.55, -0.05), (0, 0, 1), (1, 0, 0), 0.13, 0.3, depth=0.4)]
          + [a.hole_along((sx * 0.22, -0.55, 0.1), (0, 0, 1), (1, 0, 0), 0.06, 0.09, depth=0.3)
             for sx in (-1, 1)]
          + [a.hole_along((sx * 0.15, -2.2, -0.3), (0, 1, 0), (1, 0, 0), 0.08, 0.11, depth=0.4)
             for sx in (-1, 1)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    # Ouverture nasale ajourée sur le chanfrein, foramens frontaux, avec rebords
    ring = [top(0.15 * math.cos(t), -1.55 + 0.33 * math.sin(t)) for t in
            (2 * math.pi * k / 12 for k in range(12))]
    if all(p is not None for p in ring):
        rig.add(r.tube("NasalRim", [tuple(p + Vector((0, 0, 0.02))) for p in ring], 0.04,
                       segments=4, closed=True), H, "bone_shade", **HEAD)
    for sx in (-1, 1):
        rig.add(a.ring_around(f"FrontalForamen{sx}", top(sx * 0.22, -0.55), (0, 0, 1), 0.09, 0.025,
                              segments=8), H, "bone_shade", **HEAD)
        rig.add(a.blade(f"BrowRidge{sx}", (sx * 0.25, -0.75, 0.12), (sx * 0.62, -0.5, 0.05), 0.16,
                        0.08, width_end=0.1, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
    # Chignon (crête entre les cornes), crête frontale, os nasaux, mufle
    rig.add(a.band("Poll", [(-0.5, 0.02, 0.08), (0, 0.06, 0.2), (0.5, 0.02, 0.08)],
                   [0.12, 0.18, 0.12], 0.1, up=(0, 0.3, 1), offset=0), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        rig.add(r.tube(f"Frontal{s}", [tuple(top(s * 0.3, y) + Vector((0, 0, 0.01)))
                                       for y in (-0.15, -0.5, -0.85)], [0.05, 0.06, 0.04],
                       segments=4), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Nasal{s}", [tuple(top(s * 0.1, y) + Vector((0, 0, 0.01)))
                                     for y in (-1.0, -1.15, -1.25)], [0.04, 0.045, 0.04],
                       segments=4), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"NostrilRim{s}", (s * 0.15, -2.26, -0.3), (0, -1, 0), 0.1, 0.035,
                              segments=10), H, "bone_shade", **HEAD)
        # Orbites en manchon qui dépassent sur les côtés, œil de feu, arcade à piques
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.tube(f"OrbitTube{s}", [tuple(c0 - Vector((s * 0.05, 0, 0))),
                                         tuple(c0 + Vector((s * 0.16, 0.02, 0.02)))],
                       [0.2, 0.21], segments=10), H, "bone", **HEAD)
        rig.add(r.ico(f"Eye{s}", 0.12, subdivisions=2, location=c0 + Vector((s * 0.1, 0, 0))), H,
                "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", c0 + Vector((s * 0.17, 0, 0)), (s, 0, 0), 0.2, H,
                       spikes=5, **HEAD)
        # Cornes de buffle : tombent sur les côtés puis remontent en crochet vers l'avant
        horn = [(s * 0.35, -0.1, 0.25), (s * 0.95, -0.05, 0.12), (s * 1.35, -0.25, -0.35),
                (s * 1.5, -0.6, -0.05), (s * 1.35, -0.95, 0.7)]
        rig.add(a.ridged_horn(f"Horn{s}", horn, 0.25, ridges=9), H, "horn", **HEAD)
        rig.add(a.claw(f"HornCap{s}", mr.along(horn, 0.93), Vector(horn[-1]) - Vector(horn[-2]), 0.22, 0.06,
                       curl=0, segments=5), H, "gold", **HEAD)
        # Bouclier frontal : deux moitiés de casque bosselées, séparées par un sillon
        rig.add(a.band(f"Boss{s}", [(s * 0.06, 0.05, 0.3), (s * 0.4, 0.0, 0.32), (s * 0.85, -0.05, 0.18)],
                       [0.55, 0.5, 0.35], 0.16, up=(0, -1, 0.15), offset=0.3), H, "horn", **HEAD)
        for k in range(3):
            rig.add(r.ico(f"BossBump{s}{k}", 0.08, subdivisions=1,
                          location=(s * (0.2 + 0.22 * k), -0.12, 0.42 - 0.06 * k), scale=(1.2, 0.8, 0.6)),
                    H, "bone_shade", **HEAD)
        # Fissures cramoisies, pores du mufle
        for k in range(4):
            rig.add(r.ico(f"MuzzlePore{s}{k}", 0.03, subdivisions=1,
                          location=(s * a.side_width(SKULL, -1.6 - 0.08 * k, -0.35) * 1.02,
                                    -1.6 - 0.08 * k, -0.35 + 0.05 * (k % 2))), H, "ink", **HEAD)
        # Arcade zygomatique
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.5, -0.3, -0.38), (s * 0.58, -0.75, -0.42),
                                         (s * 0.44, -1.15, -0.45)], [0.06, 0.07, 0.05],
                       segments=5), H, "bone", **HEAD)
    rig.add(r.ico("NosePad", 0.2, subdivisions=1, location=(0, -2.12, -0.22), scale=(1.8, 0.6, 1)),
            H, "bone_shade", **HEAD)
    # Rangée du haut : molaires, défenses démoniaques ; mandibule longue
    for s in (-1, 1):
        for k in range(5):
            y = -0.6 - 0.2 * k
            x = s * a.side_width(SKULL, y, -0.58) * 0.85
            rig.add(mr.tooth(f"UpMolar{s}{k}", (x, y, -0.58), (x, y - 0.02, -0.72), 0.17, 0.1,
                             Vector((s, 0, 0)), curl=0.02), H, "tooth", **HEAD)
        tusk_base = Vector((s * 0.33, -1.5, -0.58))
        rig.add(mr.tooth(f"UpTusk{s}", tusk_base, tusk_base + Vector((s * 0.06, -0.12, -0.5)), 0.16,
                         0.1, Vector((s, -0.3, 0)), curl=0.15), H, "tooth", **HEAD)
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.36, -1.0, -0.72)),
                Vector((s * 0.26, -1.55, -0.8)), Vector((s * 0.1, -1.95, -0.84))]
        hs = [0.42, 0.3, 0.24, 0.2]
        rig.add(a.band(f"Mandible{s}", line, hs, [0.13, 0.11, 0.1, 0.09], offset=1), J, "bone",
                **HEAD)
        rig.add(r.tube(f"MandibleBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.045, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.1, 0)),
                        line[0] + Vector((0, 0.0, 0.38)), 0.22, 0.07, width_end=0.1,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.1, subdivisions=1, location=line[0] + Vector((0, 0.03, 0.05))),
                H, "bone_shade", **HEAD)
        for k in range(4):
            p = mr.along(line, 0.12 + 0.12 * k)
            rig.add(mr.tooth(f"LowMolar{s}{k}", p, p + Vector((0, 0, 0.13)), 0.16, 0.09,
                             Vector((s, 0, 0)), curl=0.02), J, "tooth", **HEAD)
        tb = mr.along(line, 0.72)
        rig.add(mr.tooth(f"LowTusk{s}", tb, tb + Vector((s * 0.12, -0.05, 0.55)), 0.15, 0.1,
                         Vector((s, -0.2, 0)), curl=0.2), J, "tooth", **HEAD)
        for k in range(4):    # incisives en pelle, en éventail à l'avant
            t = 0.88 + 0.035 * k
            p = mr.along(line, t) + Vector((-s * 0.02 * k, 0, 0))
            rig.add(mr.tooth(f"Incisor{s}{k}", p, p + Vector((0, -0.12, 0.16)), 0.1, 0.04,
                             Vector((s * 0.4, -1, 0)), curl=0.02), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.04, 0, 0.02))) for p in line[1:]],
                       0.045, segments=4), J, "gum", **HEAD)
    rig.add(r.ico("Throat", 0.18, subdivisions=2, location=(0, -0.9, -0.6), scale=(1.4, 2, 0.5)),
            H, "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        hump = i >= n - 7
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.27, spine=2.2 if hump else 1.3,
                           lean=0.5 if hump else 0.4), spine_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.27), spine_bone(i),
                    "disc")
    # Cou : vertèbres du garrot jusqu'à la nuque
    m = head_matrix()
    neck = a.smooth_path([tuple(SPINE[-1]), tuple(SPINE[-1].lerp(m @ Vector((0, 0.05, -0.35)), 0.5)
                                                  + Vector((0, 0.05, 0.05))),
                          tuple(m @ Vector((0, 0.05, -0.35)))], 5)
    for i in range(len(neck)):
        t = tangent(neck, i)
        rig.add(a.vertebra(f"NeckVert{i}", neck[i], t, 0.24, spine=1.6, lean=0.6), "Neck", "bone")
    # Cage thoracique en tonneau, sternum, cœur de flammes
    sternum = []
    for k, i in enumerate(range(5, 14)):
        hw = 0.8 + 0.25 * math.sin(math.pi * k / 8)
        depth = 1.2 + 0.4 * math.sin(math.pi * (k + 1) / 10)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.3, radius=0.09),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.3, -depth)))
    rig.add(r.tube("Sternum", [tuple(p) for p in sternum[1:-1:2]], 0.1, segments=6), "Spine2",
            "bone_shade")
    # Médaillon-labyrinthe lumineux sur le cœur (anneaux concentriques + pierre centrale)
    heart = Vector((0, -0.75, 4.25))
    for k, rad in enumerate((0.34, 0.24, 0.14)):
        rig.add(a.ring_around(f"Labyrinth{k}", heart, (0, -1, 0.2), rad, 0.03, segments=12), "Spine2", "glow",
                glow=True)
    rig.add(a.crystal("LabyrinthCore", heart, 0.07, 0.2, sides=4), "Spine2", "glow", glow=True)
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2
        rig.add(r.tube(f"LabyrinthWall{k}", [tuple(heart + Vector((0.14 * math.cos(ang), 0, 0.14 * math.sin(ang)))),
                                             tuple(heart + Vector((0.34 * math.cos(ang), 0, 0.34 * math.sin(ang))))],
                       0.025, segments=4), "Spine2", "gold")
    # Omoplates, clavicules, bassin
    for s in (-1, 1):
        sh = arm_points(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[12] + Vector((s * 0.3, 0.15, 0.1)),
                        sh + Vector((0, 0.08, 0.05)), 0.6, 0.09, width_end=0.3, mid=0.65,
                        normal=(0.3 * s, 0.6, 1)), "Spine3", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, sternum[-2] + Vector((s * 0.2, 0, 0)), 0.07,
                            condyles=False), "Spine3", "bone_shade")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.15, 0, 0)),
                        hp + Vector((s * 0.25, -0.1, 0.6)), 0.5, 0.09, width_end=0.4, mid=0.6,
                        normal=(s, 0, 0.3)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.3, 0.05, 3.1), (0, 0.1, 3.05)], 0.08,
                       segments=5), "Spine1", "bone")
        rig.add(r.tube(f"Ischium{s}", [tuple(hp), (s * 0.3, 0.75, 3.2)], [0.08, 0.06], segments=5),
                "Spine1", "bone_shade")
    # Queue de taureau, touffe de feu
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        size = 0.13 - 0.06 * i / (nt - 1)
        bone = "Tail1" if i < 6 else "Tail2"
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=0.8, transverse=False), bone,
                "bone")
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc")
    rig.add(a.ring_around("TailRing", TAIL[-2], tangent(TAIL, nt - 2), 0.08, 0.03, segments=8), "Tail2", "gold")
    for k in range(5):
        ang = 2 * math.pi * k / 5
        rig.add(a.claw(f"TailTuft{k}", TAIL[-1], (0.4 * math.cos(ang), 0.4 * math.sin(ang), -1), 0.35, 0.04,
                       curl=0.2, segments=4), "Tail2", "bone_shade")
    # Armure grecque : ceinture de bronze à méandres, jupe de lanières de cuir (ptéryges)
    belt_c = SPINE[1] + Vector((0, -0.15, -0.25))
    rig.add(a.ring_around("Belt", belt_c, (0, 0.1, 1), 0.85, 0.07, segments=16), "Spine1", "gold")
    for k in range(12):
        ang = 2 * math.pi * k / 12
        d = Vector((math.cos(ang), math.sin(ang) * 0.9, 0))
        if d.y > 0.6:
            continue
        rig.add(a.blade(f"Pteryx{k}", belt_c + d * 0.85, belt_c + d * 1.0 + Vector((0, 0, -0.75)), 0.2, 0.03,
                        width_end=0.18, normal=d, bevel=0), "Spine1", "leather")
        rig.add(r.box(f"Meander{k}", (0.1, 0.03, 0.08), location=belt_c + d * 0.93), "Spine1", "gold")

def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd = arm_points(s)
        ua, fa, hb = f"UpperArm_{side}", f"ForeArm_{side}", f"Hand_{side}"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.19, segments=8), ua, "bone", **ARMS)
        off = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.1
        rig.add(a.long_bone(f"Radius{s}", el + off, wr + off, 0.1, condyles=False, segments=6), fa,
                "bone", **ARMS)
        rig.add(a.long_bone(f"Ulna{s}", el - off, wr - off, 0.09, condyles=False, segments=6), fa,
                "bone_shade", **ARMS)
        rig.add(a.claw(f"Olecranon{s}", el, (0, 1, 0.3), 0.32, 0.08, curl=0, segments=5), fa,
                "horn", **ARMS)
        # Brassard de bronze à méandres
        for k, f in enumerate((0.15, 0.4)):
            rig.add(a.ring_around(f"Bracer{s}{k}", wr.lerp(el, f), el - wr, 0.17, 0.05, segments=10), fa,
                    "gold", **ARMS)
        # Main : métacarpes + 4 doigts griffus
        rig.add(r.ico(f"Wrist{s}", 0.14, subdivisions=1, location=wr), hb, "bone_shade", **ARMS)
        lat = Vector((s, 0, 0))
        for j in range(4):
            off_j = (j - 1.5) * 0.12
            base = hd + lat * off_j
            rig.add(a.long_bone(f"Metacarpal{s}{j}", wr + lat * off_j * 0.5, base, 0.05,
                                condyles=False, segments=5), hb, "bone", **ARMS)
            mid = base + Vector((lat.x * off_j * 0.2, -0.25, -0.25))
            rig.add(a.long_bone(f"Finger{s}{j}", base, mid, 0.045, condyles=False, segments=5), hb,
                    "bone", **ARMS)
            rig.add(a.claw(f"HandClaw{s}{j}", mid, (0, -0.4, -1), 0.3, 0.05, curl=0.45,
                           segments=5), hb, "horn", **ARMS)


def build_gear(rig):
    """Labrys en main droite, épaulière, fil d'Ariane enroulé au bras gauche."""
    sh, el, wr, hd = arm_points(-1)
    grip = hd + Vector((0, -0.1, -0.1))
    bottom, top_ = grip + Vector((0.05, 0.25, -1.5)), grip + Vector((-0.1, 0.15, 2.6))
    rig.add(r.tube("LabrysHaft", [tuple(bottom), tuple(grip), tuple(top_)], [0.07, 0.08, 0.07], segments=6),
            "Hand_R", "leather", **ARMS)
    for k, f in enumerate((0.45, 0.62, 0.8)):
        rig.add(a.ring_around(f"HaftRing{k}", bottom.lerp(top_, f), top_ - bottom, 0.09, 0.025, segments=8),
                "Hand_R", "gold", **ARMS)
    head = bottom.lerp(top_, 0.9)
    up = (top_ - bottom).normalized()
    for sy in (-1, 1):
        rig.add(a.blade(f"LabrysBlade{sy}", head, head + Vector((0, sy * 0.95, 0)), 0.35, 0.06, width_end=1.05,
                        mid=0.55, normal=(1, 0, 0)), "Hand_R", "gold", **ARMS)
        rig.add(r.tube(f"LabrysEdge{sy}", [tuple(head + Vector((0, sy * 0.9, 0.52))),
                                           tuple(head + Vector((0, sy * 1.0, 0))),
                                           tuple(head + Vector((0, sy * 0.9, -0.52)))], 0.03, segments=4),
                "Hand_R", "glow", glow=True)
    rig.add(a.claw("LabrysSpike", top_, up, 0.35, 0.06, curl=0, segments=4), "Hand_R", "gold", **ARMS)
    # Épaulière de bronze sur l'épaule droite
    rig.add(a.band("Pauldron", [sh + Vector((0.25, -0.35, 0.05)), sh + Vector((-0.05, 0, 0.3)),
                                sh + Vector((0.2, 0.35, 0.05))], [0.5, 0.6, 0.5], 0.06, up=(-1, 0, -0.3),
                   offset=0.2), "UpperArm_R", "gold", **ARMS)
    # Fil d'Ariane : spirale autour de l'avant-bras gauche puis pelote qui traîne au sol
    sh, el, wr, hd = arm_points(1)
    axis = (wr - el).normalized()
    side = axis.cross(Vector((0, 1, 0))).normalized()
    up2 = axis.cross(side)
    coil = [tuple(el.lerp(wr, 0.1 + 0.8 * k / 23) + (side * math.cos(k * 0.9) + up2 * math.sin(k * 0.9)) * 0.16)
            for k in range(24)]
    rig.add(r.tube("ThreadCoil", coil, 0.022, segments=4), "ForeArm_L", "glow_thread", glow=True)
    trail = a.smooth_path([coil[-1], tuple(wr + Vector((0.25, -0.3, -0.9))), (2.1, -2.0, 0.5), (1.6, -2.4, 0.08),
                           (0.8, -2.9, 0.05)], 12)
    rig.add(r.tube("ThreadTrail", [tuple(p) for p in trail], 0.02, segments=4), "Hand_L", "glow_thread",
            glow=True)
    rig.add(r.ico("ThreadBall", 0.14, subdivisions=2, location=(0.8, -2.9, 0.14)), "Root", "glow_thread",
            glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, hk, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.16, segments=8), th, "bone", **LEGS)
        rig.add(r.ico(f"Patella{s}", 0.11, subdivisions=1, location=kn + Vector((0, -0.15, 0.03))),
                th, "bone_shade", **LEGS)
        rig.add(a.long_bone(f"Tibia{s}", kn, hk, 0.13, segments=8), sn, "bone", **LEGS)
        rig.add(a.claw(f"Calcaneus{s}", hk, (0, 1, 0.5), 0.32, 0.09, curl=0, segments=5), fo,
                "bone_shade", **LEGS)
        rig.add(a.long_bone(f"Cannon{s}", hk, ft, 0.1, segments=7), fo, "bone", **LEGS)
        rig.add(a.ring_around(f"Fetlock{s}", ft, ft - hk, 0.16, 0.04, segments=10), fo, "gold", **LEGS)
        rig.add(a.band(f"Greave{s}", [kn + Vector((0, -0.14, -0.1)), kn.lerp(hk, 0.5) + Vector((0, -0.16, 0)),
                                      hk + Vector((0, -0.14, 0.15))], 0.3, 0.04, up=(1, 0, 0), offset=0.5),
                sn, "gold", **LEGS)
        # Sabot fendu : deux onglons de corne noire
        for k, dx in enumerate((-0.11, 0.11)):
            base = ft + Vector((dx, -0.05, -0.12))
            pastern = base + Vector((dx * 0.3, -0.2, -0.1))
            rig.add(a.long_bone(f"Pastern{s}{k}", ft, pastern, 0.06, condyles=False, segments=5),
                    fo, "bone", **LEGS)
            rig.add(a.claw(f"Hoof{s}{k}", pastern + Vector((0, 0.08, 0.02)), (dx * 0.5, -1, -0.55),
                           0.32, 0.12, curl=0.1, segments=6), fo, "horn", **LEGS)
        rig.add(a.claw(f"Dewclaw{s}", ft + Vector((0, 0.12, -0.02)), (0, 1, -0.4), 0.14, 0.04,
                       curl=0.2, segments=4), fo, "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    before = {o.name for o in bpy.context.scene.objects}
    build_head(rig)
    place(new_objects(before), head_matrix())
    build_body(rig)
    build_arms(rig)
    build_gear(rig)
    build_legs(rig)
    return rig
