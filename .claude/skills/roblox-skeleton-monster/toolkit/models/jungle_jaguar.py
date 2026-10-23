"""Jaguar squelette (≈ 2,6 studs au garrot, 5 de long + queue) — créature animable.
Pack « Ruines de la jungle maudite », créature 3.

Animal modèle : le jaguar (jaguar noir) — crâne **rond, large et court**, arcades
zygomatiques énormes (morsure la plus puissante des félins), grandes orbites vers l'avant,
museau court et large, canines épaisses (pas des sabres), carnassières ; corps compact et
musclé, pattes courtes, longue queue.

Identité : os noirs (jaguar noir) **tachetés de rosettes-runes dorées lumineuses** ;
pas de cornes mais des **lames d'obsidienne** sur la colonne (comme un macuahuitl) et un
collier rituel de jade et d'or ; posture de **traque**, ramassé, tête basse, queue relevée
au bout ; plumes de jade derrière les oreilles ; thème d'effets « ruins » (poussière d'or +
feuilles qui tombent).

Différences voulues avec le Tigre à dents de sabre : crâne rond et court (≠ long museau),
canines épaisses (≠ sabres), posture basse de traque (≠ debout), os noirs (≠ gris rayé).

4 pièces Roblox : corps, Head, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, Tail1-2, Front/Hind{Upper,Lower,Paw}_{L,R}, FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.forest_werewolf import vine
from models.hell_phoenix import feather
from models.jungle_gorilla import glyph

COLORS = {
    "bone": "#3a3630",
    "bone_shade": "#1e1c18",
    "tooth": "#f3ead2",
    "horn": "#0d0d10",
    "horn_tip": "#ffc23a",
    "disc": "#5a4a30",
    "obsidian": "#14121a",
    "gold": "#d9a52a",
    "jade": "#2f8f6f",
    "vane": "#2fa37a",
    "stone": "#7a7466",
    "moss": "#4f6b2a",
    "root": "#3a2a1c",
    "gum": "#5a2228",
    "ink": "#0a0908",
    "glow": "#ffc23a",
    "glow_hot": "#fff0c0",
}

EFFECT_THEME = "ruins"

TEST_POSE = {
    "Jaw": (-20, 0, 0),
    "Head": (12, 0, 0),
    "FrontUpper_L": (-30, 0, 0),
    "Tail2": (0, 0, 35),
    "Spine3": (8, 0, 0),
}

VIEW = (0.95, -0.95, 0.4)

SPINE = a.smooth_path([(0, 1.6, 2.15), (0, 0.8, 2.38), (0, 0.0, 2.42), (0, -0.7, 2.2)], 20)
NECK = a.smooth_path([(0, -0.7, 2.2), (0, -1.0, 2.07), (0, -1.22, 1.98)], 5)
TAIL = a.smooth_path([(0, 1.65, 2.15), (0, 2.4, 1.9), (0, 3.2, 1.3), (0.2, 3.9, 1.0),
                      (0.35, 4.5, 1.3), (0.3, 4.75, 1.95)], 26)
# Crâne de jaguar : rond, large, court (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-1.22, 0.42, 0.55, 0.42, 2.35, 1.7), (-1.55, 0.52, 0.7, 0.54, 2.5, 1.65),
         (-1.85, 0.48, 0.64, 0.54, 2.44, 1.65), (-2.15, 0.38, 0.48, 0.46, 2.24, 1.68),
         (-2.4, 0.34, 0.42, 0.4, 2.1, 1.7), (-2.55, 0.32, 0.38, 0.36, 2.05, 1.72)]
EYE = (-1.92, 2.2)
HINGE = (0.52, -1.55, 1.68)
GAPE = math.radians(22)        # grondement
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
CHIN = tuple(_jm @ Vector((0, -2.55, 1.66)))
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def front_leg(s):
    """Patte avant de traque : coude relevé vers l'arrière, épaule basse."""
    return (Vector((s * 0.5, -0.55, 2.0)), Vector((s * 0.64, -0.12, 1.2)),
            Vector((s * 0.6, -0.95, 0.42)), Vector((s * 0.6, -1.22, 0.12)))


