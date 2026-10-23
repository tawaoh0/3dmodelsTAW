"""Tricératops squelette givré (≈ 13 studs de long, 7 de haut avec la collerette) — animable.

Identité propre (différente du T-Rex, du dragon et du raptor) :
- os givrés blanc-bleuté, croûtes et grappes de cristaux de glace sur le dos ;
- trois cornes de glace facettée (2 sourcilières, 1 nasale) aux pointes lumineuses,
  collerette géante percée de deux fenêtres et bordée d'éclats de glace ;
- quadrupède trapu et bas, tête énorme baissée pour charger, queue courte,
  pattes épaisses à sabots ;
- thème givre : stalactites qui pendent (côtes, mâchoire, collerette), cœur en
  grappe de cristaux gelés, effets Roblox « frost ».

2 pièces Roblox : corps, tête (crâne + collerette + cornes), plus le mesh lumineux.
Os du rig : Root, Hips, Spine, Neck, Head, Jaw, Tail1-3, UpperArm/Forearm/Hand_L/R,
Thigh/Shin/Foot_L/R, + FX_* (yeux, gueule, cœur, pointes des cornes).
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#d6e4ec",
    "bone_shade": "#93abbd",
    "tooth": "#eef6fa",
    "horn": "#1b2433",
    "horn_tip": "#3a7fb0",
    "ice": "#a8e4fa",
    "disc": "#20354a",
    "glow": "#4fd8ff",
    "glow_hot": "#e2fbff",
}

EFFECT_THEME = "frost"

TEST_POSE = {
    "Jaw": (25, 0, 0),
    "Neck": (-12, 0, 0),
    "Head": (-12, 0, 0),
    "UpperArm_L": (-30, 0, 0),
    "Forearm_L": (35, 0, 0),
    "Thigh_R": (-20, 0, 0),
    "Tail2": (0, 0, 20),
}

# Vue 3/4 de profil, un peu en hauteur : collerette et cornes ne se masquent pas
VIEW = (1.0, -0.55, 0.55)

# Dos qui descend des hanches (hautes) vers les épaules, tête baissée
BACK = [(0, 2.0, 4.0), (0, 0.5, 4.05), (0, -1.2, 3.65)]
NECK = [(0, -1.2, 3.65), (0, -1.8, 3.45), (0, -2.3, 3.35)]
TAIL = [(0, 2.0, 4.0), (0, 3.4, 3.6), (0, 4.8, 2.9), (0, 6.0, 2.2)]

# Crâne massif qui plonge vers un bec : (y, demi-larg. dessus, joues, bord, z dessus, z bas)
SKULL = [(-2.3, 0.7, 1.0, 0.85, 3.9, 2.6), (-2.8, 0.75, 1.05, 0.85, 4.05, 2.5),
         (-3.4, 0.6, 0.9, 0.72, 3.75, 2.4), (-4.0, 0.45, 0.68, 0.55, 3.35, 2.3),
         (-4.5, 0.38, 0.55, 0.45, 3.32, 2.2), (-5.0, 0.28, 0.4, 0.32, 3.0, 2.1),
         (-5.4, 0.15, 0.22, 0.18, 2.6, 2.05)]
JAW = [(-2.6, 0.6, 0.85, 0.7, 2.55, 1.95), (-3.5, 0.5, 0.72, 0.58, 2.45, 1.85),
       (-4.5, 0.35, 0.5, 0.4, 2.3, 1.9), (-5.3, 0.15, 0.22, 0.18, 2.15, 2.0)]

# Collerette : centre, axes du plan (x, et « haut » incliné vers l'arrière), rayons
FRILL_C = Vector((0, -2.25, 3.7))
FRILL_U = Vector((0, 0.62, 1)).normalized()
FRILL_RX, FRILL_RU = 2.3, 2.5


def width_at(sections, y, idx=3):
    for s0, s1 in zip(sections, sections[1:]):
        if s1[0] <= y <= s0[0]:
            t = (s0[0] - y) / (s0[0] - s1[0])
            return s0[idx] + (s1[idx] - s0[idx]) * t
    return sections[-1][idx]


def frill_point(theta, scale=1.0):
    """Point du bord de la collerette (theta = 0 côté gauche, π côté droit)."""
    return FRILL_C + Vector((math.cos(theta) * FRILL_RX * scale, 0, 0)) \
        + FRILL_U * math.sin(theta) * FRILL_RU * scale


def hole_along(center, axis, side, ra, rb, segments=12):
    """Cutter : tunnel elliptique traversant selon `axis` (rayons ra selon `side`)."""
    center, axis, side = Vector(center), Vector(axis).normalized(), Vector(side).normalized()
    other = axis.cross(side).normalized()
    rings = []
    for d in (-1.0, 1.0):
        rings.append([tuple(center + axis * d + side * math.cos(t) * ra + other * math.sin(t) * rb)
                      for t in (2 * math.pi * k / segments for k in range(segments))])
    return r.loft("Cutter", rings)


def icicle(rig, name, top, length, bone, radius=0.06, **kw):
    """Stalactite de glace lumineuse qui pend."""
    rig.add(a.claw(name, top, (0, 0, -1), length, radius, curl=0, segments=4), bone, "glow",
            glow=True)


def ice_cluster(rig, name, base, up, size, bone, seed=0, **kw):
    """Grappe de cristaux de glace qui pousse sur un os."""
    import random
    rnd = random.Random(seed)
    up = Vector(up).normalized()
    for k in range(3):
        d = (up + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), 0))).normalized()
        length = size * rnd.uniform(0.7, 1.2)
        rig.add(a.claw(f"{name}{k}", base, d, length, length * 0.22, curl=0, segments=4), bone,
                "ice", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 2.0, 4.0), (0, 0.3, 4.05), "Root")
    rig.bone("Spine", (0, 0.3, 4.05), (0, -1.2, 3.65), "Hips")
    rig.bone("Neck", (0, -1.2, 3.65), (0, -2.3, 3.35), "Spine")
    rig.bone("Head", (0, -2.3, 3.35), (0, -5.4, 2.6), "Neck")
    rig.bone("Jaw", (0, -2.6, 2.45), (0, -5.3, 2.05), "Head")
    parent = "Hips"
    for i in range(3):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"UpperArm_{side}", (s * 1.0, -1.0, 3.0), (s * 1.4, -0.85, 1.8), "Spine")
        rig.bone(f"Forearm_{side}", (s * 1.4, -0.85, 1.8), (s * 1.3, -1.2, 0.6),
                 f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", (s * 1.3, -1.2, 0.6), (s * 1.3, -1.8, 0.1), f"Forearm_{side}")
        rig.bone(f"Thigh_{side}", (s * 0.95, 1.8, 3.55), (s * 1.15, 1.1, 2.0), "Hips")
        rig.bone(f"Shin_{side}", (s * 1.15, 1.1, 2.0), (s * 1.15, 1.95, 0.8), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 1.15, 1.95, 0.8), (s * 1.15, 1.2, 0.1), f"Shin_{side}")
        rig.fx(f"Eye{side}", (s * 0.62, -3.25, 3.42), "Head")
        rig.fx(f"Horn{side}", (s * 0.95, -5.0, 5.25), "Head")
    rig.fx("Mouth", (0, -3.6, 2.4), "Head")
    rig.fx("Heart", (0, -0.2, 2.75), "Spine")


# ---------------------------------------------------------------- tête

def build_head(rig):
    head = dict(part="Head")
    skull = a.loft_profile("Skull", SKULL)
    a.cut(skull, [a.hole_x((0, -3.25, 3.42), 0.22, 0.22),        # orbites
                  a.hole_x((0, -4.2, 2.85), 0.24, 0.12),         # fenêtres antorbitales
                  a.hole_x((0, -4.95, 2.72), 0.18, 0.14)])       # grandes narines
    rig.add(skull, "Head", "bone", **head)

    # Bec corné supérieur (rostral) et inférieur (prédentaire), sombres
    rig.add(a.claw("Beak", (0, -5.25, 2.75), (0, -0.55, -1), 0.6, 0.24, curl=0.25, segments=5),
            "Head", "horn", **head)
    rig.add(a.claw("Predentary", (0, -5.2, 2.0), (0, -1, 0.35), 0.45, 0.16, curl=-0.2,
                   segments=5), "Jaw", "horn", **head)

    # Collerette géante : plaque épaisse en éventail, percée de 2 fenêtres
    # Contour convexe (centre + demi-ovale) : un contour qui se recoupe fausse le booléen
    outline = [(tuple(FRILL_C - FRILL_U * 0.3), {"Head": 1})]
    for k in range(17):
        theta = math.pi * k / 16
        outline.append((tuple(frill_point(theta)), {"Head": 1}))
    frill = a.membrane("Frill", outline, thickness=0.2)
    normal = Vector((0, 1, -0.62)).normalized()
    a.cut(frill, [hole_along(FRILL_C + Vector((s * 0.95, 0, 0)) + FRILL_U * 1.35, normal,
                             (1, 0, 0), 0.42, 0.6) for s in (-1, 1)])
    rig.pal.paint(frill, "bone")
    frill["part"] = "Head"
    # Nervure centrale (os pariétal) et rebord épaissi
    rig.add(r.tube("FrillRidge", [tuple(FRILL_C + FRILL_U * 0.2), tuple(FRILL_C + FRILL_U * 2.3)],
                   [0.17, 0.1], segments=6), "Head", "bone_shade", **head)
    rim = [tuple(frill_point(math.pi * k / 16, 0.97)) for k in range(17)]
    rig.add(r.tube("FrillRim", rim, 0.1, segments=5), "Head", "bone_shade", **head)
    # Éclats de glace tout autour du bord (époccipitaux)
    for k in range(2, 11):   # pas aux extrémités basses : ils pointeraient à l'horizontale
        theta = math.pi * k / 12
        p = frill_point(theta, 0.98)
        out = (p - FRILL_C).normalized()
        rig.add(a.claw(f"FrillShard{k}", p, out, 0.55 if k % 2 else 0.38, 0.11, curl=0,
                       segments=4), "Head", "ice", **head)
    # Stalactites sous les bords bas de la collerette
    for s in (-1, 1):
        p = frill_point(math.pi * (0.08 if s > 0 else 0.92), 0.95)
        icicle(rig, f"FrillIcicle{s}", p, 0.5, "Head", radius=0.07)

    for s in (-1, 1):
        # Grandes cornes sourcilières en glace facettée, pointes lumineuses
        base = Vector((s * 0.5, -2.95, 3.95))
        d = Vector((s * 0.22, -0.75, 0.75)).normalized()
        rig.add(a.claw(f"BrowHorn{s}", base, d, 2.3, 0.3, curl=-0.25, segments=5), "Head", "ice",
                **head)
        rig.add(r.tube(f"BrowHornBase{s}", [tuple(base - d * 0.1), tuple(base + d * 0.25)],
                       [0.36, 0.32], segments=5), "Head", "bone_shade", **head)
        # Pointe lumineuse posée sur la courbe réelle de la corne
        tip_base, tip_dir = a.claw_point(base, d, 2.3, -0.25, 0.8)
        rig.add(a.claw(f"BrowHornTip{s}", tip_base, tip_dir, 2.3 * 0.24, 0.07, curl=-0.1,
                       segments=4), "Head", "glow", glow=True)
        # Œil glacé au fond de l'orbite, arcade givrée au-dessus
        rig.add(r.ico(f"Eye{s}", 0.13, subdivisions=2, location=(s * 0.6, -3.25, 3.42)),
                "Head", "glow", glow=True)
        rig.add(a.blade(f"Brow{s}", (s * 0.3, -3.55, 3.82), (s * 0.85, -3.0, 3.9), 0.28, 0.14,
                        width_end=0.2, mid=0.34, normal=(0, 0.3, 1)), "Head", "bone_shade",
                **head)
        # Pommettes en pointe vers le bas et l'extérieur (épijugaux)
        rig.add(a.claw(f"Jugal{s}", (s * 0.9, -3.0, 2.6), (s * 0.8, 0.1, -0.5), 0.55, 0.15,
                       curl=0, segments=5), "Head", "ice", **head)
        # Stalactites sous la mâchoire
        for k, y in enumerate((-3.2, -4.0)):
            icicle(rig, f"JawIcicle{s}{k}", (s * width_at(JAW, y) * 0.8, y, 1.92), 0.35 - k * 0.08,
                   "Jaw", radius=0.05)

    # Corne nasale courte et épaisse
    rig.add(a.claw("NoseHorn", (0, -4.55, 3.25), (0, -0.4, 1), 0.85, 0.2, curl=-0.15, segments=5),
            "Head", "ice", **head)
    # Gorge glacée
    rig.add(r.ico("FrostThroat", 0.25, subdivisions=2, location=(0, -3.0, 2.45),
                  scale=(1.3, 1.3, 0.5)), "Head", "glow", glow=True)

    # Dents broyeuses en rangée serrée (herbivore)
    for jaw, sections, z, direction, bone in ((False, SKULL, 2.42, (0, 0.1, -1), "Head"),
                                              (True, JAW, 2.42, (0, -0.1, 1), "Jaw")):
        y, k = -4.6, 0
        while y < -2.9:
            for s in (-1, 1):
                x = s * width_at(sections, y) * 0.75
                rig.add(a.claw(f"Tooth{bone}{s}{k}", (x, y, z), direction, 0.14, 0.06, curl=0,
                               segments=4), bone, "tooth", **head)
            y += 0.24
            k += 1

    jaw = a.loft_profile("Jaw", JAW)
    a.cut(jaw, [a.hole_x((0, -3.3, 2.2), 0.3, 0.1)])
    rig.add(jaw, "Jaw", "bone", **head)



# Repère de la collerette : X (largeur), FRILL_U (hauteur inclinée), FRILL_F (face avant)
FRILL_X = Vector((1, 0, 0))
FRILL_F = FRILL_X.cross(FRILL_U).normalized()   # vers l'avant et le haut
HOLES = [(s * 0.95, 1.35) for s in (-1, 1)]      # (x, u) des fenêtres, rayons 0.42 × 0.6


def on_frill(x, u, off=0.11):
    """Point posé sur la face avant de la collerette (épaisseur 0.2)."""
    return FRILL_C + FRILL_X * x + FRILL_U * u + FRILL_F * off


def frill_polar(theta, k):
    """Point à la fraction k (0 = centre, 1 = bord) le long du rayon d'angle theta."""
    return math.cos(theta) * FRILL_RX * k, math.sin(theta) * FRILL_RU * k


