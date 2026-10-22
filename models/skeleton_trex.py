"""T-Rex squelette infernal (≈ 15 studs de long, 8 de haut) — créature animable.

Os noircis, cornes démoniaques, yeux / runes / cœur de cristal rouge braise.
Os du rig : Root, Hips, Spine, Neck, Head, Jaw, Tail1-4, Thigh/Shin/Foot_L/R,
UpperArm/Forearm_L/R, + FX_* pour les flammes (yeux, cœur, bout de queue).
"""
from mathutils import Vector

from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#6b5c55",
    "bone_light": "#9a8a80",
    "horn": "#2a1a1a",
    "claw": "#120c0c",
    "socket": "#050202",
    "tooth": "#b5a48c",
    "glow": "#ff2a10",
    "glow_hot": "#ffb030",
}

# Pose de test pour l'aperçu : gueule ouverte, tête levée, queue qui balance, pas en avant
TEST_POSE = {
    "Jaw": (28, 0, 0),
    "Neck": (-8, 0, 0),
    "Tail2": (0, 0, 15),
    "Tail3": (0, 0, 15),
    "Thigh_L": (-25, 0, 0),
    "Shin_L": (20, 0, 0),
}

# Sections du crâne : (y, demi-largeur, demi-hauteur, z centre). Le museau pointe vers -Y.
SKULL = [(-3.45, 0.7, 0.72, 6.05), (-3.9, 0.85, 0.8, 6.0), (-4.6, 0.76, 0.7, 5.9),
         (-5.4, 0.6, 0.55, 5.8), (-6.2, 0.45, 0.42, 5.75), (-6.6, 0.3, 0.3, 5.72)]
JAW = [(-3.7, 0.65, 0.25, 5.1), (-4.6, 0.62, 0.24, 4.98), (-5.6, 0.52, 0.2, 4.97),
       (-6.45, 0.36, 0.16, 5.0)]


def section(y, hw, hh, zc, segments=10):
    """Section elliptique verticale (plan XZ) à la profondeur y."""
    import math
    return [(math.cos(2 * math.pi * i / segments) * hw, y,
             zc + math.sin(2 * math.pi * i / segments) * hh) for i in range(segments)]


