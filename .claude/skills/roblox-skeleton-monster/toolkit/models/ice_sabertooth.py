"""Tigre à dents de sabre squelette (≈ 3,5 studs au garrot, bondissant) — créature animable.
Pack « Royaume de glace éternelle », créature 2.

Animal modèle : le Smilodon — crâne court et haut, crête sagittale, arcades zygomatiques
larges, orbites tournées vers l'avant, grande ouverture nasale, **canines supérieures
démesurées** en lames aplaties et dentelées, mâchoire capable de s'ouvrir à 120° avec une
**bride mentonnière** qui protège les sabres ; corps de félin puissant, queue courte.

Identité : os gris argent **rayés de bandes de glace bleu nuit** (rayures de tigre) ;
pas de cornes mais les sabres et des arêtes de givre sur les épaules ; vrai tigre à quatre
pattes, long museau, grande gueule ouverte, longue queue ; cœur de glace bleu ;
thème d'effets « blizzard » (neige soufflée).

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

COLORS = {
    "bone": "#c2c6cf",
    "bone_shade": "#7d8494",
    "stripe": "#2f4f7a",
    "tooth": "#eef4f7",
    "horn": "#1b1e26",
    "horn_tip": "#3fa9ff",
    "disc": "#2a3240",
    "ice": "#bfe6ff",
    "gum": "#5a2030",
    "ink": "#0b0d12",
    "glow": "#3fa9ff",
    "glow_hot": "#d8f0ff",
}

EFFECT_THEME = "blizzard"

TEST_POSE = {
    "Jaw": (-20, 0, 0),
    "Head": (15, 0, 0),
    "FrontUpper_L": (-30, 0, 0),
    "HindUpper_R": (-25, 0, 0),
    "Tail": (0, 0, 30),
}

VIEW = (1.0, -0.85, 0.35)

# Tigre debout sur ses quatre pattes, dos droit, longue queue
SPINE = a.smooth_path([(0, 2.4, 2.6), (0, 1.3, 2.82), (0, 0.1, 2.92), (0, -0.7, 2.82)], 22)
NECK = a.smooth_path([(0, -0.7, 2.8), (0, -1.0, 2.98), (0, -1.22, 3.1)], 5)
TAIL = a.smooth_path([(0, 2.45, 2.6), (0, 3.3, 2.4), (0, 4.0, 1.8), (0, 4.55, 1.35),
                      (0.15, 5.1, 1.5), (0.25, 5.45, 1.85)], 22)
# Crâne de tigre (Smilodon) : grand, museau long et large, truffe arrondie
# (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-1.2, 0.4, 0.5, 0.4, 3.6, 2.95), (-1.55, 0.52, 0.62, 0.5, 3.82, 2.9),
         (-1.9, 0.46, 0.58, 0.5, 3.72, 2.9), (-2.25, 0.35, 0.44, 0.42, 3.5, 2.93),
         (-2.6, 0.31, 0.39, 0.38, 3.36, 2.95), (-2.85, 0.29, 0.35, 0.34, 3.26, 2.97)]
EYE = (-1.95, 3.45)
HINGE = (0.45, -1.45, 2.92)
CHIN_CLOSED = (0.0, -2.8, 2.85)
GAPE = math.radians(55)         # gueule ouverte (posture d'attaque) : rotation autour de la charnière
_m = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
      @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
CHIN = tuple(_m @ Vector(CHIN_CLOSED))
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def front_leg(s):
    """Patte avant de tigre : coude vers l'arrière, poignet souple, doigts au sol."""
    return (Vector((s * 0.5, -0.5, 2.55)), Vector((s * 0.56, -0.25, 1.55)),
            Vector((s * 0.55, -0.6, 0.45)), Vector((s * 0.55, -0.85, 0.12)))


def hind_leg(s):
    """Patte arrière : genou vers l'avant, jarret haut vers l'arrière, digitigrade."""
    return (Vector((s * 0.5, 2.3, 2.45)), Vector((s * 0.6, 1.7, 1.5)),
            Vector((s * 0.6, 2.45, 0.7)), Vector((s * 0.6, 2.15, 0.12)))


