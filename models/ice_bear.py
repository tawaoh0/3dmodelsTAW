"""Ours polaire titan squelette (≈ 5 studs au garrot, 7,5 de long) — créature animable.
Pack « Royaume de glace éternelle », créature 4.

Animal modèle : l'ours blanc — crâne long et bas au front plat, long museau, crête
sagittale, arcades zygomatiques larges, grosses canines ; long cou, corps massif, pattes
**plantigrades** (marche sur toute la plante) aux larges pattes, queue courte.

Identité : os blanc neige ; pas de cornes mais une **armure de plaques de glacier** sur le
garrot, le dos et les épaules + crinière de pics de glace sur le cou ; **griffes de glace**
géantes ; gueule ouverte en rugissement ; cœur de nuit polaire violet ; thème d'effets
« polar » (souffle glacé + gros flocons).

4 pièces Roblox : corps, Head, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, Tail, Front/Hind{Upper,Lower,Paw}_{L,R}, FX_*.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r
from models.ice_mammoth import frost, icicle

COLORS = {
    "bone": "#eef2f5",
    "bone_shade": "#6f8296",
    "tooth": "#fffaf0",
    "horn": "#1d2230",
    "horn_tip": "#c7a0ff",
    "disc": "#3a4250",
    "ice": "#bfe6ff",
    "ice_deep": "#5f9fd6",
    "gum": "#5a2434",
    "ink": "#0c0e14",
    "glow": "#c7a0ff",
    "glow_hot": "#f3e8ff",
}

EFFECT_THEME = "polar"

TEST_POSE = {
    "Jaw": (-15, 0, 0),
    "Head": (12, 0, 0),
    "FrontUpper_L": (-35, 0, 0),
    "FrontLower_L": (40, 0, 0),
    "Neck": (0, 0, 15),
}

VIEW = (0.95, -0.95, 0.4)

# Dos d'ours : grosse bosse au garrot, croupe plus basse, tête portée bas
SPINE = a.smooth_path([(0, 2.3, 3.8), (0, 1.0, 4.2), (0, -0.3, 4.65), (0, -1.0, 4.35)], 22)
NECK = a.smooth_path([(0, -1.0, 4.35), (0, -1.55, 3.95), (0, -2.05, 3.5)], 7)
TAIL = a.smooth_path([(0, 2.35, 4.0), (0, 2.75, 3.75), (0, 2.95, 3.45)], 6)
# Crâne d'ours blanc : (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
# Crâne d'ours : large et massif, front plat et large, petits yeux, museau court, large
# et carré (≠ tigre : long museau fin, grande gueule)
SKULL = [(-2.0, 0.52, 0.68, 0.52, 4.2, 3.45), (-2.4, 0.62, 0.8, 0.64, 4.38, 3.4),
         (-2.8, 0.55, 0.7, 0.6, 4.32, 3.42), (-3.2, 0.44, 0.54, 0.5, 4.12, 3.42),
         (-3.55, 0.41, 0.49, 0.46, 4.0, 3.44), (-3.72, 0.39, 0.45, 0.42, 3.94, 3.46)]
EYE = (-2.88, 4.12)
HINGE = (0.55, -2.45, 3.42)
GAPE = math.radians(14)        # grondement, gueule à peine entrouverte
HEAD_DROP = Vector((0, 0, -0.35))   # la tête est portée bas, sous la bosse des épaules
_m = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
      @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
CHIN = tuple(_m @ Vector((0, -3.72, 3.38)) + HEAD_DROP)
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def front_leg(s):
    """Patte avant d'ours : colonne massive, poignet presque au sol, longue paume à plat."""
    return (Vector((s * 1.0, -0.85, 4.0)), Vector((s * 1.1, -0.6, 2.2)),
            Vector((s * 1.1, -0.8, 0.38)), Vector((s * 1.1, -1.45, 0.13)))


def hind_leg(s):
    """Patte arrière plantigrade : talon posé au sol, longue plante jusqu'aux doigts."""
    return (Vector((s * 0.85, 2.1, 3.55)), Vector((s * 0.95, 1.55, 2.0)),
            Vector((s * 0.95, 1.9, 0.33)), Vector((s * 0.95, 1.05, 0.13)))


