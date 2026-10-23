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

# Boîte crânienne de murène (repère local : articulation à l'origine, museau vers -Y) ; le
# museau et les mâchoires sont des os séparés (barres et plaques) devant / sous elle
SKULL = [(0.15, 0.3, 0.42, 0.36, 0.55, -0.05), (-0.3, 0.34, 0.46, 0.38, 0.72, -0.08),
         (-0.75, 0.3, 0.4, 0.33, 0.62, -0.05), (-1.05, 0.22, 0.3, 0.25, 0.5, 0.0)]
EYE = (-0.7, 0.33)
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

def maxilla(s):
    return [Vector((s * x, y, z)) for x, y, z in ((0.4, 0.0, -0.12), (0.38, -0.6, -0.12),
                                                  (0.3, -1.2, -0.1), (0.17, -1.75, -0.08),
                                                  (0.07, -2.05, -0.08))]


def dentary(s):
    # Bouche entrouverte vers l'avant (gueule de murène) : le dentaire descend vers le menton
    return [Vector((s * x, y, z)) for x, y, z in ((0.42, 0.05, -0.38), (0.38, -0.6, -0.44),
                                                  (0.28, -1.2, -0.5), (0.15, -1.75, -0.55),
                                                  (0.05, -2.0, -0.57))]


MAX_H = [0.26, 0.24, 0.2, 0.16, 0.14]
DEN_H = [0.32, 0.28, 0.22, 0.18, 0.16]


