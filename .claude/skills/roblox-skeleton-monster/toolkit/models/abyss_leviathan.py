"""Léviathan squelette, serpent des abysses (≈ 9 studs de haut dressé, 20 de long) — animable.
Pack « Abysses », créature 3.

Animaux modèles : le régalec (corps-ruban, longue crête dorsale rouge, couronne de longs
rayons sur la tête) et la murène (crâne haut et étroit, crocs en aiguilles, seconde mâchoire
dans la gorge).

Identité : os nacrés blanc-lavande ; pas de cornes mais une crête de rayons sur tout le dos
et une couronne de rayons sur la tête ; long serpent dont la queue ondule au sol et l'avant
se dresse ; lueur magenta, thème d'effets « souls ».

3 pièces Roblox : corps (avant), Tail (arrière), Head (tête), + lumineux.
Os : Root, Seg1-10 (de la queue vers le cou), Head, Jaw, + FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#e7e1ef",
    "bone_shade": "#aaa0bd",
    "tooth": "#fbf8ff",
    "horn": "#2a1630",
    "horn_tip": "#b02a8f",
    "disc": "#4a2550",
    "membrane": "#8c1f4f",
    "glow": "#ff3df0",
    "glow_hot": "#ffd0f8",
}

EFFECT_THEME = "souls"

TEST_POSE = {
    "Jaw": (35, 0, 0),
    "Seg10": (-15, 0, 0),
    "Seg9": (0, 0, 15),
    "Seg4": (0, 0, -20),
}

VIEW = (0.9, -1.0, 0.55)

N = 70
PATH = a.smooth_path([(3.0, 9.0, 0.4), (0.5, 7.5, 0.45), (-2.5, 6.0, 0.5), (-2.0, 3.0, 0.55),
                      (1.5, 1.5, 0.6), (2.0, -1.0, 0.9), (0.5, -2.5, 2.6), (-0.2, -3.0, 4.9),
                      (0, -3.5, 6.6)], N)

# Crâne de murène (repère local : articulation à l'origine, museau vers -Y)
SKULL = [(0.1, 0.38, 0.5, 0.42, 0.62, -0.3), (-0.4, 0.4, 0.55, 0.45, 0.75, -0.32),
         (-0.9, 0.34, 0.47, 0.4, 0.62, -0.3), (-1.4, 0.27, 0.37, 0.32, 0.48, -0.27),
         (-1.85, 0.2, 0.27, 0.24, 0.32, -0.24)]
JAW = [(0.0, 0.34, 0.47, 0.4, -0.32, -0.62), (-0.9, 0.3, 0.4, 0.34, -0.32, -0.6),
       (-1.8, 0.18, 0.23, 0.2, -0.28, -0.45)]
EYE = (-0.75, 0.3)


def seg_bone(i):
    return f"Seg{min(10, i * 10 // (N - 1) + 1)}"


def tangent(i):
    return (PATH[min(i + 1, N - 1)] - PATH[max(i - 1, 0)]).normalized()


def head_matrix():
    # La tête regarde devant elle (légèrement vers le bas), pas dans l'axe du cou qui monte
    f = (tangent(N - 1) * 0.25 + Vector((0, -1, -0.15))).normalized()
    y_axis = -f
    x_axis = y_axis.cross(Vector((0, 0, 1))).normalized()
    z_axis = x_axis.cross(y_axis).normalized()
    rot = Matrix((x_axis, y_axis, z_axis)).transposed().to_4x4()
    return Matrix.Translation(PATH[-1] + f * 0.15) @ rot


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    for b in range(10):
        i0, i1 = b * (N - 1) // 10, (b + 1) * (N - 1) // 10
        parent = rig.bone(f"Seg{b + 1}", PATH[i0], PATH[i1], parent)
    m = head_matrix()
    rig.bone("Head", m @ Vector((0, 0, 0)), m @ Vector((0, -1.9, 0)), "Seg10")
    rig.bone("Jaw", m @ Vector((0, 0.05, -0.32)), m @ Vector((0, -1.8, -0.45)), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        rig.fx(f"Eye{side}", m @ Vector((s * 0.4, EYE[0], EYE[1])), "Head")
    rig.fx("Mouth", m @ Vector((0, -0.6, -0.3)), "Head")
    rig.fx("Heart", PATH[N - 13] + Vector((0, 0, -0.1)), "Seg9")


# ---------------------------------------------------------------- tête (repère local)

def build_head(rig):
    H, J, kw = "Head", "Jaw", dict(part="Head")
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.13, 0.12), a.hole_x((0, -1.3, 0.05), 0.22, 0.09)])
    rig.add(skull, H, "bone", **kw)
    jaw = a.loft_profile("Jaw", JAW, droop=-0.1)
    rig.add(jaw, J, "bone", **kw)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=(s * (x - 0.05), EYE[0], EYE[1])),
                H, "glow", glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", (s * x, EYE[0], EYE[1]), (1, 0, 0), 0.17, 0.04,
                              segments=12), H, "bone_shade", **kw)
        # Narines tubulaires de murène au bout du museau
        rig.add(r.tube(f"NostrilTube{s}", [(s * 0.12, -1.85, 0.3), (s * 0.16, -2.05, 0.45)],
                       [0.05, 0.04], segments=6), H, "bone_shade", **kw)
        # Barbillons qui pendent
        rig.add(r.tube(f"Barbel{s}", [(s * 0.18, -1.7, -0.25), (s * 0.35, -1.9, -0.55),
                                      (s * 0.3, -1.7, -0.95)], [0.03, 0.022, 0.012], segments=4),
                H, "horn", **kw)
        # Rangées de pores lumineux le long de la mâchoire
        for i in range(5):
            yy = -0.3 - 0.3 * i
            rig.add(r.ico(f"JawPhoto{s}{i}", 0.035, subdivisions=1,
                          location=(s * a.side_width(JAW, yy, -0.45), yy, -0.45)), J, "glow",
                    glow=True)
        rig.add(r.tube(f"CheekRidge{s}", [(s * 0.42, -1.2, 0.0), (s * 0.5, -0.6, 0.02),
                                          (s * 0.44, 0.0, 0.15)], [0.04, 0.055, 0.04], segments=4),
                H, "bone_shade", **kw)
    # Couronne de régalec : longs rayons en éventail sur la tête, reliés par une membrane
    crown_root, crown_tips = [], []
    for i in range(7):
        base = Vector((0, -0.95 + 0.17 * i, a.width_at(SKULL, -0.95 + 0.17 * i, 4) - 0.03))
        d = Vector((0, 0.55 + 0.12 * i, 1)).normalized()
        length = 1.9 - 0.18 * abs(i - 2)
        tip, tan = a.claw_point(base, d, length, -0.15, 1.0)
        crown_root.append(base)
        crown_tips.append(tip)
        rig.add(a.claw(f"CrownRay{i}", base, d, length, 0.045, curl=-0.15, segments=4), H, "horn",
                **kw)
        rig.add(r.ico(f"CrownTip{i}", 0.05, subdivisions=1, location=tip), H, "glow", glow=True)
    outline = [(tuple(crown_root[0]), {H: 1})] + [(tuple(t), {H: 1}) for t in crown_tips] + \
        [(tuple(crown_root[-1]), {H: 1})]
    crest = a.membrane("CrownMembrane", outline, thickness=0.03)
    rig.pal.paint(crest, "membrane")
    crest["part"] = "Head"
    # Crocs en aiguilles (mâchoire) + seconde mâchoire de murène dans la gorge
    for jaw_s, sections, z, direction, bone in ((False, SKULL, -0.25, (0, 0.25, -1), H),
                                                (True, JAW, -0.35, (0, -0.25, 1), J)):
        y, i = -1.75, 0
        while y < -0.2:
            for s in (-1, 1):
                xx = s * a.width_at(sections, y) * 0.8
                length = (0.4 if i in (0, 1) else 0.24) * (0.85 if jaw_s else 1)
                rig.add(a.claw(f"Tooth{bone}{s}{i}", (xx, y, z), direction, length, 0.04,
                               curl=-0.12, segments=4), bone, "tooth", **kw)
            y += 0.22
            i += 1
    inner = [(0, 0.1, -0.3), (0, -0.25, -0.32), (0, -0.55, -0.3)]
    rig.add(r.tube("PharyngealJaw", inner, [0.12, 0.13, 0.1], segments=6), H, "bone_shade", **kw)
    for i in range(4):
        rig.add(a.claw(f"PharynxFang{i}", (0.06 * (1 if i % 2 else -1), -0.55 - 0.02 * i, -0.38),
                       (0, -1, -0.6), 0.22, 0.035, curl=0.1, segments=4), H, "tooth", **kw)
    rig.add(r.ico("ThroatGlow", 0.16, subdivisions=2, location=(0, -0.2, -0.32),
                  scale=(1.2, 1.4, 0.6)), H, "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    crest_pts = []
    for i, p in enumerate(PATH):
        t = i / (N - 1)
        tan = tangent(i)
        side, up = a._basis(tan)
        size = 0.14 + 0.3 * math.sin(math.pi * min(1.0, 0.15 + 0.95 * t))
        bone = seg_bone(i)
        part = "Tail" if i < N // 2 else None
        kw = dict(part=part) if part else {}
        rig.add(a.vertebra(f"V{i}", p, -tan, size, spine=0.55, lean=0.25, transverse=False),
                bone, "bone", **kw)
        if i < N - 1:
            rig.add(a.disc(f"VD{i}", p.lerp(PATH[i + 1], 0.5), tan, size), bone, "disc", **kw)
        if i % 3 == 0 and 6 <= i <= N - 8:   # côtes de serpent
            for s in (-1, 1):
                # Côte qui s'enroule autour du corps (pas vers le sol, sinon « pattes »)
                rib = r.tube(f"Rib{i}{s}", [tuple(p + side * s * size * 0.5),
                                            tuple(p + side * s * size * 1.25 - up * size * 0.35),
                                            tuple(p + side * s * size * 1.05 - up * size * 1.1),
                                            tuple(p + side * s * size * 0.35 - up * size * 1.45)],
                             [size * 0.17, size * 0.15, size * 0.12, size * 0.07], segments=4)
                rig.add(rib, bone, "bone", **kw)
        # Crête dorsale : un rayon par vertèbre, plus haut vers l'avant
        h = 0.2 + 0.35 * t
        tip = p + up * (size * 1.2 + h) - tan * h * 0.25
        crest_pts.append((p + up * size * 0.9, tip, bone, part))
        if i % 3 == 0:
            rig.add(r.tube(f"CrestRay{i}", [tuple(p + up * size * 0.9), tuple(tip)], [0.035, 0.015],
                           segments=4), bone, "horn", **kw)
        if i % 7 == 3:
            rig.add(r.ico(f"BodyPhoto{i}", size * 0.25, subdivisions=1,
                          location=p + side * size * 0.95), bone, "glow", glow=True)
    # Membrane de la crête : une bande par os, qui suit la courbure du corps
    for b in range(10):
        idx = [i for i in range(N) if seg_bone(i) == f"Seg{b + 1}"]
        idx = idx + [min(idx[-1] + 1, N - 1)]
        roots = [crest_pts[i][0] for i in idx]
        tips = [crest_pts[i][1] for i in idx]
        bones = [crest_pts[i][2] for i in idx]
        outline = [(tuple(roots[0]), {bones[0]: 1})] + \
            [(tuple(t), {bn: 1}) for t, bn in zip(tips, bones)] + \
            [(tuple(rt), {bn: 1}) for rt, bn in zip(reversed(roots[1:]), reversed(bones[1:]))]
        m = a.membrane(f"Crest{b}", outline, thickness=0.03)
        rig.pal.paint(m, "membrane")
        if crest_pts[idx[0]][3]:
            m["part"] = "Tail"
    # Cœur : cristal pulsant dans la partie dressée
    rig.add(a.crystal("Heart", PATH[N - 13] + Vector((0, 0, -0.1)), 0.22, 0.6), "Seg9", "glow",
            glow=True)
    # Pointe de queue : petit éventail de rayons lumineux
    tan = tangent(0)
    for k in (-1, 0, 1):
        side, up = a._basis(tan)
        rig.add(a.claw(f"TailRay{k}", PATH[0], -tan + side * 0.5 * k, 0.6, 0.04, curl=0,
                       segments=4), "Seg1", "horn", part="Tail")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    before = {o.name for o in bpy.context.scene.objects}
    build_head(rig)
    m = head_matrix()
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    build_body(rig)
    return rig
