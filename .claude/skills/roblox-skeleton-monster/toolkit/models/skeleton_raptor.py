"""Raptor squelette rongé d'acide (≈ 11 studs de long, 5 de haut) — créature animable.

Identité propre (différente du T-Rex et du dragon) :
- os vert-gris maladif, piqués de cratères de corrosion qui brillent ;
- pas de cornes recourbées : éventails de piquants-plumes ossifiés (nuque, bras,
  queue) et deux fines crêtes jumelles sur le museau ;
- posture ramassée prête à bondir : tête basse en avant, pattes très fléchies,
  queue relevée, bras écartés griffes en avant ;
- thème acide : gouttes qui pendent des crocs et des griffes, poche d'acide
  bouillonnante dans la cage, effets Roblox « acid » (bulles, coulures).

2 pièces Roblox : corps, tête (+ cou), plus le mesh lumineux.
Os du rig : Root, Hips, Spine, Neck1-2, Head, Jaw, Tail1-4, Thigh/Shin/Foot/Sickle_L/R,
UpperArm/Forearm/Hand_L/R, + FX_* (yeux, gueule, poche d'acide, griffes faucilles).
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#c4c9a0",
    "bone_shade": "#8b9468",
    "tooth": "#e9ecd0",
    "horn": "#1a2418",
    "horn_tip": "#4c8a1c",
    "quill": "#203a2a",
    "disc": "#1e3312",
    "glow": "#8dff1f",
    "glow_hot": "#f0ffb8",
}

# Effets Roblox : bulles qui montent + gouttes qui tombent (voir CreatureEffects.server.lua)
EFFECT_THEME = "acid"

TEST_POSE = {
    "Jaw": (35, 0, 0),
    "Neck1": (-15, 0, 0),
    "Head": (10, 0, 0),
    "Sickle_L": (-40, 0, 0),
    "Sickle_R": (-40, 0, 0),
    "UpperArm_L": (-35, 0, 0),
    "UpperArm_R": (-35, 0, 0),
    "Thigh_R": (-20, 0, 0),
    "Tail2": (-10, 0, 0),
    "Tail3": (0, 0, 15),
}

# Dos incliné : hanches hautes, épaules basses (posture de chasse)
BACK = [(0, 0.8, 3.0), (0, -0.2, 2.88), (0, -1.1, 2.7)]
NECK = [(0, -1.1, 2.7), (0, -1.7, 3.1), (0, -2.1, 3.55), (0, -2.65, 3.8)]
# Queue relevée pour l'équilibre
TAIL = [(0, 0.8, 3.0), (0, 2.4, 3.35), (0, 4.0, 3.65), (0, 5.6, 3.8), (0, 7.0, 3.75)]

# Crâne bas et étroit : (y, demi-largeur dessus, joues, bord dentaire, z dessus, z bas)
SKULL = [(-2.65, 0.36, 0.52, 0.42, 4.3, 3.6), (-2.95, 0.4, 0.56, 0.44, 4.42, 3.55),
         (-3.25, 0.36, 0.5, 0.4, 4.42, 3.55), (-3.6, 0.26, 0.38, 0.33, 4.22, 3.57),
         (-4.0, 0.22, 0.31, 0.28, 4.12, 3.6), (-4.4, 0.2, 0.27, 0.25, 4.08, 3.62),
         (-4.75, 0.15, 0.21, 0.2, 3.98, 3.64), (-5.0, 0.1, 0.14, 0.13, 3.82, 3.66)]
JAW = [(-2.7, 0.3, 0.46, 0.38, 3.57, 3.25), (-3.4, 0.26, 0.38, 0.31, 3.55, 3.2),
       (-4.3, 0.19, 0.27, 0.23, 3.55, 3.3), (-4.95, 0.1, 0.14, 0.12, 3.55, 3.42)]


def width_at(sections, y, idx=3):
    for s0, s1 in zip(sections, sections[1:]):
        if s1[0] <= y <= s0[0]:
            t = (s0[0] - y) / (s0[0] - s1[0])
            return s0[idx] + (s1[idx] - s0[idx]) * t
    return sections[-1][idx]


def drip(rig, name, top, bone, size=0.05, **kw):
    """Goutte d'acide qui pend : une goutte étirée + une petite qui se détache."""
    top = Vector(top)
    rig.add(r.ico(f"{name}a", size, subdivisions=1, location=top - Vector((0, 0, size * 1.6)),
                  scale=(1, 1, 2.0)), bone, "glow", glow=True)
    rig.add(r.ico(f"{name}b", size * 0.6, subdivisions=1,
                  location=top - Vector((0, 0, size * 5.0))), bone, "glow", glow=True)