def ice_plate(rig, name, base, up, along, bone, size=0.5, **kw):
    """Plaque de glacier en écaille : lame épaisse posée sur l'os, bord relevé."""
    base, up, along = Vector(base), Vector(up).normalized(), Vector(along).normalized()
    tip = base + up * size * 0.5 + along * size * 0.8
    rig.add(a.blade(name, base, tip, size * 0.7, size * 0.14, width_end=size * 0.25,
                    mid=size * 0.8, normal=up), bone,
            "ice" if sum(map(ord, name)) % 2 else "ice_deep", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], Vector((0, -3.75, 3.7)) + HEAD_DROP, "Neck")
    rig.bone("Jaw", Vector((0, HINGE[1], HINGE[2])) + HEAD_DROP, (0, CHIN[1], CHIN[2]), "Head")
    rig.bone("Tail", TAIL[0], TAIL[-1], "Spine1")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Spine3"), ("Hind", hind_leg(s), "Spine1")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Paw_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
        rig.fx(f"Eye{side}", Vector((s * 0.5, EYE[0], EYE[1])) + HEAD_DROP, "Head")
        rig.fx(f"Claws{side}", front_leg(s)[3] + Vector((0, -0.4, 0)), f"FrontPaw_{side}")
    rig.fx("Heart", (0, -0.2, 3.3), "Spine2")
    rig.fx("Breath", Vector((0, -3.85, 3.6)) + HEAD_DROP, "Head")
    rig.fx("Back", SPINE[11] + Vector((0, 0, 0.9)), "Spine2")


# ---------------------------------------------------------------- tête