def interp(sections, y):
    """Interpole (demi-largeur, demi-hauteur, z centre) le long d'un profil."""
    for a, b in zip(sections, sections[1:]):
        if b[0] <= y <= a[0]:
            t = (a[0] - y) / (a[0] - b[0])
            return tuple(a[k] + (b[k] - a[k]) * t for k in (1, 2, 3))
    return sections[-1][1:]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 0.6, 4.5), (0, -0.8, 4.65), "Root")
    rig.bone("Spine", (0, -0.8, 4.65), (0, -2.3, 4.9), "Hips")
    rig.bone("Neck", (0, -2.3, 4.9), (0, -3.5, 6.0), "Spine")
    rig.bone("Head", (0, -3.5, 6.0), (0, -6.4, 6.0), "Neck")
    rig.bone("Jaw", (0, -3.7, 5.2), (0, -6.4, 5.0), "Head")
    tail = [(0, 1.0, 4.5), (0, 3.5, 4.2), (0, 6.0, 3.6), (0, 8.3, 3.0), (0, 10.2, 2.4)]
    parent = "Hips"
    for i in range(4):
        parent = rig.bone(f"Tail{i + 1}", tail[i], tail[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Thigh_{side}", (s * 0.8, 0.5, 4.2), (s * 1.0, -0.4, 2.5), "Hips")
        rig.bone(f"Shin_{side}", (s * 1.0, -0.4, 2.5), (s * 1.0, 0.6, 0.95), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 1.0, 0.6, 0.95), (s * 1.0, -0.6, 0.2), f"Shin_{side}")
        rig.bone(f"UpperArm_{side}", (s * 0.55, -2.5, 4.0), (s * 0.8, -2.9, 3.3), "Spine")
        rig.bone(f"Forearm_{side}", (s * 0.8, -2.9, 3.3), (s * 0.75, -3.4, 3.45),
                 f"UpperArm_{side}")
        rig.fx(f"Eye{side}", (s * 0.8, -4.15, 6.15), "Head")
    rig.fx("Heart", (0, -1.4, 3.75), "Spine")
    rig.fx("TailTip", (0, 10.4, 2.4), "Tail4")
    return tail


def build_skull(rig):
    skull = r.loft("Skull", [section(*s) for s in SKULL])
    r.smooth(skull, 40)
    rig.add(skull, "Head", "bone")
    jaw = r.loft("Jaw", [section(*s, segments=8) for s in JAW])
    r.smooth(jaw, 40)
    rig.add(jaw, "Jaw", "bone")

    for s in (-1, 1):
        # Orbites sombres + yeux de braise
        socket = r.ico(f"Socket{s}", 0.3, location=(s * 0.66, -4.1, 6.15), scale=(0.6, 1, 1))
        rig.add(socket, "Head", "socket")
        eye = r.ico(f"Eye{s}", 0.16, subdivisions=2, location=(s * 0.75, -4.15, 6.15))
        rig.add(eye, "Head", "glow", glow=True)
        # Ouvertures du crâne (fenêtres temporale et antorbitale), narines
        for name, loc, size in (("Temporal", (s * 0.6, -3.6, 5.95), (0.5, 0.9, 1.3)),
                                ("Antorbital", (s * 0.5, -5.0, 5.82), (0.5, 1.6, 0.8)),
                                ("Nostril", (s * 0.2, -6.45, 5.88), (0.5, 0.6, 0.4))):
            hole = r.ico(f"{name}{s}", 0.25, location=loc, scale=size)
            rig.add(hole, "Head", "socket")

        # Cornes démoniaques recourbées vers l'arrière + petites cornes au-dessus des yeux
        horn = c.spike(f"Horn{s}", (s * 0.5, -3.7, 6.55), (s * 1.35, -2.4, 7.5), 0.2,
                       bend=(s * 0.35, 0.1, 0.45))
        rig.add(horn, "Head", "horn")
        brow = c.spike(f"Brow{s}", (s * 0.6, -4.3, 6.55), (s * 0.85, -4.0, 7.05), 0.11,
                       bend=(s * 0.05, 0, 0.1))
        rig.add(brow, "Head", "horn")

        # Dents : rangée du haut (vers le bas) et du bas (vers le haut)
        y = -4.2
        while y > -6.45:
            hw, hh, zc = interp(SKULL, y)
            tooth = c.spike(f"ToothU{s}{y:.1f}", (s * hw * 0.82, y, zc - hh * 0.75),
                            (s * hw * 0.8, y - 0.05, zc - hh * 0.75 - 0.38), 0.075, segments=4)
            rig.add(tooth, "Head", "tooth")
            jhw, jhh, jzc = interp(JAW, y - 0.15)
            ltooth = c.spike(f"ToothL{s}{y:.1f}", (s * jhw * 0.8, y - 0.15, jzc + jhh * 0.6),
                             (s * jhw * 0.78, y - 0.18, jzc + jhh * 0.6 + 0.28), 0.06, segments=4)
            rig.add(ltooth, "Jaw", "tooth")
            y -= 0.3

    # Runes lumineuses sur le dessus du crâne
    for i, y in enumerate((-4.5, -5.0, -5.5)):
        hw, hh, zc = interp(SKULL, y)
        size = 0.2 - i * 0.04
        rune = r.box(f"Rune{i}", (size, size, 0.06), location=(0, y, zc + hh - 0.01),
                     rotation=(0, 0, 0.785))
        rig.add(rune, "Head", "glow", glow=True)


def build_spine(rig, tail_points):
    # Dos : vertèbres à grandes épines (crête), du bassin vers les épaules
    back = c.Chain([(0, 0.8, 4.5), (0, -0.8, 4.65), (0, -2.3, 4.9)])
    n = 9
    for i in range(n):
        t = i / (n - 1)
        p, tan = back.at(t)
        bone = "Hips" if p.y > -0.8 else "Spine"
        c.vertebra(rig, f"Back{i}", p, tan, 0.38, bone, "bone_light",
                   spine_height=0.55 + 0.35 * (1 - abs(t - 0.4)), spine_color="horn")

    neck = c.Chain([(0, -2.3, 4.9), (0, -3.0, 5.5), (0, -3.5, 5.95)])
    for i in range(4):
        p, tan = neck.at(i / 3)
        c.vertebra(rig, f"Neck{i}", p, tan, 0.34, "Neck", "bone_light",
                   spine_height=0.35, spine_color="horn")

    # Queue : vertèbres de plus en plus petites, chevrons dessous
    tail = c.Chain(tail_points)
    n = 16
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(4, int((p.y - tail_points[0][1]) / 2.3) + 1)}"
        size = 0.38 - 0.26 * t
        c.vertebra(rig, f"Tail{i}", p, tan, size, bone, "bone_light",
                   spine_height=size * 1.4, spine_color="horn")
        if i < 11:
            chevron = c.spike(f"Chevron{i}", p - Vector((0, 0, size * 0.3)),
                              p - Vector((0, -size * 0.6, size * 2.2)), size * 0.25, segments=4)
            rig.add(chevron, bone, "bone")
    # Pointe de queue en cristal
    tip, tan = tail.at(1.0)
    crystal = c.spike("TailCrystal", tip, tip + tan * 0.9, 0.2, segments=5)
    rig.add(crystal, "Tail4", "glow", glow=True)


