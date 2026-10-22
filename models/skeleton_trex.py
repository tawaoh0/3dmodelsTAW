"""T-Rex démoniaque (≈ 17 studs de long, 10 de haut) — créature animable.

Style « boss Roblox » : corps massif et musclé d'un seul tenant (skinning doux),
peau noire bleutée, plaques d'armure et cornes grises, griffes et crocs clairs,
gueule rouge, yeux et gorge incandescents.
Os du rig : Root, Hips, Spine, Neck, Head, Jaw, Tail1-4, Thigh/Shin/Foot_L/R,
UpperArm/Forearm_L/R, + FX_* pour les flammes (yeux, gueule).
"""
from mathutils import Vector

from lib import creature as c
from lib import sculpt

COLORS = {
    "skin": "#2a2e44",
    "skin_dark": "#181a26",
    "plate": "#7a7e8a",
    "plate_dark": "#545862",
    "claw": "#e6d2c4",
    "mouth": "#6a0b16",
    "tongue": "#b0243a",
    "glow": "#ff2020",
    "glow_hot": "#ffb090",
}

TEST_POSE = {
    "Jaw": (32, 0, 0),
    "Neck": (-10, 0, 0),
    "Head": (-8, 0, 0),
    "Tail2": (0, 0, 15),
    "Tail3": (0, 0, 15),
    "Thigh_L": (-25, 0, 0),
    "Shin_L": (20, 0, 0),
    "UpperArm_R": (-40, 0, 0),
}

TAIL = [(0, 1.8, 5.0), (0, 4.0, 4.7), (0, 6.2, 4.1), (0, 8.3, 3.3), (0, 10.4, 2.5)]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 1.2, 4.8), (0, -0.6, 5.2), "Root")
    rig.bone("Spine", (0, -0.6, 5.2), (0, -2.0, 5.9), "Hips")
    rig.bone("Neck", (0, -2.0, 5.9), (0, -3.0, 6.8), "Spine")
    rig.bone("Head", (0, -3.0, 6.8), (0, -6.3, 6.8), "Neck")
    rig.bone("Jaw", (0, -3.4, 6.1), (0, -6.0, 5.6), "Head")
    parent = "Hips"
    for i in range(4):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Thigh_{side}", (s * 1.4, 0.8, 4.6), (s * 1.6, -0.2, 2.6), "Hips")
        rig.bone(f"Shin_{side}", (s * 1.6, -0.2, 2.6), (s * 1.6, 0.9, 1.0), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 1.6, 0.9, 1.0), (s * 1.6, -0.7, 0.3), f"Shin_{side}")
        rig.bone(f"UpperArm_{side}", (s * 1.5, -2.1, 5.1), (s * 1.9, -2.7, 4.1), "Spine")
        rig.bone(f"Forearm_{side}", (s * 1.9, -2.7, 4.1), (s * 1.75, -3.5, 3.8),
                 f"UpperArm_{side}")
        rig.fx(f"Eye{side}", (s * 1.0, -4.95, 7.3), "Head")
    rig.fx("Mouth", (0, -4.8, 6.25), "Head")


