"""Baudroie des abysses squelette (≈ 9 studs de long) — créature animable.
Pack « Abysses », créature 5.

Animal modèle : la baudroie abyssale (Melanocetus) — crâne large et plat, petits yeux sur le
dessus, gueule immense en prognathie (mâchoire du bas qui dépasse), forêt de longs crocs
vitreux recourbés vers l'intérieur, illicium (canne à pêche articulée) terminé par une esca
lumineuse, corps en boule, nageoires pectorales en « bras ».

Identité : os brun tourbe et crocs vitreux ; pas de cornes mais la **canne-appât** articulée
au-dessus de la tête et des épines sphénotiques ; silhouette en boule, tout en gueule ;
lueur citron vert, thème d'effets « lure » (points lumineux qui flottent) ; une proie
squelettique avalée brille dans le ventre.

5 pièces Roblox : corps, Head (crâne + mâchoires + canne), Teeth (crocs), Fins, + lumineux.
Os : Root, Body1-3, Tail, Head, Jaw, Lure1-3, PecFin_L/R, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#7d6a55",
    "bone_shade": "#4f4234",
    "tooth": "#f6f0dc",
    "horn": "#1d1612",
    "horn_tip": "#6f8f1a",
    "disc": "#3a2c22",
    "membrane": "#2b2420",
    "gum": "#4a1c2a",
    "ink": "#0e0b09",
    "glow": "#c6ff2e",
    "glow_hot": "#f4ffc0",
}

EFFECT_THEME = "lure"

TEST_POSE = {
    "Jaw": (18, 0, 0),
    "Lure2": (-20, 0, 0),
    "Lure3": (-25, 0, 0),
    "Tail": (0, 0, 25),
    "PecFin_L": (0, 30, 0),
}

VIEW = (1.0, -0.9, 0.35)

SPINE = a.smooth_path([(0, 0.3, 3.75), (0, 1.5, 3.65), (0, 3.0, 3.4), (0, 4.3, 3.2),
                       (0, 5.4, 3.15)], 30)
# Crâne de baudroie : large et plat, petits yeux sur le dessus
# (aussi large que la gueule et assez long pour venir se poser sur le prémaxillaire)
SKULL = [(0.4, 0.7, 1.0, 0.85, 4.25, 3.2), (-0.4, 1.0, 1.35, 1.15, 4.55, 3.3),
         (-1.3, 0.95, 1.3, 1.1, 4.45, 3.55), (-2.1, 0.7, 0.95, 0.8, 4.3, 3.85),
         (-2.6, 0.45, 0.62, 0.5, 4.2, 4.0)]
EYE = (-0.6, 4.15)
UPPER = (1.45, 2.2, 3.95, 3.0)      # (demi-largeur, longueur, z avant, z charnière)
LOWER = (1.62, 2.55, 2.05, 2.9)
Y_BACK = -0.8
LURE = a.smooth_path([(0, -1.35, 4.5), (0, -1.55, 5.4), (0, -2.25, 6.05), (0, -3.15, 6.15),
                      (0, -3.8, 5.65)], 13)
ESCA = Vector((0, -3.92, 5.3))
HEAD = dict(part="Head")
TEETH = dict(part="Teeth")
FINS = dict(part="Fins")


def arc(width, length, z_front, z_back, n=17):
    """Arc de mâchoire en U ; la ligne de gueule monte (haut) ou descend (bas) vers l'avant."""
    pts = []
    for i in range(n):
        th = -math.pi / 2 + math.pi * i / (n - 1)
        cth = math.cos(th)
        pts.append(Vector((width * math.sin(th) * (1 - 0.08 * cth), Y_BACK - length * cth,
                           z_back + (z_front - z_back) * cth ** 1.3)))
    return pts


def out_of(p, width, length):
    v = Vector((p.x / width ** 2, (p.y - Y_BACK) / length ** 2, 0))
    return v.normalized() if v.length > 1e-6 else Vector((0, -1, 0))


def front_of(p, length):
    return min(1.0, max(0.0, (Y_BACK - p.y) / length))


