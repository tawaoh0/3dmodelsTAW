"""Golem de magma squelette (≈ 7 studs de haut, voûté) — créature animable.
Pack « Enfers volcaniques », créature 3.

Modèle : un crâne de géant primitif (type homme de Néandertal surdimensionné) — énorme
bourrelet sus-orbitaire, orbites tournées vers l'avant, pommettes saillantes, crête
sagittale, mâchoire massive mais arrondie ; squelette de colosse aux avant-bras énormes.

Identité : os d'obsidienne noire fendus de veines de lave ; pas de cornes mais une
**couronne d'orgues basaltiques** (prismes hexagonaux) sur le crâne, les épaules et le dos ;
lave qui coule des yeux et de la gueule ; poings massifs hérissés de colonnes de basalte ;
cœur de magma dans une cage en tonneau ; thème d'effets « magma ».

4 pièces Roblox : corps, Head, Arms, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, UpperArm/ForeArm/Fist_{L,R}, Thigh/Shin/Foot_{L,R}, FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#2f2826",
    "bone_shade": "#4d3832",
    "tooth": "#e8d9bf",
    "horn": "#141010",
    "horn_tip": "#ff7a00",
    "disc": "#3a1a10",
    "basalt": "#5e5856",
    "gum": "#6a2210",
    "ink": "#0b0807",
    "glow": "#ff7a00",
    "glow_hot": "#ffe08a",
}

EFFECT_THEME = "magma"

TEST_POSE = {
    "Jaw": (20, 0, 0),
    "UpperArm_L": (-50, 0, 0),
    "ForeArm_L": (-40, 0, 0),
    "Thigh_R": (20, 0, 0),
    "Head": (-12, 0, 0),
}

VIEW = (0.9, -1.0, 0.3)

SPINE = a.smooth_path([(0, 0.45, 3.4), (0, 0.2, 4.3), (0, -0.4, 5.1), (0, -0.85, 5.55)], 16)
NECK = a.smooth_path([(0, -0.85, 5.55), (0, -0.95, 5.72), (0, -1.0, 5.85)], 4)
# Crâne de géant : (y, demi-larg. dessus, tempes, bas, z dessus, z bas)
SKULL = [(-0.55, 0.42, 0.5, 0.38, 6.62, 5.85), (-0.95, 0.56, 0.63, 0.5, 6.95, 5.75),
         (-1.35, 0.53, 0.6, 0.5, 6.9, 5.7), (-1.62, 0.45, 0.52, 0.46, 6.68, 5.66),
         (-1.76, 0.33, 0.4, 0.36, 6.42, 5.66)]   # face plate de crâne humain, pas de museau
UPPER = (0.42, 0.62, 5.66, 5.7)      # arc dentaire du haut (demi-larg., longueur, z avant, z arrière)
LOWER = (0.47, 0.7, 5.42, 5.55)
Y_BACK = -1.22
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def arc(width, length, z_front, z_back, n=11):
    pts = []
    for i in range(n):
        th = -math.pi / 2 + math.pi * i / (n - 1)
        cth = math.cos(th)
        pts.append(Vector((width * math.sin(th), Y_BACK - length * cth,
                           z_back + (z_front - z_back) * cth ** 1.3)))
    return pts


def out_of(p, width, length):
    v = Vector((p.x / width ** 2, (p.y - Y_BACK) / length ** 2, 0))
    return v.normalized() if v.length > 1e-6 else Vector((0, -1, 0))


def column(rig, name, base, direction, height, radius, bone, glow_top=True, **kw):
    """Orgue basaltique : prisme hexagonal à sommet plat, lueur de lave au sommet."""
    base, d = Vector(base), Vector(direction).normalized()
    top = base + d * height
    rig.add(r.tube(name, [tuple(base - d * 0.1), tuple(top)], radius, segments=6), bone, "basalt",
            **kw)
    rig.add(r.tube(f"{name}Rim", [tuple(top - d * 0.06), tuple(top + d * 0.01)], radius * 1.08,
                   segments=6), bone, "bone_shade", **kw)
    if glow_top:
        rig.add(r.ico(f"{name}Lava", radius * 0.6, subdivisions=1, location=top + d * 0.02,
                      scale=(1, 1, 0.4)), bone, "glow", glow=True)


def cluster(rig, name, center, up, bone, n=5, height=0.7, radius=0.12, seed=0, **kw):
    up = Vector(up).normalized()
    side, fwd = a._basis(up)
    for k in range(n):
        ang = 2 * math.pi * k / n + seed
        rr = 0.0 if k == 0 else radius * 2.1
        base = Vector(center) + (side * math.cos(ang) + fwd * math.sin(ang)) * rr
        d = up + (side * math.cos(ang) + fwd * math.sin(ang)) * (0 if k == 0 else 0.25)
        column(rig, f"{name}{k}", base, d, height * (1.0 if k == 0 else 0.55 + 0.1 * (k % 3)),
               radius * (1.0 if k == 0 else 0.8), bone, **kw)


def crack(rig, name, a_pt, b_pt, radius, bone, seed=0):
    """Veine de lave le long d'un os long (posée sur sa surface)."""
    a_pt, b_pt = Vector(a_pt), Vector(b_pt)
    side, up = a._basis(b_pt - a_pt)
    off = (side * math.cos(seed) + up * math.sin(seed)) * radius * 1.02
    mr.scar(rig, name, a_pt.lerp(b_pt, 0.2) + off, a_pt.lerp(b_pt, 0.8) + off, bone,
            width=radius * 0.4, seed=seed)


