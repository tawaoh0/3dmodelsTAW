"""Mille-pattes titan squelette (exosquelette ajouré, ≈ 3,2 studs dressé, 11 de long) — animable.
Pack « Insectes géants », créature 3.

Animal modèle : la **scolopendre géante** — tête plate à antennes longues, énormes
**forcipules** à venin qui encadrent la bouche, 21 anneaux portant chacun une paire de
pattes, pattes anales allongées vers l'arrière.

Identité : chitine rouge sang, pattes jaune d'or ; **aucune corne** : forcipules noires
et antennes ; avant du corps **dressé** en menace, arrière qui serpente au sol ; jours
lumineux jaunes entre les plaques ; thème d'effets « swarm » (nuée grouillante).

Pièces Roblox : corps, Head, Legs, + lumineux.
Os : Root, Seg1-5, Head, Forcipule_{L,R}.
"""
from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r
from models import _bugs as b

COLORS = {
    "chitin": "#8c211b",
    "chitin_dark": "#250807",
    "legs": "#d99a2a",
    "horn": "#0b0606",
    "tooth": "#f2e6cc",
    "ink": "#060303",
    "glow": "#ffe23a",
    "glow_hot": "#fffbd0",
}

EFFECT_THEME = "swarm"

TEST_POSE = {
    "Seg1": (25, 0, 0),
    "Seg3": (0, 0, 25),
    "Seg5": (0, 0, -30),
    "Forcipule_L": (0, 0, -20),
    "Head": (-15, 0, 0),
}

VIEW = (1.0, -0.8, 0.5)