def hind_leg(s):
    return (Vector((s * 0.48, 1.5, 1.95)), Vector((s * 0.62, 0.85, 1.05)),
            Vector((s * 0.62, 1.75, 0.55)), Vector((s * 0.62, 1.38, 0.12)))


def rosette(rig, name, center, normal, size, bone):
    """Rosette de jaguar devenue rune : anneau doré lumineux + point central."""
    center, normal = Vector(center), Vector(normal).normalized()
    rig.add(a.ring_around(name, center + normal * 0.01, normal, size, size * 0.22, segments=8), bone,
            "glow", glow=True)
    rig.add(r.ico(f"{name}Dot", size * 0.3, subdivisions=1, location=center + normal * 0.015,
                  scale=(1, 1, 0.5)), bone, "glow", glow=True)


def bone_rosettes(rig, name, a_pt, b_pt, radius, bone, n=2, phase=0.0):
    a_pt, b_pt = Vector(a_pt), Vector(b_pt)
    side, up = a._basis(b_pt - a_pt)
    for k in range(n):
        t = (k + 0.7) / (n + 0.4)
        ang = phase + k * 2.2
        nrm = side * math.cos(ang) + up * math.sin(ang)
        rosette(rig, f"{name}{k}", a_pt.lerp(b_pt, t) + nrm * radius, nrm, radius * 0.55, bone)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], (0, -2.6, 2.0), "Neck")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    rig.bone("Tail1", TAIL[0], TAIL[13], "Spine1")
    rig.bone("Tail2", TAIL[13], TAIL[-1], "Tail1")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Spine3"), ("Hind", hind_leg(s), "Spine1")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Paw_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
        rig.fx(f"Eye{side}", (s * 0.4, EYE[0], EYE[1]), "Head")
        rig.fx(f"Claws{side}", front_leg(s)[3] + Vector((0, -0.25, 0)), f"FrontPaw_{side}")
    rig.fx("Heart", (0, -0.1, 1.7), "Spine2")
    rig.fx("Mouth", (0, -2.3, 1.6), "Head")
    rig.fx("TailTip", TAIL[-1], "Tail2")
    rig.fx("Back", SPINE[10] + Vector((0, 0, 0.6)), "Spine2")