def stripes(rig, name, a_pt, b_pt, radius, bone, n=2, **kw):
    """Rayures de tigre : bandes de glace bleu nuit autour d'un os long."""
    a_pt, b_pt = Vector(a_pt), Vector(b_pt)
    for k in range(n):
        t = (k + 1) / (n + 1)
        rig.add(a.ring_around(f"{name}{k}", a_pt.lerp(b_pt, t), b_pt - a_pt, radius * 1.05,
                              radius * 0.35, segments=8), bone, "stripe", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE)
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[-1], "Spine2")
    rig.bone("Neck", NECK[0], NECK[-1], "Spine3")
    rig.bone("Head", NECK[-1], (0, -2.95, 3.2), "Neck")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    rig.bone("Tail", TAIL[0], TAIL[11], "Spine1")
    rig.bone("Tail2", TAIL[11], TAIL[-1], "Tail")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Spine3"), ("Hind", hind_leg(s), "Spine1")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Paw_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
        rig.fx(f"Eye{side}", (s * 0.35, EYE[0], EYE[1]), "Head")
        rig.fx(f"Saber{side}", (s * 0.27, -2.68, 2.0), "Head")
    rig.fx("Heart", (0, -0.2, 2.1), "Spine2")
    rig.fx("Mouth", (0, -2.0, 2.7), "Head")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.15)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.15, 0.14),
                  a.hole_x((0, -1.5, 3.2), 0.2, 0.15),
                  a.hole_along((0, -2.98, 3.13), (0, 1, 0), (1, 0, 0), 0.14, 0.12, depth=0.3)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Crête sagittale haute, crête nucale, rayures de glace sur le crâne
    crest = [top(0, y) for y in (-1.2, -1.45, -1.75, -2.05)]
    rig.add(a.band("Sagittal", crest, [0.22, 0.26, 0.16, 0.05], 0.06, offset=0.15), H,
            "bone_shade", **HEAD)
    rig.add(r.tube("Nuchal", [(-0.35, -1.22, 3.4), (0, -1.15, 3.6), (0.35, -1.22, 3.4)], 0.05,
                   segments=5), H, "bone_shade", **HEAD)
    for k, y in enumerate((-1.4, -1.65, -2.15, -2.4, -2.65)):
        arc_pts = [top(x, y) for x in (-0.3, -0.15, 0.15, 0.3)]
        if all(p is not None for p in arc_pts):
            rig.add(r.tube(f"SkullStripe{k}", [tuple(p + Vector((0, 0, 0.015))) for p in arc_pts],
                           0.03, segments=4), H, "stripe", **HEAD)
    rig.add(a.ring_around("NasalRim", (0, -3.02, 3.13), (0, -1, 0), 0.15, 0.035, segments=10), H,
            "bone_shade", **HEAD)
    for s in (-1, 1):    # os nasaux longs du museau
        nasal = [top(s * 0.1, y) for y in (-2.0, -2.45, -2.85)]
        if all(p is not None for p in nasal):
            rig.add(r.tube(f"Nasal{s}", [tuple(p + Vector((0, 0, 0.015))) for p in nasal],
                           [0.04, 0.045, 0.04], segments=4), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        for k in range(5):     # pores des moustaches
            y = -2.5 - 0.07 * k
            rig.add(r.ico(f"Whisker{s}{k}", 0.025, subdivisions=1,
                          location=(s * a.side_width(SKULL, y, 3.15 + 0.04 * (k % 2)) * 1.02, y,
                                    3.15 + 0.04 * (k % 2))), H, "ink", **HEAD)
        for k in range(3):     # piques de givre sur l'arcade
            rig.add(a.claw(f"BrowFrost{s}{k}", (s * (0.2 + 0.08 * k), -2.0 + 0.1 * k, 3.66),
                           (s * 0.3, 0.6, 1), 0.18, 0.03, curl=-0.1, segments=4), H, "ice", **HEAD)
    for s in (-1, 1):
        # Orbites tournées vers l'avant, œil bleu, arcade givrée
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.1, subdivisions=2, location=c0 - Vector((s * 0.06, 0, 0))), H,
                "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", c0, (s, -0.6, 0), 0.15, H, spikes=4, color="ice", **HEAD)
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.36, -1.75, 3.68), (s * 0.56, -1.8, 3.35)], 0.04,
                       segments=4), H, "bone_shade", **HEAD)
        # Arcade zygomatique très large
        zyg = a.smooth_path([(s * 0.45, -1.4, 3.02), (s * 0.76, -1.8, 3.08), (s * 0.45, -2.25, 3.1)], 5)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg], [0.05, 0.065, 0.07, 0.06, 0.05],
                       segments=5), H, "bone", **HEAD)
        rig.add(a.ring_around(f"ZygStripe{s}", zyg[2], zyg[3] - zyg[1], 0.075, 0.025, segments=6),
                H, "stripe", **HEAD)
        # SABRE : canine démesurée en lame aplatie, dentelée, courbée vers l'arrière
        base = Vector((s * 0.25, -2.55, 2.97))
        rig.add(r.ico(f"SaberRoot{s}", 0.1, subdivisions=1, location=base + Vector((0, 0, 0.05)),
                      scale=(0.8, 1.3, 1)), H, "bone_shade", **HEAD)
        rig.add(mr.tooth(f"Saber{s}", base, base + Vector((s * 0.05, -0.12, -0.95)), 0.26, 0.09,
                         Vector((s, 0, 0)), curl=0.22), H, "tooth", **HEAD)
        # Incisives en arc, prémolaire, carnassière
        for k in range(3):
            p = Vector((s * (0.05 + 0.07 * k), -2.88 + 0.03 * k, 2.98))
            rig.add(mr.tooth(f"UpIncisor{s}{k}", p, p + Vector((0, -0.03, -0.14)), 0.06, 0.04,
                             Vector((s * 0.3, -1, 0))), H, "tooth", **HEAD)
        for k, (y, size) in enumerate(((-2.3, 0.12), (-2.1, 0.15), (-1.85, 0.22))):
            p = Vector((s * a.side_width(SKULL, y, 3.0) * 0.85, y, 2.97))
            rig.add(mr.tooth(f"Carnassial{s}{k}", p, p + Vector((0, 0, -size)), size * 0.9,
                             size * 0.4, Vector((s, 0, 0))), H, "tooth", **HEAD)
        gum = [(s * 0.16, -2.85, 3.0), (s * 0.3, -2.4, 2.98), (s * 0.36, -1.8, 2.95)]
        rig.add(r.tube(f"UpperGum{s}", gum, 0.045, segments=4), H, "gum", **HEAD)
    build_jaw(rig)
    rig.add(r.ico("Throat", 0.2, subdivisions=2, location=(0, -1.7, 2.7), scale=(1.4, 1.6, 1)),
            H, "glow", glow=True)


