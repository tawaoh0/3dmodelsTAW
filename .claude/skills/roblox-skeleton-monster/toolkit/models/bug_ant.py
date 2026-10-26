"""Fourmi guerrière squelette (soldat Dorylus, exosquelette ajouré, ≈ 2,6 studs de haut) — animable.
Pack « Insectes géants », créature 5 (remplace la mante, déjà faite dans le pack jungle).

Animal modèle : le **soldat de fourmi magnan** (Dorylus) — tête énorme et carrée, aveugle,
**mandibules en faucille** plus longues que la tête et croisées, thorax épineux, double
pétiole en nœuds, gastre à glande acide.

Identité : chitine brun-rouge ; **aucune corne** : faucilles géantes dentées ; tête-bélier
massive, corps tendu en avant ; acide vert lumineux qui goutte des mandibules et luit dans le
gastre ; thème d'effets « acid ».

Pièces Roblox : corps, Head, Legs, + lumineux.
Os : Root, Thorax, Head, Mandible_{L,R}, Gaster, Leg{1-3}_{L,R}_{1-3}.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r
from models import _bugs as b

COLORS = {
    "chitin": "#7a3016",
    "chitin_dark": "#200b05",
    "horn": "#0b0503",
    "tooth": "#f0e4c8",
    "ink": "#050302",
    "glow": "#7dff4a",
    "glow_hot": "#e4ffd0",
}

EFFECT_THEME = "acid"

TEST_POSE = {
    "Mandible_L": (0, 0, -25),
    "Mandible_R": (0, 0, 25),
    "Head": (15, 0, 0),
    "Gaster": (-20, 0, 0),
    "Leg2_L_1": (0, 0, 20),
}

VIEW = (1.0, -0.9, 0.45)

HEAD_C = Vector((0, -1.75, 1.75))
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def leg(k, s):
    th = math.radians((-40, 5, 45)[k])
    d = Vector((s * math.cos(th), math.sin(th), 0))
    a0 = Vector((s * 0.28, -0.85 + 0.42 * k, 1.35))
    return [a0, a0 + d * 0.8 + Vector((0, 0, 0.45)), a0 + d * 1.5 + Vector((0, 0, -0.55)), a0 + d * 1.8 + Vector((0, 0, -1.3))]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Thorax", (0, 0.3, 1.5), (0, -1.0, 1.6), "Root")
    rig.bone("Head", (0, -1.0, 1.7), (0, -2.45, 1.7), "Thorax")
    rig.bone("Gaster", (0, 0.9, 1.45), (0, 2.6, 1.3), "Thorax")
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Mandible_{side}", HEAD_C + Vector((s * 0.45, -0.55, -0.15)), HEAD_C + Vector((-s * 0.3, -1.65, -0.25)), "Head")
        for k in range(3):
            p = leg(k, s)
            prev = "Thorax"
            for j in range(3):
                prev = rig.bone(f"Leg{k + 1}_{side}_{j + 1}", p[j], p[j + 1], prev)
        rig.fx(f"Acid{side}", HEAD_C + Vector((-s * 0.3, -1.7, -0.4)), f"Mandible_{side}")
        rig.fx(f"Gland{side}", HEAD_C + Vector((s * 0.45, -0.3, 0.3)), "Head")
    rig.fx("Gaster", (0, 2.6, 1.3), "Gaster")


def build_head(rig):
    H = "Head"
    for k, dy in enumerate((0.45, 0.15, -0.15, -0.45)):
        b.plate(rig, f"HeadPlate{k}", HEAD_C + Vector((0, dy, 0)), (0, 1, 0), 0.72, 0.55, 0.27, H,
                color="chitin" if k % 2 == 0 else "chitin_dark", start=-130, end=130, n=11, **HEAD)
    rig.add(r.ico("HeadCore", 0.5, subdivisions=1, location=HEAD_C, scale=(1.25, 1.3, 0.95)), H, "chitin_dark", **HEAD)
    rig.add(r.tube("FrontalCarina", [tuple(HEAD_C + Vector((0, 0.5, 0.57))), tuple(HEAD_C + Vector((0, -0.55, 0.55)))], 0.04,
                   segments=4), H, "chitin_dark", **HEAD)
    rig.add(r.ico("Clypeus", 0.22, subdivisions=1, location=HEAD_C + Vector((0, -0.62, -0.1)), scale=(2.2, 0.8, 1.0)), H, "chitin",
            **HEAD)
    for s in (-1, 1):
        # Lobes occipitaux saillants, glandes acides lumineuses à la place des yeux
        rig.add(a.claw(f"Occipital{s}", HEAD_C + Vector((s * 0.5, 0.55, 0.3)), (s * 0.5, 1, 0.4), 0.35, 0.09, curl=0, segments=4),
                H, "horn", **HEAD)
        for k in range(4):
            rig.add(a.claw(f"Bristle{s}{k}", HEAD_C + Vector((s * 0.7, 0.4 - 0.27 * k, -0.05)), (s, 0.2, 0.3), 0.22, 0.035, curl=0,
                           segments=4), H, "horn", **HEAD)
        b.compound_eye(rig, f"Gland{s}", HEAD_C + Vector((s * 0.6, -0.3, 0.25)), 0.08, (s, -0.4, 0.3), H, **HEAD)
        # Mandibules en faucille, croisées devant la tête, dents pleines
        bone = f"Mandible_{'L' if s > 0 else 'R'}"
        base = HEAD_C + Vector((s * 0.45, -0.55, -0.15))
        tip = HEAD_C + Vector((-s * 0.3, -1.65, -0.25 + 0.05 * s))
        b.mandible(rig, f"Sickle{s}", base, tip, (-s, 0, 0), bone, width=0.2, teeth=5, **HEAD)
        rig.add(r.ico(f"AcidDrop{s}", 0.05, subdivisions=1, location=tip + Vector((0, -0.05, -0.12)), scale=(1, 1, 1.7)), bone,
                "glow", glow=True)
        rig.add(r.ico(f"MandibleHinge{s}", 0.13, subdivisions=1, location=base), H, "chitin_dark", **HEAD)
        b.antenna(rig, f"Antenna{s}", [HEAD_C + Vector((s * 0.3, -0.58, 0.15)), HEAD_C + Vector((s * 0.55, -0.7, 0.75)),
                                       HEAD_C + Vector((s * 0.95, -1.0, 0.6)), HEAD_C + Vector((s * 1.2, -1.4, 0.35))], H,
                  radius=0.035, **HEAD)


def build_body(rig):
    T = "Thorax"
    for k, (y, rx, rz) in enumerate(((-0.95, 0.35, 0.38), (-0.65, 0.42, 0.45), (-0.35, 0.38, 0.4), (-0.05, 0.33, 0.35))):
        b.ring_segment(rig, f"Thorax{k}", (0, y, 1.6 - 0.05 * k), (0, 1, 0.1), rx, rz, 0.27, T, spikes=2 if k == 3 else 0)
    rig.add(r.ico("ThoraxCore", 0.32, subdivisions=1, location=(0, -0.5, 1.55), scale=(1.1, 2.2, 1.1)), T, "chitin_dark")
    rig.add(r.ico("Neck", 0.22, subdivisions=1, location=(0, -1.15, 1.65), scale=(1.2, 1.4, 1.1)), T, "chitin_dark")
    b.organs(rig, "ThoraxGland", (0, -0.5, 1.55), 0.4, T, n=2)
    for k, y in enumerate((0.3, 0.6)):
        rig.add(r.ico(f"PetioleNode{k}", 0.2, subdivisions=1, location=(0, y, 1.55 - 0.05 * k), scale=(1, 0.9, 1.3)), T, "chitin")
        rig.add(a.claw(f"NodeSpine{k}", (0, y, 1.78 - 0.05 * k), (0, 0.4, 1), 0.2, 0.05, curl=0, segments=4), T, "horn")
    rig.add(r.tube("Petiole", [(0, 0.1, 1.55), (0, 0.45, 1.53), (0, 0.85, 1.48)], 0.09, segments=6), T, "chitin_dark")
    # Gastre : anneaux ajourés, glande acide qui luit
    for k in range(5):
        y = 1.0 + 0.35 * k
        size = 0.75 * math.sin(math.pi * (0.2 + 0.7 * k / 4)) + 0.1
        b.ring_segment(rig, f"Gaster{k}", (0, y, 1.42 - 0.04 * k), (0, 1, -0.1), size, size * 0.85, 0.3, "Gaster",
                       color="chitin" if k % 2 == 0 else "chitin_dark")
        zc = 1.42 - 0.04 * k
        rig.add(r.tube(f"GasterSeptum{k}", [(0, y, zc - size * 0.8), (0, y, zc + size * 0.85)], 0.045, segments=4), "Gaster",
                "chitin_dark")
    rig.add(r.tube("GasterSpine", [(0, 0.85, 1.48), (0, 1.8, 1.35), (0, 2.5, 1.27)], 0.08, segments=6), "Gaster", "chitin_dark")
    rig.add(r.ico("AcidSac", 0.42, subdivisions=2, location=(0, 1.65, 1.35), scale=(1, 1.4, 0.9)), "Gaster", "glow", glow=True)
    rig.add(a.claw("Acidopore", (0, 2.55, 1.27), (0, 1, -0.3), 0.2, 0.06, curl=0, segments=4), "Gaster", "horn")


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(3):
            b.leg_chain(rig, f"Leg{s}{k}", leg(k, s), [f"Leg{k + 1}_{side}_{j}" for j in (1, 2, 3)], 0.075, **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