# ---------------------------------------------------------------- crâne

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.08, tip_length=0.15)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.17, 0.16),
                  a.hole_x((0, -1.5, 1.98), 0.22, 0.16),
                  a.hole_along((0, -2.62, 1.95), (0, 1, 0), (1, 0, 0), 0.13, 0.12, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    crest = [top(0, y) for y in (-1.22, -1.45, -1.7)]
    rig.add(a.band("Sagittal", crest, [0.16, 0.18, 0.05], 0.06, offset=0.15), H, "bone_shade",
            **HEAD)
    rig.add(a.ring_around("NasalRim", (0, -2.66, 1.95), (0, -1, 0), 0.14, 0.035, segments=10), H,
            "gold", **HEAD)
    glyph(rig, "ForeheadGlyph", top(0, -1.95) + Vector((0, 0, 0.02)), (0, -0.3, 1), 0.22, H, **HEAD)
    for k, (x, y) in enumerate(((0.3, -1.4), (-0.3, -1.45), (0.22, -2.25), (-0.22, -2.2),
                                (0.42, -1.7), (-0.42, -1.75))):
        p, nrm = hit((x, y, 9))
        if p is not None:
            rosette(rig, f"SkullRosette{k}", p, nrm if nrm.z > 0 else -nrm, 0.07, H)
    for s in (-1, 1):
        # Grandes orbites vers l'avant, œil doré, arcade
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.12, subdivisions=2, location=c0 - Vector((s * 0.07, 0, 0))), H,
                "glow", glow=True)
        rig.add(r.ico(f"Pupil{s}", 0.05, subdivisions=1, location=c0 + Vector((s * 0.0, -0.08, 0)),
                      scale=(0.5, 0.5, 1.6)), H, "ink", **HEAD)
        rig.add(a.ring_around(f"OrbitRim{s}", c0, (s, -0.7, 0), 0.17, 0.04, segments=10), H,
                "bone_shade", **HEAD)
        # Arcades zygomatiques énormes (signature : morsure)
        zyg = a.smooth_path([(s * 0.5, -1.35, 1.78), (s * 0.92, -1.75, 1.82), (s * 0.52, -2.15, 1.85)], 5)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg], [0.08, 0.12, 0.13, 0.11, 0.08],
                       segments=6), H, "bone", **HEAD)
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.38, -1.75, 2.42), (s * 0.62, -1.8, 2.05)], 0.045,
                       segments=4), H, "bone_shade", **HEAD)
        # Plumes de jade derrière les oreilles, ornement d'oreille en or
        ear = Vector((s * 0.6, -1.35, 2.2))
        rig.add(a.ring_around(f"EarGold{s}", ear, (s, 0, 0), 0.1, 0.035, segments=10), H, "gold",
                **HEAD)
        for k in range(2):
            feather(rig, f"EarFeather{s}{k}", ear, ear + Vector((s * 0.35, 0.35 + 0.15 * k, 0.4 - 0.2 * k)),
                    0.14, H, flame=False, **HEAD)
        for k in range(5):
            y = -2.3 - 0.05 * k
            rig.add(r.ico(f"Whisker{s}{k}", 0.025, subdivisions=1,
                          location=(s * a.side_width(SKULL, y, 1.9 + 0.04 * (k % 2)) * 1.02, y,
                                    1.9 + 0.04 * (k % 2))), H, "gold", **HEAD)
        # Rangée du haut : incisives, canine épaisse, carnassières
        for k in range(3):
            p = Vector((s * (0.06 + 0.07 * k), -2.56 + 0.03 * k, 1.7))
            rig.add(mr.tooth(f"UpIncisor{s}{k}", p, p + Vector((0, -0.02, -0.13)), 0.07, 0.05,
                             Vector((s * 0.3, -1, 0))), H, "tooth", **HEAD)
        p = Vector((s * 0.3, -2.38, 1.69))
        rig.add(mr.tooth(f"UpCanine{s}", p, p + Vector((s * 0.02, -0.04, -0.45)), 0.18, 0.14,
                         Vector((s, -0.5, 0)), curl=0.12), H, "tooth", **HEAD)
        for k, (y, size, w) in enumerate(((-2.15, 0.12, 0.12), (-1.92, 0.18, 0.2))):
            p = Vector((s * a.side_width(SKULL, y, 1.7) * 0.85, y, 1.68))
            rig.add(mr.tooth(f"Carnassial{s}{k}", p, p + Vector((0, 0, -size)), w, w * 0.45,
                             Vector((s, 0, 0))), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * 0.18, -2.52, 1.71), (s * 0.34, -2.2, 1.7),
                                        (s * 0.46, -1.8, 1.69)], 0.04, segments=4), H, "gum", **HEAD)
    # Mandibule (modélisée fermée, puis ouverte autour de la charnière)
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.45, -1.95, 1.66)),
                Vector((s * 0.3, -2.3, 1.66)), Vector((s * 0.1, -2.55, 1.66))]
        hs = [0.34, 0.31, 0.29, 0.29]
        rig.add(a.band(f"Dentary{s}", line, hs, [0.14, 0.13, 0.12, 0.12], offset=1), J, "bone",
                **HEAD)
        rig.add(r.tube(f"DentaryBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.035, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.12, 0)),
                        line[0] + Vector((0, -0.03, 0.32)), 0.2, 0.07, width_end=0.1,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        p = mr.along(line, 0.85)
        rig.add(mr.tooth(f"LowCanine{s}", p, p + Vector((s * 0.02, -0.03, 0.36)), 0.16, 0.12,
                         Vector((s, -0.5, 0)), curl=0.12), J, "tooth", **HEAD)
        for k, (t, size) in enumerate(((0.35, 0.16), (0.55, 0.12))):
            q = mr.along(line, t)
            rig.add(mr.tooth(f"LowCarn{s}{k}", q, q + Vector((0, 0, size)), size, size * 0.45,
                             Vector((s, 0, 0))), J, "tooth", **HEAD)
        for k in range(3):
            q = line[3] + Vector((-s * 0.03 * k, -0.01, 0))
            rig.add(mr.tooth(f"LowIncisor{s}{k}", q, q + Vector((0, -0.03, 0.11)), 0.06, 0.04,
                             Vector((s * 0.3, -1, 0))), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.03, 0, 0.015))) for p in line[1:]],
                       0.035, segments=4), J, "gum", **HEAD)
        rosette(rig, f"JawRosette{s}", mr.along(line, 0.5) + Vector((s * 0.08, 0, -0.15)), (s, 0, 0),
                0.07, J)
    rig.add(r.ico("ChinGold", 0.07, subdivisions=1, location=(0, -2.58, 1.42)), J, "gold", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Throat", 0.17, subdivisions=2, location=(0, -1.95, 1.62), scale=(1.4, 1.6, 0.6)),
            H, "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for path, bonef, size in ((SPINE, spine_bone, 0.24), (NECK, lambda i: "Neck", 0.21)):
        for i in range(len(path)):
            t = tangent(path, i)
            rig.add(a.vertebra(f"Vert{size}{i}", path[i], t, size, spine=1.3, lean=0.45),
                    bonef(i), "bone")
            if i < len(path) - 1:
                rig.add(a.disc(f"Disc{size}{i}", path[i].lerp(path[i + 1], 0.5), t, size),
                        bonef(i), "disc")
            # Lames d'obsidienne sur la colonne (macuahuitl), une sur deux
            if path is SPINE and i % 2 == 1:
                side, up = a._basis(t)
                rig.add(a.blade(f"Obsidian{i}", path[i] + up * size * 1.5,
                                path[i] + up * size * 3.2 - t * 0.12, 0.14, 0.03, width_end=0.02,
                                normal=side, bevel=0), bonef(i), "obsidian")
            if path is SPINE and i % 3 == 0:
                side, up = a._basis(t)
                for sd in (-1, 1):
                    rosette(rig, f"SpineRosette{i}{sd}", path[i] + side * sd * 0.26 + up * 0.12,
                            side * sd + up * 0.5, 0.06, bonef(i))
    sternum = []
    for k, i in enumerate(range(6, 18)):
        hw = 0.6 + 0.22 * math.sin(math.pi * k / 11)
        depth = 0.75 + 0.35 * math.sin(math.pi * (k + 2) / 14)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.06),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[1:-1:2], 0.08, 0.36), "Spine2", "bone_shade")
    # Cœur : soleil d'or (glyphe solaire) qui brille dans la cage
    rig.add(a.ring_around("SunHeart", (0, -0.1, 1.7), (0, 1, 0), 0.18, 0.05, segments=12), "Spine2",
            "gold")
    rig.add(r.ico("HeartGlow", 0.13, subdivisions=2, location=(0, -0.1, 1.7)), "Spine2", "glow",
            glow=True)
    for k in range(8):
        ang = 2 * math.pi * k / 8
        d = Vector((math.cos(ang), 0, math.sin(ang)))
        rig.add(a.claw(f"SunRay{k}", Vector((0, -0.1, 1.7)) + d * 0.2, d, 0.14, 0.03, curl=0,
                       segments=4), "Spine2", "gold")
    rig.add(r.tube("HeartHang", [tuple(SPINE[10] + Vector((0, 0, -0.1))), (0, -0.1, 1.9)], 0.025,
                   segments=4), "Spine2", "root")
    # Collier rituel de jade et d'or autour du cou
    cc, ct = NECK[2], tangent(NECK, 2)
    rig.add(a.ring_around("Collar", cc, ct, 0.32, 0.06, segments=14), "Neck", "gold")
    side, up = a._basis(ct)
    for k in range(9):
        ang = math.pi * (0.1 + 0.8 * k / 8) + math.pi
        p = cc + (side * math.cos(ang) + up * math.sin(ang)) * 0.36
        rig.add(r.ico(f"JadeBead{k}", 0.065, subdivisions=1, location=p), "Neck", "jade")
    rig.add(r.box("CollarPlaque", (0.2, 0.06, 0.24), location=tuple(cc - up * 0.42 - ct * 0.05)), "Neck",
            "gold")
    # Ceintures
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[16] + Vector((s * 0.22, 0.1, 0.08)),
                        sh + Vector((0, 0.04, 0.04)), 0.45, 0.07, width_end=0.22, mid=0.5,
                        normal=(s, 0, 0.4)), "Spine3", "bone")
        rosette(rig, f"ScapulaRosette{s}", SPINE[16].lerp(sh, 0.5) + Vector((s * 0.06, 0.05, 0.08)),
                (s, 0, 0.6), 0.08, "Spine3")
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.12, 0, 0.05)),
                        hp + Vector((s * 0.12, -0.25, 0.35)), 0.38, 0.06, width_end=0.3,
                        normal=(s, 0, 0.4)), "Spine1", "bone")
        rig.add(r.tube(f"Ischium{s}", [tuple(hp), (s * 0.22, 1.85, 1.75)], [0.06, 0.04], segments=5),
                "Spine1", "bone_shade")
    # Longue queue, relevée au bout, rosettes et touffe de plumes de jade
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        size = 0.14 - 0.08 * i / (nt - 1)
        bone = "Tail1" if i < 13 else "Tail2"
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=0.8, transverse=i < 6), bone,
                "bone")
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc")
        if i % 4 == 2:
            rig.add(a.ring_around(f"TailRune{i}", TAIL[i], t, size * 1.05, size * 0.25, segments=8),
                    bone, "glow", glow=True)
    for k in range(3):
        d = (tangent(TAIL, nt - 1) + Vector((0.3 * (k - 1), 0, 0.3))).normalized()
        feather(rig, f"TailFeather{k}", TAIL[-1], TAIL[-1] + d * 0.5, 0.14, "Tail2", flame=False)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts in (("Front", front_leg(s)), ("Hind", hind_leg(s))):
            ub, lb, pb = f"{prefix}Upper_{side}", f"{prefix}Lower_{side}", f"{prefix}Paw_{side}"
            big = 1.2 if prefix == "Front" else 1.0
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.12 * big, segments=7), ub,
                    "bone", **LEGS)
            bone_rosettes(rig, f"{prefix}UpRos{s}", pts[0], pts[1], 0.12 * big, ub, phase=s)
            off = (pts[2] - pts[1]).cross(Vector((0, 0, 1))).normalized() * 0.07
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1] + off, pts[2] + off, 0.09 * big,
                                condyles=False, segments=6), lb, "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] - off, pts[2] - off, 0.07 * big,
                                condyles=False, segments=6), lb, "bone_shade", **LEGS)
            bone_rosettes(rig, f"{prefix}LowRos{s}", pts[1], pts[2], 0.13 * big, lb, phase=1 + s)
            vine(rig, f"{prefix}Vine{s}", pts[1], pts[2], 0.13 * big, lb, turns=1.2, phase=s, **LEGS)
            rig.add(a.ring_around(f"{prefix}Anklet{s}", pts[2].lerp(pts[1], 0.15), pts[1] - pts[2],
                                  0.13 * big, 0.04, segments=10), lb, "gold", **LEGS)
            rig.add(r.ico(f"{prefix}Wrist{s}", 0.1 * big, subdivisions=1, location=pts[2]), pb,
                    "bone_shade", **LEGS)
            # Larges pattes rondes de jaguar : 4 doigts, griffes d'obsidienne sorties
            lat = Vector((s, 0, 0))
            for j in range(4):
                off_j = (j - 1.5) * 0.11 * big
                m1 = pts[3] + lat * off_j
                rig.add(a.long_bone(f"{prefix}Meta{s}{j}", pts[2] + lat * off_j * 0.5, m1, 0.045,
                                    condyles=False, segments=5), pb, "bone", **LEGS)
                toe = m1 + Vector((lat.x * off_j * 0.3, -0.22, -0.04))
                rig.add(a.long_bone(f"{prefix}Toe{s}{j}", m1, toe, 0.04, condyles=False, segments=5),
                        pb, "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{j}", toe, (0, -1, -0.8), 0.22 * big, 0.045,
                               curl=0.5, segments=4), pb, "obsidian", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
