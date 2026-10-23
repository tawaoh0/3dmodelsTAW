"""Serpent à plumes (Quetzalcoatl) squelette (≈ 5,5 studs dressé, 16 de long) — animable.
Pack « Ruines de la jungle maudite », créature 2.

Animal modèle : la vipère (crotale) — tête triangulaire plate élargie à l'arrière (glandes
à venin), grandes écailles sus-oculaires, fossettes thermosensibles devant les yeux,
**crochets à venin** repliables énormes + rangées palatines, mandibules fines très écartées
(frappe), long os carré ; emprunt mythique : la **collerette de plumes** du quetzal.

Identité : os ocre-or, plumes d'os vert jade ; **collerette de plumes d'os** en éventail
derrière la tête, touffes de plumes espacées sur le dos (pas de bande continue), bagues d'or
gravées et **glyphes mayas** sur le corps ; enroulé au sol, l'avant dressé pour frapper ;
crécelle de pierre au bout de la queue ; venin émeraude ; thème d'effets « quetzal ».

4 pièces Roblox : corps (avant), Tail (spirale), Head (crâne + collerette), + lumineux.
Os : Root, Seg1-10 (de la queue vers le cou), Head, Jaw, + FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.hell_phoenix import feather
from models.jungle_gorilla import glyph

COLORS = {
    "bone": "#d8c48a",
    "bone_shade": "#7a6638",
    "tooth": "#fbf6e6",
    "horn": "#1e2418",
    "horn_tip": "#3dff8a",
    "disc": "#3a3020",
    "vane": "#2fa37a",
    "gold": "#d9a52a",
    "stone": "#7a7466",
    "jade": "#2f8f6f",
    "gum": "#4a1a2a",
    "ink": "#0c0b08",
    "glow": "#3dff8a",
    "glow_hot": "#e0ffe8",
}

EFFECT_THEME = "quetzal"

TEST_POSE = {
    "Jaw": (-25, 0, 0),
    "Seg10": (-15, 0, 0),
    "Seg9": (0, 0, 20),
    "Seg3": (0, 0, -20),
}

VIEW = (0.9, -1.0, 0.5)


def _path():
    pts = []
    for k in range(20):                      # spirale au sol (de la queue vers l'avant)
        t = k / 19
        ang = 2 * math.pi * 1.5 * (t - 1)
        rad = 0.75 + 1.45 * t
        pts.append((rad * math.sin(ang), 1.7 - rad * math.cos(ang), 0.32 + 0.12 * t))
    pts += [(0.55, -0.75, 0.6), (0.45, -1.25, 1.5), (0.1, -1.3, 2.7), (-0.1, -1.0, 3.8),
            (0.0, -1.35, 4.65), (0.0, -1.85, 5.0)]
    return a.smooth_path(pts, 80)


PATH = _path()
N = len(PATH)
# Crâne de vipère (repère local : occiput à l'origine, museau vers -Y)
SKULL = [(0.0, 0.3, 0.38, 0.3, 0.18, -0.12), (-0.35, 0.4, 0.5, 0.42, 0.22, -0.12),
         (-0.7, 0.32, 0.42, 0.36, 0.2, -0.1), (-1.05, 0.21, 0.27, 0.25, 0.15, -0.08),
         (-1.3, 0.15, 0.18, 0.16, 0.12, -0.06)]
EYE = (-0.62, 0.1)
HINGE = (0.36, 0.05, -0.1)
GAPE = math.radians(48)       # frappe : gueule grande ouverte, crochets dressés
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD = dict(part="Head")
TAILP = dict(part="Tail")


def seg_bone(i):
    return f"Seg{min(10, i * 10 // (N - 1) + 1)}"


def tangent(i):
    return (PATH[min(i + 1, N - 1)] - PATH[max(i - 1, 0)]).normalized()


def body_size(t):
    return 0.08 + 0.24 * min(1.0, t / 0.45) - 0.05 * max(0.0, (t - 0.85) / 0.15)


def head_matrix():
    f = (tangent(N - 1) * 0.3 + Vector((0, -1, -0.2))).normalized()
    y_axis = -f
    x_axis = y_axis.cross(Vector((0, 0, 1))).normalized()
    z_axis = x_axis.cross(y_axis).normalized()
    rot = Matrix((x_axis, y_axis, z_axis)).transposed().to_4x4()
    return Matrix.Translation(PATH[-1] + f * 0.12) @ rot


def place(objs, m):
    for o in objs:
        o.data.transform(m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


def new_objects(before):
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    for b in range(10):
        parent = rig.bone(f"Seg{b + 1}", PATH[b * (N - 1) // 10], PATH[(b + 1) * (N - 1) // 10],
                          parent)
    m = head_matrix()
    rig.bone("Head", m @ Vector((0, 0, 0)), m @ Vector((0, -1.35, 0)), "Seg10")
    chin = _jm @ Vector((0, -1.25, -0.1))
    rig.bone("Jaw", m @ Vector((0, HINGE[1], HINGE[2])), m @ chin, "Head")
    for s, side in ((1, "L"), (-1, "R")):
        rig.fx(f"Eye{side}", m @ Vector((s * 0.36, EYE[0], EYE[1])), "Head")
        rig.fx(f"Fang{side}", m @ Vector((s * 0.17, -1.2, -0.6)), "Head")
    rig.fx("Collar", m @ Vector((0, 0.3, 0.6)), "Head")
    rig.fx("Heart", PATH[int(N * 0.62)] + Vector((0, 0, -0.05)), "Seg7")
    rig.fx("Rattle", PATH[0], "Seg1")


# ---------------------------------------------------------------- tête de vipère (repère local)

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.12, 0.11),
                  a.hole_x((0, -0.2, 0.02), 0.16, 0.1),
                  a.hole_x((0, -0.98, 0.0), 0.06, 0.05)])           # fossettes thermosensibles
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    # Grandes écailles sus-oculaires en corniche + écailles de la tête
    for s in (-1, 1):
        rig.add(a.blade(f"Supraocular{s}", (s * 0.16, -0.85, 0.2), (s * 0.4, -0.45, 0.24), 0.2, 0.06,
                        width_end=0.12, mid=0.24, normal=(0, -0.1, 1)), H, "bone_shade", **HEAD)
        rig.add(a.claw(f"BrowHorn{s}", (s * 0.36, -0.5, 0.26), (s * 0.3, 0.6, 0.9), 0.3, 0.05,
                       curl=-0.15, segments=4), H, "horn", **HEAD)
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.09, subdivisions=2, location=c0 - Vector((s * 0.05, 0, 0))), H,
                "glow", glow=True)
        rig.add(r.ico(f"Pupil{s}", 0.04, subdivisions=1, location=c0 + Vector((s * 0.03, 0, 0)),
                      scale=(0.4, 0.4, 1.8)), H, "ink", **HEAD)
        rig.add(a.ring_around(f"OrbitRim{s}", c0, (s, 0, 0), 0.12, 0.03, segments=10), H,
                "gold", **HEAD)
        pit = Vector((s * a.side_width(SKULL, -0.98, 0.0), -0.98, 0.0))
        rig.add(a.ring_around(f"PitRim{s}", pit, (s, -0.3, 0), 0.07, 0.02, segments=8), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"PitGlow{s}", 0.04, subdivisions=1, location=pit), H, "glow", glow=True)
        rig.add(r.ico(f"Nostril{s}", 0.035, subdivisions=1, location=(s * 0.09, -1.3, 0.08)), H,
                "ink", **HEAD)
        mr.scutes(rig, f"HeadScale{s}", [top(s * 0.12, y) + Vector((0, 0, 0.01))
                                         for y in (-0.15, -0.45, -1.0)],
                  [Vector((s * 0.2, 0, 1))] * 3, H, size=0.06, color="bone_shade", **HEAD)
        # Os carré long (articulation de la mâchoire), bijou d'or
        rig.add(r.tube(f"Quadrate{s}", [(s * 0.3, 0.15, 0.1), (s * 0.38, 0.05, -0.1)], 0.045,
                       segments=5), H, "bone", **HEAD)
        rig.add(a.ring_around(f"GoldRing{s}", (s * 0.42, -0.25, 0.05), (s, 0, 0), 0.08, 0.025,
                              segments=8), H, "gold", **HEAD)
        # Crochets à venin énormes (dressés pour la frappe) + gouttes de venin
        fang_base = Vector((s * 0.16, -1.12, -0.06))
        rig.add(r.ico(f"Maxilla{s}", 0.07, subdivisions=1, location=fang_base + Vector((0, 0, 0.03))),
                H, "bone_shade", **HEAD)
        rig.add(mr.tooth(f"Fang{s}", fang_base, fang_base + Vector((s * 0.02, 0.15, -0.55)), 0.11, 0.07,
                         Vector((s, -0.3, 0)), curl=0.2), H, "tooth", **HEAD)
        rig.add(r.ico(f"VenomDrop{s}", 0.035, subdivisions=1,
                      location=fang_base + Vector((s * 0.02, 0.2, -0.6))), H, "glow", glow=True)
        # Rangées palatines de petites dents recourbées
        for k in range(5):
            p = Vector((s * 0.1, -0.85 + 0.15 * k, -0.08))
            rig.add(mr.tooth(f"Palatine{s}{k}", p, p + Vector((0, 0.06, -0.12)), 0.05, 0.03,
                             Vector((s, 0, 0)), curl=0.25), H, "tooth", **HEAD)
    rig.add(a.ring_around("NoseGold", (0, -1.32, 0.03), (0, -1, 0), 0.12, 0.025, segments=10), H,
            "gold", **HEAD)
    glyph(rig, "CrownGlyph", top(0, -0.3) + Vector((0, 0, 0.01)), (0, 0.2, 1), 0.2, H, **HEAD)
    # Mandibules fines écartées (modélisées fermées puis ouvertes autour de la charnière)
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.3, -0.45, -0.1)),
                Vector((s * 0.2, -0.9, -0.1)), Vector((s * 0.07, -1.25, -0.1))]
        rig.add(a.band(f"Mandible{s}", line, [0.12, 0.1, 0.08, 0.06], 0.05, offset=1), J, "bone",
                **HEAD)
        for k in range(6):
            p = mr.along(line, 0.2 + 0.13 * k)
            rig.add(mr.tooth(f"LowTooth{s}{k}", p, p + Vector((0, 0.05, 0.13)), 0.06, 0.035,
                             Vector((s, 0, 0)), curl=0.25), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.02, 0, 0.01))) for p in line[1:]],
                       0.02, segments=4), J, "gum", **HEAD)
    rig.add(r.ico("ChinGold", 0.05, subdivisions=1, location=(0, -1.27, -0.14)), J, "gold", **HEAD)
    place(new_objects(before), _jm)
    rig.add(r.ico("Throat", 0.12, subdivisions=2, location=(0, -0.3, -0.12), scale=(1.4, 2.4, 0.6)),
            H, "glow", glow=True)
    # Collerette de plumes d'os en éventail derrière la tête (comme un capuchon de cobra)
    center = Vector((0, 0.3, 0.0))
    for k in range(13):
        ang = math.pi * (-0.1 + 1.2 * k / 12)
        d = Vector((math.cos(ang), 0.25, math.sin(ang) + 0.15)).normalized()
        length = 0.85 + 0.35 * math.sin(math.pi * k / 12)
        feather(rig, f"Collar{k}", center + d * 0.18, center + d * length, 0.22, H,
                flame=k % 2 == 0, normal=(0, 1, 0), **HEAD)
    rig.add(a.ring_around("CollarDisc", center, (0, 1, 0), 0.24, 0.06, segments=14), H, "gold",
            **HEAD)
    rig.add(r.ico("CollarJade", 0.1, subdivisions=1, location=center + Vector((0, 0.05, 0.25))), H,
            "jade", **HEAD)


# ---------------------------------------------------------------- corps

def build_body(rig):
    m = head_matrix()
    for i in range(N):
        t = tangent(i)
        size = body_size(i / (N - 1))
        bone = seg_bone(i)
        kw = TAILP if i < N * 0.42 else {}
        rig.add(a.vertebra(f"Vert{i}", PATH[i], t, size, spine=0.9, lean=0.4), bone, "bone", **kw)
        if i < N - 1:
            rig.add(a.disc(f"Disc{i}", PATH[i].lerp(PATH[i + 1], 0.5), t, size), bone, "disc", **kw)
        side, up = a._basis(t)
        # Côtes courtes de serpent (une sur deux)
        if i % 2 == 0 and 4 < i < N - 4:
            for s in (-1, 1):
                rig.add(a.rib(f"Rib{i}{s}", PATH[i], size * 1.1, size * 1.4, s, sweep=0.0,
                              radius=size * 0.18, segments=4), bone, "bone", **kw)
        # Touffes de plumes espacées sur le dos, bagues d'or, glyphes
        if i % 9 == 4 and i > 10:
            for k, sd in enumerate((-0.35, 0.0, 0.35)):
                d = (up + side * sd).normalized()
                feather(rig, f"Tuft{i}{k}", PATH[i] + up * size * 0.8,
                        PATH[i] + up * size * 0.8 + (d + t * 0.5).normalized() * (0.55 + 0.15 * (k == 1)),
                        0.16, bone, flame=k == 1, normal=side if sd == 0 else None, **kw)
        if i % 9 == 0 and 8 < i < N - 3:
            rig.add(a.ring_around(f"GoldBand{i}", PATH[i], t, size * 1.05, size * 0.22, segments=10),
                    bone, "gold", **kw)
        if i % 18 == 13:
            glyph(rig, f"BodyGlyph{i}", PATH[i] + side * size * 0.95, side, 0.22, bone, **kw)
    # Cœur de jade dans la cage du cou
    hc = PATH[int(N * 0.62)]
    rig.add(a.crystal("JadeHeart", hc + Vector((0, 0, -0.25)), 0.08, 0.4, sides=4), "Seg7", "jade")
    rig.add(r.ico("HeartGlow", 0.09, subdivisions=1, location=hc + Vector((0, 0, -0.05))), "Seg7",
            "glow", glow=True)
    # Crécelle de pierre gravée au bout de la queue
    end, t = PATH[0], -tangent(0)
    for k in range(4):
        q = end + t * (0.08 + 0.12 * k)
        rig.add(r.tube(f"Rattle{k}", [tuple(q), tuple(q + t * 0.11)], [0.11 - 0.015 * k, 0.07],
                       segments=8), "Seg1", "stone", **TAILP)
        rig.add(a.ring_around(f"RattleGlow{k}", q + t * 0.05, t, 0.1 - 0.015 * k, 0.015,
                              segments=8), "Seg1", "glow", glow=True)
    # Mousse et liane sur la spirale
    for k, i in enumerate((6, 15, 24, 33)):
        side, up = a._basis(tangent(i))
        rig.add(r.ico(f"Moss{k}", 0.09, subdivisions=1,
                      location=PATH[i] + up * body_size(i / (N - 1)) * 0.6,
                      scale=(1.4, 1.2, 0.4)), seg_bone(i), "jade", **TAILP)
    before = {o.name for o in bpy.context.scene.objects}
    build_head(rig)
    place(new_objects(before), m)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_body(rig)
    return rig
