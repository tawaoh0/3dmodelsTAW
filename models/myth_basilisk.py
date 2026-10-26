"""Basilic squelette (roi des serpents médiéval, ≈ 4,5 studs dressé, 9 de long) — animable.
Pack « Mythologie », créature 5 (bestiaire médiéval européen).

Animal modèle : le **coq** pour la tête (boîte crânienne ronde, bec court crochu, crête,
barbillons) greffée sur une **vipère** géante, comme le basilic des bestiaires : serpent
couronné à pattes de coq. Très différent du serpent à plumes (enroulé, collerette) et du
léviathan (murène des abysses) : **dressé en S sur deux pattes de coq**, couronné.

Identité : os vert olive ; **couronne** d'or à pointes d'os + crête rouge ; bec à crochets
venimeux et dents en scie ; regard pétrifiant (grands yeux vert-jaune) ; plumes d'os en
camail sur la nuque et ailes vestigiales ; ergots noirs ; **le bout de la queue est changé
en pierre** fissurée de lueurs (sa propre pétrification) ; thème d'effets « petrify ».

Pièces Roblox : corps, Head, Tail, Legs, + lumineux.
Os : Root, Chest, Neck, Head, Jaw, Tail1-3, Wing_{L,R}, Thigh/Shin/Foot_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.hell_phoenix import feather

COLORS = {
    "bone": "#bdbb8c",
    "bone_shade": "#4b5530",
    "tooth": "#f4f0dc",
    "horn": "#141510",
    "disc": "#2e3320",
    "vane": "#5d6b36",
    "comb": "#a8262a",
    "gold": "#d8aa36",
    "stone": "#8a877f",
    "gum": "#5a2a20",
    "ink": "#070806",
    "glow": "#d8ff3a",
    "glow_hot": "#f8ffd0",
}

EFFECT_THEME = "petrify"

TEST_POSE = {
    "Jaw": (-20, 0, 0),
    "Neck": (20, 0, 0),
    "Tail2": (0, 0, 30),
    "Wing_L": (0, 30, 0),
    "Thigh_R": (25, 0, 0),
}

VIEW = (1.0, -0.9, 0.35)

FRONT = a.smooth_path([(0, -1.0, 3.95), (0, -0.7, 3.7), (0, -0.35, 3.1), (0, -0.2, 2.2), (0, 0.0, 1.2),
                       (0, 0.6, 0.55)], 22)
BACK = a.smooth_path([(0, 0.6, 0.55), (0.6, 1.3, 0.45), (1.3, 2.4, 0.42), (0.9, 3.6, 0.4), (-0.4, 4.2, 0.35),
                      (-1.8, 4.6, 0.3), (-2.6, 5.4, 0.25)], 40)
# Crâne de coq dans son repère (occiput en 0, bec vers -Y)
SKULL = [(0.0, 0.25, 0.3, 0.22, 0.3, -0.2), (-0.25, 0.32, 0.36, 0.26, 0.36, -0.22),
         (-0.5, 0.25, 0.3, 0.22, 0.28, -0.18), (-0.7, 0.15, 0.18, 0.15, 0.18, -0.12),
         (-0.95, 0.1, 0.12, 0.1, 0.1, -0.08), (-1.1, 0.06, 0.07, 0.06, 0.03, -0.06)]
EYE = (-0.3, 0.08)
HINGE = (0.2, -0.3, -0.14)
GAPE = math.radians(26)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = Matrix.Translation(FRONT[0] + Vector((0, 0.05, 0.12))) @ Matrix.Rotation(math.radians(8), 4, "X")
HEAD = dict(part="Head")
TAILP = dict(part="Tail")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def frame(path, i):
    """Tangente, dos (vers le haut / l'arrière) et côté d'un point du corps de serpent."""
    t = tangent(path, i)
    ref = Vector((0, 0.8, 0.6))
    dorsal = (ref - t * t.dot(ref)).normalized()
    return t, dorsal, t.cross(dorsal).normalized()


def leg_points(s):
    return (Vector((s * 0.38, 0.05, 1.7)), Vector((s * 0.58, -0.4, 1.1)), Vector((s * 0.52, 0.15, 0.55)),
            Vector((s * 0.52, -0.12, 0.1)))


def front_bone(i):
    return "Neck" if i < 10 else "Chest"


def back_bone(i):
    return f"Tail{min(3, i * 3 // len(BACK) + 1)}"


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0.6, 0.0), (0, 0.6, 0.55))
    rig.bone("Chest", FRONT[-1], FRONT[10], "Root")
    rig.bone("Neck", FRONT[10], FRONT[0], "Chest")
    rig.bone("Head", FRONT[0], HEAD_M @ Vector((0, -1.1, 0.0)), "Neck")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE), HEAD_M @ (_jm @ Vector((0, -1.05, -0.08))), "Head")
    n = len(BACK) - 1
    parent = "Root"
    for k in range(3):
        parent = rig.bone(f"Tail{k + 1}", BACK[k * n // 3], BACK[(k + 1) * n // 3], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Wing_{side}", (s * 0.3, -0.25, 2.7), (s * 0.9, 0.3, 2.75), "Chest")
        hp, kn, hk, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Chest")
        rig.bone(f"Shin_{side}", kn, hk, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", hk, ft, f"Shin_{side}")
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.3, EYE[0], EYE[1])), "Head")
    rig.fx("Crown", HEAD_M @ Vector((0, -0.25, 0.75)), "Head")
    rig.fx("Heart", FRONT[14] + Vector((0, -0.2, 0)), "Chest")
    rig.fx("Stone", BACK[-8], "Tail3")


# ---------------------------------------------------------------- tête de coq couronnée

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.04, tip_length=0.08)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.15, 0.14),
                  a.hole_x((0, -0.6, 0.0), 0.08, 0.06),
                  a.hole_x((0, -0.82, 0.06), 0.1, 0.035),
                  a.hole_x((0, -0.02, -0.02), 0.07, 0.1)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    # Bec : gaine cornée noire, crochet, crochets venimeux et dents en scie
    rig.add(r.tube("Culmen", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in (-0.55, -0.8, -1.0)], [0.06, 0.05, 0.04],
                   segments=5), H, "horn", **HEAD)
    rig.add(a.claw("BeakHook", (0, -1.0, 0.05), (0, -1, -0.8), 0.28, 0.06, curl=0.7, segments=6), H, "horn", **HEAD)
    for s in (-1, 1):
        fang = Vector((s * 0.11, -0.72, -0.08))
        rig.add(mr.tooth(f"Fang{s}", fang, fang + Vector((0, -0.06, -0.38)), 0.09, 0.07, Vector((s, -0.3, 0)), curl=0.2), H,
                "tooth", **HEAD)
        rig.add(r.ico(f"Venom{s}", 0.025, subdivisions=1, location=fang + Vector((0, -0.07, -0.41)), scale=(1, 1, 1.6)), H,
                "glow", glow=True)
        for k in range(4):
            y = -0.55 - 0.12 * k
            xx = s * a.side_width(SKULL, y, -0.06) * 0.85
            rig.add(mr.tooth(f"Serration{s}{k}", (xx, y, -0.06), (xx, y - 0.02, -0.13), 0.05, 0.035, Vector((s, 0, 0)),
                             curl=0.1), H, "tooth", **HEAD)
        # Œil pétrifiant : globe lumineux, iris cerclé, pupille fendue
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.13, subdivisions=2, location=c0 - Vector((s * 0.05, 0, 0))), H, "glow", glow=True)
        rig.add(r.ico(f"Pupil{s}", 0.04, subdivisions=1, location=c0 + Vector((s * 0.06, -0.02, 0)), scale=(0.4, 0.4, 2.2)), H,
                "ink", **HEAD)
        for k in range(8):
            ang = 2 * math.pi * k / 8
            plate = r.box(f"Scleral{s}{k}", (0.03, 0.07, 0.05))
            a.oriented(plate, c0 + Vector((0, 0.15 * math.cos(ang), 0.14 * math.sin(ang))), Vector((s, 0, 0)))
            rig.add(plate, H, "bone_shade", **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.1, -0.45, 0.32), (s * 0.3, -0.15, 0.35), 0.1, 0.04, width_end=0.06,
                        normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Jugal{s}", [(s * 0.17, -0.62, -0.08), (s * 0.26, -0.38, -0.1), (s * 0.22, -0.2, -0.1)], 0.03,
                       segments=4), H, "bone", **HEAD)
        rig.add(a.claw(f"CheekSpike{s}", (s * 0.27, -0.1, -0.05), (s * 0.5, 1, -0.3), 0.3, 0.04, curl=-0.2, segments=4), H,
                "horn", **HEAD)
    # Couronne : bandeau d'or à pointes d'os, crête de coq rouge au milieu
    rig.add(a.ring_around("Circlet", (0, -0.25, 0.3), (0, 0.15, 1), 0.3, 0.045, segments=14), H, "gold", **HEAD)
    for k in range(7):
        ang = math.radians(-150 + 300 * k / 6)
        base = Vector((0.3 * math.sin(ang), -0.25 - 0.3 * math.cos(ang), 0.32))
        h = 0.32 + 0.22 * math.cos(ang / 2) ** 2
        rig.add(a.claw(f"CrownPoint{k}", base, (math.sin(ang) * 0.25, -math.cos(ang) * 0.25, 1), h, 0.05, curl=0,
                       segments=4), H, "bone", **HEAD)
        gem = r.ico(f"CrownGem{k}", 0.035, subdivisions=1, location=base + Vector((0, 0, 0.04)))
        if k % 2 == 0:
            rig.add(gem, H, "glow", glow=True)
        else:
            rig.add(gem, H, "comb", **HEAD)
    for k in range(4):
        rig.add(a.claw(f"Comb{k}", (0, -0.05 - 0.13 * k, 0.36), (0, -0.2, 1), 0.3 - 0.04 * abs(k - 1.5), 0.06, curl=-0.2,
                       segments=4), H, "comb", **HEAD)
    # Camail : plumes d'os sur la nuque
    for k in range(4):
        for s in (-1, 1):
            base = Vector((s * 0.15, 0.0 + 0.05 * k, 0.15 - 0.1 * k))
            feather(rig, f"Hackle{s}{k}", base, base + Vector((s * 0.2, 0.55, -0.25)), 0.14, H, flame=False,
                    normal=(s, 0, 0.3), **HEAD)
    # Mandibule (bec inférieur) + barbillons de coq
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.12, -0.65, -0.1)), Vector((s * 0.05, -0.95, -0.08))]
        rig.add(a.band(f"Mandible{s}", line, [0.12, 0.09, 0.06], [0.05, 0.045, 0.04], offset=1), J, "bone", **HEAD)
        rig.add(r.tube(f"LowerTomium{s}", [tuple(p + Vector((0, 0, 0.005))) for p in line[1:]], 0.02, segments=4), J, "horn",
                **HEAD)
        for k in range(3):
            p = mr.along(line, 0.45 + 0.17 * k)
            rig.add(mr.tooth(f"LowSerration{s}{k}", p, p + Vector((0, -0.02, 0.08)), 0.05, 0.035, Vector((s, 0, 0)), curl=0.1),
                    J, "tooth", **HEAD)
        rig.add(a.blade(f"Wattle{s}", (s * 0.06, -0.55, -0.18), (s * 0.08, -0.5, -0.55), 0.14, 0.04, width_end=0.1, mid=0.2,
                        normal=(s, 0, 0)), J, "comb", **HEAD)
        rig.add(r.ico(f"Quadrate{s}", 0.05, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
    rig.add(a.claw("JawTip", (0, -0.95, -0.12), (0, -1, 0.3), 0.12, 0.035, curl=-0.3, segments=4), J, "horn", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Tongue", 0.05, subdivisions=1, location=(0, -0.55, -0.15), scale=(1, 3, 0.5)), J, "glow", glow=True)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps de serpent

def snake_segment(rig, name, path, i, size, bone, color="bone", stone=False, **kw):
    t, dorsal, side = frame(path, i)
    p = path[i]
    rig.add(a.vertebra(f"{name}Vert{i}", p, t, size, spine=1.0, lean=0.4), bone, "stone" if stone else color, **kw)
    if i < len(path) - 1:
        rig.add(a.disc(f"{name}Disc{i}", p.lerp(path[i + 1], 0.5), t, size), bone, "stone" if stone else "disc", **kw)
    # Côtes en arc autour du corps + écaille ventrale
    w = size * 2.1
    if i % 2 == 0:
        for sx in (-1, 1):
            pts = [tuple(p + side * sx * (size * 0.5 + w * math.sin(an)) - dorsal * w * 1.1 * (1 - math.cos(an)) / 2)
                   for an in (math.pi * 0.92 * k / 6 for k in range(7))]
            rig.add(r.tube(f"{name}Rib{i}{sx}", pts, [size * 0.22 * (1 - 0.06 * k) for k in range(7)], segments=4), bone,
                    "stone" if stone else color, **kw)
        belly = p - dorsal * w * 0.98
        rig.add(a.band(f"{name}Scute{i}", [belly - side * w * 0.4, belly + side * w * 0.4], 0.035, size * 0.45,
                       up=tuple(-dorsal), offset=0.5), bone, "stone" if stone else "bone_shade", **kw)
        if stone and i % 4 == 0:
            g = r.box(f"{name}Crack{i}", (size * 0.5, 0.03, size * 0.12))
            a.oriented(g, p + side * (w * 0.9), side)
            rig.add(g, bone, "glow", glow=True)
    if i % 3 == 0 and not stone:
        rig.add(a.claw(f"{name}Spine{i}", p + dorsal * size * 0.9, dorsal - t * 0.4, size * 2.0, size * 0.25, curl=0,
                       segments=4), bone, "horn", **kw)


def build_body(rig):
    n = len(FRONT)
    for i in range(n):
        size = 0.17 + 0.1 * i / (n - 1)
        snake_segment(rig, "Front", FRONT, i, size, front_bone(i))
    nb = len(BACK)
    for i in range(1, nb):
        size = 0.27 - 0.2 * i / (nb - 1)
        snake_segment(rig, "Back", BACK, i, size, back_bone(i), stone=i > nb * 0.72, **TAILP)
    rig.add(a.claw("TailSpike", BACK[-1], tangent(BACK, nb - 1), 0.35, 0.05, curl=0, segments=4), "Tail3", "stone", **TAILP)
    for k, (dx, h) in enumerate(((0, 0.45), (0.1, 0.3), (-0.1, 0.32))):
        rig.add(a.crystal(f"VenomHeart{k}", FRONT[14] + Vector((dx, -0.15, 0)), 0.08 if k == 0 else 0.055, h, sides=5), "Chest",
                "glow", glow=True)
    # Ailes vestigiales de coq : petit bras + éventail de plumes d'os
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, tip = Vector((s * 0.3, -0.25, 2.7)), Vector((s * 0.7, 0.0, 2.95)), Vector((s * 0.95, 0.35, 2.7))
        rig.add(a.long_bone(f"WingHumerus{s}", sh, el, 0.06, condyles=False, segments=5), f"Wing_{side}", "bone")
        rig.add(a.long_bone(f"WingHand{s}", el, tip, 0.045, condyles=False, segments=5), f"Wing_{side}", "bone")
        for k in range(5):
            base = el.lerp(tip, k / 4)
            feather(rig, f"WingFeather{s}{k}", base, base + Vector((s * 0.25, 0.75 + 0.1 * k, -0.45 - 0.08 * k)), 0.2,
                    f"Wing_{side}", flame=False, normal=(s, 0, 0.3))


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, hk, ft = leg_points(s)
        th, sn, fo = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.blade(f"Pelvis{s}", FRONT[16] + Vector((s * 0.1, 0.1, 0)), hp + Vector((0, 0.05, 0.1)), 0.25, 0.05,
                        width_end=0.15, normal=(s, 0, 0.3)), "Chest", "bone", **LEGS)
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.1, segments=6), th, "bone", **LEGS)
        rig.add(a.long_bone(f"Tibiotarsus{s}", kn, hk, 0.08, segments=6), sn, "bone", **LEGS)
        rig.add(a.long_bone(f"Tarsus{s}", hk, ft + Vector((0, 0, 0.05)), 0.06, segments=6), fo, "bone", **LEGS)
        rig.add(a.blade(f"LegScales{s}", hk.lerp(ft, 0.15), hk.lerp(ft, 0.85), 0.07, 0.03, normal=(0, -1, 0.2), bevel=0), fo,
                "horn", **LEGS)
        rig.add(a.claw(f"Spur{s}", hk.lerp(ft, 0.45) + Vector((0, 0.05, 0)), (s * 0.4, 1, 0.3), 0.35, 0.05, curl=0.4,
                       segments=5), fo, "horn", **LEGS)
        for k, (dx, dy) in enumerate(((-0.35, -1), (0, -1), (0.35, -1), (0, 1))):
            d = Vector((dx * s, dy, 0)).normalized()
            length = 0.25 if k == 3 else 0.42
            toe = ft + d * length + Vector((0, 0, -0.05))
            rig.add(a.long_bone(f"Toe{s}{k}", ft + Vector((0, 0, 0.04)), toe, 0.035, condyles=False, segments=5), fo, "bone",
                    **LEGS)
            rig.add(a.claw(f"Talon{s}{k}", toe, d + Vector((0, 0, -0.8)), 0.16, 0.035, curl=0.5, segments=4), fo, "horn",
                    **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