def pit(rig, name, location, bone, size=0.06):
    """Cratère de corrosion lumineux incrusté dans l'os."""
    rig.add(r.ico(name, size, subdivisions=1, location=location, scale=(1, 1, 0.5)), bone,
            "glow", glow=True)


def quill_fan(rig, name, base, directions, lengths, bone, radius=0.035, **kw):
    """Éventail de piquants-plumes ossifiés, pointes teintées."""
    base = Vector(base)
    for k, (d, length) in enumerate(zip(directions, lengths)):
        d = Vector(d).normalized()
        rig.add(a.claw(f"{name}{k}", base, d, length, radius, curl=-0.08, segments=4), bone,
                "quill", **kw)
        rig.add(a.claw(f"{name}{k}tip", base + d * length * 0.82, d, length * 0.2, radius * 0.5,
                       curl=0, segments=4), bone, "horn_tip", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 0.8, 3.0), (0, -0.3, 2.86), "Root")
    rig.bone("Spine", (0, -0.3, 2.86), (0, -1.1, 2.7), "Hips")
    rig.bone("Neck1", (0, -1.1, 2.7), (0, -2.1, 3.55), "Spine")
    rig.bone("Neck2", (0, -2.1, 3.55), (0, -2.65, 3.8), "Neck1")
    rig.bone("Head", (0, -2.65, 3.8), (0, -5.0, 3.75), "Neck2")
    rig.bone("Jaw", (0, -2.75, 3.5), (0, -4.95, 3.45), "Head")
    parent = "Hips"
    for i in range(4):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Thigh_{side}", (s * 0.5, 0.6, 2.65), (s * 0.68, -0.55, 1.55), "Hips")
        rig.bone(f"Shin_{side}", (s * 0.68, -0.55, 1.55), (s * 0.68, 0.55, 0.72), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 0.68, 0.55, 0.72), (s * 0.68, -0.55, 0.12), f"Shin_{side}")
        rig.bone(f"Sickle_{side}", (s * 0.55, -0.1, 0.32), (s * 0.55, -0.6, 0.55), f"Foot_{side}")
        rig.bone(f"UpperArm_{side}", (s * 0.42, -1.2, 2.45), (s * 0.78, -1.0, 1.95), "Spine")
        rig.bone(f"Forearm_{side}", (s * 0.78, -1.0, 1.95), (s * 0.85, -1.85, 2.05),
                 f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", (s * 0.85, -1.85, 2.05), (s * 0.9, -2.35, 1.85), f"Forearm_{side}")
        rig.fx(f"Eye{side}", (s * 0.3, -3.2, 4.15), "Head")
        rig.fx(f"Sickle{side}", (s * 0.55, -0.55, 0.95), f"Sickle_{side}")
    rig.fx("Mouth", (0, -3.4, 3.5), "Head")
    rig.fx("Heart", (0, -0.4, 2.2), "Spine")


# ---------------------------------------------------------------- tête

def build_head(rig):
    head = dict(part="Head")
    skull = a.loft_profile("Skull", SKULL, tip=None)
    cutters = []
    for center, ry, rz in (((0, -3.2, 4.15), 0.22, 0.22),     # grandes orbites rondes
                           ((0, -3.9, 3.88), 0.34, 0.13),     # fenêtres antorbitales
                           ((0, -2.72, 4.05), 0.09, 0.2),     # fenêtres temporales
                           ((0, -4.8, 3.85), 0.08, 0.06)):    # narines
        cutter = a.hole_x(center, ry, rz)
        a.rotate_obj(cutter, "X", -0.15, center)
        cutters.append(cutter)
    a.cut(skull, cutters)
    rig.add(skull, "Head", "bone", **head)

    # Crêtes jumelles sur le museau : fines lames en demi-lune, bord dentelé, écartées en V
    for s in (-1, 1):
        y0, y1 = -4.7, -3.3
        outline = []
        n = 9
        for k in range(n + 1):           # bord supérieur en arc, une dent sur deux
            t = k / n
            y = y0 + (y1 - y0) * t
            base_z = width_at(SKULL, y, 4) - 0.04
            h = 0.5 * math.sin(math.pi * (0.15 + 0.85 * t)) + (0.07 if k % 2 else 0)
            outline.append(((s * (0.1 + 0.12 * h), y, base_z + h), {"Head": 1}))
        for y in (y1, (y0 + y1) / 2, y0):  # retour le long du crâne
            outline.append(((s * 0.1, y, width_at(SKULL, y, 4) - 0.05), {"Head": 1}))
        crest = a.membrane(f"Crest{s}", outline, thickness=0.05)
        rig.pal.paint(crest, "bone_shade")
        crest["part"] = "Head"
        for k, y in enumerate((-4.2, -3.75)):
            pit(rig, f"CrestPit{s}{k}", (s * 0.15, y, width_at(SKULL, y, 4) + 0.25), "Head",
                size=0.045)

    for s in (-1, 1):
        # Arcade basse au-dessus de l'œil (pas de corne : c'est la signature du dragon)
        rig.add(a.blade(f"Brow{s}", (s * 0.15, -3.45, 4.4), (s * 0.42, -2.9, 4.42), 0.18, 0.1,
                        width_end=0.14, mid=0.22, normal=(0, 0.2, 1), bevel=0.01), "Head",
                "bone_shade", **head)
        # Pommette fine
        cheek = [(s * 0.3, -3.6, 3.72), (s * 0.48, -3.15, 3.72), (s * 0.5, -2.8, 3.85)]
        arch = r.tube(f"Zygomatic{s}", cheek, [0.05, 0.08, 0.07], segments=6)
        r.smooth(arch, 40)
        rig.add(arch, "Head", "bone_shade", **head)
        # Œil acide
        rig.add(r.ico(f"Eye{s}", 0.12, subdivisions=2, location=(s * 0.3, -3.2, 4.15)),
                "Head", "glow", glow=True)
        # Cratères de corrosion sur les joues
        pit(rig, f"CheekPit{s}", (s * 0.4, -3.55, 3.8), "Head")
        pit(rig, f"SnoutPit{s}", (s * 0.24, -4.35, 3.8), "Head", size=0.045)
        # Mâchoire : apophyse + petite épine
        rig.add(a.blade(f"Coronoid{s}", (s * 0.35, -3.0, 3.35), (s * 0.37, -2.85, 3.65), 0.2,
                        0.06, width_end=0.1, normal=(1, 0, 0), bevel=0), "Jaw", "bone_shade",
                **head)

    # Éventail de piquants-plumes à l'arrière du crâne (la « coiffe » du raptor)
    dirs, lengths = [], []
    for k in range(7):
        ang = -0.95 + k * (1.9 / 6)          # de gauche à droite
        dirs.append((math.sin(ang) * 0.9, 1.0, 0.55 + 0.35 * math.cos(ang)))
        lengths.append(1.25 - abs(k - 3) * 0.13)
    quill_fan(rig, "HeadQuill", (0, -2.7, 4.3), dirs, lengths, "Head", radius=0.04, **head)

    # Poche d'acide dans la gorge (visible gueule ouverte)
    rig.add(r.ico("AcidGland", 0.15, subdivisions=2, location=(0, -3.0, 3.55),
                  scale=(1.0, 1.3, 0.55)), "Head", "glow", glow=True)

    # Dents fines en aiguilles, crochets à l'avant qui gouttent d'acide
    for jaw, sections, z, direction, bone in ((False, SKULL, 3.62, (0, 0.3, -1), "Head"),
                                              (True, JAW, 3.52, (0, -0.25, 1), "Jaw")):
        y, k = -4.85, 0
        while y < -3.0:
            for s in (-1, 1):
                x = s * width_at(sections, y) * (0.72 if jaw else 0.86)
                fang = k == 1
                length = (0.36 if fang else 0.17) * (0.8 if jaw else 1)
                rig.add(a.claw(f"Tooth{bone}{s}{k}", (x, y, z), direction, length,
                               0.05 if fang else 0.035, curl=-0.1, segments=4),
                        bone, "tooth", **head)
                if fang and not jaw:
                    drip(rig, f"FangDrip{s}", (x, y + 0.1, z - 0.36), "Head", size=0.04)
            y += 0.2
            k += 1

    jaw = a.loft_profile("Jaw", JAW, tip=None)
    a.cut(jaw, [a.hole_x((0, -3.3, 3.38), 0.24, 0.07)])
    rig.add(jaw, "Jaw", "bone", **head)
    drip(rig, "ChinDrip", (0, -4.6, 3.32), "Jaw", size=0.045)


# ---------------------------------------------------------------- colonne

def build_spine(rig):
    back = c.Chain(BACK)
    for i in range(6):
        p, t = back.at(i / 5)
        bone = "Hips" if p.y > -0.3 else "Spine"
        rig.add(a.vertebra(f"Back{i}", p, -t, 0.27, spine=0.75, lean=0.35), bone, "bone")
        if i < 5:
            q, tq = back.at((i + 0.5) / 5)
            rig.add(a.disc(f"BackDisc{i}", q, tq, 0.27), bone, "disc")
        # Piquants-plumes courts le long du dos
        quill_fan(rig, f"BackQuill{i}", p + Vector((0, 0, 0.4)),
                  [(-0.35, 1, 0.8), (0.35, 1, 0.8)], [0.5, 0.5], bone, radius=0.03)

    neck = c.Chain(NECK)
    for i in range(7):
        p, t = neck.at(i / 6)
        bone = "Neck1" if i < 5 else "Neck2"
        size = 0.3 - 0.04 * i / 6
        rig.add(a.vertebra(f"Neck{i}", p, -t, size, spine=0.4, lean=0.2), bone, "bone",
                part="Head")
        if i < 6:
            q, tq = neck.at((i + 0.5) / 6)
            rig.add(a.disc(f"NeckDisc{i}", q, tq, size), bone, "disc", part="Head")

    tail = c.Chain(TAIL)
    n = 15
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(4, int(t * 4 * 0.999) + 1)}"
        size = 0.27 - 0.16 * t
        rig.add(a.vertebra(f"Tail{i}", p, tan, size, spine=0.7 - 0.3 * t, lean=-0.3,
                           transverse=i < 9), bone, "bone")
        if i < n - 1:
            q, tq = tail.at((i + 0.5) / (n - 1))
            rig.add(a.disc(f"TailDisc{i}", q, tq, size), bone, "disc")
    # Tendons ossifiés qui raidissent la queue, un tronçon par os
    for i in range(4):
        a0, b0 = Vector(TAIL[i]), Vector(TAIL[i + 1])
        rad = 0.27 - 0.16 * (i + 0.5) / 4
        for s in (-1, 1):
            off = Vector((s * rad * 0.9, 0, rad * 0.5))
            rig.add(r.tube(f"Tendon{i}{s}", [tuple(a0 + off), tuple(b0.lerp(a0, 0.05) + off)],
                           [0.03, 0.025], segments=4), f"Tail{i + 1}", "bone_shade")
    # Éventail de plumes osseuses à plat au bout de la queue
    tip, tan = tail.at(1.0)
    dirs = [(math.sin(ang) * 1.1, 1.0, 0.1) for ang in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0)]
    quill_fan(rig, "TailQuill", tip - tan * 0.6, dirs, [1.0, 1.25, 1.4, 1.4, 1.25, 1.0], "Tail4",
              radius=0.045)