def build_head(rig, sc):
    # Crâne massif + museau carré, fondus dans le cou
    sc.ellipsoid("Head", "skin", (0, -3.9, 7.0), (1.5, 1.6, 1.2))
    sc.ellipsoid("Head", "skin", (0, -5.3, 6.75), (1.15, 1.35, 0.78))
    sc.ellipsoid("Head", "skin", (0, -6.3, 6.65), (0.8, 0.55, 0.55))
    for s in (-1, 1):
        sc.carve("Head", "skin", (s * 1.0, -4.95, 7.3), 0.3)            # orbite
        sc.carve("Head", "skin", (s * 0.35, -6.75, 6.85), 0.12)          # narine
        # Joues musclées
        sc.ellipsoid("Head", "skin", (s * 1.05, -3.7, 6.5), (0.6, 0.9, 0.7))

    # Gueule rouge (visible quand la mâchoire s'ouvre) + gorge incandescente
    sc.ellipsoid("Head", "mouth", (0, -4.8, 6.2), (1.0, 1.6, 0.42), group="mouth")
    sc.ball("Head", "glow", (0, -3.9, 6.3), 0.4)

    # Mâchoire : groupe séparé pour pouvoir s'ouvrir
    sc.ellipsoid("Jaw", "skin", (0, -4.7, 5.75), (1.2, 1.8, 0.55), group="jaw")
    sc.ellipsoid("Jaw", "skin", (0, -3.6, 5.85), (1.0, 0.7, 0.5), group="jaw")
    sc.ellipsoid("Jaw", "tongue", (0, -4.9, 6.1), (0.6, 1.2, 0.2), group="tongue")

    for s in (-1, 1):
        # Arcade sourcilière : plaque grise inclinée → regard furieux
        sc.ellipsoid("Head", "plate", (s * 0.8, -4.85, 7.72), (0.75, 0.45, 0.17),
                     rotation=(0.25, s * 0.45, 0), group=f"brow{s}")
        # Yeux rouges en amande
        sc.ellipsoid("Head", "glow", (s * 1.0, -4.95, 7.28), (0.16, 0.3, 0.14),
                     rotation=(0, s * 0.4, s * 0.3))
        # Grandes cornes grises recourbées
        horn = [(s * 0.95, -3.6, 7.9), (s * 1.5, -3.2, 8.45), (s * 1.85, -2.55, 8.95),
                (s * 1.95, -1.9, 9.45)]
        sc.limb("Head", "plate", horn, [0.5, 0.42, 0.34, 0.26], group=f"horn{s}")
        for k in (1, 2):   # anneaux plus sombres sur la corne
            sc.ball("Head", "plate_dark", horn[k], [0.42, 0.34][k - 1] * 1.08,
                    group=f"hornring{s}{k}")
        tip = c.spike(f"HornTip{s}", horn[-1], (s * 1.9, -1.4, 10.3), 0.26, segments=10,
                      bend=(0, -0.1, 0))
        rig.add(tip, "Head", "plate")
        # Corne de joue
        cheek = c.spike(f"Cheek{s}", (s * 1.4, -3.5, 6.6), (s * 2.15, -3.0, 6.4), 0.22,
                        segments=8, bend=(0, 0.1, 0.1))
        rig.add(cheek, "Head", "plate")
        # Plaques sur le crâne
        sc.ellipsoid("Head", "plate_dark", (s * 0.45, -3.6, 8.05), (0.4, 0.5, 0.28),
                     group=f"skull{s}")

        # Crocs : haut (vers le bas) et bas (vers le haut), canines plus longues
        for k in range(5):
            y = -6.3 + k * 0.5
            x = s * (0.6 + k * 0.12)
            length = 0.6 if k == 1 else 0.4
            tooth = c.spike(f"ToothU{s}{k}", (x, y, 6.25), (x, y - 0.05, 6.25 - length), 0.12,
                            segments=6)
            rig.add(tooth, "Head", "claw")
            low = c.spike(f"ToothL{s}{k}", (x * 0.95, y + 0.25, 6.05),
                          (x * 0.95, y + 0.2, 6.05 + length * 0.8), 0.11, segments=6)
            rig.add(low, "Jaw", "claw")


def build_body(rig, sc):
    # Torse en poire : poitrail énorme, dos voûté, bassin
    sc.ellipsoid("Spine", "skin", (0, -1.3, 5.6), (1.9, 1.7, 1.8))
    sc.ellipsoid("Spine", "skin", (0, -1.0, 6.4), (1.5, 1.3, 1.1))
    sc.ellipsoid("Hips", "skin", (0, 0.9, 5.1), (1.6, 1.6, 1.45))
    sc.limb(["Neck", "Neck"], "skin", [(0, -2.0, 6.2), (0, -2.7, 6.7), (0, -3.2, 7.0)],
            [1.25, 1.15, 1.05])

    # Plastron : plaques grises segmentées sur le ventre et la gorge
    plates = [("Neck", (0, -2.85, 6.0), (0.75, 0.45, 0.38), -1.0),
              ("Spine", (0, -2.45, 5.25), (1.0, 0.5, 0.42), -0.75),
              ("Spine", (0, -1.85, 4.6), (1.1, 0.5, 0.42), -0.45),
              ("Spine", (0, -1.1, 4.1), (1.1, 0.55, 0.4), -0.2),
              ("Hips", (0, -0.25, 3.85), (0.95, 0.55, 0.38), 0.0),
              ("Hips", (0, 0.6, 3.85), (0.8, 0.5, 0.35), 0.15)]
    for k, (bone, p, radii, tilt) in enumerate(plates):
        sc.ellipsoid(bone, "plate" if k % 2 == 0 else "plate_dark", p, radii,
                     rotation=(tilt, 0, 0), group=f"belly{k}")

    # Épaulières en plaques avec pointe
    for s in (-1, 1):
        sc.ellipsoid("Spine", "plate_dark", (s * 1.55, -1.9, 6.45), (0.8, 0.95, 0.6),
                     rotation=(0, s * 0.5, 0), group=f"shoulder{s}")
        sp = c.spike(f"ShoulderSpike{s}", (s * 1.8, -1.9, 6.75), (s * 2.6, -1.7, 7.55), 0.32,
                     segments=8)
        rig.add(sp, "Spine", "plate")

    # Crête de pointes sur le dos
    crest = [("Neck", (0, -2.6, 7.75), 0.55), ("Spine", (0, -1.7, 7.45), 0.8),
             ("Spine", (0, -0.6, 7.25), 0.9), ("Hips", (0, 0.5, 6.45), 0.75),
             ("Hips", (0, 1.5, 6.25), 0.6)]
    for k, (bone, p, h) in enumerate(crest):
        p = Vector(p)
        sp = c.spike(f"Crest{k}", p - Vector((0, 0, 0.35)), p + Vector((0, 0.35, h)), h * 0.42,
                     segments=7)
        rig.add(sp, bone, "plate")


