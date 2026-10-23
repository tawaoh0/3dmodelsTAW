"""Cheval cauchemar squelette (≈ 6,5 studs de haut) — animable.
Pack « Cimetière gothique / nécromancie », créature 2.

Animal modèle : le **cheval** — crâne très long et étroit, grandes orbites cerclées très en
arrière, encoche naso-incisive, crête faciale, énorme mandibule à angle arrondi, incisives en
peigne (ici changées en crocs), diastème ; jambes longues à canons et sabots.

Identité : os charbonneux gris-noir ; **aucune corne** : crinière et queue de **flammes
spectrales vert poison**, sabots en feu ferrés de fer ; **cercueil-selle** sanglé de chaînes sur
le dos avec bougies ; fers brisés aux paturons ; thème d'effets « nightmare ».

Pièces Roblox : corps, Head, Legs, + lumineux.
Os : Root, Hips, Chest, Neck1-2, Head, Jaw, Tail1-2, {Front,Hind}{Upper,Lower,Cannon,Hoof}_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.grave_lich_dragon import candle, chain

COLORS = {
    "bone": "#6e6873",
    "bone_shade": "#2f2b33",
    "tooth": "#e9e2cf",
    "horn": "#141216",
    "disc": "#1e1b21",
    "iron": "#45424a",
    "wood": "#3b2a24",
    "wax": "#e3dbc0",
    "gum": "#4a1f2a",
    "ink": "#060507",
    "glow": "#a6ff3d",
    "glow_hot": "#f2ffd6",
}

EFFECT_THEME = "nightmare"

TEST_POSE = {
    "Jaw": (-18, 0, 0),
    "FrontUpper_L": (-35, 0, 0),
    "FrontLower_L": (60, 0, 0),
    "Neck2": (-15, 0, 0),
    "Tail2": (0, 0, 25),
}

VIEW = (1.0, -0.8, 0.3)

SPINE = a.smooth_path([(0, 2.1, 3.55), (0, 1.0, 3.72), (0, -0.2, 3.78), (0, -1.1, 4.0)], 18)
NECK = a.smooth_path([(0, -1.1, 4.0), (0, -1.6, 4.65), (0, -2.0, 5.2), (0, -2.3, 5.55)], 9)
TAIL = a.smooth_path([(0, 2.15, 3.5), (0, 2.7, 3.35), (0, 3.0, 2.8), (0, 3.15, 2.1)], 12)
# Crâne de cheval dans son repère (occiput en 0, museau vers -Y)
SKULL = [(0.0, 0.18, 0.24, 0.2, 0.26, -0.12), (-0.4, 0.36, 0.43, 0.3, 0.33, -0.24),
         (-0.75, 0.32, 0.38, 0.28, 0.3, -0.3), (-1.2, 0.24, 0.3, 0.24, 0.22, -0.32),
         (-1.7, 0.18, 0.22, 0.18, 0.12, -0.3), (-2.1, 0.16, 0.19, 0.16, 0.05, -0.26),
         (-2.35, 0.15, 0.17, 0.14, 0.0, -0.22)]
EYE = (-0.48, 0.12)
HINGE = (0.3, -0.2, -0.05)
GAPE = math.radians(9)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = Matrix.Translation(NECK[-1] + Vector((0, -0.12, 0.05))) @ Matrix.Rotation(math.radians(48), 4, "X")
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def leg(prefix, s):
    if prefix == "Front":
        return (Vector((s * 0.45, -1.0, 3.45)), Vector((s * 0.52, -0.8, 2.55)),
                Vector((s * 0.45, -0.95, 1.35)), Vector((s * 0.42, -0.95, 0.42)),
                Vector((s * 0.42, -1.15, 0.1)))
    return (Vector((s * 0.5, 1.85, 3.35)), Vector((s * 0.56, 1.35, 2.45)),
            Vector((s * 0.5, 2.25, 1.55)), Vector((s * 0.45, 2.1, 0.42)),
            Vector((s * 0.45, 1.9, 0.1)))


def flame(rig, name, base, direction, length, bone, width=0.07, **kw):
    """Langue de flamme spectrale (lumineuse) recourbée."""
    rig.add(a.claw(name, base, direction, length, width, curl=-0.35, segments=4), bone, "glow",
            glow=True)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[8], "Root")
    rig.bone("Chest", SPINE[8], SPINE[-1], "Hips")
    rig.bone("Neck1", NECK[0], NECK[4], "Chest")
    rig.bone("Neck2", NECK[4], NECK[-1], "Neck1")
    rig.bone("Head", NECK[-1], HEAD_M @ Vector((0, -2.35, -0.1)), "Neck2")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE) * 1, HEAD_M @ (_jm @ Vector((0, -2.3, -0.32))), "Head")
    rig.bone("Tail1", TAIL[0], TAIL[5], "Hips")
    rig.bone("Tail2", TAIL[5], TAIL[-1], "Tail1")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, parent in (("Front", "Chest"), ("Hind", "Hips")):
            p = leg(prefix, s)
            prev = parent
            for k, nm in enumerate(("Upper", "Lower", "Cannon", "Hoof")):
                prev = rig.bone(f"{prefix}{nm}_{side}", p[k], p[k + 1], prev)
            rig.fx(f"{prefix}Hoof{side}", p[4] + Vector((0, 0, 0.1)), f"{prefix}Hoof_{side}")
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.3, EYE[0], EYE[1])), "Head")
    rig.fx("Nostrils", HEAD_M @ Vector((0, -2.3, -0.05)), "Head")
    rig.fx("Mane", NECK[4] + Vector((0, 0.2, 0.5)), "Neck1")
    rig.fx("Coffin", SPINE[8] + Vector((0, 0, 0.7)), "Chest")
    rig.fx("TailTip", TAIL[-1], "Tail2")


# ---------------------------------------------------------------- tête (repère local puis posée)

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.0, tip_length=0.15)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.15, 0.14),
                  a.hole_x((0, -0.12, 0.12), 0.12, 0.09),                 # fosse temporale
                  a.hole_x((0, -1.9, -0.1), 0.28, 0.07),                  # encoche naso-incisive
                  a.hole_x((0, -1.15, -0.05), 0.2, 0.06)])                # fenêtre faciale
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    rig.add(r.tube("NasalRidge", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in
                                  (-0.6, -1.1, -1.6, -2.05)], [0.05, 0.045, 0.04, 0.03], segments=4),
            H, "bone_shade", **HEAD)
    rig.add(r.ico("Poll", 0.12, subdivisions=1, location=(0, 0.02, 0.22), scale=(1.4, 1, 0.8)), H,
            "bone_shade", **HEAD)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.1, subdivisions=2, location=c0 - Vector((s * 0.08, 0, 0))), H,
                "glow", glow=True)
        # Barre post-orbitaire en anneau saillant (typique du cheval)
        rig.add(a.ring_around(f"OrbitRing{s}", c0 + Vector((s * 0.03, 0, 0)), (s, -0.3, 0.2), 0.17,
                              0.045, segments=12), H, "bone_shade", **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.18, -0.65, 0.3), (s * 0.4, -0.35, 0.3), 0.12, 0.05,
                        width_end=0.08, normal=(0, -0.2, 1)), H, "bone", **HEAD)
        # Crête faciale (arête latérale sous l'œil vers le museau)
        rig.add(r.tube(f"FacialCrest{s}", [(s * 0.4, -0.55, -0.08), (s * 0.34, -0.95, -0.12),
                                           (s * 0.27, -1.35, -0.14)], [0.05, 0.045, 0.03],
                       segments=4), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.42, -0.5, -0.02), (s * 0.4, -0.25, 0.0),
                                         (s * 0.3, -0.08, 0.05)], 0.045, segments=4), H, "bone",
                **HEAD)
        # Rangée du haut : prémolaires en bloc + croc (« crochet ») + incisives-crocs devant
        for k in range(5):
            y = -0.75 - 0.17 * k
            xx = s * a.side_width(SKULL, y, -0.3) * 0.85
            rig.add(mr.tooth(f"Molar{s}{k}", (xx, y, -0.3), (xx, y, -0.42), 0.13, 0.11,
                             Vector((s, 0, 0)), curl=0.0), H, "tooth", **HEAD)
        tusk = Vector((s * 0.15, -1.85, -0.26))
        rig.add(mr.tooth(f"Tush{s}", tusk, tusk + Vector((s * 0.02, -0.03, -0.24)), 0.1, 0.08,
                         Vector((s, 0, 0)), curl=0.1), H, "tooth", **HEAD)
        for k in range(3):
            p = Vector((s * (0.04 + 0.05 * k), -2.36 + 0.03 * k, -0.2))
            rig.add(mr.tooth(f"Incisor{s}{k}", p, p + Vector((0, -0.05, -0.16 + 0.02 * k)), 0.07, 0.06,
                             Vector((0, -1, 0)), curl=0.1), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * 0.2, -0.7, -0.29), (s * 0.18, -1.5, -0.28),
                                        (s * 0.12, -2.3, -0.2)], 0.035, segments=4), H, "gum", **HEAD)
        # Naseau fumant
        rig.add(a.ring_around(f"NostrilRim{s}", (s * 0.12, -2.25, 0.0), (s * 0.3, -1, 0.3), 0.06,
                              0.02, segments=8), H, "bone_shade", **HEAD)
    # Mandibule : branche montante large à angle arrondi + corps fin vers les incisives
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        angle = [Vector((s * 0.32, -0.15, -0.05)), Vector((s * 0.34, -0.12, -0.4)),
                 Vector((s * 0.33, -0.3, -0.68)), Vector((s * 0.3, -0.6, -0.72))]
        rig.add(r.tube(f"JawAngle{s}", [tuple(p) for p in a.smooth_path(angle, 7)],
                       [0.08, 0.09, 0.1, 0.1, 0.09, 0.08, 0.08], segments=6), J, "bone", **HEAD)
        rig.add(a.blade(f"Ramus{s}", (s * 0.32, -0.45, -0.6), (s * 0.31, -0.3, -0.08), 0.26, 0.05,
                        width_end=0.14, normal=(1, 0, 0), bevel=0), J, "bone_shade", **HEAD)
        body = [Vector((s * 0.3, -0.6, -0.7)), Vector((s * 0.24, -1.2, -0.56)),
                Vector((s * 0.17, -1.8, -0.44)), Vector((s * 0.1, -2.3, -0.34))]
        rig.add(a.band(f"Mandible{s}", body, [0.3, 0.22, 0.17, 0.14], [0.09, 0.08, 0.07, 0.06],
                       offset=0), J, "bone", **HEAD)
        rig.add(a.claw(f"Coronoid{s}", (s * 0.31, -0.35, -0.15), (0, 0.2, 1), 0.3, 0.05, curl=0.2,
                       segments=4), J, "bone_shade", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.07, subdivisions=1, location=(s * 0.33, -0.15, -0.05)), H,
                "bone_shade", **HEAD)
        for k in range(5):
            y = -0.8 - 0.17 * k
            p = mr.along(body, 0.08 + 0.14 * k) + Vector((-s * 0.04, 0, 0))
            p.z = body[0].z + 0.3 - (0.3 - 0.17) * (k / 4) - 0.02
            rig.add(mr.tooth(f"LowMolar{s}{k}", p, p + Vector((0, 0, 0.11)), 0.12, 0.1,
                             Vector((s, 0, 0)), curl=0.0), J, "tooth", **HEAD)
        for k in range(3):
            p = Vector((s * (0.04 + 0.05 * k), -2.33 + 0.03 * k, -0.22))
            rig.add(mr.tooth(f"LowIncisor{s}{k}", p, p + Vector((0, -0.04, 0.15)), 0.06, 0.05,
                             Vector((0, -1, 0)), curl=0.1), J, "tooth", **HEAD)
        tusk = Vector((s * 0.12, -1.95, -0.24))
        rig.add(mr.tooth(f"LowTush{s}", tusk, tusk + Vector((s * 0.02, 0, 0.2)), 0.08, 0.07,
                         Vector((s, 0, 0)), curl=0.1), J, "tooth", **HEAD)
    rig.add(r.ico("Chin", 0.1, subdivisions=2, location=(0, -2.3, -0.3), scale=(1.4, 1, 0.8)), J,
            "bone", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    rig.add(r.ico("Throat", 0.12, subdivisions=2, location=(0, -0.9, -0.35), scale=(1.2, 2.5, 0.6)), H,
            "glow", glow=True)
    # Bride brisée : anneau de mors et chaîne pendante
    for s in (-1, 1):
        rig.add(a.ring_around(f"Bit{s}", (s * 0.2, -1.95, -0.35), (1, 0, 0), 0.08, 0.025,
                              segments=8), H, "iron", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    # Crinière de flammes spectrales posée sur le haut de la tête
    for k in range(3):
        p = HEAD_M @ Vector((0, 0.05 - 0.15 * k, 0.28))
        flame(rig, f"Forelock{k}", p, (0, 0.3 + 0.2 * k, 1), 0.45 - 0.08 * k, "Head", width=0.06)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        side, up = a._basis(t)
        bone = "Hips" if i < 8 else "Chest"
        withers = max(0.0, (i - 10) / (n - 10))
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.25, spine=1.3 + 1.6 * withers, lean=0.5), bone,
                "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.25), bone, "disc")
    # Grande cage en tonneau, profonde et étroite (cheval), sternum
    sternum = []
    for k, i in enumerate(range(5, n - 1)):
        f = k / (n - 7)
        hw = 0.55 + 0.25 * math.sin(math.pi * (0.3 + 0.6 * (1 - f)))
        depth = 1.0 + 0.45 * f
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.06),
                    "Hips" if i < 8 else "Chest", "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[::2], 0.1, 0.35), "Chest", "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.5), (0.12, 0.35), (-0.12, 0.38))):
        rig.add(a.crystal(f"SoulHeart{k}", (dx, -0.4, 3.0), 0.12 if k == 0 else 0.08, h, sides=4),
                "Chest", "glow", glow=True)
    # Cou : vertèbres + crinière de flammes spectrales en mèches séparées
    for i in range(len(NECK)):
        t = tangent(NECK, i)
        side, up = a._basis(t)
        bone = "Neck1" if i < 4 else "Neck2"
        rig.add(a.vertebra(f"NeckVert{i}", NECK[i], t, 0.24, spine=0.9, lean=0.3), bone, "bone")
        if i < len(NECK) - 1:
            rig.add(a.disc(f"NeckDisc{i}", NECK[i].lerp(NECK[i + 1], 0.5), t, 0.24), bone, "disc")
        flame(rig, f"Mane{i}", NECK[i] + up * 0.3 + side * 0.05 * (-1) ** i, up * 0.6 + Vector((0, 1, 0)),
              0.55 + 0.1 * (i % 2), bone)
    # Épaules, bassin
    for s in (-1, 1):
        sh = leg("Front", s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[-3] + Vector((s * 0.3, 0.1, 0.25)), sh, 0.45, 0.06,
                        width_end=0.25, mid=0.5, normal=(s, 0, 0.3)), "Chest", "bone")
        hp = leg("Hind", s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[2] + Vector((s * 0.25, -0.3, 0.1)), hp + Vector((s * 0.05, 0, 0.1)),
                        0.5, 0.07, width_end=0.3, mid=0.55, normal=(s, 0, 0.6)), "Hips", "bone")
        rig.add(a.long_bone(f"Ischium{s}", hp, (s * 0.25, 2.35, 3.0), 0.07, condyles=False, segments=5),
                "Hips", "bone")
    # Queue : vertèbres + panache de flammes
    for i in range(len(TAIL)):
        t = tangent(TAIL, i)
        bone = "Tail1" if i < 5 else "Tail2"
        size = 0.15 - 0.08 * i / (len(TAIL) - 1)
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=0.8, lean=0.4), bone, "bone")
        if i % 2 == 1:
            flame(rig, f"TailFlame{i}", TAIL[i], t + Vector((0, 0.4, -0.3)), 0.5 + 0.05 * i, bone)
    # Cercueil-selle sanglé de chaînes, deux bougies sur le couvercle
    cc = SPINE[9] + Vector((0, 0, 0.55))
    outline = [(-0.22, 0.75), (0.22, 0.75), (0.36, 0.35), (0.26, -0.75), (-0.26, -0.75), (-0.36, 0.35)]
    rig.add(r.loft("Coffin", [[(cc.x + x, cc.y - yy, cc.z + dz) for x, yy in outline]
                              for dz in (-0.12, 0.12)]), "Chest", "wood")
    rig.add(r.loft("CoffinLid", [[(cc.x + x * 0.85, cc.y - yy * 0.9, cc.z + dz) for x, yy in outline]
                                 for dz in (0.12, 0.16)]), "Chest", "iron")
    rig.add(a.crystal("CoffinSoul", cc + Vector((0, -0.2, 0.2)), 0.07, 0.25, sides=4), "Chest", "glow",
            glow=True)
    for k, dy in enumerate((-0.4, 0.45)):
        candle(rig, f"CoffinCandle{k}", cc + Vector((0.12 * (-1) ** k, dy, 0.16)), 0.2 + 0.06 * k, "Chest")
        for s in (-1, 1):
            chain(rig, f"Strap{k}{s}", cc + Vector((s * 0.33, dy * 0.6, 0)),
                  SPINE[9 + k * 2] + Vector((s * 0.7, -0.2, -1.0)), "Chest", sag=-0.1, radius=0.06)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix in ("Front", "Hind"):
            p = leg(prefix, s)
            names = [f"{prefix}{nm}_{side}" for nm in ("Upper", "Lower", "Cannon", "Hoof")]
            rig.add(a.long_bone(f"{prefix}Upper{s}", p[0], p[1], 0.15, segments=7), names[0], "bone",
                    **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower{s}", p[1], p[2], 0.11, segments=7), names[1], "bone",
                    **LEGS)
            rig.add(r.ico(f"{prefix}Joint{s}", 0.13, subdivisions=1, location=p[2], scale=(1, 0.9, 1.2)),
                    names[1], "bone_shade", **LEGS)
            rig.add(a.long_bone(f"{prefix}Cannon{s}", p[2], p[3], 0.08, segments=6), names[2], "bone",
                    **LEGS)
            if prefix == "Front":
                rig.add(a.claw(f"Olecranon{s}", p[1], (0, 0.6, 0.6), 0.25, 0.07, curl=0, segments=4),
                        names[1], "bone_shade", **LEGS)
            else:
                rig.add(a.claw(f"HockPoint{s}", p[2], (0, 1, 0.5), 0.25, 0.07, curl=0, segments=4),
                        names[1], "bone_shade", **LEGS)
            # Paturon, sabot noir ferré, fer brisé + flammes autour du sabot
            rig.add(a.long_bone(f"{prefix}Pastern{s}", p[3], p[4] + Vector((0, 0, 0.12)), 0.065,
                                condyles=False, segments=5), names[3], "bone", **LEGS)
            rig.add(r.tube(f"{prefix}HoofHorn{s}", [tuple(p[4] + Vector((0, 0.04, 0.15))),
                                                    tuple(p[4] + Vector((0, -0.03, -0.08)))],
                           [0.09, 0.17], segments=8), names[3], "horn", **LEGS)
            rig.add(a.ring_around(f"{prefix}Shoe{s}", p[4] + Vector((0, -0.03, -0.07)), (0, 0, 1), 0.17,
                                  0.03, segments=10), names[3], "iron", **LEGS)
            rig.add(a.ring_around(f"{prefix}Shackle{s}", p[3] + Vector((0, 0, 0.12)), (0, 0, 1), 0.11,
                                  0.03, segments=8), names[2], "iron", **LEGS)
            for j in range(2):
                q = p[3] + Vector((s * 0.12, 0.05 * j, -0.05 - 0.14 * j))
                rig.add(a.ring_around(f"{prefix}ShackleLink{s}{j}", q, (1, 0, 0) if j % 2 else (0, 1, 0),
                                      0.06, 0.02, segments=8), names[2], "iron", **LEGS)
            for j in range(4):
                ang = 2 * math.pi * j / 4 + 0.4
                d = Vector((math.cos(ang), math.sin(ang), 0))
                flame(rig, f"{prefix}HoofFire{s}{j}", p[4] + d * 0.16 + Vector((0, 0, 0.05)),
                      d * 0.3 + Vector((0, 0, 1)), 0.3, names[3], width=0.05)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