def build_ribcage(rig):
    back = c.Chain(BACK)
    for i in range(6):
        t = 0.15 + 0.8 * i / 5
        p, _ = back.at(t)
        bone = "Hips" if p.y > -0.3 else "Spine"
        bulge = math.sin((i + 1) / 7 * math.pi)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{i}{s}", p + Vector((0, 0, -0.06)), 0.4 + 0.35 * bulge,
                          0.75 + 0.45 * bulge, s, sweep=-0.25, radius=0.065), bone, "bone")
            if i in (1, 3):
                pit(rig, f"RibPit{i}{s}", p + Vector((s * (0.4 + 0.35 * bulge) * 0.95, -0.1,
                                                      -0.4 - 0.2 * bulge)), bone, size=0.05)
    rig.add(a.blade("Sternum", (0, -1.2, 2.0), (0, -0.7, 1.75), 0.42, 0.08, width_end=0.26,
                    normal=(0, 0, 1)), "Spine", "bone_shade")
    # Poche d'acide bouillonnante (pas un cristal : c'est la signature du T-Rex et du dragon)
    rig.add(r.ico("AcidSac", 0.32, subdivisions=2, location=(0, -0.4, 2.2),
                  scale=(1.0, 1.15, 0.9)), "Spine", "glow", glow=True)
    for k, (dx, dy, dz, rad) in enumerate(((0.3, 0.2, 0.3, 0.07), (-0.25, -0.2, 0.35, 0.06),
                                           (0.1, 0.35, 0.45, 0.05), (-0.1, -0.35, 0.5, 0.04),
                                           (0.2, -0.1, 0.62, 0.035))):
        rig.add(r.ico(f"Bubble{k}", rad, subdivisions=1, location=(dx, -0.4 + dy, 2.2 + dz)),
                "Spine", "glow", glow=True)
    drip(rig, "SacDrip", (0, -0.4, 1.9), "Spine", size=0.05)