def build_ribcage(rig):
    back = c.Chain([(0, 0.8, 4.5), (0, -0.8, 4.65), (0, -2.3, 4.9)])
    n = 8
    for i in range(n):
        t = 0.3 + 0.65 * i / (n - 1)
        p, _ = back.at(t)
        bulge = 1 - abs(i - 3.5) / 4.5
        bone = "Hips" if p.y > -0.8 else "Spine"
        for s in (-1, 1):
            rb = c.rib(f"Rib{i}{s}", p - Vector((0, 0, 0.1)), 0.7 + 0.55 * bulge,
                       1.3 + 0.7 * bulge, s, radius=0.075)
            rig.add(rb, bone, "bone")
    # Cœur de cristal infernal flottant dans la cage + éclats autour
    heart = r.ico("Heart", 0.42, subdivisions=1, location=(0, -1.4, 3.75), scale=(1, 1, 1.5))
    rig.add(heart, "Spine", "glow", glow=True)
    for k, (dx, dz) in enumerate(((0.55, 0.3), (-0.55, 0.1), (0.1, -0.75))):
        shard = c.spike(f"Shard{k}", (dx, -1.4, 3.75 + dz),
                        (dx * 1.4, -1.5, 3.75 + dz * 1.6 + 0.2), 0.08, segments=4)
        rig.add(shard, "Spine", "glow", glow=True)


def build_pelvis(rig):
    for s in (-1, 1):
        ilium = r.box(f"Ilium{s}", (0.18, 2.4, 0.9), location=(s * 0.42, 0.45, 4.65),
                      bevel_width=0.06)
        rig.add(ilium, "Hips", "bone")
        socket = r.ico(f"HipJoint{s}", 0.3, subdivisions=2, location=(s * 0.8, 0.5, 4.2))
        rig.add(socket, "Hips", "bone_light")
        pubis = c.long_bone(f"Pubis{s}", (s * 0.3, 0.0, 4.3), (s * 0.12, -0.9, 2.65), 0.12)
        rig.add(pubis, "Hips", "bone")
        ischium = c.long_bone(f"Ischium{s}", (s * 0.3, 1.0, 4.3), (s * 0.1, 1.9, 3.1), 0.1)
        rig.add(ischium, "Hips", "bone")
    boot = r.ico("PubicBoot", 0.3, subdivisions=2, location=(0, -1.0, 2.55), scale=(0.7, 1.7, 0.5))
    rig.add(boot, "Hips", "bone_light")


