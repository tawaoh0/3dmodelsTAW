"""Mégalodon squelette (≈ 15 studs de long, 6 de haut) — créature animable.
Pack « Abysses », créature 2.

Animal modèle : le grand requin blanc géant — mâchoires en fer à cheval à 3 rangées de
dents triangulaires, rostre arrondi, petits yeux, 5 arcs branchiaux, grande dorsale,
pectorales en ailes, queue en croissant (lobe haut plus long).

Identité : os ardoise sombre et dents claires ; pas de cornes mais des harpons rouillés
plantés dans le dos avec leurs chaînes ; silhouette horizontale en nage ; lueur rouge sang,
thème d'effets « blood ».

2 pièces Roblox : corps, tête (crâne + mâchoires + branchies), + lumineux.
Os : Root, Body1-5, Head, Jaw, Caudal, PecFin_L/R, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#56616c",
    "bone_shade": "#3a434c",
    "tooth": "#ece6d6",
    "horn": "#d8d2c4",
    "horn_tip": "#a8323a",
    "disc": "#2a1f24",
    "membrane": "#2b3238",
    "rust": "#8a4b2a",
    "ink": "#0e0d10",
    "glow": "#ff2d4a",
    "glow_hot": "#ffc2b8",
}

EFFECT_THEME = "blood"

TEST_POSE = {
    "Jaw": (35, 0, 0),
    "Body3": (0, 0, 12),
    "Body4": (0, 0, 15),
    "Caudal": (0, 0, 20),
    "PecFin_L": (0, 25, 0),
}

VIEW = (1.0, -0.7, 0.45)

SPINE = a.smooth_path([(0, -2.8, 3.1), (0, -1.0, 3.15), (0, 1.5, 3.2), (0, 4.0, 3.3),
                       (0, 6.2, 3.5), (0, 7.8, 3.7)], 40)

# Crâne (chondrocrâne) : (y, demi-larg. dessus, joues, bas, z dessus, z bas) → rostre arrondi
SKULL = [(-2.9, 0.55, 0.8, 0.7, 3.75, 2.75), (-3.5, 0.6, 0.85, 0.72, 3.85, 2.75),
         (-4.2, 0.5, 0.72, 0.62, 3.75, 2.8), (-4.9, 0.36, 0.52, 0.45, 3.55, 2.9),
         (-5.4, 0.24, 0.34, 0.3, 3.35, 2.98)]
EYE = (-4.15, 3.45)


def horseshoe(width, length, z, y_back=-3.0, n=15):
    """Arc en fer à cheval (mâchoire de requin) dans le plan horizontal z."""
    pts = []
    for i in range(n):
        th = -math.pi / 2 + math.pi * i / (n - 1)
        pts.append(Vector((width * math.sin(th), y_back - length * math.cos(th), z)))
    return pts


def fin(rig, name, root, edge, bone, part=None, rays=True, color="membrane"):
    """Nageoire : membrane entre une racine (2 points ou plus) et un bord, + rayons d'os."""
    pts = [root[0]] + list(edge) + [root[-1]] + list(reversed(root[1:-1]))
    m = a.membrane(name, [(tuple(p), {bone: 1}) for p in pts], thickness=0.05)
    rig.pal.paint(m, color)
    if part:
        m["part"] = part
    if rays:
        kw = dict(part=part) if part else {}
        for i, e in enumerate(edge):
            start = root[0].lerp(root[-1], i / max(1, len(edge) - 1))
            rig.add(r.tube(f"{name}Ray{i}", [tuple(start), tuple(start.lerp(e, 0.92))],
                           [0.05, 0.02], segments=4), bone, "bone_shade", **kw)


def I(k):
    """Index de vertèbre exprimé sur une colonne de référence à 26 vertèbres."""
    return round(k * (len(SPINE) - 1) / 25)