# ---------------------------------------------------------------- membres

def build_arm(rig, s, side):
    shoulder, elbow, wrist = Vector((s * 0.42, -1.2, 2.45)), Vector((s * 0.78, -1.0, 1.95)), \
        Vector((s * 0.85, -1.85, 2.05))
    up, fore, hand = f"UpperArm_{side}", f"Forearm_{side}", f"Hand_{side}"
    rig.add(a.blade(f"Scapula{s}", (s * 0.4, -1.2, 2.55), (s * 0.48, -0.35, 3.0), 0.28, 0.07,
                    width_end=0.2, normal=(s, 0, 0.3)), "Spine", "bone")
    rig.add(a.long_bone(f"Humerus{s}", shoulder, elbow, 0.075), up, "bone")
    rig.add(a.long_bone(f"Radius{s}", elbow, wrist, 0.062), fore, "bone")
    rig.add(a.long_bone(f"Ulna{s}", elbow + Vector((s * 0.09, 0.05, -0.05)),
                        wrist + Vector((s * 0.08, 0.04, -0.04)), 0.03, condyles=False),
            fore, "bone_shade")
    # Éventail de plumes osseuses le long de l'avant-bras (« aile » repliée)
    dirs = [(s * 0.6, 1.0, -0.3 - 0.15 * k) for k in range(5)]
    for k in range(5):
        base = elbow.lerp(wrist, 0.1 + k * 0.2) + Vector((s * 0.06, 0.03, -0.02))
        quill_fan(rig, f"ArmQuill{s}{k}", base, [dirs[k]], [0.75 - k * 0.08], fore, radius=0.03)
    pit(rig, f"ArmPit{s}", elbow.lerp(wrist, 0.5) + Vector((s * 0.065, 0, 0.02)), fore, size=0.04)
    # Main à 3 doigts écartés, griffes en avant
    for k, (dx, length) in enumerate(((-0.12, 0.28), (0.0, 0.38), (0.12, 0.32))):
        knuckle = wrist + Vector((s * dx, -length, -0.08))
        rig.add(a.long_bone(f"Finger{s}{k}", wrist, knuckle, 0.035, knob=1.4, condyles=False),
                hand, "bone")
        rig.add(a.claw(f"HandClaw{s}{k}", knuckle, (s * dx * 2, -1, -0.5), 0.32, 0.05, curl=0.35),
                hand, "horn")
    drip(rig, f"HandDrip{s}", wrist + Vector((0, -0.45, -0.3)), hand, size=0.035)


