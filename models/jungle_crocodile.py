"""Crocodile ancien squelette (Deinosuchus, ≈ 11 studs de long) — créature animable.
Pack « Ruines de la jungle maudite », créature 5.

Animal modèle : le crocodile géant (Deinosuchus) — crâne **long, large et plat**, table
crânienne carrée percée de deux fenêtres supratemporales, orbites sur le dessus, museau
élargi en spatule au bout, narines sur une bosse, surface rugueuse (ostéodermes),
**mâchoire massive** aux dents coniques entrecroisées (4e dent du bas visible) ; pattes
écartées, gastralia (côtes ventrales), longue queue épaisse.

Identité : os gris pierre usée ; **dos en plaques** : rangées d'ostéodermes carénés en
pierre gravée de glyphes lumineux, double crête de plaques sur la queue ; mousse, lianes,
yeux de jade ; rampant au sol, gueule entrouverte ; thème d'effets « swamp » (brume verte du
marécage + bulles de poison).

5 pièces Roblox : corps, Head, Tail, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, Tail1-4, Front/Hind{Upper,Lower,Foot}_{L,R}, FX_*.
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
    "bone": "#8f8a78",
    "bone_shade": "#4f4b3e",
    "tooth": "#f2ead4",
    "horn": "#22201a",
    "horn_tip": "#3dffb4",
    "disc": "#3a362a",
    "stone": "#6a665a",
    "jade": "#2f8f6f",
    "gold": "#d9a52a",
    "moss": "#4f6b2a",
    "root": "#3a2a1c",
    "gum": "#5a2228",
    "ink": "#0b0b08",
    "glow": "#3dffb4",
    "glow_hot": "#d8fff0",
}

EFFECT_THEME = "swamp"

TEST_POSE = {
    "Jaw": (-20, 0, 0),
    "Head": (0, 0, 15),
    "Tail2": (0, 0, 25),
    "Tail3": (0, 0, -30),
    "FrontUpper_L": (0, 0, 30),
}

VIEW = (0.95, -0.9, 0.6)

SPINE = a.smooth_path([(0, 2.2, 1.0), (0, 1.0, 1.1), (0, -0.2, 1.12), (0, -1.15, 1.05)], 22)
TAIL = a.smooth_path([(0, 2.2, 1.0), (0, 3.5, 0.85), (0.35, 5.0, 0.62), (-0.25, 6.5, 0.45),
                      (0.3, 7.9, 0.38)], 36)
# Crâne de Deinosuchus : (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-1.25, 0.6, 0.72, 0.62, 1.45, 0.85), (-1.8, 0.62, 0.76, 0.66, 1.5, 0.8),
         (-2.3, 0.5, 0.62, 0.58, 1.35, 0.82), (-2.9, 0.4, 0.5, 0.48, 1.22, 0.85),
         (-3.5, 0.36, 0.45, 0.44, 1.15, 0.86), (-4.0, 0.42, 0.5, 0.48, 1.13, 0.88),
         (-4.3, 0.37, 0.43, 0.41, 1.12, 0.9)]
HINGE = (0.66, -1.15, 0.86)
GAPE = math.radians(14)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
CHIN = tuple(_jm @ Vector((0, -4.4, 0.86)))
HEAD = dict(part="Head")
TAILP = dict(part="Tail")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    if i >= len(SPINE) - 4:
        return "Neck"
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // (len(SPINE) - 4))]


def tail_bone(i):
    return f"Tail{min(4, i * 4 // len(TAIL) + 1)}"


def front_leg(s):
    return (Vector((s * 0.6, -0.7, 0.92)), Vector((s * 1.25, -0.8, 0.85)),
            Vector((s * 1.35, -1.1, 0.18)), Vector((s * 1.4, -1.45, 0.08)))


def hind_leg(s):
    return (Vector((s * 0.58, 1.9, 0.92)), Vector((s * 1.4, 1.6, 0.95)),
            Vector((s * 1.5, 1.95, 0.18)), Vector((s * 1.55, 1.45, 0.08)))


def osteoderm(rig, name, center, up, along, size, bone, glyph_glow=False, **kw):
    """Plaque osseuse carénée en pierre (ostéoderme) ; certaines portent un glyphe lumineux."""
    center, up, along = Vector(center), Vector(up).normalized(), Vector(along).normalized()
    side = along.cross(up).normalized()
    rig.add(a.blade(name, center - along * size * 0.5, center + along * size * 0.5, size * 0.8,
                    size * 0.18, width_end=size * 0.65, mid=size * 0.9, normal=up, bevel=0), bone,
            "stone", **kw)
    rig.add(a.blade(f"{name}Keel", center - along * size * 0.35 + up * size * 0.08,
                    center + along * size * 0.3 + up * size * 0.32, size * 0.18, size * 0.07,
                    width_end=size * 0.04, normal=side, bevel=0), bone, "bone_shade", **kw)
    if glyph_glow:
        g = r.box(f"{name}Glyph", (size * 0.22, size * 0.22, size * 0.04))
        a.oriented(g, center + up * size * 0.1 + side * size * 0.22, up)
        rig.add(g, bone, "glow", glow=True)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE) - 4
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[n], "Spine2")
    rig.bone("Neck", SPINE[n], SPINE[-1], "Spine3")
    rig.bone("Head", SPINE[-1], (0, -4.3, 1.0), "Neck")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    nt = len(TAIL) - 1
    parent = "Spine1"
    for k in range(4):
        parent = rig.bone(f"Tail{k + 1}", TAIL[k * nt // 4], TAIL[(k + 1) * nt // 4], parent)
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Spine3"), ("Hind", hind_leg(s), "Spine1")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Foot_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
        rig.fx(f"Eye{side}", (s * 0.3, -2.0, 1.48), "Head")
    rig.fx("Heart", (0, 0.3, 0.75), "Spine2")
    rig.fx("Nostrils", (0, -4.15, 1.2), "Head")
    rig.fx("Back", SPINE[8] + Vector((0, 0, 0.5)), "Spine2")
    rig.fx("TailTip", TAIL[-1], "Tail4")


# ---------------------------------------------------------------- crâne

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.05, tip_length=0.18)
    hit = a.surface_caster(skull)
    holes = [a.hole_along((0, -4.12, 1.12), (0, 0, 1), (1, 0, 0), 0.1, 0.08, depth=0.4)]
    for s in (-1, 1):
        holes += [a.hole_along((s * 0.28, -1.45, 1.45), (0, 0, 1), (1, 0, 0), 0.15, 0.19, depth=0.4),
                  a.hole_along((s * 0.3, -2.0, 1.45), (s * 0.3, 0, 1), (1, 0, 0), 0.16, 0.15, depth=0.4)]
    # Crâne ajouré : fenêtre infratemporale + fosses latérales du museau (tunnels traversants)
    holes += [a.hole_x((0, -1.6, 1.13), 0.24, 0.14), a.hole_x((0, -2.75, 1.04), 0.3, 0.08),
              a.hole_x((0, -3.45, 1.0), 0.22, 0.065)]
    a.cut(skull, holes)
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Table crânienne carrée : rebords des fenêtres, crête occipitale
    for s in (-1, 1):
        ring = [top(s * (0.28 + 0.12 * 1.1 * math.cos(t)), -1.45 + 0.15 * 1.1 * math.sin(t))
                for t in (2 * math.pi * k / 10 for k in range(10))]
        if all(p is not None for p in ring):
            rig.add(r.tube(f"FenestraRim{s}", [tuple(p + Vector((0, 0, 0.015))) for p in ring], 0.03,
                           segments=4, closed=True), H, "bone_shade", **HEAD)
        # Orbites sur le dessus, œil de jade lumineux, paupière osseuse
        c0 = Vector((s * 0.3, -2.0, 1.4))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=c0), H, "glow", glow=True)
        rig.add(r.ico(f"Pupil{s}", 0.045, subdivisions=1, location=c0 + Vector((s * 0.05, -0.06, 0.06)),
                      scale=(0.4, 0.4, 1.5)), H, "ink", **HEAD)
        rig.add(a.ring_around(f"OrbitRim{s}", c0 + Vector((0, 0, 0.06)), (s * 0.3, 0, 1), 0.15, 0.04,
                              segments=10), H, "jade", **HEAD)
        rig.add(a.blade(f"Palpebral{s}", (s * 0.18, -2.15, 1.5), (s * 0.42, -1.85, 1.52), 0.12, 0.05,
                        width_end=0.08, normal=(0, 0, 1)), H, "bone_shade", **HEAD)
        # Bourrelet latéral de la mâchoire supérieure (festonné)
        rig.add(r.tube(f"MaxillaRidge{s}", [(s * a.side_width(SKULL, y, 0.95) * 1.0, y, 0.95)
                                            for y in (-1.5, -2.3, -3.1, -3.7, -4.15)],
                       [0.05, 0.06, 0.05, 0.06, 0.04], segments=4), H, "bone_shade", **HEAD)
        # Rangée du haut : dents coniques entrecroisées, plus grosses (« canines ») au 4e/9e rang
        for k in range(15):
            y = -4.3 + 0.21 * k
            x = s * a.side_width(SKULL, y, 0.9) * 0.92
            big = k in (2, 8)
            size = 0.3 if big else 0.16 + 0.03 * (k % 2)
            rig.add(mr.tooth(f"UpTooth{s}{k}", (x, y, 0.88), (x + s * 0.02, y, 0.88 - size), size * 0.5,
                             size * 0.42, Vector((s, 0, 0)), curl=0.06), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * a.side_width(SKULL, y, 0.9) * 0.8, y, 0.9)
                                        for y in (-4.2, -3.3, -2.3, -1.5)], 0.04, segments=4), H,
                "gum", **HEAD)
    # Rugosités (ostéodermes) sur le dessus du crâne + narines sur leur bosse
    for k, (x, y) in enumerate(((0.15, -2.6), (-0.15, -2.75), (0.25, -3.1), (-0.22, -3.3),
                                (0.1, -3.6), (-0.1, -3.85), (0.0, -2.45), (0.35, -2.5), (-0.35, -2.55))):
        p = top(x, y)
        if p is not None:
            rig.add(r.ico(f"Rugosity{k}", 0.06, subdivisions=1, location=p, scale=(1.3, 1.3, 0.5)), H,
                    "bone_shade", **HEAD)
    rig.add(r.ico("NarialBoss", 0.17, subdivisions=1, location=(0, -4.12, 1.1), scale=(1.3, 1, 0.6)), H,
            "bone_shade", **HEAD)
    rig.add(a.ring_around("NarialRim", (0, -4.12, 1.18), (0, 0, 1), 0.12, 0.03, segments=10), H, "gold",
            **HEAD)
    rig.add(r.ico("NarialGlow", 0.06, subdivisions=1, location=(0, -4.12, 1.12)), H, "glow", glow=True)
    rig.add(a.band("Occipital", [(-0.55, -1.2, 1.4), (0, -1.15, 1.5), (0.55, -1.2, 1.4)],
                   [0.1, 0.15, 0.1], 0.08, up=(0, 1, 0.4), offset=0), H, "bone_shade", **HEAD)
    for k, (x, y) in enumerate(((0.35, -1.75), (-0.4, -1.6))):
        rig.add(r.ico(f"HeadMoss{k}", 0.1, subdivisions=1, location=top(x, y), scale=(1.5, 1.3, 0.4)),
                H, "moss", **HEAD)
    # Mandibule massive (fermée puis entrouverte), 4e dent du bas visible
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = a.smooth_path([(s * HINGE[0], HINGE[1], HINGE[2]), (s * 0.6, -2.0, 0.86),
                              (s * 0.45, -3.0, 0.86), (s * 0.42, -3.9, 0.86), (s * 0.14, -4.42, 0.86)], 10)
        # Profil bombé : haute derrière (coronoïde), fine au milieu, renflée à la 4e dent
        prof = [(0, 0.48), (0.25, 0.36), (0.6, 0.24), (0.82, 0.28), (1, 0.2)]
        hs = []
        for i in range(len(line)):
            f = i / (len(line) - 1)
            j = max(k for k in range(len(prof) - 1) if prof[k][0] <= f)
            u = (f - prof[j][0]) / (prof[j + 1][0] - prof[j][0])
            hs.append(prof[j][1] + (prof[j + 1][1] - prof[j][1]) * (3 * u * u - 2 * u ** 3))
        mand = a.band(f"Mandible{s}", line, hs, [0.17 - 0.05 * i / (len(line) - 1) for i in range(len(line))],
                      offset=1)
        a.cut(mand, [a.hole_along((s * 0.62, -1.75, 0.62), (1, 0, 0), (0, 1, 0), 0.26, 0.09, depth=0.5)])
        rig.add(mand, J, "bone", **HEAD)
        rig.add(r.tube(f"MandibleBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.045, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.claw(f"Retroarticular{s}", line[0] - Vector((0, 0, 0.15)), (0, 1, 0.3), 0.4, 0.08,
                       curl=-0.2, segments=5), J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.12, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
        for k in range(14):
            p = mr.along(line, 0.1 + 0.065 * k) + Vector((-s * 0.05, 0, 0))
            big = k in (11,)
            size = 0.32 if big else 0.15 + 0.03 * (k % 2)
            rig.add(mr.tooth(f"LowTooth{s}{k}", p, p + Vector((s * 0.03 if big else 0, 0, size)),
                             size * 0.5, size * 0.42, Vector((s, 0, 0)), curl=0.06), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.06, 0, 0.02))) for p in line[1:]],
                       0.04, segments=4), J, "gum", **HEAD)
        for k in range(3):
            rig.add(r.ico(f"JawPore{s}{k}", 0.035, subdivisions=1,
                          location=mr.along(line, 0.35 + 0.18 * k) + Vector((s * 0.08, 0, -0.14))), J,
                    "ink", **HEAD)
    rig.add(r.ico("Symphysis", 0.17, subdivisions=2, location=(0, -4.36, 0.74), scale=(1.5, 1.0, 0.85)),
            J, "bone", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Throat", 0.25, subdivisions=2, location=(0, -2.0, 0.82), scale=(1.4, 2.5, 0.4)), H,
            "glow", glow=True)


# ---------------------------------------------------------------- corps, dos en plaques, queue

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        side, up = a._basis(t)
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.26, spine=1.0, lean=0.4), spine_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.26), spine_bone(i), "disc")
        # Dos en plaques : 4 ostéodermes carénés par rangée (2 au cou)
        if i % 2 == 0:
            cols = (-0.2, 0.2) if i >= n - 5 else (-0.55, -0.2, 0.2, 0.55)
            for k, x in enumerate(cols):
                osteoderm(rig, f"Osteoderm{i}{k}", SPINE[i] + up * (0.4 - 0.12 * abs(x)) + side * x,
                          up + side * x * 0.5, t, 0.36, spine_bone(i), glyph_glow=(i + k) % 5 == 0)
    # Côtes larges et basses + gastralia (côtes ventrales en chevrons)
    for k, i in enumerate(range(3, n - 4)):
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], 0.7, 0.55, s, sweep=-0.15, radius=0.06),
                    spine_bone(i), "bone")
        if k % 2 == 0:
            belly = SPINE[i] + Vector((0, -0.1, -0.6))
            rig.add(r.tube(f"Gastralia{k}", [(-0.55, belly.y + 0.1, belly.z + 0.1), tuple(belly),
                                             (0.55, belly.y + 0.1, belly.z + 0.1)], 0.035, segments=4),
                    spine_bone(i), "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.45), (0.15, 0.3), (-0.15, 0.32))):
        rig.add(a.crystal(f"JadeHeart{k}", (dx, 0.3, 0.55), 0.09 if k == 0 else 0.06, h, sides=4),
                "Spine2", "glow", glow=True)
    vine(rig, "BackVine", SPINE[2], SPINE[14], 0.62, "Spine2", turns=1.5)
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[15] + Vector((s * 0.2, 0, 0)), sh, 0.3, 0.06,
                        width_end=0.18, normal=(s, 0, 1)), "Spine3", "bone")
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.2, 0, 0)), hp + Vector((s * 0.05, 0, 0.1)),
                        0.35, 0.07, width_end=0.28, normal=(s, 0, 1)), "Spine1", "bone")
    # Queue épaisse : double crête de plaques qui devient simple vers le bout
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        side, up = a._basis(t)
        size = 0.25 - 0.17 * i / (nt - 1)
        bone = tail_bone(i)
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=1.0, lean=0.4, transverse=i < 14),
                bone, "bone", **TAILP)
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc",
                    **TAILP)
        rig.add(a.claw(f"Chevron{i}", TAIL[i] - up * size * 0.4, -up + t * 0.5, size * 1.6, size * 0.2,
                       curl=0, segments=4), bone, "bone", **TAILP)
        if i % 2 == 0:
            pair = (-0.16, 0.16) if i < nt * 0.55 else (0.0,)
            for k, x in enumerate(pair):
                h = size * 2.2
                base = TAIL[i] + up * size * 0.9 + side * x * (size / 0.25)
                rig.add(a.blade(f"TailCrest{i}{k}", base, base + up * h - t * h * 0.3, h * 0.9, 0.05,
                                width_end=0.04, normal=side, bevel=0), bone, "stone", **TAILP)
                if i % 6 == 0:
                    g = r.box(f"TailGlyph{i}{k}", (0.06, 0.06, 0.02))
                    a.oriented(g, base + up * h * 0.4 + side * 0.03, side)
                    rig.add(g, bone, "glow", glow=True)
    rig.add(r.ico("TailMoss", 0.12, subdivisions=1, location=TAIL[10] + Vector((0.15, 0, 0.3)),
                  scale=(1.5, 1.3, 0.4)), "Tail2", "moss", **TAILP)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, n_toes in (("Front", front_leg(s), 5), ("Hind", hind_leg(s), 4)):
            ub, lb, fb = f"{prefix}Upper_{side}", f"{prefix}Lower_{side}", f"{prefix}Foot_{side}"
            big = 1.15 if prefix == "Hind" else 1.0
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.13 * big, segments=7), ub,
                    "bone", **LEGS)
            off = (pts[2] - pts[1]).cross(Vector((0, 1, 0))).normalized() * 0.07
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1] + off, pts[2] + off, 0.09 * big,
                                condyles=False, segments=6), lb, "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] - off, pts[2] - off, 0.07 * big,
                                condyles=False, segments=6), lb, "bone_shade", **LEGS)
            osteoderm(rig, f"{prefix}LegPlate{s}", pts[0].lerp(pts[1], 0.5) + Vector((0, 0, 0.12)),
                      (0, 0, 1), pts[1] - pts[0], 0.3, ub, **LEGS)
            vine(rig, f"{prefix}Vine{s}", pts[1], pts[2], 0.12, lb, turns=1.2, phase=s, **LEGS)
            rig.add(r.ico(f"{prefix}Wrist{s}", 0.1 * big, subdivisions=1, location=pts[2]), fb,
                    "bone_shade", **LEGS)
            for j in range(n_toes):
                ang = math.radians(-60 + 120 * j / (n_toes - 1))
                d = Vector((s * math.sin(ang), -math.cos(ang) if prefix == "Front" else -math.cos(ang) * 0.9, 0))
                toe = pts[2] + d * 0.4 + Vector((0, 0, -0.1))
                rig.add(a.long_bone(f"{prefix}Toe{s}{j}", pts[2], toe, 0.045, condyles=False,
                                    segments=5), fb, "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{j}", toe, d + Vector((0, 0, -0.5)), 0.16, 0.04,
                               curl=0.35, segments=4), fb, "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
