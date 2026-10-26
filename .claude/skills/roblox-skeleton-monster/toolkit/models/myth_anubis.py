"""Anubis squelette (≈ 8 studs de haut, bipède élancé) — créature animable.
Pack « Mythologie », créature 3 (mythe égyptien).

Animal modèle : le **chacal doré** — crâne fin et allongé, museau étroit, grandes orbites,
canines fines, oreilles immenses dressées ; sur un corps humain élancé aux jambes de chacal.
Très différent du Minotaure (voûté, en jupe de cuir) : droit, hiératique, carrure de dieu
guerrier (épaules très larges, épaulières or et lapis).

Identité : **os noirs d'obsidienne** cerclés d'or ; **aucune corne** : oreilles géantes de
lapis-lazuli bordées d'or, diadème à **uraeus** (cobra dressé) ; collier ousekh de perles
or / lapis / turquoise, pagne plissé à tablier d'hiéroglyphes lumineux, bracelets ; **sceptre
ouas** tenu à pleine main et planté au sol, **ankh** pendue à l'autre main ; thème d'effets
« duat » (sable doré + esprits bleus).

Pièces Roblox : corps, Head, Arms, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, UpperArm/ForeArm/Hand_{L,R}, Thigh/Shin/Foot_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#2f2b30",
    "bone_shade": "#121014",
    "tooth": "#f3ead2",
    "horn": "#0a090b",
    "disc": "#1a181c",
    "gold": "#e0b03c",
    "lapis": "#2448b0",
    "turquoise": "#2fb8a8",
    "linen": "#e6dcc2",
    "gum": "#4a1a20",
    "ink": "#050405",
    "glow": "#45d8ff",
    "glow_hot": "#e4f9ff",
}

EFFECT_THEME = "duat"

TEST_POSE = {
    "Jaw": (-12, 0, 0),
    "Head": (0, 0, 20),
    "UpperArm_R": (-40, 0, 0),
    "ForeArm_R": (-50, 0, 0),
    "Thigh_L": (25, 0, 0),
}

VIEW = (1.0, -1.0, 0.25)

SPINE = a.smooth_path([(0, 0.15, 4.0), (0, 0.12, 4.9), (0, 0.02, 5.8), (0, -0.08, 6.5)], 16)
NECK = a.smooth_path([(0, -0.08, 6.5), (0, -0.22, 7.0), (0, -0.3, 7.4)], 8)
# Crâne de chacal dans son repère (occiput en 0, museau vers -Y)
SKULL = [(0.0, 0.26, 0.3, 0.22, 0.3, -0.2), (-0.3, 0.33, 0.38, 0.27, 0.35, -0.25),
         (-0.6, 0.27, 0.34, 0.25, 0.28, -0.28), (-1.0, 0.17, 0.23, 0.19, 0.14, -0.27),
         (-1.5, 0.12, 0.16, 0.14, 0.05, -0.24), (-1.85, 0.1, 0.13, 0.11, 0.0, -0.2)]
EYE = (-0.62, 0.12)
HINGE = (0.28, -0.25, -0.22)
GAPE = math.radians(14)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = Matrix.Translation(NECK[-1] + Vector((0, 0.15, 0.15)))
GRIP = Vector((1.75, -0.55, 4.55))
STAFF_TOP, STAFF_BOTTOM = GRIP + Vector((0, 0, 3.6)), Vector((1.75, -0.55, 0.0))
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def arm_points(s):
    if s > 0:   # bras gauche : main serrée sur le sceptre ouas
        return (Vector((1.15, -0.05, 6.35)), Vector((1.55, 0.12, 5.15)), Vector((1.75, -0.3, 4.62)),
                Vector((1.75, -0.45, 4.58)))
    return (Vector((-1.15, -0.05, 6.35)), Vector((-1.45, 0.15, 5.05)), Vector((-1.45, -0.35, 3.95)),
            Vector((-1.45, -0.45, 3.6)))


def leg_points(s):
    return (Vector((s * 0.55, 0.15, 3.95)), Vector((s * 0.68, -0.35, 2.3)), Vector((s * 0.68, 0.4, 0.9)),
            Vector((s * 0.72, 0.0, 0.15)))


def beads(rig, name, center, radius, start, end, n, bone, colors, size=0.06, dz=0.0, **kw):
    """Arc de perles alternées (collier ousekh, bracelets) devant `center`."""
    for k in range(n):
        ang = math.radians(start + (end - start) * k / max(1, n - 1))
        p = Vector(center) + Vector((radius * math.sin(ang), -radius * math.cos(ang) * 0.85,
                                     dz - 0.12 * (1 - math.cos(ang))))
        rig.add(r.ico(f"{name}{k}", size, subdivisions=1, location=p, scale=(1, 1, 1.3)), bone,
                colors[k % len(colors)], **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], HEAD_M @ Vector((0, -1.85, 0.0)), "Neck")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE), HEAD_M @ (_jm @ Vector((0, -1.8, -0.25))), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd = arm_points(s)
        rig.bone(f"UpperArm_{side}", sh, el, "Spine3")
        rig.bone(f"ForeArm_{side}", el, wr, f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", wr, hd, f"ForeArm_{side}")
        hp, kn, an, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Spine1")
        rig.bone(f"Shin_{side}", kn, an, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", an, ft, f"Shin_{side}")
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.25, EYE[0], EYE[1])), "Head")
    rig.fx("Uraeus", HEAD_M @ Vector((0, -0.75, 0.55)), "Head")
    rig.fx("Heart", (0, -0.2, 5.3), "Spine2")
    rig.fx("Was", STAFF_TOP, "Hand_L")
    rig.fx("Ankh", arm_points(-1)[3] + Vector((0, 0, -0.55)), "Hand_R")


# ---------------------------------------------------------------- tête de chacal

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.0, tip_length=0.1)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.12, 0.11),
                  a.hole_x((0, -0.2, 0.0), 0.16, 0.13),
                  a.hole_x((0, -1.15, -0.08), 0.24, 0.05),
                  a.hole_x((0, -1.55, 0.0), 0.13, 0.035),
                  a.hole_along((0, -0.3, 0.33), (0, 0, 1), (1, 0, 0), 0.07, 0.12, depth=0.3),
                  a.hole_along((0, -1.85, -0.08), (0, 1, 0), (1, 0, 0), 0.06, 0.08, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    rig.add(r.tube("Nasal", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in (-0.75, -1.2, -1.6, -1.8)],
                   [0.035, 0.035, 0.03, 0.02], segments=4), H, "gold", **HEAD)
    rig.add(a.band("Crest", [top(0, y) for y in (-0.05, -0.25, -0.5)], [0.06, 0.12, 0.05], 0.04, offset=0.2), H,
            "bone_shade", **HEAD)
    # Diadème d'or + uraeus (cobra dressé sur le front)
    band = [tuple(top(0.3 * math.cos(math.pi * k / 8), -0.4 - 0.12 * math.sin(math.pi * k / 8)) + Vector((0, 0, 0.02)))
            for k in range(9)]
    rig.add(r.tube("Diadem", band, 0.04, segments=4), H, "gold", **HEAD)
    base = top(0, -0.55) + Vector((0, 0, 0.02))
    body = a.smooth_path([base, base + Vector((0, -0.12, 0.1)), base + Vector((0, -0.05, 0.25)),
                          base + Vector((0, -0.15, 0.4))], 8)
    rig.add(r.tube("UraeusBody", [tuple(p) for p in body], [0.05, 0.05, 0.045, 0.04, 0.04, 0.035, 0.03, 0.03],
                   segments=5), H, "gold", **HEAD)
    rig.add(a.blade("UraeusHood", body[-3] + Vector((0, 0.02, -0.08)), body[-1] + Vector((0, 0.02, 0.06)), 0.12, 0.025,
                    width_end=0.06, mid=0.2, normal=(0, -1, 0.2)), H, "lapis", **HEAD)
    rig.add(r.ico("UraeusHead", 0.05, subdivisions=1, location=body[-1] + Vector((0, -0.05, 0.03)),
                  scale=(1, 1.5, 0.7)), H, "gold", **HEAD)
    for s in (-1, 1):
        rig.add(r.ico(f"UraeusEye{s}", 0.015, subdivisions=1, location=body[-1] + Vector((s * 0.03, -0.1, 0.05))),
                H, "glow", glow=True)
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.085, subdivisions=2, location=c0 - Vector((s * 0.05, 0, 0))), H, "glow",
                glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", c0, (s, -0.4, 0.15), 0.13, 0.03, segments=10), H, "gold", **HEAD)
        # Trait de khôl d'or qui prolonge l'œil vers l'arrière
        rig.add(r.tube(f"Kohl{s}", [tuple(c0 + Vector((s * 0.02, 0.12, -0.02))), tuple(c0 + Vector((s * 0.05, 0.35, -0.06)))],
                       0.02, segments=4), H, "gold", **HEAD)
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.22, -0.9, -0.08), (s * 0.36, -0.55, -0.1), (s * 0.3, -0.2, -0.07)],
                       [0.03, 0.04, 0.03], segments=4), H, "bone", **HEAD)
        # Oreilles immenses dressées : membrane de lapis, armature et liseré d'or
        eb, et = Vector((s * 0.2, -0.12, 0.3)), Vector((s * 0.34, 0.12, 1.3))
        rig.add(a.blade(f"Ear{s}", eb, et, 0.3, 0.03, width_end=0.03, mid=0.34, normal=(s * 0.15, -1, 0.1), bevel=0),
                H, "lapis", **HEAD)
        mid = eb.lerp(et, 0.45)
        for k, sx in enumerate((-1, 1)):
            rig.add(r.tube(f"EarRim{s}{k}", [tuple(eb + Vector((sx * 0.14, sx * 0.02, 0))),
                                             tuple(mid + Vector((sx * 0.17, sx * 0.03, 0))), tuple(et)],
                           [0.03, 0.025, 0.012], segments=4), H, "gold", **HEAD)
        rig.add(r.tube(f"EarRib{s}", [tuple(eb.lerp(et, 0.1) + Vector((0, -0.02, 0))), tuple(eb.lerp(et, 0.8) + Vector((0, -0.02, 0)))],
                       0.018, segments=4), H, "bone", **HEAD)
        # Dents : canines fines, prémolaires
        can = Vector((s * 0.1, -1.68, -0.2))
        rig.add(mr.tooth(f"Canine{s}", can, can + Vector((0, -0.02, -0.26)), 0.09, 0.07, Vector((s, -0.3, 0)), curl=0.12),
                H, "tooth", **HEAD)
        for k in range(4):
            y = -1.45 + 0.2 * k
            xx = s * a.side_width(SKULL, y, -0.22) * 0.85
            size = 0.15 if k == 2 else 0.09
            rig.add(mr.tooth(f"UpTooth{s}{k}", (xx, y, -0.22), (xx, y, -0.22 - size), size * 0.7, size * 0.4,
                             Vector((s, 0, 0)), curl=0.05), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * a.side_width(SKULL, y, -0.22) * 0.75, y, -0.2) for y in (-1.75, -1.2, -0.75)],
                       0.025, segments=4), H, "gum", **HEAD)
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.22, -0.8, -0.27)),
                Vector((s * 0.14, -1.4, -0.27)), Vector((s * 0.06, -1.8, -0.25))]
        rig.add(a.band(f"Mandible{s}", line, [0.24, 0.14, 0.12, 0.1], [0.06, 0.055, 0.05, 0.045], offset=1), J,
                "bone", **HEAD)
        rig.add(r.tube(f"MandibleGold{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, (0.24, 0.14, 0.12, 0.1))],
                       0.025, segments=4), J, "gold", **HEAD)
        rig.add(a.claw(f"Coronoid{s}", line[0] + Vector((0, -0.08, 0)), (0, -0.2, 1), 0.22, 0.04, curl=0.2, segments=4),
                J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.05, subdivisions=1, location=line[0]), H, "gold", **HEAD)
        can = mr.along(line, 0.85) + Vector((-s * 0.02, 0, 0))
        rig.add(mr.tooth(f"LowCanine{s}", can, can + Vector((0, -0.02, 0.22)), 0.08, 0.06, Vector((s, -0.3, 0)),
                         curl=0.12), J, "tooth", **HEAD)
        for k in range(3):
            p = mr.along(line, 0.35 + 0.15 * k) + Vector((-s * 0.02, 0, 0))
            rig.add(mr.tooth(f"LowTooth{s}{k}", p, p + Vector((0, 0, 0.1)), 0.07, 0.04, Vector((s, 0, 0)), curl=0.05),
                    J, "tooth", **HEAD)
    rig.add(r.ico("Chin", 0.06, subdivisions=2, location=(0, -1.8, -0.33), scale=(1.3, 1, 0.8)), J, "bone", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    # --- Couches de détail : arcades d'or, os nasaux cloutés, plaques de joue, coiffe némès, barbe
    for s in (-1, 1):
        rig.add(a.blade(f"GoldBrow{s}", (s * 0.12, -0.85, 0.27), (s * 0.34, -0.5, 0.3), 0.08, 0.04, width_end=0.05,
                        normal=(s * 0.2, -0.3, 1)), H, "gold", **HEAD)
        rig.add(r.tube(f"NasalBone{s}", [tuple(top(s * 0.07, y) + Vector((0, 0, 0.012))) for y in (-0.8, -1.25, -1.7)],
                       [0.028, 0.025, 0.02], segments=4), H, "bone_shade", **HEAD)
        for k in range(5):
            q = top(s * 0.12, -0.85 - 0.2 * k)
            if q is not None:
                rig.add(r.ico(f"SnoutStud{s}{k}", 0.025, subdivisions=1, location=q + Vector((0, 0, 0.01))), H, "gold",
                        **HEAD)
        cw = a.side_width(SKULL, -0.95, -0.1)
        rig.add(a.blade(f"CheekPlate{s}", (s * (cw + 0.01), -0.75, -0.1), (s * (cw - 0.04), -1.25, -0.12), 0.14, 0.03,
                        width_end=0.07, normal=(s, 0, 0.1)), H, "gold", **HEAD)
        rig.add(a.blade(f"CheekInlay{s}", (s * (cw + 0.03), -0.8, -0.1), (s * (cw - 0.02), -1.15, -0.12), 0.07, 0.02,
                        width_end=0.03, normal=(s, 0, 0.1)), H, "lapis", **HEAD)
        rig.add(r.tube(f"Maxilla{s}", [(s * a.side_width(SKULL, y, -0.15) * 1.0, y, -0.15) for y in (-0.5, -0.9, -1.35, -1.7)],
                       [0.035, 0.035, 0.03, 0.022], segments=4), H, "bone_shade", **HEAD)
        # Pans rayés de la coiffe némès : de derrière les oreilles jusqu'aux épaules
        lap = a.smooth_path([(s * 0.3, 0.02, 0.18), (s * 0.42, 0.12, -0.25), (s * 0.48, 0.05, -0.75),
                             (s * 0.46, -0.08, -1.15)], 9)
        for k in range(8):
            rig.add(a.blade(f"Nemes{s}{k}", lap[k], lap[k + 1], 0.34 + 0.03 * k, 0.04, width_end=0.36 + 0.03 * k,
                            normal=(s, 0.1, 0.1), bevel=0), H, "gold" if k % 2 == 0 else "lapis", **HEAD)
        rig.add(r.tube(f"NemesHem{s}", [tuple(p + Vector((0, -0.17 - 0.015 * i, 0))) for i, p in enumerate(lap)], 0.022,
                       segments=4), H, "gold", **HEAD)
    for k in range(5):    # rabat arrière de la coiffe
        z0 = 0.15 - 0.22 * k
        rig.add(a.blade(f"NemesBack{k}", (0, 0.15 + 0.04 * k, z0), (0, 0.19 + 0.04 * k, z0 - 0.22), 0.55 + 0.05 * k, 0.04,
                        width_end=0.6 + 0.05 * k, normal=(0, 1, 0.15), bevel=0), H, "gold" if k % 2 == 0 else "lapis", **HEAD)
    rig.add(r.tube("NemesBand", [(-0.33, -0.05, 0.12), (-0.2, -0.32, 0.36), (0.2, -0.32, 0.36), (0.33, -0.05, 0.12)], 0.035,
                   segments=4), H, "lapis", **HEAD)
    # Barbe postiche tressée (or / lapis) sous le menton, portée par la mâchoire
    beard = [_jm @ Vector((0, -1.7, -0.32 - 0.07 * k)) + Vector((0, 0.02 * k, 0)) for k in range(7)]
    rig.add(r.tube("Beard", [tuple(p) for p in beard], [0.06, 0.065, 0.065, 0.065, 0.065, 0.06, 0.07], segments=6), J,
            "lapis", **HEAD)
    for k in range(1, 6):
        rig.add(a.ring_around(f"BeardBand{k}", beard[k], beard[k] - beard[k - 1], 0.07, 0.02, segments=8), J, "gold",
                **HEAD)
    rig.add(a.blade("BeardTip", beard[-1], beard[-1] + (beard[-1] - beard[-2]) * 1.2, 0.14, 0.04, width_end=0.18,
                    normal=(0, -1, 0)), J, "gold", **HEAD)
    rig.add(r.ico("Throat", 0.08, subdivisions=2, location=(0, -0.8, -0.25), scale=(1.2, 3, 0.6)), H, "glow", glow=True)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.27, spine=1.1, lean=0.4), spine_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.27), spine_bone(i), "disc")
    for i in range(len(NECK)):
        rig.add(a.vertebra(f"NeckVert{i}", NECK[i], tangent(NECK, i), 0.22, spine=0.9), "Neck", "bone")
        if i < len(NECK) - 1:
            rig.add(a.disc(f"NeckDisc{i}", NECK[i].lerp(NECK[i + 1], 0.5), tangent(NECK, i), 0.22), "Neck", "disc")
    sternum = []
    for k, i in enumerate(range(7, 15)):
        hw = 0.72 + 0.2 * math.sin(math.pi * (k + 3) / 10)
        depth = 0.7 + 0.2 * math.sin(math.pi * (k + 1) / 9)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.3, radius=0.07), spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.3, -depth)))
    rig.add(r.tube("Sternum", [tuple(p) for p in sternum[2::2]], 0.06, segments=6), "Spine3", "gold")
    for k, (dx, h) in enumerate(((0, 0.5), (0.12, 0.35), (-0.12, 0.38))):
        rig.add(a.crystal(f"SoulHeart{k}", (dx, -0.2, 5.3), 0.09 if k == 0 else 0.06, h, sides=4), "Spine2", "glow",
                glow=True)
    for s in (-1, 1):
        sh = arm_points(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[13] + Vector((s * 0.25, 0.2, 0)), sh + Vector((0, 0.1, 0)), 0.4, 0.05,
                        width_end=0.2, normal=(0.3 * s, 1, 0.2)), "Spine3", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, sternum[-1] + Vector((s * 0.12, 0, 0.05)), 0.07, condyles=False), "Spine3",
                "gold")
        # Épaulière à plaques superposées or / lapis
        for k in range(3):
            c0 = sh + Vector((s * (0.1 + 0.1 * k), 0, 0.3 - 0.16 * k))
            rig.add(a.band(f"Pauldron{s}{k}", [c0 + Vector((0, -0.4, -0.1)), c0 + Vector((s * 0.05, 0, 0.04)),
                                              c0 + Vector((0, 0.4, -0.1))], [0.3, 0.32, 0.3], 0.05,
                           up=(s, 0, -0.6), offset=0.5), "Spine3", "gold" if k % 2 == 0 else "lapis")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.12, 0, 0.05)), hp + Vector((s * 0.15, 0, 0.45)), 0.4, 0.06,
                        width_end=0.32, mid=0.45, normal=(s, -0.2, 0.2)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.2, -0.05, 3.7), (0, -0.05, 3.65)], 0.05, segments=5), "Spine1",
                "bone")
    # Collier ousekh : rangs de perles or / lapis / turquoise + liseré d'or
    cc = Vector((0, -0.12, 6.5))
    for k in range(4):
        beads(rig, f"Usekh{k}", cc, 0.5 + 0.13 * k, -105, 105, 9 + 2 * k, "Spine3",
              (("gold", "lapis", "turquoise", "lapis"))[k:] + ("gold",) * k, size=0.05, dz=-0.04 * k)
    rim = []
    for k in range(13):
        ang = math.radians(-110 + 220 * k / 12)
        rim.append((0.5 + 0.13 * 4) * Vector((math.sin(ang), -math.cos(ang) * 0.85, 0)) + cc
                   + Vector((0, 0, -0.16 - 0.12 * (1 - math.cos(ang)))))
    rig.add(r.tube("UsekhRim", [tuple(p) for p in rim], 0.03, segments=4), "Spine3", "gold")
    # Pagne (shendyt) : ceinture d'or, plis de lin, tablier triangulaire à hiéroglyphes lumineux
    belt_c = Vector((0, 0.05, 3.95))
    rx, ry = 0.78, 0.58
    pts = [belt_c + Vector((rx * math.sin(math.radians(d)), -ry * math.cos(math.radians(d)), 0)) for d in range(-170, 171, 20)]
    rig.add(a.band("Belt", pts, 0.2, 0.05, up=(0, 0, 1), offset=0.5), "Spine1", "gold")
    for k, d in enumerate(range(-160, 161, 16)):
        if abs(d) < 25:
            continue
        ang = math.radians(d)
        out = Vector((math.sin(ang), -math.cos(ang), 0))
        p0 = belt_c + Vector((rx * out.x, ry * out.y, -0.1))
        rig.add(a.blade(f"Pleat{k}", p0, p0 + out * 0.2 + Vector((0, 0, -1.0)), 0.16, 0.025, width_end=0.2, normal=out,
                        bevel=0), "Spine1", "linen")
    front = belt_c + Vector((0, -ry - 0.04, -0.1))
    rig.add(a.blade("Apron", front, front + Vector((0, -0.12, -1.1)), 0.45, 0.04, width_end=0.12, normal=(0, -1, 0)),
            "Spine1", "gold")
    for k in range(4):
        rig.add(r.box(f"ApronStripe{k}", (0.36 - 0.06 * k, 0.02, 0.04),
                      location=front + Vector((0, -0.04 - 0.012 * k, -0.15 - 0.22 * k))), "Spine1", "lapis")
        g = r.box(f"Hieroglyph{k}", (0.06, 0.02, 0.09), location=front + Vector((0.08 * (k % 2 * 2 - 1) * (k < 2), -0.06 - 0.012 * k,
                                                                                   -0.26 - 0.22 * k)))
        rig.add(g, "Spine1", "glow", glow=True)


def grip_hand(rig, grip, axis, wrist, bone, rr=0.12, **kw):
    """Poing fermé : 4 doigts en phalanges enroulés autour de l'axe + pouce par-dessus."""
    back = (wrist - grip) - axis * (wrist - grip).dot(axis)
    back.normalize()
    wrap = axis.cross(back)
    for j in range(4):
        o = grip + axis * ((j - 1.5) * 0.1)
        pts = [o + (back * math.cos(an) + wrap * math.sin(an)) * rr for an in (math.radians(d) for d in (0, 80, 160, 240))]
        rig.add(a.long_bone(f"GripMeta{bone}{j}", wrist + axis * ((j - 1.5) * 0.04), pts[0], 0.042, condyles=False,
                            segments=5), bone, "bone", **kw)
        for k in range(3):
            rig.add(a.long_bone(f"GripPhal{bone}{j}{k}", pts[k], pts[k + 1], 0.038 - 0.005 * k, condyles=False, segments=5),
                    bone, "bone", **kw)
            rig.add(r.ico(f"GripKnuckle{bone}{j}{k}", 0.042 - 0.005 * k, subdivisions=1, location=pts[k]), bone, "gold"
                    if k == 0 else "bone_shade", **kw)
        rig.add(a.claw(f"GripClaw{bone}{j}", pts[3], pts[3] - pts[2], 0.1, 0.028, curl=0.3, segments=4), bone, "horn", **kw)
    t0 = grip + axis * 0.25 + back * rr * 0.6
    t1 = grip + axis * 0.15 - wrap * rr * 1.1
    t2 = grip + axis * 0.03 - back * rr * 0.9
    for k, (p, q) in enumerate(((wrist - wrap * 0.06, t0), (t0, t1), (t1, t2))):
        rig.add(a.long_bone(f"GripThumb{bone}{k}", p, q, 0.045 - 0.005 * k, condyles=False, segments=5), bone, "bone", **kw)
    rig.add(a.claw(f"GripThumbClaw{bone}", t2, t2 - t1, 0.1, 0.028, curl=0.3, segments=4), bone, "horn", **kw)