BODY = a.smooth_path([(0, -2.9, 3.0), (0, -2.4, 2.55), (0, -1.7, 1.65), (0, -0.8, 0.8), (0.6, 0.5, 0.58), (0, 2.0, 0.58),
                      (-0.7, 3.4, 0.55), (0, 4.8, 0.5), (0.6, 5.9, 0.45)], 22)
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def seg_bone(i):
    return f"Seg{min(5, i * 5 // (len(BODY) - 1) + 1)}"


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(BODY) - 1
    rig.bone("Seg3", BODY[2 * n // 5], BODY[3 * n // 5], "Root")
    rig.bone("Seg2", BODY[2 * n // 5], BODY[n // 5], "Seg3")
    rig.bone("Seg1", BODY[n // 5], BODY[0], "Seg2")
    rig.bone("Seg4", BODY[3 * n // 5], BODY[4 * n // 5], "Seg3")
    rig.bone("Seg5", BODY[4 * n // 5], BODY[-1], "Seg4")
    rig.bone("Head", BODY[0], BODY[0] + Vector((0, -0.7, 0.2)), "Seg1")
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Forcipule_{side}", BODY[0] + Vector((s * 0.35, -0.2, -0.2)), BODY[0] + Vector((s * 0.1, -0.85, -0.35)), "Head")
        rig.fx(f"Eye{side}", BODY[0] + Vector((s * 0.3, -0.45, 0.2)), "Head")
        rig.fx(f"Venom{side}", BODY[0] + Vector((s * 0.05, -0.95, -0.4)), f"Forcipule_{side}")
    rig.fx("Swarm", BODY[8] + Vector((0, 0, 0.6)), "Seg2")


def build_head(rig):
    H = "Head"
    c0 = BODY[0]
    fwd = (BODY[0] - BODY[1]).normalized()
    b.plate(rig, "HeadShield", c0 + fwd * 0.25, fwd, 0.55, 0.32, 0.55, H, up=(0, 0.3, 1), start=-120, end=120, n=11, **HEAD)
    rig.add(r.ico("NeckCore", 0.35, subdivisions=1, location=c0 - fwd * 0.2, scale=(1.5, 1.4, 1.0)), H, "chitin_dark", **HEAD)
    rig.add(r.ico("HeadCore", 0.3, subdivisions=1, location=c0 + fwd * 0.2, scale=(1.5, 1.2, 0.8)), H, "chitin_dark", **HEAD)
    rig.add(r.tube("HeadRidge", [tuple(c0 + fwd * 0.05 + Vector((0, 0, 0.33))), tuple(c0 + fwd * 0.5 + Vector((0, 0, 0.28)))],
                   0.035, segments=4), H, "chitin_dark", **HEAD)
    for s in (-1, 1):
        for k in range(3):
            b.compound_eye(rig, f"Ocellus{s}{k}", c0 + fwd * (0.35 - 0.08 * k) + Vector((s * (0.38 - 0.03 * k), 0, 0.15 + 0.04 * k)),
                           0.05, (s, -0.5, 0.4), H, **HEAD)
        b.antenna(rig, f"Antenna{s}", [c0 + fwd * 0.5 + Vector((s * 0.25, 0, 0.27)), c0 + fwd * 1.1 + Vector((s * 0.6, 0, 0.6)),
                                       c0 + fwd * 1.5 + Vector((s * 1.1, 0.2, 0.9))], H, radius=0.04, **HEAD)
        # Forcipules : énormes crochets à venin en tenaille devant la bouche
        b.mandible(rig, f"Forcipule{s}", c0 + Vector((s * 0.38, -0.2, -0.2)), c0 + Vector((s * 0.05, -0.95, -0.35)), (-s, 0, 0),
                   f"Forcipule_{s > 0 and 'L' or 'R'}", width=0.18, teeth=4, **HEAD)
        rig.add(r.ico(f"VenomDrop{s}", 0.045, subdivisions=1, location=c0 + Vector((s * 0.05, -1.05, -0.45)), scale=(1, 1, 1.6)),
                f"Forcipule_{s > 0 and 'L' or 'R'}", "glow", glow=True)
        b.mandible(rig, f"Maxilla{s}", c0 + fwd * 0.4 + Vector((s * 0.12, 0, -0.2)), c0 + fwd * 0.65 + Vector((s * 0.03, 0, -0.28)),
                   (-s, 0, 0), H, width=0.07, teeth=2, **HEAD)


def build_body(rig):
    n = len(BODY)
    for i in range(1, n):
        p = BODY[i]
        t = (BODY[i - 1] - BODY[min(i + 1, n - 1)]).normalized()
        size = 0.5 - 0.15 * i / (n - 1)
        bone = seg_bone(i)
        b.ring_segment(rig, f"Seg{i}", p, t, size * 1.3, size * 0.75, 0.42, bone, up=(0, 0.25 if i < 4 else 0, 1),
                       spikes=2 if i % 3 == 0 else 0)
        rig.add(r.ico(f"Core{i}", size * 0.4, subdivisions=1, location=p, scale=(1.4, 1.4, 0.8)), bone, "glow", glow=True)
        if i < n - 1:
            rig.add(a.ring_around(f"Joint{i}", p.lerp(BODY[i + 1], 0.5), BODY[i + 1] - p, size * 0.75, 0.05, segments=10), bone,
                    "chitin_dark")
        # Une paire de pattes par anneau : au sol derrière, pattes avant qui griffent l'air
        axis, dorsal, side = b.basis(t, (0, 0, 1))
        for s in (-1, 1):
            base = p + side * s * size * 1.1 - dorsal * size * 0.3
            out = side * s
            if p.z > 1.0:
                pts = [base, base + out * 0.45 + Vector((0, -0.25, 0.15)), base + out * 0.75 + Vector((0, -0.45, -0.25)),
                       base + out * 0.85 + Vector((0, -0.6, -0.55))]
            else:
                pts = [base, base + out * 0.5 + Vector((0, 0, 0.45)), base + out * 0.95 + Vector((0, 0, 0.0)),
                       Vector((base.x + out.x * 1.15, base.y + out.y * 1.15, 0.04))]
            if i == n - 1:      # pattes anales allongées vers l'arrière
                back = -t
                pts = [base, base + out * 0.3 + back * 0.5 + Vector((0, 0, 0.2)), base + out * 0.45 + back * 1.1,
                       base + out * 0.55 + back * 1.5 + Vector((0, 0, -0.3))]
            b.leg_chain(rig, f"Leg{i}{s}", pts, [bone], 0.06, color="legs", spines=i % 2 == 0, **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    return rig