def build_tail(rig, sc):
    radii = [1.3, 1.0, 0.7, 0.45, 0.22]
    sc.limb([f"Tail{i + 1}" for i in range(4)], "skin", TAIL, radii)
    for i in range(4):
        p = Vector(TAIL[i]).lerp(Vector(TAIL[i + 1]), 0.5)
        rad = (radii[i] + radii[i + 1]) / 2
        h = 0.6 - i * 0.12
        sp = c.spike(f"TailSpike{i}", p + Vector((0, 0, rad * 0.7)),
                     p + Vector((0, 0.35, rad * 0.7 + h)), h * 0.42, segments=6)
        rig.add(sp, f"Tail{i + 1}", "plate")
    # Pointe de flèche démoniaque au bout
    tip = Vector(TAIL[-1])
    blade = c.spike("TailBlade", tip - Vector((0, 0.3, 0)), tip + Vector((0, 1.4, -0.4)), 0.5,
                    segments=4)
    rig.add(blade, "Tail4", "plate")


def build_leg(rig, sc, s, side):
    hip, knee, ankle = Vector((s * 1.4, 0.8, 4.6)), Vector((s * 1.6, -0.2, 2.6)), \
        Vector((s * 1.6, 0.9, 1.0))
    thigh, shin, foot = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
    sc.ellipsoid(thigh, "skin", hip.lerp(knee, 0.45), (1.05, 1.3, 1.5), rotation=(0.45, 0, 0))
    sc.limb(shin, "skin", [knee, ankle], [0.78, 0.52])
    sc.ellipsoid(foot, "skin", (s * 1.6, 0.3, 0.55), (0.78, 1.15, 0.55))
    # Plaque de genou
    sc.ellipsoid(shin, "plate_dark", knee + Vector((0, -0.55, 0.1)), (0.55, 0.3, 0.5),
                 group=f"knee{s}")
    for k, dx in enumerate((-0.45, 0.0, 0.45)):
        base = Vector((s * 1.6 + dx, -0.55 + abs(dx) * 0.3, 0.45))
        claw = c.spike(f"Claw{s}{k}", base, base + Vector((dx * 0.3, -0.8, -0.35)), 0.26,
                       segments=8, bend=(0, -0.05, 0.14))
        rig.add(claw, foot, "claw")
    spur = c.spike(f"Spur{s}", (s * 1.6, 1.1, 0.6), (s * 1.6, 1.7, 0.25), 0.17, segments=6)
    rig.add(spur, foot, "claw")


def build_arm(rig, sc, s, side):
    shoulder, elbow, wrist = Vector((s * 1.5, -2.1, 5.1)), Vector((s * 1.9, -2.7, 4.1)), \
        Vector((s * 1.75, -3.5, 3.8))
    sc.limb(f"UpperArm_{side}", "skin", [shoulder, elbow], [0.68, 0.5])
    sc.limb(f"Forearm_{side}", "skin", [elbow, wrist], [0.5, 0.45])
    for k, dx in enumerate((-0.2, 0.2)):
        base = wrist + Vector((dx, -0.3, -0.1))
        claw = c.spike(f"HandClaw{s}{k}", base, base + Vector((dx * 0.4, -0.5, -0.55)), 0.19,
                       segments=7, bend=(0, -0.1, 0.05))
        rig.add(claw, f"Forearm_{side}", "claw")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    sc = sculpt.Sculpt(rig, resolution=0.1)
    build_head(rig, sc)
    build_body(rig, sc)
    build_tail(rig, sc)
    for s, side in ((1, "L"), (-1, "R")):
        build_leg(rig, sc, s, side)
        build_arm(rig, sc, s, side)
    sc.build({"body:skin": 8000, "jaw:skin": 1000, "*": 260})
    return rig
