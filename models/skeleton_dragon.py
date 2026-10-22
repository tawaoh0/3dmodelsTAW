"""Dragon squelette ailé démoniaque (≈ 20 studs de long, 18 d'envergure) — créature animable.

Crâne en coin au museau crochu, crête osseuse, yeux en fente, longues cornes
plaquées en arrière et collerette de piques palmée, long cou en S, quatre pattes griffues,
deux ailes à quatre doigts tendues d'une membrane violette déchirée, queue
terminée par une lame de cristal. Lueurs violettes : yeux, gorge, cœur, runes.

3 pièces Roblox : corps, tête (+ cou), ailes, plus le mesh lumineux.
Os du rig : Root, Hips, Chest, Neck1-2, Head, Jaw, Tail1-5,
UpperArm/Forearm/Hand_L/R (pattes avant), Thigh/Shin/Foot_L/R (arrière),
Wing1/Wing2/WingFinger1-4_L/R (ailes), + FX_* (yeux, gueule, cœur, queue).
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#dcd3c8",
    "bone_shade": "#a89a8c",
    "tooth": "#f4eee0",
    "horn": "#1c1424",
    "horn_tip": "#4a1a66",
    "disc": "#3b2350",
    "membrane": "#3d1b58",
    "glow": "#b44dff",
    "glow_hot": "#f2c6ff",
}

TEST_POSE = {
    "Jaw": (30, 0, 0),
    "Neck1": (-12, 0, 0),
    "Neck2": (-10, 0, 0),
    "Head": (15, 0, 0),
    "Wing1_L": (0, 0, -25),
    "Wing2_L": (0, 0, 35),
    "WingFinger2_L": (0, 0, 15),
    "WingFinger3_L": (0, 0, 25),
    "UpperArm_L": (-30, 0, 0),
    "Forearm_L": (40, 0, 0),
    "Tail3": (0, 0, 20),
    "Tail4": (0, 0, 20),
}

# Vue de 3/4 avant, un peu en hauteur, pour voir les ailes déployées
VIEW = (0.4, -1.0, 0.8)

BACK = [(0, 1.6, 4.9), (0, 0.4, 5.0), (0, -1.0, 5.1), (0, -2.3, 5.25)]
NECK = [(0, -2.3, 5.25), (0, -3.1, 5.7), (0, -3.6, 6.5), (0, -4.2, 7.15), (0, -4.75, 7.4)]
TAIL = [(0, 1.6, 4.9), (0, 3.8, 4.5), (0, 6.2, 3.8), (0, 8.4, 3.0), (0, 10.4, 2.5),
        (0, 12.3, 2.6)]

# Crâne en coin : (y, demi-largeur dessus, joues, bord dentaire, z dessus, z bord dentaire)
SKULL = [(-4.7, 0.7, 1.05, 0.8, 7.95, 7.0), (-5.2, 0.62, 0.95, 0.72, 8.05, 6.96),
         (-5.9, 0.42, 0.66, 0.55, 7.82, 6.98), (-6.7, 0.3, 0.46, 0.4, 7.52, 7.0),
         (-7.5, 0.22, 0.34, 0.32, 7.34, 7.02), (-8.1, 0.12, 0.2, 0.2, 7.22, 7.05)]
JAW = [(-4.75, 0.5, 0.85, 0.7, 6.97, 6.5), (-5.7, 0.42, 0.68, 0.55, 6.95, 6.45),
       (-6.8, 0.3, 0.45, 0.36, 6.95, 6.56), (-8.0, 0.12, 0.2, 0.18, 6.95, 6.72)]

# Aile gauche (x > 0) ; l'aile droite est le miroir
WING_ROOT = Vector((0.7, -1.5, 5.7))
ELBOW = Vector((2.9, -0.6, 7.6))
WRIST = Vector((5.0, -0.9, 9.3))
TIPS = [Vector((7.6, -0.4, 11.2)), Vector((8.7, 1.2, 8.6)), Vector((7.8, 2.8, 6.1)),
        Vector((5.6, 3.5, 4.7))]
BODY_ROOT = Vector((0.55, -1.7, 5.55))
BODY_MID = Vector((0.55, 0.2, 5.15))
BODY_HIP = Vector((0.55, 1.9, 4.95))


def mirror(v, s):
    return Vector((v.x * s, v.y, v.z))


def width_at(sections, y, idx=3):
    for s0, s1 in zip(sections, sections[1:]):
        if s1[0] <= y <= s0[0]:
            t = (s0[0] - y) / (s0[0] - s1[0])
            return s0[idx] + (s1[idx] - s0[idx]) * t
    return sections[-1][idx]


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 1.6, 4.9), (0, -0.3, 5.05), "Root")
    rig.bone("Chest", (0, -0.3, 5.05), (0, -2.3, 5.25), "Hips")
    rig.bone("Neck1", (0, -2.3, 5.25), (0, -3.6, 6.5), "Chest")
    rig.bone("Neck2", (0, -3.6, 6.5), (0, -4.75, 7.4), "Neck1")
    rig.bone("Head", (0, -4.75, 7.4), (0, -8.1, 7.2), "Neck2")
    rig.bone("Jaw", (0, -4.85, 6.95), (0, -8.0, 6.8), "Head")
    parent = "Hips"
    for i in range(5):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"UpperArm_{side}", (s * 0.8, -2.0, 4.4), (s * 1.0, -1.5, 2.7), "Chest")
        rig.bone(f"Forearm_{side}", (s * 1.0, -1.5, 2.7), (s * 1.0, -2.2, 1.05),
                 f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", (s * 1.0, -2.2, 1.05), (s * 1.0, -2.9, 0.3), f"Forearm_{side}")
        rig.bone(f"Thigh_{side}", (s * 0.85, 1.4, 4.4), (s * 1.05, 0.3, 2.8), "Hips")
        rig.bone(f"Shin_{side}", (s * 1.05, 0.3, 2.8), (s * 1.05, 1.5, 1.3), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 1.05, 1.5, 1.3), (s * 1.05, 0.4, 0.3), f"Shin_{side}")
        rig.bone(f"Wing1_{side}", mirror(WING_ROOT, s), mirror(ELBOW, s), "Chest")
        rig.bone(f"Wing2_{side}", mirror(ELBOW, s), mirror(WRIST, s), f"Wing1_{side}")
        for i, tip in enumerate(TIPS):
            rig.bone(f"WingFinger{i + 1}_{side}", mirror(WRIST, s), mirror(tip, s),
                     f"Wing2_{side}")
        rig.fx(f"Eye{side}", (s * 0.55, -5.45, 7.6), "Head")
    rig.fx("Mouth", (0, -5.6, 6.95), "Head")
    rig.fx("Heart", (0, -1.0, 3.95), "Chest")
    rig.fx("TailTip", (0, 13.3, 2.6), "Tail5")


# ---------------------------------------------------------------- tête

def build_head(rig):
    head = dict(part="Head")

    # Crâne en coin : large à l'arrière, museau long et pointu, profil bas
    skull = a.loft_profile("Skull", SKULL)
    tilt = -0.3   # fentes inclinées (avant plus bas) → regard mauvais
    cutters = []
    for center, ry, rz in (((0, -5.45, 7.6), 0.42, 0.17),      # orbites en fente
                           ((0, -6.5, 7.28), 0.5, 0.14),       # fenêtres antorbitales
                           ((0, -4.85, 7.42), 0.14, 0.3),      # fenêtres temporales
                           ((0, -7.85, 7.25), 0.12, 0.08)):    # narines
        cutter = a.hole_x(center, ry, rz)
        a.rotate_obj(cutter, "X", tilt, center)
        cutters.append(cutter)
    a.cut(skull, cutters)
    rig.add(skull, "Head", "bone", **head)

    # Crête sagittale (quille osseuse sur le dessus du crâne)
    keel = a.blade("Keel", (0, -4.9, 8.05), (0, -7.3, 7.35), 0.32, 0.12, width_end=0.12,
                   normal=(1, 0, 0), bevel=0.02)
    rig.add(keel, "Head", "bone_shade", **head)
    # Bec crochu au bout du museau + ergot sous le menton
    rig.add(a.claw("Beak", (0, -8.05, 7.22), (0, -0.7, -1), 0.5, 0.17, curl=0.25),
            "Head", "horn", **head)
    # Rangée de cornes sur le museau, de plus en plus grandes vers les yeux
    for k, (y, size) in enumerate(((-7.55, 0.22), (-7.05, 0.3), (-6.5, 0.4))):
        z = width_at(SKULL, y, 4) - 0.02
        rig.add(a.claw(f"NoseHorn{k}", (0, y, z), (0, 0.55, 1), size, 0.06 + size * 0.2,
                       curl=-0.15), "Head", "horn", **head)

    for s in (-1, 1):
        # Arcade sourcilière en lame, prolongée par une pointe vers l'arrière
        brow = a.blade(f"Brow{s}", (s * 0.32, -6.0, 7.85), (s * 0.82, -4.95, 8.1), 0.3, 0.1,
                       width_end=0.2, normal=(0, 0.3, 1), bevel=0.02)
        rig.add(brow, "Head", "bone_shade", **head)
        rig.add(a.claw(f"BrowSpike{s}", (s * 0.82, -4.95, 8.1), (s * 0.5, 1, 0.25), 0.45, 0.08,
                       curl=-0.1), "Head", "horn", **head)
        # Œil en fente
        eye = r.ico(f"Eye{s}", 0.15, subdivisions=2, location=(s * 0.55, -5.45, 7.6),
                    scale=(0.6, 2.2, 0.9))
        a.rotate_obj(eye, "X", tilt, (0, 0, 0))   # sommets locaux, centrés sur l'œil
        rig.add(eye, "Head", "glow", glow=True)

        # Deux longues cornes plaquées vers l'arrière
        horn = a.ridged_horn(f"Horn{s}", [(s * 0.5, -4.95, 8.0), (s * 0.7, -4.0, 8.45),
                                          (s * 0.9, -2.9, 8.7), (s * 1.0, -1.8, 8.65),
                                          (s * 1.0, -1.0, 8.35)], 0.27, ridges=7)
        rig.add(horn, "Head", "horn", **head)
        rig.add(a.claw(f"HornTip{s}", (s * 1.0, -1.02, 8.36), (0, 0.6, -0.5), 0.2, 0.06),
                "Head", "horn_tip", **head)

        # Collerette : éventail de piques reliées par une membrane déchirée
        bases = [Vector((s * 0.95, -4.8, 7.85 - k * 0.32)) for k in range(4)]
        dirs = [Vector((s * 0.55, 0.55, 0.75)), Vector((s * 0.75, 0.7, 0.25)),
                Vector((s * 0.75, 0.7, -0.2)), Vector((s * 0.55, 0.6, -0.6))]
        tips = []
        for k, (b, d, length) in enumerate(zip(bases, dirs, (1.25, 1.15, 0.95, 0.7))):
            tip = b + d.normalized() * length
            tips.append(tip)
            rig.add(a.claw(f"Frill{s}{k}", b, d, length, 0.09 - k * 0.012, curl=-0.05),
                    "Head", "horn", **head)
        outline = [(tuple(bases[0]), {"Head": 1})]
        for k in range(4):
            outline.append((tuple(tips[k]), {"Head": 1}))
            if k < 3:
                for p, _ in a.tattered_edge(tips[k], tips[k + 1], {"Head": 1}, {"Head": 1},
                                            bases[k] * 0.5 + bases[k + 1] * 0.5, depth=0.22,
                                            notches=1, seed=20 + k + s):
                    outline.append((p, {"Head": 1}))
        outline.append((tuple(bases[3]), {"Head": 1}))
        frill = a.membrane(f"FrillMembrane{s}", outline, thickness=0.04)
        rig.pal.paint(frill, "membrane")
        frill["part"] = "Head"

        # Épines à l'arrière de la mâchoire
        rig.add(a.claw(f"JawSpike{s}", (s * 0.6, -4.95, 6.6), (s * 0.6, 0.7, -0.4), 0.4, 0.09,
                       curl=-0.1), "Jaw", "horn", **head)

    rig.add(a.claw("ChinSpike", (0, -7.5, 6.62), (0, 0.1, -1), 0.4, 0.11, curl=0.15),
            "Jaw", "horn", **head)
    # Rune du front, entre les arcades
    rune = r.box("Rune", (0.12, 0.12, 0.05), location=(0, -5.75, width_at(SKULL, -5.75, 4) + 0.03),
                 rotation=(0, 0, 0.785))
    rig.add(rune, "Head", "glow", glow=True)
    rig.add(r.ico("Throat", 0.28, subdivisions=2, location=(0, -5.1, 6.95), scale=(1.3, 1, 0.6)),
            "Head", "glow", glow=True)

    # Crocs : longs devant (crocs de vipère), plus courts vers l'arrière
    for jaw, sections, z, direction, bone in ((False, SKULL, 7.03, (0, 0.2, -1), "Head"),
                                              (True, JAW, 6.93, (0, -0.2, 1), "Jaw")):
        y, k = -7.85, 0
        while y < -5.3:
            for s in (-1, 1):
                x = s * width_at(sections, y) * (0.72 if jaw else 0.88)
                length = (0.55 if k == 0 else 0.36 - 0.02 * k) * (0.8 if jaw else 1)
                rig.add(a.claw(f"Tooth{bone}{s}{k}", (x, y, z), direction, length,
                               0.075 if jaw else 0.085, curl=-0.06, segments=4),
                        bone, "tooth", **head)
            y += 0.32
            k += 1

    jaw = a.loft_profile("Jaw", JAW)
    a.cut(jaw, [a.hole_x((0, -5.5, 6.72), 0.35, 0.1)])
    rig.add(jaw, "Jaw", "bone", **head)


# ---------------------------------------------------------------- colonne

def spine_run(rig, name, chain, count, bone_of, size_of, spine_of, part=None, tips=True,
              reverse=False):
    ch = c.Chain(chain)
    kw = dict(part=part) if part else {}
    for i in range(count):
        t = i / (count - 1)
        p, tan = ch.at(t)
        size = size_of(t)
        bone = bone_of(t)
        h = spine_of(t)
        v = a.vertebra(f"{name}{i}", p, tan if reverse else -tan, size, spine=h,
                       lean=-0.3 if reverse else 0.3, transverse=size > 0.22)
        rig.add(v, bone, "bone", **kw)
        if i < count - 1:
            q, tq = ch.at((i + 0.5) / (count - 1))
            rig.add(a.disc(f"{name}Disc{i}", q, tq, size), bone, "disc", **kw)
        if tips and h > 0.3:
            up = Vector((0, 0, 1))
            back = tan if reverse else -tan
            top = p + up * (size * 0.7 + size * h) - back * size * h * (-0.3 if reverse else 0.3)
            rig.add(a.claw(f"{name}Spike{i}", top - up * 0.08, (0, 0.4, 1), 0.2 + size * 0.5,
                           0.05 + size * 0.15, curl=-0.1), bone, "horn", **kw)


def build_spine(rig):
    spine_run(rig, "Back", BACK, 8, lambda t: "Hips" if t < 0.45 else "Chest",
              lambda t: 0.4, lambda t: 1.0 + 0.3 * math.sin(t * math.pi))
    spine_run(rig, "Neck", NECK, 8, lambda t: "Neck1" if t < 0.5 else "Neck2",
              lambda t: 0.44 - 0.08 * t, lambda t: 0.65, part="Head")
    spine_run(rig, "Tail", TAIL, 16, lambda t: f"Tail{min(5, int(t * 5 * 0.999) + 1)}",
              lambda t: 0.38 - 0.26 * t, lambda t: 1.1 - 0.6 * t, reverse=True)
    # Lame de cristal en pointe de flèche au bout de la queue
    tip, tan = c.Chain(TAIL).at(1.0)
    spade = a.blade("TailSpade", tip, tip + tan * 1.6, 0.2, 0.1, width_end=0.02, mid=0.75,
                    normal=(0, 0, 1), bevel=0)
    rig.add(spade, "Tail5", "glow", glow=True)
    for s in (-1, 1):   # barbes de la pointe de flèche
        rig.add(a.claw(f"SpadeBarb{s}", tip + tan * 0.5, Vector((s, 0, 0)) - tan * 0.8, 0.55,
                       0.07, curl=0), "Tail5", "glow", glow=True)


def build_ribcage(rig):
    back = c.Chain(BACK)
    for i in range(8):
        t = 0.25 + 0.72 * i / 7
        p, _ = back.at(t)
        bone = "Hips" if t < 0.45 else "Chest"
        bulge = math.sin((i + 1) / 9 * math.pi)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{i}{s}", p + Vector((0, 0, -0.1)), 0.7 + 0.55 * bulge,
                          1.1 + 0.7 * bulge, s, sweep=-0.35, radius=0.1), bone, "bone")
    rig.add(a.blade("Sternum", (0, -2.0, 3.85), (0, -0.6, 3.5), 0.75, 0.12, width_end=0.4,
                    normal=(0, 0, 1)), "Chest", "bone_shade")
    rig.add(a.crystal("Heart", (0, -1.0, 3.95), 0.38, 1.0), "Chest", "glow", glow=True)
    for k, (dx, dy, dz) in enumerate(((0.5, 0.25, 0.2), (-0.5, -0.2, 0.05), (0.05, 0.4, -0.45))):
        rig.add(a.crystal(f"Shard{k}", (dx, -1.0 + dy, 3.95 + dz), 0.11, 0.32, sides=4),
                "Chest", "glow", glow=True)


# ---------------------------------------------------------------- pattes

def digits(rig, name, wrist, base_y, base_z, spread, side_x, bone, count=4, length=0.4,
           radius=0.075, back_toe=False):
    for k in range(count):
        dx = (k - (count - 1) / 2) * spread
        base = Vector((side_x + dx, base_y, base_z))
        rig.add(a.long_bone(f"{name}Meta{k}", wrist, base, radius, knob=1.5, condyles=False),
                bone, "bone")
        tip = base + Vector((dx * 0.4, -length, -0.08))
        rig.add(a.long_bone(f"{name}Phal{k}", base, tip, radius * 0.9, knob=1.4,
                            condyles=False), bone, "bone")
        rig.add(a.claw(f"{name}Claw{k}", tip, (dx * 0.3, -1, 0.1), 0.45, radius * 1.5, curl=0.4),
                bone, "horn")
    if back_toe:
        rig.add(a.claw(f"{name}Spur", wrist + Vector((0, 0.2, -0.45)), (0, 1, -0.6), 0.38,
                       0.08, curl=0.25), bone, "horn")


def build_front_leg(rig, s, side):
    shoulder, elbow, wrist = Vector((s * 0.8, -2.0, 4.4)), Vector((s * 1.0, -1.5, 2.7)), \
        Vector((s * 1.0, -2.2, 1.05))
    rig.add(a.blade(f"Scapula{s}", (s * 0.75, -2.0, 4.5), (s * 0.8, -0.9, 5.45), 0.5, 0.12,
                    width_end=0.35, normal=(s, 0, 0.3)), "Chest", "bone")
    rig.add(a.long_bone(f"Humerus{s}", shoulder, elbow, 0.17), f"UpperArm_{side}", "bone")
    rig.add(a.long_bone(f"Radius{s}", elbow, wrist, 0.13), f"Forearm_{side}", "bone")
    rig.add(a.long_bone(f"Ulna{s}", elbow + Vector((s * 0.18, 0.12, 0.1)),
                        wrist + Vector((s * 0.15, 0.05, 0.1)), 0.06, knob=1.3, condyles=False),
            f"Forearm_{side}", "bone_shade")
    rig.add(a.claw(f"Elbow{s}", elbow + Vector((0, 0.15, 0)), (0, 1, 0.3), 0.4, 0.1, curl=0),
            f"Forearm_{side}", "horn")
    digits(rig, f"Hand{s}", wrist, -2.55, 0.3, 0.22, s * 1.0, f"Hand_{side}", length=0.35)


def build_hind_leg(rig, s, side):
    hip, knee, ankle = Vector((s * 0.85, 1.4, 4.4)), Vector((s * 1.05, 0.3, 2.8)), \
        Vector((s * 1.05, 1.5, 1.3))
    # Bassin : ilium en lame + os pubiens
    rig.add(a.blade(f"Ilium{s}", (s * 0.45, 0.2, 4.95), (s * 0.45, 2.8, 5.05), 0.5, 0.15,
                    width_end=0.35, mid=1.1, normal=(1, 0, 0)), "Hips", "bone")
    rig.add(r.ico(f"Acetabulum{s}", 0.27, subdivisions=1, location=hip), "Hips", "bone_shade")
    rig.add(a.long_bone(f"Pubis{s}", (s * 0.4, 1.0, 4.4), (s * 0.15, 0.4, 3.3), 0.09,
                        condyles=False), "Hips", "bone_shade")
    rig.add(a.long_bone(f"Femur{s}", hip, knee, 0.2), f"Thigh_{side}", "bone")
    mid = hip.lerp(knee, 0.5)
    rig.add(r.box(f"FemurRune{s}", (0.05, 0.16, 0.16), location=mid + Vector((s * 0.19, 0, 0)),
                  rotation=(0.785, 0, 0)), f"Thigh_{side}", "glow", glow=True)
    rig.add(r.ico(f"Patella{s}", 0.18, subdivisions=1, location=knee + Vector((0, -0.26, 0.05))),
            f"Shin_{side}", "bone_shade")
    rig.add(a.long_bone(f"Tibia{s}", knee, ankle, 0.16), f"Shin_{side}", "bone")
    rig.add(r.ico(f"Ankle{s}", 0.2, subdivisions=1, location=ankle), f"Foot_{side}",
            "bone_shade")
    digits(rig, f"Foot{s}", ankle, 0.75, 0.3, 0.28, s * 1.05, f"Foot_{side}", count=3,
           length=0.45, radius=0.085, back_toe=True)


# ---------------------------------------------------------------- ailes

def build_wing(rig, s, side):
    wing = dict(part="Wings")
    root, elbow, wrist = mirror(WING_ROOT, s), mirror(ELBOW, s), mirror(WRIST, s)
    tips = [mirror(t, s) for t in TIPS]
    w1, w2 = f"Wing1_{side}", f"Wing2_{side}"
    fingers = [f"WingFinger{i + 1}_{side}" for i in range(4)]

    # Os de l'aile : humérus, radius + cubitus, 4 doigts articulés
    rig.add(a.long_bone(f"WingHumerus{s}", root, elbow, 0.16), w1, "bone", **wing)
    rig.add(a.long_bone(f"WingRadius{s}", elbow, wrist, 0.12), w2, "bone", **wing)
    rig.add(a.long_bone(f"WingUlna{s}", elbow + Vector((0, 0.15, -0.12)),
                        wrist + Vector((0, 0.12, -0.1)), 0.06, condyles=False), w2,
            "bone_shade", **wing)
    rig.add(r.ico(f"WingWrist{s}", 0.22, subdivisions=1, location=wrist), w2, "bone_shade",
            **wing)
    for i, (tip, bone) in enumerate(zip(tips, fingers)):
        knuckle = wrist.lerp(tip, 0.45)
        rig.add(a.long_bone(f"WingFingerA{s}{i}", wrist, knuckle, 0.085, knob=1.5,
                            condyles=False), bone, "bone", **wing)
        rig.add(a.long_bone(f"WingFingerB{s}{i}", knuckle, tip, 0.06, knob=1.4,
                            condyles=False), bone, "bone", **wing)
        rig.add(a.claw(f"WingTipClaw{s}{i}", tip, tip - wrist, 0.3, 0.05, curl=0.1), bone,
                "horn", **wing)
    # Griffe du pouce, vers l'avant
    rig.add(a.claw(f"Thumb{s}", wrist + Vector((0, -0.1, 0.1)), (s * 0.3, -1, 0.5), 0.55, 0.11,
                   curl=0.3), w2, "horn", **wing)
    # Rune lumineuse sur l'avant-bras
    rig.add(r.box(f"WingRune{s}", (0.14, 0.14, 0.05), location=elbow.lerp(wrist, 0.5)
                  + Vector((0, 0, 0.12)), rotation=(0, 0, 0.785)), w2, "glow", glow=True)

    # Membrane : un panneau entre chaque paire de doigts, bords festonnés et déchirés
    W = {w2: 1.0}
    panels = []
    for i in range(3):
        edge = a.tattered_edge(tips[i], tips[i + 1], {fingers[i]: 1}, {fingers[i + 1]: 1},
                               wrist, depth=0.8 - 0.1 * i, notches=3, seed=10 * s + i)
        panels.append([(wrist, W), (tips[i], {fingers[i]: 1})] + edge
                      + [(tips[i + 1], {fingers[i + 1]: 1})])
    # Panneau intérieur : dernier doigt → hanche → dos → épaule → coude
    hip, mid, body_root = mirror(BODY_HIP, s), mirror(BODY_MID, s), mirror(BODY_ROOT, s)
    edge = a.tattered_edge(tips[3], hip, {fingers[3]: 1}, {"Hips": 1}, wrist.lerp(mid, 0.5),
                           depth=0.7, notches=3, seed=7 * s)
    panels.append([(wrist, W), (tips[3], {fingers[3]: 1})] + edge
                  + [(hip, {"Hips": 1}), (mid, {"Chest": 0.5, "Hips": 0.5}),
                     (body_root, {"Chest": 1}), (elbow, {w1: 0.5, w2: 0.5})])
    # Propatagium : petite membrane entre épaule et poignet, devant le coude
    lead = root.lerp(wrist, 0.5) + Vector((0, -0.35, 0.3))
    panels.append([(wrist, W), (elbow, {w1: 0.5, w2: 0.5}), (root, {w1: 1}),
                   (lead, {w1: 0.5, w2: 0.5})])
    for k, outline in enumerate(panels):
        m = a.membrane(f"Membrane{s}{k}", [(tuple(p), w) for p, w in outline])
        rig.pal.paint(m, "membrane")
        m["part"] = "Wings"


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_spine(rig)
    build_ribcage(rig)
    for s, side in ((1, "L"), (-1, "R")):
        build_front_leg(rig, s, side)
        build_hind_leg(rig, s, side)
        build_wing(rig, s, side)
    return rig
