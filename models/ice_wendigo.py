"""Wendigo squelette (≈ 10 studs de haut avec les bois) — créature animable.
Pack « Royaume de glace éternelle », créature 3.

Animal modèle : le cerf — crâne long et étroit, pédicules qui portent de grands **bois**
ramifiés, grandes orbites latérales, fossette lacrymale devant l'œil, long museau, mandibule
fine ; ici sur un corps humanoïde **très grand et décharné** aux sabots fendus.

Identité : os gris cendre sales et maigres, bois sombres givrés aux pointes ; gueule pleine
de crocs fins et serrés (la faim) ; côtes saillantes et colonne aux épines hautes ; bras
démesurés aux doigts interminables ; cœur gelé ; lueur blanc glacé ; thème d'effets
« wraith » (brume spectrale).

4 pièces Roblox : corps, Head (crâne + bois), Arms, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, UpperArm/ForeArm/Hand_{L,R}, Thigh/Shin/Foot_{L,R}, FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#9a8f84",
    "bone_shade": "#4e453e",
    "tooth": "#f0ece0",
    "horn": "#1a1614",
    "horn_tip": "#e8f6ff",
    "disc": "#2e2724",
    "antler": "#4a3a2e",
    "ice": "#cfeeff",
    "gum": "#4a1a22",
    "ink": "#0b0a09",
    "glow": "#e8f6ff",
    "glow_hot": "#ffffff",
}

EFFECT_THEME = "wraith"

TEST_POSE = {
    "Jaw": (25, 0, 0),
    "Head": (15, 0, 10),
    "UpperArm_L": (-55, 0, 0),
    "ForeArm_L": (-35, 0, 0),
    "Thigh_R": (25, 0, 0),
}

VIEW = (0.95, -1.0, 0.25)

SPINE = a.smooth_path([(0, 0.4, 4.6), (0, 0.25, 5.5), (0, -0.15, 6.35), (0, -0.5, 6.9)], 20)
NECK = a.smooth_path([(0, -0.5, 6.9), (0, -0.7, 7.2), (0, -0.85, 7.45)], 5)
# Crâne de cerf : (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-0.85, 0.3, 0.38, 0.3, 7.85, 7.35), (-1.1, 0.36, 0.44, 0.34, 7.97, 7.3),
         (-1.4, 0.33, 0.42, 0.32, 7.88, 7.3), (-1.75, 0.22, 0.28, 0.24, 7.66, 7.32),
         (-2.2, 0.16, 0.2, 0.18, 7.5, 7.3), (-2.5, 0.13, 0.15, 0.14, 7.42, 7.3)]
EYE = (-1.4, 7.62)
HINGE = (0.3, -1.15, 7.3)
CHIN = (0.06, -2.4, 6.95)
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def arm_points(s):
    return (Vector((s * 0.6, -0.45, 6.6)), Vector((s * 0.9, -0.15, 4.85)),
            Vector((s * 0.95, -0.95, 3.4)), Vector((s * 1.0, -1.2, 2.95)))


def leg_points(s):
    return (Vector((s * 0.38, 0.4, 4.45)), Vector((s * 0.48, -0.45, 2.9)),
            Vector((s * 0.48, 0.5, 1.4)), Vector((s * 0.5, 0.1, 0.32)))


def antler_beam(s):
    return a.smooth_path([(s * 0.24, -1.05, 7.95), (s * 0.55, -0.95, 8.4), (s * 0.95, -0.75, 9.0),
                          (s * 1.15, -0.85, 9.6), (s * 1.0, -1.15, 10.15)], 12)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], (0, -2.55, 7.4), "Neck")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd = arm_points(s)
        rig.bone(f"UpperArm_{side}", sh, el, "Spine3")
        rig.bone(f"ForeArm_{side}", el, wr, f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", wr, hd, f"ForeArm_{side}")
        hp, kn, hk, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Spine1")
        rig.bone(f"Shin_{side}", kn, hk, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", hk, ft, f"Shin_{side}")
        rig.fx(f"Eye{side}", (s * 0.4, EYE[0], EYE[1]), "Head")
        rig.fx(f"Antler{side}", antler_beam(s)[-1], "Head")
        rig.fx(f"Claws{side}", hd + Vector((0, -0.2, -0.9)), f"Hand_{side}")
    rig.fx("Heart", (0, -0.4, 5.6), "Spine2")
    rig.fx("Mouth", (0, -1.8, 7.15), "Head")


# ---------------------------------------------------------------- tête de cerf et bois

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.12)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.17, 0.16),
                  a.hole_x((0, -1.78, 7.5), 0.13, 0.07),                    # fossette lacrymale
                  a.hole_x((0, -1.05, 7.55), 0.12, 0.1),
                  a.hole_along((0, -2.55, 7.38), (0, 1, 0), (1, 0, 0), 0.07, 0.06, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 15))
        return p

    # Os nasaux longs, crête frontale, fissures de givre
    for s in (-1, 1):
        rig.add(r.tube(f"Nasal{s}", [tuple(top(s * 0.06, y) + Vector((0, 0, 0.01)))
                                     for y in (-1.6, -2.0, -2.4)], [0.03, 0.035, 0.03], segments=4),
                H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Frontal{s}", [tuple(top(s * 0.2, y) + Vector((0, 0, 0.01)))
                                       for y in (-0.95, -1.2, -1.5)], [0.04, 0.045, 0.035],
                       segments=4), H, "bone_shade", **HEAD)
        mr.scar(rig, f"FrostCrack{s}", top(s * 0.12, -0.95), top(s * 0.1, -1.35), H, width=0.03,
                seed=s)
        # Grandes orbites latérales, œil blanc glacé, arcade
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=c0 - Vector((s * 0.07, 0, 0))), H,
                "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", c0, (s, -0.2, 0.1), 0.18, H, spikes=4, color="antler",
                       **HEAD)
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.32, -1.0, 7.38), (s * 0.45, -1.3, 7.4),
                                         (s * 0.3, -1.65, 7.42)], [0.04, 0.05, 0.04], segments=4),
                H, "bone", **HEAD)
        rig.add(a.ring_around(f"LacrimalRim{s}", (s * a.side_width(SKULL, -1.78, 7.5), -1.78, 7.5),
                              (s, 0, 0), 0.12, 0.025, segments=8), H, "bone_shade", **HEAD)
        # Pédicule + bois ramifié (andouillers), pointes givrées
        beam = antler_beam(s)
        rig.add(r.tube(f"Pedicle{s}", [(s * 0.18, -1.05, 7.85), tuple(beam[0])], 0.1, segments=7),
                H, "bone", **HEAD)
        rig.add(a.ring_around(f"Burr{s}", beam[0], beam[1] - beam[0], 0.12, 0.04, segments=10), H,
                "antler", **HEAD)
        rig.add(r.tube(f"Beam{s}", [tuple(p) for p in beam],
                       [0.09 - 0.005 * i for i in range(len(beam))], segments=6), H, "antler",
                **HEAD)
        for k, (i, d, ln) in enumerate(((2, (s * 0.1, -1, 0.5), 0.7), (4, (s * 0.2, -0.8, 0.9), 0.75),
                                        (6, (s * 0.6, 0.1, 1), 0.7), (8, (s * 0.2, -0.6, 1), 0.6),
                                        (9, (s * 0.9, 0.3, 0.6), 0.5))):
            base = beam[i]
            tine = a.claw(f"Tine{s}{k}", base, d, ln, 0.06, curl=-0.25, segments=5)
            rig.add(tine, H, "antler", **HEAD)
            tip, tdir = a.claw_point(base, Vector(d), ln, -0.25, 0.92)
            rig.add(a.claw(f"TineFrost{s}{k}", tip, tdir, 0.18, 0.035, curl=0, segments=4), H,
                    "ice", **HEAD)
        rig.add(a.claw(f"BeamFrost{s}", beam[-1], beam[-1] - beam[-2], 0.2, 0.04, curl=0,
                       segments=4), H, "ice", **HEAD)
        for k in (3, 7):
            rig.add(a.claw(f"AntlerIcicle{s}{k}", beam[k] - Vector((0, 0, 0.07)), (0, 0, -1), 0.25,
                           0.035, curl=0, segments=4), H, "ice", **HEAD)
    # Crocs fins et serrés (la faim) : rangée du haut sur tout le museau
    for s in (-1, 1):
        for k in range(9):
            y = -2.4 + 0.15 * k
            x = s * a.side_width(SKULL, y, 7.32) * 0.85
            size = 0.28 if k in (0, 1) else 0.18 + 0.02 * (k % 2)
            rig.add(mr.tooth(f"UpFang{s}{k}", (x, y, 7.32), (x, y + 0.02, 7.32 - size), size * 0.35,
                             size * 0.3, Vector((s, -0.2, 0)), curl=0.1), H, "tooth", **HEAD)
        gum = [(s * a.side_width(SKULL, y, 7.32) * 0.75, y, 7.33) for y in (-2.4, -1.9, -1.3)]
        rig.add(r.tube(f"UpperGum{s}", gum, 0.035, segments=4), H, "gum", **HEAD)
        # Mandibule longue et fine, crocs du bas
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.22, -1.6, 7.12)),
                Vector((s * 0.13, -2.05, 7.02)), Vector((s * 0.06, -2.4, 6.95))]
        rig.add(a.band(f"Mandible{s}", line, [0.24, 0.17, 0.13, 0.11], 0.07, offset=1), J, "bone",
                **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.08, 0)), line[0] + Vector((0, 0.02, 0.3)),
                        0.14, 0.05, width_end=0.06, normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.08, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
        for k in range(8):
            p = mr.along(line, 0.2 + 0.1 * k)
            size = 0.24 if k >= 6 else 0.15 + 0.02 * (k % 2)
            rig.add(mr.tooth(f"LowFang{s}{k}", p, p + Vector((0, -0.02, size)), size * 0.35,
                             size * 0.3, Vector((s, -0.2, 0)), curl=0.1), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.02, 0, 0.01))) for p in line[1:]],
                       0.03, segments=4), J, "gum", **HEAD)
    rig.add(r.ico("Throat", 0.15, subdivisions=2, location=(0, -1.35, 7.25), scale=(1.2, 1.8, 0.6)),
            H, "glow", glow=True)


# ---------------------------------------------------------------- corps décharné

def build_body(rig):
    for path, bonef, size, sp in ((SPINE, spine_bone, 0.17, 2.2), (NECK, lambda i: "Neck", 0.14, 1.2)):
        for i in range(len(path)):
            t = tangent(path, i)
            rig.add(a.vertebra(f"Vert{size}{i}", path[i], t, size, spine=sp, lean=0.5), bonef(i),
                    "bone")
            if i < len(path) - 1:
                rig.add(a.disc(f"Disc{size}{i}", path[i].lerp(path[i + 1], 0.5), t, size), bonef(i),
                        "disc")
    # Côtes saillantes, étroites et longues, quelques côtes brisées
    sternum = []
    for k, i in enumerate(range(8, 19)):
        hw = 0.45 + 0.12 * math.sin(math.pi * k / 10)
        depth = 0.9 + 0.35 * math.sin(math.pi * (k + 2) / 13)
        for s in (-1, 1):
            if k == 6 and s == 1:      # côte brisée qui pend
                rig.add(r.tube(f"BrokenRib{k}", [tuple(SPINE[i]), tuple(SPINE[i] + Vector((0.4, -0.05, -0.3))),
                                                 tuple(SPINE[i] + Vector((0.5, -0.1, -0.55)))],
                               [0.04, 0.035, 0.02], segments=4), spine_bone(i), "bone_shade")
                continue
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.3, radius=0.045),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.3, -depth)))
    rig.add(a.band("Sternum", sternum[1:-1:2], 0.06, 0.24), "Spine2", "bone_shade")
    # Cœur gelé suspendu dans la cage
    for k, (dx, h) in enumerate(((0, 0.55), (0.12, 0.35), (-0.12, 0.4))):
        rig.add(a.crystal(f"FrozenHeart{k}", (dx, -0.4, 5.35), 0.08 if k == 0 else 0.05, h, sides=6),
                "Spine2", "glow", glow=True)
    rig.add(r.tube("HeartHang", [tuple(SPINE[12] + Vector((0, -0.05, -0.1))), (0, -0.4, 5.9)], 0.02,
                   segments=4), "Spine2", "bone_shade")
    # Omoplates saillantes, clavicules, bassin étroit, givre sur les épaules
    for s in (-1, 1):
        sh = arm_points(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[16] + Vector((s * 0.2, 0.1, 0.05)),
                        sh + Vector((0, 0.06, 0.05)), 0.42, 0.06, width_end=0.2, mid=0.45,
                        normal=(0.3 * s, 0.6, 1)), "Spine3", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, sternum[-2] + Vector((s * 0.12, 0, 0)), 0.04,
                            condyles=False), "Spine3", "bone_shade")
        for k in range(3):
            rig.add(a.claw(f"ShoulderIce{s}{k}", sh + Vector((s * 0.05 * k, 0.05, 0.12)),
                           (s * 0.3, 0.2, 1), 0.22 - 0.04 * k, 0.035, curl=0, segments=4),
                    "Spine3", "ice")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.12, 0, 0)),
                        hp + Vector((s * 0.06, -0.02, 0.12)), 0.35, 0.06, width_end=0.3, mid=0.4,
                        normal=(s, 0, 0.3)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.2, 0.1, 4.1), (0, 0.15, 4.05)], 0.05,
                       segments=5), "Spine1", "bone")


def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd = arm_points(s)
        ua, fa, hb = f"UpperArm_{side}", f"ForeArm_{side}", f"Hand_{side}"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.08, segments=6), ua, "bone", **ARMS)
        off = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.06
        rig.add(a.long_bone(f"Radius{s}", el + off, wr + off, 0.05, condyles=False, segments=5), fa,
                "bone", **ARMS)
        rig.add(a.long_bone(f"Ulna{s}", el - off, wr - off, 0.045, condyles=False, segments=5), fa,
                "bone_shade", **ARMS)
        rig.add(a.claw(f"Elbow{s}", el, (0, 1, 0.2), 0.22, 0.05, curl=0, segments=4), fa, "horn",
                **ARMS)
        rig.add(r.ico(f"Wrist{s}", 0.08, subdivisions=1, location=wr), hb, "bone_shade", **ARMS)
        # Doigts interminables à 3 phalanges, griffes noires crochues
        lat = Vector((s, 0, 0))
        for j in range(4):
            off_j = (j - 1.5) * 0.1
            base = hd + lat * off_j
            rig.add(a.long_bone(f"Metacarpal{s}{j}", wr + lat * off_j * 0.4, base, 0.035,
                                condyles=False, segments=5), hb, "bone", **ARMS)
            p1 = base + Vector((lat.x * off_j * 0.3, -0.25, -0.35))
            p2 = p1 + Vector((0, -0.15, -0.35))
            p3 = p2 + Vector((0, 0.05, -0.28))
            for k, (q0, q1) in enumerate(((base, p1), (p1, p2), (p2, p3))):
                rig.add(a.long_bone(f"Phalanx{s}{j}{k}", q0, q1, 0.03 - 0.004 * k, condyles=False,
                                    segments=5), hb, "bone", **ARMS)
                rig.add(r.ico(f"Knuckle{s}{j}{k}", 0.04, subdivisions=1, location=q0), hb,
                        "bone_shade", **ARMS)
            rig.add(a.claw(f"HandClaw{s}{j}", p3, (0, -0.3, -1), 0.3, 0.04, curl=0.55, segments=5),
                    hb, "horn", **ARMS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, hk, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.1, segments=6), th, "bone", **LEGS)
        rig.add(r.ico(f"Patella{s}", 0.07, subdivisions=1, location=kn + Vector((0, -0.1, 0.02))),
                th, "bone_shade", **LEGS)
        rig.add(a.long_bone(f"Tibia{s}", kn, hk, 0.08, segments=6), sn, "bone", **LEGS)
        rig.add(a.claw(f"Calcaneus{s}", hk, (0, 1, 0.4), 0.25, 0.06, curl=0, segments=5), fo,
                "bone_shade", **LEGS)
        rig.add(a.long_bone(f"Cannon{s}", hk, ft, 0.065, segments=6), fo, "bone", **LEGS)
        rig.add(a.ring_around(f"AnkleFrost{s}", ft, ft - hk, 0.1, 0.03, segments=8), fo, "glow",
                glow=True)
        for k, dx in enumerate((-0.08, 0.08)):
            pastern = ft + Vector((dx * 1.3, -0.18, -0.12))
            rig.add(a.long_bone(f"Pastern{s}{k}", ft, pastern, 0.04, condyles=False, segments=5), fo,
                    "bone", **LEGS)
            rig.add(a.claw(f"Hoof{s}{k}", pastern + Vector((0, 0.06, 0.02)), (dx * 0.5, -1, -0.6),
                           0.24, 0.08, curl=0.1, segments=5), fo, "horn", **LEGS)
        for k in range(2):
            rig.add(a.claw(f"ShinIcicle{s}{k}", kn.lerp(hk, 0.3 + 0.3 * k) + Vector((0, 0.08, 0)),
                           (0, 0.2, -1), 0.2, 0.03, curl=0, segments=4), sn, "ice", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_arms(rig)
    build_legs(rig)
    return rig
