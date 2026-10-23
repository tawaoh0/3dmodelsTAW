"""Raptor squelette toxique (≈ 13 studs de long, 6.5 de haut) — créature animable.

Silhouette fine et nerveuse : crâne bas et long au profil ondulé, crête nasale en
dents de scie, grandes orbites, cornes balayées vers l'arrière, crochets qui gouttent
de venin ; cou en S, longs bras à 3 griffes hérissés de piquants, griffe faucille
relevée sur chaque pied, queue raide gainée de tendons ossifiés. Lueur vert toxique.

2 pièces Roblox : corps, tête (+ cou), plus le mesh lumineux.
Os du rig : Root, Hips, Spine, Neck1-2, Head, Jaw, Tail1-4, Thigh/Shin/Foot/Sickle_L/R,
UpperArm/Forearm/Hand_L/R, + FX_* (yeux, gueule, cœur, bout de queue).
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#ddd3bd",
    "bone_shade": "#a39a80",
    "tooth": "#f4f0e0",
    "horn": "#1d2119",
    "horn_tip": "#2f5a12",
    "disc": "#2b3d1c",
    "glow": "#7dff2a",
    "glow_hot": "#e8ffb0",
}

TEST_POSE = {
    "Jaw": (32, 0, 0),
    "Neck1": (-12, 0, 0),
    "Head": (12, 0, 0),
    "Thigh_L": (-30, 0, 0),
    "Shin_L": (25, 0, 0),
    "Sickle_L": (-35, 0, 0),
    "UpperArm_R": (-45, 0, 0),
    "Forearm_R": (-20, 0, 0),
    "Tail2": (0, 0, 12),
    "Tail3": (0, 0, 12),
}

BACK = [(0, 0.9, 3.65), (0, -0.2, 3.75), (0, -1.4, 3.95)]
NECK = [(0, -1.4, 3.95), (0, -1.95, 4.45), (0, -2.2, 5.05), (0, -2.75, 5.55)]
TAIL = [(0, 0.9, 3.65), (0, 2.6, 3.55), (0, 4.3, 3.35), (0, 6.0, 3.1), (0, 7.6, 2.85)]

# Crâne : (y, demi-largeur dessus, joues, bord dentaire, z dessus, z bord dentaire).
# Profil : dôme → arcade → creux → bosse de la crête nasale → museau effilé mais émoussé.
SKULL = [(-2.75, 0.42, 0.62, 0.5, 6.05, 5.25), (-3.05, 0.46, 0.66, 0.52, 6.2, 5.2),
         (-3.4, 0.44, 0.6, 0.48, 6.25, 5.2), (-3.8, 0.32, 0.46, 0.4, 6.0, 5.22),
         (-4.25, 0.26, 0.38, 0.34, 5.88, 5.25), (-4.7, 0.25, 0.34, 0.3, 5.94, 5.28),
         (-5.1, 0.2, 0.27, 0.25, 5.82, 5.3), (-5.4, 0.13, 0.18, 0.17, 5.6, 5.33)]
JAW = [(-2.8, 0.36, 0.55, 0.45, 5.22, 4.85), (-3.6, 0.3, 0.45, 0.36, 5.2, 4.8),
       (-4.6, 0.22, 0.32, 0.27, 5.2, 4.92), (-5.35, 0.12, 0.17, 0.15, 5.2, 5.03)]


def width_at(sections, y, idx=3):
    for s0, s1 in zip(sections, sections[1:]):
        if s1[0] <= y <= s0[0]:
            t = (s0[0] - y) / (s0[0] - s1[0])
            return s0[idx] + (s1[idx] - s0[idx]) * t
    return sections[-1][idx]


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 0.9, 3.65), (0, -0.4, 3.78), "Root")
    rig.bone("Spine", (0, -0.4, 3.78), (0, -1.4, 3.95), "Hips")
    rig.bone("Neck1", (0, -1.4, 3.95), (0, -2.2, 5.05), "Spine")
    rig.bone("Neck2", (0, -2.2, 5.05), (0, -2.75, 5.55), "Neck1")
    rig.bone("Head", (0, -2.75, 5.55), (0, -5.4, 5.55), "Neck2")
    rig.bone("Jaw", (0, -2.85, 5.12), (0, -5.35, 5.05), "Head")
    parent = "Hips"
    for i in range(4):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Thigh_{side}", (s * 0.55, 0.7, 3.3), (s * 0.7, -0.25, 2.0), "Hips")
        rig.bone(f"Shin_{side}", (s * 0.7, -0.25, 2.0), (s * 0.7, 0.6, 0.8), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 0.7, 0.6, 0.8), (s * 0.7, -0.6, 0.15), f"Shin_{side}")
        rig.bone(f"Sickle_{side}", (s * 0.58, -0.05, 0.35), (s * 0.58, -0.6, 0.6), f"Foot_{side}")
        rig.bone(f"UpperArm_{side}", (s * 0.5, -1.55, 3.5), (s * 0.72, -1.15, 2.75), "Spine")
        rig.bone(f"Forearm_{side}", (s * 0.72, -1.15, 2.75), (s * 0.68, -1.95, 2.5),
                 f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", (s * 0.68, -1.95, 2.5), (s * 0.68, -2.5, 2.2), f"Forearm_{side}")
        rig.fx(f"Eye{side}", (s * 0.36, -3.35, 5.85), "Head")
    rig.fx("Mouth", (0, -3.6, 5.15), "Head")
    rig.fx("Heart", (0, -0.6, 2.9), "Spine")
    rig.fx("TailTip", (0, 8.1, 2.85), "Tail4")


# ---------------------------------------------------------------- tête

def build_head(rig):
    head = dict(part="Head")
    skull = a.loft_profile("Skull", SKULL)
    tilt = -0.25
    cutters = []
    for center, ry, rz in (((0, -3.35, 5.85), 0.27, 0.27),     # grandes orbites rondes
                           ((0, -4.3, 5.58), 0.42, 0.16),      # fenêtres antorbitales
                           ((0, -2.88, 5.72), 0.11, 0.24),     # fenêtres temporales
                           ((0, -5.12, 5.58), 0.1, 0.07)):     # narines
        cutter = a.hole_x(center, ry, rz)
        a.rotate_obj(cutter, "X", tilt, center)
        cutters.append(cutter)
    a.cut(skull, cutters)
    rig.add(skull, "Head", "bone", **head)

    # Crête nasale en dents de scie sur toute la longueur du museau
    for k, y in enumerate((-3.95, -4.25, -4.55, -4.85, -5.12)):
        z = width_at(SKULL, y, 4) - 0.03
        size = 0.32 - abs(k - 2) * 0.06
        rig.add(a.claw(f"NasalSaw{k}", (0, y, z), (0, 0.6, 1), size, 0.08, curl=-0.1, segments=4),
                "Head", "horn", **head)
    # Crête sagittale sur le dôme
    rig.add(a.blade("Sagittal", (0, -3.5, 6.24), (0, -2.75, 6.08), 0.14, 0.09, width_end=0.2,
                    normal=(1, 0, 0), bevel=0.015), "Head", "bone_shade", **head)

    for s in (-1, 1):
        # Arcade sourcilière en corniche + pique arrière
        rig.add(a.blade(f"Brow{s}", (s * 0.18, -3.75, 6.12), (s * 0.58, -3.0, 6.25), 0.26, 0.14,
                        width_end=0.2, mid=0.34, normal=(0, 0.25, 1)), "Head", "bone_shade",
                **head)
        rig.add(a.claw(f"BrowSpike{s}", (s * 0.58, -3.0, 6.25), (s * 0.5, 1, 0.35), 0.4, 0.08,
                       curl=-0.1), "Head", "horn", **head)
        # Petite corne lacrymale devant l'œil
        rig.add(a.claw(f"Lacrimal{s}", (s * 0.28, -3.72, 6.02), (s * 0.35, -0.2, 1), 0.32, 0.08,
                       curl=-0.2), "Head", "horn", **head)
        # Pommette en arche avec une pique
        cheek = [(s * 0.36, -3.95, 5.38), (s * 0.6, -3.35, 5.38), (s * 0.64, -2.85, 5.5),
                 (s * 0.5, -2.6, 5.78)]
        arch = r.tube(f"Zygomatic{s}", cheek, [0.07, 0.11, 0.11, 0.08], segments=6)
        r.smooth(arch, 40)
        rig.add(arch, "Head", "bone_shade", **head)
        rig.add(a.claw(f"CheekSpike{s}", cheek[2], (s * 0.8, 0.7, -0.2), 0.32, 0.06, curl=-0.1),
                "Head", "horn", **head)
        # Bosse de narine
        rig.add(r.ico(f"NostrilBoss{s}", 0.12, subdivisions=1, location=(s * 0.18, -5.0, 5.72),
                      scale=(0.9, 1.6, 0.8)), "Head", "bone_shade", **head)
        # Cornes balayées vers l'arrière
        horn = a.ridged_horn(f"Horn{s}", [(s * 0.3, -2.95, 6.12), (s * 0.48, -2.4, 6.4),
                                          (s * 0.62, -1.75, 6.55), (s * 0.68, -1.15, 6.45)],
                             0.17, ridges=6)
        rig.add(horn, "Head", "horn", **head)
        rig.add(a.claw(f"HornTip{s}", (s * 0.68, -1.17, 6.46), (0, 0.6, -0.4), 0.14, 0.04),
                "Head", "horn_tip", **head)
        # Œil vert au fond de l'orbite
        rig.add(r.ico(f"Eye{s}", 0.13, subdivisions=2, location=(s * 0.36, -3.35, 5.85)),
                "Head", "glow", glow=True)
        # Mâchoire : apophyse coronoïde + épine à l'angle
        rig.add(a.blade(f"Coronoid{s}", (s * 0.42, -3.1, 5.0), (s * 0.45, -2.9, 5.35), 0.24, 0.08,
                        width_end=0.13, normal=(1, 0, 0), bevel=0), "Jaw", "bone_shade", **head)
        rig.add(a.claw(f"JawSpike{s}", (s * 0.45, -2.8, 4.9), (s * 0.5, 0.8, -0.4), 0.32, 0.06,
                       curl=-0.1), "Jaw", "horn", **head)

    # Sac à venin incandescent dans la gorge
    rig.add(r.ico("VenomSac", 0.17, subdivisions=2, location=(0, -3.2, 5.3), scale=(1.0, 1.3, 0.55)),
            "Head", "glow", glow=True)
    rig.add(r.box("Rune", (0.09, 0.09, 0.04), location=(0, -3.2, width_at(SKULL, -3.2, 4) + 0.02),
                  rotation=(0, 0, 0.785)), "Head", "glow", glow=True)

    # Dents en scie, crochets à venin à l'avant (avec gouttes)
    for jaw, sections, z, direction, bone in ((False, SKULL, 5.27, (0, 0.3, -1), "Head"),
                                              (True, JAW, 5.17, (0, -0.25, 1), "Jaw")):
        y, k = -5.25, 0
        while y < -3.3:
            for s in (-1, 1):
                x = s * width_at(sections, y) * (0.72 if jaw else 0.86)
                fang = k == 1
                length = (0.42 if fang else 0.2) * (0.8 if jaw else 1)
                rig.add(a.claw(f"Tooth{bone}{s}{k}", (x, y, z), direction, length,
                               0.06 if fang else 0.045, curl=-0.1, segments=4),
                        bone, "tooth", **head)
                if fang and not jaw:
                    drip = Vector((x, y + 0.13, z - 0.45))
                    rig.add(r.ico(f"Venom{s}", 0.05, subdivisions=1, location=drip,
                                  scale=(1, 1, 1.8)), "Head", "glow", glow=True)
            y += 0.22
            k += 1

    jaw = a.loft_profile("Jaw", JAW)
    a.cut(jaw, [a.hole_x((0, -3.45, 5.0), 0.28, 0.08)])
    rig.add(jaw, "Jaw", "bone", **head)


# ---------------------------------------------------------------- colonne

def build_spine(rig):
    back = c.Chain(BACK)
    for i in range(7):
        p, t = back.at(i / 6)
        bone = "Hips" if p.y > -0.4 else "Spine"
        v = a.vertebra(f"Back{i}", p, -t, 0.3, spine=1.1 + 0.3 * math.sin(i / 6 * math.pi),
                       lean=0.3)
        rig.add(v, bone, "bone")
        if i < 6:
            q, tq = back.at((i + 0.5) / 6)
            rig.add(a.disc(f"BackDisc{i}", q, tq, 0.3), bone, "disc")
        if i % 2 == 1:
            tip = p + Vector((0, 0.1, 0.3 * 0.7 + 0.3 * 1.3))
            rig.add(a.claw(f"BackSpike{i}", tip, (0, 0.5, 1), 0.3, 0.07, curl=-0.1), bone, "horn")

    neck = c.Chain(NECK)
    for i in range(7):
        p, t = neck.at(i / 6)
        bone = "Neck1" if i < 5 else "Neck2"
        size = 0.34 - 0.04 * i / 6
        rig.add(a.vertebra(f"Neck{i}", p, -t, size, spine=0.55, lean=0.2), bone, "bone",
                part="Head")
        if i < 6:
            q, tq = neck.at((i + 0.5) / 6)
            rig.add(a.disc(f"NeckDisc{i}", q, tq, size), bone, "disc", part="Head")
        if i % 2 == 0:
            up = Vector((0, 0, 1))
            rig.add(a.claw(f"NeckSpike{i}", p + up * size * 1.2, (0, 0.6, 1), 0.22, 0.05,
                           curl=-0.1, segments=4), bone, "horn", part="Head")

    tail = c.Chain(TAIL)
    n = 16
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(4, int(t * 4 * 0.999) + 1)}"
        size = 0.3 - 0.19 * t
        rig.add(a.vertebra(f"Tail{i}", p, tan, size, spine=1.0 - 0.5 * t, lean=-0.3,
                           transverse=i < 10), bone, "bone")
        if i < n - 1:
            q, tq = tail.at((i + 0.5) / (n - 1))
            rig.add(a.disc(f"TailDisc{i}", q, tq, size), bone, "disc")
        if i < 10:
            down = p - Vector((0, -0.05, size * 0.4))
            rig.add(a.blade(f"Chevron{i}", down, down + Vector((0, 0.3, -size * 1.8)),
                            size * 0.45, size * 0.16, width_end=size * 0.2, normal=(1, 0, 0),
                            bevel=0), bone, "bone_shade")
    # Tendons ossifiés : baguettes qui gainent la queue (raideur du raptor), un tronçon par os
    for i in range(4):
        a0, b0 = Vector(TAIL[i]), Vector(TAIL[i + 1])
        rad = 0.3 - 0.19 * (i + 0.5) / 4
        for s in (-1, 1):
            off = Vector((s * rad * 0.9, 0, rad * 0.55))
            rig.add(r.tube(f"Tendon{i}{s}", [tuple(a0 + off), tuple(b0.lerp(a0, 0.05) + off)],
                           [0.035, 0.03], segments=4), f"Tail{i + 1}", "bone_shade")
    # Pointe de queue : bouquet de cristaux toxiques
    tip, tan = tail.at(1.0)
    rig.add(a.claw("TailCrystal", tip, tan, 0.7, 0.14, curl=0, segments=5), "Tail4", "glow",
            glow=True)
    for s in (-1, 1):
        rig.add(a.claw(f"TailShard{s}", tip, tan + Vector((s * 0.6, 0, 0.4)), 0.4, 0.07, curl=0,
                       segments=4), "Tail4", "glow", glow=True)


def build_ribcage(rig):
    back = c.Chain(BACK)
    for i in range(7):
        t = 0.2 + 0.78 * i / 6
        p, _ = back.at(t)
        bone = "Hips" if p.y > -0.4 else "Spine"
        bulge = math.sin((i + 1) / 8 * math.pi)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{i}{s}", p + Vector((0, 0, -0.08)), 0.45 + 0.4 * bulge,
                          0.85 + 0.55 * bulge, s, sweep=-0.3, radius=0.075), bone, "bone")
    for i in range(5):
        y = -1.25 + i * 0.32
        z = 2.45 + 0.06 * i
        for s in (-1, 1):
            rig.add(r.tube(f"Gastralia{i}{s}", [(0, y, z - 0.04), (s * 0.38, y + 0.08, z + 0.04),
                                                (s * 0.65, y + 0.15, z + 0.28)],
                           [0.05, 0.05, 0.03], segments=4),
                    "Spine" if y < -0.4 else "Hips", "bone_shade")
    rig.add(a.blade("Sternum", (0, -1.55, 2.95), (0, -1.0, 2.6), 0.5, 0.09, width_end=0.3,
                    normal=(0, 0, 1)), "Spine", "bone_shade")
    rig.add(a.crystal("Heart", (0, -0.6, 2.9), 0.28, 0.8), "Spine", "glow", glow=True)
    for k, (dx, dy, dz) in enumerate(((0.38, 0.15, 0.15), (-0.36, -0.15, 0.0), (0.05, 0.3, -0.35))):
        rig.add(a.crystal(f"Shard{k}", (dx, -0.6 + dy, 2.9 + dz), 0.08, 0.24, sides=4),
                "Spine", "glow", glow=True)


# ---------------------------------------------------------------- membres

def build_arm(rig, s, side):
    shoulder, elbow, wrist = Vector((s * 0.5, -1.55, 3.5)), Vector((s * 0.72, -1.15, 2.75)), \
        Vector((s * 0.68, -1.95, 2.5))
    up, fore, hand = f"UpperArm_{side}", f"Forearm_{side}", f"Hand_{side}"
    rig.add(a.blade(f"Scapula{s}", (s * 0.48, -1.6, 3.6), (s * 0.55, -0.6, 4.1), 0.32, 0.08,
                    width_end=0.22, normal=(s, 0, 0.3)), "Spine", "bone")
    rig.add(a.long_bone(f"Humerus{s}", shoulder, elbow, 0.085), up, "bone")
    rig.add(a.long_bone(f"Radius{s}", elbow, wrist, 0.07), fore, "bone")
    rig.add(a.long_bone(f"Ulna{s}", elbow + Vector((s * 0.1, 0.05, -0.06)),
                        wrist + Vector((s * 0.09, 0.04, -0.05)), 0.035, condyles=False),
            fore, "bone_shade")
    # Piquants le long de l'avant-bras (là où le raptor avait ses plumes)
    for k in range(4):
        base = elbow.lerp(wrist, 0.15 + k * 0.22) + Vector((s * 0.08, 0.05, 0.05))
        rig.add(a.claw(f"Quill{s}{k}", base, (s * 0.5, 1, 0.5), 0.3 - k * 0.04, 0.045, curl=-0.1,
                       segments=4), fore, "horn")
    rig.add(r.box(f"ArmRune{s}", (0.04, 0.12, 0.12), location=elbow.lerp(wrist, 0.5)
                  + Vector((s * 0.075, 0, 0)), rotation=(0.785, 0, 0)), fore, "glow", glow=True)
    # Main à 3 doigts griffus
    for k, (dx, length) in enumerate(((-0.08, 0.3), (0.0, 0.42), (0.08, 0.34))):
        knuckle = wrist + Vector((s * dx, -length, -0.12))
        rig.add(a.long_bone(f"Finger{s}{k}", wrist, knuckle, 0.04, knob=1.4, condyles=False),
                hand, "bone")
        rig.add(a.claw(f"HandClaw{s}{k}", knuckle, (s * dx, -0.6, -1), 0.32, 0.055, curl=0.35),
                hand, "horn")


def build_leg(rig, s, side):
    hip, knee, ankle = Vector((s * 0.55, 0.7, 3.3)), Vector((s * 0.7, -0.25, 2.0)), \
        Vector((s * 0.7, 0.6, 0.8))
    thigh, shin, foot, sickle = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}", f"Sickle_{side}"
    # Bassin : ilium + pubis rétroversé (signature des raptors) + ischium
    rig.add(a.blade(f"Ilium{s}", (s * 0.32, -0.4, 3.75), (s * 0.32, 1.5, 3.85), 0.35, 0.11,
                    width_end=0.28, mid=0.8, normal=(1, 0, 0)), "Hips", "bone")
    rig.add(r.ico(f"Acetabulum{s}", 0.2, subdivisions=1, location=hip), "Hips", "bone_shade")
    rig.add(a.long_bone(f"Pubis{s}", (s * 0.3, 0.6, 3.25), (s * 0.1, 1.4, 2.2), 0.08,
                        condyles=False), "Hips", "bone")
    rig.add(a.long_bone(f"Ischium{s}", (s * 0.3, 0.95, 3.3), (s * 0.12, 1.6, 2.85), 0.06,
                        condyles=False), "Hips", "bone_shade")

    rig.add(a.long_bone(f"Femur{s}", hip, knee, 0.15), thigh, "bone")
    rig.add(r.box(f"FemurRune{s}", (0.04, 0.12, 0.12), location=hip.lerp(knee, 0.5)
                  + Vector((s * 0.14, 0, 0)), rotation=(0.785, 0, 0)), thigh, "glow", glow=True)
    rig.add(r.ico(f"Patella{s}", 0.13, subdivisions=1, location=knee + Vector((0, -0.18, 0.04))),
            shin, "bone_shade")
    rig.add(a.long_bone(f"Tibia{s}", knee, ankle, 0.12), shin, "bone")
    rig.add(a.long_bone(f"Fibula{s}", knee + Vector((s * 0.15, 0.08, -0.1)),
                        ankle + Vector((s * 0.13, 0, 0.08)), 0.045, condyles=False), shin,
            "bone_shade")
    rig.add(r.ico(f"Ankle{s}", 0.15, subdivisions=1, location=ankle), foot, "bone_shade")

    # Orteils 3 et 4 au sol
    for k, dx in enumerate((0.0, 0.17)):
        base = Vector((s * (0.72 + dx), -0.05, 0.2))
        rig.add(a.long_bone(f"Meta{s}{k}", ankle, base, 0.065, knob=1.5, condyles=False), foot,
                "bone")
        j1 = base + Vector((s * dx * 0.4, -0.32, -0.04))
        j2 = j1 + Vector((s * dx * 0.2, -0.25, -0.03))
        rig.add(a.long_bone(f"Phal{s}{k}a", base, j1, 0.055, knob=1.4, condyles=False), foot,
                "bone")
        rig.add(a.long_bone(f"Phal{s}{k}b", j1, j2, 0.05, knob=1.4, condyles=False), foot, "bone")
        rig.add(a.claw(f"Claw{s}{k}", j2, (s * dx * 0.3, -1, 0.05), 0.3, 0.07, curl=0.35), foot,
                "horn")
    # Orteil 2 : relevé, avec la grande griffe faucille (os à part pour l'animer)
    base = Vector((s * 0.56, -0.02, 0.32))
    rig.add(a.long_bone(f"Meta{s}2", ankle, base, 0.07, knob=1.5, condyles=False), foot, "bone")
    j1 = base + Vector((0, -0.25, 0.12))
    rig.add(a.long_bone(f"Phal{s}2", base, j1, 0.06, knob=1.4, condyles=False), sickle, "bone")
    rig.add(a.claw(f"Sickle{s}", j1, (0, -0.55, 1), 0.85, 0.13, curl=0.75, segments=6), sickle,
            "horn")
    rig.add(r.box(f"SickleRune{s}", (0.03, 0.08, 0.08), location=j1 + Vector((s * 0.06, 0, 0.02)),
                  rotation=(0.785, 0, 0)), sickle, "glow", glow=True)
    # Ergot arrière
    rig.add(a.claw(f"Spur{s}", ankle + Vector((0, 0.15, -0.3)), (0, 1, -0.6), 0.25, 0.05,
                   curl=0.2), foot, "horn")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_spine(rig)
    build_ribcage(rig)
    for s, side in ((1, "L"), (-1, "R")):
        build_arm(rig, s, side)
        build_leg(rig, s, side)
    return rig
