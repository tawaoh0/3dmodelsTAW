"""Mégalodon squelette (≈ 15 studs de long, 6 de haut) — créature animable.
Pack « Abysses », créature 2.

Animal modèle : le grand requin blanc géant — mâchoires en fer à cheval à 3 rangées de
dents triangulaires, rostre arrondi, petits yeux, évents, 5 arcs branchiaux, grande dorsale,
pectorales en ailes, queue en croissant (lobe haut plus long), denticules cutanés.

Identité : os ardoise sombre et dents claires ; pas de cornes mais des harpons et hameçons
rouillés plantés dans le corps et la mâchoire, avec leurs chaînes ; cicatrices rougeoyantes ;
silhouette horizontale en nage ; lueur rouge sang, thème d'effets « blood ».

3 pièces Roblox : corps, tête (crâne + mâchoires + branchies), nageoires, + lumineux.
Os : Root, Body1-5, Head, Jaw, Caudal, PecFin_L/R, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#56616c",
    "bone_shade": "#3a434c",
    "tooth": "#ece6d6",
    "horn": "#d8d2c4",
    "horn_tip": "#a8323a",
    "disc": "#2a1f24",
    "membrane": "#262c33",
    "gum": "#5a2a30",
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
HEAD = dict(part="Head")


def I(k):
    """Index de vertèbre exprimé sur une colonne de référence à 26 vertèbres."""
    return round(k * (len(SPINE) - 1) / 25)


def body_bone(i):
    return f"Body{min(5, i * 5 // (len(SPINE) - 1) + 1)}"


def horseshoe(width, length, z, y_back=-3.0, n=15):
    """Arc en fer à cheval (mâchoire de requin) dans le plan horizontal z."""
    pts = []
    for i in range(n):
        th = -math.pi / 2 + math.pi * i / (n - 1)
        pts.append(Vector((width * math.sin(th), y_back - length * math.cos(th), z)))
    return pts


def skull_surface(y, side, frac):
    """Point sur le dessus/flanc du crâne : frac 0 = milieu du dessus, 1 = flanc."""
    zt, zb = a.width_at(SKULL, y, 4), a.width_at(SKULL, y, 5)
    z = zt - (zt - zb) * 0.35 * frac
    return Vector((side * a.side_width(SKULL, y, z) * frac * 0.98, y, z if frac else zt))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    n = len(SPINE) - 1
    for b in range(5):
        parent = rig.bone(f"Body{b + 1}", SPINE[b * n // 5], SPINE[(b + 1) * n // 5], parent)
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

def build_skull(rig):
    H = "Head"
    skull = a.loft_profile("Skull", SKULL, droop=0.12)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.15, 0.13)]
          + [a.hole_along((sx * 0.22, -5.25, 2.97), (0, 0.3, 1), (1, 0, 0), 0.07, 0.12, depth=0.2)
             for sx in (-1, 1)])
    rig.add(skull, H, "bone", **HEAD)
    # Crête sagittale + crêtes latérales hérissées de denticules
    rig.add(r.tube("SkullRidge", [tuple(skull_surface(yy, 0, 0) + Vector((0, 0, 0.02)))
                                  for yy in (-3.0, -3.8, -4.6, -5.2)], [0.06, 0.08, 0.07, 0.05],
                   segments=5), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        ridge = [skull_surface(yy, s, 0.55) for yy in (-2.95, -3.5, -4.1, -4.7, -5.15)]
        rig.add(r.tube(f"LatRidge{s}", [tuple(p) for p in ridge], [0.05, 0.06, 0.06, 0.05, 0.03],
                       segments=4), H, "bone_shade", **HEAD)
        for i, p in enumerate(ridge[:-1]):
            rig.add(a.claw(f"Denticle{s}{i}", p, (s * 0.4, 0.7, 0.6), 0.16, 0.035, curl=0,
                           segments=4), H, "horn", **HEAD)
        # Écailles osseuses en losange entre les crêtes
        pts = [skull_surface(yy, s, 0.28) + Vector((0, 0, 0.01)) for yy in (-3.2, -3.7, -4.3, -4.85)]
        mr.scutes(rig, f"Scute{s}", pts, [Vector((s * 0.3, 0, 1))] * len(pts), H, size=0.08,
                  **HEAD)
        # Œil : orbite hérissée, arcade à piques, évent derrière l'œil
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.12, subdivisions=2, location=(s * (x - 0.06), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, 0, 0), 0.19, H, **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.3, -4.5, 3.78), (s * 0.62, -3.7, 3.82), 0.22, 0.1,
                        width_end=0.16, mid=0.28, normal=(0, 0.15, 1)), H, "bone_shade", **HEAD)
        for i in range(3):
            rig.add(a.claw(f"BrowSpike{s}{i}", (s * (0.36 + 0.1 * i), -4.35 + 0.3 * i, 3.85),
                           (s * 0.4, 0.7, 0.5), 0.2, 0.035, curl=-0.1, segments=4), H, "horn",
                    **HEAD)
        spir = Vector((s * a.side_width(SKULL, -3.45, 3.4), -3.45, 3.4))
        rig.add(a.ring_around(f"Spiracle{s}", spir, (s, 0, 0), 0.08, 0.03, segments=8), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"SpiracleGlow{s}", 0.05, subdivisions=1, location=spir), H, "glow",
                glow=True)
        # Pores électrorécepteurs (ampoules de Lorenzini) sur le rostre
        for i in range(8):
            yy = -4.65 - 0.1 * i
            zz = 3.15 + 0.15 * math.sin(i * 1.7)
            rig.add(r.ico(f"Pore{s}{i}", 0.032, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy, zz), yy, zz)), H, "ink", **HEAD)
        # Rebords des narines sous le rostre
        rig.add(a.ring_around(f"NostrilRim{s}", (s * 0.22, -5.25, 2.95), (0, 0.3, 1), 0.1, 0.03,
                              segments=8), H, "bone_shade", **HEAD)
        # Cicatrices rougeoyantes sur le flanc du crâne
        mr.scar(rig, f"Scar{s}", skull_surface(-3.2, s, 0.85), skull_surface(-4.0, s, 0.7), H,
                seed=s + 3)
        mr.scar(rig, f"ScarB{s}", skull_surface(-3.6, s, 0.95), skull_surface(-4.3, s, 0.95), H,
                width=0.05, seed=s + 7)
        # 5 arcs branchiaux en C, branchiospines, filaments et fentes rougeoyantes
        for g in range(5):
            yy = -2.45 + 0.27 * g
            arc = [(s * 0.5, yy, 3.4), (s * 0.85, yy + 0.05, 2.75), (s * 0.78, yy, 2.15),
                   (s * 0.4, yy - 0.05, 1.95)]
            rig.add(r.tube(f"Gill{s}{g}", arc, [0.05, 0.065, 0.06, 0.04], segments=5), H,
                    "bone_shade", **HEAD)
            for k in range(4):
                p = mr.along(arc, 0.2 + 0.2 * k)
                rig.add(a.claw(f"Raker{s}{g}{k}", p, (-s, 0.1, 0.1), 0.16, 0.025, curl=0,
                               segments=4), H, "horn", **HEAD)
                rig.add(a.claw(f"Filament{s}{g}{k}", p, (s, 0.4, 0), 0.14, 0.02, curl=0.2,
                               segments=4), H, "gum", **HEAD)
            if g < 4:
                rig.add(r.tube(f"GillGlow{s}{g}", [(s * 0.62, yy + 0.13, 3.2),
                                                   (s * 0.86, yy + 0.15, 2.75),
                                                   (s * 0.74, yy + 0.13, 2.2)], 0.025, segments=4),
                        H, "glow", glow=True)
    # Carène sous le rostre
    rig.add(r.tube("RostrumKeel", [(0, -4.3, 2.8), (0, -4.9, 2.86), (0, -5.35, 2.92)],
                   [0.06, 0.05, 0.03], segments=4), H, "bone_shade", **HEAD)


def build_jaws(rig):
    H, J = "Head", "Jaw"
    upper = horseshoe(0.78, 2.0, 2.72)
    lower = horseshoe(0.82, 2.05, 2.12)
    rig.add(r.tube("UpperJaw", [tuple(p) for p in upper], 0.15, segments=6), H, "bone_shade", **HEAD)
    rig.add(r.tube("LowerJaw", [tuple(p) for p in lower], 0.17, segments=6), J, "bone", **HEAD)
    rig.add(r.tube("LowerJawBase", [tuple(p - Vector((0, 0, 0.22))) for p in lower[2:-2]], 0.1,
                   segments=5), J, "bone_shade", **HEAD)
    # Gencives sombres à l'intérieur des arcs
    rig.add(r.tube("UpperGum", [tuple(Vector((p.x * 0.85, p.y * 0.98 - 0.06, 2.66))) for p in upper],
                   0.07, segments=5), H, "gum", **HEAD)
    rig.add(r.tube("LowerGum", [tuple(Vector((p.x * 0.85, p.y * 0.98 - 0.06, 2.2))) for p in lower],
                   0.08, segments=5), J, "gum", **HEAD)
    # Alvéoles : bosses à l'extérieur de chaque dent, et 3 rangées de dents triangulaires
    for jaw_pts, z, bone in ((upper, 2.72, H), (lower, 2.12, J)):
        for i in range(1, 14):
            p = jaw_pts[i]
            out = Vector((p.x, p.y + 3.0, 0)).normalized() if (p.x or p.y + 3.0) else Vector((0, -1, 0))
            rig.add(r.ico(f"Socket{bone}{i}", 0.07, subdivisions=1, location=p + out * 0.14),
                    bone, "bone_shade", **HEAD)
    for row in range(3):
        sc = 1 - 0.13 * row
        for jaw_pts, down, bone in ((horseshoe(0.78 - 0.1 * row, 2.0 - 0.15 * row, 2.62), -1, H),
                                    (horseshoe(0.82 - 0.1 * row, 2.05 - 0.15 * row, 2.25), 1, J)):
            for i in range(1, 14):
                p = jaw_pts[i]
                front = 1 - abs(i - 7) / 7
                size = (0.18 + 0.16 * front) * sc
                inward = Vector((-p.x, 0, 0)).normalized() * 0.2 if abs(p.x) > 1e-4 else Vector()
                tip = p + Vector((0, 0, down * size)) + inward * row + Vector((0, 0.05 * row, 0))
                rig.add(a.blade(f"Tooth{bone}{row}{i}", p, tip, size * 0.75, 0.035, width_end=0.01,
                                normal=(p.x, -(p.y + 3.0), 0) if (abs(p.x) > 1e-4 or abs(p.y + 3.0) > 1e-4) else (0, -1, 0),
                                bevel=0), bone, "tooth", **HEAD)
    for s in (-1, 1):
        # Charnières : grosses rotules + ligaments entre mâchoire haute et basse
        rig.add(r.ico(f"Hinge{s}", 0.2, subdivisions=1, location=(s * 0.8, -3.05, 2.42)), H,
                "bone", **HEAD)
        for k, dy in enumerate((-0.12, 0.1)):
            rig.add(r.tube(f"Ligament{s}{k}", [(s * 0.78, -3.1 + dy, 2.7), (s * 0.84, -3.1 + dy, 2.42),
                                               (s * 0.8, -3.1 + dy, 2.12)], 0.035, segments=4), J,
                    "gum", **HEAD)
        # Hameçons rouillés plantés dans la mâchoire, avec leur chaîne
        mr.hook(rig, f"JawHook{s}", (s * 0.62, -4.4, 1.95), (s * 0.3, -0.4, -1), J, chain=3, **HEAD)
    # Langue osseuse (basihyal) et gorge rougeoyante
    rig.add(a.blade("Tongue", (0, -3.2, 2.2), (0, -4.3, 2.18), 0.4, 0.08, width_end=0.22,
                    normal=(0, 0, 1)), J, "bone_shade", **HEAD)
    rig.add(r.ico("Throat", 0.3, subdivisions=2, location=(0, -3.4, 2.45), scale=(1.4, 1, 0.5)), H,
            "glow", glow=True)
    rig.add(a.blade("ChinPlate", (0, -4.6, 1.92), (0, -5.0, 1.85), 0.45, 0.08, width_end=0.25,
                    normal=(0, -0.3, 1)), J, "bone_shade", **HEAD)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i, p in enumerate(SPINE):
        t = i / (n - 1)
        nxt, prv = SPINE[min(i + 1, n - 1)], SPINE[max(i - 1, 0)]
        tan = (nxt - prv).normalized()
        size = 0.42 - 0.22 * t
        bone = body_bone(i)
        rig.add(a.vertebra(f"V{i}", p, tan, size, spine=0.8 - 0.4 * t, lean=-0.3,
                           transverse=t < 0.55), bone, "bone")
        if i < n - 1:
            rig.add(a.disc(f"VD{i}", p.lerp(nxt, 0.5), tan, size), bone, "disc")
        top = p + Vector((0, 0, size * 0.7 + size * (0.8 - 0.4 * t)))
        if i % 2 == 0:   # denticules crochus le long du dos
            rig.add(a.claw(f"Dent{i}", top - Vector((0, 0, 0.05)), (0, 0.8, 0.6), 0.22, 0.04,
                           curl=0.2, segments=4), bone, "horn")
        for s in (-1, 1):
            if i % 2 == 1 and t < 0.55:   # ligne latérale lumineuse, au bout des apophyses
                rig.add(r.ico(f"Lateral{i}{s}", 0.05, subdivisions=1,
                              location=p + Vector((s * size * 1.0, 0, size * 0.5))), bone, "glow",
                        glow=True)
            if 0.04 <= t <= 0.36 and i % 2 == 0:   # côtes courtes à petite pique
                rig.add(a.rib(f"Rib{i}{s}", p - Vector((0, 0, 0.1)), 0.55, 0.9, s, sweep=-0.15,
                              radius=0.06, segments=5), bone, "bone")
                rig.add(a.claw(f"RibSpike{i}{s}", p + Vector((s * 0.6, 0, -0.45)), (s, 0.3, 0),
                               0.16, 0.03, curl=0, segments=4), bone, "horn")
        if t >= 0.48 and i % 2 == 0:   # arcs hémaux sous la queue
            down = p - Vector((0, 0, size * 0.4))
            rig.add(a.blade(f"Haemal{i}", down, down + Vector((0, 0.25, -size * 1.6)), size * 0.45,
                            size * 0.15, width_end=size * 0.2, normal=(1, 0, 0), bevel=0), bone,
                    "bone_shade")
    # Ceinture scapulaire : arc sous le ventre qui relie les deux pectorales
    girdle = [(0.6, -1.15, 2.6), (0.5, -1.2, 2.15), (0, -1.25, 1.95), (-0.5, -1.2, 2.15),
              (-0.6, -1.15, 2.6)]
    rig.add(r.tube("ScapularGirdle", girdle, 0.08, segments=6), "Body1", "bone")
    for s in (-1, 1):
        rig.add(r.tube(f"Scapula{s}", [(s * 0.6, -1.15, 2.6), (s * 0.5, -1.0, 3.4)], [0.07, 0.04],
                       segments=5), "Body1", "bone")
    rig.add(r.tube("PelvicGirdle", [tuple(SPINE[I(14)] + Vector((s * 0.35, 0, -0.5))) for s in (1, -1)],
                   0.06, segments=5), body_bone(I(14)), "bone")
    # Cœur de sang derrière les branchies + veines
    rig.add(a.crystal("Heart", (0, -1.6, 2.65), 0.25, 0.7), "Body1", "glow", glow=True)
    for s in (-1, 1):
        rig.add(r.tube(f"Vein{s}", [(0, -1.6, 2.65), (s * 0.3, -2.1, 2.5), (s * 0.4, -2.5, 2.4)],
                       0.03, segments=4), "Body1", "glow", glow=True)


def build_fins(rig):
    F = "Fins"
    top = lambda i, dz=0.55: SPINE[i] + Vector((0, 0, dz))  # noqa: E731
    bot = lambda i: SPINE[i] - Vector((0, 0, 0.45))  # noqa: E731
    mr.fin(rig, "Dorsal", [top(I(7)), top(I(9)), top(I(11))],
           [top(I(7)) + Vector((0, 0.6, 1.5)), top(I(8)) + Vector((0, 1.3, 2.6)),
            top(I(10)) + Vector((0, 1.6, 1.6)), top(I(11)) + Vector((0, 1.1, 0.5))], "Body2",
           part=F, rays=10, seed=1)
    mr.fin(rig, "Dorsal2", [top(I(19), 0.35), top(I(21), 0.35)],
           [top(I(19)) + Vector((0, 0.6, 0.7)), top(I(21)) + Vector((0, 0.5, 0.2))], "Body4",
           part=F, rays=4, seed=2)
    mr.fin(rig, "Anal", [bot(I(19)), bot(I(21))], [bot(I(19)) + Vector((0, 0.6, -0.7)),
                                                    bot(I(21)) + Vector((0, 0.5, -0.25))], "Body4",
           part=F, rays=4, seed=3)
    for s, side in ((1, "L"), (-1, "R")):
        root = [Vector((s * 0.55, -1.6, 2.55)), Vector((s * 0.6, -1.15, 2.55)),
                Vector((s * 0.55, -0.7, 2.6))]
        mr.fin(rig, f"Pec{s}", root, [Vector((s * 1.8, -1.25, 1.95)), Vector((s * 3.1, 0.3, 1.2)),
                                      Vector((s * 2.3, 0.35, 1.55)), Vector((s * 1.2, -0.2, 2.1))],
               f"PecFin_{side}", part=F, rays=10, seed=4 + s)
        root = [SPINE[I(13)] + Vector((s * 0.35, 0, -0.45)), SPINE[I(15)] + Vector((s * 0.3, 0, -0.45))]
        mr.fin(rig, f"Pelvic{s}", root, [root[0] + Vector((s * 0.8, 0.6, -0.65)),
                                         root[1] + Vector((s * 0.4, 0.4, -0.3))], "Body3",
               part=F, rays=4, seed=8 + s)
    base = SPINE[-1]
    mr.fin(rig, "Caudal", [base + Vector((0, -0.45, 0.35)), base, base + Vector((0, -0.45, -0.35))],
           [Vector((0, 8.9, 5.0)), Vector((0, 9.95, 6.35)), Vector((0, 9.15, 4.1)),
            Vector((0, 9.65, 1.75)), Vector((0, 8.7, 2.3))], "Caudal", part=F, rays=14, seed=11)


def build_harpoons(rig):
    """Harpons rouillés plantés dans le dos, avec chaînes qui pendent."""
    for k, (i, s, d) in enumerate(((I(9), 1, (0.55, 0.35, 1)), (I(16), -1, (-0.5, 0.6, 1)))):
        bone = body_bone(i)
        base = SPINE[i] + Vector((s * 0.25, 0, 0.35))
        d = Vector(d).normalized()
        end = base + d * 2.0
        rig.add(r.tube(f"HarpoonShaft{k}", [tuple(base - d * 0.3), tuple(end)], 0.05, segments=6),
                bone, "rust")
        for j, t in enumerate((0.45, 0.7)):   # bagues de fer sur le manche
            rig.add(a.ring_around(f"HarpoonBand{k}{j}", base.lerp(end, t), d, 0.07, 0.02,
                                  segments=8), bone, "rust")
        side, up = a._basis(d)
        for b in (-1, 1):
            rig.add(a.claw(f"HarpoonBarb{k}{b}", base + d * 0.05, d + side * b * 0.8, 0.25, 0.04,
                           curl=0, segments=4), bone, "rust")
        rig.add(a.ring_around(f"HarpoonEye{k}", end, d, 0.1, 0.03, segments=10), bone, "rust")
        p = end + Vector((0, 0, -0.12))
        for j in range(6):
            axis = Vector((1, 0, 0)) if j % 2 == 0 else Vector((0, 1, 0))
            rig.add(a.ring_around(f"Chain{k}{j}", p, axis, 0.1, 0.025, segments=8), bone, "rust")
            p = p + Vector((0.05 * s, 0.04, -0.16))
        rig.add(r.ico(f"BloodGlow{k}", 0.1, subdivisions=1, location=base + d * 0.12), bone,
                "glow", glow=True)
        mr.scar(rig, f"Wound{k}", base + side * 0.1, base + Vector((0, 0.5, -0.25)), bone, seed=k)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_skull(rig)
    build_jaws(rig)
    build_body(rig)
    build_fins(rig)
    build_harpoons(rig)
    return rig
