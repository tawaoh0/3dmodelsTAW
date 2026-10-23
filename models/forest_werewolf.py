"""Loup-garou squelette (≈ 6,5 studs de haut, voûté) — créature animable.
Pack « Forêt maudite », créature 1.

Animal modèle : le loup gris — crâne au stop marqué (front qui tombe sur le museau), haute
crête sagittale, arcades zygomatiques très larges, énormes canines, carnassières en lame ;
pattes arrière digitigrades (marche sur les doigts, jarret haut).

Identité : os gris cendre envahis de mousse et de racines ; pas de cornes mais des
« oreilles » en lames d'os noir et une **crinière de piquants** sur la nuque et le dos ;
silhouette bipède voûtée, bras démesurés à griffes ; fers brisés aux poignets, flèches
d'argent plantées dans le dos ; cœur en **croissant de lune** ; thème d'effets « moon ».

4 pièces Roblox : corps, Head (crâne + mâchoire), Arms, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, Tail1-2, UpperArm/ForeArm/Hand_{L,R},
Thigh/Shin/Foot_{L,R}, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#a39a88",
    "bone_shade": "#6e675a",
    "tooth": "#f2ecdc",
    "horn": "#1c1a18",
    "horn_tip": "#5d6f8a",
    "disc": "#3b3530",
    "moss": "#4f6b2a",
    "root": "#3a2a1c",
    "rust": "#7a4a2a",
    "silver": "#c9ced6",
    "gum": "#4e2228",
    "ink": "#0d0c0b",
    "glow": "#9cc4ff",
    "glow_hot": "#ffffff",
}

EFFECT_THEME = "moon"

TEST_POSE = {
    "Jaw": (22, 0, 0),
    "UpperArm_L": (-45, 0, 0),
    "ForeArm_L": (-30, 0, 0),
    "Thigh_R": (25, 0, 0),
    "Tail1": (0, 0, 25),
    "Head": (-10, 0, 0),
}

VIEW = (0.95, -1.0, 0.35)

SPINE = a.smooth_path([(0, 0.55, 3.35), (0, 0.3, 4.15), (0, -0.25, 4.85), (0, -0.85, 5.3),
                       (0, -1.25, 5.72)], 22)
TAIL = a.smooth_path([(0, 0.75, 3.3), (0, 1.5, 3.05), (0, 2.25, 2.5), (0, 2.8, 1.75),
                      (0, 3.05, 1.0)], 14)
# Crâne de loup : (y, demi-larg. dessus, joues, bord dentaire, z dessus, z bas)
# dôme crânien → arcades → stop (le dessus plonge) → museau long → truffe arrondie
SKULL = [(-1.3, 0.45, 0.55, 0.42, 6.22, 5.5), (-1.7, 0.52, 0.64, 0.5, 6.42, 5.45),
         (-2.1, 0.46, 0.6, 0.48, 6.32, 5.45), (-2.38, 0.32, 0.42, 0.38, 6.02, 5.47),
         (-2.8, 0.25, 0.33, 0.32, 5.92, 5.47), (-3.2, 0.21, 0.27, 0.27, 5.86, 5.48)]
EYE = (-2.12, 6.02)
HINGE = (0.47, -1.6, 5.4)
CHIN = (0.1, -3.12, 4.92)      # gueule entrouverte en grondement
HEAD = dict(part="Head")
ARMS = dict(part="Arms")
LEGS = dict(part="Legs")


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3", "Neck")[min(3, (0, 7, 14, 18).index(
        max(b for b in (0, 7, 14, 18) if b <= i)))]


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def arm_points(s):
    shoulder = Vector((s * 0.85, -0.85, 4.95))
    elbow = Vector((s * 1.2, -0.45, 3.6))
    wrist = Vector((s * 1.18, -1.3, 2.55))
    knuckle = Vector((s * 1.25, -1.75, 2.0))
    return shoulder, elbow, wrist, knuckle


def leg_points(s):
    hip = Vector((s * 0.55, 0.45, 3.15))
    knee = Vector((s * 0.72, -0.45, 2.1))
    hock = Vector((s * 0.74, 0.55, 1.0))
    paw = Vector((s * 0.76, 0.05, 0.2))
    return hip, knee, hock, paw


def vine(rig, name, a_pt, b_pt, radius, bone, turns=1.5, phase=0.0, **kw):
    """Racine qui s'enroule en spirale autour d'un os (de a_pt à b_pt)."""
    a_pt, b_pt = Vector(a_pt), Vector(b_pt)
    d = b_pt - a_pt
    side, up = a._basis(d)
    pts = []
    for k in range(9):
        t = k / 8
        ang = phase + 2 * math.pi * turns * t
        pts.append(a_pt + d * t + (side * math.cos(ang) + up * math.sin(ang)) * radius)
    rig.add(r.tube(name, [tuple(p) for p in pts], 0.035, segments=4), bone, "root", **kw)
    for k in (2, 6):   # petites feuilles de mousse
        rig.add(r.ico(f"{name}Moss{k}", 0.06, subdivisions=1, location=pts[k], scale=(1.4, 1, 0.6)),
                bone, "moss", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    for name, (i0, i1) in zip(("Spine1", "Spine2", "Spine3", "Neck"),
                              ((0, 7), (7, 14), (14, 18), (18, 21))):
        parent = rig.bone(name, SPINE[i0], SPINE[i1], parent)
    rig.bone("Head", SPINE[-1], (0, -3.3, 5.7), "Neck")
    rig.bone("Jaw", Vector(HINGE) * Vector((0, 1, 1)), (0, CHIN[1], CHIN[2]), "Head")
    rig.bone("Tail1", TAIL[0], TAIL[7], "Spine1")
    rig.bone("Tail2", TAIL[7], TAIL[-1], "Tail1")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, kn = arm_points(s)
        rig.bone(f"UpperArm_{side}", sh, el, "Spine3")
        rig.bone(f"ForeArm_{side}", el, wr, f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", wr, kn, f"ForeArm_{side}")
        hp, kn2, hk, pw = leg_points(s)
        rig.bone(f"Thigh_{side}", hp, kn2, "Spine1")
        rig.bone(f"Shin_{side}", kn2, hk, f"Thigh_{side}")
        rig.bone(f"Foot_{side}", hk, pw, f"Shin_{side}")
        rig.fx(f"Eye{side}", (s * 0.4, EYE[0], EYE[1]), "Head")
        rig.fx(f"Claws{side}", kn + Vector((0, -0.3, -0.5)), f"Hand_{side}")
    rig.fx("Heart", (0, -0.55, 4.25), "Spine2")
    rig.fx("Mouth", (0, -2.6, 5.35), "Head")
    rig.fx("Mane", SPINE[17] + Vector((0, 0.1, 0.6)), "Spine3")


# ---------------------------------------------------------------- crâne de loup

def build_skull(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.18)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.19, 0.16),
                  a.hole_x((0, -1.62, 5.78), 0.26, 0.17),             # fosse temporale
                  a.hole_x((0, -2.62, 5.72), 0.12, 0.07)])            # foramen infra-orbitaire
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Crête sagittale haute + crête nucale en éventail à l'arrière
    crest = [top(0, y) for y in (-1.3, -1.55, -1.85, -2.1)]
    rig.add(a.band("Sagittal", crest, [0.3, 0.34, 0.22, 0.06], 0.07, offset=0.15), H,
            "bone_shade", **HEAD)
    rig.add(a.band("Nuchal", [(-0.45, -1.3, 6.0), (0, -1.22, 6.35), (0.45, -1.3, 6.0)],
                   [0.12, 0.2, 0.12], 0.08, up=(0, 1, 0.4), offset=0), H, "bone_shade", **HEAD)
    # Os nasaux : deux crêtes du stop à la truffe ; truffe et narines
    for s in (-1, 1):
        nasal = [top(s * 0.1, y) + Vector((0, 0, 0.02)) for y in (-2.35, -2.75, -3.15)]
        rig.add(r.tube(f"Nasal{s}", [tuple(p) for p in nasal], [0.045, 0.05, 0.04], segments=4),
                H, "bone_shade", **HEAD)
        rig.add(r.ico(f"Nostril{s}", 0.07, subdivisions=1, location=(s * 0.08, -3.48, 5.6),
                      scale=(0.8, 0.6, 1.1)), H, "ink", **HEAD)
    rig.add(r.ico("NoseKnob", 0.13, subdivisions=1, location=(0, -3.42, 5.72),
                  scale=(1.3, 0.8, 0.9)), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        # Orbite cerclée, œil lunaire, arcade sourcilière en corniche à piques
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.13, subdivisions=2, location=(s * (x - 0.08), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, -0.25, 0.1), 0.19, H,
                       spikes=4, **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.18, -2.35, 6.2), (s * 0.55, -1.95, 6.28), 0.2, 0.09,
                        width_end=0.12, mid=0.24, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        for k in range(2):
            rig.add(a.claw(f"BrowSpike{s}{k}", (s * (0.38 + 0.12 * k), -2.15 + 0.12 * k, 6.3),
                           (s * 0.4, 0.6, 0.6), 0.2, 0.035, curl=-0.1, segments=4), H, "horn",
                    **HEAD)
        # Arcade zygomatique très large (signature du loup) + processus postorbitaire
        zyg = a.smooth_path([(s * 0.48, -1.42, 5.6), (s * 0.8, -1.75, 5.64),
                             (s * 0.8, -2.08, 5.7), (s * 0.48, -2.42, 5.76)], 7)
        rig.add(r.tube(f"Zygomatic{s}", [tuple(p) for p in zyg],
                       [0.06, 0.075, 0.085, 0.085, 0.08, 0.07, 0.06], segments=6), H, "bone",
                **HEAD)
        zyg = [zyg[0], zyg[2], zyg[4], zyg[6]]
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.55, -1.95, 6.25), (s * 0.75, -2.0, 5.75)],
                       [0.06, 0.05], segments=5), H, "bone_shade", **HEAD)
        rig.add(a.claw(f"ZygSpike{s}", zyg[1], (s, 0.5, 0.1), 0.25, 0.05, curl=0, segments=4), H,
                "horn", **HEAD)
        # Oreilles en lames d'os noir (silhouette du loup)
        rig.add(a.blade(f"Ear{s}", (s * 0.32, -1.45, 6.3), (s * 0.58, -0.95, 6.82), 0.26, 0.07,
                        width_end=0.02, mid=0.27, normal=(1, -0.5, 0.6)), H, "horn", **HEAD)
        rig.add(r.tube(f"EarRidge{s}", [(s * 0.34, -1.42, 6.33), (s * 0.47, -1.18, 6.6),
                                        (s * 0.56, -0.98, 6.8)], [0.045, 0.035, 0.015],
                       segments=4), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"EarRing{s}", (s * 0.42, -1.27, 6.5), (s * 0.4, 0.5, 1), 0.08, 0.025,
                              segments=8), H, "silver", **HEAD)
        # Crête infra-orbitaire, pores des moustaches, cicatrice lunaire
        rig.add(r.tube(f"Maxillary{s}", [(s * 0.42, -2.3, 5.62), (s * 0.33, -2.75, 5.6),
                                         (s * 0.27, -3.15, 5.58)], [0.06, 0.05, 0.04],
                       segments=5), H, "bone_shade", **HEAD)
        for k in range(6):
            yy = -2.8 - 0.09 * k
            rig.add(r.ico(f"Whisker{s}{k}", 0.028, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy, 5.67 + 0.05 * (k % 2)) * 1.02, yy,
                                    5.67 + 0.05 * (k % 2))), H, "ink", **HEAD)
        mr.scar(rig, f"MoonScar{s}", top(s * 0.3, -1.4), top(s * 0.42, -1.85), H, width=0.04,
                seed=s)
        # Gencive le long de la rangée du haut
        gum = [(s * a.side_width(SKULL, y, 5.5) * 0.8, y, 5.47) for y in (-1.95, -2.4, -2.9, -3.3)]
        rig.add(r.tube(f"UpperGum{s}", gum, 0.05, segments=4), H, "gum", **HEAD)
    # Mousse sur le crâne
    for k, (x, y) in enumerate(((0.25, -1.5), (-0.3, -1.95), (0.15, -2.55))):
        rig.add(r.ico(f"SkullMoss{k}", 0.1, subdivisions=1, location=top(x, y),
                      scale=(1.3, 1.6, 0.45)), H, "moss", **HEAD)
    build_jaw(rig)
    build_teeth(rig)


def jaw_line(s):
    """Bord dentaire du dentaire, de la charnière au menton."""
    hx, hy, hz = HINGE
    cx, cy, cz = CHIN
    # bord légèrement creusé (courbe), pas une planche droite
    return [Vector((s * (hx + (cx - hx) * t ** 0.8), hy + (cy - hy) * t,
                    hz + (cz - hz) * t - 0.07 * math.sin(math.pi * t)))
            for t in (0.0, 0.25, 0.5, 0.75, 1.0)]


def build_jaw(rig):
    J = "Jaw"
    for s in (-1, 1):
        line = jaw_line(s)
        hs = [0.38, 0.37, 0.33, 0.27, 0.25]    # bord inférieur bombé, menton marqué
        rig.add(a.band(f"Dentary{s}", line, hs, [0.16, 0.15, 0.13, 0.12, 0.11], offset=1), J,
                "bone", **HEAD)
        rig.add(r.tube(f"DentaryRidge{s}", [tuple(p + Vector((s * 0.09, 0, -h * 0.6)))
                                            for p, h in zip(line[:4], hs)],
                       [0.05, 0.05, 0.04, 0.03], segments=4), J, "bone_shade", **HEAD)
        rig.add(r.tube(f"DentaryBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)],
                       0.045, segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.15, 0)),
                        line[0] + Vector((0, -0.05, 0.42)), 0.24, 0.07, width_end=0.1,
                        normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(a.claw(f"Angular{s}", line[0] - Vector((0, 0, 0.25)), (0, 1, -0.3), 0.22, 0.05,
                       curl=0.1, segments=4), J, "bone_shade", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.11, subdivisions=1, location=line[0] + Vector((0, 0.05, 0.03))),
                "Head", "bone_shade", **HEAD)
        for k in range(3):
            q = line[1 + k] - Vector((0, 0, 0.12))
            rig.add(r.ico(f"MentalForamen{s}{k}", 0.03, subdivisions=1,
                          location=q + Vector((s * 0.055, 0, 0))), J, "ink", **HEAD)
        gum = [tuple(p + Vector((-s * 0.04, 0, 0.02))) for p in line[1:]]
        rig.add(r.tube(f"LowerGum{s}", gum, 0.045, segments=4), J, "gum", **HEAD)
    rig.add(r.ico("ChinKnob", 0.1, subdivisions=1, location=(0, -3.16, 4.72)), J, "bone_shade",
            **HEAD)
    rig.add(r.ico("Throat", 0.2, subdivisions=2, location=(0, -1.85, 5.35), scale=(1.2, 1.4, 0.7)),
            "Head", "glow", glow=True)


def build_teeth(rig):
    H, J = "Head", "Jaw"
    # Rangée du haut : incisives, canine énorme, prémolaires, carnassière en lame
    upper = ((-3.33, 0.07, 0.14, "inc"), (-3.3, 0.14, 0.16, "inc"), (-3.24, 0.2, 0.17, "inc"),
             (-3.08, None, 0.62, "can"), (-2.85, None, 0.2, "pm"), (-2.6, None, 0.24, "pm"),
             (-2.35, None, 0.26, "pm"), (-2.08, None, 0.36, "carn"), (-1.85, None, 0.2, "mol"))
    for s in (-1, 1):
        for k, (y, x, size, kind) in enumerate(upper):
            xx = s * (x if x is not None else a.side_width(SKULL, y, 5.5) * 0.88)
            base = Vector((xx, y, 5.48))
            out = Vector((s * 0.6, -1 if kind in ("inc", "can") else -0.2, 0)).normalized()
            width = size * {"inc": 0.55, "can": 0.4, "pm": 0.8, "carn": 0.9, "mol": 1.0}[kind]
            tip = base + Vector((0, 0, -size)) + Vector((0, 0.06 * size, 0))
            rig.add(mr.tooth(f"UpTooth{s}{k}", base, tip, width, width * 0.5, out,
                             curl=0.12 if kind == "can" else 0.04), H, "tooth", **HEAD)
            if kind in ("can", "carn"):
                rig.add(r.ico(f"UpSocket{s}{k}", 0.07, subdivisions=1,
                              location=base + Vector((s * 0.06, 0, 0.08))), H, "bone_shade",
                        **HEAD)
        # Rangée du bas, sur le dentaire (canine qui remonte devant la canine du haut)
        line = jaw_line(s)
        lower = ((0.97, 0.12, "inc"), (0.92, 0.13, "inc"), (0.86, 0.5, "can"), (0.7, 0.18, "pm"),
                 (0.55, 0.2, "pm"), (0.4, 0.3, "carn"), (0.25, 0.22, "mol"))
        for k, (t, size, kind) in enumerate(lower):
            base = mr.along(line, t)
            if kind == "inc":
                base = base + Vector((-s * 0.03 * (1 + k), 0, 0))
            out = Vector((s * 0.6, -1 if kind in ("inc", "can") else -0.2, 0)).normalized()
            width = size * {"inc": 0.55, "can": 0.42, "pm": 0.8, "carn": 0.9, "mol": 1.0}[kind]
            rig.add(mr.tooth(f"LowTooth{s}{k}", base, base + Vector((0, -0.05 * size, size)),
                             width, width * 0.5, out, curl=0.12 if kind == "can" else 0.04), J,
                    "tooth", **HEAD)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        size = 0.24 if i < 18 else 0.2
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, size, spine=1.4 if i < 18 else 0.8,
                           lean=0.45), spine_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, size), spine_bone(i),
                    "disc")
    # Crinière : piquants d'os sur la nuque et le haut du dos, en éventail alterné
    for i in range(9, n):
        t = tangent(SPINE, i)
        side, up = a._basis(t)
        for k, sd in enumerate((-1, 0, 1)):
            base = SPINE[i] + up * 0.3 + side * sd * 0.14
            length = (0.45 + 0.25 * math.sin(math.pi * (i - 9) / (n - 9))) * (0.75 if sd else 1)
            rig.add(a.claw(f"Mane{i}{k}", base, up + t * 0.9 + side * sd * 0.5, length, 0.045,
                           curl=-0.15, segments=4), spine_bone(i),
                    "horn" if (i + k) % 2 else "bone_shade")
    # Cage thoracique pendante sous le dos voûté, sternum
    sternum = []
    for k, i in enumerate(range(8, 18)):
        hw = 0.55 + 0.25 * math.sin(math.pi * k / 9)
        depth = 0.95 + 0.4 * math.sin(math.pi * (k + 2) / 12)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.25, radius=0.07),
                    spine_bone(i), "bone")
        sternum.append(SPINE[i] + Vector((0, -0.25, -depth)))
    rig.add(r.tube("Sternum", [tuple(p) for p in sternum[1:-1:2]], 0.08, segments=6), "Spine2",
            "bone_shade")
    # Cœur : croissant de lune + éclats
    moon = r.torus("MoonHeart", 0.28, 0.07, segments=10, minor_segments=5, arc=4.2,
                   location=(0, -0.55, 4.25), rotation=(math.pi / 2, 0, 1.2))
    rig.add(moon, "Spine2", "glow", glow=True)
    for k in range(3):
        rig.add(a.crystal(f"MoonShard{k}", (0.15 * (k - 1), -0.5, 3.95), 0.06, 0.3 + 0.1 * k,
                          sides=5), "Spine2", "glow", glow=True)
    rig.add(r.tube("HeartHang", [(0, -0.45, 4.62), tuple(sternum[4] + Vector((0, 0.1, 0.15)))],
                   0.03, segments=4), "Spine2", "root")
    # Omoplates, clavicules, bassin
    for s in (-1, 1):
        sh = arm_points(s)[0]
        rig.add(a.blade(f"Scapula{s}", (s * 0.35, -0.35, 5.25), sh + Vector((0, 0.05, 0.05)), 0.5,
                        0.08, width_end=0.25, mid=0.55, normal=(0.3 * s, 0.6, 1)), "Spine3", "bone")
        rig.add(a.long_bone(f"Clavicle{s}", sh, sternum[-2] + Vector((s * 0.15, 0, 0)), 0.06,
                            condyles=False), "Spine3", "bone_shade")
        hp = leg_points(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[1] + Vector((s * 0.15, 0, 0)),
                        hp + Vector((s * 0.15, -0.1, 0.55)), 0.45, 0.08, width_end=0.35, mid=0.55,
                        normal=(s, 0, 0.3)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.3, 0.1, 2.75), (0, 0.15, 2.7)], 0.07,
                       segments=5), "Spine1", "bone")
        rig.add(r.tube(f"Ischium{s}", [tuple(hp), (s * 0.35, 0.8, 2.85)], [0.07, 0.05],
                       segments=5), "Spine1", "bone_shade")
        rig.add(a.ring_around(f"Acetabulum{s}", hp, (s, 0, 0), 0.14, 0.04, segments=8), "Spine1",
                "bone_shade")
    # Queue + piquants
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        size = 0.17 - 0.09 * i / (nt - 1)
        bone = "Tail1" if i < 7 else "Tail2"
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=1.2, lean=0.5,
                           transverse=i < 6), bone, "bone")
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc")
        if i % 2 == 0:
            side, up = a._basis(t)
            rig.add(a.claw(f"TailQuill{i}", TAIL[i] + up * size, up + t, 0.3 - 0.015 * i, 0.035,
                           curl=-0.1, segments=4), bone, "horn")
    # Flèches d'argent plantées dans le dos (empennage, pointe lumineuse dans la cage)
    for k, (base, d) in enumerate(((SPINE[11] + Vector((0.35, 0.2, 0.3)), (0.4, 0.8, 0.7)),
                                   (SPINE[6] + Vector((-0.3, 0.1, 0.25)), (-0.5, 0.6, 0.8)))):
        d = Vector(d).normalized()
        bone = spine_bone(11 if k == 0 else 6)
        rig.add(r.tube(f"Arrow{k}", [tuple(base - d * 0.25), tuple(base + d * 1.3)], 0.03,
                       segments=5), bone, "silver")
        rig.add(r.ico(f"ArrowTip{k}", 0.06, subdivisions=1, location=base - d * 0.27), bone,
                "glow", glow=True)
        side, up = a._basis(d)
        for j in range(3):
            ang = 2 * math.pi * j / 3
            nrm = side * math.cos(ang) + up * math.sin(ang)
            rig.add(a.blade(f"Fletch{k}{j}", base + d * 1.0, base + d * 1.3, 0.1, 0.015,
                            width_end=0.05, normal=nrm.cross(d), bevel=0), bone, "silver")
    # Mousse et racines sur le dos et le bassin
    for k, i in enumerate((3, 8, 13)):
        rig.add(r.ico(f"BackMoss{k}", 0.13, subdivisions=1,
                      location=SPINE[i] + Vector((0.2 * (-1) ** k, 0, 0.18)),
                      scale=(1.4, 1.2, 0.5)), spine_bone(i), "moss")
    vine(rig, "SpineVine", SPINE[2], SPINE[12], 0.28, "Spine2", turns=2.0)


# ---------------------------------------------------------------- membres

def build_arms(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, kn = arm_points(s)
        ua, fa, hd = f"UpperArm_{side}", f"ForeArm_{side}", f"Hand_{side}"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.12, segments=7), ua, "bone", **ARMS)
        # Avant-bras : radius + cubitus côte à côte, olécrane pointu
        side_v = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.08
        rig.add(a.long_bone(f"Radius{s}", el + side_v, wr + side_v, 0.07, condyles=False,
                            segments=6), fa, "bone", **ARMS)
        rig.add(a.long_bone(f"Ulna{s}", el - side_v, wr - side_v, 0.065, condyles=False,
                            segments=6), fa, "bone_shade", **ARMS)
        rig.add(a.claw(f"Olecranon{s}", el, (0, 1, 0.3), 0.28, 0.07, curl=0, segments=5), fa,
                "horn", **ARMS)
        rig.add(r.ico(f"Wrist{s}", 0.12, subdivisions=1, location=wr), hd, "bone_shade", **ARMS)
        # Fers brisés au poignet + maillons qui pendent
        rig.add(a.ring_around(f"Shackle{s}", wr.lerp(el, 0.15), el - wr, 0.16, 0.05, segments=10),
                fa, "rust", **ARMS)
        p = wr.lerp(el, 0.15) + Vector((s * 0.12, 0, -0.12))
        for j in range(3):
            ax = Vector((1, 0, 0)) if j % 2 == 0 else Vector((0, 1, 0))
            rig.add(a.ring_around(f"Chain{s}{j}", p, ax, 0.065, 0.02, segments=8), fa, "rust",
                    **ARMS)
            p = p + Vector((0.02, 0.02, -0.11))
        # Main : métacarpes + 4 doigts à 2 phalanges et griffes noires
        lat = Vector((s, 0, 0))
        for j in range(4):
            off = (j - 1.5) * 0.11
            mc0 = wr + lat * off * 0.6
            base = kn + lat * off + Vector((0, 0.03 * abs(j - 1.5), 0))
            rig.add(a.long_bone(f"Metacarpal{s}{j}", mc0, base, 0.045, condyles=False,
                                segments=5), hd, "bone", **ARMS)
            mid = base + Vector((lat.x * off * 0.3, -0.3, -0.25))
            end = mid + Vector((0, -0.18, -0.25))
            rig.add(a.long_bone(f"Phalanx{s}{j}", base, mid, 0.04, condyles=False, segments=5), hd,
                    "bone", **ARMS)
            rig.add(a.long_bone(f"Phalanx2{s}{j}", mid, end, 0.035, condyles=False, segments=5), hd,
                    "bone", **ARMS)
            rig.add(a.claw(f"HandClaw{s}{j}", end, (0, -0.3, -1), 0.4 if j else 0.3, 0.05,
                           curl=0.45, segments=5), hd, "horn", **ARMS)
            rig.add(r.ico(f"Knuckle{s}{j}", 0.055, subdivisions=1, location=base), hd,
                    "bone_shade", **ARMS)
        vine(rig, f"ArmVine{s}", sh, el, 0.16, ua, turns=1.5, phase=s, **ARMS)
        rig.add(r.ico(f"ShoulderMoss{s}", 0.14, subdivisions=1, location=sh + Vector((0, 0, 0.12)),
                      scale=(1.3, 1.3, 0.5)), ua, "moss", **ARMS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, hk, pw = leg_points(s)
        th, sn, ft = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.14, segments=7), th, "bone", **LEGS)
        rig.add(r.ico(f"Patella{s}", 0.1, subdivisions=1, location=kn + Vector((0, -0.12, 0.02))),
                th, "bone_shade", **LEGS)
        rig.add(a.long_bone(f"Tibia{s}", kn, hk, 0.11, segments=7), sn, "bone", **LEGS)
        rig.add(a.long_bone(f"Fibula{s}", kn + Vector((s * 0.1, 0.05, 0)),
                            hk + Vector((s * 0.08, 0, 0.1)), 0.04, condyles=False, segments=5), sn,
                "bone_shade", **LEGS)
        rig.add(a.claw(f"Calcaneus{s}", hk, (0, 1, 0.4), 0.3, 0.08, curl=0, segments=5), ft,
                "bone_shade", **LEGS)
        # Métatarses longs (marche sur les doigts) + 4 orteils griffus
        lat = Vector((s, 0, 0))
        for j in range(4):
            off = (j - 1.5) * 0.1
            m0 = hk + lat * off * 0.5
            m1 = pw + lat * off
            rig.add(a.long_bone(f"Metatarsal{s}{j}", m0, m1, 0.045, condyles=False, segments=5), ft,
                    "bone", **LEGS)
            toe = m1 + Vector((lat.x * off * 0.4, -0.35, -0.12))
            rig.add(a.long_bone(f"Toe{s}{j}", m1, toe, 0.04, condyles=False, segments=5), ft,
                    "bone", **LEGS)
            rig.add(a.claw(f"FootClaw{s}{j}", toe, (0, -1, -0.6), 0.25, 0.045, curl=0.35,
                           segments=4), ft, "horn", **LEGS)
        rig.add(a.claw(f"Dewclaw{s}", hk.lerp(pw, 0.5) + Vector((-s * 0.08, -0.05, 0)),
                       (-s * 0.3, -1, 0.2), 0.2, 0.04, curl=0.4, segments=4), ft, "horn", **LEGS)
        vine(rig, f"LegVine{s}", kn, hk, 0.14, sn, turns=1.5, phase=2 * s, **LEGS)
        rig.add(r.ico(f"KneeMoss{s}", 0.11, subdivisions=1, location=kn + Vector((0, -0.08, 0.12)),
                      scale=(1.3, 1.2, 0.5)), th, "moss", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_skull(rig)
    build_body(rig)
    build_arms(rig)
    build_legs(rig)
    return rig
