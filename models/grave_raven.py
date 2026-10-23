"""Corbeau géant squelette (≈ 4,5 studs de haut) — animable.
Pack « Cimetière gothique / nécromancie », créature 3.

Animal modèle : le **grand corbeau** — boîte crânienne ronde, énorme bec profond au bout
crochu, très grandes orbites à **anneau sclérotique** (plaquettes osseuses), carène sternale,
côtes à processus uncinés, pygostyle ; voûté, ailes **repliées** le long du corps (opposé du
phénix aux ailes déployées).

Identité : os ardoise sombre, plumes noir-bleuté ; **aucune corne** : bec crochu noir à dents
en scie + huppe de plumes ; perché une patte sur une **tombe brisée** (bougie, runes) ; anneau
de fer brisé à la patte ; lueur rouge sang ; thème d'effets « ravens ».

Pièces Roblox : corps, Head, Wings, + lumineux.
Os : Root, Hips, Chest, Neck1-2, Head, Jaw, Tail, Wing_{L,R}_1-3, Thigh/Shin/Tarsus/Foot_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.grave_lich_dragon import candle, chain
from models.hell_phoenix import feather

COLORS = {
    "bone": "#5d5864",
    "bone_shade": "#2a2730",
    "tooth": "#dcd5c3",
    "horn": "#111014",
    "vane": "#1f2433",
    "disc": "#1b191f",
    "iron": "#4a474f",
    "stone": "#7a7680",
    "wax": "#e3dbc0",
    "gum": "#4a1018",
    "ink": "#050406",
    "glow": "#ff2438",
    "glow_hot": "#ffd6d6",
}

EFFECT_THEME = "ravens"

TEST_POSE = {
    "Jaw": (-25, 0, 0),
    "Wing_L_1": (0, 0, -40),
    "Wing_L_2": (0, 0, 50),
    "Neck2": (20, 0, 0),
    "Tail": (-20, 0, 0),
}

VIEW = (1.0, -0.9, 0.35)

SPINE = a.smooth_path([(0, 0.95, 2.25), (0, 0.3, 2.55), (0, -0.4, 2.9)], 9)
NECK = a.smooth_path([(0, -0.4, 2.95), (0, -0.75, 3.35), (0, -0.7, 3.75), (0, -0.9, 4.0)], 8)
# Crâne de corbeau dans son repère (occiput en 0, bec vers -Y)
SKULL = [(0.0, 0.24, 0.28, 0.2, 0.28, -0.2), (-0.25, 0.32, 0.36, 0.25, 0.36, -0.22),
         (-0.5, 0.26, 0.3, 0.2, 0.3, -0.17), (-0.75, 0.14, 0.17, 0.14, 0.23, -0.1),
         (-1.1, 0.1, 0.12, 0.1, 0.15, -0.06), (-1.4, 0.07, 0.08, 0.07, 0.07, -0.04),
         (-1.6, 0.04, 0.05, 0.04, 0.0, -0.04)]
EYE = (-0.32, 0.08)
HINGE = (0.2, -0.38, -0.12)
GAPE = math.radians(22)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = Matrix.Translation(NECK[-1] + Vector((0, 0.05, 0.08))) @ Matrix.Rotation(math.radians(12), 4, "X")
TOMB = Vector((-0.42, 0.25, 0.0))
HEAD = dict(part="Head")
WINGS = dict(part="Wings")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def leg_points(s):
    if s > 0:
        return (Vector((0.32, 0.7, 2.15)), Vector((0.45, 0.2, 1.6)), Vector((0.35, 0.75, 0.75)),
                Vector((0.35, 0.5, 0.12)))
    # Patte droite posée sur la tombe brisée
    return (Vector((-0.32, 0.7, 2.15)), Vector((-0.48, 0.1, 1.75)), Vector((-0.4, 0.55, 1.3)),
            Vector((-0.42, 0.2, 0.84)))


def wing_points(s):
    return (Vector((s * 0.4, -0.3, 2.85)), Vector((s * 0.62, 0.35, 2.6)),
            Vector((s * 0.6, -0.2, 2.35)), Vector((s * 0.5, 0.85, 1.95)))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[4], "Root")
    rig.bone("Chest", SPINE[4], SPINE[-1], "Hips")
    rig.bone("Neck1", NECK[0], NECK[4], "Chest")
    rig.bone("Neck2", NECK[4], NECK[-1], "Neck1")
    rig.bone("Head", NECK[-1], HEAD_M @ Vector((0, -1.6, 0.0)), "Neck2")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE), HEAD_M @ (_jm @ Vector((0, -1.5, -0.07))), "Head")
    rig.bone("Tail", SPINE[0], SPINE[0] + Vector((0, 0.6, -0.3)), "Hips")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, tip = wing_points(s)
        rig.bone(f"Wing_{side}_1", sh, el, "Chest")
        rig.bone(f"Wing_{side}_2", el, wr, f"Wing_{side}_1")
        rig.bone(f"Wing_{side}_3", wr, tip, f"Wing_{side}_2")
        hp, kn, an, ft = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn, "Hips")
        rig.bone(f"Shin_{side}", kn, an, f"Thigh_{side}")
        rig.bone(f"Tarsus_{side}", an, ft, f"Shin_{side}")
        rig.bone(f"Foot_{side}", ft, ft + Vector((0, -0.4, 0)), f"Tarsus_{side}")
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.3, EYE[0], EYE[1])), "Head")
    rig.fx("Beak", HEAD_M @ Vector((0, -1.5, -0.05)), "Head")
    rig.fx("Heart", (0, -0.1, 2.3), "Chest")
    rig.fx("Candle", TOMB + Vector((-0.3, 0, 1.05)), "Root")
    rig.fx("Back", SPINE[4] + Vector((0, 0, 0.4)), "Chest")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.05, tip_length=0.1)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.16, 0.15),
                  a.hole_x((0, -0.62, 0.02), 0.08, 0.06),                  # fenêtre antorbitaire
                  a.hole_x((0, -0.88, 0.1), 0.12, 0.04),                   # narine en fente
                  a.hole_x((0, -0.05, 0.0), 0.07, 0.1)])                   # fosse temporale
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    # Gaine cornée du bec : arête dorsale (culmen) noire et crochet terminal
    rig.add(r.tube("Culmen", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in
                              (-0.6, -0.9, -1.2, -1.45)], [0.06, 0.055, 0.045, 0.035], segments=5),
            H, "horn", **HEAD)
    rig.add(a.claw("BeakHook", (0, -1.42, 0.06), (0, -1, -0.5), 0.32, 0.06, curl=0.7, segments=6), H,
            "horn", **HEAD)
    rig.add(r.tube("Nuchal", [(0, 0.05, 0.25), (0, -0.2, 0.37), (0, -0.45, 0.31)], 0.04, segments=4), H,
            "bone_shade", **HEAD)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=c0 - Vector((s * 0.07, 0, 0))), H,
                "glow", glow=True)
        # Anneau sclérotique : couronne de plaquettes osseuses autour de l'œil
        for k in range(10):
            ang = 2 * math.pi * k / 10
            p = c0 + Vector((0, 0.15 * math.cos(ang), 0.14 * math.sin(ang)))
            plate = r.box(f"Scleral{s}{k}", (0.03, 0.08, 0.05))
            a.oriented(plate, p, Vector((s, 0, 0)))
            rig.add(plate, H, "bone_shade", **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.12, -0.5, 0.33), (s * 0.3, -0.18, 0.36), 0.1, 0.04,
                        width_end=0.06, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Jugal{s}", [(s * 0.2, -0.75, -0.08), (s * 0.27, -0.45, -0.12),
                                     (s * 0.22, -0.3, -0.12)], 0.03, segments=4), H, "bone", **HEAD)
        # Bord tranchant du bec en dents de scie (démoniaque)
        for k in range(6):
            y = -0.7 - 0.12 * k
            xx = s * a.side_width(SKULL, y, -0.05) * 0.85
            size = 0.1 - 0.008 * k
            rig.add(mr.tooth(f"Serration{s}{k}", (xx, y, -0.05), (xx, y - 0.03, -0.05 - size), size * 0.6,
                             size * 0.4, Vector((s, 0, 0)), curl=0.15), H, "tooth", **HEAD)
        rig.add(r.tube(f"Tomium{s}", [(s * a.side_width(SKULL, y, -0.05) * 0.95, y, -0.05)
                                      for y in (-0.6, -1.0, -1.35)], 0.025, segments=4), H, "horn",
                **HEAD)
        # Huppe de plumes de corbeau sur la nuque
        for k in range(3):
            base = Vector((s * 0.12, 0.0 + 0.05 * k, 0.2 - 0.08 * k))
            feather(rig, f"Hackle{s}{k}", base, base + Vector((s * 0.15, 0.45, 0.1 - 0.12 * k)), 0.12, H,
                    flame=False, normal=(s, 0, 0.3), **HEAD)
    # Mandibule (bec inférieur) : deux branches qui se rejoignent, gaine cornée, dents en scie
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.14, -0.75, -0.11)),
                Vector((s * 0.08, -1.15, -0.08)), Vector((s * 0.02, -1.5, -0.06))]
        rig.add(a.band(f"Mandible{s}", line, [0.14, 0.11, 0.08, 0.05], [0.06, 0.05, 0.045, 0.04],
                       offset=1), J, "bone", **HEAD)
        rig.add(r.tube(f"LowerTomium{s}", [tuple(p + Vector((0, 0, 0.005))) for p in line[1:]], 0.022,
                       segments=4), J, "horn", **HEAD)
        rig.add(r.ico(f"Quadrate{s}", 0.06, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
        for k in range(5):
            p = mr.along(line, 0.3 + 0.12 * k)
            size = 0.08 - 0.008 * k
            rig.add(mr.tooth(f"LowSerration{s}{k}", p, p + Vector((0, -0.02, size)), size * 0.6, size * 0.4,
                             Vector((s, 0, 0)), curl=0.15), J, "tooth", **HEAD)
    rig.add(a.claw("JawTip", (0, -1.45, -0.1), (0, -1, 0.3), 0.15, 0.04, curl=-0.3, segments=4), J,
            "horn", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Tongue", 0.06, subdivisions=1, location=(0, -0.7, -0.14), scale=(1, 3, 0.5)), J,
            "glow", glow=True)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for path, bones, size in ((SPINE, ("Hips", "Chest"), 0.2), (NECK, ("Neck1", "Neck2"), 0.16)):
        n = len(path)
        for i in range(n):
            t = tangent(path, i)
            bone = bones[0] if i < n // 2 else bones[1]
            rig.add(a.vertebra(f"Vert{bones[0]}{i}", path[i], t, size, spine=1.0, lean=0.4), bone, "bone")
            if i < n - 1:
                rig.add(a.disc(f"Disc{bones[0]}{i}", path[i].lerp(path[i + 1], 0.5), t, size), bone,
                        "disc")
    # Cage : côtes à processus uncinés, énorme carène (bréchet), fourchette, coracoïdes
    keel = []
    for k, i in enumerate(range(2, 8)):
        depth = 0.55 + 0.35 * math.sin(math.pi * k / 5)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], 0.42, depth, s, sweep=-0.2, radius=0.045), "Chest",
                    "bone")
            rig.add(a.claw(f"Uncinate{k}{s}", SPINE[i] + Vector((s * 0.4, 0.02, -depth * 0.4)),
                           (0, 1, -0.3), 0.18, 0.025, curl=0, segments=4), "Chest", "bone_shade")
        keel.append(SPINE[i] + Vector((0, -0.15, -depth - 0.05)))
    rig.add(a.band("Sternum", keel[1:], 0.08, 0.5), "Chest", "bone_shade")
    rig.add(a.band("Carina", keel[1:], [0.08, 0.18, 0.24, 0.18, 0.08], 0.05, up=(0, 0, -1), offset=0),
            "Chest", "bone")
    for s in (-1, 1):
        sh = wing_points(s)[0]
        rig.add(a.long_bone(f"Coracoid{s}", sh, keel[-1] + Vector((s * 0.15, 0, 0.05)), 0.06,
                            condyles=False, segments=5), "Chest", "bone")
        rig.add(a.long_bone(f"Furcula{s}", sh + Vector((0, -0.05, -0.05)), keel[-1] + Vector((0, -0.2, 0.3)),
                            0.035, condyles=False, segments=4), "Chest", "bone_shade")
        rig.add(a.blade(f"Scapula{s}", sh, SPINE[2] + Vector((s * 0.25, 0, 0.1)), 0.12, 0.04,
                        width_end=0.05, normal=(s, 0, 1)), "Chest", "bone")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[3] + Vector((s * 0.15, 0, 0.05)), SPINE[0] + Vector((s * 0.3, 0.3, -0.05)),
                        0.35, 0.05, width_end=0.25, mid=0.45, normal=(s, 0, 1)), "Hips", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.3, 1.1, 1.85), (s * 0.15, 1.35, 1.75)], 0.03,
                       segments=4), "Hips", "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.4), (0.1, 0.28), (-0.1, 0.3))):
        rig.add(a.crystal(f"BloodHeart{k}", (dx, -0.1, 2.3), 0.09 if k == 0 else 0.06, h, sides=4),
                "Chest", "glow", glow=True)
    # Pygostyle + éventail de plumes de queue
    pyg = SPINE[0] + Vector((0, 0.25, -0.05))
    rig.add(a.claw("Pygostyle", SPINE[0], (0, 1, 0.3), 0.3, 0.08, curl=0, segments=4), "Tail", "bone")
    for k in range(5):
        dx = (k - 2) * 0.12
        feather(rig, f"TailFeather{k}", pyg + Vector((dx * 0.5, 0, 0)),
                pyg + Vector((dx * 2, 1.4 - 0.1 * abs(k - 2), -0.75)), 0.2, "Tail", flame=False,
                normal=(0, 0.45, 1))


def build_wings(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, tip = wing_points(s)
        b1, b2, b3 = (f"Wing_{side}_{k}" for k in (1, 2, 3))
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.07, segments=6), b1, "bone", **WINGS)
        rig.add(a.long_bone(f"Ulna{s}", el, wr, 0.055, segments=6), b2, "bone", **WINGS)
        rig.add(a.long_bone(f"Radius{s}", el + Vector((0, -0.03, 0.06)), wr + Vector((0, -0.02, 0.06)), 0.035,
                            condyles=False, segments=5), b2, "bone_shade", **WINGS)
        rig.add(a.long_bone(f"Hand{s}", wr, tip, 0.05, condyles=False, segments=5), b3, "bone", **WINGS)
        rig.add(a.claw(f"Alula{s}", wr, (s * 0.2, -1, 0.3), 0.2, 0.035, curl=0.3, segments=4), b3, "horn",
                **WINGS)
        # Rémiges repliées le long du corps : secondaires (avant-bras) puis primaires (main)
        nrm = (s, 0, 0.15)
        for k in range(5):
            p = el.lerp(wr, 0.15 + 0.17 * k)
            feather(rig, f"Secondary{s}{k}", p, p + Vector((s * 0.05, 1.1 + 0.05 * k, -0.7 - 0.05 * k)), 0.22,
                    b2, flame=False, normal=nrm, **WINGS)
        for k in range(6):
            p = wr.lerp(tip, 0.1 + 0.17 * k)
            feather(rig, f"Primary{s}{k}", p, p + Vector((-s * 0.04 * k, 1.0 + 0.12 * k, -0.45 - 0.03 * k)),
                    0.2, b3, flame=False, normal=nrm, **WINGS)
        for k in range(3):
            p = sh.lerp(el, 0.3 + 0.25 * k)
            feather(rig, f"Covert{s}{k}", p, p + Vector((s * 0.06, 0.6, -0.35)), 0.18, b1, flame=False,
                    normal=nrm, **WINGS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        th, sn, ts, fo = (f"{nm}_{side}" for nm in ("Thigh", "Shin", "Tarsus", "Foot"))
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.09, segments=6), th, "bone")
        rig.add(a.long_bone(f"Tibiotarsus{s}", kn, an, 0.07, segments=6), sn, "bone")
        rig.add(a.long_bone(f"Tarsometatarsus{s}", an, ft + Vector((0, 0, 0.04)), 0.055, segments=6), ts,
                "bone")
        rig.add(a.blade(f"Scales{s}", an.lerp(ft, 0.15), an.lerp(ft, 0.85), 0.06, 0.03, normal=(0, -1, 0.2),
                        bevel=0), ts, "horn")
        # 3 doigts devant, 1 derrière, griffes noires
        for k, (dx, dy) in enumerate(((-0.25, -1), (0, -1), (0.25, -1), (0, 1))):
            d = Vector((dx * s, dy, 0)).normalized()
            length = 0.28 if k == 3 else 0.42
            toe = ft + d * length + Vector((0, 0, -0.06))
            rig.add(a.long_bone(f"Toe{s}{k}", ft, toe, 0.035, condyles=False, segments=5), fo, "bone")
            rig.add(a.claw(f"Talon{s}{k}", toe, d + Vector((0, 0, -0.9)), 0.17, 0.035, curl=0.5,
                           segments=4), fo, "horn")
    # Anneau de fer brisé à la patte gauche
    hp, kn, an, ft = leg_points(1)
    rig.add(a.ring_around("Shackle", an.lerp(ft, 0.4), ft - an, 0.09, 0.025, segments=8), "Tarsus_L", "iron")
    chain(rig, "ShackleChain", an.lerp(ft, 0.4) + Vector((0.08, 0, -0.05)), Vector((0.55, 0.5, 0.05)),
          "Tarsus_L", sag=0.05, radius=0.05)
    # Tombe brisée sous la patte droite : dalle penchée, éclat, runes, bougie
    stone = r.box("Tombstone", (0.75, 0.3, 0.84), location=TOMB + Vector((0, 0, 0.42)))
    rig.add(stone, "Root", "stone")
    rig.add(r.box("TombBase", (0.95, 0.5, 0.12), location=TOMB + Vector((0, 0, 0.06))), "Root", "stone")
    rig.add(a.crystal("TombShard", TOMB + Vector((0.28, 0.0, 0.84)), 0.1, 0.25, sides=4), "Root", "stone")
    for k in range(3):
        g = r.box(f"TombRune{k}", (0.1, 0.02, 0.12), location=TOMB + Vector((-0.2 + 0.2 * k, -0.155, 0.45)))
        rig.add(g, "Root", "glow", glow=True)
    candle(rig, "TombCandle", TOMB + Vector((-0.3, -0.05, 0.84)), 0.18, "Root")
    for k in range(3):
        rig.add(r.ico(f"Bones{k}", 0.08, subdivisions=1, location=TOMB + Vector((0.5 + 0.12 * k, -0.25, 0.04)),
                      scale=(2.2, 0.6, 0.6)), "Root", "bone_shade")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_wings(rig)
    build_legs(rig)
    return rig