def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd = arm_points(s)
        ua, fa, hb = f"UpperArm_{side}", f"ForeArm_{side}", f"Hand_{side}"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.17, segments=7), ua, "bone", **ARMS)
        off = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.08
        rig.add(a.long_bone(f"Radius{s}", el + off, wr + off, 0.1, condyles=False, segments=6), fa, "bone", **ARMS)
        rig.add(a.long_bone(f"Ulna{s}", el - off, wr - off, 0.085, condyles=False, segments=6), fa, "bone_shade", **ARMS)
        for k, (p, q, rad, bn) in enumerate(((sh.lerp(el, 0.45), el - sh, 0.2, ua), (wr.lerp(el, 0.15), el - wr, 0.15, fa),
                                            (wr.lerp(el, 0.28), el - wr, 0.15, fa))):
            rig.add(a.ring_around(f"Bracelet{s}{k}", p, q, rad, 0.04, segments=10), bn, "gold" if k != 1 else "lapis",
                    **ARMS)
        rig.add(r.ico(f"Wrist{s}", 0.08, subdivisions=1, location=wr), hb, "bone_shade", **ARMS)
    # Main gauche : poing sur le sceptre ouas (bâton droit, fourche au sol, tête de l'animal de Seth)
    sh, el, wr, hd = arm_points(1)
    grip_hand(rig, GRIP, Vector((0, 0, 1)), wr, "Hand_L", **ARMS)
    rig.add(r.tube("WasStaff", [tuple(STAFF_BOTTOM + Vector((0, 0, 0.35))), tuple(STAFF_TOP)], 0.055, segments=8), "Hand_L",
            "gold", **ARMS)
    for k in range(9):
        z = 0.9 + 0.75 * k
        if abs(STAFF_BOTTOM.z + z - GRIP.z) < 0.3:
            continue
        rig.add(a.ring_around(f"WasBand{k}", STAFF_BOTTOM + Vector((0, 0, z)), (0, 0, 1), 0.065, 0.025, segments=8), "Hand_L",
                "lapis", **ARMS)
    for sx in (-1, 1):    # fourche
        rig.add(a.claw(f"WasFork{sx}", STAFF_BOTTOM + Vector((0, 0, 0.4)), (sx * 0.4, 0, -1), 0.42, 0.045, curl=-0.15,
                       segments=4), "Hand_L", "gold", **ARMS)
    head_base = STAFF_TOP
    rig.add(a.blade("WasHead", head_base, head_base + Vector((0, -0.45, 0.22)), 0.14, 0.05, width_end=0.06, mid=0.16,
                    normal=(1, 0, 0)), "Hand_L", "gold", **ARMS)
    for sx in (-1, 1):
        rig.add(a.claw(f"WasEar{sx}", head_base + Vector((sx * 0.03, -0.12, 0.1)), (sx * 0.1, 0.3, 1), 0.2, 0.025, curl=0,
                       segments=4), "Hand_L", "gold", **ARMS)
    rig.add(r.ico("WasEye", 0.03, subdivisions=1, location=head_base + Vector((0, -0.28, 0.17))), "Hand_L", "glow", glow=True)
    rig.add(r.ico("WasGem", 0.07, subdivisions=1, location=head_base + Vector((0, 0, -0.08))), "Hand_L", "glow", glow=True)
    # Main droite : doigts qui pendent, ankh tenue par sa boucle
    sh, el, wr, hd = arm_points(-1)
    for j in range(4):
        off_j = (j - 1.5) * 0.07
        base = hd + Vector((0, off_j, 0))
        tip = base + Vector((0.05, off_j * 0.3 - 0.06, -0.22))
        rig.add(a.long_bone(f"Metacarpal{j}", wr + Vector((0, off_j * 0.5, 0)), base, 0.035, condyles=False, segments=5),
                "Hand_R", "bone", **ARMS)
        rig.add(a.long_bone(f"Finger{j}", base, tip, 0.03, condyles=False, segments=5), "Hand_R", "bone", **ARMS)
        rig.add(a.claw(f"FingerClaw{j}", tip, (0.2, -0.3, -1), 0.1, 0.025, curl=0.4, segments=4), "Hand_R", "horn", **ARMS)
    loop_c = hd + Vector((0.02, -0.03, -0.28))
    rig.add(a.ring_around("AnkhLoop", loop_c, (1, 0, 0), 0.13, 0.04, segments=12), "Hand_R", "gold", **ARMS)
    rig.add(r.ico("AnkhSoul", 0.07, subdivisions=2, location=loop_c, scale=(0.4, 1, 1.3)), "Hand_R", "glow", glow=True)
    bar_c = loop_c + Vector((0, 0, -0.18))
    rig.add(r.box("AnkhBar", (0.07, 0.42, 0.07), location=bar_c), "Hand_R", "gold", **ARMS)
    rig.add(r.box("AnkhStem", (0.07, 0.09, 0.45), location=bar_c + Vector((0, 0, -0.25))), "Hand_R", "gold", **ARMS)
    rig.add(r.box("AnkhInlay", (0.075, 0.04, 0.3), location=bar_c + Vector((0, 0, -0.22))), "Hand_R", "lapis", **ARMS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.16, segments=7), th, "bone", **LEGS)
        rig.add(r.ico(f"Patella{s}", 0.07, subdivisions=1, location=kn + Vector((0, -0.1, 0.02))), th, "gold", **LEGS)
        rig.add(a.long_bone(f"Tibia{s}", kn, an, 0.12, segments=7), sn, "bone", **LEGS)
        rig.add(a.long_bone(f"Tarsus{s}", an, ft + Vector((0, 0, 0.06)), 0.09, segments=6), fo, "bone", **LEGS)
        rig.add(a.claw(f"Heel{s}", an, (0, 1, 0.3), 0.18, 0.05, curl=0, segments=4), fo, "bone_shade", **LEGS)
        rig.add(a.ring_around(f"Anklet{s}", an.lerp(ft, 0.25), ft - an, 0.1, 0.035, segments=10), fo, "gold", **LEGS)
        for k in range(4):
            d = Vector((s * (k - 1.5) * 0.22, -1, 0)).normalized()
            toe = ft + d * 0.3 + Vector((0, 0, -0.05))
            rig.add(a.long_bone(f"Toe{s}{k}", ft + Vector((0, 0, 0.05)), toe, 0.035, condyles=False, segments=5), fo, "bone",
                    **LEGS)
            rig.add(a.claw(f"ToeClaw{s}{k}", toe, d + Vector((0, 0, -0.7)), 0.13, 0.03, curl=0.4, segments=4), fo, "horn",
                    **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_arms(rig)
    build_legs(rig)
    return rig