def build_jaw(rig):
    """Mandibule modélisée fermée, puis ouverte d'un bloc autour de la charnière (GAPE)."""
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])), Vector((s * 0.38, -1.9, 2.9)),
                Vector((s * 0.26, -2.4, 2.87)), Vector((s * 0.1, -2.8, 2.85))]
        hs = [0.34, 0.3, 0.27, 0.26]
        rig.add(a.band(f"Dentary{s}", line, hs, [0.1, 0.09, 0.09, 0.08], offset=1), J, "bone",
                **HEAD)
        rig.add(r.tube(f"DentaryBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.035, segments=4), J, "bone_shade", **HEAD)
        # Bride mentonnière qui descend pour protéger le sabre
        rig.add(a.blade(f"Flange{s}", line[3] + Vector((0, 0.05, -0.1)),
                        line[3] + Vector((s * 0.02, 0.12, -0.5)), 0.22, 0.06, width_end=0.1,
                        normal=(1, 0, 0)), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.12, 0)), line[0] + Vector((0, -0.05, 0.28)),
                        0.16, 0.06, width_end=0.08, normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(p + Vector((-s * 0.03, 0, 0.02))) for p in line[1:]],
                       0.035, segments=4), J, "gum", **HEAD)
        for k, (t, size) in enumerate(((0.28, 0.2), (0.42, 0.17), (0.56, 0.14))):
            p = mr.along(line, t)
            rig.add(mr.tooth(f"LowCarn{s}{k}", p, p + Vector((0, 0, size)), size * 0.9, size * 0.4,
                             Vector((s, 0, 0))), J, "tooth", **HEAD)
        for k in range(3):
            p = line[3] + Vector((-s * 0.025 * k, -0.02, 0))
            rig.add(mr.tooth(f"LowIncisor{s}{k}", p, p + Vector((0, -0.02, 0.1)), 0.05, 0.035,
                             Vector((s * 0.3, -1, 0))), J, "tooth", **HEAD)
        p = mr.along(line, 0.82)
        rig.add(mr.tooth(f"LowCanine{s}", p, p + Vector((s * 0.02, -0.02, 0.28)), 0.11, 0.08,
                         Vector((s, -0.5, 0)), curl=0.1), J, "tooth", **HEAD)
        rig.add(a.ring_around(f"JawStripe{s}", mr.along(line, 0.45), line[2] - line[1], 0.12, 0.025,
                              segments=6), J, "stripe", **HEAD)
        for k in range(3):
            rig.add(r.ico(f"MentalPore{s}{k}", 0.025, subdivisions=1,
                          location=mr.along(line, 0.55 + 0.12 * k) + Vector((s * 0.05, 0, -0.1))),
                    J, "ink", **HEAD)
    rig.add(r.ico("ChinKnob", 0.09, subdivisions=1, location=(0, -2.82, 2.66)), J, "bone_shade",
            **HEAD)
    for k in range(3):
        rig.add(a.claw(f"ChinIcicle{k}", (0.07 * (k - 1), -2.79, 2.4), (0, 0.15, -1), 0.2, 0.035,
                       curl=0, segments=4), J, "ice", **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(_m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for path, bonef, base_size in ((SPINE, spine_bone, 0.22), (NECK, lambda i: "Neck", 0.19)):
        for i in range(len(path)):
            t = tangent(path, i)
            rig.add(a.vertebra(f"Vert{base_size}{i}", path[i], t, base_size, spine=1.4, lean=0.45),
                    bonef(i), "stripe" if (i % 4 == 2 and path is SPINE) else "bone")
            if i < len(path) - 1:
                rig.add(a.disc(f"Disc{base_size}{i}", path[i].lerp(path[i + 1], 0.5), t, base_size),
                        bonef(i), "disc")
    sternum = []
    for k, i in enumerate(range(6, 20)):
        hw = 0.55 + 0.22 * math.sin(math.pi * k / 13)
        depth = 0.85 + 0.45 * (k / 13) ** 0.6
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.06),
                    spine_bone(i), "stripe" if k % 3 == 1 else "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[1:-1:2], 0.08, 0.32), "Spine2", "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.6), (0.15, 0.4), (-0.15, 0.45))):
        rig.add(a.crystal(f"IceHeart{k}", (dx, -0.2, 1.95), 0.1 if k == 0 else 0.07, h, sides=6),
                "Spine2", "glow", glow=True)
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[18] + Vector((s * 0.2, 0, 0.1)),
                        sh + Vector((0, 0.03, 0.03)), 0.42, 0.06, width_end=0.22, mid=0.45,
                        normal=(s, 0, 0.4)), "Spine3", "bone")
        for k in range(3):    # arêtes de givre sur l'épaule
            rig.add(a.claw(f"ShoulderFrost{s}{k}", SPINE[18].lerp(sh, 0.4 + 0.15 * k)
                           + Vector((s * 0.05, 0, 0.12)), (s * 0.3, 0.5, 1), 0.25 - 0.04 * k, 0.04,
                           curl=-0.1, segments=4), "Spine3", "ice")
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.12, 0, 0.05)),
                        hp + Vector((s * 0.12, -0.25, 0.35)), 0.35, 0.06, width_end=0.28,
                        normal=(s, 0, 0.4)), "Spine1", "bone")
        rig.add(r.tube(f"Ischium{s}", [tuple(hp), (s * 0.22, 2.7, 2.3)], [0.06, 0.04], segments=5),
                "Spine1", "bone_shade")
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        size = 0.15 - 0.08 * i / (nt - 1)
        bone = "Tail" if i < 11 else "Tail2"
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=0.8, transverse=i < 6), bone,
                "stripe" if i % 3 == 1 else "bone")
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc")
    rig.add(a.crystal("TailFrost", TAIL[-1], 0.06, 0.3, sides=5), "Tail2", "ice")


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts in (("Front", front_leg(s)), ("Hind", hind_leg(s))):
            ub, lb, pb = f"{prefix}Upper_{side}", f"{prefix}Lower_{side}", f"{prefix}Paw_{side}"
            big = 1.15 if prefix == "Front" else 1.0
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.11 * big, segments=7), ub,
                    "bone", **LEGS)
            stripes(rig, f"{prefix}UpStripe{s}", pts[0], pts[1], 0.11 * big, ub, **LEGS)
            off = (pts[2] - pts[1]).cross(Vector((0, 0, 1))).normalized() * 0.06
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1] + off, pts[2] + off, 0.08 * big,
                                condyles=False, segments=6), lb, "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] - off, pts[2] - off, 0.06 * big,
                                condyles=False, segments=6), lb, "bone_shade", **LEGS)
            stripes(rig, f"{prefix}LowStripe{s}", pts[1], pts[2], 0.13 * big, lb, n=2, **LEGS)
            rig.add(r.ico(f"{prefix}Wrist{s}", 0.1, subdivisions=1, location=pts[2]), pb,
                    "bone_shade", **LEGS)
            # Patte : 4 doigts, griffes noires sorties
            lat = Vector((s, 0, 0))
            for j in range(4):
                off_j = (j - 1.5) * 0.09
                m1 = pts[3] + lat * off_j
                rig.add(a.long_bone(f"{prefix}Meta{s}{j}", pts[2] + lat * off_j * 0.5, m1, 0.04,
                                    condyles=False, segments=5), pb, "bone", **LEGS)
                toe = m1 + Vector((lat.x * off_j * 0.3, -0.24, -0.05))
                rig.add(a.long_bone(f"{prefix}Toe{s}{j}", m1, toe, 0.035, condyles=False,
                                    segments=5), pb, "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{j}", toe, (0, -1, -0.8), 0.22 * big, 0.04,
                               curl=0.5, segments=4), pb, "horn", **LEGS)
            rig.add(a.ring_around(f"{prefix}Glow{s}", pts[1], pts[2] - pts[1], 0.12 * big, 0.03,
                                  segments=8), lb, "glow", glow=True)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
