"""Araignée tisseuse d'âmes squelette (≈ 3,5 studs de haut, 7 d'envergure) — animable.
Pack « Cimetière gothique / nécromancie », créature 5.

Animal modèle : la **mygale** — céphalothorax bombé à fovéa, 8 yeux groupés sur le devant
(2 grands médians), chélicères massives à crochets, pédipalpes, 8 pattes coudées aux
genoux plus hauts que le corps, abdomen ovale à filières.

Identité : os blanchi, ombres bleu ardoise, crochets noirs ; **aucune corne** : 8 yeux et
chélicères dentelées ; abdomen en **cage d'os** où flottent des âmes prisonnières ; **toile
d'âmes** lumineuse et **cocon-cercueil** pendu aux filières ; thème d'effets « soulweb ».

Pièces Roblox : corps (abdomen), Head (céphalothorax), Legs, + lumineux.
Os : Root, Head (céphalothorax), Abdomen, Chelicera_{L,R}, Palp_{L,R}, Leg{1-4}_{L,R}_{1-3}, Cocoon.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#e4dbc4",
    "bone_shade": "#3d4c55",
    "tooth": "#f6f1e2",
    "horn": "#0f1215",
    "disc": "#22292e",
    "silk": "#cfe9ee",
    "wood": "#3b2a24",
    "iron": "#45424a",
    "ink": "#050607",
    "glow": "#8ff6ff",
    "glow_hot": "#eaffff",
}

EFFECT_THEME = "soulweb"

TEST_POSE = {
    "Leg1_L_1": (0, 0, 25),
    "Leg1_L_2": (-30, 0, 0),
    "Chelicera_R": (25, 0, 0),
    "Abdomen": (15, 0, 0),
    "Cocoon": (0, 20, 0),
}

VIEW = (1.0, -0.8, 0.6)

# Céphalothorax : (y, demi-larg. dessus, flancs, bas, z dessus, z bas)
THORAX = [(0.45, 0.3, 0.42, 0.36, 2.05, 1.55), (0.05, 0.5, 0.68, 0.58, 2.3, 1.42),
          (-0.6, 0.56, 0.74, 0.64, 2.36, 1.4), (-1.15, 0.42, 0.56, 0.46, 2.25, 1.48),
          (-1.55, 0.28, 0.36, 0.3, 2.1, 1.58)]
ABD_C = Vector((0, 2.15, 2.25))
ABD_R = (1.15, 1.55, 1.05)            # demi-axes x, y, z
HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def leg(k, s):
    """Attache, genou (haut), cheville, pied au sol pour la patte k (0 = avant)."""
    th = math.radians((-58, -20, 18, 52)[k])
    d = Vector((s * math.cos(th), math.sin(th), 0))
    a0 = Vector((s * 0.55, -1.0 + 0.4 * k, 1.75))
    reach = (1.0, 0.95, 0.95, 1.1)[k]
    return (a0, a0 + d * 1.2 * reach + Vector((0, 0, 1.25 - a0.z + 1.75)),
            a0 + d * 2.3 * reach + Vector((0, 0, 1.2 - a0.z)),
            a0 + d * 2.85 * reach + Vector((0, 0, 0.05 - a0.z)))


def abd_point(u, v, scale=1.0):
    """Point sur l'ellipsoïde de l'abdomen (u : tour autour de Y, v : -1 avant .. 1 arrière)."""
    rr = math.sqrt(max(0.0, 1 - v * v))
    return ABD_C + Vector((ABD_R[0] * rr * math.cos(u), ABD_R[1] * v, ABD_R[2] * rr * math.sin(u))) * scale


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Head", (0, 0.4, 1.85), (0, -1.5, 1.85), "Root")
    rig.bone("Abdomen", (0, 0.55, 1.95), ABD_C + Vector((0, ABD_R[1], 0)), "Head")
    tail = ABD_C + Vector((0, ABD_R[1] * 0.97, -0.2))
    rig.bone("Cocoon", tail, tail + Vector((0, 0.4, -0.9)), "Abdomen")
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Chelicera_{side}", (s * 0.2, -1.5, 1.7), (s * 0.22, -1.85, 1.05), "Head")
        rig.bone(f"Palp_{side}", (s * 0.4, -1.4, 1.6), (s * 0.7, -2.2, 0.8), "Head")
        for k in range(4):
            p = leg(k, s)
            prev = "Head"
            for j in range(3):
                prev = rig.bone(f"Leg{k + 1}_{side}_{j + 1}", p[j], p[j + 1], prev)
        rig.fx(f"Eye{side}", (s * 0.12, -1.5, 2.15), "Head")
        rig.fx(f"Fang{side}", (s * 0.18, -1.95, 1.0), f"Chelicera_{side}")
    rig.fx("Souls", ABD_C, "Abdomen")
    rig.fx("Spinneret", ABD_C + Vector((0, ABD_R[1], -0.2)), "Abdomen")
    rig.fx("Web", (0, 4.4, 0.8), "Root")


# ---------------------------------------------------------------- céphalothorax

def build_thorax(rig):
    T = "Head"
    shell = a.loft_profile("Carapace", THORAX, droop=0.0, tip_length=0.1)
    hit = a.surface_caster(shell)
    holes = [a.hole_along((0, -0.35, 2.3), (0, 0, 1), (1, 0, 0), 0.08, 0.18, depth=0.4)]   # fovéa
    for s in (-1, 1):
        for y, rx, ry in ((-0.75, 0.13, 0.2), (0.0, 0.12, 0.18)):
            holes.append(a.hole_along((s * 0.32, y, 2.25), (s * 0.4, 0, 1), (1, 0, 0), rx, ry, depth=0.5))
        holes.append(a.hole_x((0, -0.4, 1.62), 0.35, 0.08))
    a.cut(shell, holes)
    rig.add(shell, T, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 6))
        return p

    # Sillons rayonnants depuis la fovéa (nervures)
    for k in range(4):
        for s in (-1, 1):
            ang = math.radians(-60 + 40 * k)
            pts = [top(s * 0.12 * math.cos(ang), -0.35 + 0.12 * math.sin(ang)),
                   top(s * 0.48 * math.cos(ang), -0.35 + 0.55 * math.sin(ang))]
            if all(p is not None for p in pts):
                rig.add(r.tube(f"Groove{k}{s}", [tuple(p + Vector((0, 0, 0.02))) for p in pts], 0.03,
                               segments=4), T, "bone_shade", **HEAD)
    rig.add(r.tube("FoveaRim", [tuple(top(0.1 * math.cos(t), -0.35 + 0.2 * math.sin(t)) + Vector((0, 0, 0.02)))
                                for t in (2 * math.pi * k / 10 for k in range(10))], 0.025, segments=4,
                   closed=True), T, "bone_shade", **HEAD)
    # 8 yeux sur la butte oculaire : 2 grands médians, 6 latéraux
    rig.add(r.ico("EyeMound", 0.2, subdivisions=1, location=(0, -1.38, 2.12), scale=(1.4, 1, 0.7)), T,
            "bone_shade", **HEAD)
    eyes = [(0.1, -1.55, 2.18, 0.08), (0.24, -1.48, 2.22, 0.05), (0.3, -1.4, 2.12, 0.05),
            (0.18, -1.42, 2.3, 0.045)]
    for s in (-1, 1):
        for k, (x, y, z, rad) in enumerate(eyes):
            p = Vector((s * x, y, z))
            rig.add(r.ico(f"Eye{s}{k}", rad, subdivisions=2, location=p), T, "glow", glow=True)
            rig.add(a.ring_around(f"EyeRim{s}{k}", p + Vector((0, 0.01, 0)), (s * 0.3, -1, 0.4), rad * 1.15,
                                  0.02, segments=8), T, "horn", **HEAD)
    # Rebord de la carapace hérissé de soies noires + nodules d'os sur le dos
    for s in (-1, 1):
        for k in range(8):
            y = 0.3 - 0.22 * k
            x = a.side_width(THORAX, y, 1.75)
            rig.add(a.claw(f"Bristle{s}{k}", (s * x * 0.97, y, 1.75), (s, -0.2, 0.5), 0.18, 0.03, curl=0.2,
                           segments=4), T, "horn", **HEAD)
        for k, y in enumerate((0.15, -0.95)):
            p = top(s * 0.22, y)
            if p is not None:
                rig.add(r.ico(f"Nodule{s}{k}", 0.07, subdivisions=1, location=p, scale=(1, 1, 0.6)), T,
                        "bone_shade", **HEAD)
    # Sternum et coxae (dessous)
    rig.add(r.ico("Sternum", 0.4, subdivisions=1, location=(0, -0.45, 1.45), scale=(1, 1.4, 0.3)), T,
            "bone_shade", **HEAD)


def build_mouth(rig):
    for s, side in ((1, "L"), (-1, "R")):
        ch = f"Chelicera_{side}"
        base, tip = Vector((s * 0.2, -1.5, 1.7)), Vector((s * 0.22, -1.85, 1.08))
        rig.add(a.long_bone(f"Chelicera{s}", base, tip, 0.14, segments=7), ch, "bone", **HEAD)
        rig.add(a.ring_around(f"ChelRing{s}", base.lerp(tip, 0.35), tip - base, 0.15, 0.03, segments=8), ch,
                "bone_shade", **HEAD)
        # Crochet noir qui se replie vers l'intérieur + goutte de venin
        rig.add(a.claw(f"Fang{s}", tip, (-s * 0.7, -0.4, -0.5), 0.42, 0.065, curl=0.55, segments=6), ch, "horn",
                **HEAD)
        fang_end, _ = a.claw_point(tip, (-s * 0.7, -0.4, -0.5), 0.42, 0.55, 1.0)
        rig.add(r.ico(f"Venom{s}", 0.035, subdivisions=1, location=fang_end + Vector((0, 0, -0.04)),
                      scale=(1, 1, 1.6)), ch, "glow", glow=True)
        # Rangée de dents dentelées sur la face interne de la chélicère
        for k in range(4):
            p = base.lerp(tip, 0.4 + 0.15 * k) + Vector((-s * 0.12, -0.03, 0))
            rig.add(mr.tooth(f"ChelTooth{s}{k}", p, p + Vector((-s * 0.13, -0.02, -0.03)), 0.07, 0.05,
                             Vector((0, -1, 0)), curl=0.1), ch, "tooth", **HEAD)
        # Pédipalpe à 3 segments, bout griffu
        pp = [Vector((s * 0.4, -1.4, 1.6)), Vector((s * 0.65, -1.9, 1.75)), Vector((s * 0.72, -2.15, 1.2)),
              Vector((s * 0.7, -2.2, 0.85))]
        for j in range(3):
            rig.add(a.long_bone(f"Palp{s}{j}", pp[j], pp[j + 1], 0.06, condyles=False, segments=5),
                    f"Palp_{side}", "bone", **HEAD)
        rig.add(a.claw(f"PalpClaw{s}", pp[3], (0, -0.5, -1), 0.15, 0.04, curl=0.4, segments=4), f"Palp_{side}",
                "horn", **HEAD)


# ---------------------------------------------------------------- abdomen-cage, toile, cocon

def build_abdomen(rig):
    A = "Abdomen"
    rig.add(r.tube("Pedicel", [(0, 0.4, 1.85), (0, 0.65, 1.95), tuple(abd_point(0, -1))], [0.14, 0.11, 0.14],
                   segments=6), A, "bone_shade")
    # Cage : anneaux d'os transverses + baleines longitudinales
    for k, v in enumerate((-0.75, -0.4, 0.0, 0.4, 0.75)):
        rr = math.sqrt(1 - v * v)
        c0 = ABD_C + Vector((0, ABD_R[1] * v, 0))
        ring = [tuple(c0 + Vector((ABD_R[0] * rr * math.cos(u), 0, ABD_R[2] * rr * math.sin(u))))
                for u in (2 * math.pi * j / 14 for j in range(14))]
        rig.add(r.tube(f"CageRing{k}", ring, 0.06, segments=5, closed=True), A, "bone")
    for j in range(8):
        u = 2 * math.pi * j / 8 + math.pi / 8
        pts = [tuple(abd_point(u, v)) for v in (-0.92, -0.6, -0.2, 0.2, 0.6, 0.92)]
        rig.add(r.tube(f"CageStave{j}", pts, [0.04, 0.06, 0.07, 0.07, 0.06, 0.04], segments=4), A,
                "bone_shade" if j % 2 else "bone")
    # Dos : rangée de « vertèbres » et chevrons pointus (motif de crâne en os)
    for k, v in enumerate((-0.7, -0.35, 0.0, 0.35, 0.7)):
        p = abd_point(math.pi / 2, v, 1.04)
        rig.add(a.vertebra(f"DorsalVert{k}", p, (0, 1, 0), 0.14, spine=1.2, lean=0.3), A, "bone")
        if k % 2 == 0:
            for s in (-1, 1):
                q = abd_point(math.pi / 2 - s * 0.6, v, 1.04)
                rig.add(a.claw(f"DorsalSpike{k}{s}", q, (s * 0.6, 0.3, 1), 0.3, 0.05, curl=0.1, segments=4), A,
                        "horn")
    # Âmes prisonnières à l'intérieur de la cage
    for k, (dx, dy, dz, rad) in enumerate(((0, 0, 0, 0.38), (0.45, -0.6, -0.1, 0.2), (-0.4, 0.55, 0.15, 0.22),
                                           (0.2, 0.8, -0.3, 0.15))):
        rig.add(r.ico(f"Soul{k}", rad, subdivisions=2, location=ABD_C + Vector((dx, dy, dz)), scale=(1, 1, 1.4)),
                A, "glow", glow=True)
    # Filières + fils d'âme jusqu'au sol (ancrage de la toile)
    rig.add(r.ico("CageCap", 0.22, subdivisions=1, location=abd_point(0, 0.97), scale=(1, 0.8, 1)), A, "bone_shade")
    sp = ABD_C + Vector((0, ABD_R[1] * 0.95, -0.15))
    for s in (-1, 0, 1):
        rig.add(a.claw(f"Spinneret{s}", sp + Vector((s * 0.12, -0.1, 0)), (s * 0.3, 1, -0.3), 0.3, 0.05, curl=0,
                       segments=4), A, "bone_shade")
    web_c = Vector((0, 4.4, 0.8))
    rig.add(r.tube("WebLine", [tuple(sp + Vector((0, 0.25, 0))), tuple(web_c)], 0.025, segments=4), A, "glow",
            glow=True)
    # Toile d'âmes dressée derrière : rayons + spirale lumineuse, piquets d'os au sol
    rays = [web_c + Vector((math.cos(math.pi * j / 7) * 1.6, 0.0, math.sin(math.pi * j / 7) * 1.4 - 0.75))
            for j in range(8)]
    for j, end in enumerate(rays):
        rig.add(r.tube(f"WebRay{j}", [tuple(web_c), tuple(end)], 0.02, segments=4), "Root", "glow", glow=True)
    for ring_k, f in enumerate((0.35, 0.6, 0.85)):
        pts = [tuple(web_c.lerp(e, f) + Vector((0, 0, -0.06 * (j % 2)))) for j, e in enumerate(rays)]
        rig.add(r.tube(f"WebSpiral{ring_k}", pts, 0.015, segments=4), "Root", "glow", glow=True)
    for s in (-1, 1):
        post = web_c + Vector((s * 1.65, 0, -0.8))
        rig.add(a.long_bone(f"WebPost{s}", post, post + Vector((0, 0, 1.1)), 0.06, condyles=False, segments=5),
                "Root", "bone")
    # Cocon-cercueil pendu aux filières, enrobé de soie, âme qui luit à travers
    top = ABD_C + Vector((0, ABD_R[1] * 0.97, -0.2))
    rig.add(r.tube("CocoonThread", [tuple(top), tuple(top + Vector((0, 0.35, -0.45)))], 0.025, segments=4),
            "Cocoon", "silk")
    cc = top + Vector((0, 0.4, -0.95))
    outline = [(-0.1, 0.42), (0.1, 0.42), (0.17, 0.22), (0.11, -0.4), (-0.11, -0.4), (-0.17, 0.22)]
    rig.add(r.loft("CocoonCoffin", [[(cc.x + x, cc.y + dy, cc.z + z) for x, z in outline] for dy in (0.08, -0.08)]),
            "Cocoon", "wood")
    for k in range(4):
        rig.add(a.ring_around(f"Silk{k}", cc + Vector((0, 0, -0.3 + 0.2 * k)), (0, 0.15, 1), 0.2 - 0.02 * (k % 2),
                              0.035, segments=8), "Cocoon", "silk")
    rig.add(a.crystal("CocoonSoul", cc + Vector((0, -0.1, 0.05)), 0.06, 0.25, sides=4), "Cocoon", "glow",
            glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(4):
            p = leg(k, s)
            bones = [f"Leg{k + 1}_{side}_{j + 1}" for j in range(3)]
            big = 1.0 if k in (0, 3) else 0.9
            rig.add(r.ico(f"Coxa{s}{k}", 0.13, subdivisions=1, location=p[0], scale=(1.3, 1, 0.9)), bones[0],
                    "bone_shade", **LEGS)
            rig.add(a.long_bone(f"Femur{s}{k}", p[0], p[1], 0.1 * big, segments=6), bones[0], "bone", **LEGS)
            rig.add(r.ico(f"Patella{s}{k}", 0.11 * big, subdivisions=1, location=p[1]), bones[1], "bone_shade",
                    **LEGS)
            rig.add(a.long_bone(f"Tibia{s}{k}", p[1], p[2], 0.08 * big, segments=6), bones[1], "bone", **LEGS)
            rig.add(a.long_bone(f"Tarsus{s}{k}", p[2], p[3] + Vector((0, 0, 0.08)), 0.055, condyles=False,
                                segments=5), bones[2], "bone", **LEGS)
            rig.add(a.claw(f"LegClaw{s}{k}", p[3] + Vector((0, 0, 0.08)), (p[3] - p[2]).normalized(), 0.16, 0.04,
                           curl=0.4, segments=4), bones[2], "horn", **LEGS)
            # Épines noires sur le fémur et le tibia
            for j, (a_pt, b_pt, bn) in enumerate(((p[0], p[1], bones[0]), (p[1], p[2], bones[1]))):
                q = a_pt.lerp(b_pt, 0.55)
                rig.add(a.claw(f"LegSpine{s}{k}{j}", q, Vector((0, 0, 1)) + (b_pt - a_pt).normalized() * 0.6, 0.18,
                               0.03, curl=0, segments=4), bn, "horn", **LEGS)
            rig.add(a.ring_around(f"LegBand{s}{k}", p[1].lerp(p[2], 0.2), p[2] - p[1], 0.1 * big, 0.025,
                                  segments=8), bones[1], "bone_shade", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_thorax(rig)
    build_mouth(rig)
    build_abdomen(rig)
    build_legs(rig)
    return rig
