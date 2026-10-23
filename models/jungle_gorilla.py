"""Gorille titan squelette (≈ 6 studs au garrot, marche sur les phalanges) — créature animable.
Pack « Ruines de la jungle maudite », créature 1.

Animal modèle : le gorille mâle — énorme **crête sagittale**, bourrelet sus-orbitaire massif
(torus), orbites tournées vers l'avant, museau projeté (prognathe), larges arcades, crête
nucale, canines géantes ; mandibule profonde en U ; bras très longs, marche sur les
phalanges, jambes courtes, cage large.

Identité : os gris pierre ancienne envahis de mousse et de lianes ; pas de cornes mais des
**glyphes mayas lumineux** incrustés (front, poitrine, avant-bras) et des bracelets de pierre
gravée ; **poings énormes** cerclés de pierre ; idole de jade comme cœur ; lueur turquoise de
poison ; thème d'effets « jungle » (spores + gouttes de poison).

4 pièces Roblox : corps, Head, Arms, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, UpperArm/ForeArm/Fist_{L,R}, Thigh/Shin/Foot_{L,R}, FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.forest_werewolf import vine

COLORS = {
    "bone": "#a89a7c",
    "bone_shade": "#5e5440",
    "tooth": "#f0e6cc",
    "horn": "#2a241c",
    "horn_tip": "#2fffd0",
    "disc": "#3a3428",
    "stone": "#7a7466",
    "jade": "#2f8f6f",
    "moss": "#4f6b2a",
    "root": "#3a2a1c",
    "gum": "#5a2228",
    "ink": "#0c0b08",
    "glow": "#2fffd0",
    "glow_hot": "#d0fff4",
}

EFFECT_THEME = "jungle"

TEST_POSE = {
    "Jaw": (-18, 0, 0),
    "Head": (-12, 0, 0),
    "UpperArm_L": (-50, 0, 0),
    "ForeArm_L": (-40, 0, 0),
    "Spine3": (-12, 0, 0),
}

VIEW = (0.95, -1.0, 0.3)

SPINE = a.smooth_path([(0, 1.35, 3.0), (0, 0.7, 3.6), (0, 0.0, 4.2), (0, -0.6, 4.6)], 18)
NECK = a.smooth_path([(0, -0.6, 4.6), (0, -0.78, 4.7), (0, -0.92, 4.8)], 4)
# Crâne de gorille : (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-0.85, 0.42, 0.55, 0.45, 5.35, 4.55), (-1.2, 0.5, 0.66, 0.55, 5.45, 4.45),
         (-1.5, 0.55, 0.72, 0.6, 5.4, 4.4), (-1.8, 0.45, 0.56, 0.52, 5.0, 4.35),
         (-2.05, 0.38, 0.46, 0.44, 4.8, 4.35), (-2.2, 0.33, 0.4, 0.38, 4.7, 4.36)]
HINGE = (0.55, -1.2, 4.45)
GAPE = math.radians(24)       # grognement, crocs découverts
_m = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
      @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
MUZZLE_Y = -1.5               # en avant de ce plan, la face est raccourcie (gorille = face courte)
MUZZLE_K = 0.7


def shorten(v):
    v = Vector(v)
    if v.y < MUZZLE_Y:
        v.y = MUZZLE_Y + (v.y - MUZZLE_Y) * MUZZLE_K
    return v


CHIN = tuple(shorten(_m @ Vector((0, -2.25, 4.37))))
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def arm_points(s):
    return (Vector((s * 1.05, -0.55, 4.35)), Vector((s * 1.4, -0.3, 2.5)),
            Vector((s * 1.32, -0.75, 0.95)), Vector((s * 1.32, -1.0, 0.45)))


def leg_points(s):
    return (Vector((s * 0.6, 1.25, 2.85)), Vector((s * 0.82, 0.6, 1.6)),
            Vector((s * 0.78, 1.2, 0.42)), Vector((s * 0.78, 0.55, 0.12)))


def glyph(rig, name, center, normal, size, bone, **kw):
    """Glyphe maya : tablette de pierre gravée + motif lumineux (œil carré, barres, points)."""
    center, normal = Vector(center), Vector(normal).normalized()
    tablet = r.box(name, (size, size, size * 0.22))
    a.oriented(tablet, center, normal)
    rig.add(tablet, bone, "stone", **kw)
    side, up = a._basis(normal)
    front = center + normal * size * 0.12
    parts = [((0, 0.08), (0.36, 0.3)), ((0, -0.28), (0.6, 0.1)), ((-0.3, 0.3), (0.12, 0.12)),
             ((0.3, 0.3), (0.12, 0.12))]
    for k, ((dx, dy), (sx, sy)) in enumerate(parts):
        p = r.box(f"{name}Glow{k}", (size * sx, size * sy, size * 0.08))
        mw = Matrix((side, up, normal)).transposed().to_4x4()
        p.data.transform(Matrix.Translation(front + side * dx * size + up * dy * size) @ mw)
        rig.add(p, bone, "glow", glow=True)


def stone_band(rig, name, a_pt, b_pt, t, radius, bone, **kw):
    """Bracelet de pierre gravée autour d'un os long, avec 4 incrustations lumineuses."""
    a_pt, b_pt = Vector(a_pt), Vector(b_pt)
    d = b_pt - a_pt
    q = a_pt.lerp(b_pt, t)
    rig.add(r.tube(name, [tuple(q - d.normalized() * 0.1), tuple(q + d.normalized() * 0.1)],
                   radius, segments=8), bone, "stone", **kw)
    side, up = a._basis(d)
    for k in range(4):
        ang = k * math.pi / 2 + 0.4
        n = side * math.cos(ang) + up * math.sin(ang)
        p = r.box(f"{name}Glyph{k}", (0.08, 0.08, 0.03))
        a.oriented(p, q + n * radius * 1.02, n)
        rig.add(p, bone, "glow", glow=True)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], shorten((0, -2.25, 4.8)), "Neck")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, fs = arm_points(s)
        rig.bone(f"UpperArm_{side}", sh, el, "Spine3")
        rig.bone(f"ForeArm_{side}", el, wr, f"UpperArm_{side}")
        rig.bone(f"Fist_{side}", wr, fs, f"ForeArm_{side}")
        hp, kn, an, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Spine1")
        rig.bone(f"Shin_{side}", kn, an, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", an, ft, f"Shin_{side}")
        rig.fx(f"Eye{side}", (s * 0.25, -1.55, 5.1), "Head")
        rig.fx(f"Fist{side}", fs + Vector((0, -0.3, 0.2)), f"Fist_{side}")
    rig.fx("Heart", (0, -0.2, 3.25), "Spine2")
    rig.fx("Mouth", shorten((0, -2.0, 4.3)), "Head")
    rig.fx("Crest", (0, -1.1, 6.0), "Head")


# ---------------------------------------------------------------- crâne

def build_head(rig):
    before = {o.name for o in bpy.context.scene.objects}
    build_skull(rig)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
        for v in o.data.vertices:
            v.co = shorten(v.co)


def build_skull(rig):
    H = "Head"
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_along((sx * 0.25, -1.6, 5.1), (0, 1, 0), (1, 0, 0), 0.14, 0.13,
                               depth=0.5) for sx in (-1, 1)]
          + [a.hole_along((0, -2.0, 4.82), (0, 1, 0.3), (1, 0, 0), 0.1, 0.16, depth=0.4),
             a.hole_x((0, -1.05, 4.85), 0.24, 0.18)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Énorme crête sagittale + crête nucale en éventail
    crest = [top(0, y) for y in (-0.85, -1.05, -1.25, -1.45)]
    rig.add(a.band("Sagittal", crest, [0.32, 0.4, 0.3, 0.08], 0.08, offset=0.1), H,
            "bone_shade", **HEAD)
    rig.add(r.tube("CrestRim", [tuple(p + Vector((0, 0, h + 0.03))) for p, h in
                                zip(crest, (0.29, 0.37, 0.27, 0.06))], [0.04, 0.05, 0.04, 0.02],
                   segments=4), H, "bone", **HEAD)
    rig.add(a.band("Nuchal", [(-0.55, -0.82, 5.05), (0, -0.72, 5.3), (0.55, -0.82, 5.05)],
                   [0.15, 0.25, 0.15], 0.1, up=(0, 1, 0.5), offset=0), H, "bone_shade", **HEAD)
    # Bourrelet sus-orbitaire massif (torus) en visière au-dessus des orbites
    torus = a.smooth_path([(-0.6, -1.45, 5.15), (-0.28, -1.72, 5.32), (0, -1.68, 5.28),
                           (0.28, -1.72, 5.32), (0.6, -1.45, 5.15)], 9)
    rig.add(r.tube("BrowTorus", [tuple(p) for p in torus],
                   [0.09, 0.12, 0.14, 0.13, 0.12, 0.13, 0.14, 0.12, 0.09], segments=8), H, "bone",
            **HEAD)
    glyph(rig, "ForeheadGlyph", top(0, -1.45) + Vector((0, -0.02, 0.03)), (0, -0.6, 1), 0.3, H,
          **HEAD)
    for s in (-1, 1):
        # Orbites vers l'avant, œil turquoise, arcades zygomatiques larges
        rig.add(r.ico(f"Eye{s}", 0.1, subdivisions=2, location=(s * 0.25, -1.55, 5.1)), H, "glow",
                glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", (s * 0.25, -1.68, 5.1), (0, -1, 0), 0.15, 0.04,
                              segments=10), H, "bone_shade", **HEAD)
        zyg = a.smooth_path([(s * 0.55, -1.0, 4.7), (s * 0.85, -1.35, 4.72), (s * 0.55, -1.75, 4.8)], 5)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg], [0.07, 0.1, 0.11, 0.1, 0.08],
                       segments=6), H, "bone", **HEAD)
        rig.add(r.tube(f"Maxilla{s}", [(s * 0.35, -1.75, 4.85), (s * 0.4, -2.0, 4.55),
                                       (s * 0.35, -2.12, 4.4)], [0.06, 0.07, 0.06], segments=5), H,
                "bone_shade", **HEAD)
        mr.scar(rig, f"GlyphCrack{s}", top(s * 0.3, -0.95), top(s * 0.35, -1.35), H, width=0.04,
                seed=s)
        # Rangée du haut : incisives, canine géante, prémolaires, molaires
        for k in range(2):
            p = Vector((s * (0.07 + 0.09 * k), -2.18 + 0.03 * k, 4.38))
            rig.add(mr.tooth(f"UpIncisor{s}{k}", p, p + Vector((0, -0.04, -0.15)), 0.1, 0.06,
                             Vector((s * 0.3, -1, 0))), H, "tooth", **HEAD)
        p = Vector((s * 0.3, -2.02, 4.38))
        rig.add(mr.tooth(f"UpCanine{s}", p, p + Vector((s * 0.03, -0.05, -0.6)), 0.18, 0.13,
                         Vector((s, -0.5, 0)), curl=0.15), H, "tooth", **HEAD)
        for k, (y, size, w) in enumerate(((-1.8, 0.13, 0.12), (-1.6, 0.13, 0.17), (-1.4, 0.12, 0.2))):
            p = Vector((s * a.side_width(SKULL, y, 4.4) * 0.86, y, 4.4))
            rig.add(mr.tooth(f"UpMolar{s}{k}", p, p + Vector((0, 0, -size)), w, w * 0.6,
                             Vector((s, 0, 0)), curl=0.02), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * 0.18, -2.15, 4.4), (s * 0.35, -1.9, 4.4),
                                        (s * 0.48, -1.4, 4.42)], 0.05, segments=4), H, "gum",
                **HEAD)
    for s in (-1, 1):
        # Ornements d'oreille mayas en jade (disques à tige) sur les arcades
        ear = Vector((s * 0.88, -1.2, 4.72))
        rig.add(r.tube(f"EarSpool{s}", [tuple(ear - Vector((s * 0.06, 0, 0))), tuple(ear + Vector((s * 0.1, 0, 0)))],
                       [0.18, 0.18], segments=10), H, "jade", **HEAD)
        rig.add(r.ico(f"EarGem{s}", 0.07, subdivisions=1, location=ear + Vector((s * 0.12, 0, 0))), H,
                "glow", glow=True)
        for k in range(4):
            rig.add(r.ico(f"MuzzlePore{s}{k}", 0.03, subdivisions=1,
                          location=(s * (0.25 + 0.05 * k), -1.95 + 0.06 * k, 4.62 - 0.05 * k)), H,
                    "ink", **HEAD)
    rig.add(r.tube("SkullVine", [tuple(top(x, y) + Vector((0, 0, 0.03))) for x, y in
                                 ((-0.45, -0.9), (-0.25, -1.15), (0.15, -1.25), (0.45, -1.05))],
                   0.035, segments=4), H, "root", **HEAD)
    # Mousse et liane sur le crâne
    for k, (x, y) in enumerate(((0.3, -1.05), (-0.35, -1.2), (0.0, -0.9))):
        rig.add(r.ico(f"SkullMoss{k}", 0.1, subdivisions=1, location=top(x, y),
                      scale=(1.4, 1.4, 0.45)), H, "moss", **HEAD)
    build_jaw(rig)
    rig.add(r.ico("Throat", 0.22, subdivisions=2, location=(0, -1.55, 4.38), scale=(1.4, 1.5, 0.6)),
            H, "glow", glow=True)


