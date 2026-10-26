"""Kitsune à neuf queues squelette (≈ 5 studs de haut, queues comprises) — animable.
Pack « Mythologie », créature 4 (mythe japonais).

Animal modèle : le **renard roux** — crâne fin et léger, museau étroit et pointu, grandes
orbites, canines fines, oreilles triangulaires ; corps élancé, pattes fines.
Très différent d'Anubis (bipède noir et or) et de Fenrir (colosse hérissé) : petit
quadrupède gracieux, tête haute, **neuf queues en éventail**.

Identité : os de **porcelaine blanche** peints de **marques vermillon** comme un masque de
kitsune ; **aucune corne** : oreilles triangulaires laquées ; neuf queues d'os à « fourrure »
de lames, chacune terminée par un **kitsunebi** (feu de renard), la queue centrale porte la
**hoshi no tama** (perle-joyau) ; **shimenawa** (corde sacrée tressée) au cou avec ses papiers
shide en zigzag et une clochette ; thème d'effets « foxfire ».

Pièces Roblox : corps, Head, Legs, Tails, + lumineux.
Os : Root, Hips, Chest, Neck, Head, Jaw, Tail{1-9}_{1,2}, {Front,Hind}{Upper,Lower,Foot}_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#f1ece4",
    "bone_shade": "#a39a90",
    "tooth": "#fffaf0",
    "horn": "#1a1416",
    "disc": "#6e655d",
    "lacquer": "#d4231f",
    "rope": "#d6c38a",
    "paper": "#fbfaf5",
    "gold": "#d9a93a",
    "gum": "#8a2a30",
    "ink": "#0c0809",
    "glow": "#ff7a2e",
    "glow_hot": "#ffe2b8",
}

EFFECT_THEME = "foxfire"

TEST_POSE = {
    "Jaw": (-15, 0, 0),
    "Head": (0, 0, 20),
    "Tail5_1": (20, 0, 0),
    "Tail1_2": (0, 30, 0),
    "FrontUpper_L": (-35, 0, 0),
}

VIEW = (1.0, -0.9, 0.35)

SPINE = a.smooth_path([(0, 1.5, 3.0), (0, 0.4, 3.15), (0, -0.8, 3.3)], 14)
NECK = a.smooth_path([(0, -0.8, 3.35), (0, -1.25, 3.85), (0, -1.45, 4.35), (0, -1.65, 4.65)], 7)
# Crâne de renard dans son repère (occiput en 0, museau vers -Y)
SKULL = [(0.0, 0.24, 0.28, 0.2, 0.26, -0.16), (-0.3, 0.3, 0.36, 0.25, 0.3, -0.2),
         (-0.6, 0.24, 0.32, 0.22, 0.24, -0.22), (-0.95, 0.14, 0.2, 0.16, 0.12, -0.2),
         (-1.3, 0.1, 0.14, 0.11, 0.04, -0.16), (-1.5, 0.08, 0.11, 0.09, 0.0, -0.13)]
EYE = (-0.55, 0.1)
HINGE = (0.24, -0.2, -0.15)
GAPE = math.radians(12)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = Matrix.Translation(NECK[-1] + Vector((0, 0.1, 0.1))) @ Matrix.Rotation(math.radians(-6), 4, "X")
TAIL_BASE = Vector((0, 1.65, 3.0))
HEAD = dict(part="Head")
LEGS = dict(part="Legs")
TAILS = dict(part="Tails")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def leg(prefix, s):
    if prefix == "Front":
        return (Vector((s * 0.4, -0.85, 2.9)), Vector((s * 0.45, -0.6, 1.85)), Vector((s * 0.42, -1.0, 0.75)),
                Vector((s * 0.43, -1.15, 0.12)))
    return (Vector((s * 0.4, 1.5, 2.8)), Vector((s * 0.48, 0.95, 1.85)), Vector((s * 0.44, 1.85, 0.85)),
            Vector((s * 0.45, 1.6, 0.12)))


def tail_path(k):
    """Queue k (0..8) : part de la croupe, monte puis s'ouvre en éventail derrière."""
    phi = math.radians(-75 + 150 * k / 8)
    d = Vector((math.sin(phi), 0.45, math.cos(phi) * 0.9 + 0.25)).normalized()
    curl = Vector((math.sin(phi) * 0.4, -0.3, 0.35))
    return a.smooth_path([TAIL_BASE, TAIL_BASE + Vector((0, 0.45, 0.05)), TAIL_BASE + Vector((0, 0.55, 0.1)) + d * 1.3,
                          TAIL_BASE + Vector((0, 0.5, 0.1)) + d * 2.5 + curl], 14)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[7], "Root")
    rig.bone("Chest", SPINE[7], SPINE[-1], "Hips")
    rig.bone("Neck", NECK[0], NECK[-1], "Chest")
    rig.bone("Head", NECK[-1], HEAD_M @ Vector((0, -1.5, 0.0)), "Neck")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE), HEAD_M @ (_jm @ Vector((0, -1.45, -0.2))), "Head")
    for k in range(9):
        p = tail_path(k)
        rig.bone(f"Tail{k + 1}_1", p[0], p[7], "Hips")
        rig.bone(f"Tail{k + 1}_2", p[7], p[-1], f"Tail{k + 1}_1")
        rig.fx(f"Foxfire{k + 1}", p[-1], f"Tail{k + 1}_2")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, parent in (("Front", "Chest"), ("Hind", "Hips")):
            p = leg(prefix, s)
            prev = parent
            for k, nm in enumerate(("Upper", "Lower", "Foot")):
                prev = rig.bone(f"{prefix}{nm}_{side}", p[k], p[k + 1], prev)
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.27, EYE[0], EYE[1])), "Head")
    rig.fx("Bell", NECK[2] + Vector((0, -0.35, -0.35)), "Neck")
    rig.fx("Heart", (0, -0.3, 2.6), "Chest")


