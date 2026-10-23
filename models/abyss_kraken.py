"""Kraken squelette des abysses (≈ 8 studs de large, 9 de haut) — créature animable.
Pack « Abysses », créature 1.

Animal modèle : le calmar géant — énormes yeux sur les côtés de la tête, bec de perroquet,
entonnoir (siphon) sous la tête, plume interne (gladius) le long du dos, ventouses et
crochets sur les bras, longs tentacules à massue.

Identité dans le projet :
- os blanchis par la mer, teinte vert d'eau, couverts de balanes et de coraux rouges ;
- pas de cornes : crochets noirs sur les tentacules ;
- manteau dressé en cage d'os verticale à nageoires, 8 bras étalés au sol qui s'enroulent,
  2 longs tentacules dressés à massue ;
- thème « abysses » : points bioluminescents cyan, organe lumineux, bulles.

3 pièces Roblox : corps (tête + manteau), Arms (8 bras), Tentacles (2 tentacules), + lumineux.
Os du rig : Root, Head, Mantle, Jaw (bec), Arm{0-7}_1-4, Tentacle_{L,R}_1-5, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#c9d8cf",
    "bone_shade": "#86a198",
    "tooth": "#eef5ef",
    "horn": "#141a1f",
    "horn_tip": "#1f6b78",
    "disc": "#2a4a52",
    "membrane": "#2c5560",
    "coral": "#e0573a",
    "barnacle": "#8f8b78",
    "ink": "#160f26",
    "glow": "#25f0ff",
    "glow_hot": "#d6fdff",
}

EFFECT_THEME = "abyss"

TEST_POSE = {
    "Jaw": (30, 0, 0),
    "Mantle": (-12, 0, 0),
    "Arm0_3": (0, 0, 25),
    "Arm3_2": (-25, 0, 0),
    "Tentacle_L_3": (25, 0, 0),
    "Tentacle_R_2": (0, 0, -20),
}

VIEW = (0.75, -1.0, 0.45)

HEAD_C = Vector((0, 0, 2.2))
# Manteau : axe de la base (au-dessus de la tête) à la pointe, incliné vers l'arrière
MANTLE_A, MANTLE_B = Vector((0, 0.35, 2.95)), Vector((0, 1.2, 7.6))
HOOPS = [(0.0, 0.95), (0.15, 1.25), (0.35, 1.32), (0.55, 1.12), (0.75, 0.78), (0.9, 0.45)]
EYE = (-0.1, 2.35)          # (y, z) des yeux, sur les flancs de la tête

# Tête (capsule cartilagineuse) : (y, demi-larg. dessus, joues, bas, z dessus, z bas)
HEAD = [(0.85, 0.5, 0.75, 0.6, 2.9, 1.6), (0.4, 0.75, 1.0, 0.8, 3.05, 1.45),
        (-0.2, 0.8, 1.05, 0.82, 3.0, 1.45), (-0.65, 0.6, 0.8, 0.65, 2.85, 1.55),
        (-0.9, 0.42, 0.56, 0.46, 2.62, 1.68)]


def mantle_frame(t):
    """Centre, axe et 2 vecteurs perpendiculaires du manteau à la fraction t."""
    axis = (MANTLE_B - MANTLE_A).normalized()
    side = Vector((1, 0, 0))
    other = axis.cross(side).normalized()     # vers l'avant-haut du manteau
    return MANTLE_A.lerp(MANTLE_B, t), axis, side, other


def hoop_radius(t):
    for (t0, r0), (t1, r1) in zip(HOOPS, HOOPS[1:]):
        if t0 <= t <= t1:
            return r0 + (r1 - r0) * (t - t0) / (t1 - t0)
    return HOOPS[-1][1]


def barnacle(rig, name, location, normal, bone, size=0.1, **kw):
    """Balane : petit cône tronqué percé d'un trou sombre."""
    shell = a.oriented(r.cylinder(name, size, size * 0.9, segments=6, radius_top=size * 0.45,
                                  location=(0, 0, size * 0.35)), location, normal)
    rig.add(shell, bone, "barnacle", **kw)
    hole = a.oriented(r.cylinder(f"{name}h", size * 0.32, 0.03, segments=6,
                                 location=(0, 0, size * 0.8)), location, normal)
    rig.add(hole, bone, "ink", **kw)