def build_frill_details(rig):
    head = dict(part="Head")
    # Bourrelets osseux autour des deux fenêtres
    for k, (hx, hu) in enumerate(HOLES):
        ring = [tuple(on_frill(hx + math.cos(t) * 0.47, hu + math.sin(t) * 0.66, 0.1))
                for t in (2 * math.pi * i / 14 for i in range(14))]
        rig.add(r.tube(f"HoleRim{k}", ring, 0.07, segments=5, closed=True), "Head", "bone_shade",
                **head)
    # Nervures rayonnantes (comme les baleines d'un éventail), entre les fenêtres
    for k, theta in enumerate((0.13, 0.4, 0.6, 0.87)):
        theta *= math.pi
        pts = [tuple(on_frill(*frill_polar(theta, f), 0.1)) for f in (0.22, 0.55, 0.9)]
        rig.add(r.tube(f"FrillRib{k}", pts, [0.09, 0.07, 0.05], segments=5), "Head",
                "bone_shade", **head)
    # Nodules osseux (époccipitaux) entre les éclats de glace du bord
    for k in range(2, 10):
        theta = math.pi * (k + 0.5) / 12
        p = frill_point(theta, 0.97) + FRILL_F * 0.04
        rig.add(r.ico(f"Epoccipital{k}", 0.16, subdivisions=1, location=p, scale=(1, 0.7, 1)),
                "Head", "bone", **head)
    # Veines de givre lumineuses qui partent du centre vers le bord, en zigzag
    for k, theta in enumerate((0.27, 0.5, 0.73)):
        theta *= math.pi
        pts = []
        for i, f in enumerate((0.15, 0.35, 0.55, 0.75, 0.92)):
            x, u = frill_polar(theta + (0.07 if i % 2 else -0.07), f)
            pts.append(tuple(on_frill(x, u, 0.115)))
        rig.add(r.tube(f"FrostVein{k}", pts, 0.028, segments=4), "Head", "glow", glow=True)
    # Croûtes de cristaux de glace sur la collerette
    for k, (x, u) in enumerate(((1.6, 0.55), (-1.6, 0.55), (0.45, 2.05), (-0.45, 2.05))):
        ice_cluster(rig, f"FrillIce{k}", on_frill(x, u, 0.08), FRILL_F + FRILL_U * 0.3, 0.32,
                    "Head", seed=40 + k, **head)
    # Stalactites supplémentaires sous le bord bas
    for s in (-1, 1):
        p = frill_point(math.pi * (0.17 if s > 0 else 0.83), 0.96)
        icicle(rig, f"FrillIcicleB{s}", p, 0.38, "Head", radius=0.055)