def build_leg(rig, s, side):
    hip, knee, ankle = Vector((s * 0.8, 0.5, 4.2)), Vector((s * 1.0, -0.4, 2.5)), \
        Vector((s * 1.0, 0.6, 0.95))
    femur = c.long_bone(f"Femur{s}", hip, knee, 0.2)
    rig.add(femur, f"Thigh_{side}", "bone")
    # Rune lumineuse sur la face externe du fémur
    mid = hip.lerp(knee, 0.5)
    rune = r.box(f"ThighRune{s}", (0.06, 0.18, 0.18), location=mid + Vector((s * 0.2, 0, 0)),
                 rotation=(0.785, 0, 0))
    rig.add(rune, f"Thigh_{side}", "glow", glow=True)

    knee_ball = r.ico(f"Knee{s}", 0.26, subdivisions=2, location=knee)
    rig.add(knee_ball, f"Shin_{side}", "bone_light")
    tibia = c.long_bone(f"Tibia{s}", knee, ankle, 0.16)
    rig.add(tibia, f"Shin_{side}", "bone")
    fibula = c.long_bone(f"Fibula{s}", knee + Vector((s * 0.15, 0.1, -0.1)),
                         ankle + Vector((s * 0.15, 0, 0.1)), 0.06)
    rig.add(fibula, f"Shin_{side}", "bone")
    ankle_ball = r.ico(f"Ankle{s}", 0.2, subdivisions=2, location=ankle)
    rig.add(ankle_ball, f"Foot_{side}", "bone_light")

    # 3 orteils : métatarse + phalange + griffe
    for k, dx in enumerate((-0.28, 0.0, 0.28)):
        base = Vector((s * 1.0 + dx, -0.4, 0.25))
        meta = c.long_bone(f"Meta{s}{k}", ankle, base, 0.08)
        rig.add(meta, f"Foot_{side}", "bone")
        toe_tip = base + Vector((dx * 0.5, -0.5 + abs(dx) * 0.4, -0.08))
        toe = c.long_bone(f"Toe{s}{k}", base, toe_tip, 0.065)
        rig.add(toe, f"Foot_{side}", "bone")
        claw = c.spike(f"Claw{s}{k}", toe_tip, toe_tip + Vector((dx * 0.2, -0.38, -0.12)), 0.08,
                       segments=5, bend=(0, 0, 0.06))
        rig.add(claw, f"Foot_{side}", "claw")


def build_arm(rig, s, side):
    shoulder, elbow, wrist = Vector((s * 0.55, -2.5, 4.0)), Vector((s * 0.8, -2.9, 3.3)), \
        Vector((s * 0.75, -3.4, 3.45))
    scapula = c.long_bone(f"Scapula{s}", (s * 0.6, -1.9, 4.75), shoulder, 0.1)
    rig.add(scapula, "Spine", "bone")
    upper = c.long_bone(f"Humerus{s}", shoulder, elbow, 0.08)
    rig.add(upper, f"UpperArm_{side}", "bone")
    lower = c.long_bone(f"Radius{s}", elbow, wrist, 0.065)
    rig.add(lower, f"Forearm_{side}", "bone")
    for k, dx in enumerate((-0.07, 0.07)):
        tip = wrist + Vector((dx, -0.25, -0.05))
        finger = c.long_bone(f"Finger{s}{k}", wrist, tip, 0.04)
        rig.add(finger, f"Forearm_{side}", "bone")
        claw = c.spike(f"HandClaw{s}{k}", tip, tip + Vector((0, -0.18, -0.12)), 0.05,
                       segments=4)
        rig.add(claw, f"Forearm_{side}", "claw")


def build(pal):
    rig = c.Rig(pal)
    tail = build_rig(rig)
    build_skull(rig)
    build_spine(rig, tail)
    build_ribcage(rig)
    build_pelvis(rig)
    for s, side in ((1, "L"), (-1, "R")):
        build_leg(rig, s, side)
        build_arm(rig, s, side)
    return rig
