"""T-Rex squelette démoniaque (≈ 17 studs de long, 9 de haut) — créature animable.

Crâne anatomique aux ouvertures découpées (orbites, fenêtres, narines), mâchoire
articulée garnie de crocs, colonne de vertèbres à épines en lame, cage
thoracique et côtes ventrales, bassin en lames, os longs à condyles, griffes et
cornes annelées noires, yeux / cœur de cristal / runes rouge braise.

Os du rig : Root, Hips, Spine, Neck, Head, Jaw, Tail1-4, Thigh/Shin/Foot_L/R,
UpperArm/Forearm_L/R, + FX_* pour les flammes (yeux, cœur, gueule, queue).
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#ddd0b8",
    "bone_shade": "#a8977c",
    "tooth": "#f4eee0",
    "horn": "#231a20",
    "horn_tip": "#4a1418",
    "disc": "#5a2a2a",
    "glow": "#ff2418",
    "glow_hot": "#ffb070",
}

TEST_POSE = {
    "Jaw": (30, 0, 0),
    "Neck": (-10, 0, 0),
    "Head": (-6, 0, 0),
    "Tail2": (0, 0, 15),
    "Tail3": (0, 0, 15),
    "Thigh_L": (-25, 0, 0),
    "Shin_L": (20, 0, 0),
    "UpperArm_R": (-40, 0, 0),
}

BACK = [(0, 1.3, 4.75), (0, 0.0, 4.85), (0, -1.2, 5.0), (0, -2.2, 5.2)]
NECK = [(0, -2.2, 5.2), (0, -2.75, 5.55), (0, -3.05, 6.05)]
TAIL = [(0, 1.3, 4.75), (0, 3.6, 4.5), (0, 6.0, 3.9), (0, 8.2, 3.2), (0, 10.4, 2.5)]

# Crâne : (y, demi-largeur dessus, joues, bord dentaire, z dessus, z bord dentaire)
SKULL = [(-3.0, 0.55, 0.92, 0.74, 7.05, 5.55), (-3.45, 0.66, 1.06, 0.86, 7.3, 5.45),
         (-4.2, 0.56, 0.92, 0.78, 7.2, 5.42), (-5.0, 0.44, 0.74, 0.66, 6.95, 5.45),
         (-5.8, 0.36, 0.6, 0.55, 6.7, 5.48), (-6.5, 0.3, 0.48, 0.46, 6.45, 5.5),
         (-6.95, 0.16, 0.3, 0.32, 6.2, 5.55)]
# Mâchoire : même format, plus basse
JAW = [(-3.1, 0.42, 0.78, 0.68, 5.55, 4.95), (-3.9, 0.4, 0.76, 0.62, 5.48, 4.82),
       (-5.0, 0.34, 0.62, 0.52, 5.48, 4.9), (-6.0, 0.28, 0.48, 0.4, 5.48, 5.02),
       (-6.75, 0.16, 0.3, 0.26, 5.48, 5.12)]


def width_at(sections, y, idx=3):
    for s0, s1 in zip(sections, sections[1:]):
        if s1[0] <= y <= s0[0]:
            t = (s0[0] - y) / (s0[0] - s1[0])
            return s0[idx] + (s1[idx] - s0[idx]) * t
    return sections[-1][idx]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 1.3, 4.75), (0, -0.6, 4.9), "Root")
    rig.bone("Spine", (0, -0.6, 4.9), (0, -2.2, 5.2), "Hips")
    rig.bone("Neck", (0, -2.2, 5.2), (0, -3.05, 6.05), "Spine")
    rig.bone("Head", (0, -3.05, 6.05), (0, -6.9, 6.05), "Neck")
    rig.bone("Jaw", (0, -3.2, 5.45), (0, -6.7, 5.2), "Head")
    parent = "Hips"
    for i in range(4):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Thigh_{side}", (s * 0.8, 0.55, 4.25), (s * 0.95, -0.5, 2.55), "Hips")
        rig.bone(f"Shin_{side}", (s * 0.95, -0.5, 2.55), (s * 0.95, 0.55, 1.05), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 0.95, 0.55, 1.05), (s * 0.95, -1.0, 0.2), f"Shin_{side}")
        rig.bone(f"UpperArm_{side}", (s * 0.75, -2.35, 4.25), (s * 0.95, -2.75, 3.55), "Spine")
        rig.bone(f"Forearm_{side}", (s * 0.95, -2.75, 3.55), (s * 0.9, -3.3, 3.6),
                 f"UpperArm_{side}")
        rig.fx(f"Eye{side}", (s * 0.55, -3.8, 6.6), "Head")
    rig.fx("Heart", (0, -1.0, 3.85), "Spine")
    rig.fx("Mouth", (0, -4.6, 5.5), "Head")
    rig.fx("TailTip", (0, 11.0, 2.4), "Tail4")


def build_skull(rig):
    skull = a.loft_profile("Skull", SKULL)
    a.cut(skull, [
        a.hole_x((0, -3.8, 6.6), 0.3, 0.4),          # orbites
        a.hole_x((0, -4.9, 6.1), 0.58, 0.3),          # fenêtres antorbitales
        a.hole_x((0, -3.22, 6.0), 0.16, 0.4),         # fenêtres temporales
        a.hole_x((0, -6.72, 6.1), 0.15, 0.11),        # narines
    ])
    rig.add(skull, "Head", "bone")

    # Crête occipitale (arrière du crâne) et arcades
    crest = a.blade("Occipital", (0, -3.05, 6.85), (0, -2.8, 7.4), 1.5, 0.22, width_end=0.9,
                    normal=(0, 1, 0))
    rig.add(crest, "Head", "bone_shade")
    for s in (-1, 1):
        brow = a.claw(f"Brow{s}", (s * 0.5, -3.95, 7.15), (s * 0.4, -0.3, 1), 0.65, 0.2,
                      curl=-0.15)
        rig.add(brow, "Head", "horn")
        # Grandes cornes annelées vers l'arrière
        horn = a.ridged_horn(f"Horn{s}", [(s * 0.55, -3.1, 7.1), (s * 1.0, -2.7, 7.7),
                                          (s * 1.45, -2.0, 8.1), (s * 1.6, -1.2, 8.05),
                                          (s * 1.5, -0.6, 7.7)], 0.32, ridges=5)
        rig.add(horn, "Head", "horn")
        tip = a.claw(f"HornTip{s}", (s * 1.5, -0.62, 7.71), (s * -0.1, 0.5, -0.6), 0.25, 0.07)
        rig.add(tip, "Head", "horn_tip")
        # Pommettes : petites pointes noires
        cheek = a.claw(f"Cheek{s}", (s * 0.85, -3.4, 5.85), (s * 1, 0.4, -0.2), 0.45, 0.14,
                       curl=-0.1)
        rig.add(cheek, "Head", "horn")
        # Yeux : braises au fond des orbites
        eye = r.ico(f"Eye{s}", 0.17, subdivisions=2, location=(s * 0.5, -3.8, 6.6))
        rig.add(eye, "Head", "glow", glow=True)

    # Rune sur le front : trois losanges incrustés
    for k, (y, size) in enumerate(((-4.3, 0.15), (-4.75, 0.12), (-5.15, 0.09))):
        z = width_at(SKULL, y, 4) + 0.02
        rune = r.box(f"Rune{k}", (size, size, 0.05), location=(0, y, z), rotation=(0, 0, 0.785))
        rig.add(rune, "Head", "glow", glow=True)

    # Gorge incandescente (visible gueule ouverte)
    throat = r.ico("Throat", 0.32, subdivisions=2, location=(0, -3.6, 5.5), scale=(1.4, 1, 0.6))
    rig.add(throat, "Head", "glow", glow=True)

    # Crocs supérieurs, courbés vers l'arrière, canines plus longues
    y = -6.7
    k = 0
    while y < -3.9:
        for s in (-1, 1):
            x = s * width_at(SKULL, y) * 0.86
            length = 0.58 if k in (1, 2) else 0.42 - 0.02 * k
            tooth = a.claw(f"ToothU{s}{k}", (x, y, 5.6), (0, 0.18, -1), length, 0.1, curl=-0.08,
                           segments=4)
            rig.add(tooth, "Head", "tooth")
        y += 0.36
        k += 1


def build_jaw(rig):
    jaw = a.loft_profile("Jaw", JAW)
    a.cut(jaw, [a.hole_x((0, -3.75, 5.2), 0.38, 0.14)])
    rig.add(jaw, "Jaw", "bone")
    y = -6.5
    k = 0
    while y < -4.0:
        for s in (-1, 1):
            x = s * width_at(JAW, y) * 0.7
            tooth = a.claw(f"ToothL{s}{k}", (x, y, 5.45), (0, -0.15, 1), 0.34, 0.085,
                           curl=-0.06, segments=4)
            rig.add(tooth, "Jaw", "tooth")
        y += 0.38
        k += 1


def build_spine(rig):
    back = c.Chain(BACK)
    for i in range(9):
        p, t = back.at(i / 8)
        bone = "Hips" if p.y > -0.6 else "Spine"
        h = 1.25 + 0.5 * math.sin(i / 8 * math.pi)
        v = a.vertebra(f"Back{i}", p, -t, 0.42, spine=h, lean=0.3)
        rig.add(v, bone, "bone")
        if i < 8:
            q, tq = back.at((i + 0.5) / 8)
            rig.add(a.disc(f"BackDisc{i}", q, tq, 0.42), bone, "disc")
        # Pointes noires au sommet des épines du dos
        if i % 2 == 0:
            up = Vector((0, 0, 1))
            tip = p + up * (0.42 * 0.7 + 0.42 * h) + t * 0.42 * h * 0.3
            spk = a.claw(f"BackSpike{i}", tip - up * 0.1, (0, 0.35, 1), 0.45, 0.11, curl=-0.1)
            rig.add(spk, bone, "horn")

    neck = c.Chain(NECK)
    for i in range(5):
        p, t = neck.at(i / 4)
        v = a.vertebra(f"Neck{i}", p, -t, 0.38, spine=0.7, lean=0.2)
        rig.add(v, "Neck", "bone")
        if i < 4:
            q, tq = neck.at((i + 0.5) / 4)
            rig.add(a.disc(f"NeckDisc{i}", q, tq, 0.38), "Neck", "disc")

    tail = c.Chain(TAIL)
    n = 15
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(4, int(t * 4 * 0.999) + 1)}"
        size = 0.4 - 0.27 * t
        v = a.vertebra(f"Tail{i}", p, tan, size, spine=1.4 - 0.6 * t, lean=-0.35,
                       transverse=i < 12)
        rig.add(v, bone, "bone")
        if i < n - 1:
            q, tq = tail.at((i + 0.5) / (n - 1))
            rig.add(a.disc(f"TailDisc{i}", q, tq, size), bone, "disc")
        if i < 11:   # chevrons sous la queue
            down = p - Vector((0, -0.1, size * 0.4))
            chev = a.blade(f"Chevron{i}", down, down + Vector((0, 0.35, -size * 2.2)),
                           size * 0.5, size * 0.18, width_end=size * 0.25, normal=(1, 0, 0),
                           bevel=0)
            rig.add(chev, bone, "bone_shade")
    # Lame de cristal au bout de la queue
    tip, tan = tail.at(1.0)
    blade_crystal = a.claw("TailCrystal", tip, tan, 1.1, 0.28, curl=0.0, segments=6)
    rig.add(blade_crystal, "Tail4", "glow", glow=True)


def build_ribcage(rig):
    back = c.Chain(BACK)
    for i in range(8):
        t = 0.32 + 0.66 * i / 7
        p, _ = back.at(t)
        bone = "Hips" if p.y > -0.6 else "Spine"
        bulge = math.sin((i + 1) / 9 * math.pi)
        for s in (-1, 1):
            rb = a.rib(f"Rib{i}{s}", p + Vector((0, 0, -0.1)), 0.75 + 0.6 * bulge,
                       1.2 + 0.85 * bulge, s, sweep=-0.4, radius=0.11)
            rig.add(rb, bone, "bone")
    # Côtes ventrales (gastralia) en V sous le ventre
    for i in range(6):
        y = -1.9 + i * 0.42
        z = 3.2 + 0.08 * i
        for s in (-1, 1):
            g = r.tube(f"Gastralia{i}{s}", [(0, y, z - 0.05), (s * 0.55, y + 0.1, z + 0.05),
                                            (s * 0.95, y + 0.2, z + 0.35)],
                       [0.07, 0.07, 0.04], segments=5)
            rig.add(g, "Spine" if y < -0.6 else "Hips", "bone_shade")
    # Sternum
    sternum = a.blade("Sternum", (0, -2.3, 3.75), (0, -1.6, 3.25), 0.7, 0.12, width_end=0.45,
                      normal=(0, 0, 1))
    rig.add(sternum, "Spine", "bone_shade")
    # Cœur de cristal infernal flottant dans la cage + éclats
    heart = a.crystal("Heart", (0, -1.0, 3.85), 0.4, 1.1)
    rig.add(heart, "Spine", "glow", glow=True)
    for k, (dx, dy, dz) in enumerate(((0.55, 0.2, 0.2), (-0.5, -0.25, 0.0), (0.1, 0.4, -0.5))):
        shard = a.crystal(f"Shard{k}", (dx, -1.0 + dy, 3.85 + dz), 0.12, 0.35, sides=4)
        rig.add(shard, "Spine", "glow", glow=True)


def build_shoulders_and_arms(rig, s, side):
    scap = a.blade(f"Scapula{s}", (s * 0.75, -2.3, 4.35), (s * 0.85, -1.0, 5.35), 0.55, 0.12,
                   width_end=0.38, normal=(s, 0, 0.3))
    rig.add(scap, "Spine", "bone")
    shoulder, elbow, wrist = Vector((s * 0.75, -2.35, 4.25)), Vector((s * 0.95, -2.75, 3.55)), \
        Vector((s * 0.9, -3.3, 3.6))
    rig.add(a.long_bone(f"Humerus{s}", shoulder, elbow, 0.1), f"UpperArm_{side}", "bone")
    rig.add(a.long_bone(f"Ulna{s}", elbow, wrist, 0.085), f"Forearm_{side}", "bone")
    for k, dx in enumerate((-0.09, 0.09)):
        knuckle = wrist + Vector((dx, -0.28, -0.05))
        rig.add(a.long_bone(f"Finger{s}{k}", wrist, knuckle, 0.06, knob=1.4, condyles=False),
                f"Forearm_{side}", "bone")
        rig.add(a.claw(f"HandClaw{s}{k}", knuckle, (dx, -1, -0.4), 0.32, 0.075),
                f"Forearm_{side}", "horn")


def build_pelvis(rig):
    for s in (-1, 1):
        # Ilium : grande lame verticale le long du dos
        ilium = a.blade(f"Ilium{s}", (s * 0.45, -0.75, 4.85), (s * 0.45, 2.0, 5.0), 0.55, 0.16,
                        width_end=0.4, mid=1.35, normal=(1, 0, 0))
        rig.add(ilium, "Hips", "bone")
        rig.add(r.ico(f"Acetabulum{s}", 0.3, subdivisions=2, location=(s * 0.62, 0.55, 4.25)),
                "Hips", "bone_shade")
        rig.add(a.long_bone(f"Pubis{s}", (s * 0.4, 0.1, 4.2), (s * 0.15, -0.8, 2.75), 0.13),
                "Hips", "bone")
        rig.add(a.long_bone(f"Ischium{s}", (s * 0.4, 0.95, 4.2), (s * 0.15, 1.8, 3.15), 0.11),
                "Hips", "bone")
    boot = r.ico("PubicBoot", 0.35, subdivisions=2, location=(0, -0.95, 2.65),
                 scale=(0.75, 1.7, 0.45))
    r.smooth(boot, 60)
    rig.add(boot, "Hips", "bone_shade")


def build_leg(rig, s, side):
    hip, knee, ankle = Vector((s * 0.8, 0.55, 4.25)), Vector((s * 0.95, -0.5, 2.55)), \
        Vector((s * 0.95, 0.55, 1.05))
    thigh, shin, foot = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
    rig.add(a.long_bone(f"Femur{s}", hip, knee, 0.22), thigh, "bone")
    # Grand trochanter et rune incandescente sur le fémur
    rig.add(a.claw(f"Trochanter{s}", hip + Vector((s * 0.2, -0.15, -0.25)), (s * 0.4, -0.4, -1),
                   0.45, 0.13, curl=0), thigh, "bone_shade")
    mid = hip.lerp(knee, 0.5)
    rig.add(r.box(f"FemurRune{s}", (0.05, 0.18, 0.18), location=mid + Vector((s * 0.21, 0, 0)),
                  rotation=(0.785, 0, 0)), thigh, "glow", glow=True)

    rig.add(r.ico(f"Patella{s}", 0.2, subdivisions=2, location=knee + Vector((0, -0.28, 0.05))),
            shin, "bone_shade")
    rig.add(a.long_bone(f"Tibia{s}", knee, ankle, 0.18), shin, "bone")
    rig.add(a.long_bone(f"Fibula{s}", knee + Vector((s * 0.24, 0.1, -0.15)),
                        ankle + Vector((s * 0.2, 0, 0.12)), 0.07, knob=1.3), shin, "bone_shade")
    rig.add(r.ico(f"Ankle{s}", 0.24, subdivisions=2, location=ankle), foot, "bone_shade")

    # 3 orteils : métatarse + 2 phalanges + griffe noire
    for k, dx in enumerate((-0.32, 0.0, 0.32)):
        base = Vector((s * 0.95 + dx, -0.3, 0.32))
        rig.add(a.long_bone(f"Meta{s}{k}", ankle, base, 0.09, knob=1.5, condyles=False), foot,
                "bone")
        j1 = base + Vector((dx * 0.35, -0.42 + abs(dx) * 0.25, -0.05))
        j2 = j1 + Vector((dx * 0.2, -0.35 + abs(dx) * 0.2, -0.05))
        rig.add(a.long_bone(f"Phal{s}{k}a", base, j1, 0.085, knob=1.4, condyles=False), foot, "bone")
        rig.add(a.long_bone(f"Phal{s}{k}b", j1, j2, 0.075, knob=1.4, condyles=False), foot, "bone")
        rig.add(a.claw(f"Claw{s}{k}", j2, (dx * 0.4, -1, 0.1), 0.55, 0.13, curl=0.4),
                foot, "horn")
    # Ergot arrière
    rig.add(a.claw(f"Spur{s}", ankle + Vector((0, 0.25, -0.4)), (0, 1, -0.6), 0.4, 0.09,
                   curl=0.2), foot, "horn")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_skull(rig)
    build_jaw(rig)
    build_spine(rig)
    build_ribcage(rig)
    build_pelvis(rig)
    for s, side in ((1, "L"), (-1, "R")):
        build_shoulders_and_arms(rig, s, side)
        build_leg(rig, s, side)
    return rig
