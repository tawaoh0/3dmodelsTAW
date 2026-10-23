"""Liche dragon squelette (wyverne voûtée, ≈ 7 studs de haut) — animable.
Pack « Cimetière gothique / nécromancie », créature 1.

Animal modèle : le **markhor** (chèvre sauvage à cornes en tire-bouchon) pour le crâne et les
cornes, sur un corps de wyverne ; différent du dragon quadrupède (pack 1) et du dragon de givre
(ailes de cristal dressées) : ici les **ailes déchirées retombent en cape**.

Identité : os gris cendre violacé ; **cornes en spirale** noires + **couronne de fer à bougies** ;
ailes en lambeaux tombantes ; **cercueil-phylactère** enchaîné au poitrail ; **lanterne d'âme**
pendue au bout de la queue ; bougies coulantes sur le dos ; thème d'effets « necro »
(âmes violettes + étincelles de chandelle).

5 pièces Roblox : corps, Head, Wings, Tail, + lumineux.
Os : Root, Hips, Chest, Neck1-2, Head, Jaw, Tail1-4, Thigh/Shin/Foot_{L,R},
Wing1/Wing2_{L,R}, WingFinger1-4_{L,R}, + FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#b3a9b8",
    "bone_shade": "#5e5068",
    "tooth": "#f1ece0",
    "horn": "#1c1622",
    "horn_tip": "#c58cff",
    "disc": "#2e2436",
    "crystal": "#241c2c",
    "crystal_deep": "#4a3366",
    "membrane": "#3b3045",
    "iron": "#3d3a40",
    "wax": "#e8dfc4",
    "wood": "#4a3328",
    "gum": "#3a2650",
    "ink": "#0a0810",
    "glow": "#b45cff",
    "glow_hot": "#f3e2ff",
}

EFFECT_THEME = "necro"

TEST_POSE = {
    "Jaw": (-20, 0, 0),
    "Wing1_L": (0, 35, 20),
    "Wing2_R": (0, -25, 0),
    "Neck2": (-15, 0, 0),
    "Tail3": (0, 0, 30),
}

VIEW = (0.45, -1.0, 0.4)

SPINE = a.smooth_path([(0, 1.0, 3.35), (0, 0.1, 3.7), (0, -0.8, 4.2)], 14)
NECK = a.smooth_path([(0, -0.8, 4.25), (0, -1.35, 4.95), (0, -1.6, 5.7), (0, -2.0, 6.22)], 11)
TAIL = a.smooth_path([(0, 1.0, 3.35), (0, 2.2, 3.0), (0, 3.4, 2.2), (0, 4.6, 1.4),
                      (0.4, 5.8, 0.95), (0.9, 6.6, 0.95)], 28)
# Crâne de varan : (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-2.0, 0.3, 0.42, 0.32, 6.55, 5.95), (-2.35, 0.36, 0.48, 0.38, 6.7, 5.92),
         (-2.75, 0.33, 0.44, 0.36, 6.66, 5.94), (-3.2, 0.24, 0.32, 0.28, 6.5, 5.97),
         (-3.7, 0.2, 0.26, 0.22, 6.3, 5.99), (-4.0, 0.17, 0.21, 0.18, 6.18, 6.02)]
EYE = (-2.75, 6.32)
HINGE = (0.38, -2.3, 5.95)
GAPE = math.radians(32)
_m = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
      @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
CHIN = tuple(_m @ Vector((0, -3.95, 5.98)))
WING_ROOT = Vector((0.62, -0.75, 4.75))
ELBOW = Vector((1.65, -0.3, 5.6))
WRIST = Vector((2.6, -0.4, 6.7))
# Ailes repliées qui retombent en cape déchirée
TIPS = [Vector((3.9, 0.2, 7.3)), Vector((4.2, 1.2, 4.9)), Vector((3.6, 2.0, 2.9)),
        Vector((2.6, 2.4, 1.7))]
BODY_ROOT = Vector((0.6, -0.8, 4.45))
BODY_MID = Vector((0.6, 0.15, 3.8))
BODY_HIP = Vector((0.4, 1.0, 3.35))
HEAD = dict(part="Head")
WINGS = dict(part="Wings")
TAILP = dict(part="Tail")


def mirror(v, s):
    return Vector((v.x * s, v.y, v.z))


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def tail_bone(i):
    return f"Tail{min(4, i * 4 // len(TAIL) + 1)}"


def leg_points(s):
    return (Vector((s * 0.62, 0.85, 3.15)), Vector((s * 0.8, -0.15, 2.0)),
            Vector((s * 0.82, 0.75, 0.8)), Vector((s * 0.82, 0.2, 0.15)))


def crystal_spike(rig, name, base, direction, length, radius, bone, color="crystal", **kw):
    """Pointe d'os noire légèrement recourbée (base posée sur l'os)."""
    rig.add(a.claw(name, base, direction, length, radius, curl=0.15, segments=5), bone, color, **kw)


def chain(rig, name, start, end, bone, sag=0.15, radius=0.07, **kw):
    """Chaîne de maillons alternés entre deux points, avec un peu de mou."""
    start, end = Vector(start), Vector(end)
    d = (end - start).normalized()
    side = d.cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-3 else Vector((1, 0, 0))
    n = max(3, math.ceil((end - start).length / (radius * 1.7)))
    for j in range(n):
        f = (j + 0.5) / n
        p = start.lerp(end, f) - Vector((0, 0, sag * math.sin(math.pi * f)))
        ax = side if j % 2 else d.cross(side)
        rig.add(a.ring_around(f"{name}{j}", p, ax, radius, radius * 0.3, segments=8), bone, "iron",
                **kw)


def candle(rig, name, base, height, bone, radius=0.045, **kw):
    """Bougie coulante (cire + coulures) et sa flamme lumineuse."""
    base = Vector(base)
    top = base + Vector((0, 0, height))
    rig.add(r.tube(name, [tuple(base), tuple(top)], [radius * 1.25, radius], segments=6), bone, "wax",
            **kw)
    rig.add(r.ico(f"{name}Drip", radius * 0.55, subdivisions=1,
                  location=base.lerp(top, 0.55) + Vector((radius * 0.9, 0, 0)), scale=(0.7, 0.7, 2)),
            bone, "wax", **kw)
    rig.add(r.ico(f"{name}Flame", radius * 0.8, subdivisions=1, location=top + Vector((0, 0, radius)),
                  scale=(0.8, 0.8, 1.8)), bone, "glow", glow=True)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[7], "Root")
    rig.bone("Chest", SPINE[7], SPINE[-1], "Hips")
    rig.bone("Neck1", NECK[0], NECK[5], "Chest")
    rig.bone("Neck2", NECK[5], NECK[-1], "Neck1")
    rig.bone("Head", NECK[-1], (0, -4.0, 6.2), "Neck2")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    n = len(TAIL) - 1
    parent = "Hips"
    for k in range(4):
        parent = rig.bone(f"Tail{k + 1}", TAIL[k * n // 4], TAIL[(k + 1) * n // 4], parent)
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Hips")
        rig.bone(f"Shin_{side}", kn, an, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", an, ft, f"Shin_{side}")
        root, elbow, wrist = mirror(WING_ROOT, s), mirror(ELBOW, s), mirror(WRIST, s)
        rig.bone(f"Wing1_{side}", root, elbow, "Chest")
        rig.bone(f"Wing2_{side}", elbow, wrist, f"Wing1_{side}")
        for i, tip in enumerate(TIPS):
            rig.bone(f"WingFinger{i + 1}_{side}", wrist, mirror(tip, s), f"Wing2_{side}")
        rig.fx(f"Eye{side}", (s * 0.38, EYE[0], EYE[1]), "Head")
        rig.fx(f"WingTip{side}", mirror(TIPS[0], s), f"WingFinger1_{side}")
    rig.fx("Heart", (0, -0.3, 3.3), "Chest")
    rig.fx("Breath", (0, -3.7, 5.7), "Head")
    rig.fx("Lantern", TAIL[-1] + Vector((0, 0.05, -0.75)), "Tail4")
    rig.fx("Crown", (0, -2.5, 7.0), "Head")
    rig.fx("Coffin", (0, -1.5, 2.7), "Chest")


# ---------------------------------------------------------------- tête de varan

def build_head(rig):
    H = "Head"
    skull = a.loft_profile("Skull", SKULL, droop=0.12)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.17, 0.15),
                  a.hole_x((0, -2.25, 6.2), 0.2, 0.14),
                  a.hole_x((0, -3.75, 6.12), 0.1, 0.045)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 12))
        return p

    # Cornes de markhor en tire-bouchon, vers l'arrière et vers le haut
    for s in (-1, 1):
        base = top(s * 0.22, -2.15) or Vector((s * 0.22, -2.15, 6.6))
        pts = []
        for k in range(22):
            f = k / 21
            ang = 5 * math.pi * f
            axis = base + Vector((s * 0.7 * f, 1.6 * f, 1.5 * f))
            pts.append(axis + Vector((s * 0.3 * math.sin(math.pi * min(1, f * 1.4)) * math.cos(ang), -0.12 * math.sin(ang), 0.3 * math.sin(math.pi * min(1, f * 1.4)) * math.sin(ang))))
        rig.add(a.ridged_horn(f"Horn{s}", pts, 0.13, ridges=10), H, "horn", **HEAD)
        rig.add(r.ico(f"HornTip{s}", 0.03, subdivisions=1, location=pts[-1]), H, "horn_tip", **HEAD)
    # Couronne de fer : pointes alternées avec des bougies
    band = [top(0.3 * math.cos(math.pi * k / 6), -2.45 - 0.12 * math.sin(math.pi * k / 6))
            + Vector((0, 0, 0.03)) for k in range(7)]
    rig.add(r.tube("CrownBand", [tuple(p) for p in band], 0.05, segments=4), H, "iron", **HEAD)
    for k, p in enumerate(band):
        if k % 2:
            candle(rig, f"CrownCandle{k}", p, 0.22 + 0.06 * (k == 3), H, **HEAD)
        else:
            rig.add(a.claw(f"CrownSpike{k}", p, (0, 0.2, 1), 0.28, 0.05, curl=0, segments=4), H,
                    "iron", **HEAD)
    rig.add(r.tube("Midline", [tuple(top(0, y) + Vector((0, 0, 0.015))) for y in
                               (-2.3, -2.8, -3.3, -3.8)], [0.04, 0.045, 0.035, 0.025], segments=4),
            H, "bone_shade", **HEAD)
    for s in (-1, 1):
        # Orbite cerclée de piques de glace, œil cyan, arcade
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=c0 - Vector((s * 0.07, 0, 0))), H,
                "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", c0, (s, -0.2, 0.15), 0.17, H, spikes=5, color="crystal",
                       **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.15, -3.0, 6.48), (s * 0.4, -2.55, 6.58), 0.16, 0.07,
                        width_end=0.1, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        for k in range(3):
            crystal_spike(rig, f"BrowShard{s}{k}", (s * (0.22 + 0.08 * k), -2.85 + 0.15 * k, 6.55),
                          (s * 0.4, 0.5, 1), 0.25, 0.04, H, **HEAD)
        # Arcade zygomatique, écailles osseuses (ostéodermes), narine en fente
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.4, -2.1, 6.02), (s * 0.55, -2.45, 6.05),
                                         (s * 0.4, -2.85, 6.08)], [0.045, 0.06, 0.045],
                       segments=5), H, "bone", **HEAD)
        mr.scutes(rig, f"Osteoderm{s}", [top(s * 0.18, y) + Vector((0, 0, 0.01))
                                         for y in (-2.5, -3.0, -3.45)],
                  [Vector((s * 0.3, 0, 1))] * 3, H, size=0.07, color="crystal_deep", **HEAD)
        rig.add(a.ring_around(f"NostrilRim{s}", (s * a.side_width(SKULL, -3.75, 6.12), -3.75, 6.12),
                              (s, 0, 0), 0.1, 0.025, segments=8), H, "bone_shade", **HEAD)
        mr.scar(rig, f"SoulVein{s}", top(s * 0.12, -2.15), top(s * 0.15, -2.7), H, width=0.03,
                seed=s)
        # Rangée du haut : dents recourbées et dentelées de varan, crocs devant
        for k in range(9):
            y = -3.95 + 0.2 * k
            xx = s * a.side_width(SKULL, y, 6.0) * 0.85
            size = 0.24 if k == 1 else 0.13 + 0.03 * (k % 2)
            rig.add(mr.tooth(f"UpTooth{s}{k}", (xx, y, 6.0), (xx, y + 0.05, 6.0 - size), size * 0.5,
                             size * 0.28, Vector((s, -0.2, 0)), curl=0.2), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * a.side_width(SKULL, y, 6.0) * 0.72, y, 6.02)
                                        for y in (-3.9, -3.2, -2.4)], 0.035, segments=4), H, "gum",
                **HEAD)
    build_jaw(rig)
    rig.add(r.ico("Throat", 0.16, subdivisions=2, location=(0, -2.6, 5.9), scale=(1.3, 2, 0.6)), H,
            "glow", glow=True)


def build_jaw(rig):
    J = "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.3, -2.9, 5.95)),
                Vector((s * 0.18, -3.5, 5.97)), Vector((s * 0.07, -3.95, 5.98))]
        hs = [0.26, 0.2, 0.16, 0.13]
        rig.add(a.band(f"Dentary{s}", line, hs, [0.09, 0.08, 0.07, 0.06], offset=1), J, "bone",
                **HEAD)
        rig.add(r.tube(f"DentaryBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.03, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.12, 0)),
                        line[0] + Vector((0, -0.05, 0.25)), 0.15, 0.05, width_end=0.07,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.08, subdivisions=1, location=line[0]), "Head", "bone_shade",
                **HEAD)
        for k in range(8):
            p = mr.along(line, 0.2 + 0.1 * k)
            size = 0.2 if k == 7 else 0.12 + 0.03 * (k % 2)
            rig.add(mr.tooth(f"LowTooth{s}{k}", p, p + Vector((0, 0.04, size)), size * 0.5,
                             size * 0.28, Vector((s, -0.2, 0)), curl=0.2), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.025, 0, 0.015))) for p in line[1:]],
                       0.03, segments=4), J, "gum", **HEAD)
    for k in range(3):
        rig.add(a.claw(f"ChinShard{k}", (0.07 * (k - 1), -3.85, 5.83), (0, 0.2, -1), 0.2, 0.03,
                       curl=0, segments=4), J, "crystal", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(_m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps, cou, queue, pattes

def build_body(rig):
    for path, bones, size in ((SPINE, ("Hips", "Chest"), 0.3), (NECK, ("Neck1", "Neck2"), 0.23)):
        n = len(path)
        for i in range(n):
            t = tangent(path, i)
            bone = bones[0] if i < n // 2 else bones[1]
            rig.add(a.vertebra(f"Vert{bones[0]}{i}", path[i], t, size, spine=1.5, lean=0.45),
                    bone, "bone")
            if i < n - 1:
                rig.add(a.disc(f"Disc{bones[0]}{i}", path[i].lerp(path[i + 1], 0.5), t, size),
                        bone, "disc")
            if i % 2 == 0:
                side, up = a._basis(t)
                crystal_spike(rig, f"DorsalShard{bones[0]}{i}", path[i] + up * size * 1.6, up - t * 0.5,
                              0.4, 0.06, bone, "crystal" if i % 4 else "crystal_deep")
    # Buste massif : grande cage en tonneau (plus large et profonde vers l'avant), sternum
    # large, énorme bréchet de vol, coracoïdes épais, plastron de plaques de cristal
    sternum = []
    for k, i in enumerate(range(2, 14)):
        f = k / 11
        hw = 0.6 + 0.45 * math.sin(math.pi * (0.25 + 0.6 * f))
        depth = 0.9 + 0.75 * f ** 0.8
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.25, radius=0.08),
                    "Chest" if i >= 7 else "Hips", "bone")
        sternum.append(SPINE[i] + Vector((0, -0.25, -depth)))
    rig.add(a.band("Sternum", sternum[1::2], 0.12, 0.55), "Chest", "bone_shade")
    keel = [sternum[5], sternum[8], sternum[11] + Vector((0, -0.15, 0))]
    rig.add(a.band("Keel", keel, [0.35, 0.6, 0.45], 0.08, up=(0, 0, -1), offset=0), "Chest", "bone")
    rig.add(r.tube("KeelRim", [tuple(p + Vector((0, 0, -h))) for p, h in zip(keel, (0.35, 0.6, 0.45))],
                   0.045, segments=4), "Chest", "bone_shade")
    for s in (-1, 1):
        root = mirror(WING_ROOT, s)
        rig.add(a.long_bone(f"Coracoid{s}", root, sternum[-1] + Vector((s * 0.25, 0, 0.05)), 0.1,
                            condyles=False, segments=6), "Chest", "bone")
        rig.add(a.blade(f"Scapula{s}", SPINE[11] + Vector((s * 0.25, 0.2, 0.15)), root, 0.45, 0.07,
                        width_end=0.22, mid=0.5, normal=(s, 0, 0.5)), "Chest", "bone")
        rig.add(a.long_bone(f"Furcula{s}", root + Vector((0, -0.05, -0.05)),
                            sternum[-1] + Vector((0, -0.3, 0.35)), 0.05, condyles=False,
                            segments=5), "Chest", "bone_shade")
    # Cercueil-phylactère enchaîné devant le poitrail (couvercle de fer, âme qui luit)
    cc = sternum[-1] + Vector((0, -0.45, -0.35))
    outline = [(-0.13, 0.42), (0.13, 0.42), (0.22, 0.2), (0.14, -0.4), (-0.14, -0.4), (-0.22, 0.2)]
    rig.add(r.loft("Coffin", [[(cc.x + x, cc.y + dy, cc.z + z) for x, z in outline]
                              for dy in (0.08, -0.08)]), "Chest", "wood")
    rig.add(r.loft("CoffinLid", [[(cc.x + x * 0.8, cc.y + dy, cc.z + z * 0.85) for x, z in outline]
                                 for dy in (-0.07, -0.11)]), "Chest", "iron")
    rig.add(r.box("CoffinCrossV", (0.05, 0.03, 0.34), location=cc + Vector((0, -0.12, 0.02))), "Chest",
            "glow", glow=True)
    rig.add(r.box("CoffinCrossH", (0.2, 0.03, 0.05), location=cc + Vector((0, -0.12, 0.1))), "Chest",
            "glow", glow=True)
    for s in (-1, 1):
        chain(rig, f"CoffinChain{s}", mirror(WING_ROOT, s) + Vector((0, -0.1, -0.1)),
              cc + Vector((s * 0.12, 0, 0.4)), "Chest", sag=0.1)
    for k, (dx, h) in enumerate(((0, 0.65), (0.15, 0.45), (-0.15, 0.5))):
        rig.add(a.crystal(f"SoulHeart{k}", (dx, -0.3, 2.95), 0.14 if k == 0 else 0.1, h * 1.3, sides=6),
                "Chest", "glow", glow=True)
    # Bassin, queue à massue de cristaux
    for s in (-1, 1):
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.15, 0, 0.05)),
                        hp + Vector((s * 0.1, -0.1, 0.25)), 0.4, 0.07, width_end=0.3, mid=0.45,
                        normal=(s, 0, 0.4)), "Hips", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.25, 0.4, 2.8), (0, 0.45, 2.75)], 0.06,
                       segments=5), "Hips", "bone")
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        side, up = a._basis(t)
        size = 0.2 - 0.12 * i / (nt - 1)
        bone = tail_bone(i)
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=1.3, lean=0.4,
                           transverse=i < 12), bone, "bone", **TAILP)
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc",
                    **TAILP)
        if i % 3 == 0:
            crystal_spike(rig, f"TailShard{i}", TAIL[i] + up * size * 1.4, up - t * 0.4,
                          0.42 - 0.01 * i, 0.06, bone, **TAILP)
    end, t = TAIL[-1], tangent(TAIL, nt - 1)
    side, up = a._basis(t)
    # Lanterne d'âme pendue à la queue
    lc = end + Vector((0, 0.05, -0.75))
    chain(rig, "LanternChain", end, lc + Vector((0, 0, 0.3)), "Tail4", sag=0.0, radius=0.06, **TAILP)
    for z, rad in ((0.25, 0.13), (-0.25, 0.15)):
        rig.add(a.ring_around(f"LanternRing{z}", lc + Vector((0, 0, z)), (0, 0, 1), rad, 0.035,
                              segments=8), "Tail4", "iron", **TAILP)
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2
        o = Vector((math.cos(ang), math.sin(ang), 0)) * 0.14
        rig.add(r.tube(f"LanternBar{k}", [tuple(lc + o + Vector((0, 0, 0.25))),
                                          tuple(lc + o * 1.15),
                                          tuple(lc + o + Vector((0, 0, -0.25)))], 0.025, segments=4),
                "Tail4", "iron", **TAILP)
    rig.add(a.claw("LanternSpike", lc + Vector((0, 0, -0.27)), (0, 0, -1), 0.2, 0.05, curl=0,
                   segments=4), "Tail4", "iron", **TAILP)
    rig.add(r.ico("LanternSoul", 0.11, subdivisions=2, location=lc, scale=(1, 1, 1.4)), "Tail4", "glow",
            glow=True)
    # Bougies coulantes plantées sur le dos
    for k, i in enumerate((3, 6, 9)):
        t0 = tangent(SPINE, i)
        side, up = a._basis(t0)
        for s in (-1, 1):
            candle(rig, f"BackCandle{k}{s}", SPINE[i] + up * 0.3 + side * s * 0.22, 0.2 + 0.05 * (k % 2),
                   "Chest" if i >= 7 else "Hips", radius=0.04)
    # Pattes arrière : fémur, tibia, métatarses, 3 doigts avant + ergot, griffes de glace
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.18, segments=7), th, "bone")
        rig.add(a.long_bone(f"Tibia{s}", kn, an, 0.14, segments=7), sn, "bone")
        rig.add(a.long_bone(f"Tarsus{s}", an, ft, 0.08, segments=6), fo, "bone")
        rig.add(a.ring_around(f"KneeGlow{s}", kn, an - kn, 0.16, 0.035, segments=8), sn, "glow",
                glow=True)
        crystal_spike(rig, f"KneeShard{s}", kn + Vector((0, -0.1, 0.05)), (s * 0.2, -1, 0.5), 0.35,
                      0.05, th)
        for k, ang in enumerate((-0.4, 0.0, 0.4, math.pi)):
            d = Vector((math.sin(ang) * s, -math.cos(ang), 0))
            toe = ft + d * 0.38 + Vector((0, 0, -0.06))
            rig.add(a.long_bone(f"Toe{s}{k}", ft, toe, 0.045, condyles=False, segments=5), fo,
                    "bone")
            rig.add(a.claw(f"Talon{s}{k}", toe, d + Vector((0, 0, -0.6)), 0.28, 0.05, curl=0.45,
                           segments=5), fo, "crystal")


def build_wing(rig, s, side):
    root, elbow, wrist = mirror(WING_ROOT, s), mirror(ELBOW, s), mirror(WRIST, s)
    tips = [mirror(t, s) for t in TIPS]
    w1, w2 = f"Wing1_{side}", f"Wing2_{side}"
    fingers = [f"WingFinger{i + 1}_{side}" for i in range(4)]
    rig.add(a.long_bone(f"WingHumerus{s}", root, elbow, 0.12), w1, "bone", **WINGS)
    rig.add(a.long_bone(f"WingRadius{s}", elbow, wrist, 0.09), w2, "bone", **WINGS)
    rig.add(a.long_bone(f"WingUlna{s}", elbow + Vector((0, 0.12, -0.1)),
                        wrist + Vector((0, 0.1, -0.08)), 0.05, condyles=False), w2, "bone_shade",
            **WINGS)
    rig.add(r.ico(f"WingWrist{s}", 0.17, subdivisions=1, location=wrist), w2, "bone_shade", **WINGS)
    crystal_spike(rig, f"WristShard{s}", wrist, (s * 0.2, -1, 0.6), 0.6, 0.08, w2, **WINGS)
    crystal_spike(rig, f"ElbowShard{s}", elbow, (s * 0.3, -0.6, 1), 0.45, 0.06, w1, **WINGS)
    for i, (tip, bone) in enumerate(zip(tips, fingers)):
        knuckle = wrist.lerp(tip, 0.45)
        rig.add(a.long_bone(f"WingFingerA{s}{i}", wrist, knuckle, 0.065, knob=1.5,
                            condyles=False), bone, "bone", **WINGS)
        rig.add(a.long_bone(f"WingFingerB{s}{i}", knuckle, tip, 0.045, knob=1.4,
                            condyles=False), bone, "bone", **WINGS)
        crystal_spike(rig, f"FingerTip{s}{i}", tip, tip - wrist, 0.4, 0.05, bone, **WINGS)
        # Veines lumineuses le long des doigts
        rig.add(r.tube(f"WingVein{s}{i}", [tuple(wrist.lerp(tip, 0.1) + Vector((0, 0, 0.05))),
                                           tuple(wrist.lerp(tip, 0.85) + Vector((0, 0, 0.04)))],
                       0.02, segments=4), bone, "glow", glow=True)
        # Lambeaux pendants au bout des doigts
        rig.add(a.blade(f"Tatter{s}{i}", tip.lerp(wrist, 0.15), tip.lerp(wrist, 0.15) + Vector((0, 0.1, -0.5)),
                        0.12, 0.02, width_end=0.03, normal=(1, 0, 0), bevel=0), bone, "membrane",
                **WINGS)
    rig.add(a.claw(f"Thumb{s}", wrist + Vector((0, -0.1, 0.1)), (s * 0.3, -1, 0.4), 0.45, 0.08,
                   curl=0.3), w2, "crystal", **WINGS)
    # Membranes de cristal : panneaux entre les doigts, bords déchirés
    W = {w2: 1.0}
    panels = []
    for i in range(3):
        edge = a.tattered_edge(tips[i], tips[i + 1], {fingers[i]: 1}, {fingers[i + 1]: 1},
                               wrist, depth=0.9 - 0.1 * i, notches=5, seed=10 * s + i)
        panels.append([(wrist, W), (tips[i], {fingers[i]: 1})] + edge
                      + [(tips[i + 1], {fingers[i + 1]: 1})])
    hip, mid, body_root = mirror(BODY_HIP, s), mirror(BODY_MID, s), mirror(BODY_ROOT, s)
    edge = a.tattered_edge(tips[3], hip, {fingers[3]: 1}, {"Hips": 1}, wrist.lerp(mid, 0.5),
                           depth=0.7, notches=5, seed=7 * s)
    panels.append([(wrist, W), (tips[3], {fingers[3]: 1})] + edge
                  + [(hip, {"Hips": 1}), (mid, {"Chest": 0.5, "Hips": 0.5}),
                     (body_root, {"Chest": 1}), (elbow, {w1: 0.5, w2: 0.5})])
    lead = root.lerp(wrist, 0.5) + Vector((0, -0.3, 0.25))
    panels.append([(wrist, W), (elbow, {w1: 0.5, w2: 0.5}), (root, {w1: 1}),
                   (lead, {w1: 0.5, w2: 0.5})])
    for k, outline in enumerate(panels):
        m = a.membrane(f"Membrane{s}{k}", [(tuple(p), w) for p, w in outline])
        rig.pal.paint(m, "membrane")
        m["part"] = "Wings"


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    for s, side in ((1, "L"), (-1, "R")):
        build_wing(rig, s, side)
    return rig