def build_jaw(rig):
    J = "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.48, -1.75, 4.38)),
                Vector((s * 0.32, -2.08, 4.37)), Vector((s * 0.1, -2.25, 4.37))]
        hs = [0.5, 0.44, 0.4, 0.42]
        rig.add(a.band(f"Mandible{s}", line, hs, [0.16, 0.15, 0.14, 0.14], offset=1), J, "bone",
                **HEAD)
        rig.add(r.tube(f"MandibleBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.05, segments=5), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Ramus{s}", line[0] + Vector((0, -0.1, -0.1)), line[0] + Vector((0, 0.05, 0.45)),
                        0.35, 0.1, width_end=0.2, normal=(1, 0, 0)), J, "bone", **HEAD)
        p = mr.along(line, 0.86)
        rig.add(mr.tooth(f"LowCanine{s}", p, p + Vector((s * 0.03, -0.04, 0.45)), 0.16, 0.12,
                         Vector((s, -0.5, 0)), curl=0.15), J, "tooth", **HEAD)
        for k in range(2):
            p = line[3] + Vector((-s * 0.04 * k, -0.01, 0))
            rig.add(mr.tooth(f"LowIncisor{s}{k}", p, p + Vector((0, -0.05, 0.14)), 0.08, 0.05,
                             Vector((s * 0.3, -1, 0))), J, "tooth", **HEAD)
        for k, (t, w) in enumerate(((0.6, 0.12), (0.42, 0.17), (0.25, 0.2))):
            p = mr.along(line, t)
            rig.add(mr.tooth(f"LowMolar{s}{k}", p, p + Vector((0, 0, 0.12)), w, w * 0.6,
                             Vector((s, 0, 0)), curl=0.02), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.04, 0, 0.02))) for p in line[1:]],
                       0.045, segments=4), J, "gum", **HEAD)
    rig.add(r.ico("ChinBoss", 0.14, subdivisions=1, location=(0, -2.28, 4.0), scale=(1.4, 1, 1)),
            J, "bone_shade", **HEAD)
    glyph(rig, "ChinGlyph", (0, -2.32, 4.15), (0, -1, 0.1), 0.2, J, **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(_m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for path, bonef, size in ((SPINE, spine_bone, 0.3), (NECK, lambda i: "Neck", 0.26)):
        for i in range(len(path)):
            t = tangent(path, i)
            rig.add(a.vertebra(f"Vert{size}{i}", path[i], t, size, spine=1.6, lean=0.45),
                    bonef(i), "bone")
            if i < len(path) - 1:
                rig.add(a.disc(f"Disc{size}{i}", path[i].lerp(path[i + 1], 0.5), t, size),
                        bonef(i), "disc")
    sternum = []
    for k, i in enumerate(range(6, 17)):
        hw = 1.0 + 0.3 * math.sin(math.pi * k / 10)
        depth = 1.2 + 0.4 * math.sin(math.pi * (k + 2) / 13)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.3, radius=0.09),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.35, -depth)))
    rig.add(a.band("Sternum", sternum[1:-1:2], 0.12, 0.55), "Spine2", "bone_shade")
    glyph(rig, "ChestGlyph", sternum[6] + Vector((0, -0.12, 0.05)), (0, -1, -0.3), 0.4, "Spine2")
    # Idole de jade lumineuse comme cœur
    heart = Vector((0, -0.2, 3.25))
    rig.add(a.crystal("JadeIdol", heart - Vector((0, 0, 0.3)), 0.2, 0.7, sides=4), "Spine2", "jade")
    rig.add(r.ico("HeartGlow", 0.18, subdivisions=2, location=heart), "Spine2", "glow", glow=True)
    rig.add(r.tube("IdolVine", [tuple(SPINE[11] + Vector((0, 0, -0.15))), tuple(heart + Vector((0, 0, 0.15)))],
                   0.035, segments=4), "Spine2", "root")
    for s in (-1, 1):
        sh = arm_points(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[14] + Vector((s * 0.3, 0.15, 0.1)),
                        sh + Vector((0, 0.08, 0.05)), 0.75, 0.1, width_end=0.35, mid=0.8,
                        normal=(0.3 * s, 0.6, 1)), "Spine3", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, sternum[-2] + Vector((s * 0.25, 0, 0)), 0.08,
                            condyles=False), "Spine3", "bone_shade")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.2, 0, 0)),
                        hp + Vector((s * 0.3, -0.1, 0.55)), 0.7, 0.1, width_end=0.55, mid=0.8,
                        normal=(s, 0, 0.3)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.35, 1.1, 2.5), (0, 1.15, 2.45)], 0.09,
                       segments=5), "Spine1", "bone")
    vine(rig, "BackVine", SPINE[3], SPINE[14], 0.4, "Spine2", turns=1.8)
    for k, i in enumerate((4, 9, 15)):
        rig.add(r.ico(f"BackMoss{k}", 0.16, subdivisions=1,
                      location=SPINE[i] + Vector((0.25 * (-1) ** k, 0, 0.25)), scale=(1.4, 1.3, 0.5)),
                spine_bone(i), "moss")