def build_skull_details(rig):
    head = dict(part="Head")
    for s in (-1, 1):
        # Cercle osseux autour de l'orbite
        x = s * (width_at(SKULL, -3.25, 2) - 0.02)
        ring = [(x, -3.25 + math.cos(t) * 0.28, 3.42 + math.sin(t) * 0.28)
                for t in (2 * math.pi * i / 12 for i in range(12))]
        rig.add(r.tube(f"OrbitRim{s}", ring, 0.055, segments=5, closed=True), "Head",
                "bone_shade", **head)
        # Bosse sus-orbitaire hérissée de cristaux, au pied de la grande corne
        rig.add(r.ico(f"BrowBoss{s}", 0.26, subdivisions=1, location=(s * 0.62, -3.1, 3.9),
                      scale=(1, 1.3, 0.7)), "Head", "bone_shade", **head)
        ice_cluster(rig, f"BrowIce{s}", (s * 0.8, -3.0, 4.0), (s * 1, 0.4, 0.8), 0.3, "Head",
                    seed=60 + s, **head)
        # Anneaux d'os autour des grandes cornes (fourreau)
        base = Vector((s * 0.5, -2.95, 3.95))
        d = Vector((s * 0.22, -0.75, 0.75)).normalized()
        for k, t in enumerate((0.18, 0.36)):
            p, tan = a.claw_point(base, d, 2.3, -0.25, t)
            rad = 0.3 * (1 - t) ** 0.8 + 0.035
            side = tan.cross(Vector((0, 0, 1))).normalized()
            other = tan.cross(side).normalized()
            ring = [tuple(p + side * math.cos(a_) * rad + other * math.sin(a_) * rad)
                    for a_ in (2 * math.pi * i / 10 for i in range(10))]
            rig.add(r.tube(f"HornBand{s}{k}", ring, 0.045, segments=4, closed=True), "Head",
                    "bone_shade", **head)
        # Bosses rugueuses alignées sur les flancs du museau
        for k, y in enumerate((-3.9, -4.3, -4.7)):
            z = (width_at(SKULL, y, 4) + width_at(SKULL, y, 5)) / 2 + 0.15
            rig.add(r.ico(f"SnoutKnob{s}{k}", 0.1 - k * 0.015, subdivisions=1,
                          location=(s * width_at(SKULL, y, 2) * 0.97, y, z), scale=(0.6, 1, 1)),
                    "Head", "bone_shade", **head)
        # Bosse de la pommette sous la pointe de glace
        rig.add(r.ico(f"JugalBoss{s}", 0.2, subdivisions=1, location=(s * 0.88, -3.0, 2.62),
                      scale=(0.8, 1.1, 0.9)), "Head", "bone_shade", **head)
        # Mâchoire : crête le long du bord et apophyse coronoïde
        rig.add(r.tube(f"JawRidge{s}", [(s * width_at(JAW, y, 2) * 0.98, y, 2.12)
                                        for y in (-2.8, -3.6, -4.4)], [0.06, 0.07, 0.05],
                       segments=5), "Jaw", "bone_shade", **head)
        rig.add(a.blade(f"Coronoid{s}", (s * 0.6, -2.95, 2.3), (s * 0.62, -2.7, 2.75), 0.35, 0.1,
                        width_end=0.2, normal=(1, 0, 0), bevel=0), "Jaw", "bone_shade", **head)
    # Arête nasale de la corne du nez jusqu'au bec
    ridge = [(0, y, width_at(SKULL, y, 4) + 0.02) for y in (-4.6, -4.85, -5.1)]
    rig.add(r.tube("NasalRidge", ridge, [0.11, 0.09, 0.07], segments=5), "Head", "bone_shade",
            **head)
    # Bague d'os à la base de la corne du nez
    ring = [(math.cos(t) * 0.24, -4.55 + math.sin(t) * 0.24, 3.3)
            for t in (2 * math.pi * i / 10 for i in range(10))]
    rig.add(r.tube("NoseHornRing", ring, 0.05, segments=4, closed=True), "Head", "bone_shade",
            **head)
    # Cristaux entre les cornes, sur le haut du crâne
    ice_cluster(rig, "CrownIce", (0, -2.85, 4.05), (0, 0.3, 1), 0.4, "Head", seed=77, **head)
    # Veine de givre lumineuse du front jusqu'au museau
    vein = [(0.08 * (1 if i % 2 else -1), y, width_at(SKULL, y, 4) + 0.025)
            for i, y in enumerate((-3.1, -3.45, -3.8, -4.15))]
    rig.add(r.tube("SkullVein", vein, 0.03, segments=4), "Head", "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_spine(rig):
    back = c.Chain(BACK)
    for i in range(8):
        p, t = back.at(i / 7)
        bone = "Hips" if p.y > 0.3 else "Spine"
        rig.add(a.vertebra(f"Back{i}", p, -t, 0.42, spine=0.8, lean=0.15), bone, "bone")
        if i < 7:
            q, tq = back.at((i + 0.5) / 7)
            rig.add(a.disc(f"BackDisc{i}", q, tq, 0.42), bone, "disc")
        if i % 2 == 0:   # grappes de cristaux de glace sur l'échine
            ice_cluster(rig, f"BackIce{i}", p + Vector((0, 0, 0.9)), (0, 0.2, 1), 0.7, bone, seed=i)

    neck = c.Chain(NECK)
    for i in range(3):
        p, t = neck.at(i / 2)
        rig.add(a.vertebra(f"Neck{i}", p, -t, 0.4, spine=0.4, lean=0.1), "Neck", "bone")
        if i < 2:
            q, tq = neck.at((i + 0.5) / 2)
            rig.add(a.disc(f"NeckDisc{i}", q, tq, 0.4), "Neck", "disc")

    tail = c.Chain(TAIL)
    n = 13   # assez de vertèbres pour qu'elles se touchent jusqu'au bout de la queue
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(3, int(t * 3 * 0.999) + 1)}"
        size = 0.38 - 0.24 * t
        rig.add(a.vertebra(f"Tail{i}", p, tan, size, spine=0.8 - 0.4 * t, lean=-0.2,
                           transverse=i < 6), bone, "bone")
        if i < n - 1:
            q, tq = tail.at((i + 0.5) / (n - 1))
            rig.add(a.disc(f"TailDisc{i}", q, tq, size), bone, "disc")
        if i < 9:
            down = p - Vector((0, -0.05, size * 0.4))
            rig.add(a.blade(f"Chevron{i}", down, down + Vector((0, 0.25, -size * 1.6)),
                            size * 0.45, size * 0.16, width_end=size * 0.2, normal=(1, 0, 0),
                            bevel=0), bone, "bone_shade")
    tip, tan = tail.at(1.0)
    ice_cluster(rig, "TailIce", tip, tan + Vector((0, 0, 0.3)), 0.5, "Tail3", seed=9)