def build_head(rig):
    before = {o.name for o in bpy.context.scene.objects}
    build_skull(rig)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(Matrix.Translation(HEAD_DROP) @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


def build_skull(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.12)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.1, 0.1),
                  a.hole_x((0, -2.4, 3.85), 0.25, 0.17),
                  a.hole_along((0, -3.85, 3.68), (0, 1, 0), (1, 0, 0), 0.22, 0.18, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    crest = [top(0, y) for y in (-2.05, -2.3, -2.6, -2.85)]
    rig.add(a.band("Sagittal", crest, [0.18, 0.2, 0.12, 0.04], 0.06, offset=0.15), H,
            "bone_shade", **HEAD)
    rig.add(r.tube("Nuchal", [(-0.4, -2.02, 3.95), (0, -1.95, 4.2), (0.4, -2.02, 3.95)], 0.05,
                   segments=5), H, "bone_shade", **HEAD)
    rig.add(a.ring_around("NasalRim", (0, -3.88, 3.68), (0, -1, 0), 0.24, 0.05, segments=12), H,
            "bone_shade", **HEAD)
    frost(rig, "BrowFrost", top(0, -2.75), (0, 0.4, 1), H, n=4, size=0.16, **HEAD)
    # Masque de glacier : plaques de glace en écailles sur le front et le chanfrein
    for k, (x, y, size) in enumerate(((0, -2.35, 0.5), (0.25, -2.5, 0.36), (-0.25, -2.5, 0.36),
                                      (0, -3.2, 0.38), (0.15, -3.55, 0.28), (-0.15, -3.55, 0.28))):
        p = top(x, y)
        if p is not None:
            ice_plate(rig, f"Mask{k}", p - Vector((0, 0, 0.04)), (x * 1.5, 0.2, 1), (0, 1, 0.15), H,
                      size=size, **HEAD)
    for s in (-1, 1):   # pics de givre sur les joues
        for k in range(3):
            rig.add(a.claw(f"CheekIce{s}{k}", (s * 0.6, -2.35 - 0.2 * k, 3.6 - 0.05 * k),
                           (s, 0.4, -0.2), 0.3 - 0.05 * k, 0.045, curl=-0.1, segments=4), H, "ice",
                    **HEAD)
    for s in (-1, 1):
        nasal = [top(s * 0.1, y) for y in (-3.0, -3.45, -3.85)]
        rig.add(r.tube(f"Nasal{s}", [tuple(p + Vector((0, 0, 0.015))) for p in nasal],
                       [0.04, 0.045, 0.04], segments=4), H, "bone_shade", **HEAD)
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.07, subdivisions=2, location=c0 - Vector((s * 0.05, 0, 0))), H,
                "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", c0, (s, -0.3, 0.1), 0.11, H, spikes=4, color="ice",
                       **HEAD)
        zyg = a.smooth_path([(s * 0.62, -2.1, 3.55), (s * 0.98, -2.5, 3.62), (s * 0.6, -3.0, 3.65)], 5)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg], [0.08, 0.11, 0.12, 0.1, 0.08],
                       segments=5), H, "bone", **HEAD)
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.32, -2.75, 4.2), (s * 0.55, -2.8, 3.85)], 0.04,
                       segments=4), H, "bone_shade", **HEAD)
        for k in range(5):
            y = -3.55 - 0.07 * k
            rig.add(r.ico(f"Whisker{s}{k}", 0.025, subdivisions=1,
                          location=(s * a.side_width(SKULL, y, 3.62 + 0.04 * (k % 2)) * 1.02, y,
                                    3.62 + 0.04 * (k % 2))), H, "ink", **HEAD)
        mr.scar(rig, f"FrostCrack{s}", top(s * 0.22, -2.1), top(s * 0.3, -2.6), H, width=0.04,
                seed=s)
        # Rangée du haut : incisives, grosse canine, prémolaires, molaires larges
        for k in range(3):
            p = Vector((s * (0.07 + 0.08 * k), -3.76 + 0.03 * k, 3.48))
            rig.add(mr.tooth(f"UpIncisor{s}{k}", p, p + Vector((0, -0.02, -0.14)), 0.07, 0.05,
                             Vector((s * 0.3, -1, 0))), H, "tooth", **HEAD)
        p = Vector((s * 0.33, -3.58, 3.46))
        rig.add(mr.tooth(f"UpCanine{s}", p, p + Vector((s * 0.02, -0.04, -0.34)), 0.17, 0.13,
                         Vector((s, -0.5, 0)), curl=0.15), H, "tooth", **HEAD)
        # (diastème après la canine, puis grosses molaires broyeuses plates d'omnivore)
        for k, (y, size, w) in enumerate(((-3.2, 0.08, 0.08), (-2.98, 0.11, 0.2), (-2.75, 0.11, 0.24),
                                          (-2.52, 0.1, 0.24))):
            p = Vector((s * a.side_width(SKULL, y, 3.45) * 0.86, y, 3.44))
            rig.add(mr.tooth(f"UpCheek{s}{k}", p, p + Vector((0, 0, -size)), w, w * 0.6,
                             Vector((s, 0, 0)), curl=0.02), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * 0.22, -3.72, 3.48), (s * 0.38, -3.3, 3.46),
                                        (s * 0.5, -2.55, 3.44)], 0.05, segments=4), H, "gum",
                **HEAD)
    build_jaw(rig)
    rig.add(r.ico("Throat", 0.22, subdivisions=2, location=(0, -2.75, 3.4), scale=(1.4, 1.8, 0.6)),
            H, "glow", glow=True)


