"""Mante religieuse géante squelette (mante orchidée, ≈ 4,5 studs de haut) — animable.
Pack « Ruines de la jungle maudite », créature 4.

Animal modèle : la mante orchidée — tête triangulaire très mobile, deux énormes **yeux
composés**, trois ocelles, longues antennes, mandibules dentées ; prothorax allongé en cou ;
**pattes ravisseuses (bras-faux)** repliées « en prière », fémur et tibia hérissés de deux
rangées d'épines, crochet terminal ; pattes marcheuses aux **lobes en pétales** ; ailes en
feuilles nervurées ; abdomen segmenté.

Identité : exosquelette ajouré blanc rosé (orchidée), lobes et ailes en pétales roses ;
pas de cornes mais les bras-faux épineux et une crête de pétales ; dressée, ailes levées en
parade d'intimidation ; glyphes mayas, bagues d'or et lianes ; cœur-pollen lumineux ;
thème d'effets « orchid » (pollen + pétales).

5 pièces Roblox : corps, Head, Arms, Legs, Wings, + lumineux.
Os : Root, Abdomen1-2, Thorax, Prothorax, Head, Jaw, Arm_{L,R}_1-3, Leg{1,2}_{L,R}_1-2,
Wing_{L,R}, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.forest_werewolf import vine
from models.jungle_gorilla import glyph

COLORS = {
    "bone": "#f0dde6",
    "bone_shade": "#9a6f86",
    "tooth": "#fff8ee",
    "horn": "#3a1e30",
    "horn_tip": "#ff4fd8",
    "disc": "#6a3a58",
    "petal": "#f2a6d2",
    "membrane": "#e98fc4",
    "gold": "#d9a52a",
    "stone": "#7a7466",
    "jade": "#2f8f6f",
    "moss": "#4f6b2a",
    "root": "#3a2a1c",
    "ink": "#1a0a14",
    "glow": "#ff4fd8",
    "glow_hot": "#ffe0f6",
}

EFFECT_THEME = "orchid"

TEST_POSE = {
    "Jaw": (-15, 0, 0),
    "Head": (0, 0, 25),
    "Arm_L_2": (-45, 0, 0),
    "Arm_L_3": (40, 0, 0),
    "Wing_R": (0, 25, 0),
}

VIEW = (0.9, -1.0, 0.35)

ABDOMEN = a.smooth_path([(0, 0.55, 1.65), (0, 1.3, 1.55), (0, 2.1, 1.35), (0, 2.8, 1.15),
                         (0, 3.25, 1.1)], 9)
PROTHORAX = a.smooth_path([(0, 0.35, 1.8), (0, 0.05, 2.35), (0, -0.3, 3.0), (0, -0.55, 3.55)], 8)
HEAD_C = Vector((0, -0.75, 3.8))
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")
WINGS = dict(part="Wings")
# Tête triangulaire : large en haut, pointue en bas (y, demi-larg. dessus, milieu, bas, z haut, z bas)
SKULL = [(-0.55, 0.42, 0.45, 0.1, 4.12, 3.45), (-0.78, 0.5, 0.52, 0.12, 4.18, 3.38),
         (-0.95, 0.38, 0.4, 0.09, 4.1, 3.45)]


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def arm_points(s):
    """Patte ravisseuse repliée en prière : fémur levé, tibia rabattu, crochet."""
    return (Vector((s * 0.15, -0.35, 3.05)), Vector((s * 0.3, -0.75, 2.6)),
            Vector((s * 0.32, -1.4, 3.45)), Vector((s * 0.27, -0.95, 2.7)))


def leg_points(k, s):
    if k == 1:
        return Vector((s * 0.18, 0.3, 1.72)), Vector((s * 1.3, -0.05, 2.35)), Vector((s * 1.95, -0.45, 0.02))
    return Vector((s * 0.18, 0.65, 1.68)), Vector((s * 1.4, 1.35, 2.25)), Vector((s * 2.05, 2.25, 0.02))


def spine_row(rig, name, a_pt, b_pt, out, n, size, bone, **kw):
    """Rangée d'épines pleines le long d'un segment de bras-faux."""
    a_pt, b_pt, out = Vector(a_pt), Vector(b_pt), Vector(out).normalized()
    for k in range(n):
        t = 0.12 + 0.76 * k / max(1, n - 1)
        p = a_pt.lerp(b_pt, t)
        sz = size * (1.4 if k % 3 == 0 else 1.0)
        rig.add(mr.tooth(f"{name}{k}", p, p + out * sz + (b_pt - a_pt).normalized() * sz * 0.3,
                         sz * 0.45, sz * 0.3, (b_pt - a_pt).normalized(), curl=0.15), bone, "tooth",
                **kw)


def petal(rig, name, base, tip, width, bone, **kw):
    """Lobe en pétale d'orchidée (lame large et arrondie) + nervure."""
    base, tip = Vector(base), Vector(tip)
    d = tip - base
    side, up = a._basis(d)
    rig.add(a.blade(name, base, tip, width * 0.5, 0.03, width_end=width * 0.35, mid=width,
                    normal=up, bevel=0), bone, "petal", **kw)
    rig.add(r.tube(f"{name}Vein", [tuple(base), tuple(base.lerp(tip, 0.9))], 0.015, segments=4),
            bone, "bone_shade", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Thorax", (0, 0.6, 1.7), (0, 0.3, 1.8), "Root")
    rig.bone("Abdomen1", ABDOMEN[0], ABDOMEN[4], "Thorax")
    rig.bone("Abdomen2", ABDOMEN[4], ABDOMEN[-1], "Abdomen1")
    rig.bone("Prothorax", PROTHORAX[0], PROTHORAX[-1], "Thorax")
    rig.bone("Head", PROTHORAX[-1], HEAD_C + Vector((0, -0.3, -0.2)), "Prothorax")
    rig.bone("Jaw", (0, -0.85, 3.45), (0, -0.95, 3.2), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        cx, fe, ti, cl = arm_points(s)
        rig.bone(f"Arm_{side}_1", cx, fe, "Prothorax")
        rig.bone(f"Arm_{side}_2", fe, ti, f"Arm_{side}_1")
        rig.bone(f"Arm_{side}_3", ti, cl, f"Arm_{side}_2")
        for k in (1, 2):
            root, knee, foot = leg_points(k, s)
            rig.bone(f"Leg{k}_{side}_1", root, knee, "Thorax")
            rig.bone(f"Leg{k}_{side}_2", knee, foot, f"Leg{k}_{side}_1")
        rig.bone(f"Wing_{side}", (s * 0.15, 0.4, 1.95), (s * 0.9, 1.6, 3.4), "Thorax")
        rig.fx(f"Eye{side}", (s * 0.52, -0.8, 4.05), "Head")
        rig.fx(f"Scythe{side}", arm_points(s)[2], f"Arm_{side}_2")
    rig.fx("Heart", (0, 1.4, 1.5), "Abdomen1")
    rig.fx("Mouth", (0, -0.95, 3.3), "Head")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("HeadShell", SKULL, droop=0.0, tip_length=0.12)
    a.cut(skull, [a.hole_along((0, -0.95, 3.8), (0, 1, 0), (1, 0, 0), 0.12, 0.16, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)
    rig.add(a.ring_around("FrontRim", (0, -0.98, 3.8), (0, -1, 0), 0.16, 0.03, segments=10), H,
            "bone_shade", **HEAD)
    for s in (-1, 1):
        # Yeux composés géants (dôme lumineux + facettes), cerclés d'or
        eye = Vector((s * 0.5, -0.78, 4.02))
        rig.add(r.ico(f"Eye{s}", 0.23, subdivisions=2, location=eye, scale=(0.85, 1, 1.15)), H,
                "glow", glow=True)
        # Pseudo-pupille sombre (comme une vraie mante), orientée vers l'avant
        pupil = r.ico(f"Pupil{s}", 0.07, subdivisions=2, location=eye + Vector((s * 0.1, -0.15, 0.0)),
                      scale=(0.6, 0.6, 1.0))
        pupil["float_ok"] = True           # posée sur l'œil lumineux
        rig.add(pupil, H, "ink", **HEAD)
        rig.add(r.ico(f"EyeCup{s}", 0.2, subdivisions=2, location=eye - Vector((s * 0.1, 0, 0)),
                      scale=(0.7, 1, 1.1)), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"EyeRim{s}", eye + Vector((-s * 0.08, 0, 0)), (s, 0, 0), 0.22, 0.03,
                              segments=12), H, "gold", **HEAD)
        # Longues antennes annelées
        ant = a.smooth_path([(s * 0.12, -0.92, 4.15), (s * 0.3, -1.3, 4.7), (s * 0.7, -1.4, 5.3),
                             (s * 1.2, -1.0, 5.6)], 9)
        rig.add(r.tube(f"Antenna{s}", [tuple(p) for p in ant], [0.04 - 0.003 * i for i in range(9)],
                       segments=4), H, "bone_shade", **HEAD)
        for k in (2, 5):
            rig.add(a.ring_around(f"AntRing{s}{k}", ant[k], ant[k + 1] - ant[k], 0.045, 0.015,
                                  segments=6), H, "gold", **HEAD)
        rig.add(r.ico(f"AntTip{s}", 0.04, subdivisions=1, location=ant[-1]), H, "glow", glow=True)
        # Pétale de crête au sommet de la tête (vertex de la mante orchidée)
        petal(rig, f"CrownPetal{s}", (s * 0.15, -0.72, 4.15), (s * 0.35, -0.6, 4.55), 0.22, H,
              **HEAD)
        # Mandibules dentées + palpes maxillaires
        base = Vector((s * 0.12, -0.9, 3.42))
        rig.add(r.tube(f"Mandible{s}", [tuple(base), tuple(base + Vector((-s * 0.1, -0.12, -0.18)))],
                       [0.06, 0.03], segments=6), J, "bone_shade", **HEAD)
        for k in range(3):
            p = base + Vector((-s * 0.03 * k, -0.04 * k, -0.06 * k))
            rig.add(mr.tooth(f"MandTooth{s}{k}", p, p + Vector((-s * 0.12, -0.03, 0)), 0.06, 0.03,
                             Vector((0, -1, 0))), J, "tooth", **HEAD)
        palp = [base + Vector((s * 0.08, 0, 0)), base + Vector((s * 0.15, -0.12, -0.15)),
                base + Vector((s * 0.12, -0.1, -0.32))]
        rig.add(r.tube(f"Palp{s}", [tuple(p) for p in palp], [0.03, 0.025, 0.02], segments=4), J,
                "bone", **HEAD)
    for k, x in enumerate((-0.08, 0.0, 0.08)):    # trois ocelles
        rig.add(r.ico(f"Ocellus{k}", 0.035, subdivisions=1,
                      location=(x, -0.97, 4.0 + (0.05 if k == 1 else 0))), H, "glow", glow=True)
    glyph(rig, "FaceGlyph", (0, -0.98, 3.62), (0, -1, 0), 0.14, H, **HEAD)


# ---------------------------------------------------------------- corps

def build_body(rig):
    # Prothorax en cou annelé ajouré
    for i in range(len(PROTHORAX)):
        t = tangent(PROTHORAX, i)
        rig.add(a.ring_around(f"ProRing{i}", PROTHORAX[i], t, 0.14 - 0.008 * i, 0.04, segments=8),
                "Prothorax", "bone")
        if i % 2 == 0:
            side, up = a._basis(t)
            for sd in (-1, 1):
                rig.add(a.claw(f"ProSpine{i}{sd}", PROTHORAX[i] + side * sd * 0.12, side * sd + up * 0.3,
                               0.12, 0.025, curl=0, segments=4), "Prothorax", "bone_shade")
    rig.add(r.tube("ProCore", [tuple(p) for p in PROTHORAX], 0.05, segments=5), "Prothorax",
            "bone_shade")
    glyph(rig, "ProGlyph", PROTHORAX[3] + Vector((0, -0.14, 0.02)), (0, -1, 0.3), 0.16, "Prothorax")
    # Thorax : plaques ajourées
    rig.add(r.ico("Mesothorax", 0.3, subdivisions=2, location=(0, 0.45, 1.72), scale=(1, 1.3, 0.8)),
            "Thorax", "bone")
    rig.add(a.ring_around("ThoraxRim", (0, 0.45, 1.72), (0, 1, 0), 0.32, 0.05, segments=12), "Thorax",
            "bone_shade")
    # Abdomen segmenté : tergites en anneaux ouverts + cœur-pollen à l'intérieur
    for i in range(len(ABDOMEN)):
        t = tangent(ABDOMEN, i)
        side, up = a._basis(t)
        rad = 0.32 + 0.12 * math.sin(math.pi * i / (len(ABDOMEN) - 1)) - 0.02 * i
        bone = "Abdomen1" if i < 4 else "Abdomen2"
        rig.add(a.ring_around(f"Tergite{i}", ABDOMEN[i], t, rad, 0.05, segments=12), bone, "bone")
        rig.add(a.blade(f"TergitePlate{i}", ABDOMEN[i] + up * rad * 0.8 - t * 0.12,
                        ABDOMEN[i] + up * rad * 0.8 + t * 0.12, rad * 1.4, 0.04, width_end=rad * 1.2,
                        normal=up, bevel=0), bone, "bone_shade")
        if i % 2 == 1:
            for sd in (-1, 1):
                rig.add(r.ico(f"Spiracle{i}{sd}", 0.03, subdivisions=1,
                              location=ABDOMEN[i] + side * sd * rad), bone, "ink")
    rig.add(r.tube("AbdomenCore", [tuple(p) for p in ABDOMEN], 0.06, segments=5), "Abdomen1",
            "bone_shade")
    rig.add(r.ico("PollenHeart", 0.2, subdivisions=2, location=(0, 1.4, 1.5)), "Abdomen1", "glow",
            glow=True)
    for s in (-1, 1):
        rig.add(a.claw(f"Cercus{s}", ABDOMEN[-1], (s * 0.3, 1, -0.2), 0.3, 0.03, curl=0.1,
                       segments=4), "Abdomen2", "bone_shade")
    rig.add(r.ico("AbdomenMoss", 0.1, subdivisions=1, location=ABDOMEN[5] + Vector((0.1, 0, 0.42)),
                  scale=(1.4, 1.2, 0.4)), "Abdomen2", "moss")


def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        cx, fe, ti, cl = arm_points(s)
        b1, b2, b3 = f"Arm_{side}_1", f"Arm_{side}_2", f"Arm_{side}_3"
        rig.add(a.long_bone(f"Coxa{s}", cx, fe, 0.07, condyles=False, segments=6), b1, "bone",
                **ARMS)
        # Fémur ravisseur : lame large aplatie + 2 rangées d'épines vers l'intérieur-bas
        rig.add(a.band(f"Femur{s}", [fe, fe.lerp(ti, 0.5), ti], [0.16, 0.24, 0.12],
                       [0.08, 0.09, 0.07], up=(0, 0.6, -1), offset=0.5), b2, "bone", **ARMS)
        rig.add(r.tube(f"FemurRidge{s}", [tuple(fe), tuple(ti)], 0.035, segments=4), b2,
                "bone_shade", **ARMS)
        spine_row(rig, f"FemurSpineA{s}", fe, ti, (0, 0.6, -1), 6, 0.14, b2, **ARMS)
        spine_row(rig, f"FemurSpineB{s}", fe + Vector((s * 0.05, 0, 0)), ti + Vector((s * 0.05, 0, 0)),
                  (s * 0.6, 0.5, -1), 4, 0.1, b2, **ARMS)
        rig.add(a.ring_around(f"FemurGold{s}", fe.lerp(ti, 0.25), ti - fe, 0.1, 0.025, segments=8),
                b2, "gold", **ARMS)
        rig.add(r.ico(f"Knee{s}", 0.08, subdivisions=1, location=ti), b3, "bone_shade", **ARMS)
        # Tibia-faux rabattu, dents, crochet terminal
        rig.add(a.band(f"Tibia{s}", [ti, ti.lerp(cl, 0.5), cl], [0.12, 0.1, 0.06], 0.06,
                       up=(0, -0.6, -1), offset=0.5), b3, "bone", **ARMS)
        spine_row(rig, f"TibiaSpine{s}", ti, cl, (0, -0.4, 1), 5, 0.1, b3, **ARMS)
        rig.add(a.claw(f"Hook{s}", cl, (cl - ti) + Vector((0, 0, -0.3)), 0.3, 0.05, curl=0.6,
                       segments=5), b3, "horn", **ARMS)
        rig.add(r.ico(f"ScytheGlow{s}", 0.04, subdivisions=1, location=ti.lerp(fe, 0.5)), b2, "glow",
                glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in (1, 2):
            root, knee, foot = leg_points(k, s)
            b1, b2 = f"Leg{k}_{side}_1", f"Leg{k}_{side}_2"
            rig.add(a.long_bone(f"Leg{k}Femur{s}", root, knee, 0.06, knob=1.4, condyles=False,
                                segments=6), b1, "bone", **LEGS)
            rig.add(a.long_bone(f"Leg{k}Tibia{s}", knee, foot + Vector((0, 0, 0.12)), 0.045,
                                knob=1.4, condyles=False, segments=5), b2, "bone", **LEGS)
            rig.add(a.claw(f"Leg{k}Tarsus{s}", foot + Vector((0, 0, 0.12)), (0, -0.4 if k == 1 else 0.4, -1),
                           0.16, 0.03, curl=0.3, segments=4), b2, "horn", **LEGS)
            # Lobes en pétales d'orchidée sur le fémur (signature)
            mid = root.lerp(knee, 0.55)
            out = Vector((s, 0.1 if k == 2 else -0.1, -0.2)).normalized()
            petal(rig, f"Leg{k}Petal{s}", mid, mid + out * 0.55 + Vector((0, 0, -0.2)), 0.32, b1,
                  **LEGS)
            rig.add(a.ring_around(f"Leg{k}Gold{s}", knee.lerp(foot, 0.2), foot - knee, 0.06, 0.02,
                                  segments=8), b2, "gold", **LEGS)
            rig.add(r.ico(f"Leg{k}KneeGlow{s}", 0.05, subdivisions=1, location=knee), b2, "glow",
                    glow=True)
            if k == 2:
                vine(rig, f"Leg{k}Vine{s}", knee, foot + Vector((0, 0, 0.3)), 0.07, b2, turns=1.5,
                     phase=s, **LEGS)


def build_wings(rig):
    for s, side in ((1, "L"), (-1, "R")):
        bone = f"Wing_{side}"
        root = Vector((s * 0.15, 0.45, 1.95))
        # Ailes postérieures en éventail (derrière) puis élytres en feuilles (devant)
        for name, pts, color in (
                ("HindWing", [(s * 0.15, 0.6, 1.95), (s * 1.2, 1.1, 3.0), (s * 1.6, 1.9, 3.5),
                              (s * 1.3, 2.7, 3.2), (s * 0.6, 3.0, 2.4), (s * 0.15, 2.2, 1.9)], "membrane"),
                ("Tegmen", [(s * 0.12, 0.35, 1.98), (s * 0.85, 0.75, 3.1), (s * 1.0, 1.6, 3.6),
                            (s * 0.65, 2.3, 3.2), (s * 0.18, 1.6, 2.0)], "petal")):
            m = a.membrane(f"{name}{s}", [(p, {bone: 1}) for p in pts], thickness=0.03)
            rig.pal.paint(m, color)
            m["part"] = "Wings"
            for k in range(1, len(pts) - 1):
                rig.add(r.tube(f"{name}Vein{s}{k}", [tuple(root), tuple(Vector(pts[0]).lerp(Vector(pts[k]), 0.95))],
                               0.02, segments=4), bone, "bone_shade", **WINGS)
            rig.add(r.tube(f"{name}Edge{s}", [tuple(p) for p in pts[1:-1]], 0.025, segments=4), bone,
                    "bone", **WINGS)
        rig.add(r.ico(f"WingEye{s}", 0.12, subdivisions=1, location=(s * 1.05, 1.55, 3.3),
                      scale=(0.4, 1, 1)), bone, "glow", glow=True)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_arms(rig)
    build_legs(rig)
    build_wings(rig)
    return rig
