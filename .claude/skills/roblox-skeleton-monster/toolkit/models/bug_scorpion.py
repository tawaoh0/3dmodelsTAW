"""Scorpion empereur squelette (exosquelette ajouré, ≈ 3,8 studs de haut, 8 de long) — animable.
Pack « Insectes géants », créature 1.

Animal modèle : le **scorpion empereur** (Pandinus) — énormes pinces bombées et dentées,
carapace large à tubercule oculaire, 7 anneaux de mésosome, queue de 5 anneaux recourbée
au-dessus du dos, vésicule à venin et aiguillon.

Identité : chitine bleu-noir laquée ; **aucune corne** : pinces géantes dentées ; queue dressée
en arc ; plaques séparées par des jours qui laissent voir les glandes à venin magenta ;
**insignes impériaux** : bagues d'or aux anneaux de la queue, emblème d'or sur la carapace ;
thème d'effets « venom ».

Pièces Roblox : corps, Head, Tail, Legs, Claws, + lumineux.
Os : Root, Body, Head, Tail1-5, Sting, Claw_{L,R}_1-3, Pincer_{L,R}, Leg{1-4}_{L,R}_{1-3}.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r
from models import _bugs as b

COLORS = {
    "chitin": "#2e3a55",
    "chitin_dark": "#121624",
    "horn": "#0a0b10",
    "tooth": "#ece6d6",
    "gold": "#d8aa36",
    "ink": "#050608",
    "glow": "#ff3fa8",
    "glow_hot": "#ffd0ea",
}

EFFECT_THEME = "venom"

TEST_POSE = {
    "Tail2": (25, 0, 0),
    "Sting": (30, 0, 0),
    "Claw_L_2": (0, 0, 25),
    "Pincer_R": (0, 0, -20),
    "Leg2_L_1": (0, 0, 20),
}

VIEW = (1.0, -0.9, 0.55)

TAIL = a.smooth_path([(0, 1.95, 1.1), (0, 2.65, 1.6), (0, 2.9, 2.5), (0, 2.5, 3.3), (0, 1.75, 3.6)], 6)
CURL_C = Vector((0, 1.95, 2.4))
HEAD = dict(part="Head")
TAILP = dict(part="Tail")
LEGS = dict(part="Legs")
CLAWS = dict(part="Claws")


def leg(k, s):
    th = math.radians((-40, -12, 18, 45)[k])
    d = Vector((s * math.cos(th), math.sin(th), 0))
    a0 = Vector((s * 0.55, -1.2 + 0.4 * k, 0.9))
    return [a0, a0 + d * 1.0 + Vector((0, 0, 0.65)), a0 + d * 1.9 + Vector((0, 0, -0.35)), a0 + d * 2.35 + Vector((0, 0, -0.85))]


def claw_arm(s):
    return [Vector((s * 0.6, -1.5, 1.0)), Vector((s * 1.35, -1.9, 1.3)), Vector((s * 1.25, -2.6, 1.2)),
            Vector((s * 1.12, -3.15, 1.15))]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Body", (0, 1.8, 1.05), (0, -0.6, 1.05), "Root")
    rig.bone("Head", (0, -0.6, 1.05), (0, -1.9, 1.05), "Body")
    prev = "Body"
    for k in range(5):
        prev = rig.bone(f"Tail{k + 1}", TAIL[k], TAIL[k + 1], prev)
    rig.bone("Sting", TAIL[-1], TAIL[-1] + Vector((0, -0.6, -0.3)), "Tail5")
    for s, side in ((1, "L"), (-1, "R")):
        arm = claw_arm(s)
        prev = "Head"
        for k in range(3):
            prev = rig.bone(f"Claw_{side}_{k + 1}", arm[k], arm[k + 1], prev)
        rig.bone(f"Pincer_{side}", Vector((s * 1.3, -3.25, 1.15)), Vector((s * 1.2, -3.95, 1.18)), f"Claw_{side}_3")
        for k in range(4):
            p = leg(k, s)
            prev = "Body" if k > 1 else "Head"
            for j in range(3):
                prev = rig.bone(f"Leg{k + 1}_{side}_{j + 1}", p[j], p[j + 1], prev)
        rig.fx(f"Eye{side}", (s * 0.1, -1.25, 1.5), "Head")
    rig.fx("Sting", TAIL[-1] + Vector((0, -0.75, -0.45)), "Sting")
    rig.fx("Venom", (0, 0.6, 1.05), "Body")


def build_head(rig):
    H = "Head"
    for k, (y, rx, rz) in enumerate(((-0.75, 0.78, 0.36), (-1.15, 0.72, 0.34), (-1.55, 0.58, 0.3))):
        b.plate(rig, f"Carapace{k}", (0, y, 1.05), (0, 1, 0), rx, rz, 0.38, H, start=-115, end=115, **HEAD)
    rig.add(r.ico("Tubercle", 0.16, subdivisions=1, location=(0, -1.25, 1.38), scale=(1.3, 1.1, 0.8)), H, "chitin_dark",
            **HEAD)
    rig.add(a.crystal("Emblem", (0, -0.85, 1.43), 0.1, 0.22, sides=4), H, "gold", **HEAD)
    rig.add(r.tube("Keel", [(0, -0.6, 1.42), (0, -1.0, 1.42), (0, -1.6, 1.36)], 0.035, segments=4), H, "gold", **HEAD)
    for s in (-1, 1):
        b.compound_eye(rig, f"MedianEye{s}", (s * 0.1, -1.3, 1.5), 0.07, (s * 0.4, -0.5, 1), H, **HEAD)
        for k in range(3):
            b.compound_eye(rig, f"LateralEye{s}{k}", (s * (0.5 - 0.05 * k), -1.7 + 0.08 * k, 1.2 + 0.04 * k), 0.035,
                           (s, -0.6, 0.4), H, **HEAD)
        b.mandible(rig, f"Chelicera{s}", (s * 0.15, -1.75, 1.0), (s * 0.04, -2.15, 0.92), (-s, 0, 0), H, width=0.1, teeth=3,
                   **HEAD)
    rig.add(r.ico("Clypeus", 0.2, subdivisions=1, location=(0, -1.62, 1.12), scale=(1.8, 1.2, 1.2)), H, "chitin_dark", **HEAD)
    b.organs(rig, "HeadGland", (0, -1.1, 1.0), 0.4, H, n=2)


def build_body(rig):
    for k in range(7):
        y = -0.5 + 0.36 * k
        f = k / 6
        b.ring_segment(rig, f"Meso{k}", (0, y, 1.05), (0, 1, 0), 0.82 - 0.12 * f, 0.42 - 0.04 * f, 0.32, "Body",
                       spikes=2 if k % 2 == 0 else 0)
    b.organs(rig, "VenomGland", (0, 0.6, 1.0), 0.8, "Body", n=4)
    rig.add(r.tube("Spine", [(0, -0.6, 1.0), (0, 0.6, 1.0), (0, 1.9, 1.05)], 0.07, segments=6), "Body", "chitin_dark")
    for k in range(5):
        p, q = TAIL[k], TAIL[k + 1]
        mid = p.lerp(q, 0.5)
        up = mid - CURL_C
        size = 0.42 - 0.04 * k
        b.ring_segment(rig, f"Tail{k}", mid, q - p, size, size * 0.9, (q - p).length * 0.85, f"Tail{k + 1}", up=up,
                       spikes=1, **TAILP)
        rig.add(a.ring_around(f"TailGold{k}", p, q - p, size * 1.02, 0.04, segments=12), f"Tail{k + 1}", "gold", **TAILP)
        rig.add(r.ico(f"TailCore{k}", size * 0.35, subdivisions=1, location=mid), f"Tail{k + 1}", "glow", glow=True)
    # Telson : vésicule ajourée à glande lumineuse + aiguillon noir
    end, d = TAIL[-1], (TAIL[-1] - TAIL[-2]).normalized()
    ves = end + d * 0.3
    b.plate(rig, "VesicleA", ves, d, 0.32, 0.36, 0.45, "Sting", up=ves - CURL_C, start=-120, end=120, **TAILP)
    rig.add(r.ico("VenomSac", 0.24, subdivisions=2, location=ves, scale=(1, 1.2, 1)), "Sting", "glow", glow=True)
    tip_base = ves + d * 0.25
    rig.add(a.claw("Aculeus", tip_base, (0, -0.8, -0.9), 0.75, 0.11, curl=0.5, segments=6), "Sting", "horn", **TAILP)
    tip, _ = a.claw_point(tip_base, (0, -0.8, -0.9), 0.75, 0.5, 1.0)
    rig.add(r.ico("VenomDrop", 0.05, subdivisions=1, location=tip + Vector((0, 0, -0.06)), scale=(1, 1, 1.6)), "Sting", "glow",
            glow=True)


def build_claws(rig):
    for s, side in ((1, "L"), (-1, "R")):
        arm = claw_arm(s)
        b.leg_chain(rig, f"Palp{s}", arm, [f"Claw_{side}_{k}" for k in (1, 2, 3)], 0.13, spines=True, **CLAWS)
        hand = Vector((s * 1.12, -2.95, 1.15))
        b.ring_segment(rig, f"Chela{s}", hand, (0, -1, 0), 0.32, 0.26, 0.55, f"Claw_{side}_3", spikes=3, **CLAWS)
        rig.add(r.ico(f"ChelaCore{s}", 0.14, subdivisions=1, location=hand), f"Claw_{side}_3", "glow", glow=True)
        b.mandible(rig, f"FixedFinger{s}", (s * 0.98, -3.2, 1.12), (s * 0.85, -3.95, 1.1), (s, 0, 0), f"Claw_{side}_3",
                   width=0.17, teeth=4, **CLAWS)
        b.mandible(rig, f"MovingFinger{s}", (s * 1.3, -3.2, 1.15), (s * 1.18, -3.95, 1.2), (-s, 0, 0), f"Pincer_{side}",
                   width=0.17, teeth=4, **CLAWS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(4):
            b.leg_chain(rig, f"Leg{s}{k}", leg(k, s), [f"Leg{k + 1}_{side}_{j}" for j in (1, 2, 3)], 0.08, **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_claws(rig)
    build_legs(rig)
    return rig