def build_ribcage(rig):
    back = c.Chain(BACK)
    for i in range(8):
        t = 0.1 + 0.85 * i / 7
        p, _ = back.at(t)
        bone = "Hips" if p.y > 0.3 else "Spine"
        bulge = math.sin((i + 1) / 9 * math.pi)
        hw, depth = 0.95 + 0.55 * bulge, 1.5 + 0.55 * bulge
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{i}{s}", p + Vector((0, 0, -0.1)), hw, depth, s, sweep=-0.2,
                          radius=0.12), bone, "bone")
            if i in (2, 4, 6):   # stalactites sous le flanc
                icicle(rig, f"RibIcicle{i}{s}", p + Vector((s * hw * 0.85, -0.15, -depth * 0.62)),
                       0.4, bone, radius=0.055)
    rig.add(a.blade("Sternum", (0, -1.0, 2.15), (0, 0.4, 2.0), 0.8, 0.12, width_end=0.5,
                    normal=(0, 0, 1)), "Spine", "bone_shade")
    # Cœur gelé : grappe de cristaux lumineux
    for k, (dx, dy, dz, rad, h) in enumerate(((0, 0, 0, 0.3, 0.95), (0.3, 0.15, 0.1, 0.15, 0.55),
                                              (-0.28, -0.1, 0.05, 0.14, 0.5),
                                              (0.05, 0.3, -0.25, 0.12, 0.45))):
        rig.add(a.crystal(f"FrozenHeart{k}", (dx, -0.2 + dy, 2.75 + dz), rad, h, sides=5),
                "Spine", "glow", glow=True)