def arm_points(s):
    return (Vector((s * 1.25, -0.55, 5.15)), Vector((s * 1.8, -0.25, 3.7)),
            Vector((s * 1.8, -1.0, 2.35)), Vector((s * 1.84, -1.22, 1.85)))


def leg_points(s):
    return (Vector((s * 0.65, 0.45, 3.25)), Vector((s * 0.85, -0.15, 1.8)),
            Vector((s * 0.85, 0.15, 0.45)), Vector((s * 0.88, -0.35, 0.15)))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], (0, -1.95, 6.3), "Neck")
    rig.bone("Jaw", (0, -0.98, 5.95), (0, -1.9, 5.2), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, fs = arm_points(s)
        rig.bone(f"UpperArm_{side}", sh, el, "Spine3")
        rig.bone(f"ForeArm_{side}", el, wr, f"UpperArm_{side}")
        rig.bone(f"Fist_{side}", wr, fs, f"ForeArm_{side}")
        hp, kn, an, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Spine1")
        rig.bone(f"Shin_{side}", kn, an, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", an, ft, f"Shin_{side}")
        rig.fx(f"Eye{side}", (s * 0.22, -1.7, 6.42), "Head")
        rig.fx(f"Fist{side}", fs + Vector((0, -0.3, 0)), f"Fist_{side}")
        rig.fx(f"Shoulder{side}", sh + Vector((s * 0.1, 0.1, 0.9)), "Spine3")
    rig.fx("Heart", (0, -0.35, 4.1), "Spine2")
    rig.fx("Mouth", (0, -1.75, 5.5), "Head")
    rig.fx("Crown", (0, -1.0, 7.6), "Head")


# ---------------------------------------------------------------- crâne

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.05, tip_length=0.1)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_along((sx * 0.22, -1.75, 6.42), (0, 1, 0), (1, 0, 0), 0.15, 0.14,
                               depth=0.45) for sx in (-1, 1)]
          + [a.hole_along((0, -1.8, 6.12), (0, 1, 0), (1, 0, 0), 0.07, 0.11, depth=0.4),
             a.hole_x((0, -1.0, 6.18), 0.22, 0.15)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 10))
        return p

    # Bourrelet sus-orbitaire massif, glabelle, crête sagittale, nucale
    brow = [(-0.52, -1.58, 6.6), (-0.24, -1.84, 6.64), (0, -1.82, 6.6), (0.24, -1.84, 6.64),
            (0.52, -1.58, 6.6)]
    rig.add(r.tube("Brow", brow, [0.08, 0.11, 0.1, 0.11, 0.08], segments=7), H, "bone", **HEAD)
    rig.add(a.band("Sagittal", [top(0, y) for y in (-0.6, -0.9, -1.2, -1.45)],
                   [0.12, 0.2, 0.16, 0.06], 0.08, offset=0.2), H, "bone_shade", **HEAD)
    rig.add(r.tube("Nuchal", [(-0.4, -0.58, 6.15), (0, -0.5, 6.25), (0.4, -0.58, 6.15)], 0.07,
                   segments=5), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        # Yeux de lave au fond des orbites, coulées de lave sur les joues
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=(s * 0.22, -1.6, 6.42)), H, "glow",
                glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", (s * 0.22, -1.79, 6.42), (0, -1, 0), 0.16, 0.04,
                              segments=10), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"LavaTear{s}", [(s * 0.26, -1.82, 6.3), (s * 0.3, -1.84, 6.1),
                                        (s * 0.33, -1.8, 5.92)], [0.035, 0.03, 0.02], segments=4),
                H, "glow", glow=True)
        # Pommettes et arcades zygomatiques
        zyg = a.smooth_path([(s * 0.42, -1.68, 6.22), (s * 0.6, -1.3, 6.18), (s * 0.55, -0.9, 6.05)],
                            5)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg], [0.09, 0.08, 0.07, 0.065, 0.06],
                       segments=6), H, "bone", **HEAD)
        rig.add(a.claw(f"CheekSpike{s}", zyg[1], (s, 0.3, -0.2), 0.22, 0.05, curl=0, segments=4),
                H, "horn", **HEAD)
        # Fissures de lave sur le crâne, foramens
        mr.scar(rig, f"SkullCrack{s}", top(s * 0.2, -0.75), top(s * 0.35, -1.35), H, width=0.06,
                seed=s)
        mr.scar(rig, f"TempleCrack{s}", (s * 0.6, -1.3, 6.5), (s * 0.55, -0.75, 6.35), H,
                width=0.05, seed=s + 3)
        for k in range(3):
            rig.add(r.ico(f"Foramen{s}{k}", 0.035, subdivisions=1,
                          location=(s * 0.35, -1.84 + 0.04 * k, 6.0 - 0.08 * k)), H, "ink",
                    **HEAD)
    # Réseau de fissures de lave qui rayonne depuis le sommet du crâne (sutures éclatées)
    for k in range(6):
        ang = 2 * math.pi * k / 6 + 0.3
        p0 = top(0.08 * math.cos(ang), -1.05 + 0.08 * math.sin(ang))
        p1 = top(0.42 * math.cos(ang), -1.05 + 0.42 * math.sin(ang))
        if p0 is not None and p1 is not None:
            mr.scar(rig, f"Suture{k}", p0 + Vector((0, 0, 0.01)), p1, H, width=0.05, seed=k)
    rig.add(a.ring_around("NasalRim", (0, -1.8, 6.12), (0, -1, 0), 0.11, 0.035, segments=10), H,
            "bone_shade", **HEAD)
    rig.add(a.claw("Vomer", (0, -1.7, 6.0), (0, -0.4, 1), 0.2, 0.03, curl=0, segments=4), H,
            "bone_shade", **HEAD)
    # Couronne d'orgues basaltiques
    for k in range(7):
        ang = math.pi * (k / 6)
        x, y = 0.42 * math.cos(ang), -1.05 + 0.32 * math.sin(ang) - 0.15
        base = top(x, y) or Vector((x, y, 6.8))
        column(rig, f"Crown{k}", base, (x * 0.8, 0.2, 1), 0.45 + 0.35 * math.sin(ang), 0.09, H,
               **HEAD)
    # Rangée du haut (molaires larges, prémolaires, canines, incisives) + gencive
    up_pts = arc(*UPPER)
    rig.add(r.tube("UpperGum", [tuple(p + Vector((0, 0, 0.05)) - out_of(p, UPPER[0], UPPER[1]) * 0.05)
                                for p in up_pts], 0.06, segments=5), H, "gum", **HEAD)
    rig.add(a.band("Maxilla", up_pts, 0.16, 0.12, offset=0), H, "bone_shade", **HEAD)
    teeth_kind = ["mol", "mol", "pm", "can", "inc", "inc", "inc", "can", "pm", "mol", "mol"]
    for i, (p, kind) in enumerate(zip(up_pts, teeth_kind)):
        size = {"mol": 0.16, "pm": 0.17, "can": 0.3, "inc": 0.15}[kind]
        width = {"mol": 0.17, "pm": 0.13, "can": 0.12, "inc": 0.09}[kind]
        o = out_of(p, UPPER[0], UPPER[1])
        rig.add(mr.tooth(f"UpTooth{i}", p, p + Vector((0, 0, -size)) - o * 0.03, width, width * 0.6,
                         o, curl=0.08 if kind == "can" else 0.02), H, "tooth", **HEAD)
    for k, i in enumerate((2, 5, 8)):   # bave de lave qui pend
        p = up_pts[i] - out_of(up_pts[i], UPPER[0], UPPER[1]) * 0.08
        rig.add(r.tube(f"LavaDrool{k}", [tuple(p), tuple(p + Vector((0, 0.02, -0.25 - 0.08 * k)))],
                       [0.03, 0.015], segments=4), H, "glow", glow=True)
    # Mâchoire arrondie en bol, branches montantes jusqu'à la charnière
    lo_pts = arc(*LOWER)
    fr = [max(0.0, min(1.0, (Y_BACK - p.y) / LOWER[1])) for p in lo_pts]
    lo = [out_of(p, LOWER[0], LOWER[1]) for p in lo_pts]
    lh = [0.34 - 0.06 * f + 0.06 * math.sin(math.pi * f) for f in fr]
    lu = [Vector((0, 0, 1)) + o * 0.4 for o in lo]
    rig.add(a.band("Mandible", lo_pts, lh, 0.16, up=lu, offset=1), J, "bone", **HEAD)
    bottom = [p - u.normalized() * h for p, u, h in zip(lo_pts, lu, lh)]
    rig.add(r.tube("MandibleBase", [tuple(q) for q in bottom], 0.06, segments=5), J, "bone_shade",
            **HEAD)
    rig.add(r.ico("Chin", 0.12, subdivisions=1, location=bottom[5] + Vector((0, -0.04, 0.05)),
                  scale=(1.4, 1, 1)), J, "bone_shade", **HEAD)
    for s, i in ((-1, 0), (1, 10)):
        rig.add(a.blade(f"Ramus{s}", lo_pts[i] + Vector((0, 0.05, -0.1)),
                        Vector((s * 0.5, -0.98, 5.95)), 0.3, 0.1, width_end=0.18,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Condyle{s}", 0.1, subdivisions=1, location=(s * 0.5, -0.98, 5.97)), H,
                "bone_shade", **HEAD)
    rig.add(r.tube("LowerGum", [tuple(p - Vector((0, 0, 0.04)) - o * 0.05)
                                for p, o in zip(lo_pts, lo)], 0.06, segments=5), J, "gum", **HEAD)
    for i, (p, kind) in enumerate(zip(lo_pts, teeth_kind)):
        size = {"mol": 0.14, "pm": 0.15, "can": 0.26, "inc": 0.13}[kind]
        width = {"mol": 0.16, "pm": 0.12, "can": 0.11, "inc": 0.08}[kind]
        rig.add(mr.tooth(f"LowTooth{i}", p, p + Vector((0, 0, size)) - lo[i] * 0.03, width,
                         width * 0.6, lo[i], curl=0.08 if kind == "can" else 0.02), J, "tooth",
                **HEAD)
    for i in (2, 4, 6, 8):
        rig.add(r.ico(f"JawPore{i}", 0.035, subdivisions=1,
                      location=lo_pts[i] + lo[i] * 0.09 - Vector((0, 0, lh[i] * 0.55))), J, "ink",
                **HEAD)
    rig.add(r.ico("Throat", 0.2, subdivisions=2, location=(0, -1.35, 5.6), scale=(1.4, 1.4, 0.7)),
            H, "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for path, bonef, size in ((SPINE, spine_bone, 0.3), (NECK, lambda i: "Neck", 0.24)):
        for i in range(len(path)):
            t = tangent(path, i)
            rig.add(a.vertebra(f"Vert{size}{i}", path[i], t, size, spine=1.2, lean=0.4), bonef(i),
                    "bone")
            if i < len(path) - 1:
                rig.add(a.disc(f"Disc{size}{i}", path[i].lerp(path[i + 1], 0.5), t, size),
                        bonef(i), "glow", glow=True)
    # Cage en tonneau, sternum, cœur de magma
    sternum = []
    for k, i in enumerate(range(5, 15)):
        hw = 0.85 + 0.3 * math.sin(math.pi * k / 9)
        depth = 1.3 + 0.5 * math.sin(math.pi * (k + 1) / 11)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.25, radius=0.1),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.3, -depth)))
    rig.add(r.tube("Sternum", [tuple(p) for p in sternum[1:-1:2]], 0.12, segments=6), "Spine2",
            "bone_shade")
    rig.add(r.ico("MagmaCore", 0.45, subdivisions=2, location=(0, -0.35, 4.1)), "Spine2", "glow",
            glow=True)
    for k in range(6):
        ang = 2 * math.pi * k / 6
        rig.add(a.crystal(f"CoreShard{k}", (0.35 * math.cos(ang), -0.35 + 0.35 * math.sin(ang), 3.75),
                          0.08, 0.6, sides=6), "Spine2", "basalt")
    # Orgues basaltiques sur le dos et les épaules
    for k, i in enumerate((4, 8, 12)):
        side, up = a._basis(tangent(SPINE, i))
        cluster(rig, f"BackColumns{k}", SPINE[i] + up * 0.35, up + Vector((0, 0.4, 0)),
                spine_bone(i), n=4, height=0.8 - 0.1 * k, radius=0.12, seed=k)
    # Omoplates, clavicules, bassin
    for s in (-1, 1):
        sh = arm_points(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[12] + Vector((s * 0.3, 0.1, 0.1)),
                        sh + Vector((0, 0.1, 0.05)), 0.7, 0.1, width_end=0.35, mid=0.75,
                        normal=(0.3 * s, 0.5, 1)), "Spine3", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, sternum[-2] + Vector((s * 0.2, 0, 0)), 0.08,
                            condyles=False), "Spine3", "bone_shade")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.2, 0, 0)),
                        hp + Vector((s * 0.25, -0.1, 0.6)), 0.6, 0.1, width_end=0.45, mid=0.7,
                        normal=(s, 0, 0.3)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.35, 0.1, 2.85), (0, 0.15, 2.8)], 0.09,
                       segments=5), "Spine1", "bone")
        rig.add(a.ring_around(f"Hip{s}", hp, (s, 0, 0), 0.2, 0.05, segments=10), "Spine1", "glow",
                glow=True)