# ---------------------------------------------------------------- tête-masque

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.0, tip_length=0.08)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.12, 0.11),
                  a.hole_x((0, -0.15, 0.0), 0.13, 0.11),
                  a.hole_x((0, -0.95, -0.06), 0.15, 0.04),
                  a.hole_x((0, -1.25, -0.02), 0.08, 0.03),
                  a.hole_along((0, -1.5, -0.06), (0, 1, 0), (1, 0, 0), 0.05, 0.06, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    rig.add(a.band("Crest", [top(0, y) for y in (-0.02, -0.2, -0.4)], [0.05, 0.1, 0.04], 0.035, offset=0.2), H,
            "bone_shade", **HEAD)
    rig.add(r.tube("Nasal", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in (-0.65, -1.0, -1.35)], [0.03, 0.025, 0.02],
                   segments=4), H, "bone_shade", **HEAD)
    # Marques vermillon du masque : flamme au front, traits sur le museau
    rig.add(a.blade("ForeheadMark", top(0, -0.5) + Vector((0, 0, 0.01)), top(0, -0.15) + Vector((0, 0, 0.03)), 0.12, 0.02,
                    width_end=0.02, mid=0.14, normal=(0, -0.3, 1), bevel=0), H, "lacquer", **HEAD)
    for k, y in enumerate((-0.75, -0.95, -1.15)):
        rig.add(r.tube(f"SnoutMark{k}", [tuple(top(-0.09 + 0.01 * k, y) + Vector((0, 0, 0.012))),
                                         tuple(top(0.09 - 0.01 * k, y) + Vector((0, 0, 0.012)))], 0.014, segments=4), H,
                "lacquer", **HEAD)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.085, subdivisions=2, location=c0 - Vector((s * 0.05, 0, 0))), H, "glow", glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", c0, (s, -0.4, 0.15), 0.12, 0.028, segments=10), H, "bone_shade", **HEAD)
        # Trait vermillon qui part de l'œil vers l'oreille (masque)
        rig.add(r.tube(f"EyeMark{s}", [tuple(c0 + Vector((s * 0.02, -0.14, 0.04))), tuple(c0 + Vector((s * 0.0, 0.05, 0.12))),
                                       tuple(c0 + Vector((-s * 0.05, 0.28, 0.2)))], [0.02, 0.025, 0.012], segments=4), H,
                "lacquer", **HEAD)
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.2, -0.7, -0.07), (s * 0.31, -0.42, -0.08), (s * 0.26, -0.15, -0.06)],
                       [0.025, 0.035, 0.025], segments=4), H, "bone", **HEAD)
        rig.add(r.tube(f"Maxilla{s}", [(s * a.side_width(SKULL, y, -0.12), y, -0.12) for y in (-0.4, -0.8, -1.2, -1.45)],
                       [0.03, 0.028, 0.022, 0.016], segments=4), H, "bone_shade", **HEAD)
        # Oreilles triangulaires : cadre d'os, intérieur laqué vermillon
        eb, et = Vector((s * 0.18, -0.18, 0.24)), Vector((s * 0.4, 0.02, 0.85))
        rig.add(a.blade(f"Ear{s}", eb, et, 0.32, 0.03, width_end=0.02, mid=0.3, normal=(s * 0.3, -1, 0.15), bevel=0), H,
                "bone", **HEAD)
        rig.add(a.blade(f"EarInner{s}", eb + Vector((0, -0.025, 0.05)), et + Vector((0, -0.02, -0.12)), 0.18, 0.02,
                        width_end=0.02, mid=0.17, normal=(s * 0.3, -1, 0.15), bevel=0), H, "lacquer", **HEAD)
        for k, sx in enumerate((-1, 1)):
            rig.add(r.tube(f"EarRim{s}{k}", [tuple(eb + Vector((sx * 0.16, 0.02, 0))), tuple(et)], [0.025, 0.01], segments=4),
                    H, "bone_shade", **HEAD)
        # Dents : canines fines et longues, prémolaires
        can = Vector((s * 0.08, -1.35, -0.14))
        rig.add(mr.tooth(f"Canine{s}", can, can + Vector((0, -0.02, -0.22)), 0.07, 0.05, Vector((s, -0.3, 0)), curl=0.12), H,
                "tooth", **HEAD)
        for k in range(4):
            y = -1.15 + 0.17 * k
            xx = s * a.side_width(SKULL, y, -0.17) * 0.85
            size = 0.12 if k == 2 else 0.07
            rig.add(mr.tooth(f"UpTooth{s}{k}", (xx, y, -0.17), (xx, y, -0.17 - size), size * 0.7, size * 0.4, Vector((s, 0, 0)),
                             curl=0.05), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * a.side_width(SKULL, y, -0.17) * 0.75, y, -0.15) for y in (-1.4, -1.0, -0.6)],
                       0.02, segments=4), H, "gum", **HEAD)
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = a.smooth_path([(s * HINGE[0], HINGE[1], HINGE[2]), (s * 0.2, -0.7, -0.21), (s * 0.12, -1.15, -0.21),
                              (s * 0.05, -1.45, -0.19)], 6)
        rig.add(a.band(f"Mandible{s}", line, [0.2, 0.14, 0.11, 0.1, 0.1, 0.08], [0.05, 0.045, 0.04, 0.04, 0.035, 0.03],
                       offset=1), J, "bone", **HEAD)
        rig.add(a.claw(f"Coronoid{s}", line[0] + Vector((0, -0.06, 0)), (0, -0.2, 1), 0.17, 0.035, curl=0.2, segments=4), J,
                "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.04, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"JawMark{s}", [tuple(p + Vector((s * 0.02, 0, -0.04))) for p in line[1:4]], 0.012, segments=4), J,
                "lacquer", **HEAD)
        can = mr.along(line, 0.86) + Vector((-s * 0.02, 0, 0))
        rig.add(mr.tooth(f"LowCanine{s}", can, can + Vector((0, -0.02, 0.18)), 0.06, 0.045, Vector((s, -0.3, 0)), curl=0.12),
                J, "tooth", **HEAD)
        for k in range(3):
            p = mr.along(line, 0.35 + 0.15 * k) + Vector((-s * 0.02, 0, 0))
            rig.add(mr.tooth(f"LowTooth{s}{k}", p, p + Vector((0, 0, 0.08)), 0.06, 0.035, Vector((s, 0, 0)), curl=0.05), J,
                    "tooth", **HEAD)
    rig.add(r.ico("Chin", 0.05, subdivisions=2, location=(0, -1.45, -0.27), scale=(1.3, 1, 0.8)), J, "bone", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Throat", 0.07, subdivisions=2, location=(0, -0.6, -0.18), scale=(1.2, 3, 0.6)), H, "glow", glow=True)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps, shimenawa

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        bone = "Hips" if i < 7 else "Chest"
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.2, spine=1.0, lean=0.45), bone, "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.2), bone, "disc")
    for i in range(len(NECK)):
        t = tangent(NECK, i)
        rig.add(a.vertebra(f"NeckVert{i}", NECK[i], t, 0.17, spine=0.8, lean=0.3), "Neck", "bone")
        if i < len(NECK) - 1:
            rig.add(a.disc(f"NeckDisc{i}", NECK[i].lerp(NECK[i + 1], 0.5), t, 0.17), "Neck", "disc")
    sternum = []
    for k, i in enumerate(range(4, n - 1)):
        f = k / (n - 6)
        hw = 0.42 + 0.12 * math.sin(math.pi * f)
        depth = 0.55 + 0.4 * f
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.045), "Hips" if i < 7 else "Chest", "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[::2], 0.07, 0.4), "Chest", "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.42), (0.1, 0.3), (-0.1, 0.32))):
        rig.add(a.crystal(f"FoxHeart{k}", (dx, -0.3, 2.6), 0.08 if k == 0 else 0.055, h, sides=5), "Chest", "glow", glow=True)
    for s in (-1, 1):
        sh = leg("Front", s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[-3] + Vector((s * 0.2, 0.2, 0.12)), sh, 0.32, 0.05, width_end=0.16,
                        normal=(s, 0, 0.3)), "Chest", "bone")
        rig.add(r.tube(f"ScapulaMark{s}", [tuple(SPINE[-3].lerp(sh, 0.25) + Vector((s * 0.27, 0.2, 0.1))),
                                           tuple(SPINE[-3].lerp(sh, 0.8) + Vector((s * 0.09, 0.05, 0)))], 0.018, segments=4),
                "Chest", "lacquer")
        hp = leg("Hind", s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[2] + Vector((s * 0.15, -0.2, 0.05)), hp + Vector((s * 0.05, 0, 0.1)), 0.32, 0.05,
                        width_end=0.22, normal=(s, 0, 0.5)), "Hips", "bone")
    # Shimenawa : corde sacrée tressée de deux brins, papiers shide en zigzag, clochette suzu
    cc, t = NECK[2], tangent(NECK, 2)
    side, up = a._basis(t)
    for k in range(2):
        pts = [tuple(cc + (side * math.cos(an) + up * math.sin(an)) * (0.27 + 0.04 * math.cos(3 * an + k * math.pi))
                     + t * 0.04 * math.sin(3 * an + k * math.pi))
               for an in (2 * math.pi * j / 24 for j in range(24))]
        rig.add(r.tube(f"Shimenawa{k}", pts, 0.045, segments=5, closed=True), "Neck", "rope")
    for k, ang in enumerate((-2.2, -1.75, -1.4, -0.95)):
        top_ = cc + (side * math.cos(ang) + up * math.sin(ang)) * 0.3
        for j in range(3):
            a_ = top_ + Vector((0.04 * (j % 2) - 0.02, 0, -0.13 * j))
            rig.add(r.box(f"Shide{k}{j}", (0.09, 0.015, 0.13), location=a_ + Vector((0, -0.02, -0.07))), "Neck", "paper")
    bell_top = cc - up * 0.32
    rig.add(r.tube("BellCord", [tuple(bell_top), tuple(bell_top + Vector((0, -0.02, -0.12)))], 0.015, segments=4), "Neck",
            "lacquer")
    rig.add(r.ico("Suzu", 0.08, subdivisions=2, location=bell_top + Vector((0, -0.02, -0.2))), "Neck", "gold")
    rig.add(r.box("SuzuSlit", (0.12, 0.02, 0.012), location=bell_top + Vector((0, -0.09, -0.22))), "Neck", "ink")