def build_head(rig):
    """Crâne de murène ajouré : boîte crânienne percée (orbites, fenêtres temporales), haute
    crête sus-occipitale, museau en barre (ethmoïde) qui laisse voir le vide, maxillaires et
    dentaires en plaques séparées, opercules en éventail, seconde mâchoire dans la gorge."""
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.2, 0.17),
                  a.hole_x((0, -0.12, 0.22), 0.15, 0.12)])
    rig.add(skull, H, "bone", **HEAD)
    # Crête sus-occipitale haute et dentelée
    crest = [(0, 0.25, 0.4), (0, 0.0, 0.6), (0, -0.35, 0.7), (0, -0.62, 0.63)]
    crest_h = [0.55, 0.62, 0.36, 0.08]
    crest_up = Vector((0, 0.4, 1)).normalized()
    crest_obj = a.band("Crest", crest, crest_h, 0.07, up=crest_up, offset=0)
    a.cut(crest_obj, [a.hole_x(Vector(crest[k]) + crest_up * crest_h[k] * 0.55, rr, rr * 0.8)
                      for k, rr in ((0, 0.1), (1, 0.13), (2, 0.07))])
    rig.add(crest_obj, H, "bone", **HEAD)
    rig.add(r.tube("CrestRim", [tuple(Vector(p) + crest_up * h) for p, h in zip(crest, crest_h)],
                   [0.04, 0.045, 0.035, 0.02], segments=5), H, "bone_shade", **HEAD)
    for i, (p, h) in enumerate(zip(crest[:3], crest_h[:3])):
        rig.add(a.claw(f"CrestSpike{i}", Vector(p) + crest_up * h, (0, 1, 0.8), 0.28 - 0.05 * i,
                       0.04, curl=-0.15, segments=4), H, "horn", **HEAD)
    # Museau : barre ethmoïde jusqu'à un nœud arrondi (vide visible dessous)
    node = Vector((0, -2.05, 0.02))
    rig.add(r.tube("Ethmoid", [(0, -0.95, 0.4), (0, -1.5, 0.3), (0, -1.95, 0.12)],
                   [0.12, 0.1, 0.09], segments=6), H, "bone", **HEAD)
    rig.add(r.ico("SnoutNode", 0.14, subdivisions=2, location=node, scale=(1.25, 1, 1)), H,
            "bone", **HEAD)
    for k, s in enumerate((-1, 1)):   # 2 grands crocs prémaxillaires
        rig.add(a.claw(f"FrontFang{k}", node + Vector((s * 0.07, -0.05, -0.1)), (0, -0.25, -1),
                       0.45, 0.05, curl=-0.15, segments=4), H, "tooth", **HEAD)
    for s in (-1, 1):
        mx, dn = maxilla(s), dentary(s)
        rig.add(a.band(f"Maxilla{s}", mx, MAX_H, 0.08), H, "bone_shade", **HEAD)
        rig.add(a.band(f"Dentary{s}", dn, DEN_H, 0.09), J, "bone", **HEAD)
        rig.add(r.tube(f"DentaryKeel{s}", [tuple(p - Vector((0, 0, h / 2)))
                                           for p, h in zip(dn, DEN_H)],
                       [0.045, 0.045, 0.04, 0.035, 0.03], segments=4), J, "bone_shade", **HEAD)
        # Crocs en aiguilles (plus grands à l'avant) + alvéoles
        for i in range(8):
            t = 0.08 + 0.11 * i
            big = 1.5 if i in (5, 6) else 1.0
            for pts, hs, sign, bone in ((mx, MAX_H, -1, H), (dn, DEN_H, 1, J)):
                h = hs[min(4, round(t * 4))]
                base = mr.along(pts, t) + Vector((0, 0, sign * h / 2))
                rig.add(a.claw(f"Tooth{bone}{s}{i}", base, (0, -0.25 * sign, sign),
                               0.22 * big * (0.85 if bone == J else 1), 0.035, curl=-0.12,
                               segments=4), bone, "tooth", **HEAD)
                rig.add(r.ico(f"Socket{bone}{s}{i}", 0.035, subdivisions=1,
                              location=base + Vector((s * 0.05, 0, -sign * 0.03))), bone,
                        "bone_shade", **HEAD)
            # Photophores le long du dentaire, pores sombres le long du maxillaire
            if i % 2 == 0:
                rig.add(r.ico(f"JawPhoto{s}{i}", 0.035, subdivisions=1,
                              location=mr.along(dn, t) + Vector((s * 0.05, 0, -0.02))), J,
                        "glow", glow=True)
                rig.add(r.ico(f"LipPore{s}{i}", 0.03, subdivisions=1,
                              location=mr.along(mx, t) + Vector((s * 0.045, 0, 0.02))), H,
                        "horn", **HEAD)
        # Apophyse coronoïde, processus rétro-articulaire, charnière, carré
        rig.add(a.blade(f"Coronoid{s}", (s * 0.42, -0.2, -0.28), (s * 0.4, -0.08, 0.02), 0.22,
                        0.06, width_end=0.08, normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(a.claw(f"Retroarticular{s}", (s * 0.43, 0.1, -0.42), (0, 1, -0.4), 0.25, 0.05,
                       curl=0.1, segments=4), J, "bone_shade", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.1, subdivisions=1, location=(s * 0.45, 0.05, -0.27)), H,
                "bone", **HEAD)
        rig.add(r.tube(f"Quadrate{s}", [(s * 0.32, 0.05, 0.15), (s * 0.45, 0.05, -0.25)],
                       [0.08, 0.07], segments=5), H, "bone", **HEAD)
        # Opercule en éventail strié, ouïe ronde lumineuse, cicatrice
        rig.add(a.blade(f"Opercle{s}", (s * 0.42, 0.18, 0.15), (s * 0.52, 0.55, -0.22), 0.42, 0.05,
                        width_end=0.3, normal=(1, -0.2, 0)), H, "bone_shade", **HEAD)
        for k in range(3):
            rig.add(r.tube(f"OpercleRay{s}{k}", [(s * 0.46, 0.2, 0.12),
                                                 (s * 0.54, 0.5, 0.05 - 0.17 * k)],
                           [0.025, 0.015], segments=4), H, "bone", **HEAD)
        gill = Vector((s * 0.55, 0.5, -0.25))
        rig.add(a.ring_around(f"Gill{s}", gill, (s, 0.2, 0), 0.09, 0.03, segments=10), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"GillGlow{s}", 0.065, subdivisions=1, location=gill), H, "glow", glow=True)
        mr.scar(rig, f"Scar{s}", (s * 0.49, 0.25, 0.08), (s * 0.55, 0.5, -0.12), H, width=0.04,
                seed=s)
        # Orbite traversante hérissée, œil enfoncé, arcade, chaîne d'os sous-orbitaires
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=(s * (x - 0.1), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, 0, 0), 0.2, H, spikes=5,
                       **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.2, -1.0, 0.58), (s * 0.44, -0.45, 0.68), 0.2, 0.08,
                        width_end=0.14, mid=0.24, normal=(0, 0.15, 1)), H, "bone_shade", **HEAD)
        for k in range(4):
            yy = -1.0 + 0.16 * k
            rig.add(r.ico(f"Suborbital{s}{k}", 0.075, subdivisions=1,
                          location=(s * (a.side_width(SKULL, yy, 0.08) + 0.01), yy, 0.06),
                          scale=(0.6, 1.2, 1)), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"Temporal{s}", (s * a.side_width(SKULL, -0.12, 0.22), -0.12, 0.22),
                              (s, 0, 0), 0.15, 0.03, segments=10), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"FrontalRidge{s}", [(s * 0.05, -1.15, 0.47), tuple(top(-0.85, 0.35, s)),
                                            tuple(top(-0.45, 0.45, s)), tuple(top(0.05, 0.4, s))],
                       [0.03, 0.045, 0.05, 0.04], segments=4), H, "bone_shade", **HEAD)
        mr.scutes(rig, f"Scute{s}", [top(y, 0.7, s) for y in (-1.0, -0.3, 0.1)],
                  [Vector((s * 0.4, 0, 1))] * 3, H, size=0.06, **HEAD)
        # Narines tubulaires sur le nœud du museau, barbillons lumineux
        rig.add(r.tube(f"NostrilTube{s}", [(s * 0.08, -2.05, 0.08), (s * 0.15, -2.25, 0.3)],
                       [0.05, 0.04], segments=6), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"NostrilRing{s}", (s * 0.15, -2.25, 0.3), (0.2 * s, -1, 0.7), 0.05,
                              0.018, segments=8), H, "horn", **HEAD)
        barbel = [(s * 0.14, -1.85, -0.2), (s * 0.35, -1.95, -0.55), (s * 0.3, -1.75, -0.95)]
        rig.add(r.tube(f"Barbel{s}", barbel, [0.03, 0.022, 0.012], segments=4), H, "horn", **HEAD)
        rig.add(r.ico(f"BarbelGlow{s}", 0.045, subdivisions=1, location=barbel[-1]), H, "glow",
                glow=True)
        # Collerette d'épines sur la nuque
        for i in range(4):
            rig.add(a.claw(f"Nuchal{s}{i}", (s * 0.35, 0.1, 0.45 - 0.2 * i),
                           (s * 0.6, 1, 0.4 - 0.3 * i), 0.4 - 0.05 * i, 0.04, curl=-0.1,
                           segments=4), H, "horn", **HEAD)
        # Arc branchial qui porte la mâchoire pharyngienne
        rig.add(r.tube(f"PharynxArch{s}", [(0, -0.05, -0.3), (s * 0.25, 0.0, -0.3),
                                           (s * 0.44, 0.05, -0.27)], 0.04, segments=4), H,
                "bone_shade", **HEAD)
    # Couronne de régalec : nageoire à rayons articulés sur le front, devant la crête
    root = [top(-1.0), top(-0.85), top(-0.68)]
    edge = [Vector((0, -1.4, 1.75)), Vector((0, -1.05, 2.05)), Vector((0, -0.7, 1.85)),
            Vector((0, -0.55, 1.15))]
    mr.fin(rig, "Crown", root, edge, H, part="Head", rays=7, seed=3)
    # Seconde mâchoire de murène dans la gorge (visible par la bouche ouverte)
    inner = [(0, 0.1, -0.3), (0, -0.25, -0.32), (0, -0.55, -0.3)]
    rig.add(r.tube("PharyngealJaw", inner, [0.12, 0.13, 0.1], segments=6), H, "bone_shade", **HEAD)
    for i in range(6):
        rig.add(a.claw(f"PharynxFang{i}", (0.07 * (1 if i % 2 else -1), -0.45 - 0.04 * i, -0.38),
                       (0, -1, -0.6), 0.22, 0.035, curl=0.1, segments=4), H, "tooth", **HEAD)
    rig.add(r.ico("ThroatGlow", 0.16, subdivisions=2, location=(0, -0.2, -0.32),
                  scale=(1.2, 1.4, 0.6)), H, "glow", glow=True)
    rig.add(r.ico("Chin", 0.11, subdivisions=1, location=(0, -2.02, -0.58)), J, "bone", **HEAD)
    for i, xx in enumerate((-0.06, 0.0, 0.06)):   # barbillons du menton
        rig.add(a.claw(f"ChinBarbel{i}", (xx, -2.0, -0.66), (xx * 2, 0.2, -1), 0.3, 0.02,
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