def body_bone(i):
    return f"Body{min(3, i * 3 // (len(SPINE) - 1) + 1)}" if i < len(SPINE) - 7 else "Tail"


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    n = len(SPINE) - 7
    for b in range(3):
        parent = rig.bone(f"Body{b + 1}", SPINE[b * n // 3], SPINE[(b + 1) * n // 3], parent)
    rig.bone("Tail", SPINE[n], SPINE[-1] + Vector((0, 1.2, 0.1)), "Body3")
    rig.bone("Head", SPINE[0], (0, -1.6, 4.0), "Body1")
    rig.bone("Jaw", (0, Y_BACK, 2.9), (0, -3.3, 2.05), "Head")
    parent = "Head"
    for k in range(3):
        parent = rig.bone(f"Lure{k + 1}", LURE[k * 4], LURE[min(12, k * 4 + 4)], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"PecFin_{side}", (s * 1.0, 0.9, 2.7), (s * 1.9, 0.9, 1.6), "Body1")
        rig.fx(f"Eye{side}", (s * 0.62, EYE[0], EYE[1]), "Head")
    rig.fx("Lure", ESCA, "Lure3")
    rig.fx("Belly", (0, 1.3, 2.4), "Body1")
    rig.fx("Mouth", (0, -1.6, 3.0), "Head")


# ---------------------------------------------------------------- crâne

def build_skull(rig):
    H = "Head"
    skull = a.loft_profile("Skull", SKULL, droop=0.12)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.2, 0.17), a.hole_x((0, 0.0, 3.65), 0.26, 0.2)]
          + [a.hole_along((sx * 0.36, -0.95, 4.35), (0, 0, 1), (1, 0, 0), 0.12, 0.2, depth=0.4)
             for sx in (-1, 1)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Crête médiane basse + crêtes frontales, écailles, pores, cicatrices
    crest = [top(0, y) for y in (0.3, -0.3, -0.9, -1.5)]
    rig.add(a.band("Crest", crest, [0.12, 0.2, 0.16, 0.08], 0.07, offset=0.3), H, "bone_shade",
            **HEAD)
    for s in (-1, 1):
        ridge = [top(s * 0.75, y) for y in (0.2, -0.4, -1.1, -1.8)]
        rig.add(r.tube(f"FrontalRidge{s}", [tuple(p) for p in ridge], [0.05, 0.07, 0.06, 0.04],
                       segments=5), H, "bone_shade", **HEAD)
        mr.scutes(rig, f"Scute{s}", [top(s * 0.25, y) + Vector((0, 0, 0.01))
                                     for y in (0.15, -0.45, -1.2)],
                  [Vector((s * 0.3, 0, 1))] * 3, H, size=0.08, **HEAD)
        rig.add(a.ring_around(f"FrontalWin{s}", top(s * 0.36, -0.95) or Vector((s * 0.36, -0.95, 4.4)),
                              (0, 0, 1), 0.17, 0.035, segments=10), H, "bone_shade", **HEAD)
        # Petits yeux sur le dessus, orbite hérissée + épines sphénotiques en arrière
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.12, subdivisions=2, location=(s * (x - 0.08), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, 0, 0.3), 0.2, H, spikes=5,
                       **HEAD)
        for k, (dy, ln) in enumerate(((-0.1, 0.55), (0.25, 0.42))):
            base = top(s * 0.7, EYE[0] + 0.35 + dy) or Vector((s * 0.7, -0.2, 4.3))
            rig.add(a.claw(f"Sphenotic{s}{k}", base, (s * 0.6, 0.8, 0.7), ln, 0.08, curl=-0.2,
                           segments=5), H, "horn", **HEAD)
        rig.add(a.ring_around(f"Temporal{s}", (s * a.side_width(SKULL, 0.0, 3.65), 0.0, 3.65),
                              (s, 0, 0), 0.26, 0.04, segments=12), H, "bone_shade", **HEAD)
        # Narines en rosette sur le museau
        nose = top(s * 0.32, -2.45) + Vector((0, -0.02, 0.03))
        rig.add(a.ring_around(f"Nostril{s}", nose, (s * 0.3, -1, 0.4), 0.08, 0.03, segments=8), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"NostrilHole{s}", 0.05, subdivisions=1, location=nose), H, "ink", **HEAD)
        for k in range(5):
            yy = -0.2 - 0.3 * k
            rig.add(r.ico(f"Pore{s}{k}", 0.035, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy, 3.75), yy, 3.75)), H, "ink",
                    **HEAD)
        mr.scar(rig, f"Scar{s}", top(s * 0.45, 0.25), top(s * 0.55, -0.4), H, width=0.05,
                seed=s + 2)
        # Préopercule à 3 épines, opercule en éventail strié, carré vers la charnière
        hinge = Vector((s * UPPER[0] * 1.05, Y_BACK, 2.92))
        pre = [Vector((s * 1.0, 0.3, 3.9)), Vector((s * 1.4, 0.05, 3.3)), hinge + Vector((0, 0.1, 0))]
        rig.add(r.tube(f"Preopercle{s}", [tuple(p) for p in pre], [0.08, 0.1, 0.09], segments=6),
                H, "bone", **HEAD)
        for k, t in enumerate((0.3, 0.55, 0.8)):
            q = mr.along(pre, t)
            rig.add(a.claw(f"PreSpine{s}{k}", q, (s * 0.7, 0.8, -0.2), 0.32 - 0.05 * k, 0.05,
                           curl=-0.1, segments=4), H, "horn", **HEAD)
        rig.add(a.blade(f"Opercle{s}", (s * 0.95, 0.45, 3.5), (s * 1.25, 1.2, 2.9), 0.6, 0.05,
                        width_end=0.4, mid=0.7, normal=(1, -0.3, 0)), H, "bone_shade", **HEAD)
        for k in range(4):
            rig.add(r.tube(f"OpercleRay{s}{k}", [(s * 1.0, 0.5, 3.45),
                                                 (s * 1.3, 1.25, 3.25 - 0.2 * k)],
                           [0.03, 0.015], segments=4), H, "bone", **HEAD)
        # Suspensorium : grande plaque hyomandibulaire du flanc du crâne à la charnière
        rig.add(a.blade(f"Hyomandibular{s}", (s * 1.12, -0.35, 3.55), hinge + Vector((0, 0.05, 0.05)),
                        0.5, 0.1, width_end=0.3, mid=0.5, normal=(1, 0, 0)), H, "bone", **HEAD)
        rig.add(r.tube(f"Quadrate{s}", [(s * 1.18, -0.75, 3.5), (s * 1.4, -0.8, 3.2),
                                        tuple(hinge)], [0.1, 0.09, 0.11], segments=6), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.17, subdivisions=1, location=hinge), H, "bone", **HEAD)
        # Rayons branchiostèges en éventail sous la gorge + arcs branchiaux lumineux
        for k in range(5):
            rig.add(r.tube(f"Branchiostegal{s}{k}", [(s * 0.25, -0.9, 2.55),
                                                     (s * (0.7 + 0.12 * k), -0.4 + 0.25 * k, 2.35),
                                                     (s * (1.0 + 0.1 * k), 0.2 + 0.3 * k, 2.6)],
                           [0.045, 0.04, 0.02], segments=4), H, "bone_shade", **HEAD)
        for g in range(3):
            yy = -0.6 + 0.3 * g
            garc = [(s * 0.35, yy, 3.4), (s * 0.95, yy, 3.0), (s * 0.9, yy, 2.55),
                    (s * 0.3, yy, 2.5)]
            rig.add(r.tube(f"GillArch{s}{g}", garc, 0.045, segments=4), H, "bone", **HEAD)
            for k in range(3):
                q = mr.along(garc, 0.25 + 0.25 * k)
                rig.add(a.claw(f"Raker{s}{g}{k}", q, (-s, -0.3, 0), 0.15, 0.025, curl=0,
                               segments=4), H, "tooth", **HEAD)
            rig.add(r.tube(f"GillGlow{s}{g}", [(s * 0.9, yy + 0.12, 3.0), (s * 0.86, yy + 0.12, 2.6)],
                           0.03, segments=4), H, "glow", glow=True)
    rig.add(a.blade("Hyoid", (0, -0.9, 2.5), (0, 0.3, 2.45), 0.3, 0.08, width_end=0.2,
                    normal=(0, 0, 1)), H, "bone_shade", **HEAD)
    rig.add(r.ico("Throat", 0.42, subdivisions=2, location=(0, -0.5, 3.0), scale=(1.5, 1, 0.9)),
            H, "glow", glow=True)
    # Canne-appât (illicium) articulée et esca lumineuse dans une cage d'os
    rig.add(a.blade("LureBase", top(0, -1.0) + Vector((0, 0, 0.02)), top(0, -1.5), 0.3, 0.1,
                    width_end=0.22, normal=(0, 0, 1)), H, "bone_shade", **HEAD)
    for k in range(3):
        seg = LURE[k * 4:k * 4 + 5]
        rig.add(r.tube(f"LureRod{k}", [tuple(p) for p in seg], [0.09 - 0.02 * k] * len(seg),
                       segments=6), f"Lure{k + 1}", "bone", **HEAD)
        rig.add(r.ico(f"LureJoint{k}", 0.13 - 0.025 * k, subdivisions=1, location=LURE[k * 4]),
                f"Lure{k + 1}", "bone_shade", **HEAD)
        for j in (1, 3):
            q = LURE[k * 4 + j]
            rig.add(a.ring_around(f"LureRing{k}{j}", q, LURE[k * 4 + j + 1] - q,
                                  0.1 - 0.02 * k, 0.025, segments=8), f"Lure{k + 1}", "horn",
                    **HEAD)
            rig.add(a.claw(f"LureBarb{k}{j}", q, (0, 0.5, 1) if k < 2 else (0, -0.3, 1), 0.15,
                           0.025, curl=0, segments=4), f"Lure{k + 1}", "horn", **HEAD)
    rig.add(r.tube("LureStem", [tuple(LURE[-1]), tuple(ESCA + Vector((0, 0, 0.28)))], 0.04,
                   segments=5), "Lure3", "bone", **HEAD)
    rig.add(r.ico("Esca", 0.27, subdivisions=2, location=ESCA, scale=(1, 1, 1.15)), "Lure3",
            "glow", glow=True)
    for k in range(4):
        ang = k * math.pi / 2 + 0.4
        side = Vector((math.cos(ang), math.sin(ang), 0))
        cage = [ESCA + Vector((0, 0, 0.32)), ESCA + side * 0.34 + Vector((0, 0, 0.05)),
                ESCA + side * 0.26 + Vector((0, 0, -0.25)), ESCA + Vector((0, 0, -0.36))]
        rig.add(r.tube(f"EscaCage{k}", [tuple(p) for p in cage], 0.028, segments=4), "Lure3",
                "horn", **HEAD)
    for k in range(3):
        fil = [ESCA + Vector((0.12 * (k - 1), 0, -0.35)),
               ESCA + Vector((0.2 * (k - 1), 0.05, -0.65)),
               ESCA + Vector((0.15 * (k - 1), -0.05, -0.95 - 0.1 * k))]
        rig.add(r.tube(f"EscaFilament{k}", [tuple(p) for p in fil], [0.025, 0.018, 0.012],
                       segments=4), "Lure3", "horn", **HEAD)
        rig.add(r.ico(f"EscaDrop{k}", 0.05, subdivisions=1, location=fil[-1]), "Lure3", "glow",
                glow=True)
    # Petits rayons-appâts secondaires sur la nuque
    for k, s in enumerate((-1, 1)):
        base = top(s * 0.25, 0.2)
        stub = [base, base + Vector((s * 0.1, 0.25, 0.5)), base + Vector((s * 0.2, 0.55, 0.75))]
        rig.add(r.tube(f"MinorLure{k}", [tuple(p) for p in stub], [0.05, 0.035, 0.02], segments=4),
                H, "bone", **HEAD)
        rig.add(r.ico(f"MinorLureGlow{k}", 0.07, subdivisions=1, location=stub[-1]), H, "glow",
                glow=True)


