"""Cerbère squelette (≈ 5 studs au garrot, 7 de long) — créature animable.
Pack « Enfers volcaniques », créature 1.

Animal modèle : le loup (chien de garde des Enfers) — 3 crânes de loup **identiques** : stop
marqué, haute crête sagittale, arcades zygomatiques très larges, canines et carnassières ;
corps de grand molosse au poitrail profond, pattes digitigrades ; queue de serpent (mythe).

Identité : os calcinés gris-noir fendus de lave, rebords rouille ; **cornes démoniaques
annelées** sur chaque tête ; **colliers de fer à pointes** reliés par des chaînes brisées à un
anneau sur le poitrail ; crinières de flammes sur les cous ; quadrupède massif à 3 cous en
éventail ; queue terminée par une tête de vipère ; thème d'effets « fire » rouge-orange.

6 pièces Roblox : corps, HeadA/HeadB/HeadC (une par tête), Legs, + lumineux.
Os : Root, Hips, Spine, Chest, Neck{A,B,C}1-2, Head{A,B,C}, Jaw{A,B,C}, Tail1-3,
Front/Hind{Upper,Lower,Paw}_{L,R}, + FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#4d4440",
    "bone_shade": "#5e3426",
    "tooth": "#efe2c8",
    "horn": "#151212",
    "horn_tip": "#ff5a1a",
    "disc": "#2a1f1c",
    "iron": "#55555c",
    "gum": "#5a1a14",
    "ink": "#0c0a09",
    "glow": "#ff4a1a",
    "glow_hot": "#ffd080",
}

EFFECT_THEME = "fire"

TEST_POSE = {
    "JawA": (25, 0, 0),
    "NeckB2": (0, 0, 20),
    "NeckC1": (15, 0, 0),
    "FrontUpper_L": (-35, 0, 0),
    "Tail2": (0, 0, 30),
}

VIEW = (0.9, -1.0, 0.45)

SPINE = a.smooth_path([(0, 2.25, 2.95), (0, 1.1, 3.1), (0, -0.1, 3.3), (0, -0.85, 3.45)], 18)
TAIL = a.smooth_path([(0, 2.35, 2.95), (0, 3.2, 3.35), (0.35, 4.0, 3.35), (0.8, 4.5, 2.8),
                      (0.75, 4.35, 2.05)], 16)
# Crâne de loup (repère canonique, occiput en O) — identique pour les 3 têtes
SKULL = [(-1.3, 0.45, 0.55, 0.42, 6.22, 5.5), (-1.7, 0.52, 0.64, 0.5, 6.42, 5.45),
         (-2.1, 0.46, 0.6, 0.48, 6.32, 5.45), (-2.38, 0.32, 0.42, 0.38, 6.02, 5.47),
         (-2.8, 0.25, 0.33, 0.32, 5.92, 5.47), (-3.2, 0.21, 0.27, 0.27, 5.86, 5.48)]
EYE = (-2.12, 6.02)
HINGE = (0.47, -1.6, 5.4)
CHIN = (0.1, -3.12, 4.92)
O = Vector((0, -1.3, 5.8))
HEAD_SCALE = 0.75
# Cous : (chemin depuis le poitrail, lacet, tangage) ; tête centrale plus haute
NECKS = {
    "A": ([(0, -0.95, 3.5), (0, -1.5, 4.5), (0, -1.75, 5.35)], 0.0, 0.1),
    "B": ([(0.35, -0.95, 3.4), (1.1, -1.45, 4.0), (1.75, -1.75, 4.45)], 0.6, 0.15),
    "C": ([(-0.35, -0.95, 3.4), (-1.1, -1.45, 4.0), (-1.75, -1.75, 4.45)], -0.6, 0.15),
}
LEGS = dict(part="Legs")


def head_matrix(key):
    pts, yaw, pitch = NECKS[key]
    return (Matrix.Translation(pts[-1]) @ Matrix.Rotation(yaw, 4, "Z")
            @ Matrix.Rotation(pitch, 4, "X") @ Matrix.Scale(HEAD_SCALE, 4)
            @ Matrix.Translation(-O))


def place(objs, m):
    for o in objs:
        o.data.transform(m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


def new_objects(before):
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return "Hips" if i < 6 else ("Spine" if i < 12 else "Chest")


def front_leg(s):
    return (Vector((s * 0.72, -0.75, 2.9)), Vector((s * 0.8, -0.45, 1.75)),
            Vector((s * 0.8, -0.8, 0.7)), Vector((s * 0.82, -0.95, 0.18)))


def hind_leg(s):
    return (Vector((s * 0.6, 2.05, 2.8)), Vector((s * 0.72, 1.35, 1.8)),
            Vector((s * 0.74, 2.2, 0.95)), Vector((s * 0.76, 1.8, 0.18)))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[6], "Root")
    rig.bone("Spine", SPINE[6], SPINE[12], "Hips")
    rig.bone("Chest", SPINE[12], SPINE[-1], "Spine")
    for key, (pts, _, _) in NECKS.items():
        rig.bone(f"Neck{key}1", pts[0], pts[1], "Chest")
        rig.bone(f"Neck{key}2", pts[1], pts[2], f"Neck{key}1")
        m = head_matrix(key)
        rig.bone(f"Head{key}", m @ O, m @ Vector((0, -3.3, 5.7)), f"Neck{key}2")
        rig.bone(f"Jaw{key}", m @ Vector((0, HINGE[1], HINGE[2])), m @ Vector((0, CHIN[1], CHIN[2])),
                 f"Head{key}")
        for s, side in ((1, "L"), (-1, "R")):
            rig.fx(f"Eye{key}{side}", m @ Vector((s * 0.4, EYE[0], EYE[1])), f"Head{key}")
        rig.fx(f"Mouth{key}", m @ Vector((0, -2.6, 5.3)), f"Head{key}")
    rig.bone("Tail1", TAIL[0], TAIL[5], "Hips")
    rig.bone("Tail2", TAIL[5], TAIL[10], "Tail1")
    rig.bone("Tail3", TAIL[10], TAIL[-1], "Tail2")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Chest"), ("Hind", hind_leg(s), "Hips")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Paw_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
    rig.fx("Heart", (0, -0.4, 2.45), "Chest")
    rig.fx("TailHead", TAIL[-1] + Vector((0, -0.3, -0.1)), "Tail3")


# ---------------------------------------------------------------- têtes (repère canonique)

def build_head(rig, k):
    H, J = f"Head{k}", f"Jaw{k}"
    HEAD = dict(part=f"Head{k}")
    skull = a.loft_profile("Skull", SKULL, droop=0.18)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.19, 0.16),
                  a.hole_x((0, -1.62, 5.78), 0.26, 0.17),             # fosse temporale
                  a.hole_x((0, -2.62, 5.72), 0.12, 0.07)])            # foramen infra-orbitaire
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Crête sagittale haute + crête nucale en éventail à l'arrière
    crest = [top(0, y) for y in (-1.3, -1.55, -1.85, -2.1)]
    rig.add(a.band("Sagittal", crest, [0.3, 0.34, 0.22, 0.06], 0.07, offset=0.15), H,
            "bone_shade", **HEAD)
    rig.add(a.band("Nuchal", [(-0.45, -1.3, 6.0), (0, -1.22, 6.35), (0.45, -1.3, 6.0)],
                   [0.12, 0.2, 0.12], 0.08, up=(0, 1, 0.4), offset=0), H, "bone_shade", **HEAD)
    # Os nasaux : deux crêtes du stop à la truffe ; truffe et narines
    for s in (-1, 1):
        nasal = [top(s * 0.1, y) + Vector((0, 0, 0.02)) for y in (-2.35, -2.75, -3.15)]
        rig.add(r.tube(f"Nasal{s}", [tuple(p) for p in nasal], [0.045, 0.05, 0.04], segments=4),
                H, "bone_shade", **HEAD)
        rig.add(r.ico(f"Nostril{s}", 0.07, subdivisions=1, location=(s * 0.08, -3.48, 5.6),
                      scale=(0.8, 0.6, 1.1)), H, "ink", **HEAD)
    rig.add(r.ico("NoseKnob", 0.13, subdivisions=1, location=(0, -3.42, 5.72),
                  scale=(1.3, 0.8, 0.9)), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        # Orbite cerclée, œil lunaire, arcade sourcilière en corniche à piques
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.13, subdivisions=2, location=(s * (x - 0.08), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, -0.25, 0.1), 0.19, H,
                       spikes=4, **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.18, -2.35, 6.2), (s * 0.55, -1.95, 6.28), 0.2, 0.09,
                        width_end=0.12, mid=0.24, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        for j in range(2):
            rig.add(a.claw(f"BrowSpike{s}{j}", (s * (0.38 + 0.12 * j), -2.15 + 0.12 * j, 6.3),
                           (s * 0.4, 0.6, 0.6), 0.2, 0.035, curl=-0.1, segments=4), H, "horn",
                    **HEAD)
        # Arcade zygomatique très large (signature du loup) + processus postorbitaire
        zyg = a.smooth_path([(s * 0.48, -1.42, 5.6), (s * 0.8, -1.75, 5.64),
                             (s * 0.8, -2.08, 5.7), (s * 0.48, -2.42, 5.76)], 7)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg],
                       [0.06, 0.075, 0.085, 0.085, 0.08, 0.07, 0.06], segments=6), H, "bone",
                **HEAD)
        zyg = [zyg[0], zyg[2], zyg[4], zyg[6]]
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.55, -1.95, 6.25), (s * 0.75, -2.0, 5.75)],
                       [0.06, 0.05], segments=5), H, "bone_shade", **HEAD)
        rig.add(a.claw(f"ZygSpike{s}", zyg[1], (s, 0.5, 0.1), 0.25, 0.05, curl=0, segments=4), H,
                "horn", **HEAD)
        # Cornes démoniaques annelées balayées vers l'arrière (à la place des oreilles)
        horn = [(s * 0.33, -1.55, 6.25), (s * 0.58, -1.2, 6.62), (s * 0.78, -0.72, 6.78),
                (s * 0.8, -0.32, 6.6)]
        rig.add(a.ridged_horn(f"Horn{s}", horn, 0.1, ridges=6), H, "horn", **HEAD)
        rig.add(a.ring_around(f"HornBand{s}", Vector(horn[1]), Vector(horn[2]) - Vector(horn[0]),
                              0.11, 0.03, segments=8), H, "iron", **HEAD)
        rig.add(r.ico(f"HornEmber{s}", 0.045, subdivisions=1, location=horn[-1]), H, "glow",
                glow=True)
        # Crête infra-orbitaire, pores des moustaches, cicatrice lunaire
        rig.add(r.tube(f"Maxillary{s}", [(s * 0.42, -2.3, 5.62), (s * 0.33, -2.75, 5.6),
                                         (s * 0.27, -3.15, 5.58)], [0.06, 0.05, 0.04],
                       segments=5), H, "bone_shade", **HEAD)
        for j in range(6):
            yy = -2.8 - 0.09 * j
            rig.add(r.ico(f"Whisker{s}{j}", 0.028, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy, 5.67 + 0.05 * (j % 2)) * 1.02, yy,
                                    5.67 + 0.05 * (j % 2))), H, "ink", **HEAD)
        mr.scar(rig, f"LavaScar{s}", top(s * 0.3, -1.4), top(s * 0.42, -1.85), H, width=0.04,
                seed=s)
        # Gencive le long de la rangée du haut
        gum = [(s * a.side_width(SKULL, y, 5.5) * 0.8, y, 5.47) for y in (-1.95, -2.4, -2.9, -3.3)]
        rig.add(r.tube(f"UpperGum{s}", gum, 0.05, segments=4), H, "gum", **HEAD)
    # Fissures de lave sur le crâne calciné
    for j, (p0, p1) in enumerate((((0.12, -1.35), (0.2, -1.9)), ((-0.15, -1.4), (-0.25, -2.0)),
                                  ((0.1, -2.45), (0.14, -3.0)))):
        mr.scar(rig, f"SkullCrack{j}", top(*p0) + Vector((0, 0, 0.01)),
                top(*p1) + Vector((0, 0, 0.01)), H, width=0.05, seed=j + 4)
    build_jaw(rig, k)
    build_teeth(rig, k)


def jaw_line(s):
    """Bord dentaire du dentaire, de la charnière au menton."""
    hx, hy, hz = HINGE
    cx, cy, cz = CHIN
    # bord légèrement creusé (courbe), pas une planche droite
    return [Vector((s * (hx + (cx - hx) * t ** 0.8), hy + (cy - hy) * t,
                    hz + (cz - hz) * t - 0.07 * math.sin(math.pi * t)))
            for t in (0.0, 0.25, 0.5, 0.75, 1.0)]


def build_jaw(rig, k):
    H, J = f"Head{k}", f"Jaw{k}"
    HEAD = dict(part=f"Head{k}")
    for s in (-1, 1):
        line = jaw_line(s)
        hs = [0.38, 0.37, 0.33, 0.27, 0.25]    # bord inférieur bombé, menton marqué
        rig.add(a.band(f"Dentary{s}", line, hs, [0.16, 0.15, 0.13, 0.12, 0.11], offset=1), J,
                "bone", **HEAD)
        rig.add(r.tube(f"DentaryRidge{s}", [tuple(p + Vector((s * 0.09, 0, -h * 0.6)))
                                            for p, h in zip(line[:4], hs)],
                       [0.05, 0.05, 0.04, 0.03], segments=4), J, "bone_shade", **HEAD)
        rig.add(r.tube(f"DentaryBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.045, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.15, 0)),
                        line[0] + Vector((0, -0.05, 0.42)), 0.24, 0.07, width_end=0.1,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(a.claw(f"Angular{s}", line[0] - Vector((0, 0, 0.25)), (0, 1, -0.3), 0.22, 0.05,
                       curl=0.1, segments=4), J, "bone_shade", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.11, subdivisions=1, location=line[0] + Vector((0, 0.05, 0.03))),
                H, "bone_shade", **HEAD)
        for j in range(3):
            q = line[1 + j] - Vector((0, 0, 0.12))
            rig.add(r.ico(f"MentalForamen{s}{j}", 0.03, subdivisions=1,
                          location=q + Vector((s * 0.055, 0, 0))), J, "ink", **HEAD)
        gum = [tuple(p + Vector((-s * 0.04, 0, 0.02))) for p in line[1:]]
        rig.add(r.tube(f"LowerGum{s}", gum, 0.045, segments=4), J, "gum", **HEAD)
    rig.add(r.ico("ChinKnob", 0.1, subdivisions=1, location=(0, -3.16, 4.72)), J, "bone_shade",
            **HEAD)
    rig.add(r.ico("Throat", 0.2, subdivisions=2, location=(0, -1.85, 5.35), scale=(1.2, 1.4, 0.7)),
            H, "glow", glow=True)


def build_teeth(rig, k):
    H, J = f"Head{k}", f"Jaw{k}"
    HEAD = dict(part=f"Head{k}")
    # Rangée du haut : incisives, canine énorme, prémolaires, carnassière en lame
    upper = ((-3.33, 0.07, 0.14, "inc"), (-3.3, 0.14, 0.16, "inc"), (-3.24, 0.2, 0.17, "inc"),
             (-3.08, None, 0.62, "can"), (-2.85, None, 0.2, "pm"), (-2.6, None, 0.24, "pm"),
             (-2.35, None, 0.26, "pm"), (-2.08, None, 0.36, "carn"), (-1.85, None, 0.2, "mol"))
    for s in (-1, 1):
        for j, (y, x, size, kind) in enumerate(upper):
            xx = s * (x if x is not None else a.side_width(SKULL, y, 5.5) * 0.88)
            base = Vector((xx, y, 5.48))
            out = Vector((s * 0.6, -1 if kind in ("inc", "can") else -0.2, 0)).normalized()
            width = size * {"inc": 0.55, "can": 0.4, "pm": 0.8, "carn": 0.9, "mol": 1.0}[kind]
            tip = base + Vector((0, 0, -size)) + Vector((0, 0.06 * size, 0))
            rig.add(mr.tooth(f"UpTooth{s}{j}", base, tip, width, width * 0.5, out,
                             curl=0.12 if kind == "can" else 0.04), H, "tooth", **HEAD)
            if kind in ("can", "carn"):
                rig.add(r.ico(f"UpSocket{s}{j}", 0.07, subdivisions=1,
                              location=base + Vector((s * 0.06, 0, 0.08))), H, "bone_shade",
                        **HEAD)
        # Rangée du bas, sur le dentaire (canine qui remonte devant la canine du haut)
        line = jaw_line(s)
        lower = ((0.97, 0.12, "inc"), (0.92, 0.13, "inc"), (0.86, 0.5, "can"), (0.7, 0.18, "pm"),
                 (0.55, 0.2, "pm"), (0.4, 0.3, "carn"), (0.25, 0.22, "mol"))
        for j, (t, size, kind) in enumerate(lower):
            base = mr.along(line, t)
            if kind == "inc":
                base = base + Vector((-s * 0.03 * (1 + j), 0, 0))
            out = Vector((s * 0.6, -1 if kind in ("inc", "can") else -0.2, 0)).normalized()
            width = size * {"inc": 0.55, "can": 0.42, "pm": 0.8, "carn": 0.9, "mol": 1.0}[kind]
            rig.add(mr.tooth(f"LowTooth{s}{j}", base, base + Vector((0, -0.05 * size, size)),
                             width, width * 0.5, out, curl=0.12 if kind == "can" else 0.04), J,
                    "tooth", **HEAD)


# ---------------------------------------------------------------- corps


def build_heads(rig):
    for key in NECKS:
        before = {o.name for o in bpy.context.scene.objects}
        build_head(rig, key)
        place(new_objects(before), head_matrix(key))


# ---------------------------------------------------------------- cous, colliers, chaînes

def build_necks(rig):
    ring_c = Vector((0, -1.3, 2.75))     # anneau du poitrail où se rejoignent les chaînes
    rig.add(a.ring_around("ChestRing", ring_c, (0, 1, 0.3), 0.22, 0.06, segments=12), "Chest",
            "iron")
    for key, (pts, _, _) in NECKS.items():
        path = a.smooth_path(pts + [tuple(head_matrix(key) @ O)], 9)
        for i in range(len(path) - 1):
            t = tangent(path, i)
            bone = f"Neck{key}1" if i < 4 else f"Neck{key}2"
            rig.add(a.vertebra(f"NeckVert{key}{i}", path[i], t, 0.2, spine=1.3, lean=0.4),
                    bone, "bone", part=f"Head{key}")
            rig.add(a.disc(f"NeckDisc{key}{i}", path[i].lerp(path[i + 1], 0.5), t, 0.2), bone,
                    "disc", part=f"Head{key}")
            # Crinière de flammes : flammes lumineuses entre des piquants d'os
            side, up = a._basis(t)
            if i % 2 == 0:
                rig.add(a.crystal(f"Flame{key}{i}", path[i] + up * 0.3 - t * 0.05, 0.07,
                                  0.55 - 0.03 * i, sides=4), bone, "glow", glow=True)
            else:
                rig.add(a.claw(f"NeckSpike{key}{i}", path[i] + up * 0.28, up + t * 0.6, 0.38,
                               0.045, curl=-0.1, segments=4), bone, "horn", part=f"Head{key}")
        # Collier de fer à pointes juste sous la tête + anneau de chaîne
        cc, ct = path[6], tangent(path, 6)
        bone = f"Neck{key}2"
        rig.add(a.ring_around(f"Collar{key}", cc, ct, 0.32, 0.07, segments=14), bone, "iron",
                part=f"Head{key}")
        rig.add(a.ring_around(f"CollarEdge{key}", cc + ct * 0.08, ct, 0.3, 0.035, segments=14),
                bone, "bone_shade", part=f"Head{key}")
        side, up = a._basis(ct)
        for j in range(8):
            ang = 2 * math.pi * j / 8
            out = side * math.cos(ang) + up * math.sin(ang)
            rig.add(a.claw(f"CollarSpike{key}{j}", cc + out * 0.36, out, 0.28, 0.055, curl=0,
                           segments=4), bone, "iron", part=f"Head{key}")
        loop = cc - up * 0.38
        rig.add(a.ring_around(f"CollarLoop{key}", loop, side, 0.08, 0.025, segments=8), bone,
                "iron", part=f"Head{key}")
        # Chaîne (brisée au milieu) du collier vers l'anneau du poitrail
        n_links = max(6, math.ceil((ring_c - loop).length / 0.14))
        for j in range(n_links):
            if j == n_links // 2:
                continue
            p = loop.lerp(ring_c, (j + 0.5) / n_links) + Vector((0, 0, -0.15 * math.sin(
                math.pi * (j + 0.5) / n_links)))
            ax = side if j % 2 else (ring_c - loop).normalized().cross(side)
            rig.add(a.ring_around(f"Chain{key}{j}", p, ax, 0.08, 0.025, segments=8), "Chest",
                    "iron")


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.26, spine=1.8 if i > 9 else 1.3, lean=0.4),
                spine_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.26), spine_bone(i),
                    "disc")
        if i % 3 == 1:
            side, up = a._basis(t)
            rig.add(a.crystal(f"BackFlame{i}", SPINE[i] + up * 0.55, 0.06, 0.4, sides=4),
                    spine_bone(i), "glow", glow=True)
    # Poitrail profond de molosse
    sternum = []
    for k, i in enumerate(range(5, 17)):
        hw = 0.6 + 0.3 * math.sin(math.pi * k / 11)
        depth = 0.9 + 0.75 * (k / 11) ** 0.7
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.08),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(r.tube("Sternum", [tuple(p) for p in sternum[3::2]], 0.09, segments=6), "Chest",
            "bone_shade")
    for k, p in enumerate(sternum[4::2]):
        rig.add(a.claw(f"KeelSpike{k}", p, (0, -0.3, -1), 0.25, 0.05, curl=0, segments=4),
                "Chest", "horn")
    # Cœur de braise dans la cage + fissures de lave sur les côtes
    for k, (dx, dy, h) in enumerate(((0, -0.4, 0.8), (0.18, -0.25, 0.55), (-0.18, -0.55, 0.6),
                                     (0.05, -0.1, 0.45))):
        rig.add(a.crystal(f"EmberHeart{k}", (dx, dy, 2.1), 0.15 if k == 0 else 0.1, h, sides=6),
                "Chest", "glow", glow=True)
    # Omoplates, bassin
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[13] + Vector((s * 0.3, 0, 0.1)),
                        sh + Vector((0, 0.05, 0.05)), 0.55, 0.08, width_end=0.28, mid=0.6,
                        normal=(s, 0, 0.4)), "Chest", "bone")
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.15, 0, 0.1)),
                        hp + Vector((s * 0.15, -0.35, 0.45)), 0.5, 0.08, width_end=0.35, mid=0.55,
                        normal=(s, 0, 0.4)), "Hips", "bone")
        rig.add(r.tube(f"Ischium{s}", [tuple(hp), (s * 0.3, 2.55, 2.65)], [0.08, 0.06],
                       segments=5), "Hips", "bone_shade")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.25, 1.7, 2.45), (0, 1.75, 2.4)], 0.07,
                       segments=5), "Hips", "bone")
        rig.add(a.ring_around(f"Acetabulum{s}", hp, (s, 0, 0), 0.15, 0.04, segments=8), "Hips",
                "bone_shade")
    # Queue de serpent : vertèbres + écailles osseuses, tête de vipère au bout
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        size = 0.17 - 0.06 * i / (nt - 1)
        bone = "Tail1" if i < 5 else ("Tail2" if i < 10 else "Tail3")
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=1.0, lean=0.5,
                           transverse=False), bone, "bone")
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc")
            side, up = a._basis(t)
            for s in (-1, 1):
                rig.add(a.rib(f"TailRib{i}{s}", TAIL[i], 0.12, 0.18, s, sweep=0, radius=0.025,
                              segments=4), bone, "bone_shade")
    end, t = TAIL[-1], tangent(TAIL, nt - 1)
    snake = a.loft_profile("SnakeSkull", [(0.0, 0.1, 0.16, 0.13, 0.12, -0.08),
                                          (-0.25, 0.13, 0.2, 0.16, 0.13, -0.08),
                                          (-0.45, 0.08, 0.12, 0.1, 0.07, -0.06)], droop=0.1)
    a.cut(snake, [a.hole_x((0, -0.2, 0.05), 0.06, 0.05)])
    parts = [snake]
    for s in (-1, 1):
        parts.append(a.claw(f"SnakeFang{s}", (s * 0.09, -0.4, -0.06), (0, -0.3, -1), 0.2, 0.025,
                            curl=0.2, segments=4))
    m = (Matrix.Translation(end) @ Vector((0, -1, 0)).rotation_difference(t).to_matrix().to_4x4())
    for o in parts:
        o.data.transform(m)
    rig.add(snake, "Tail3", "bone")
    for o in parts[1:]:
        rig.add(o, "Tail3", "tooth")
    for s in (-1, 1):
        rig.add(r.ico(f"SnakeEye{s}", 0.04, subdivisions=1,
                      location=m @ Vector((s * 0.15, -0.2, 0.05))), "Tail3", "glow", glow=True)


# ---------------------------------------------------------------- pattes

def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, toes_dir in (("Front", front_leg(s), -1), ("Hind", hind_leg(s), -1)):
            up_b, lo_b, paw_b = (f"{prefix}Upper_{side}", f"{prefix}Lower_{side}",
                                 f"{prefix}Paw_{side}")
            big = 1.1 if prefix == "Front" else 1.0
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.15 * big, segments=7), up_b,
                    "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1], pts[2], 0.12 * big, segments=7), lo_b,
                    "bone", **LEGS)
            side_v = (pts[2] - pts[1]).cross(Vector((0, 0, 1))).normalized() * 0.12
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] + side_v, pts[2] + side_v * 0.6, 0.05,
                                condyles=False, segments=5), lo_b, "bone_shade", **LEGS)
            joint_spike = (0, 1, 0.3) if prefix == "Front" else (0, -1, 0.2)
            rig.add(a.claw(f"{prefix}JointSpike{s}", pts[1], joint_spike, 0.3, 0.06, curl=0,
                           segments=4), lo_b, "horn", **LEGS)
            rig.add(a.ring_around(f"{prefix}Glow{s}", pts[2], pts[3] - pts[2], 0.13, 0.035,
                                  segments=8), paw_b, "glow", glow=True)
            # Métatarses + 4 doigts griffus (marche sur les doigts)
            lat = Vector((s, 0, 0))
            for j in range(4):
                off = (j - 1.5) * 0.12
                m1 = pts[3] + lat * off
                rig.add(a.long_bone(f"{prefix}Meta{s}{j}", pts[2] + lat * off * 0.5, m1, 0.05,
                                    condyles=False, segments=5), paw_b, "bone", **LEGS)
                toe = m1 + Vector((lat.x * off * 0.3, -0.38, -0.1))
                rig.add(a.long_bone(f"{prefix}Toe{s}{j}", m1, toe, 0.045, condyles=False,
                                    segments=5), paw_b, "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{j}", toe, (0, -1, -0.7), 0.28, 0.05, curl=0.35,
                               segments=4), paw_b, "horn", **LEGS)
        # Fer à la patte avant gauche/droite, avec 2 maillons
        fl = front_leg(s)
        q = fl[1].lerp(fl[2], 0.7)
        rig.add(a.ring_around(f"Shackle{s}", q, fl[2] - fl[1], 0.17, 0.05, segments=10),
                f"FrontLower_{'L' if s > 0 else 'R'}", "iron", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_heads(rig)
    build_necks(rig)
    build_body(rig)
    build_legs(rig)
    return rig