# ---------------------------------------------------------------- pattes

def hooves(rig, name, wrist, base_y, side_x, bone, count, spread, length):
    for k in range(count):
        dx = (k - (count - 1) / 2) * spread
        base = Vector((side_x + dx, base_y, 0.22))
        rig.add(a.long_bone(f"{name}Meta{k}", wrist, base, 0.08, knob=1.5, condyles=False),
                bone, "bone")
        tip = base + Vector((dx * 0.3, -length, -0.05))
        rig.add(a.long_bone(f"{name}Phal{k}", base, tip, 0.075, knob=1.4, condyles=False),
                bone, "bone")
        # Sabot sombre et émoussé
        rig.add(r.ico(f"{name}Hoof{k}", 0.12, subdivisions=1, location=tip + Vector((0, -0.05, -0.04)),
                      scale=(1, 1.3, 0.7)), bone, "horn")


def build_front_leg(rig, s, side):
    shoulder, elbow, wrist = Vector((s * 1.0, -1.0, 3.0)), Vector((s * 1.4, -0.85, 1.8)), \
        Vector((s * 1.3, -1.2, 0.6))
    rig.add(a.blade(f"Scapula{s}", (s * 0.95, -1.0, 3.1), (s * 0.95, 0.2, 3.9), 0.6, 0.14,
                    width_end=0.4, normal=(s, 0, 0.4)), "Spine", "bone")
    rig.add(a.long_bone(f"Humerus{s}", shoulder, elbow, 0.22), f"UpperArm_{side}", "bone")
    rig.add(a.long_bone(f"Radius{s}", elbow, wrist, 0.17), f"Forearm_{side}", "bone")
    rig.add(a.long_bone(f"Ulna{s}", elbow + Vector((s * 0.2, 0.15, 0.1)),
                        wrist + Vector((s * 0.16, 0.08, 0.1)), 0.08, condyles=False),
            f"Forearm_{side}", "bone_shade")
    rig.add(r.ico(f"Wrist{s}", 0.22, subdivisions=1, location=wrist), f"Hand_{side}", "bone_shade")
    hooves(rig, f"Hand{s}", wrist, -1.5, s * 1.3, f"Hand_{side}", 4, 0.17, 0.25)