def build_jaws(rig):
    H, J = "Head", "Jaw"
    upper = arc(*UPPER)
    lower = arc(*LOWER, n=19)
    fu = [front_of(p, UPPER[1]) for p in upper]
    fl = [front_of(p, LOWER[1]) for p in lower]
    ou = [out_of(p, UPPER[0], UPPER[1]) for p in upper]
    ol = [out_of(p, LOWER[0], LOWER[1]) for p in lower]
    uh = [0.22 + 0.1 * (1 - f) for f in fu]
    lh = [0.3 + 0.18 * (1 - f) ** 1.5 + 0.1 * math.sin(math.pi * f) for f in fl]
    uu = [Vector((0, 0, 1)) - o * 0.3 for o in ou]
    lu = [Vector((0, 0, 1)) + o * 0.45 for o in ol]
    rig.add(a.band("Premaxilla", upper, uh, 0.16, up=uu, offset=0), H, "bone", **HEAD)
    rig.add(r.tube("PremaxRim", [tuple(p + u.normalized() * h) for p, u, h in zip(upper, uu, uh)],
                   0.045, segments=5), H, "bone_shade", **HEAD)
    # Apophyse montante : le prémaxillaire remonte vers le museau
    rig.add(r.tube("AscendingProcess", [tuple(upper[8] + Vector((0, 0.05, 0.2))),
                                        (0, -2.8, 4.3), (0, -2.45, 4.35)], [0.1, 0.09, 0.08],
                   segments=6), H, "bone_shade", **HEAD)
    # Joues : plaques sous-orbitaires ajourées qui soudent le prémaxillaire au crâne
    for s in (-1, 1):
        idx = list(range(9, 16)) if s > 0 else list(range(7, 0, -1))
        rim = [upper[i] + uu[i].normalized() * uh[i] - ou[i] * 0.05 for i in idx]
        heights = [max(0.12, a.width_at(SKULL, q.y, 5) + 0.15 - q.z) for q in rim]
        cheek = a.band(f"Cheek{s}", rim, heights, 0.1, offset=0)
        holes = []
        for k in (1, 3, 5):
            q = rim[k] + Vector((0, 0, heights[k] * 0.45))
            o = ou[idx[k]]
            holes.append(a.hole_along(q, o, Vector((0, 0, 1)).cross(o), 0.11,
                                      min(0.14, heights[k] * 0.3), depth=0.4))
        a.cut(cheek, holes)
        rig.add(cheek, H, "bone_shade", **HEAD)
        for k in (1, 3, 5):
            q = rim[k] + Vector((0, 0, heights[k] * 0.45))
            rig.add(a.ring_around(f"CheekWin{s}{k}", q + ou[idx[k]] * 0.06, ou[idx[k]], 0.13,
                                  0.03, segments=8), H, "bone", **HEAD)
        rig.add(r.tube(f"CheekRidge{s}", [tuple(q + Vector((0, 0, h * 0.85)) + ou[i] * 0.06)
                                          for q, h, i in zip(rim, heights, idx)], 0.04,
                       segments=4), H, "bone", **HEAD)
        for k in (0, 2, 4, 6):
            rig.add(a.claw(f"CheekSpine{s}{k}", rim[k] + Vector((0, 0, heights[k] * 0.8)) + ou[idx[k]] * 0.05,
                           ou[idx[k]] + Vector((0, 0.3, 0.2)), 0.18, 0.035, curl=0, segments=4), H,
                    "horn", **HEAD)
    rig.add(a.band("Dentary", lower, lh, [0.18 + 0.06 * (1 - f) for f in fl], up=lu, offset=1),
            J, "bone", **HEAD)
    bottom = [p - u.normalized() * h for p, u, h in zip(lower, lu, lh)]
    rig.add(r.tube("DentaryKeel", [tuple(q) for q in bottom], 0.06, segments=5), J, "bone_shade",
            **HEAD)
    rig.add(r.tube("DentaryRidge", [tuple(p + o * 0.15 - u.normalized() * h * 0.5)
                                    for p, o, u, h in zip(lower, ol, lu, lh)], 0.045, segments=4),
            J, "bone_shade", **HEAD)
    # Tendons (muscle adducteur) entre la joue et l'arrière du dentaire + rotule articulaire
    for s, ids in ((-1, (1, 2, 3)), (1, (17, 16, 15))):
        for k, i in enumerate(ids):
            top_pt = Vector((s * (1.3 - 0.08 * k), -0.95 - 0.3 * k, 3.35 - 0.05 * k))
            low_pt = lower[i] - lu[i].normalized() * lh[i] * 0.3 + ol[i] * 0.05
            rig.add(r.tube(f"Tendon{s}{k}", [tuple(top_pt), tuple(top_pt.lerp(low_pt, 0.5)
                                                                   + ol[i] * 0.06), tuple(low_pt)],
                           [0.05, 0.065, 0.05], segments=5), J, "gum", **HEAD)
        rig.add(r.ico(f"Articular{s}", 0.16, subdivisions=1,
                      location=lower[0 if s < 0 else 18] + Vector((0, 0.05, -0.05))), J,
                "bone_shade", **HEAD)
    chin = bottom[9]
    rig.add(r.ico("Symphysis", 0.16, subdivisions=1, location=chin + Vector((0, -0.05, 0.08)),
                  scale=(1.3, 1, 1)), J, "bone_shade", **HEAD)
    for k, s in enumerate((-1, 1)):
        rig.add(a.claw(f"ChinSpike{k}", chin + Vector((s * 0.15, -0.05, 0)), (s * 0.3, -0.6, -1),
                       0.32, 0.06, curl=0.1, segments=4), J, "horn", **HEAD)
    for i in range(1, 18, 2):
        rig.add(r.ico(f"JawPore{i}", 0.035, subdivisions=1,
                      location=lower[i] + ol[i] * 0.17 - lu[i].normalized() * lh[i] * 0.78), J,
                "ink", **HEAD)
        if i % 4 == 1:
            rig.add(r.ico(f"JawPhoto{i}", 0.04, subdivisions=1,
                          location=lower[i] + ol[i] * 0.16 - lu[i].normalized() * lh[i] * 0.25),
                    J, "glow", glow=True)
    for i in range(1, 16, 2):
        rig.add(r.ico(f"LipPore{i}", 0.03, subdivisions=1,
                      location=upper[i] + ou[i] * 0.12 + uu[i].normalized() * uh[i] * 0.5), H,
            "ink", **HEAD)
    rig.add(r.tube("UpperGum", [tuple(p - o * 0.1 + Vector((0, 0, 0.04))) for p, o in zip(upper, ou)],
                   0.08, segments=5), H, "gum", **HEAD)
    rig.add(r.tube("LowerGum", [tuple(p - o * 0.1 - Vector((0, 0, 0.04))) for p, o in zip(lower, ol)],
                   0.09, segments=5), J, "gum", **HEAD)
    # Forêt de longs crocs vitreux recourbés vers l'intérieur (2 rangées par mâchoire)
    for (dims, n_rows, down, bone, big) in ((UPPER, (17, 13), -1, H, 0.85),
                                            (LOWER, (19, 15), 1, J, 1.0)):
        w, l, zf, zb = dims
        for row, n in enumerate(n_rows):
            pts = arc(w - 0.16 * row, l - 0.2 * row, zf - down * 0.04 * row, zb - down * 0.04 * row,
                      n=n)
            for i in range(1, n - 1):
                p = pts[i]
                o = out_of(p, w - 0.16 * row, l - 0.2 * row)
                f = front_of(p, l - 0.2 * row)
                size = (0.35 + 0.5 * f * (1.0 if i % 2 else 0.6)) * big * (1 - 0.4 * row)
                width = size * 0.34
                tip = p + Vector((0, 0, down * size)) - o * size * (0.35 + 0.2 * row)
                rig.add(mr.tooth(f"Fang{bone}{row}{i}", p, tip, width, width * 0.6, o, curl=0.18),
                        bone, "tooth", **TEETH)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        p = SPINE[i]
        t = (SPINE[min(i + 1, n - 1)] - SPINE[max(i - 1, 0)]).normalized()
        size = 0.26 - 0.13 * i / (n - 1)
        rig.add(a.vertebra(f"Vert{i}", p, t, size, spine=1.7, lean=0.4), body_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", p.lerp(SPINE[i + 1], 0.5), t, size), body_bone(i), "disc")
    # Cage en boule : grandes côtes qui s'arrondissent sous le ventre
    for k in range(9):
        i = 1 + k * 2
        y = SPINE[i].y
        hw = 1.45 * math.sin(math.pi * (0.25 + 0.75 * (1 - k / 9))) * (1 - k / 14)
        depth = 2.15 - 0.17 * k
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], max(0.35, hw), depth, s, sweep=-0.2,
                          radius=0.08), body_bone(i), "bone")
            if k % 2 == 0:
                q = SPINE[i] + Vector((s * max(0.35, hw) * 0.95, 0.05, -depth * 0.45))
                rig.add(a.claw(f"RibSpike{k}{s}", q, (s, 0.3, 0.1), 0.24, 0.04, curl=0,
                               segments=4), body_bone(i), "horn")
    rig.add(r.tube("BellyKeel", [(0, 0.2, 1.65), (0, 1.3, 1.5), (0, 2.6, 1.75), (0, 3.6, 2.3)],
                   [0.07, 0.09, 0.07, 0.04], segments=5), "Body1", "bone_shade")
    # Ventre lumineux avec une proie squelettique avalée
    rig.add(r.ico("Stomach", 0.75, subdivisions=2, location=(0, 1.4, 2.45), scale=(1.1, 1.3, 0.9)),
            "Body1", "glow", glow=True)
    prey = [(0.1, 0.7, 2.5), (0.0, 1.4, 2.4), (-0.1, 2.1, 2.5)]
    rig.add(r.tube("PreySpine", prey, [0.05, 0.05, 0.03], segments=5), "Body1", "bone_shade")
    rig.add(r.ico("PreySkull", 0.16, subdivisions=1, location=(0.12, 0.55, 2.55),
                  scale=(1, 1.4, 0.9)), "Body1", "bone_shade")
    for k in range(5):
        y = 0.9 + 0.25 * k
        for s in (-1, 1):
            rig.add(r.tube(f"PreyRib{k}{s}", [(0, y, 2.43), (s * 0.18, y + 0.05, 2.33),
                                              (s * 0.12, y + 0.08, 2.18)], 0.02, segments=4),
                    "Body1", "bone_shade")
    # Épines dorsales basses entre crâne et nageoire dorsale
    for k in range(4):
        i = 2 + 2 * k
        rig.add(a.claw(f"DorsalSpike{k}", SPINE[i] + Vector((0, 0, 0.35)), (0, 0.6, 1),
                       0.35 - 0.04 * k, 0.05, curl=-0.1, segments=4), body_bone(i), "horn")