def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, fs = arm_points(s)
        ua, fa, fb = f"UpperArm_{side}", f"ForeArm_{side}", f"Fist_{side}"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.2, segments=8), ua, "bone", **ARMS)
        crack(rig, f"HumerusCrack{s}", sh, el, 0.2, ua, seed=1 + s)
        side_v = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.15
        rig.add(a.long_bone(f"Radius{s}", el + side_v, wr + side_v, 0.17, segments=8), fa, "bone",
                **ARMS)
        rig.add(a.long_bone(f"Ulna{s}", el - side_v, wr - side_v, 0.15, segments=8), fa,
                "bone_shade", **ARMS)
        crack(rig, f"ForearmCrack{s}", el + side_v, wr + side_v, 0.17, fa, seed=2)
        for q, bone in ((sh, ua), (el, fa), (wr, fb)):
            rig.add(a.ring_around(f"Joint{s}{bone}", q, el - sh if bone == ua else wr - el, 0.27,
                                  0.06, segments=10), bone, "glow", glow=True)
        cluster(rig, f"ShoulderColumns{s}", sh + Vector((s * 0.1, 0.05, 0.2)),
                (s * 0.4, 0.2, 1), ua, n=5, height=0.9, radius=0.13, seed=s, **ARMS)
        column(rig, f"ElbowColumn{s}", el + Vector((0, 0.15, 0)), (s * 0.2, 1, 0.3), 0.55, 0.1, fa,
               **ARMS)
        # Poing massif relié au poignet (carpe + métacarpes), 4 doigts repliés, pouce,
        # colonnes de basalte aux jointures
        rig.add(r.ico(f"Carpal{s}", 0.2, subdivisions=1, location=wr.lerp(fs, 0.45)), fb,
                "bone_shade", **ARMS)
        for j in range(3):
            off = Vector((s * (j - 1) * 0.12, 0, 0))
            rig.add(a.long_bone(f"Metacarpal{s}{j}", wr + off * 0.5, fs + off + Vector((0, -0.1, 0.1)),
                                0.07, condyles=False, segments=5), fb, "bone", **ARMS)
        rig.add(r.ico(f"Palm{s}", 0.3, subdivisions=2, location=fs, scale=(0.9, 1.0, 0.8)), fb,
                "bone", **ARMS)
        for j in range(4):
            x = s * (0.18 - 0.12 * j) * (1 if s > 0 else 1) + fs.x
            base = Vector((x, fs.y - 0.2, fs.z + 0.12))
            curl = [base, base + Vector((0, -0.22, -0.05)), base + Vector((0, -0.2, -0.3)),
                    base + Vector((0, -0.02, -0.38))]
            rig.add(r.tube(f"Finger{s}{j}", [tuple(p) for p in curl], [0.09, 0.085, 0.08, 0.06],
                           segments=6), fb, "bone", **ARMS)
            rig.add(r.ico(f"Knuckle{s}{j}", 0.1, subdivisions=1, location=curl[1]), fb,
                    "bone_shade", **ARMS)
            column(rig, f"KnuckleColumn{s}{j}", curl[1], (0, -1, 0.15), 0.3 + 0.05 * (j % 2), 0.06,
                   fb, glow_top=j % 2 == 0, **ARMS)
        thumb = [fs + Vector((-s * 0.25, -0.05, 0.05)), fs + Vector((-s * 0.3, -0.3, -0.05)),
                 fs + Vector((-s * 0.12, -0.42, -0.12))]
        rig.add(r.tube(f"Thumb{s}", [tuple(p) for p in thumb], [0.09, 0.08, 0.06], segments=6), fb,
                "bone", **ARMS)
        rig.add(r.tube(f"FistDrip{s}", [tuple(fs + Vector((0, 0, -0.25))),
                                        tuple(fs + Vector((0.03, 0, -0.55)))], [0.04, 0.015],
                       segments=4), fb, "glow", glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.21, segments=8), th, "bone", **LEGS)
        crack(rig, f"FemurCrack{s}", hp, kn, 0.21, th, seed=0.5 * s)
        rig.add(r.ico(f"Patella{s}", 0.14, subdivisions=1, location=kn + Vector((0, -0.18, 0.05))),
                th, "bone_shade", **LEGS)
        rig.add(a.long_bone(f"Tibia{s}", kn, an, 0.19, segments=8), sn, "bone", **LEGS)
        rig.add(a.long_bone(f"Fibula{s}", kn + Vector((s * 0.15, 0.08, 0)),
                            an + Vector((s * 0.12, 0.05, 0.1)), 0.07, condyles=False, segments=5),
                sn, "bone_shade", **LEGS)
        crack(rig, f"TibiaCrack{s}", kn, an, 0.19, sn, seed=2.5)
        for q, bone, d in ((kn, sn, an - kn), (an, fo, ft - an)):
            rig.add(a.ring_around(f"LegJoint{s}{bone}", q, d, 0.25, 0.055, segments=10), bone,
                    "glow", glow=True)
        column(rig, f"KneeColumn{s}", kn + Vector((0, -0.12, 0.1)), (s * 0.2, -1, 0.5), 0.45, 0.09,
               th, **LEGS)
        # Pied massif : talon + 3 orteils épais à griffes noires
        rig.add(r.ico(f"Heel{s}", 0.2, subdivisions=1, location=an + Vector((0, 0.15, -0.25)),
                      scale=(1, 1.2, 0.8)), fo, "bone_shade", **LEGS)
        for j in range(3):
            off = (j - 1) * 0.18
            base = an + Vector((s * off * 0.5, -0.05, -0.15))
            toe = Vector((ft.x + s * off, ft.y - 0.15, 0.14))
            rig.add(a.long_bone(f"Toe{s}{j}", base, toe, 0.08, condyles=False, segments=6), fo,
                    "bone", **LEGS)
            rig.add(a.claw(f"ToeClaw{s}{j}", toe, (0, -1, -0.5), 0.22, 0.07, curl=0.3, segments=5),
                    fo, "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_arms(rig)
    build_legs(rig)
    return rig
