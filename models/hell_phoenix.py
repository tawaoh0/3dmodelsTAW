"""Phénix squelette (≈ 6 studs de haut, 10 d'envergure) — créature animable.
Pack « Enfers volcaniques », créature 2.

Animal modèle : l'aigle — crâne arrondi, énormes orbites cerclées d'un **anneau sclérotique**
(petites plaques osseuses autour de l'œil), bec crochu à « dent » tomiale, bréchet profond,
fourchette, ailes à humérus / cubitus / main, serres puissantes.

Identité : os ivoire cendré qui virent au brûlé, bec et serres noirs ; pas de cornes mais une
**crête de plumes d'os** enflammées ; ailes déployées en **plumes d'os** (rachis + vexille)
aux pointes de feu ; éventail de queue et longues traînes ; dressé sur ses serres, ailes
levées ; cœur-œuf de feu dans la cage ; thème d'effets « phoenix » (flammes dorées).

4 pièces Roblox : corps, Head, Wings, + lumineux.
Os : Root, Hips, Chest, Neck1-2, Head, Jaw, Wing{L,R}_1-3, Tail, Leg{L,R}_1-3, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#e2d3bd",
    "bone_shade": "#a5552c",
    "tooth": "#fff4dc",
    "horn": "#24160f",
    "horn_tip": "#ff9a1a",
    "disc": "#5a2a16",
    "vane": "#c98a4a",
    "gum": "#6a1e12",
    "ink": "#120a06",
    "glow": "#ffb21a",
    "glow_hot": "#fff3b0",
}

EFFECT_THEME = "phoenix"

TEST_POSE = {
    "Jaw": (25, 0, 0),
    "Wing_L_1": (0, -30, 0),
    "Wing_R_2": (0, 25, 0),
    "Neck2": (-15, 0, 0),
    "Tail": (20, 0, 0),
}

VIEW = (0.75, -1.0, 0.3)

SPINE = a.smooth_path([(0, 0.95, 2.5), (0, 0.25, 2.75), (0, -0.45, 3.1)], 8)
NECK = a.smooth_path([(0, -0.45, 3.15), (0, -0.78, 3.7), (0, -0.6, 4.3), (0, -0.72, 4.82)], 10)
# Crâne d'aigle : dôme crânien → grandes orbites → base du bec (le bec est en corne à part)
SKULL = [(-0.62, 0.24, 0.32, 0.24, 5.22, 4.74), (-0.88, 0.32, 0.4, 0.3, 5.4, 4.7),
         (-1.12, 0.29, 0.37, 0.27, 5.33, 4.76), (-1.36, 0.17, 0.21, 0.17, 5.16, 4.84)]
BEAK = [(-1.3, 0.15, 0.19, 0.16, 5.15, 4.86), (-1.6, 0.11, 0.13, 0.11, 5.08, 4.88),
        (-1.88, 0.07, 0.08, 0.07, 5.0, 4.86)]
EYE = (-1.07, 5.1)
HINGE = (0.24, -0.92, 4.76)
CHIN = (0.0, -1.85, 4.66)
HEAD = dict(part="Head")
WINGS = dict(part="Wings")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def wing_points(s):
    shoulder = Vector((s * 0.42, -0.35, 3.35))
    elbow = Vector((s * 1.65, 0.05, 4.2))
    wrist = Vector((s * 2.75, -0.35, 5.0))
    hand = Vector((s * 3.65, -0.15, 5.55))
    tip = Vector((s * 4.35, 0.15, 5.7))
    return shoulder, elbow, wrist, hand, tip


def leg_points(s):
    hip = Vector((s * 0.35, 0.5, 2.4))
    knee = Vector((s * 0.48, -0.1, 1.75))
    ankle = Vector((s * 0.46, 0.45, 0.8))
    foot = Vector((s * 0.45, 0.05, 0.16))
    return hip, knee, ankle, foot


def feather(rig, name, base, tip, width, bone, flame=True, normal=None, **kw):
    """Plume d'os : rachis (tube) + vexille (lame) + barbes en dents de scie + flamme au bout.

    `normal` : normale du plan de la plume (plan de l'aile), pour qu'on la voie de face."""
    base, tip = Vector(base), Vector(tip)
    d = tip - base
    side, up = a._basis(d)
    if normal is not None:
        up = Vector(normal).normalized()
        side = d.normalized().cross(up).normalized()
    rig.add(r.tube(f"{name}Rachis", [tuple(base), tuple(base.lerp(tip, 0.6)), tuple(tip)],
                   [0.045, 0.035, 0.015], segments=4), bone, "bone", **kw)
    rig.add(a.blade(f"{name}Vane", base.lerp(tip, 0.1), tip, width * 0.6, 0.03, width_end=0.02,
                    mid=width, normal=up, bevel=0), bone, "vane", **kw)
    for j, t in enumerate((0.4, 0.7)):
        q = base.lerp(tip, t)
        rig.add(a.claw(f"{name}Barb{j}", q, side + d.normalized() * 0.8, width * 0.55, 0.02,
                       curl=0, segments=4), bone, "bone_shade", **kw)
    if flame:
        rig.add(a.crystal(f"{name}Flame", tip - d.normalized() * 0.08, 0.09, 0.6, sides=5), bone,
                "glow", glow=True)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[4], "Root")
    rig.bone("Chest", SPINE[4], SPINE[-1], "Hips")
    rig.bone("Neck1", NECK[0], NECK[5], "Chest")
    rig.bone("Neck2", NECK[5], NECK[-1], "Neck1")
    rig.bone("Head", NECK[-1], (0, -2.0, 5.0), "Neck2")
    rig.bone("Jaw", (0, HINGE[1], HINGE[2]), (0, CHIN[1], CHIN[2]), "Head")
    rig.bone("Tail", SPINE[0], (0, 2.2, 1.9), "Hips")
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd, tp = wing_points(s)
        rig.bone(f"Wing_{side}_1", sh, el, "Chest")
        rig.bone(f"Wing_{side}_2", el, wr, f"Wing_{side}_1")
        rig.bone(f"Wing_{side}_3", wr, tp, f"Wing_{side}_2")
        hp, kn, an, ft = leg_points(s)
        rig.bone(f"Leg_{side}_1", hp, kn, "Hips")
        rig.bone(f"Leg_{side}_2", kn, an, f"Leg_{side}_1")
        rig.bone(f"Leg_{side}_3", an, ft, f"Leg_{side}_2")
        rig.fx(f"Eye{side}", (s * 0.3, EYE[0], EYE[1]), "Head")
        rig.fx(f"WingTip{side}", tp + Vector((0, 0.8, -0.6)), f"Wing_{side}_3")
    rig.fx("Heart", (0, -0.15, 2.45), "Chest")
    rig.fx("Crest", (0, -0.6, 5.9), "Head")
    rig.fx("Mouth", (0, -1.5, 4.75), "Head")
    rig.fx("TailFire", (0, 2.8, 1.2), "Tail")


# ---------------------------------------------------------------- tête d'aigle

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, tip=None)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.17, 0.16),
                  a.hole_x((0, -0.78, 4.92), 0.1, 0.08)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Bec en corne noire, crochet, narines, dents tomiales dentelées
    beak = a.loft_profile("Beak", BEAK, droop=0.35)
    rig.add(beak, H, "horn", **HEAD)
    rig.add(a.claw("BeakHook", (0, -1.86, 4.96), (0, -0.6, -1), 0.32, 0.07, curl=0.5,
                   segments=6), H, "horn", **HEAD)
    rig.add(r.tube("Culmen", [(0, -1.3, 5.16), (0, -1.6, 5.1), (0, -1.86, 5.02)],
                   [0.04, 0.035, 0.025], segments=4), H, "bone_shade", **HEAD)
    rig.add(a.ring_around("Cere", (0, -1.33, 5.0), (0, -1, 0.1), 0.19, 0.035, segments=12), H,
            "bone_shade", **HEAD)
    for s in (-1, 1):
        rig.add(r.ico(f"Naris{s}", 0.04, subdivisions=1, location=(s * 0.14, -1.42, 5.04),
                      scale=(0.6, 1.6, 0.8)), H, "ink", **HEAD)
        for k in range(4):
            y = -1.38 - 0.13 * k
            x = s * a.width_at(BEAK, y, 3) * 0.95
            rig.add(mr.tooth(f"Tomial{s}{k}", (x, y, 4.88), (x, y - 0.03, 4.88 - 0.13 + 0.015 * k),
                             0.09, 0.04, Vector((s, -0.3, 0))), H, "tooth", **HEAD)
    # Orbites : anneau sclérotique de plaques, œil de feu, sourcil, crête de plumes d'os
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.13, subdivisions=2, location=c0 - Vector((s * 0.08, 0, 0))), H,
                "glow", glow=True)
        for k in range(12):
            ang = 2 * math.pi * k / 12
            p = c0 + Vector((s * 0.02, 0.17 * math.cos(ang), 0.16 * math.sin(ang)))
            rig.add(a.blade(f"Scleral{s}{k}", p, p + Vector((s * 0.03, 0.05 * math.cos(ang),
                                                                 0.05 * math.sin(ang))),
                            0.08, 0.025, width_end=0.07, normal=(s, 0, 0), bevel=0), H,
                    "bone_shade", **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.12, -1.28, 5.28), (s * 0.34, -0.9, 5.38), 0.16, 0.07,
                        width_end=0.1, mid=0.18, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        rig.add(a.claw(f"BrowSpike{s}", (s * 0.33, -0.95, 5.38), (s * 0.4, 0.8, 0.3), 0.22, 0.04,
                       curl=-0.1, segments=4), H, "horn", **HEAD)
        rig.add(r.tube(f"Jugal{s}", [(s * 0.2, -1.32, 4.82), (s * 0.3, -1.05, 4.78),
                                     (s * 0.26, -0.82, 4.8)], 0.035, segments=4), H, "bone",
                **HEAD)
        mr.scar(rig, f"EmberScar{s}", top(s * 0.12, -0.7), top(s * 0.2, -1.0), H, width=0.03,
                seed=s)
    # Crête de plumes d'os enflammées, de l'arrière du crâne vers le haut
    for k in range(5):
        base = top(0.06 * (k - 2), -0.72 - 0.08 * abs(k - 2)) or Vector((0, -0.8, 5.35))
        tip = base + Vector((0.18 * (k - 2), 0.55 + 0.1 * k, 0.75 - 0.1 * abs(k - 2)))
        feather(rig, f"Crest{k}", base, tip, 0.2, H, normal=(1, 0, 0), **HEAD)
    # Mâchoire inférieure (bec du bas) en V, dents tomiales
    for s in (-1, 1):
        line = [Vector((s * HINGE[0], HINGE[1], HINGE[2])),
                Vector((s * 0.16, -1.25, 4.76)), Vector((s * 0.1, -1.55, 4.76)),
                Vector((s * 0.04, -1.82, 4.72))]
        rig.add(a.band(f"Mandible{s}", line, [0.16, 0.15, 0.12, 0.07], [0.1, 0.09, 0.08, 0.06],
                       up=[Vector((s * 0.4, 0, 1))] * 4, offset=1), J, "horn", **HEAD)
        rig.add(r.tube(f"MandibleRidge{s}", [tuple(p + Vector((s * 0.05, 0, -0.07))) for p in line[:3]],
                       0.025, segments=4), J, "bone_shade", **HEAD)
        for k in range(3):
            q = mr.along(line, 0.45 + 0.17 * k)
            rig.add(mr.tooth(f"LowTomial{s}{k}", q, q + Vector((0, -0.02, 0.11)), 0.08, 0.035,
                             Vector((s, -0.3, 0))), J, "tooth", **HEAD)
    rig.add(r.ico("Throat", 0.13, subdivisions=2, location=(0, -1.0, 4.8), scale=(1.2, 1.6, 0.6)),
            H, "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    for path, bones, size in ((SPINE, ("Hips", "Chest"), 0.2), (NECK, ("Neck1", "Neck2"), 0.14)):
        n = len(path)
        for i in range(n):
            t = tangent(path, i)
            bone = bones[0] if i < n // 2 else bones[1]
            rig.add(a.vertebra(f"Vert{bones[0]}{i}", path[i], t, size, spine=1.1, lean=0.4),
                    bone, "bone")
            if i < n - 1:
                rig.add(a.disc(f"Disc{bones[0]}{i}", path[i].lerp(path[i + 1], 0.5), t, size),
                        bone, "disc")
            if bones[0] == "Neck1" and i % 2 == 1:   # collerette de flammes sur le cou
                side, up = a._basis(t)
                rig.add(a.crystal(f"NeckFlame{i}", path[i] + up * 0.2 + Vector((0, 0.05, 0)), 0.05,
                                  0.35, sides=4), bone, "glow", glow=True)
    # Bréchet profond, fourchette, coracoïdes, côtes à processus uncinés
    rig.add(a.blade("Keel", (0, -0.55, 2.55), (0, 0.45, 1.75), 0.75, 0.07, width_end=0.25,
                    mid=0.8, normal=(1, 0, 0)), "Chest", "bone")
    rig.add(a.blade("SternumPlate", (0, -0.55, 2.62), (0, 0.4, 2.1), 0.8, 0.06, width_end=0.5,
                    normal=(0, 0.3, 1)), "Chest", "bone_shade")
    for s in (-1, 1):
        sh = wing_points(s)[0]
        rig.add(r.tube(f"Furcula{s}", [tuple(sh + Vector((0, -0.05, -0.05))),
                                       (s * 0.2, -0.65, 2.95), (0, -0.62, 2.65)], 0.045,
                       segments=5), "Chest", "bone")
        rig.add(a.long_bone(f"Coracoid{s}", sh, (s * 0.25, -0.5, 2.6), 0.06, condyles=False),
                "Chest", "bone")
        rig.add(a.blade(f"Scapula{s}", sh, (s * 0.25, 0.55, 3.0), 0.12, 0.04, width_end=0.05,
                        normal=(0, 0, 1)), "Chest", "bone_shade")
    for k in range(5):
        i = 1 + k
        for s in (-1, 1):
            root = SPINE[i]
            low = Vector((s * 0.32, root.y - 0.25, 2.3 - 0.08 * k))
            mid = root.lerp(low, 0.5) + Vector((s * 0.35, 0, 0))
            rig.add(r.tube(f"Rib{k}{s}", [tuple(root), tuple(mid), tuple(low)], 0.04, segments=4),
                    "Chest" if i >= 4 else "Hips", "bone")
            rig.add(a.claw(f"Uncinate{k}{s}", mid, (0, 1, 0.3), 0.18, 0.025, curl=0, segments=4),
                    "Chest" if i >= 4 else "Hips", "bone_shade")
    # Cœur-œuf de feu
    rig.add(r.ico("FireEgg", 0.28, subdivisions=2, location=(0, -0.15, 2.5), scale=(0.9, 0.9, 1.2)),
            "Chest", "glow", glow=True)
    for k in range(4):
        ang = k * math.pi / 2 + 0.4
        rig.add(a.crystal(f"EggFlame{k}", (0.22 * math.cos(ang), -0.15 + 0.22 * math.sin(ang), 2.35),
                          0.05, 0.45, sides=4), "Chest", "glow", glow=True)
    # Synsacrum + bassin, pygostyle, éventail de queue et traînes enflammées
    rig.add(a.blade("Synsacrum", SPINE[0] + Vector((0, 0.1, 0.05)), SPINE[3], 0.55, 0.06,
                    width_end=0.35, normal=(0, 0, 1)), "Hips", "bone")
    for s in (-1, 1):
        rig.add(a.blade(f"Ilium{s}", (s * 0.15, 0.3, 2.7), (s * 0.35, 0.9, 2.35), 0.3, 0.05,
                        width_end=0.2, normal=(s, 0, 0.6)), "Hips", "bone_shade")
    pyg = Vector((0, 1.1, 2.45))
    rig.add(a.claw("Pygostyle", SPINE[0], pyg - SPINE[0], 0.3, 0.07, curl=0, segments=5), "Tail",
            "bone")
    for k in range(9):
        ang = (k - 4) * 0.2
        d = Vector((math.sin(ang), math.cos(ang), -0.45 - 0.05 * abs(k - 4))).normalized()
        feather(rig, f"TailFeather{k}", pyg, pyg + d * (1.6 - 0.08 * abs(k - 4)), 0.34, "Tail",
                normal=Vector((0, 0.45, 1)))
    for k, sx in enumerate((-0.25, 0.0, 0.25)):
        tr = [pyg, pyg + Vector((sx, 0.9, -0.5)), pyg + Vector((sx * 1.6, 1.8, -0.6)),
              pyg + Vector((sx * 2, 2.4, -0.25))]
        rig.add(r.tube(f"Streamer{k}", [tuple(p) for p in tr], [0.04, 0.035, 0.025, 0.015],
                       segments=4), "Tail", "bone_shade")
        rig.add(a.crystal(f"StreamerFlame{k}", tr[-1], 0.08, 0.45, sides=5), "Tail", "glow",
                glow=True)
    # Pattes : tibiotarse, tarsométatarse écailleux, 3 doigts avant + hallux, serres noires
    for s, side in ((1, "L"), (-1, "R")):
        hp, kn, an, ft = leg_points(s)
        b1, b2, b3 = f"Leg_{side}_1", f"Leg_{side}_2", f"Leg_{side}_3"
        rig.add(a.long_bone(f"Femur{s}", hp, kn, 0.1, segments=6), b1, "bone")
        rig.add(a.long_bone(f"Tibiotarsus{s}", kn, an, 0.08, segments=6), b2, "bone")
        rig.add(a.long_bone(f"Tarsus{s}", an, ft, 0.07, segments=6), b3, "bone")
        for k in range(4):
            q = an.lerp(ft, 0.2 + 0.18 * k)
            rig.add(a.ring_around(f"TarsusScale{s}{k}", q, ft - an, 0.085, 0.025, segments=6), b3,
                    "horn")
        rig.add(a.ring_around(f"AnkleFlame{s}", an, ft - an, 0.12, 0.035, segments=8), b3,
                "glow", glow=True)
        for k, ang in enumerate((-0.45, 0.0, 0.45, math.pi)):
            d = Vector((math.sin(ang) * s, -math.cos(ang), 0))
            toe_mid = ft + d * 0.3 + Vector((0, 0, -0.06))
            rig.add(a.long_bone(f"Toe{s}{k}", ft, toe_mid, 0.04, condyles=False, segments=5), b3,
                    "bone")
            rig.add(a.claw(f"Talon{s}{k}", toe_mid, d + Vector((0, 0, -0.9)), 0.28, 0.05,
                           curl=0.55, segments=5), b3, "horn")


def build_wings(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr, hd, tp = wing_points(s)
        b1, b2, b3 = f"Wing_{side}_1", f"Wing_{side}_2", f"Wing_{side}_3"
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.1, segments=7), b1, "bone", **WINGS)
        off = (wr - el).cross(Vector((0, 0, 1))).normalized() * 0.07
        rig.add(a.long_bone(f"Ulna{s}", el + off, wr + off, 0.07, condyles=False, segments=6), b2,
                "bone", **WINGS)
        rig.add(a.long_bone(f"Radius{s}", el - off, wr - off, 0.05, condyles=False, segments=5),
                b2, "bone_shade", **WINGS)
        rig.add(a.long_bone(f"Carpometacarpus{s}", wr, hd, 0.06, condyles=False, segments=5), b3,
                "bone", **WINGS)
        rig.add(a.claw(f"Digit{s}", hd, tp - hd, (tp - hd).length, 0.05, curl=0, segments=5), b3,
                "bone", **WINGS)
        rig.add(a.claw(f"Alula{s}", wr, (s * 0.3, -1, 0.3), 0.3, 0.04, curl=0.2, segments=4), b3,
                "horn", **WINGS)
        for q, bone in ((el, b2), (wr, b3)):
            rig.add(a.ring_around(f"WingJoint{s}{bone}", q, wr - el, 0.11, 0.03, segments=8), bone,
                    "glow", glow=True)
        # Primaires (main) en éventail, secondaires (avant-bras), couvertures
        span = (tp - sh).normalized()
        hand_line = [wr, hd, tp]
        for k in range(11):
            t = k / 10
            base = mr.along(hand_line, 1 - t * 0.95)
            ang = 0.15 + 1.05 * t
            d = Vector((s * math.cos(ang) * 0.75, math.sin(ang), -0.45 - 0.25 * t)).normalized()
            feather(rig, f"Primary{s}{k}", base, base + d * (2.2 - 0.35 * t), 0.42, b3,
                    normal=span.cross(d), **WINGS)
        for k in range(9):
            t = (k + 0.5) / 9
            base = el.lerp(wr, 1 - t)
            d = Vector((s * 0.15, 1, -0.75 - 0.1 * t)).normalized()
            feather(rig, f"Secondary{s}{k}", base, base + d * (1.6 - 0.2 * t), 0.4, b2,
                    flame=k % 2 == 0, normal=span.cross(d), **WINGS)
        for k in range(8):
            t = (k + 0.5) / 8
            base = sh.lerp(el, 0.3 + 0.7 * t * 2) if k < 4 else el.lerp(wr, (t - 0.5) * 2)
            bone = b1 if k < 4 else b2
            d = Vector((s * 0.1, 1, -0.5)).normalized()
            feather(rig, f"Covert{s}{k}", base, base + d * 0.85, 0.3, bone, flame=False,
                    normal=span.cross(d), **WINGS)
        # Langues de feu le long du bord d'attaque
        for k, (q, bone) in enumerate(((sh.lerp(el, 0.5), b1), (el.lerp(wr, 0.3), b2),
                                       (el.lerp(wr, 0.7), b2), (wr.lerp(hd, 0.5), b3))):
            rig.add(a.crystal(f"EdgeFlame{s}{k}", q + Vector((0, -0.05, 0.08)), 0.07, 0.5, sides=5),
                    bone, "glow", glow=True)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_wings(rig)
    return rig