def build_fins(rig):
    n = len(SPINE)

    def top(i, h=0.4):
        return SPINE[i] + Vector((0, 0, h))

    mr.fin(rig, "Dorsal", [top(n - 12), top(n - 9), top(n - 7)],
           [top(n - 12) + Vector((0, 0.4, 0.9)), top(n - 10) + Vector((0, 0.6, 1.1)),
            top(n - 8) + Vector((0, 0.7, 0.8)), top(n - 7) + Vector((0, 0.5, 0.3))],
           "Body3", part="Fins", rays=6, seed=1)
    mr.fin(rig, "Anal", [top(n - 11, -0.3), top(n - 7, -0.3)],
           [top(n - 11, -0.3) + Vector((0, 0.5, -0.8)), top(n - 9, -0.3) + Vector((0, 0.6, -0.85)),
            top(n - 7, -0.3) + Vector((0, 0.4, -0.3))], "Body3", part="Fins", rays=5, seed=2)
    end = SPINE[-1]
    mr.fin(rig, "Caudal", [end + Vector((0, -0.1, 0.25)), end + Vector((0, 0.1, -0.25))],
           [end + Vector((0, 0.7, 1.0)), end + Vector((0, 1.3, 0.6)), end + Vector((0, 1.45, 0)),
            end + Vector((0, 1.3, -0.6)), end + Vector((0, 0.7, -1.0))], "Tail", part="Fins",
           rays=9, leading_spine=False, seed=4)
    for s, side in ((1, "L"), (-1, "R")):
        bone = f"PecFin_{side}"
        # Pectorale en « bras » : radial osseux puis éventail
        arm_a, arm_b = Vector((s * 1.0, 0.9, 2.7)), Vector((s * 1.75, 0.95, 1.75))
        rig.add(a.long_bone(f"PecArm{s}", arm_a, arm_b, 0.1, knob=1.4, segments=6,
                            condyles=False), bone, "bone", **FINS)
        mr.fin(rig, f"Pec{s}", [arm_b + Vector((0, -0.2, 0.1)), arm_b + Vector((0, 0.25, -0.05))],
               [arm_b + Vector((s * 0.5, -0.5, -0.4)), arm_b + Vector((s * 0.85, -0.05, -0.7)),
                arm_b + Vector((s * 0.7, 0.5, -0.65)), arm_b + Vector((s * 0.3, 0.6, -0.35))],
               bone, part="Fins", rays=6, leading_spine=False, seed=5 + s)
        # Pelviennes sous la gorge
        pa = Vector((s * 0.3, -0.2, 2.0))
        mr.fin(rig, f"Pelvic{s}", [pa, pa + Vector((0, 0.3, 0))],
               [pa + Vector((s * 0.3, 0.1, -0.5)), pa + Vector((s * 0.2, 0.55, -0.45))], "Body1",
               part="Fins", rays=3, tattered=False, glow_tips=False, seed=8)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_skull(rig)
    build_jaws(rig)
    build_body(rig)
    build_fins(rig)
    return rig