def build_hind_leg(rig, s, side):
    hip, knee, ankle = Vector((s * 0.95, 1.8, 3.55)), Vector((s * 1.15, 1.1, 2.0)), \
        Vector((s * 1.15, 1.95, 0.8))
    rig.add(a.blade(f"Ilium{s}", (s * 0.6, 0.6, 4.05), (s * 0.6, 3.1, 4.1), 0.5, 0.15,
                    width_end=0.4, mid=1.2, normal=(1, 0.0, 0.5)), "Hips", "bone")
    rig.add(r.ico(f"Acetabulum{s}", 0.3, subdivisions=1, location=hip), "Hips", "bone_shade")
    rig.add(a.long_bone(f"Pubis{s}", (s * 0.6, 1.4, 3.5), (s * 0.35, 0.7, 2.6), 0.09,
                        condyles=False), "Hips", "bone_shade")
    rig.add(a.long_bone(f"Femur{s}", hip, knee, 0.26), f"Thigh_{side}", "bone")
    ice_cluster(rig, f"KneeIce{s}", knee + Vector((s * 0.25, -0.15, 0.1)), (s * 1, -0.5, 0.6), 0.4,
                f"Shin_{side}", seed=20 + s)
    rig.add(a.long_bone(f"Tibia{s}", knee, ankle, 0.2), f"Shin_{side}", "bone")
    rig.add(a.long_bone(f"Fibula{s}", knee + Vector((s * 0.25, 0.1, -0.12)),
                        ankle + Vector((s * 0.2, 0, 0.1)), 0.08, condyles=False), f"Shin_{side}",
            "bone_shade")
    rig.add(r.ico(f"Ankle{s}", 0.24, subdivisions=1, location=ankle), f"Foot_{side}",
            "bone_shade")
    hooves(rig, f"Foot{s}", ankle, 1.0, s * 1.15, f"Foot_{side}", 4, 0.2, 0.3)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_frill_details(rig)
    build_skull_details(rig)
    build_spine(rig)
    build_ribcage(rig)
    for s, side in ((1, "L"), (-1, "R")):
        build_front_leg(rig, s, side)
        build_hind_leg(rig, s, side)
    return rig