def build_leg(rig, s, side):
    hip, knee, ankle = Vector((s * 0.5, 0.6, 2.65)), Vector((s * 0.68, -0.55, 1.55)), \
        Vector((s * 0.68, 0.55, 0.72))
    thigh, shin, foot, sickle = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}", f"Sickle_{side}"
    # Bassin : ilium + pubis rétroversé (signature des raptors) + ischium
    rig.add(a.blade(f"Ilium{s}", (s * 0.28, -0.3, 3.0), (s * 0.28, 1.4, 3.15), 0.3, 0.09,
                    width_end=0.24, mid=0.62, normal=(1, 0, 0)), "Hips", "bone")
    rig.add(r.ico(f"Acetabulum{s}", 0.17, subdivisions=1, location=hip), "Hips", "bone_shade")
    rig.add(a.long_bone(f"Pubis{s}", (s * 0.26, 0.55, 2.6), (s * 0.1, 1.25, 1.75), 0.065,
                        condyles=False), "Hips", "bone")
    rig.add(a.long_bone(f"Ischium{s}", (s * 0.26, 0.85, 2.65), (s * 0.1, 1.4, 2.25), 0.05,
                        condyles=False), "Hips", "bone_shade")

    rig.add(a.long_bone(f"Femur{s}", hip, knee, 0.13), thigh, "bone")
    for k, t in enumerate((0.35, 0.65)):
        pit(rig, f"FemurPit{s}{k}", hip.lerp(knee, t) + Vector((s * 0.12, 0, 0)), thigh,
            size=0.045)
    rig.add(r.ico(f"Patella{s}", 0.11, subdivisions=1, location=knee + Vector((0, -0.15, 0.03))),
            shin, "bone_shade")
    rig.add(a.long_bone(f"Tibia{s}", knee, ankle, 0.1), shin, "bone")
    rig.add(a.long_bone(f"Fibula{s}", knee + Vector((s * 0.12, 0.07, -0.08)),
                        ankle + Vector((s * 0.11, 0, 0.07)), 0.04, condyles=False), shin,
            "bone_shade")
    rig.add(r.ico(f"Ankle{s}", 0.13, subdivisions=1, location=ankle), foot, "bone_shade")

    for k, dx in enumerate((0.0, 0.15)):
        base = Vector((s * (0.7 + dx), -0.1, 0.18))
        rig.add(a.long_bone(f"Meta{s}{k}", ankle, base, 0.055, knob=1.5, condyles=False), foot,
                "bone")
        j1 = base + Vector((s * dx * 0.4, -0.28, -0.04))
        j2 = j1 + Vector((s * dx * 0.2, -0.22, -0.03))
        rig.add(a.long_bone(f"Phal{s}{k}a", base, j1, 0.045, knob=1.4, condyles=False), foot,
                "bone")
        rig.add(a.long_bone(f"Phal{s}{k}b", j1, j2, 0.04, knob=1.4, condyles=False), foot, "bone")
        rig.add(a.claw(f"Claw{s}{k}", j2, (s * dx * 0.3, -1, 0.05), 0.26, 0.06, curl=0.35), foot,
                "horn")
    # Griffe faucille relevée (os à part), qui goutte d'acide
    base = Vector((s * 0.55, -0.08, 0.3))
    rig.add(a.long_bone(f"Meta{s}2", ankle, base, 0.06, knob=1.5, condyles=False), foot, "bone")
    j1 = base + Vector((0, -0.22, 0.1))
    rig.add(a.long_bone(f"Phal{s}2", base, j1, 0.05, knob=1.4, condyles=False), sickle, "bone")
    rig.add(a.claw(f"Sickle{s}", j1, (0, -0.55, 1), 0.75, 0.115, curl=0.75, segments=6), sickle,
            "horn")
    drip(rig, f"SickleDrip{s}", j1 + Vector((0, -0.42, 0.28)), sickle, size=0.035)
    rig.add(a.claw(f"Spur{s}", ankle + Vector((0, 0.13, -0.26)), (0, 1, -0.6), 0.22, 0.045,
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
