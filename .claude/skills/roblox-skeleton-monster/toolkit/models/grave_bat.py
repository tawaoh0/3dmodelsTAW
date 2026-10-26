"""Chauve-souris vampire squelette (≈ 4 studs de haut, 6 de long) — animable.
Pack « Cimetière gothique / nécromancie », créature 4.

Animal modèle : le **vampire commun** (Desmodus) — boîte crânienne ronde à crête sagittale,
museau très court à feuille nasale, **incisives en lames de rasoir** et canines énormes,
oreilles immenses ; il **marche à quatre pattes** sur les poignets et les pieds, ailes repliées.

Identité : os ivoire rosé, ombres pourpres ; **aucune corne** : oreilles géantes à armature
d'os ; rampe ailes repliées en **cape** gothique ; collier de fer à camée rouge, chaînes
brisées aux poignets, gouttes de sang aux crocs ; thème d'effets « vampire ».

Pièces Roblox : corps, Head, Wings, + lumineux.
Os : Root, Hips, Chest, Neck, Head, Jaw, Tail, Arm_{L,R}_1-2, Thumb_{L,R}, Finger1-4_{L,R},
Thigh/Shin/Foot_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.grave_lich_dragon import chain

COLORS = {
    "bone": "#d6c4bd",
    "bone_shade": "#5e2433",
    "tooth": "#fbf6ea",
    "horn": "#1a0f14",
    "disc": "#3a1520",
    "membrane": "#4b1b2a",
    "iron": "#3f3b42",
    "gum": "#7a1428",
    "ink": "#0a0406",
    "glow": "#ff3b6b",
    "glow_hot": "#ffd8e2",
}

EFFECT_THEME = "vampire"

TEST_POSE = {
    "Jaw": (-15, 0, 0),
    "Arm_L_1": (0, -40, 30),
    "Arm_L_2": (0, -30, 0),
    "Head": (-15, 0, 10),
    "Thigh_R": (20, 0, 0),
}

VIEW = (1.0, -0.9, 0.45)

SPINE = a.smooth_path([(0, 0.85, 2.15), (0, 0.1, 2.45), (0, -0.6, 2.6)], 9)
NECK = a.smooth_path([(0, -0.6, 2.65), (0, -0.85, 2.8), (0, -1.0, 2.95)], 4)
# Crâne de vampire dans son repère (occiput en 0, museau vers -Y)
SKULL = [(0.0, 0.3, 0.35, 0.25, 0.35, -0.15), (-0.25, 0.38, 0.42, 0.3, 0.42, -0.2),
         (-0.5, 0.33, 0.37, 0.28, 0.36, -0.22), (-0.72, 0.23, 0.28, 0.22, 0.2, -0.22),
         (-0.88, 0.17, 0.21, 0.17, 0.08, -0.2), (-0.98, 0.13, 0.16, 0.13, 0.0, -0.16)]
EYE = (-0.6, 0.12)
HINGE = (0.3, -0.35, -0.2)
GAPE = math.radians(28)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = Matrix.Translation(NECK[-1] + Vector((0, 0.1, 0.05))) @ Matrix.Rotation(math.radians(8), 4, "X")
HEAD = dict(part="Head")
WINGS = dict(part="Wings")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def arm(s):
    """Épaule, coude (haut, replié), poignet (au sol), pointe du pouce, bouts des 4 doigts repliés."""
    sh, el, wr = Vector((s * 0.42, -0.55, 2.5)), Vector((s * 1.15, 0.15, 3.45)), Vector((s * 0.85, -0.9, 0.35))
    thumb = Vector((s * 0.8, -1.35, 0.06))
    tips = [Vector((s * 1.3, 0.35, 3.75)), Vector((s * 1.5, 0.75, 3.05)), Vector((s * 1.45, 1.1, 2.25)),
            Vector((s * 1.2, 1.25, 1.5))]
    return sh, el, wr, thumb, tips


def leg(s):
    return (Vector((s * 0.35, 0.8, 2.05)), Vector((s * 0.85, 1.25, 1.35)), Vector((s * 0.75, 0.95, 0.15)))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[4], "Root")
    rig.bone("Chest", SPINE[4], SPINE[-1], "Hips")
    rig.bone("Neck", NECK[0], NECK[-1], "Chest")
    rig.bone("Head", NECK[-1], HEAD_M @ Vector((0, -1.0, 0.0)), "Neck")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE), HEAD_M @ (_jm @ Vector((0, -0.95, -0.25))), "Head")
    rig.bone("Tail", SPINE[0], SPINE[0] + Vector((0, 0.5, -0.2)), "Hips")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, thumb, tips = arm(s)
        rig.bone(f"Arm_{side}_1", sh, el, "Chest")
        rig.bone(f"Arm_{side}_2", el, wr, f"Arm_{side}_1")
        rig.bone(f"Thumb_{side}", wr, thumb, f"Arm_{side}_2")
        for i, tip in enumerate(tips):
            rig.bone(f"Finger{i + 1}_{side}", wr, tip, f"Arm_{side}_2")
        hp, kn, an = leg(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Hips")
        rig.bone(f"Shin_{side}", kn, an, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", an, an + Vector((0, 0.35, -0.1)), f"Shin_{side}")
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.3, EYE[0], EYE[1])), "Head")
        rig.fx(f"Fang{side}", HEAD_M @ Vector((s * 0.05, -1.0, -0.45)), "Head")
    rig.fx("Heart", (0, -0.1, 1.95), "Chest")
    rig.fx("Collar", NECK[1] + Vector((0, -0.25, -0.2)), "Neck")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.0, tip_length=0.08)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.12, 0.11),
                  a.hole_x((0, -0.18, 0.05), 0.14, 0.12),                        # fosse temporale
                  a.hole_along((0, -0.97, -0.02), (0, 1, 0), (1, 0, 0), 0.08, 0.06, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    rig.add(a.band("SagittalCrest", [top(0, y) for y in (0.0, -0.2, -0.45)], [0.08, 0.14, 0.06], 0.05,
                   offset=0.2), H, "bone_shade", **HEAD)
    # Feuille nasale dressée sur le bout du museau
    rig.add(a.blade("NoseLeaf", (0, -0.95, 0.02), (0, -0.98, 0.3), 0.16, 0.03, width_end=0.04, mid=0.2,
                    normal=(0, -1, 0.1)), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.09, subdivisions=2, location=c0 - Vector((s * 0.06, 0, 0))), H, "glow",
                glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", c0, (s, -0.4, 0.1), 0.13, 0.035, segments=10), H,
                "bone_shade", **HEAD)
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.3, -0.7, -0.08), (s * 0.42, -0.45, -0.1),
                                         (s * 0.34, -0.25, -0.08)], [0.035, 0.045, 0.035], segments=4), H,
                "bone", **HEAD)
        # Oreilles immenses : membrane tendue sur une armature d'os (rebord + nervures)
        base, tip = Vector((s * 0.28, -0.12, 0.32)), Vector((s * 0.65, 0.12, 1.15))
        rig.add(a.blade(f"Ear{s}", base, tip, 0.25, 0.03, width_end=0.04, mid=0.42,
                        normal=(0.2 * s, -1, 0.15), bevel=0), H, "membrane", **HEAD)
        mid = base.lerp(tip, 0.45)
        rig.add(r.tube(f"EarRimF{s}", [tuple(base + Vector((-s * 0.12, -0.03, 0))),
                                       tuple(mid + Vector((-s * 0.2, -0.03, 0.05))), tuple(tip)],
                       [0.035, 0.03, 0.015], segments=4), H, "bone", **HEAD)
        rig.add(r.tube(f"EarRimB{s}", [tuple(base + Vector((s * 0.12, 0.03, -0.05))),
                                       tuple(mid + Vector((s * 0.2, 0.03, -0.05))), tuple(tip)],
                       [0.035, 0.03, 0.015], segments=4), H, "bone", **HEAD)
        for k in range(2):
            p = base.lerp(tip, 0.35 + 0.25 * k)
            rig.add(r.tube(f"EarRib{s}{k}", [tuple(p + Vector((-s * 0.12, -0.03, 0))),
                                             tuple(p + Vector((s * 0.12, 0.03, -0.02)))], 0.018,
                           segments=4), H, "bone_shade", **HEAD)
        rig.add(a.blade(f"Tragus{s}", base + Vector((-s * 0.02, -0.06, 0)),
                        base + Vector((s * 0.03, -0.1, 0.3)), 0.07, 0.025, width_end=0.02,
                        normal=(0, -1, 0)), H, "bone_shade", **HEAD)
        # Incisives en lames de rasoir + canines énormes, gouttes de sang
        inc = Vector((s * 0.05, -0.96, -0.16))
        rig.add(mr.tooth(f"Incisor{s}", inc, inc + Vector((0, -0.04, -0.32)), 0.12, 0.06,
                         Vector((0, -1, 0)), curl=0.08), H, "tooth", **HEAD)
        rig.add(r.ico(f"BloodDrop{s}", 0.03, subdivisions=1, location=inc + Vector((0, -0.04, -0.34)),
                      scale=(1, 1, 1.6)), H, "glow", glow=True)
        can = Vector((s * 0.14, -0.86, -0.18))
        rig.add(mr.tooth(f"Canine{s}", can, can + Vector((s * 0.02, -0.03, -0.36)), 0.12, 0.1,
                         Vector((s, -0.3, 0)), curl=0.12), H, "tooth", **HEAD)
        for k in range(2):
            y = -0.7 + 0.12 * k
            xx = s * a.side_width(SKULL, y, -0.2) * 0.85
            rig.add(mr.tooth(f"Cheek{s}{k}", (xx, y, -0.2), (xx, y, -0.3), 0.09, 0.07, Vector((s, 0, 0)),
                             curl=0.0), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * 0.22, -0.6, -0.19), (s * 0.16, -0.85, -0.18),
                                        (s * 0.06, -0.95, -0.16)], 0.03, segments=4), H, "gum", **HEAD)
    # Mandibule courte et haute, coronoïde, canines du bas
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.24, -0.6, -0.22)),
                Vector((s * 0.15, -0.82, -0.24)), Vector((s * 0.05, -0.95, -0.25))]
        rig.add(a.band(f"Mandible{s}", line, [0.2, 0.17, 0.15, 0.13], [0.07, 0.07, 0.06, 0.06],
                       offset=1), J, "bone", **HEAD)
        rig.add(a.claw(f"Coronoid{s}", line[0] + Vector((0, -0.08, -0.02)), (0, -0.2, 1), 0.2, 0.05,
                       curl=0.2, segments=4), J, "bone_shade", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.06, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
        p = line[2] + Vector((-s * 0.03, 0, 0))
        rig.add(mr.tooth(f"LowCanine{s}", p, p + Vector((s * 0.02, 0, 0.26)), 0.1, 0.08, Vector((s, 0, 0)),
                         curl=0.12), J, "tooth", **HEAD)
        p = line[1] + Vector((-s * 0.03, 0, 0))
        rig.add(mr.tooth(f"LowCheek{s}", p, p + Vector((0, 0, 0.12)), 0.08, 0.06, Vector((s, 0, 0)),
                         curl=0.0), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(q + Vector((-s * 0.03, 0, 0.01))) for q in line[1:]], 0.03,
                       segments=4), J, "gum", **HEAD)
    rig.add(r.ico("Chin", 0.08, subdivisions=2, location=(0, -0.93, -0.33), scale=(1.4, 1, 0.9)), J,
            "bone", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Throat", 0.1, subdivisions=2, location=(0, -0.5, -0.25), scale=(1.3, 2, 0.6)), H, "glow",
            glow=True)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for path, bones, size in ((SPINE, ("Hips", "Chest"), 0.2), (NECK, ("Neck", "Neck"), 0.18)):
        n = len(path)
        for i in range(n):
            t = tangent(path, i)
            bone = bones[0] if i < n // 2 else bones[1]
            rig.add(a.vertebra(f"Vert{bones[0]}{i}", path[i], t, size, spine=0.9, lean=0.4), bone, "bone")
            if i < n - 1:
                rig.add(a.disc(f"Disc{bones[0]}{i}", path[i].lerp(path[i + 1], 0.5), t, size), bone, "disc")
    keel = []
    for k, i in enumerate(range(2, 8)):
        depth = 0.5 + 0.25 * math.sin(math.pi * k / 5)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], 0.45, depth, s, sweep=-0.15, radius=0.045), "Chest", "bone")
        keel.append(SPINE[i] + Vector((0, -0.1, -depth)))
    rig.add(a.band("Keel", keel[1:], [0.08, 0.14, 0.18, 0.14, 0.08], 0.05, up=(0, 0, -1), offset=0),
            "Chest", "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.38), (0.1, 0.26), (-0.1, 0.28))):
        rig.add(a.crystal(f"BloodHeart{k}", (dx, -0.1, 1.95), 0.08 if k == 0 else 0.06, h, sides=4), "Chest",
                "glow", glow=True)
    for s in (-1, 1):
        sh = arm(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[4] + Vector((s * 0.2, 0, 0.12)), sh, 0.3, 0.05, width_end=0.15,
                        normal=(s, 0, 1)), "Chest", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, keel[-1] + Vector((s * 0.1, -0.1, 0.25)), 0.045,
                            condyles=False, segments=5), "Chest", "bone_shade")
        hp = leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[3] + Vector((s * 0.12, 0, 0)), hp, 0.22, 0.05, width_end=0.15,
                        normal=(s, 0, 1)), "Hips", "bone")
    # Petite queue
    tail = [SPINE[0] + Vector((0, 0.15 * k, -0.06 * k)) for k in range(5)]
    for k, p in enumerate(tail[1:]):
        rig.add(a.vertebra(f"TailVert{k}", p, (0, 1, -0.4), 0.09 - 0.012 * k, spine=0.5), "Tail", "bone")
    # Collier de fer clouté à camée rouge
    cc = NECK[1]
    rig.add(a.ring_around("Collar", cc, tangent(NECK, 1), 0.3, 0.06, segments=12), "Neck", "iron")
    t = tangent(NECK, 1)
    side, up = a._basis(t)
    for k in range(6):
        ang = 2 * math.pi * k / 6
        d = side * math.cos(ang) + up * math.sin(ang)
        rig.add(a.claw(f"CollarStud{k}", cc + d * 0.33, d, 0.14, 0.035, curl=0, segments=4), "Neck", "iron")
    rig.add(a.crystal("Cameo", cc - up * 0.36 + Vector((0, -0.05, 0)), 0.08, 0.2, sides=6), "Neck", "glow",
            glow=True)


def build_wings(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, thumb, tips = arm(s)
        a1, a2, th = f"Arm_{side}_1", f"Arm_{side}_2", f"Thumb_{side}"
        fingers = [f"Finger{i + 1}_{side}" for i in range(4)]
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.09, segments=6), a1, "bone", **WINGS)
        rig.add(a.long_bone(f"Radius{s}", el, wr + Vector((0, 0, 0.08)), 0.075, segments=6), a2, "bone",
                **WINGS)
        rig.add(r.ico(f"Wrist{s}", 0.11, subdivisions=1, location=wr + Vector((0, 0, 0.08))), a2, "bone_shade",
                **WINGS)
        rig.add(a.long_bone(f"ThumbBone{s}", wr, thumb + Vector((0, 0, 0.06)), 0.045, condyles=False,
                            segments=5), th, "bone", **WINGS)
        rig.add(a.claw(f"ThumbClaw{s}", thumb + Vector((0, 0, 0.06)), (0, -1, -0.6), 0.2, 0.045, curl=0.5,
                       segments=4), th, "horn", **WINGS)
        rig.add(a.claw(f"ElbowSpike{s}", el, (s * 0.3, 0.2, 1), 0.3, 0.05, curl=0.1, segments=4), a1, "horn",
                **WINGS)
        for i, (tip, bone) in enumerate(zip(tips, fingers)):
            knuckle = wr.lerp(tip, 0.5) + Vector((s * 0.06, 0, 0))
            rig.add(a.long_bone(f"FingerA{s}{i}", wr, knuckle, 0.04, condyles=False, segments=5), bone, "bone",
                    **WINGS)
            rig.add(a.long_bone(f"FingerB{s}{i}", knuckle, tip, 0.03, condyles=False, segments=4), bone,
                    "bone", **WINGS)
            rig.add(a.claw(f"FingerTip{s}{i}", tip, tip - wr, 0.15, 0.025, curl=0.2, segments=4), bone, "horn",
                    **WINGS)
        # Chaîne brisée au poignet
        rig.add(a.ring_around(f"Shackle{s}", wr.lerp(el, 0.12), el - wr, 0.1, 0.03, segments=8), a2, "iron",
                **WINGS)
        chain(rig, f"WristChain{s}", wr.lerp(el, 0.12) + Vector((s * 0.1, 0, -0.05)),
              wr + Vector((s * 0.4, 0.15, -0.28)), a2, sag=0.05, radius=0.05, **WINGS)
        # Membranes repliées en cape : panneaux entre les doigts, bord déchiré
        W = {a2: 1.0}
        for i in range(3):
            edge = a.tattered_edge(tips[i], tips[i + 1], {fingers[i]: 1}, {fingers[i + 1]: 1}, wr, depth=0.25,
                                   notches=3, seed=5 * s + i)
            m = a.membrane(f"Membrane{s}{i}", [(tuple(wr), W), (tuple(tips[i]), {fingers[i]: 1})]
                           + [(tuple(p), w) for p, w in edge] + [(tuple(tips[i + 1]), {fingers[i + 1]: 1})])
            rig.pal.paint(m, "membrane")
            m["part"] = "Wings"
        hp, kn, an = leg(s)
        edge = a.tattered_edge(tips[3], an + Vector((0, 0, 0.2)), {fingers[3]: 1}, {f"Shin_{side}": 1},
                               wr.lerp(hp, 0.5), depth=0.3, notches=4, seed=9 * s)
        m = a.membrane(f"MembraneBody{s}", [(tuple(wr), W), (tuple(tips[3]), {fingers[3]: 1})]
                       + [(tuple(p), w) for p, w in edge]
                       + [(tuple(an + Vector((0, 0, 0.2))), {f"Shin_{side}": 1}), (tuple(kn), {f"Thigh_{side}": 1}),
                          (tuple(hp), {"Hips": 1}), (tuple(sh + Vector((0, 0.3, -0.2))), {"Chest": 1})])
        rig.pal.paint(m, "membrane")
        m["part"] = "Wings"


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an = leg(s)
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.07, segments=6), f"Thigh_{side}", "bone")
        rig.add(a.long_bone(f"Tibia{s}", kn, an + Vector((0, 0, 0.06)), 0.06, segments=6), f"Shin_{side}", "bone")
        rig.add(a.claw(f"Calcar{s}", an + Vector((0, 0, 0.08)), (s * 0.3, 1, 0.2), 0.35, 0.03, curl=0.1,
                       segments=4), f"Shin_{side}", "bone_shade")
        for k in range(5):
            d = Vector((s * (k - 2) * 0.12, -1, 0)).normalized()
            toe = an + d * 0.22 + Vector((0, 0, -0.06))
            rig.add(a.long_bone(f"Toe{s}{k}", an + Vector((0, 0, 0.04)), toe, 0.03, condyles=False, segments=4),
                    f"Foot_{side}", "bone")
            rig.add(a.claw(f"Claw{s}{k}", toe, d + Vector((0, 0, -0.8)), 0.13, 0.03, curl=0.5, segments=4),
                    f"Foot_{side}", "horn")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_wings(rig)
    build_legs(rig)
    return rig