def coral(rig, name, base, up, size, bone, seed=0, **kw):
    """Petit corail rouge branchu qui pousse sur un os."""
    import random
    rnd = random.Random(seed)
    base, up = Vector(base), Vector(up).normalized()
    side = up.cross(Vector((0, 0, 1)) if abs(up.z) < 0.9 else Vector((1, 0, 0))).normalized()
    trunk_top = base + up * size
    rig.add(r.tube(f"{name}t", [tuple(base), tuple(trunk_top)], [size * 0.12, size * 0.08],
                   segments=5), bone, "coral", **kw)
    for i in range(3):
        ang = 2 * math.pi * i / 3 + rnd.uniform(-0.4, 0.4)
        out = (side * math.cos(ang) + up.cross(side) * math.sin(ang)) * 0.6 + up
        start = base + up * size * rnd.uniform(0.4, 0.8)
        end = start + out.normalized() * size * rnd.uniform(0.5, 0.8)
        rig.add(r.tube(f"{name}b{i}", [tuple(start), tuple(end)], [size * 0.07, size * 0.04],
                       segments=4), bone, "coral", **kw)
        rig.add(r.ico(f"{name}k{i}", size * 0.07, subdivisions=1, location=end), bone, "coral",
                **kw)


def photophore(rig, name, location, bone, size=0.05):
    rig.add(r.ico(name, size, subdivisions=1, location=location), bone, "glow", glow=True)


# ---------------------------------------------------------------- bras et tentacules

def arm_path(k):
    ang = math.radians(22.5 + 45 * k)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    side = Vector((-d.y, d.x, 0)) * (1 if k % 2 == 0 else -1)
    base = HEAD_C + d * 0.75 + Vector((0, 0, -0.65))
    up = Vector((0, 0, 1))
    ctrl = [base, base + d * 0.9 - up * 0.55, base + d * 1.9 - up * 1.15 + side * 0.15,
            base + d * 2.9 - up * 1.25 + side * 0.4, base + d * 3.4 - up * 0.8 + side * 0.65,
            base + d * 3.25 - up * 0.35 + side * 1.0]
    return a.smooth_path(ctrl, 13)


def tentacle_path(s):
    ang = math.radians(-90 + 58 * s)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    base = HEAD_C + d * 0.75 + Vector((0, 0, -0.5))
    ctrl = [base, base + d * 1.0 + Vector((0, 0, 0.1)), base + d * 1.8 + Vector((0, 0, 1.4)),
            base + d * 1.9 + Vector((0, -0.4, 3.0)), base + d * 1.5 + Vector((0, -1.1, 4.2)),
            base + d * 1.1 + Vector((0, -1.8, 4.5))]
    return a.smooth_path(ctrl, 17)


def bone_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Head", (0, 0, 1.6), (0, 0, 2.9), "Root")
    rig.bone("Mantle", MANTLE_A, MANTLE_B, "Head")
    rig.bone("Jaw", (0, -0.55, 1.75), (0, -0.85, 1.25), "Head")
    for k in range(8):
        path = arm_path(k)
        parent = "Head"
        for i in range(4):
            parent = rig.bone(f"Arm{k}_{i + 1}", path[i * 3], path[i * 3 + 3], parent)
    for s, side in ((1, "L"), (-1, "R")):
        path = tentacle_path(s)
        parent = "Head"
        for i in range(5):
            parent = rig.bone(f"Tentacle_{side}_{i + 1}", path[i * 3], path[min(16, i * 3 + 4)],
                              parent)
        rig.fx(f"Club{side}", path[-1], f"Tentacle_{side}_5")
        rig.fx(f"Eye{side}", (s * 1.0, EYE[0], EYE[1]), "Head")
    rig.fx("Heart", MANTLE_A.lerp(MANTLE_B, 0.4), "Mantle")
    rig.fx("Siphon", (0, -1.05, 1.75), "Head")