def body_bone(i):
    return f"Body{min(5, i * 5 // (len(SPINE) - 1) + 1)}"


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    n = len(SPINE) - 1
    for b in range(5):
        i0, i1 = b * n // 5, (b + 1) * n // 5
        parent = rig.bone(f"Body{b + 1}", SPINE[i0], SPINE[i1], parent)
    rig.bone("Caudal", SPINE[-1], (0, 9.6, 3.9), "Body5")
    rig.bone("Head", SPINE[0], (0, -5.4, 3.3), "Body1")
    rig.bone("Jaw", (0, -3.0, 2.35), (0, -5.0, 1.95), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"PecFin_{side}", (s * 0.6, -1.4, 2.6), (s * 3.0, 0.3, 1.2), "Body1")
        rig.fx(f"Eye{side}", (s * 0.66, EYE[0], EYE[1]), "Head")
    rig.fx("Mouth", (0, -4.2, 2.5), "Head")
    rig.fx("Heart", (0, -1.6, 2.65), "Body1")
    rig.fx("TailTip", (0, 9.6, 5.8), "Caudal")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J, kw = "Head", "Jaw", dict(part="Head")
    skull = a.loft_profile("Skull", SKULL, droop=0.12)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.15, 0.13)]
          + [a.hole_along((sx * 0.22, -5.25, 2.97), (0, 0.3, 1), (1, 0, 0), 0.07, 0.12, depth=0.2)
             for sx in (-1, 1)])
    rig.add(skull, H, "bone", **kw)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.12, subdivisions=2, location=(s * (x - 0.06), EYE[0], EYE[1])),
                H, "glow", glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", (s * x, EYE[0], EYE[1]), (1, 0, 0), 0.19, 0.045,
                              segments=12), H, "bone_shade", **kw)
        rig.add(a.blade(f"Brow{s}", (s * 0.3, -4.5, 3.78), (s * 0.62, -3.7, 3.82), 0.22, 0.1,
                        width_end=0.16, mid=0.28, normal=(0, 0.15, 1)), H, "bone_shade", **kw)
        # Pores électrorécepteurs (ampoules de Lorenzini) sur le rostre
        for i in range(6):
            yy = -4.75 - 0.12 * i
            zz = 3.2 + 0.12 * math.sin(i * 1.7)
            rig.add(r.ico(f"Pore{s}{i}", 0.035, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy, zz), yy, zz)), H, "ink", **kw)
        # 5 arcs branchiaux en C, avec branchiospines et fentes rougeoyantes
        for g in range(5):
            yy = -2.45 + 0.27 * g
            arc = [(s * 0.5, yy, 3.4), (s * 0.85, yy + 0.05, 2.75), (s * 0.78, yy, 2.15),
                   (s * 0.4, yy - 0.05, 1.95)]
            rig.add(r.tube(f"Gill{s}{g}", arc, [0.05, 0.065, 0.06, 0.04], segments=5), H,
                    "bone_shade", **kw)
            for k, p in enumerate(arc[1:3]):
                rig.add(a.claw(f"Raker{s}{g}{k}", p, (-s, 0, 0.1), 0.18, 0.03, curl=0,
                               segments=4), H, "horn", **kw)
            if g < 4:
                rig.add(r.tube(f"GillGlow{s}{g}", [(s * 0.62, yy + 0.13, 3.2),
                                                   (s * 0.86, yy + 0.15, 2.75),
                                                   (s * 0.74, yy + 0.13, 2.2)], 0.025, segments=4),
                        H, "glow", glow=True)
    # Arête dorsale du crâne et petites piques
    rig.add(r.tube("SkullRidge", [(0, yy, a.width_at(SKULL, yy, 4) + 0.02)
                                  for yy in (-3.0, -3.8, -4.6, -5.2)], [0.06, 0.08, 0.07, 0.05],
                   segments=5), H, "bone_shade", **kw)
    for i, yy in enumerate((-3.3, -3.9, -4.5)):
        rig.add(a.claw(f"SkullSpike{i}", (0, yy, a.width_at(SKULL, yy, 4)), (0, 0.6, 1),
                       0.25, 0.05, curl=-0.1, segments=4), H, "horn", **kw)

    # Mâchoires en fer à cheval, gueule entrouverte, 3 rangées de dents triangulaires
    upper = horseshoe(0.78, 2.0, 2.72)
    lower = horseshoe(0.82, 2.05, 2.12)
    rig.add(r.tube("UpperJaw", [tuple(p) for p in upper], 0.15, segments=6), H, "bone_shade", **kw)
    rig.add(r.tube("LowerJaw", [tuple(p) for p in lower], 0.17, segments=6), J, "bone", **kw)
    rig.add(r.tube("LowerJawBase", [tuple(p - Vector((0, 0, 0.22))) for p in lower[2:-2]], 0.1,
                   segments=5), J, "bone_shade", **kw)
    for row in range(3):
        sc = 1 - 0.13 * row
        for jaw_pts, down, bone in ((horseshoe(0.78 - 0.1 * row, 2.0 - 0.15 * row, 2.62), -1, H),
                                    (horseshoe(0.82 - 0.1 * row, 2.05 - 0.15 * row, 2.25), 1, J)):
            for i in range(1, 14):
                p = jaw_pts[i]
                front = 1 - abs(i - 7) / 7
                size = (0.18 + 0.16 * front) * sc
                inward = Vector((-p.x, -(p.y + 3.0) * 0.0, 0)).normalized() * 0.2 if p.x else Vector()
                tip = p + Vector((0, 0, down * size)) + inward * row + Vector((0, 0.05 * row, 0))
                rig.add(a.blade(f"Tooth{bone}{row}{i}", p, tip, size * 0.75, 0.035, width_end=0.01,
                                normal=(p.x, -(p.y + 3.0), 0) if (p.x or p.y) else (0, -1, 0),
                                bevel=0), bone, "tooth", **kw)
    rig.add(r.ico("Throat", 0.3, subdivisions=2, location=(0, -3.4, 2.45), scale=(1.4, 1, 0.5)), H,
            "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for i, p in enumerate(SPINE):
        t = i / (len(SPINE) - 1)
        nxt = SPINE[min(i + 1, len(SPINE) - 1)]
        prv = SPINE[max(i - 1, 0)]
        tan = (nxt - prv).normalized()
        size = 0.42 - 0.22 * t
        bone = body_bone(i)
        rig.add(a.vertebra(f"V{i}", p, tan, size, spine=0.8 - 0.4 * t, lean=-0.3,
                           transverse=t < 0.55), bone, "bone")
        if i < len(SPINE) - 1:
            rig.add(a.disc(f"VD{i}", p.lerp(nxt, 0.5), tan, size), bone, "disc")
        if 0.04 <= t <= 0.36 and i % 2 == 0:   # côtes courtes
            for s in (-1, 1):
                rig.add(a.rib(f"Rib{i}{s}", p - Vector((0, 0, 0.1)), 0.55, 0.9, s, sweep=-0.15,
                              radius=0.06, segments=5), bone, "bone")
        if t >= 0.48 and i % 2 == 0:   # arcs hémaux sous la queue
            down = p - Vector((0, 0, size * 0.4))
            rig.add(a.blade(f"Haemal{i}", down, down + Vector((0, 0.25, -size * 1.6)), size * 0.45,
                            size * 0.15, width_end=size * 0.2, normal=(1, 0, 0), bevel=0), bone,
                    "bone_shade")
    # Cœur de sang derrière les branchies + veines
    rig.add(a.crystal("Heart", (0, -1.6, 2.65), 0.25, 0.7), "Body1", "glow", glow=True)
    for s in (-1, 1):
        rig.add(r.tube(f"Vein{s}", [(0, -1.6, 2.65), (s * 0.3, -2.1, 2.5), (s * 0.4, -2.5, 2.4)],
                       0.03, segments=4), "Body1", "glow", glow=True)


def build_fins(rig):
    top = lambda i, dz=0.55: SPINE[i] + Vector((0, 0, dz))  # noqa: E731
    # Grande dorsale
    fin(rig, "Dorsal", [top(I(7)), top(I(9)), top(I(11))],
        [top(I(7)) + Vector((0, 0.6, 1.4)), top(I(8)) + Vector((0, 1.3, 2.5)),
         top(I(10)) + Vector((0, 1.6, 1.6)), top(I(11)) + Vector((0, 1.1, 0.5))], "Body2")
    # Seconde dorsale et anale
    fin(rig, "Dorsal2", [top(I(19), 0.35), top(I(21), 0.35)], [top(I(19)) + Vector((0, 0.6, 0.6)),
                                                          top(I(21)) + Vector((0, 0.5, 0.2))], "Body4")
    bot = lambda i: SPINE[i] - Vector((0, 0, 0.45))  # noqa: E731
    fin(rig, "Anal", [bot(I(19)), bot(I(21))], [bot(I(19)) + Vector((0, 0.6, -0.6)),
                                          bot(I(21)) + Vector((0, 0.5, -0.25))], "Body4")
    for s, side in ((1, "L"), (-1, "R")):
        # Pectorales en ailes
        root = [Vector((s * 0.55, -1.6, 2.55)), Vector((s * 0.6, -1.15, 2.55)),
                Vector((s * 0.55, -0.7, 2.6))]
        fin(rig, f"Pec{s}", root, [Vector((s * 1.8, -1.2, 1.9)), Vector((s * 3.0, 0.3, 1.2)),
                                   Vector((s * 2.0, 0.2, 1.7))], f"PecFin_{side}")
        # Pelviennes
        root = [SPINE[I(13)] + Vector((s * 0.35, 0, -0.45)), SPINE[I(15)] + Vector((s * 0.3, 0, -0.45))]
        fin(rig, f"Pelvic{s}", root, [root[0] + Vector((s * 0.8, 0.6, -0.6)),
                                      root[1] + Vector((s * 0.4, 0.4, -0.3))], "Body3")
    # Queue en croissant : lobe haut long, lobe bas plus court
    base = SPINE[-1]
    fin(rig, "Caudal", [base + Vector((0, -0.4, 0.3)), base + Vector((0, 0, 0)),
                        base + Vector((0, -0.4, -0.3))],
        [Vector((0, 8.9, 5.0)), Vector((0, 9.9, 6.3)), Vector((0, 9.15, 4.1)),
         Vector((0, 9.6, 1.8)), Vector((0, 8.7, 2.3))], "Caudal")
    rig.add(a.claw("CaudalTip", (0, 9.75, 6.15), (0, 0.4, 1), 0.3, 0.05, curl=0, segments=4),
            "Caudal", "horn")


def build_harpoons(rig):
    """Harpons rouillés plantés dans le dos, avec chaînes qui pendent."""
    for k, (i, s, d) in enumerate(((I(9), 1, (0.55, 0.35, 1)), (I(16), -1, (-0.5, 0.6, 1)))):
        bone = body_bone(i)
        base = SPINE[i] + Vector((s * 0.25, 0, 0.35))
        d = Vector(d).normalized()
        end = base + d * 2.0
        rig.add(r.tube(f"HarpoonShaft{k}", [tuple(base - d * 0.3), tuple(end)], 0.05, segments=6),
                bone, "rust")
        for b in (-1, 1):   # ailettes de la pointe, plantée dans l'os
            side, up = a._basis(d)
            rig.add(a.claw(f"HarpoonBarb{k}{b}", base + d * 0.05, d + side * b * 0.8, 0.25, 0.04,
                           curl=0, segments=4), bone, "rust")
        rig.add(a.ring_around(f"HarpoonEye{k}", end, d, 0.1, 0.03, segments=10), bone, "rust")
        # Chaîne : maillons alternés qui pendent vers le sol
        p = end + Vector((0, 0, -0.12))
        for j in range(5):
            axis = Vector((1, 0, 0)) if j % 2 == 0 else Vector((0, 1, 0))
            rig.add(a.ring_around(f"Chain{k}{j}", p, axis, 0.1, 0.025, segments=8), bone, "rust")
            p = p + Vector((0.05 * s, 0.04, -0.16))
        rig.add(r.ico(f"BloodGlow{k}", 0.08, subdivisions=1, location=base + d * 0.15), bone,
                "glow", glow=True)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_fins(rig)
    build_harpoons(rig)
    return rig