def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, fs = arm_points(s)
        ua, fa, fb = f"UpperArm_{side}", f"ForeArm_{side}", f"Fist_{side}"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.2, segments=8), ua, "bone", **ARMS)
        off = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.14
        rig.add(a.long_bone(f"Radius{s}", el + off, wr + off, 0.16, segments=8), fa, "bone", **ARMS)
        rig.add(a.long_bone(f"Ulna{s}", el - off, wr - off, 0.14, segments=8), fa, "bone_shade",
                **ARMS)
        stone_band(rig, f"ArmBand{s}", el, wr, 0.55, 0.3, fa, **ARMS)
        stone_band(rig, f"BicepsBand{s}", sh, el, 0.5, 0.27, ua, **ARMS)
        vine(rig, f"ArmVine{s}", sh, el, 0.24, ua, turns=1.5, phase=s, **ARMS)
        # Poing énorme (marche sur les phalanges) : carpe, paume, doigts repliés au sol
        rig.add(r.ico(f"Carpal{s}", 0.22, subdivisions=1, location=wr.lerp(fs, 0.35)), fb,
                "bone_shade", **ARMS)
        rig.add(r.ico(f"Palm{s}", 0.36, subdivisions=2, location=fs + Vector((0, 0.05, 0.12)),
                      scale=(1.0, 0.8, 0.85)), fb, "bone", **ARMS)
        for j in range(4):
            x = fs.x + s * (0.25 - 0.16 * j)
            base = Vector((x, fs.y - 0.25, fs.z + 0.15))
            curl = [base, base + Vector((0, -0.2, -0.15)), base + Vector((0, -0.12, -0.38)),
                    base + Vector((0, 0.08, -0.4))]
            rig.add(r.tube(f"Finger{s}{j}", [tuple(p) for p in curl], [0.1, 0.095, 0.09, 0.07],
                           segments=6), fb, "bone", **ARMS)
            rig.add(r.ico(f"Knuckle{s}{j}", 0.11, subdivisions=1, location=curl[2]), fb,
                    "bone_shade", **ARMS)
        rig.add(r.tube(f"Thumb{s}", [tuple(fs + Vector((-s * 0.3, -0.05, 0.1))),
                                     tuple(fs + Vector((-s * 0.35, -0.3, 0.0))),
                                     tuple(fs + Vector((-s * 0.2, -0.38, -0.08)))],
                       [0.09, 0.08, 0.06], segments=6), fb, "bone", **ARMS)
        rig.add(r.tube(f"FistBand{s}", [tuple(fs + Vector((0, -0.1, 0.2))),
                                        tuple(fs + Vector((0, -0.32, 0.2)))], 0.4, segments=8), fb,
                "stone", **ARMS)
        for k in range(3):
            g = r.box(f"FistGlyph{s}{k}", (0.1, 0.1, 0.03))
            a.oriented(g, fs + Vector((s * (0.15 - 0.15 * k), -0.2, 0.61)), (0, 0, 1))
            rig.add(g, fb, "glow", glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.2, segments=8), th, "bone", **LEGS)
        rig.add(a.long_bone(f"Tibia{s}", kn, an, 0.17, segments=8), sn, "bone", **LEGS)
        rig.add(a.long_bone(f"Fibula{s}", kn + Vector((s * 0.12, 0.05, 0)),
                            an + Vector((s * 0.1, 0.05, 0.05)), 0.07, condyles=False, segments=5),
                sn, "bone_shade", **LEGS)
        vine(rig, f"LegVine{s}", kn, an, 0.2, sn, turns=1.5, phase=2 * s, **LEGS)
        rig.add(r.ico(f"Heel{s}", 0.17, subdivisions=1, location=an + Vector((0, 0.1, -0.2))), fo,
                "bone_shade", **LEGS)
        # Pied plantigrade : 4 doigts vers l'avant + gros orteil opposable sur le côté
        for j in range(4):
            off = s * (0.1 - 0.12 * j) * -1
            base = an + Vector((off * 0.5, -0.1, -0.2))
            toe = Vector((ft.x + off, ft.y - 0.25, 0.1))
            rig.add(a.long_bone(f"Toe{s}{j}", base, toe, 0.07, condyles=False, segments=5), fo,
                    "bone", **LEGS)
            rig.add(a.claw(f"ToeNail{s}{j}", toe, (0, -1, -0.3), 0.12, 0.05, curl=0.2, segments=4),
                    fo, "horn", **LEGS)
        hallux = [an + Vector((-s * 0.15, -0.05, -0.2)), ft + Vector((-s * 0.4, 0.15, 0.0))]
        rig.add(a.long_bone(f"Hallux{s}", hallux[0], hallux[1], 0.08, condyles=False, segments=5),
                fo, "bone", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_arms(rig)
    build_legs(rig)
    return rig
