"""Mammouth squelette (≈ 6 studs au garrot, 8 de long) — créature animable.
Pack « Royaume de glace éternelle », créature 1.

Animal modèle : le mammouth laineux — crâne en dôme très haut, grande ouverture nasale au
milieu de la face (départ de la trompe), énormes fourreaux de défenses qui descendent,
petites orbites sur les côtés, mandibule courte à molaires en lamelles ; dos en pente (garrot
haut, hanches basses), pattes en colonnes.

Identité : os ivoire ancien envahis de givre, stalactites qui pendent sous les côtes, la
mâchoire et les défenses ; **défenses spirales en glace** ; trompe en anneaux d'os autour
d'un cœur lumineux ; bosse de garrot en hautes épines ; cœur-aurore dans la cage ; thème
d'effets « aurora » (voiles d'aurore + neige).

4 pièces Roblox : corps, Head (crâne + mâchoire + trompe), Tusks, Legs, + lumineux.
Os : Root, Spine1-3, Neck, Head, Jaw, Trunk1-3, Tail, Front/Hind{Upper,Lower,Foot}_{L,R}, FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#cdb894",
    "bone_shade": "#7d6a52",
    "tooth": "#efe6d2",
    "horn": "#2b2a30",
    "horn_tip": "#5dffa8",
    "disc": "#4a3c2e",
    "ice": "#bfe6ff",
    "ice_deep": "#6fb3e0",
    "gum": "#5a2a2a",
    "ink": "#0c0d10",
    "glow": "#5dffa8",
    "glow_hot": "#e0fff0",
}

EFFECT_THEME = "aurora"

TEST_POSE = {
    "Jaw": (18, 0, 0),
    "Trunk2": (-30, 0, 0),
    "Trunk3": (-35, 0, 0),
    "FrontUpper_L": (-30, 0, 0),
    "Head": (-12, 0, 0),
}

VIEW = (0.9, -1.0, 0.35)

SPINE = a.smooth_path([(0, 2.7, 4.2), (0, 1.5, 4.6), (0, 0.2, 5.2), (0, -0.7, 5.55),
                       (0, -1.35, 5.2)], 22)
TAIL = a.smooth_path([(0, 2.75, 4.15), (0, 3.15, 3.6), (0, 3.3, 2.9)], 11)
# Crâne en dôme : (y, demi-larg. dessus, joues, bas, z dessus, z bas) — face haute et verticale
SKULL = [(-1.3, 0.55, 0.75, 0.6, 6.0, 4.6), (-1.7, 0.7, 0.86, 0.7, 6.45, 4.2),
         (-2.1, 0.66, 0.82, 0.7, 6.35, 3.9), (-2.45, 0.5, 0.66, 0.6, 5.95, 3.75),
         (-2.62, 0.38, 0.52, 0.5, 5.5, 3.72)]
EYE = (-2.0, 5.15)
# Alvéoles des sinus du dôme, traversantes : (y, z, demi-axe y, demi-axe z)
CELLS = [(-1.5, 5.75, 0.17, 0.24), (-1.9, 5.95, 0.15, 0.2), (-1.55, 5.2, 0.12, 0.14),
         (-2.25, 5.75, 0.1, 0.16), (-1.85, 5.5, 0.08, 0.1)]
NASAL = Vector((0, -2.62, 5.25))
TRUNK = a.smooth_path([(0, -2.72, 5.15), (0, -3.0, 4.4), (0, -3.12, 3.5), (0, -3.05, 2.6),
                       (0, -3.3, 1.9), (0, -3.75, 1.7)], 22)
HEAD = dict(part="Head")
TUSKS = dict(part="Tusks")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    if i >= len(SPINE) - 4:
        return "Neck"
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // (len(SPINE) - 4))]


def tusk_path(s):
    return a.smooth_path([(s * 0.42, -2.62, 3.85), (s * 0.75, -3.25, 3.05), (s * 1.3, -4.0, 2.95),
                          (s * 1.62, -4.5, 3.75), (s * 1.3, -4.6, 4.65), (s * 0.75, -4.25, 5.0)], 14)


def front_leg(s):
    return (Vector((s * 0.95, -0.9, 4.6)), Vector((s * 1.02, -0.8, 2.6)),
            Vector((s * 1.02, -0.95, 0.9)), Vector((s * 1.02, -1.05, 0.2)))


def hind_leg(s):
    return (Vector((s * 0.8, 2.3, 3.9)), Vector((s * 0.88, 1.85, 2.2)),
            Vector((s * 0.88, 2.2, 0.9)), Vector((s * 0.88, 2.1, 0.2)))


def icicle(rig, name, base, length, bone, **kw):
    """Stalactite de glace qui pend (deux tons)."""
    base = Vector(base)
    rig.add(a.claw(name, base, (0, 0, -1), length, length * 0.18, curl=0, segments=5), bone,
            "ice", **kw)


def frost(rig, name, center, up, bone, n=4, size=0.25, **kw):
    """Grappe de cristaux de givre."""
    up = Vector(up).normalized()
    side, fwd = a._basis(up)
    for k in range(n):
        ang = 2 * math.pi * k / n
        d = up + (side * math.cos(ang) + fwd * math.sin(ang)) * (0.0 if k == 0 else 0.6)
        crystal = a.crystal(f"{name}{k}", (0, 0, 0), size * (0.35 if k == 0 else 0.25),
                            size * (2.2 if k == 0 else 1.4), sides=6)
        a.oriented(crystal, Vector(center), d)
        rig.add(crystal, bone, "ice" if k % 2 == 0 else "ice_deep", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    n = len(SPINE) - 4
    rig.bone("Spine1", SPINE[0], SPINE[n // 3], "Root")
    rig.bone("Spine2", SPINE[n // 3], SPINE[2 * n // 3], "Spine1")
    rig.bone("Spine3", SPINE[2 * n // 3], SPINE[n], "Spine2")
    rig.bone("Neck", SPINE[n], SPINE[-1], "Spine3")
    rig.bone("Head", SPINE[-1], (0, -2.65, 5.0), "Neck")
    rig.bone("Jaw", (0, -1.75, 4.05), (0, -2.3, 3.4), "Head")
    parent = "Head"
    for k in range(3):
        parent = rig.bone(f"Trunk{k + 1}", TRUNK[k * 7], TRUNK[min(21, k * 7 + 7)], parent)
    rig.bone("Tail", TAIL[0], TAIL[-1], "Spine1")
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Spine3"), ("Hind", hind_leg(s), "Spine1")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Foot_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
        rig.fx(f"Eye{side}", (s * 0.8, EYE[0], EYE[1]), "Head")
        rig.fx(f"TuskTip{side}", tusk_path(s)[-1], "Head")
    rig.fx("Heart", (0, -0.3, 4.0), "Spine3")
    rig.fx("Trunk", TRUNK[-1], "Trunk3")
    rig.fx("Hump", SPINE[14] + Vector((0, 0, 1.3)), "Spine3")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.05, tip_length=0.15)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_along(NASAL, (0, 1, 0), (1, 0, 0), 0.3, 0.24, depth=0.45),
                  a.hole_x((0, EYE[0], EYE[1]), 0.15, 0.14),
                  a.hole_x((0, -1.6, 4.85), 0.24, 0.2)]
          + [a.hole_x((0, y, z), ry, rz) for y, z, ry, rz in CELLS]
          + [a.hole_along((sx * 0.3, -1.75, 6.3), (0, 0, 1), (1, 0, 0), 0.1, 0.18, depth=0.3)
             for sx in (-1, 1)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Rebord de l'ouverture nasale, crête du dôme, sinus frontaux, cristaux de givre au sommet
    rig.add(a.ring_around("NasalRim", NASAL + Vector((0, -0.05, 0)), (0, -1, 0.1), 0.32, 0.06,
                          segments=14), H, "bone_shade", **HEAD)
    rig.add(r.tube("DomeCrest", [tuple(top(0, y) + Vector((0, 0, 0.02))) for y in
                                 (-1.35, -1.7, -2.05, -2.35)], [0.05, 0.08, 0.07, 0.05],
                   segments=5), H, "bone_shade", **HEAD)
    frost(rig, "DomeFrost", top(0.15, -1.75), (0.2, 0.2, 1), H, n=5, size=0.3, **HEAD)
    # Rebords des alvéoles (des deux côtés), cloisons visibles au travers
    for s in (-1, 1):
        for k, (y, z, ry, rz) in enumerate(CELLS):
            x = a.side_width(SKULL, y, z)
            ring = [(s * x * (1.0 - 0.05 * abs(math.sin(t))), y + ry * 1.12 * math.cos(t),
                     z + rz * 1.12 * math.sin(t)) for t in (2 * math.pi * j / 10 for j in range(10))]
            rig.add(r.tube(f"CellRim{s}{k}", ring, 0.035, segments=4, closed=True), H, "bone_shade",
                    **HEAD)
    for k, (y0, z0, y1, z1) in enumerate(((-1.5, 5.45, -1.9, 5.7), (-1.7, 6.2, -1.6, 5.3))):
        rig.add(r.tube(f"Septum{k}", [(0, y0, z0), (0, y1, z1)], 0.05, segments=5), H, "bone",
                **HEAD)
    # Crêtes de la face : du front vers les fourreaux des défenses
    for s in (-1, 1):
        ridge = [top(s * 0.42, -2.0), top(s * 0.4, -2.35)]
        if all(p is not None for p in ridge):
            rig.add(r.tube(f"FaceRidge{s}", [tuple(ridge[0]), tuple(ridge[1]),
                                             (s * 0.38, -2.55, 4.9), (s * 0.34, -2.45, 4.55)],
                           [0.05, 0.06, 0.06, 0.05], segments=4), H, "bone_shade", **HEAD)
        for k in range(4):
            rig.add(r.ico(f"FacePore{s}{k}", 0.035, subdivisions=1,
                          location=(s * (0.22 + 0.06 * k), -2.6 + 0.02 * k, 4.75 - 0.1 * k)), H,
                    "ink", **HEAD)
        mr.scar(rig, f"DomeCrack{s}", top(s * 0.2, -1.4), top(s * 0.12, -1.95), H, width=0.05,
                seed=s + 4)
    for s in (-1, 1):
        rig.add(a.ring_around(f"SinusRim{s}", top(s * 0.3, -1.75), (0, 0, 1), 0.13, 0.03,
                              segments=8), H, "bone_shade", **HEAD)
        # Petites orbites sur les côtés, œil d'aurore, arcade givrée
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=c0 - Vector((s * 0.07, 0, 0))), H,
                "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", c0, (s, -0.2, 0), 0.16, H, spikes=5, color="ice", **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.5, -2.3, 5.55), (s * 0.85, -1.8, 5.5), 0.18, 0.09,
                        width_end=0.12, normal=(0, -0.2, 1)), H, "bone_shade", **HEAD)
        # Fourreaux des défenses (alvéoles) qui descendent, bague de glace au bout
        sock = [(s * 0.32, -2.3, 4.7), (s * 0.38, -2.5, 4.25), (s * 0.42, -2.62, 3.85)]
        rig.add(r.tube(f"TuskSocket{s}", sock, [0.26, 0.3, 0.33], segments=10), H, "bone", **HEAD)
        rig.add(a.ring_around(f"SocketRim{s}", Vector(sock[-1]), Vector(sock[-1]) - Vector(sock[1]),
                              0.34, 0.05, segments=12), H, "bone_shade", **HEAD)
        for k in range(3):
            icicle(rig, f"SocketIcicle{s}{k}", Vector(sock[-1]) + Vector((s * (0.15 - 0.15 * k),
                                                                          -0.1 * k, -0.25)),
                   0.3 + 0.1 * (k % 2), H, **HEAD)
        # Défense spirale en glace : corne annelée + hélice de givre + stalactites
        tp = tusk_path(s)
        rig.add(a.ridged_horn(f"Tusk{s}", [tuple(p) for p in tp], 0.27, ridges=10, depth=0.3), H,
                "ice", **TUSKS)
        for k in (3, 7, 10):   # grappes de givre sur le dessus de la défense
            side, up = a._basis(tangent(tp, k))
            frost(rig, f"TuskFrost{s}{k}", tp[k] + Vector((0, 0, 0.27 * (1 - k / 14) ** 0.9)),
                  (s * 0.3, 0, 1), H, n=3, size=0.14, **TUSKS)
        helix = []
        for k, p in enumerate(tp[:-2]):
            t = tangent(tp, k)
            side, up = a._basis(t)
            rad = 0.27 * (1 - k / len(tp)) ** 0.9 + 0.02
            ang = k * 0.9
            helix.append(p + (side * math.cos(ang) + up * math.sin(ang)) * rad)
        rig.add(r.tube(f"TuskHelix{s}", [tuple(p) for p in helix], 0.03, segments=4), H,
                "ice_deep", **TUSKS)
        for k in (2, 4, 6):
            icicle(rig, f"TuskIcicle{s}{k}", tp[k] - Vector((0, 0, 0.2 * (1 - k / 14))),
                   0.35 - 0.03 * k, H, **TUSKS)
        rig.add(r.ico(f"TuskGlow{s}", 0.06, subdivisions=1, location=tp[-1]), H, "glow", glow=True)
        # Pommette, fissures givrées, pores
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.62, -1.4, 4.6), (s * 0.8, -1.8, 4.55),
                                         (s * 0.66, -2.25, 4.5)], [0.08, 0.09, 0.07], segments=5),
                H, "bone", **HEAD)
        mr.scar(rig, f"FrostCrack{s}", top(s * 0.45, -1.45), top(s * 0.55, -2.1), H, width=0.06,
                seed=s)
    # Mandibule courte et profonde, molaires en lamelles, bec du menton
    for s in (-1, 1):
        line = [Vector((s * 0.55, -1.7, 4.1)), Vector((s * 0.5, -2.0, 3.85)),
                Vector((s * 0.3, -2.25, 3.65)), Vector((s * 0.08, -2.4, 3.5))]
        rig.add(a.band(f"Mandible{s}", line, [0.6, 0.55, 0.45, 0.32], [0.16, 0.15, 0.13, 0.11],
                       up=[Vector((s * 0.3, 0, 1))] * 4, offset=1), J, "bone", **HEAD)
        rig.add(a.blade(f"Ramus{s}", line[0] + Vector((0, 0.05, -0.1)), (s * 0.6, -1.5, 4.7), 0.4,
                        0.12, width_end=0.22, normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Condyle{s}", 0.13, subdivisions=1, location=(s * 0.6, -1.5, 4.72)), H,
                "bone_shade", **HEAD)
        rig.add(r.tube(f"MandibleBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in
                                            zip(line, (0.6, 0.55, 0.45, 0.32))], 0.06,
                       segments=5), J, "bone_shade", **HEAD)
        # Molaires : blocs de lamelles d'émail (haut et bas)
        for row, (z0, d, bone) in enumerate(((4.12, 1, J), (4.38, -1, H))):
            for k in range(6):
                y = -1.72 - 0.08 * k
                x = s * (0.42 - 0.02 * k)
                rig.add(a.blade(f"Lamella{row}{s}{k}", (x - s * 0.08, y, z0), (x + s * 0.08, y, z0),
                                0.12, 0.05, width_end=0.12, normal=(0, 1, 0), bevel=0),
                        bone, "tooth", **HEAD)
            rig.add(mr.tooth(f"Premolar{row}{s}", (s * 0.33, -2.25, z0 if row else 3.7),
                             (s * 0.33, -2.3, (z0 if row else 3.7) + d * 0.2), 0.12, 0.07,
                             Vector((s, -0.3, 0))), bone, "tooth", **HEAD)
        rig.add(r.tube(f"Gum{s}", [(s * 0.42, -1.65, 4.08), (s * 0.36, -2.1, 3.75)], 0.05,
                       segments=4), J, "gum", **HEAD)
    rig.add(a.claw("ChinSpout", (0, -2.4, 3.2), (0, -0.6, -1), 0.3, 0.1, curl=0.3, segments=5), J,
            "bone_shade", **HEAD)
    for k, x in enumerate((-0.3, -0.1, 0.1, 0.3)):
        icicle(rig, f"JawIcicle{k}", (x * 0.8, -2.2 + abs(x), 3.2 + abs(x)), 0.3 + 0.08 * (k % 2), J,
               **HEAD)
    rig.add(r.ico("Throat", 0.22, subdivisions=2, location=(0, -1.9, 4.2), scale=(1.4, 1.2, 0.6)),
            H, "glow", glow=True)
    # Trompe en anneaux d'os autour d'un cœur lumineux
    nt = len(TRUNK)
    rig.add(r.tube("TrunkCore", [tuple(p) for p in TRUNK], [0.12 - 0.004 * i for i in range(nt)],
                   segments=5), "Trunk1", "glow", glow=True)
    for i, p in enumerate(TRUNK):
        t = tangent(TRUNK, i)
        rad = 0.3 - 0.01 * i
        side, up = a._basis(t)
        bone = f"Trunk{min(3, i // 7 + 1)}"
        rig.add(a.ring_around(f"TrunkRing{i}", p, t, rad, 0.055 - 0.0015 * i, segments=10), bone,
                "bone" if i % 2 == 0 else "bone_shade", **HEAD)
        if i % 3 == 1:
            rig.add(a.claw(f"TrunkSpike{i}", p + side * rad, side - t * 0.3, 0.16, 0.03, curl=0,
                           segments=4), bone, "ice", **HEAD)
            rig.add(a.claw(f"TrunkSpikeB{i}", p - side * rad, -side - t * 0.3, 0.16, 0.03, curl=0,
                           segments=4), bone, "ice", **HEAD)
    # Deux tiges de cartilage qui relient les anneaux (dessus et dessous de la trompe)
    for sgn, name in ((1, "TrunkBarTop"), (-1, "TrunkBarLow")):
        pts = []
        for i, p in enumerate(TRUNK):
            side, up = a._basis(tangent(TRUNK, i))
            pts.append(p + up * sgn * (0.3 - 0.01 * i))
        rig.add(r.tube(name, [tuple(q) for q in pts], [0.04 - 0.001 * i for i in range(nt)],
                       segments=4), "Trunk2", "bone_shade", **HEAD)
    for k in range(3):
        icicle(rig, f"TrunkTip{k}", TRUNK[-1] + Vector((0.08 * (k - 1), -0.05, -0.05)), 0.25, "Trunk3",
               **HEAD)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        hump = 10 <= i <= 17
        size = 0.32 if i < n - 4 else 0.27
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, size, spine=3.2 if hump else 1.3,
                           lean=0.55 if hump else 0.4), spine_bone(i), "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, size), spine_bone(i),
                    "disc")
        if hump and i % 2 == 0:
            side, up = a._basis(t)
            frost(rig, f"HumpFrost{i}", SPINE[i] + up * (size * 3.4) - t * 0.4, up, spine_bone(i),
                  n=3, size=0.18)
    # Grande cage thoracique, givre et stalactites sous les côtes
    sternum = []
    for k, i in enumerate(range(4, 17)):
        hw = 0.95 + 0.3 * math.sin(math.pi * k / 12)
        depth = 1.5 + 0.6 * math.sin(math.pi * (k + 2) / 15)
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.09),
                    spine_bone(i), "bone")
            if k % 2 == 0:
                tip = SPINE[i] + Vector((s * (0.12 + hw * math.sin(math.pi * 0.95) * 0.75), -0.2,
                                         -depth * 0.99))
                low = SPINE[i] + Vector((s * (0.12 + hw * 0.8), -0.1, -depth * 0.55))
                icicle(rig, f"RibIcicle{k}{s}", low, 0.45 + 0.1 * (k % 3), spine_bone(i))
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[2:-1:2], 0.12, 0.6, offset=0.5), "Spine2", "bone_shade")
    for k, p in enumerate(sternum[3:-1:3]):
        icicle(rig, f"SternumIcicle{k}", p - Vector((0, 0, 0.08)), 0.5, "Spine2")
    # Cœur-aurore : cristaux lumineux dans la cage
    for k, (dx, dy, h) in enumerate(((0, -0.3, 1.0), (0.25, -0.1, 0.7), (-0.25, -0.5, 0.75),
                                     (0.1, 0.2, 0.6), (-0.15, 0.1, 0.55))):
        rig.add(a.crystal(f"AuroraHeart{k}", (dx, dy, 3.55), 0.14 if k == 0 else 0.1, h, sides=6),
                "Spine3", "glow", glow=True)
    # Omoplates, bassin, queue
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[13] + Vector((s * 0.35, 0, 0.1)),
                        sh + Vector((0, 0.05, 0.05)), 0.8, 0.1, width_end=0.4, mid=0.85,
                        normal=(s, 0, 0.4)), "Spine3", "bone")
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[2] + Vector((s * 0.2, 0, 0.1)),
                        hp + Vector((s * 0.35, -0.3, 0.55)), 0.75, 0.1, width_end=0.55, mid=0.85,
                        normal=(s, 0, 0.4)), "Spine1", "bone")
        rig.add(r.tube(f"Pubis{s}", [tuple(hp), (s * 0.35, 2.0, 3.3), (0, 2.05, 3.25)], 0.09,
                       segments=5), "Spine1", "bone")
        frost(rig, f"ShoulderFrost{s}", sh + Vector((s * 0.1, 0.1, 0.25)), (s * 0.4, 0, 1), "Spine3",
              n=4, size=0.22)
    for i in range(len(TAIL)):
        t = tangent(TAIL, i)
        size = 0.16 - 0.008 * i
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=0.8, transverse=False), "Tail",
                "bone")
        if i < len(TAIL) - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), "Tail", "disc")
    for k in range(3):
        icicle(rig, f"TailIcicle{k}", TAIL[-1] + Vector((0.06 * (k - 1), 0.03, -0.05)), 0.3, "Tail")


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts in (("Front", front_leg(s)), ("Hind", hind_leg(s))):
            ub, lb, fb = f"{prefix}Upper_{side}", f"{prefix}Lower_{side}", f"{prefix}Foot_{side}"
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.22, segments=8), ub, "bone",
                    **LEGS)
            off = Vector((s * 0.1, 0, 0))
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1] + off * 0.3, pts[2] + off * 0.3, 0.18,
                                segments=8), lb, "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] - off, pts[2] - off, 0.08,
                                condyles=False, segments=6), lb, "bone_shade", **LEGS)
            rig.add(a.ring_around(f"{prefix}Knee{s}", pts[1], pts[2] - pts[1], 0.25, 0.04,
                                  segments=10), lb, "glow", glow=True)
            # Pied en colonne : carpe, 5 doigts courts en couronne, ongles sombres, semelle
            rig.add(r.ico(f"{prefix}Carpus{s}", 0.24, subdivisions=1, location=pts[2],
                          scale=(1, 1, 0.8)), fb, "bone_shade", **LEGS)
            for j in range(5):
                ang = math.radians(-80 + 160 * j / 4)
                d = Vector((s * math.sin(ang) * 0.6, -math.cos(ang), 0)).normalized()
                base = pts[2] + d * 0.12 + Vector((0, 0, -0.1))
                toe = pts[3] + d * 0.3
                rig.add(a.long_bone(f"{prefix}Toe{s}{j}", base, toe, 0.06, condyles=False,
                                    segments=5), fb, "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Nail{s}{j}", toe, d + Vector((0, 0, -0.5)), 0.12, 0.06,
                               curl=0, segments=4), fb, "horn", **LEGS)
            rig.add(r.cylinder(f"{prefix}Sole{s}", 0.38, 0.06, segments=12,
                               location=(pts[3].x, pts[3].y, 0.05)), fb, "ice_deep", **LEGS)
            frost(rig, f"{prefix}KneeFrost{s}", pts[1] + Vector((0, -0.2, 0.1)), (0, -1, 0.5), lb,
                  n=3, size=0.15, **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