def build_jaw(rig):
    """Mandibule modélisée fermée puis ouverte d'un bloc (rugissement)."""
    J = "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.5, -2.95, 3.38)),
                Vector((s * 0.38, -3.4, 3.38)), Vector((s * 0.16, -3.72, 3.38))]
        hs = [0.42, 0.38, 0.34, 0.32]
        rig.add(a.band(f"Dentary{s}", line, hs, [0.17, 0.16, 0.14, 0.13], offset=1), J, "bone",
                **HEAD)
        rig.add(r.tube(f"DentaryRidge{s}", [tuple(p + Vector((s * 0.09, 0, -h * 0.55)))
                                            for p, h in zip(line, hs)], 0.04, segments=4), J,
                "bone_shade", **HEAD)
        rig.add(r.tube(f"DentaryBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.04, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.15, 0)),
                        line[0] + Vector((0, -0.05, 0.35)), 0.2, 0.07, width_end=0.1,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.1, subdivisions=1, location=line[0]), "Head", "bone_shade",
                **HEAD)
        for k in range(3):
            p = line[3] + Vector((-s * 0.03 * k, 0.02 * k, 0))
            rig.add(mr.tooth(f"LowIncisor{s}{k}", p, p + Vector((0, -0.03, 0.12)), 0.06, 0.04,
                             Vector((s * 0.3, -1, 0))), J, "tooth", **HEAD)
        p = mr.along(line, 0.85)
        rig.add(mr.tooth(f"LowCanine{s}", p, p + Vector((s * 0.03, -0.03, 0.3)), 0.16, 0.12,
                         Vector((s, -0.5, 0)), curl=0.15), J, "tooth", **HEAD)
        for k, (t, size, w) in enumerate(((0.5, 0.1, 0.2), (0.35, 0.1, 0.24), (0.2, 0.1, 0.24))):
            p = mr.along(line, t)
            rig.add(mr.tooth(f"LowCheek{s}{k}", p, p + Vector((0, 0, size)), w, w * 0.6,
                             Vector((s, 0, 0)), curl=0.02), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.03, 0, 0.02))) for p in line[1:]],
                       0.04, segments=4), J, "gum", **HEAD)
        for k in range(2):
            rig.add(r.ico(f"MentalPore{s}{k}", 0.03, subdivisions=1,
                          location=mr.along(line, 0.6 + 0.15 * k) + Vector((s * 0.07, 0, -0.13))),
                    J, "ink", **HEAD)
    rig.add(r.ico("ChinKnob", 0.13, subdivisions=1, location=(0, -3.74, 3.1)), J, "bone_shade",
            **HEAD)
    for k in range(3):
        icicle(rig, f"ChinIcicle{k}", (0.1 * (k - 1), -3.68 + 0.1 * abs(k - 1), 3.02), 0.28, J,
               **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(_m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for path, bonef, size in ((SPINE, spine_bone, 0.3), (NECK, lambda i: "Neck", 0.25)):
        for i in range(len(path)):
            t = tangent(path, i)
            hump = path is SPINE and 13 <= i <= 19      # bosse de garrot de l'ours
            rig.add(a.vertebra(f"Vert{size}{i}", path[i], t, size * (1.1 if hump else 1),
                               spine=2.6 if hump else 1.4, lean=0.6 if hump else 0.45),
                    bonef(i), "bone")
            if i < len(path) - 1:
                rig.add(a.disc(f"Disc{size}{i}", path[i].lerp(path[i + 1], 0.5), t, size),
                        bonef(i), "disc")
    # Crinière de pics de glace sur le cou
    for i in range(len(NECK)):
        side, up = a._basis(tangent(NECK, i))
        for k, sd in enumerate((-1, 1)):
            rig.add(a.claw(f"NeckIce{i}{k}", NECK[i] + up * 0.3 + side * sd * 0.12,
                           up + side * sd * 0.4 + Vector((0, 0.5, 0)), 0.45 - 0.03 * i, 0.05,
                           curl=-0.1, segments=4), "Neck", "ice" if (i + k) % 2 else "ice_deep")
    # Armure de plaques de glacier sur le garrot et le dos (écailles qui se chevauchent)
    for i in range(3, len(SPINE) - 1, 2):
        side, up = a._basis(tangent(SPINE, i))
        for sd in (-1, 0, 1):
            base = SPINE[i] + up * 0.42 + side * sd * 0.32
            ice_plate(rig, f"BackPlate{i}{sd}", base, up + side * sd * 0.6,
                      Vector((0, 1, 0)), spine_bone(i), size=0.55 if sd == 0 else 0.42)
    # Cage massive, sternum, cœur de nuit polaire
    sternum = []
    for k, i in enumerate(range(6, 20)):
        hw = 1.1 + 0.35 * math.sin(math.pi * k / 13)
        depth = 1.5 + 0.5 * math.sin(math.pi * (k + 2) / 16)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.09),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[1:-1:2], 0.12, 0.6), "Spine2", "bone_shade")
    for k, p in enumerate(sternum[2:-1:3]):
        icicle(rig, f"BellyIcicle{k}", p - Vector((0, 0, 0.06)), 0.45, "Spine2")
    for k, (dx, dy, h) in enumerate(((0, -0.2, 0.9), (0.22, 0.0, 0.6), (-0.22, -0.4, 0.65),
                                     (0.1, 0.3, 0.5))):
        rig.add(a.crystal(f"PolarHeart{k}", (dx, dy, 2.95), 0.13 if k == 0 else 0.09, h, sides=6),
                "Spine2", "glow", glow=True)
    # Ceintures, plaques d'épaule, queue
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[17] + Vector((s * 0.3, 0, 0.1)),
                        sh + Vector((0, 0.05, 0.05)), 0.75, 0.1, width_end=0.35, mid=0.8,
                        normal=(s, 0, 0.4)), "Spine3", "bone")
        ice_plate(rig, f"ShoulderPlate{s}", sh + Vector((s * 0.2, 0.1, 0.3)), (s, 0, 1),
                  (0, 1, -0.3), "Spine3", size=0.7)
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.2, 0, 0.1)),
                        hp + Vector((s * 0.2, -0.3, 0.5)), 0.6, 0.1, width_end=0.45, mid=0.7,
                        normal=(s, 0, 0.4)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.35, 1.8, 3.15), (0, 1.85, 3.1)], 0.08,
                       segments=5), "Spine1", "bone")
    for i in range(len(TAIL)):
        t = tangent(TAIL, i)
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, 0.15 - 0.015 * i, spine=0.8,
                           transverse=False), "Tail", "bone")
    icicle(rig, "TailIcicle", TAIL[-1] - Vector((0, 0, 0.08)), 0.3, "Tail")


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts in (("Front", front_leg(s)), ("Hind", hind_leg(s))):
            ub, lb, pb = f"{prefix}Upper_{side}", f"{prefix}Lower_{side}", f"{prefix}Paw_{side}"
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.25, segments=8), ub, "bone",
                    **LEGS)
            off = (pts[2] - pts[1]).cross(Vector((0, 0, 1))).normalized() * 0.12
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1] + off, pts[2] + off, 0.19,
                                segments=7), lb, "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] - off, pts[2] - off, 0.1,
                                condyles=False, segments=6), lb, "bone_shade", **LEGS)
            rig.add(a.ring_around(f"{prefix}Joint{s}", pts[1], pts[2] - pts[1], 0.24, 0.04,
                                  segments=10), lb, "glow", glow=True)
            rig.add(r.ico(f"{prefix}Carpus{s}", 0.2, subdivisions=1, location=pts[2],
                          scale=(1.2, 1, 0.8)), pb, "bone_shade", **LEGS)
            # Patte plantigrade large : 5 doigts à plat, énormes griffes de glace
            lat = Vector((s, 0, 0))
            for j in range(5):
                off_j = (j - 2) * 0.16
                m1 = pts[3] + lat * off_j + Vector((0, 0, 0.02))
                rig.add(a.long_bone(f"{prefix}Meta{s}{j}", pts[2] + lat * off_j * 0.6, m1, 0.06,
                                    condyles=False, segments=5), pb, "bone", **LEGS)
                toe = m1 + Vector((lat.x * off_j * 0.25, -0.28, -0.03))
                rig.add(a.long_bone(f"{prefix}Toe{s}{j}", m1, toe, 0.05, condyles=False,
                                    segments=5), pb, "bone", **LEGS)
                claw_len = (0.55 if prefix == "Front" else 0.4) * (1 - 0.15 * abs(j - 2) / 2)
                rig.add(a.claw(f"{prefix}IceClaw{s}{j}", toe, (0, -1, -0.35), claw_len, 0.07,
                               curl=0.4, segments=5), pb, "ice", **LEGS)
            frost(rig, f"{prefix}ElbowFrost{s}", pts[1] + Vector((0, 0.12 if prefix == "Front" else -0.15,
                                                                  0.05)),
                  (0, 1 if prefix == "Front" else -1, 0.4), lb, n=3, size=0.16, **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