def build_limb(rig, name, path, radii, bones, part, hooks_from, club=False):
    """Bras / tentacule : segments d'os, ventouses dessous, photophores dessus, crochets."""
    kw = dict(part=part)
    n = len(path)
    for i in range(n - 1):
        bone = bones[min(len(bones) - 1, i * len(bones) // (n - 1))]
        rig.add(a.long_bone(f"{name}Seg{i}", path[i], path[i + 1], radii[i], knob=1.35,
                            condyles=False, segments=7), bone, "bone", **kw)
        tan = (path[i + 1] - path[i]).normalized()
        side, up = a._basis(tan)
        mid = path[i].lerp(path[i + 1], 0.5)
        rad = radii[i]
        if i % 2 == 0:   # ventouse : anneau sous le bras
            rig.add(a.ring_around(f"{name}Sucker{i}", mid - up * rad * 0.95, up, rad * 0.5,
                                  rad * 0.16, segments=8), bone, "bone_shade", **kw)
        if i % 3 == 1:   # photophore sur le dessus
            photophore(rig, f"{name}Photo{i}", mid + up * rad * 1.05, bone, size=rad * 0.32)
        if i >= hooks_from:   # crochets noirs recourbés vers l'arrière
            for sd in (-1, 1):
                rig.add(a.claw(f"{name}Hook{i}{sd}", mid - up * rad * 0.7 + side * sd * rad * 0.6,
                               -tan - up * 0.6 + side * sd * 0.3, rad * 1.6, rad * 0.32,
                               curl=0.4, segments=4), bone, "horn", **kw)
    if club:   # massue : couronne de crochets autour du bout
        tip, prev = path[-1], path[-2]
        tan = (tip - prev).normalized()
        side, up = a._basis(tan)
        for j in range(6):
            ang = 2 * math.pi * j / 6
            out = side * math.cos(ang) + up * math.sin(ang)
            rig.add(a.claw(f"{name}ClubHook{j}", tip - tan * 0.15 + out * radii[-1] * 0.9,
                           out - tan * 0.4, 0.35, 0.05, curl=0.35, segments=4), bones[-1], "horn",
                    **kw)
        rig.add(a.crystal(f"{name}ClubGem", tip + tan * 0.12, 0.09, 0.3, sides=4), bones[-1],
                "glow", glow=True)


def build_web(rig):
    """Membrane sombre entre les racines des bras (comme le calmar-vampire)."""
    paths = [arm_path(k) for k in range(8)]
    for k in range(8):
        p, q = paths[k], paths[(k + 1) % 8]
        bk, bq = f"Arm{k}_1", f"Arm{(k + 1) % 8}_1"
        outline = [(tuple(HEAD_C + Vector((0, 0, -0.55))), {"Head": 1}),
                   (tuple(p[0]), {bk: 1}), (tuple(p[2]), {bk: 1}), (tuple(p[3]), {bk: 0.6, f"Arm{k}_2": 0.4})]
        mid = p[3].lerp(q[3], 0.5) - Vector((0, 0, 0.0))
        inward = HEAD_C.lerp(mid, 0.55)
        outline += [(pt, w) for pt, w in a.tattered_edge(p[3], q[3], {bk: 1}, {bq: 1}, inward,
                                                         depth=0.35, notches=1, seed=k)]
        outline += [(tuple(q[3]), {bq: 0.6, f"Arm{(k + 1) % 8}_2": 0.4}), (tuple(q[2]), {bq: 1}),
                    (tuple(q[0]), {bq: 1})]
        web = a.membrane(f"Web{k}", outline, thickness=0.04)
        rig.pal.paint(web, "membrane")
        web["part"] = "Arms"


def build_arms(rig):
    build_web(rig)
    for k in range(8):
        path = arm_path(k)
        radii = [0.27 - 0.2 * i / 12 for i in range(13)]
        build_limb(rig, f"Arm{k}", path, radii, [f"Arm{k}_{i + 1}" for i in range(4)], "Arms",
                   hooks_from=9)
        if k in (1, 4, 6):   # corail et balanes sur la racine de quelques bras
            tan = (path[2] - path[1]).normalized()
            _, up = a._basis(tan)
            coral(rig, f"ArmCoral{k}", path[1] + up * 0.22, up + tan * 0.3, 0.45, f"Arm{k}_1",
                  seed=k, part="Arms")
        if k in (2, 5, 7):
            tan = (path[3] - path[2]).normalized()
            _, up = a._basis(tan)
            barnacle(rig, f"ArmBarn{k}", path[3] + up * 0.18, up, f"Arm{k}_1", size=0.1,
                     part="Arms")
    for s, side in ((1, "L"), (-1, "R")):
        path = tentacle_path(s)
        radii = [0.2 - 0.09 * i / 16 for i in range(17)]
        radii[-3:] = [0.17, 0.19, 0.18]     # massue élargie
        build_limb(rig, f"Tent{side}", path, radii, [f"Tentacle_{side}_{i + 1}" for i in range(5)],
                   "Tentacles", hooks_from=12, club=True)


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    head = a.loft_profile("HeadCapsule", HEAD, droop=0.1)
    a.cut(head, [a.hole_x((0, EYE[0], EYE[1]), 0.36, 0.36)])
    rig.add(head, H, "bone")
    for s in (-1, 1):
        x = a.side_width(HEAD, EYE[0], EYE[1])
        # Œil géant de calmar : globe lumineux + pupille sombre en barre + paupière d'os
        rig.add(r.ico(f"Eye{s}", 0.33, subdivisions=2, location=(s * (x - 0.12), EYE[0], EYE[1])),
                H, "glow", glow=True)
        rig.add(r.box(f"Pupil{s}", (0.06, 0.42, 0.1), location=(s * (x + 0.19), EYE[0], EYE[1]),
                      rotation=(0.25, 0, 0)), H, "ink")
        for rad, thick, dx in ((0.42, 0.07, 0.0), (0.47, 0.05, 0.07)):
            rig.add(a.ring_around(f"OrbitRim{s}{rad}", (s * (x + dx), EYE[0], EYE[1]), (1, 0, 0),
                                  rad, thick, segments=16), H, "bone_shade")
        # Couronne de photophores autour de l'œil
        for i in range(8):
            ang = 2 * math.pi * i / 8
            photophore(rig, f"EyePhoto{s}{i}", (s * (x + 0.04), EYE[0] + math.cos(ang) * 0.56,
                                                EYE[1] + math.sin(ang) * 0.56), H, size=0.045)
        # Arcade lourde au-dessus de l'œil, avec 3 piques courtes
        rig.add(a.blade(f"Brow{s}", (s * 0.4, -0.65, 2.98), (s * 0.95, 0.2, 2.9), 0.3, 0.14,
                        width_end=0.22, mid=0.36, normal=(0, 0.1, 1)), H, "bone_shade")
        for i in range(3):
            rig.add(a.claw(f"BrowSpike{s}{i}", (s * (0.55 + i * 0.17), -0.4 + i * 0.25, 3.0),
                           (s * 0.5, 0.6, 0.6), 0.28, 0.05, curl=-0.1, segments=4), H, "horn")
        # Crête de joue sous l'œil
        rig.add(r.tube(f"CheekRidge{s}", [(s * 0.62, -0.75, 1.75), (s * 0.95, -0.2, 1.72),
                                          (s * 0.9, 0.45, 1.85)], [0.06, 0.08, 0.05],
                       segments=5), H, "bone_shade")
        # Balanes sur le crâne
        for i, (yy, zz) in enumerate(((0.45, 2.85), (0.65, 2.5))):
            nrm = Vector((s * 1, 0.3, 0.5))
            barnacle(rig, f"HeadBarn{s}{i}", (s * a.side_width(HEAD, yy, zz) * 0.95, yy, zz), nrm, H,
                     size=0.09 + 0.02 * i)
    # Siphon (entonnoir) : tube d'os qui sort sous la tête vers l'avant
    siphon = [(0, -0.5, 1.6), (0, -0.85, 1.6), (0, -1.1, 1.72)]
    rig.add(r.tube("Siphon", siphon, [0.22, 0.17, 0.15], segments=10, cap=False), H, "bone_shade")
    rig.add(a.ring_around("SiphonLip", siphon[-1], (0, -1, 0.3), 0.15, 0.04, segments=12), H,
            "bone")
    rig.add(r.ico("SiphonGlow", 0.1, subdivisions=1, location=(0, -1.0, 1.7)), H, "glow", glow=True)
    # Bec de perroquet : mandibule supérieure crochue, inférieure qui remonte
    rig.add(a.claw("BeakUpper", (0, -0.55, 1.62), (0, -0.55, -1), 0.6, 0.2, curl=0.55, segments=7),
            H, "horn")
    rig.add(a.claw("BeakLower", (0, -0.5, 1.4), (0, -1, 0.25), 0.45, 0.15, curl=-0.35, segments=6),
            J, "horn")
    for s in (-1, 1):
        rig.add(a.claw(f"BeakEdge{s}", (s * 0.12, -0.6, 1.45), (s * 0.2, -1, 0.1), 0.28, 0.05,
                       curl=-0.2, segments=4), J, "horn_tip")
    # Masque facial : crête frontale à piques, arêtes front → joues, crochets près du bec
    front = [(0, yy, a.width_at(HEAD, yy, 4) - 0.02) for yy in (0.1, -0.35, -0.75)]
    front.append((0, -0.98, 2.45))
    front.append((0, -1.02, 2.0))
    rig.add(r.tube("FaceCrest", front, [0.07, 0.09, 0.1, 0.09, 0.07], segments=6), H, "bone_shade")
    for i, p in enumerate(front[:4]):
        rig.add(a.claw(f"CrestSpike{i}", p, (0, -0.4 - 0.3 * (i == 3), 1 - 0.6 * (i == 3)),
                       0.3 - 0.04 * i, 0.06, curl=-0.1, segments=4), H, "horn")
    for s in (-1, 1):
        mask = [(s * 0.3, -0.85, 2.85), (s * 0.5, -0.95, 2.4), (s * 0.55, -0.88, 1.95),
                (s * 0.45, -0.72, 1.62)]
        rig.add(r.tube(f"MaskRidge{s}", mask, [0.05, 0.07, 0.07, 0.05], segments=5), H,
                "bone_shade")
        for i, p in enumerate(mask[1:3]):
            photophore(rig, f"MaskPhoto{s}{i}", Vector(p) + Vector((s * 0.03, -0.07, 0)), H,
                       size=0.055)
        rig.add(a.claw(f"BeakHook{s}", (s * 0.45, -0.75, 1.65), (s * 0.4, -1, -0.6), 0.4, 0.08,
                       curl=0.35, segments=5), H, "horn")
    # Couronne de crocs autour du bec (bouche de démon des abysses)
    for i in range(10):
        ang = 2 * math.pi * i / 10
        base = Vector((math.cos(ang) * 0.38, -0.55 + math.sin(ang) * 0.3, 1.5))
        rig.add(a.claw(f"MouthFang{i}", base, (-math.cos(ang) * 0.4, -math.sin(ang) * 0.3, -1),
                       0.28, 0.05, curl=-0.15, segments=4), H, "tooth")
    rig.add(a.ring_around("MouthRim", (0, -0.55, 1.52), (0, 0, 1), 0.42, 0.06, segments=16), H,
            "bone_shade")
    # Sutures en relief qui découpent le crâne en plaques
    for s in (-1, 1):
        rig.add(r.tube(f"Suture{s}", [(s * 0.25, -0.75, 2.85), (s * 0.55, -0.1, 3.0),
                                      (s * 0.5, 0.55, 2.95), (s * 0.3, 0.85, 2.7)],
                       [0.04, 0.05, 0.05, 0.03], segments=4), H, "bone_shade")
        for i, yy in enumerate((-0.45, 0.15, 0.6)):
            rig.add(r.ico(f"SkullKnob{s}{i}", 0.07, subdivisions=1,
                          location=(s * 0.36, yy, a.width_at(HEAD, yy, 4) - 0.01),
                          scale=(1, 1, 0.6)), H, "bone_shade")
    # Arête et corail sur le sommet du crâne
    rig.add(r.tube("CrownRidge", [(0, yy, 3.0 + 0.06 * math.cos(yy * 2)) for yy in (-0.6, 0.0, 0.6)],
                   [0.08, 0.1, 0.07], segments=5), H, "bone_shade")
    coral(rig, "HeadCoral", (0.35, 0.35, 3.0), (0.4, 0.3, 1), 0.55, H, seed=3)


# ---------------------------------------------------------------- manteau

def build_mantle(rig):
    M = "Mantle"
    bars = 8
    # Côtes : partent de la plume dorsale (dos du manteau) et s'enroulent vers l'avant, en
    # laissant une ouverture devant (on voit l'organe lumineux à l'intérieur)
    back_ang = math.pi / 2 + 0.2        # direction du dos dans le repère (side, other)
    for i, t in enumerate((0.06, 0.17, 0.28, 0.39, 0.5, 0.61, 0.72, 0.82, 0.9)):
        ctr, axis, side, other = mantle_frame(t)
        rad = hoop_radius(t)
        for sd in (-1, 1):
            pts = []
            for f in range(8):
                ang = back_ang + sd * (0.15 + 2.55 * f / 7)
                wobble = 1 + 0.05 * math.sin(f * 1.7 + i)
                pts.append(ctr + (side * math.cos(ang) + other * math.sin(ang)) * rad * wobble
                           - axis * 0.08 * f / 7)
            rib = r.tube(f"MRib{i}{sd}", [tuple(p) for p in pts],
                         [0.085 - 0.04 * f / 7 for f in range(8)], segments=5)
            r.smooth(rib, 45)
            rig.add(rib, M, "bone")
            # Pointe recourbée au bout de la côte, et piques le long du flanc
            tip_dir = (pts[-1] - pts[-2]).normalized()
            rig.add(a.claw(f"MRibHook{i}{sd}", pts[-1], tip_dir - axis * 0.3, 0.22, 0.04,
                           curl=0.3, segments=4), M, "horn")
            if i % 2 == 0:
                out = (pts[3] - ctr).normalized()
                rig.add(a.claw(f"MRibSpike{i}{sd}", pts[3], out + axis * 0.4, 0.3, 0.05,
                               curl=-0.1, segments=4), M, "horn")
            if i % 3 == 1:
                photophore(rig, f"RibPhoto{i}{sd}", pts[5], M, size=0.06)
    # Vertèbres le long de la plume dorsale
    back = Vector((0, 1, -0.18)).normalized()
    for i in range(10):
        t = 0.04 + 0.86 * i / 9
        ctr, axis, side, other = mantle_frame(t)
        p = ctr + (side * math.cos(back_ang) + other * math.sin(back_ang)) * hoop_radius(t)
        rig.add(a.vertebra(f"MSpine{i}", p, axis, 0.2, spine=1.2, lean=-0.4, transverse=False), M,
                "bone_shade")
    # Pointe du manteau
    rig.add(a.claw("MantleTip", MANTLE_A.lerp(MANTLE_B, 0.96), MANTLE_B - MANTLE_A, 0.8, 0.22,
                   curl=0, segments=6), M, "bone_shade")
    # Gladius : plume d'os plate le long du dos
    back = Vector((0, 1, -0.18)).normalized()
    rig.add(a.blade("Gladius", MANTLE_A + back * 0.95, MANTLE_B + back * 0.15, 0.4, 0.07,
                    width_end=0.12, mid=0.6, normal=back), M, "bone_shade")
    # Nageoires : membranes à rayons osseux de chaque côté du haut du manteau
    for s in (-1, 1):
        root_lo, _, _, _ = mantle_frame(0.62)
        root_hi, _, _, _ = mantle_frame(0.92)
        p_lo = root_lo + Vector((s * hoop_radius(0.62), 0, 0))
        p_hi = root_hi + Vector((s * 0.4, 0, 0))
        tip = MANTLE_A.lerp(MANTLE_B, 0.78) + Vector((s * 2.0, 0.1, -0.2))
        outline = [(tuple(p_lo), {M: 1}), (tuple(tip), {M: 1})]
        outline += [(p, {M: 1}) for p, _ in a.tattered_edge(tip, p_hi, {M: 1}, {M: 1},
                                                             p_lo.lerp(p_hi, 0.5), depth=0.25,
                                                             notches=2, seed=4 + s)]
        outline.append((tuple(p_hi), {M: 1}))
        fin = a.membrane(f"Fin{s}", outline, thickness=0.05)
        rig.pal.paint(fin, "membrane")
        for i, f in enumerate((0.3, 0.6, 0.85)):
            start = p_lo.lerp(p_hi, f)
            rig.add(r.tube(f"FinRay{s}{i}", [tuple(start), tuple(start.lerp(tip, 0.85))],
                           [0.05, 0.025], segments=4), M, "bone_shade")
    # Organe lumineux + poche d'encre dans la cage
    heart = MANTLE_A.lerp(MANTLE_B, 0.38)
    rig.add(a.crystal("Heart", heart, 0.35, 1.0, sides=6), M, "glow", glow=True)
    rig.add(r.ico("InkSac", 0.32, subdivisions=2, location=heart + Vector((0, 0.45, -0.6)),
                  scale=(1, 0.8, 1.3)), M, "ink")
    for i in range(5):   # bulles lumineuses qui montent dans la cage
        p = MANTLE_A.lerp(MANTLE_B, 0.5 + 0.08 * i) + Vector((0.25 * math.sin(i * 2.1), 0,
                                                              0.0))
        photophore(rig, f"Bubble{i}", p, M, size=0.09 - 0.012 * i)
    # Balanes et corail accrochés à la cage (sur le dos, là où il y a de l'os)
    for i, (t, ang) in enumerate(((0.17, 1.2), (0.39, 2.3), (0.61, 1.0), (0.28, 2.6))):
        ctr, axis, side, other = mantle_frame(t)
        out = side * math.cos(ang) + other * math.sin(ang)
        barnacle(rig, f"MantleBarn{i}", ctr + out * (hoop_radius(t) + 0.04), out, M, size=0.11)
    ctr, axis, side, other = mantle_frame(0.39)
    out = side * math.cos(2.0) + other * math.sin(2.0)
    coral(rig, "MantleCoral", ctr + out * 1.32, out + axis * 0.4, 0.7, M, seed=8)


def build(pal):
    rig = c.Rig(pal)
    bone_rig(rig)
    build_head(rig)
    build_mantle(rig)
    build_arms(rig)
    return rig