def build_tails(rig):
    for k in range(9):
        path = tail_path(k)
        n = len(path)
        for i in range(n):
            t = tangent(path, i)
            side, up = a._basis(t)
            bone = f"Tail{k + 1}_{1 if i < 7 else 2}"
            size = 0.13 - 0.07 * i / (n - 1)
            rig.add(a.vertebra(f"T{k}Vert{i}", path[i], t, size, spine=0.6, lean=0.4, transverse=False), bone, "bone", **TAILS)
            if i < n - 1:
                rig.add(a.disc(f"T{k}Disc{i}", path[i].lerp(path[i + 1], 0.5), t, size), bone, "disc", **TAILS)
            # « Fourrure » d'os : lames effilées qui s'écartent, plus longues au milieu de la queue
            if i % 2 == 1 and i > 2:
                ln = 0.25 + 0.25 * math.sin(math.pi * i / n)
                for sx in (-1, 1):
                    rig.add(a.claw(f"T{k}Fur{i}{sx}", path[i], side * sx + t * 1.3 + up * 0.2, ln, 0.03, curl=-0.25,
                                   segments=4), bone, "bone" if i % 4 == 1 else "bone_shade", **TAILS)
            if i == n // 2:
                rig.add(a.ring_around(f"T{k}Band", path[i], t, size * 1.25, 0.02, segments=8), bone, "lacquer", **TAILS)
        tip, t = path[-1], tangent(path, n - 1)
        bone = f"Tail{k + 1}_2"
        if k == 4:     # hoshi no tama : perle-joyau en bulbe, pointe en flamme
            rig.add(r.ico("HoshiNoTama", 0.17, subdivisions=2, location=tip + t * 0.15, scale=(1, 1, 0.9)), bone, "glow",
                    glow=True)
            rig.add(a.claw("TamaFlame", tip + t * 0.28, t + Vector((0, 0, 0.6)), 0.25, 0.08, curl=-0.3, segments=4), bone,
                    "glow", glow=True)
            rig.add(a.ring_around("TamaSetting", tip + t * 0.02, t, 0.1, 0.025, segments=8), bone, "gold", **TAILS)
        else:          # kitsunebi : flamme de renard
            for j in range(3):
                rig.add(a.claw(f"Kitsunebi{k}{j}", tip, t + Vector((0.3 * (j - 1), 0, 0.5)), 0.3 - 0.06 * abs(j - 1), 0.06,
                               curl=-0.35, segments=4), bone, "glow", glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix in ("Front", "Hind"):
            p = leg(prefix, s)
            bones = [f"{prefix}{nm}_{side}" for nm in ("Upper", "Lower", "Foot")]
            rig.add(a.long_bone(f"{prefix}Upper{s}", p[0], p[1], 0.09, segments=6), bones[0], "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower{s}", p[1], p[2], 0.065, segments=6), bones[1], "bone", **LEGS)
            rig.add(a.ring_around(f"{prefix}Mark{s}", p[1].lerp(p[2], 0.3), p[2] - p[1], 0.075, 0.018, segments=8), bones[1],
                    "lacquer", **LEGS)
            rig.add(r.ico(f"{prefix}Wrist{s}", 0.07, subdivisions=1, location=p[2]), bones[2], "bone_shade", **LEGS)
            rig.add(a.long_bone(f"{prefix}Meta{s}", p[2], p[3] + Vector((0, 0, 0.05)), 0.05, condyles=False, segments=5),
                    bones[2], "bone", **LEGS)
            for k in range(4):
                d = Vector((s * (k - 1.5) * 0.22, -1, 0)).normalized()
                toe = p[3] + d * 0.22 + Vector((0, 0, -0.04))
                rig.add(a.long_bone(f"{prefix}Toe{s}{k}", p[3] + Vector((0, 0, 0.04)), toe, 0.028, condyles=False, segments=4),
                        bones[2], "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{k}", toe, d + Vector((0, 0, -0.7)), 0.1, 0.025, curl=0.4, segments=4), bones[2],
                        "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_tails(rig)
    build_legs(rig)
    return rig
