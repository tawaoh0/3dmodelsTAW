"""Frelon reine squelette (exosquelette ajouré, ≈ 4,5 studs de haut ailes comprises) — animable.
Pack « Insectes géants », créature 4.

Animal modèle : la **reine du frelon asiatique géant** — tête large aux yeux en rein, trois
ocelles, mandibules dentées, thorax bombé, taille de guêpe (pétiole), abdomen rayé terminé
par un dard, deux paires d'ailes nervurées.

Identité : chitine jaune d'or et noire en **bandes alternées** ; **couronne d'alvéoles** de cire
hexagonales (reine de la ruche) ; ailes dressées en V ; gouttes de miel lumineuses aux
mandibules ; organes orangés entre les anneaux ; thème d'effets « hive ».

Pièces Roblox : corps, Head, Wings, Legs, + lumineux.
Os : Root, Thorax, Head, Gaster1-2, Stinger, Wing_{L,R}_{1,2}, Leg{1-3}_{L,R}_{1-3}.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r
from models import _bugs as b

COLORS = {
    "chitin": "#e3aa25",
    "chitin_dark": "#1a1208",
    "horn": "#0a0703",
    "tooth": "#f6ecd2",
    "membrane": "#cdb67e",
    "wax": "#f0c75a",
    "ink": "#050402",
    "glow": "#ff8a1a",
    "glow_hot": "#ffe6b8",
}

EFFECT_THEME = "hive"

TEST_POSE = {
    "Wing_L_1": (0, -25, 0),
    "Wing_R_1": (0, 25, 0),
    "Gaster2": (-25, 0, 0),
    "Head": (15, 0, 10),
    "Leg1_L_1": (0, 0, 20),
}

VIEW = (1.0, -0.9, 0.35)

GASTER = a.smooth_path([(0, 0.45, 2.0), (0, 1.2, 1.75), (0, 1.9, 1.35), (0, 2.4, 0.9)], 7)
HEAD = dict(part="Head")
WINGS = dict(part="Wings")
LEGS = dict(part="Legs")


def leg(k, s):
    th = math.radians((-45, 0, 40)[k])
    d = Vector((s * math.cos(th), math.sin(th), 0))
    a0 = Vector((s * 0.3, -0.9 + 0.35 * k, 1.85))
    return [a0, a0 + d * 0.7 + Vector((0, 0, -0.1)), a0 + d * 1.2 + Vector((0, 0, -1.0)), a0 + d * 1.45 + Vector((0, 0, -1.8))]


def wing_outline(s, fore):
    root = Vector((s * 0.3, -0.75 if fore else -0.4, 2.75 if fore else 2.6))
    span = Vector((s * 2.4, 0.7, 1.4)) if fore else Vector((s * 1.6, 1.1, 0.75))
    tip = root + span
    lead = [root.lerp(tip, f) + Vector((0, -0.25 * math.sin(math.pi * f), 0.12 * math.sin(math.pi * f))) for f in (0.3, 0.65)]
    trail = [root.lerp(tip, f) + Vector((0, 0.55 * math.sin(math.pi * f) * (1 if fore else 0.8), -0.25 * math.sin(math.pi * f)))
             for f in (0.8, 0.5, 0.2)]
    return root, tip, lead, trail


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Thorax", (0, 0.2, 2.2), (0, -1.1, 2.35), "Root")
    rig.bone("Head", (0, -1.1, 2.4), (0, -1.9, 2.3), "Thorax")
    rig.bone("Gaster1", GASTER[0], GASTER[3], "Thorax")
    rig.bone("Gaster2", GASTER[3], GASTER[-1], "Gaster1")
    rig.bone("Stinger", GASTER[-1], GASTER[-1] + Vector((0, 0.3, -0.45)), "Gaster2")
    for s, side in ((1, "L"), (-1, "R")):
        for j, fore in ((1, True), (2, False)):
            root, tip, _, _ = wing_outline(s, fore)
            rig.bone(f"Wing_{side}_{j}", root, tip, "Thorax")
        for k in range(3):
            p = leg(k, s)
            prev = "Thorax"
            for j in range(3):
                prev = rig.bone(f"Leg{k + 1}_{side}_{j + 1}", p[j], p[j + 1], prev)
        rig.fx(f"Eye{side}", (s * 0.45, -1.55, 2.5), "Head")
    rig.fx("Crown", (0, -1.4, 3.15), "Head")
    rig.fx("Sting", GASTER[-1] + Vector((0, 0.35, -0.55)), "Stinger")
    rig.fx("Honey", (0, -2.05, 2.0), "Head")


def build_head(rig):
    H = "Head"
    c0 = Vector((0, -1.5, 2.4))
    for k, (dy, rx, rz) in enumerate(((0.25, 0.48, 0.45), (-0.05, 0.6, 0.5), (-0.32, 0.5, 0.42))):
        b.plate(rig, f"HeadPlate{k}", c0 + Vector((0, dy, 0)), (0, 1, 0), rx, rz, 0.28, H, color="chitin" if k != 1 else "chitin_dark",
                start=-125, end=125, n=11, **HEAD)
    rig.add(r.ico("Face", 0.3, subdivisions=1, location=c0 + Vector((0, -0.35, -0.1)), scale=(1.4, 0.6, 1.3)), H, "chitin", **HEAD)
    for s in (-1, 1):
        # Yeux composés en rein, très grands, sur les côtés
        for k, dz in enumerate((0.18, -0.08)):
            b.compound_eye(rig, f"Eye{s}{k}", c0 + Vector((s * 0.5, -0.12 + 0.05 * k, dz)), 0.17 - 0.03 * k, (s, -0.4, 0), H,
                           **HEAD)
        b.mandible(rig, f"Mandible{s}", c0 + Vector((s * 0.28, -0.45, -0.35)), c0 + Vector((s * 0.03, -0.75, -0.48)), (-s, 0, 0), H,
                   width=0.14, teeth=4, **HEAD)
        rig.add(r.ico(f"HoneyDrop{s}", 0.05, subdivisions=1, location=c0 + Vector((s * 0.05, -0.82, -0.6)), scale=(1, 1, 1.6)), H,
                "glow", glow=True)
        b.antenna(rig, f"Antenna{s}", [c0 + Vector((s * 0.12, -0.45, 0.22)), c0 + Vector((s * 0.25, -0.75, 0.55)),
                                       c0 + Vector((s * 0.55, -1.0, 0.4)), c0 + Vector((s * 0.75, -1.3, 0.2))], H, radius=0.035,
                  **HEAD)
    for k, (x, y) in enumerate(((0, -0.2), (-0.12, 0.0), (0.12, 0.0))):
        rig.add(r.ico(f"Ocellus{k}", 0.05, subdivisions=1, location=c0 + Vector((x, y, 0.47))), H, "glow", glow=True)
    # Couronne de la reine : alvéoles de cire hexagonales en anneau, la plus haute au centre
    for k in range(7):
        ang = math.radians(-150 + 300 * k / 6)
        base = c0 + Vector((0.3 * math.sin(ang), 0.05 - 0.25 * math.cos(ang), 0.45))
        h = 0.22 + 0.18 * math.cos(ang / 2) ** 2
        cell = r.tube(f"Cell{k}", [tuple(base), tuple(base + Vector((0, 0, h)))], 0.09, segments=6)
        rig.add(cell, H, "wax", **HEAD)
        rig.add(r.ico(f"CellHoney{k}", 0.06, subdivisions=1, location=base + Vector((0, 0, h))), H, "glow", glow=True)


def build_body(rig):
    T = "Thorax"
    for k, (y, rx, rz) in enumerate(((-0.95, 0.5, 0.48), (-0.65, 0.62, 0.58), (-0.33, 0.6, 0.55), (-0.05, 0.48, 0.45))):
        b.ring_segment(rig, f"Thorax{k}", (0, y, 2.3), (0, 1, 0), rx, rz, 0.28, T, color="chitin_dark" if k % 2 else "chitin",
                       spikes=0)
    rig.add(r.ico("Scutellum", 0.18, subdivisions=1, location=(0, -0.2, 2.85), scale=(1.4, 1, 0.6)), T, "chitin")
    rig.add(r.ico("Mesothorax", 0.45, subdivisions=1, location=(0, -0.45, 2.25), scale=(1.2, 1.55, 1.1)), T, "chitin_dark")
    b.organs(rig, "ThoraxCore", (0, -0.5, 2.25), 0.6, T, n=2)
    rig.add(r.tube("Petiole", [(0, 0.05, 2.22), (0, 0.3, 2.12), (0, 0.5, 1.98)], [0.12, 0.08, 0.12], segments=6), T, "chitin_dark")
    # Abdomen : anneaux rayés jaune / noir, organes orangés, dard
    for i in range(1, len(GASTER)):
        p = GASTER[i]
        t = (GASTER[i] - GASTER[i - 1]).normalized()
        f = i / (len(GASTER) - 1)
        size = 0.62 * math.sin(math.pi * (0.25 + 0.65 * f)) + 0.12
        bone = "Gaster1" if i <= 3 else "Gaster2"
        b.ring_segment(rig, f"Gaster{i}", p, t, size, size * 0.9, 0.42, bone, up=(0, -0.3, 1),
                       color="chitin" if i % 2 else "chitin_dark", under="chitin_dark" if i % 2 else "chitin")
        rig.add(r.ico(f"Venom{i}", size * 0.45, subdivisions=1, location=p), bone, "glow", glow=True)
    end, t = GASTER[-1], (GASTER[-1] - GASTER[-2]).normalized()
    rig.add(a.claw("Sting", end, t + Vector((0, 0, -0.3)), 0.55, 0.07, curl=0.2, segments=5), "Stinger", "horn")
    rig.add(r.tube("GasterSpine", [tuple(p) for p in GASTER], 0.06, segments=5), "Gaster1", "chitin_dark")


def build_wings(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for j, fore in ((1, True), (2, False)):
            bone = f"Wing_{side}_{j}"
            root, tip, lead, trail = wing_outline(s, fore)
            w = {bone: 1.0}
            outline = [(tuple(root), w)] + [(tuple(p), w) for p in lead] + [(tuple(tip), w)] + [(tuple(p), w) for p in trail]
            m = a.membrane(f"Wing{s}{j}", outline)
            rig.pal.paint(m, "membrane")
            m["part"] = "Wings"
            # Nervures : costale épaisse + nervures qui rayonnent
            rig.add(r.tube(f"Costa{s}{j}", [tuple(root)] + [tuple(p) for p in lead] + [tuple(tip)], 0.035, segments=4), bone,
                    "chitin_dark", **WINGS)
            for k, p in enumerate(trail):
                q = root.lerp(lead[min(k, 1)], 0.8)
                rig.add(r.tube(f"Vein{s}{j}{k}", [tuple(q), tuple(p)], 0.018, segments=4), bone, "chitin_dark", **WINGS)
            rig.add(r.ico(f"Stigma{s}{j}", 0.06, subdivisions=1, location=lead[-1], scale=(1, 2, 0.5)), bone, "glow", glow=True)
            rig.add(r.ico(f"WingBase{s}{j}", 0.09, subdivisions=1, location=root), bone, "chitin_dark", **WINGS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(3):
            p = leg(k, s)
            b.leg_chain(rig, f"Leg{s}{k}", p, [f"Leg{k + 1}_{side}_{j}" for j in (1, 2, 3)], 0.075,
                        color="chitin" if k != 1 else "chitin_dark", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_wings(rig)
    build_legs(rig)
    return rig
