"""Léviathan squelette, serpent des abysses (≈ 9 studs de haut dressé, 20 de long) — animable.
Pack « Abysses », créature 3.

Animaux modèles : le régalec (corps-ruban, longs rayons dorsaux, couronne de rayons sur la
tête) et la murène (crâne haut et étroit, crocs en aiguilles, seconde mâchoire dans la gorge,
narines tubulaires, petites ouïes rondes).

Identité : os nacrés blanc-lavande ; pas de cornes ni de bande continue sur le dos, mais des
rayons dorsaux articulés espacés et de grandes épines barbelées ; plaques ventrales ; long
serpent dont la queue ondule au sol et l'avant se dresse ; lueur magenta, thème « souls ».

4 pièces Roblox : corps (avant), Tail (arrière), Head (tête), Fins (nageoires), + lumineux.
Os : Root, Seg1-10 (de la queue vers le cou), Head, Jaw, + FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#e7e1ef",
    "bone_shade": "#aaa0bd",
    "tooth": "#fbf8ff",
    "horn": "#2a1630",
    "horn_tip": "#b02a8f",
    "disc": "#4a2550",
    "membrane": "#3a1940",
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
HEAD = dict(part="Head")


def seg_bone(i):
    return f"Seg{min(10, i * 10 // (N - 1) + 1)}"


def tangent(i):
    return (PATH[min(i + 1, N - 1)] - PATH[max(i - 1, 0)]).normalized()


def body_size(t):
    """Fin au bout de la queue (t = 0), épais à partir du milieu, cou encore costaud (t = 1)."""
    return 0.13 + 0.32 * min(1.0, t / 0.55) - 0.08 * max(0.0, (t - 0.8) / 0.2)


def head_matrix():
    # La tête regarde devant elle (légèrement vers le bas), pas dans l'axe du cou qui monte
    f = (tangent(N - 1) * 0.25 + Vector((0, -1, -0.15))).normalized()
    y_axis = -f
    x_axis = y_axis.cross(Vector((0, 0, 1))).normalized()
    z_axis = x_axis.cross(y_axis).normalized()
    rot = Matrix((x_axis, y_axis, z_axis)).transposed().to_4x4()
    return Matrix.Translation(PATH[-1] + f * 0.15) @ rot


def top(y, frac=0.0, side=1):
    """Point du dessus (frac 0) ou du flanc (frac → 1) du crâne, repère local."""
    zt, zb = a.width_at(SKULL, y, 4), a.width_at(SKULL, y, 5)
    z = zt - (zt - zb) * 0.3 * frac
    return Vector((side * a.side_width(SKULL, y, z) * frac * 0.97, y, z if frac else zt))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    for b in range(10):
        parent = rig.bone(f"Seg{b + 1}", PATH[b * (N - 1) // 10], PATH[(b + 1) * (N - 1) // 10],
                          parent)
    m = head_matrix()
    rig.bone("Head", m @ Vector((0, 0, 0)), m @ Vector((0, -1.9, 0)), "Seg10")
    rig.bone("Jaw", m @ Vector((0, 0.05, -0.32)), m @ Vector((0, -1.8, -0.45)), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        rig.fx(f"Eye{side}", m @ Vector((s * 0.4, EYE[0], EYE[1])), "Head")
    rig.fx("Mouth", m @ Vector((0, -0.6, -0.3)), "Head")
    rig.fx("Heart", PATH[N - 13] + Vector((0, 0, -0.1)), "Seg9")


# ---------------------------------------------------------------- tête (repère local)

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.13, 0.12), a.hole_x((0, -1.3, 0.05), 0.22, 0.09)])
    rig.add(skull, H, "bone", **HEAD)
    jaw = a.loft_profile("Jaw", JAW, droop=-0.1)
    rig.add(jaw, J, "bone", **HEAD)

    # Crête médiane hérissée, du museau à la nuque
    ridge = [top(y) + Vector((0, 0, 0.02)) for y in (-1.7, -1.2, -0.7, -0.2, 0.1)]
    rig.add(r.tube("SkullRidge", [tuple(p) for p in ridge], [0.04, 0.06, 0.07, 0.06, 0.05],
                   segments=5), H, "bone_shade", **HEAD)
    for i, p in enumerate(ridge[1:4]):
        rig.add(a.claw(f"RidgeSpike{i}", p, (0, 0.6, 1), 0.2, 0.04, curl=-0.1, segments=4), H,
                "horn", **HEAD)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        # Œil dans une orbite hérissée, sous une arcade
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=(s * (x - 0.05), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, 0, 0), 0.17, H, spikes=5,
                       **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.18, -1.05, 0.66), (s * 0.45, -0.5, 0.74), 0.18, 0.08,
                        width_end=0.13, mid=0.22, normal=(0, 0.15, 1)), H, "bone_shade", **HEAD)
        # Crêtes latérales et écailles osseuses
        lat = [top(y, 0.6, s) for y in (-1.6, -1.1, -0.6, -0.1)]
        rig.add(r.tube(f"LatRidge{s}", [tuple(p) for p in lat], [0.03, 0.045, 0.045, 0.035],
                       segments=4), H, "bone_shade", **HEAD)
        mr.scutes(rig, f"Scute{s}", [top(y, 0.3, s) for y in (-1.45, -1.0, -0.3, 0.0)],
                  [Vector((s * 0.4, 0, 1))] * 4, H, size=0.06, **HEAD)
        # Narines tubulaires de murène, avec bague
        rig.add(r.tube(f"NostrilTube{s}", [(s * 0.12, -1.85, 0.3), (s * 0.16, -2.05, 0.45)],
                       [0.05, 0.04], segments=6), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"NostrilRing{s}", (s * 0.16, -2.05, 0.45), (0.2 * s, -1, 0.7), 0.05,
                              0.018, segments=8), H, "horn", **HEAD)
        # Barbillons qui pendent, avec perles lumineuses au bout
        barbel = [(s * 0.18, -1.7, -0.25), (s * 0.35, -1.9, -0.55), (s * 0.3, -1.7, -0.95)]
        rig.add(r.tube(f"Barbel{s}", barbel, [0.03, 0.022, 0.012], segments=4), H, "horn", **HEAD)
        rig.add(r.ico(f"BarbelGlow{s}", 0.045, subdivisions=1, location=barbel[-1]), H, "glow",
                glow=True)
        # Ouïe ronde de murène : anneau + lueur, derrière la mâchoire
        gill = Vector((s * 0.43, 0.0, -0.2))
        rig.add(a.ring_around(f"Gill{s}", gill, (s, 0.2, 0), 0.1, 0.03, segments=10), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"GillGlow{s}", 0.07, subdivisions=1, location=gill), H, "glow", glow=True)
        # Collerette d'épines sur la nuque
        for i in range(4):
            rig.add(a.claw(f"Nuchal{s}{i}", (s * 0.35, 0.1, 0.5 - 0.22 * i),
                           (s * 0.6, 1, 0.4 - 0.3 * i), 0.4 - 0.05 * i, 0.04, curl=-0.1,
                           segments=4), H, "horn", **HEAD)
        # Pores sensoriels lumineux sur la mâchoire, pores sombres sur la lèvre
        for i in range(5):
            yy = -0.3 - 0.3 * i
            rig.add(r.ico(f"JawPhoto{s}{i}", 0.035, subdivisions=1,
                          location=(s * a.side_width(JAW, yy, -0.45), yy, -0.45)), J, "glow",
                    glow=True)
            rig.add(r.ico(f"LipPore{s}{i}", 0.03, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy - 0.1, -0.1), yy - 0.1, -0.1)), H,
                    "horn", **HEAD)
        # Crête de joue et crête de mâchoire
        rig.add(r.tube(f"CheekRidge{s}", [(s * 0.42, -1.2, 0.0), (s * 0.5, -0.6, 0.02),
                                          (s * 0.44, 0.0, 0.15)], [0.04, 0.055, 0.04], segments=4),
                H, "bone_shade", **HEAD)
        rig.add(r.tube(f"JawRidge{s}", [(s * a.width_at(JAW, y, 2) * 0.98, y, -0.52)
                                        for y in (-0.1, -0.9, -1.6)], [0.04, 0.05, 0.03],
                       segments=4), J, "bone_shade", **HEAD)
        # Cicatrices lumineuses
        mr.scar(rig, f"Scar{s}", top(-0.35, 0.95, s), top(-1.0, 0.85, s), H, width=0.05, seed=s)
    # Couronne de régalec : vraie nageoire à rayons articulés, sombre et déchirée
    root = [top(-0.95 + 0.17 * i) for i in (0, 3, 6)]
    edge = [Vector((0, -1.0, 2.2)), Vector((0, -0.4, 2.45)), Vector((0, 0.3, 2.0)),
            Vector((0, 0.75, 1.2))]
    mr.fin(rig, "Crown", root, edge, H, part="Head", rays=7, seed=3)
    # Crocs en aiguilles avec alvéoles + seconde mâchoire de murène dans la gorge
    for jaw_s, sections, z, direction, bone in ((False, SKULL, -0.25, (0, 0.25, -1), H),
                                                (True, JAW, -0.35, (0, -0.25, 1), J)):
        y, i = -1.75, 0
        while y < -0.2:
            for s in (-1, 1):
                xx = s * a.width_at(sections, y) * 0.8
                length = (0.4 if i in (0, 1) else 0.24) * (0.85 if jaw_s else 1)
                rig.add(a.claw(f"Tooth{bone}{s}{i}", (xx, y, z), direction, length, 0.04,
                               curl=-0.12, segments=4), bone, "tooth", **HEAD)
                rig.add(r.ico(f"Socket{bone}{s}{i}", 0.04, subdivisions=1,
                              location=(xx * 1.12, y, z + (0.05 if jaw_s else -0.05))), bone,
                        "bone_shade", **HEAD)
            y += 0.22
            i += 1
    inner = [(0, 0.1, -0.3), (0, -0.25, -0.32), (0, -0.55, -0.3)]
    rig.add(r.tube("PharyngealJaw", inner, [0.12, 0.13, 0.1], segments=6), H, "bone_shade", **HEAD)
    for i in range(6):
        rig.add(a.claw(f"PharynxFang{i}", (0.07 * (1 if i % 2 else -1), -0.45 - 0.04 * i, -0.38),
                       (0, -1, -0.6), 0.22, 0.035, curl=0.1, segments=4), H, "tooth", **HEAD)
    rig.add(r.ico("ThroatGlow", 0.16, subdivisions=2, location=(0, -0.2, -0.32),
                  scale=(1.2, 1.4, 0.6)), H, "glow", glow=True)
    for i, xx in enumerate((-0.08, 0.0, 0.08)):   # barbillons du menton
        rig.add(a.claw(f"ChinBarbel{i}", (xx, -1.6, -0.5), (xx * 2, 0.2, -1), 0.3, 0.02,
                       curl=0.2, segments=4), J, "horn", **HEAD)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for i, p in enumerate(PATH):
        t = i / (N - 1)
        tan = tangent(i)
        side, up = a._basis(tan)
        size = body_size(t)
        bone = seg_bone(i)
        kw = dict(part="Tail") if i < N // 2 else {}
        rig.add(a.vertebra(f"V{i}", p, -tan, size, spine=0.55, lean=0.25, transverse=i % 2 == 0),
                bone, "bone", **kw)
        if i < N - 1:
            rig.add(a.disc(f"VD{i}", p.lerp(PATH[i + 1], 0.5), tan, size), bone, "disc", **kw)
        if i % 3 == 0 and 6 <= i <= N - 8:
            for s in (-1, 1):   # côtes qui s'enroulent autour du corps
                rib = r.tube(f"Rib{i}{s}", [tuple(p + side * s * size * 0.5),
                                            tuple(p + side * s * size * 1.25 - up * size * 0.35),
                                            tuple(p + side * s * size * 1.05 - up * size * 1.1),
                                            tuple(p + side * s * size * 0.35 - up * size * 1.45)],
                             [size * 0.17, size * 0.15, size * 0.12, size * 0.07], segments=4)
                rig.add(rib, bone, "bone", **kw)
        if i % 3 == 0 and 6 <= i <= N - 8:   # plaque ventrale au bout des côtes
            belly = p - up * size * 1.5
            rig.add(a.blade(f"Belly{i}", belly + tan * size * 0.45, belly - tan * size * 0.45,
                            size * 0.9, size * 0.12, width_end=size * 0.75, normal=up, bevel=0),
                    bone, "bone_shade", **kw)
        # Rayons dorsaux articulés espacés (pas de bande continue) + grandes épines barbelées
        root = p + up * size * 1.1
        if i % 6 == 3 and i < N - 3:
            h = 0.7 + 0.5 * t
            tip = root + up * h - tan * h * 0.3
            rig.add(r.tube(f"MajorSpine{i}", [tuple(root - up * 0.1), tuple(tip)], [0.07, 0.02],
                           segments=5), bone, "horn", **kw)
            for b in (-1, 1):
                rig.add(a.claw(f"Barb{i}{b}", root.lerp(tip, 0.55), side * b - tan * 0.5 - up * 0.2,
                               0.18, 0.03, curl=0, segments=4), bone, "horn", **kw)
            rig.add(r.ico(f"SpineGlow{i}", 0.05, subdivisions=1, location=tip), bone, "glow",
                    glow=True)
        elif i % 2 == 0:
            h = 0.25 + 0.3 * t
            tip = root + up * h - tan * h * 0.25
            rig.add(r.tube(f"Ray{i}", [tuple(root - up * 0.08), tuple(tip)], [0.035, 0.015],
                           segments=4), bone, "bone_shade", **kw)
            rig.add(r.ico(f"RayJoint{i}", 0.035, subdivisions=1, location=root.lerp(tip, 0.5)),
                    bone, "bone_shade", **kw)
        # Épines latérales alternées (au bout des apophyses) et ligne latérale lumineuse
        if i % 4 == 0 and 4 <= i <= N - 5:
            s = 1 if (i // 4) % 2 == 0 else -1
            base = p + side * s * size * 0.95 + up * size * 0.45
            rig.add(a.claw(f"SideSpine{i}", base, side * s - tan * 0.6, size * 0.9, size * 0.12,
                           curl=0, segments=4), bone, "horn", **kw)
            rig.add(r.ico(f"Lateral{i}", size * 0.2, subdivisions=1,
                          location=p - side * s * size * 0.95 + up * size * 0.45), bone, "glow",
                    glow=True)
    # Pectorales derrière la tête
    for s in (-1, 1):
        i0 = N - 9
        p, tan = PATH[i0], tangent(i0)
        side, up = a._basis(tan)
        sz = body_size(i0 / (N - 1))
        root = [p + side * s * sz * 0.9 + tan * 0.15, p + side * s * sz * 0.9 - tan * 0.2]
        edge = [root[0] + side * s * 0.9 + up * 0.2 - tan * 0.1, root[0] + side * s * 1.1 - tan * 0.5,
                root[1] + side * s * 0.6 - tan * 0.5]
        mr.fin(rig, f"Pec{s}", root, edge, seg_bone(i0), part="Fins", rays=5, seed=s + 5)
    # Nageoire de queue en éventail
    p0, tan0 = PATH[0], tangent(0)
    side, up = a._basis(tan0)
    root = [p0 + up * 0.12 + tan0 * 0.25, p0, p0 - up * 0.1 + tan0 * 0.25]
    edge = [p0 - tan0 * 0.4 + up * 0.7, p0 - tan0 * 0.9 + up * 0.3, p0 - tan0 * 0.95 - up * 0.05,
            p0 - tan0 * 0.5 - up * 0.2]
    mr.fin(rig, "TailFin", root, edge, "Seg1", part="Fins", rays=6, seed=9)
    # Cœur : cristal pulsant entouré d'éclats dans la partie dressée
    heart = PATH[N - 13] + Vector((0, 0, -0.1))
    rig.add(a.crystal("Heart", heart, 0.22, 0.6), "Seg9", "glow", glow=True)
    for k in range(3):
        ang = 2 * math.pi * k / 3
        rig.add(a.crystal(f"Shard{k}", heart + Vector((math.cos(ang) * 0.3, math.sin(ang) * 0.3, 0.1)),
                          0.06, 0.2, sides=4), "Seg9", "glow", glow=True)


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
