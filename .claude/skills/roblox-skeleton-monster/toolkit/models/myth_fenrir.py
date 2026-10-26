"""Fenrir squelette (loup colossal, ≈ 6 studs au garrot, 11 de long) — animable.
Pack « Mythologie », créature 2 (mythe nordique).

Animal modèle : le **loup gris** — crâne long à forte crête sagittale, arcades zygomatiques
très écartées, orbites en avant, carnassières et canines énormes ; ici exagéré en colosse.
Très différent du loup-garou (bipède voûté) et de Cerbère (3 têtes, feu) : **colosse de
14 studs**, un seul crâne énorme à collerette de piques, gueule béante.

Identité : os gris pierre gravés de **runes** lumineuses ; **aucune corne** : crinière de
piques d'os hérissées sur la nuque et le dos ; quadrupède arc-bouté, tête basse qui tire sur
ses liens ; **Gleipnir brisé** : fragments de ruban magique lumineux déchirés qui pendent du
collier runique et des entraves ; flammes de givre aux yeux ; thème d'effets « ragnarok ».

Pièces Roblox : corps, Head, Legs, Tail, + lumineux.
Os : Root, Hips, Chest, Neck1-2, Head, Jaw, Tail1-3, {Front,Hind}{Upper,Lower,Foot}_{L,R}.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#b3aea6",
    "bone_shade": "#4a4c55",
    "tooth": "#f5efe0",
    "horn": "#15161a",
    "disc": "#2c2e35",
    "iron": "#585b63",
    "steel": "#a9b3c0",
    "leather": "#4a3424",
    "stone": "#6f6c68",
    "gum": "#5a2028",
    "ink": "#08090b",
    "glow": "#9fd4ff",
    "glow_hot": "#eef8ff",
}

EFFECT_THEME = "ragnarok"

TEST_POSE = {
    "Jaw": (10, 0, 0),
    "Neck2": (15, 0, 10),
    "FrontUpper_L": (-30, 0, 0),
    "HindUpper_R": (25, 0, 0),
    "Tail2": (0, 0, 30),
}

VIEW = (1.0, -0.8, 0.35)

SPINE = a.smooth_path([(0, 2.7, 4.3), (0, 1.2, 4.55), (0, -0.2, 4.85), (0, -1.2, 5.05)], 18)
NECK = a.smooth_path([(0, -1.2, 5.05), (0, -1.95, 5.3), (0, -2.55, 5.25), (0, -2.95, 5.0)], 9)
TAIL = a.smooth_path([(0, 2.75, 4.25), (0, 3.6, 3.9), (0, 4.4, 3.0), (0, 4.9, 2.2), (0, 5.4, 1.7)], 16)
# Crâne de loup dans son repère (occiput en 0, museau vers -Y)
SKULL = [(0.0, 0.35, 0.42, 0.3, 0.42, -0.25), (-0.4, 0.5, 0.6, 0.4, 0.5, -0.35),
         (-0.8, 0.45, 0.62, 0.42, 0.44, -0.42), (-1.3, 0.3, 0.42, 0.35, 0.26, -0.45),
         (-1.9, 0.22, 0.31, 0.27, 0.13, -0.42), (-2.5, 0.18, 0.24, 0.22, 0.03, -0.38),
         (-2.75, 0.15, 0.2, 0.18, -0.03, -0.34)]
EYE = (-0.88, 0.18)
HINGE = (0.42, -0.35, -0.35)
GAPE = math.radians(42)
_jm = (Matrix.Translation((0, HINGE[1], HINGE[2])) @ Matrix.Rotation(GAPE, 4, "X")
       @ Matrix.Translation((0, -HINGE[1], -HINGE[2])))
HEAD_M = (Matrix.Translation(NECK[-1] + Vector((0, 0.15, 0.15))) @ Matrix.Rotation(math.radians(5), 4, "X")
          @ Matrix.Diagonal((1.4, 1.08, 1.55, 1.0)))   # museau de loup : plus court et plus haut
SCALE = 1.3          # tout le modèle est agrandi à la fin (colosse)
HEAD = dict(part="Head")
LEGS = dict(part="Legs")
TAILP = dict(part="Tail")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def leg(prefix, s):
    if prefix == "Front":     # pattes avant arc-boutées vers l'avant
        return (Vector((s * 0.75, -1.25, 4.4)), Vector((s * 0.88, -0.8, 2.75)),
                Vector((s * 0.85, -1.6, 1.0)), Vector((s * 0.88, -1.95, 0.14)))
    return (Vector((s * 0.68, 2.55, 4.05)), Vector((s * 0.9, 1.75, 2.65)),
            Vector((s * 0.85, 3.0, 1.3)), Vector((s * 0.88, 2.75, 0.14)))


def rune(rig, name, center, normal, bone, size=0.12, **kw):
    """Rune nordique lumineuse gravée : hampe + deux branches (ᚠ / ᚨ)."""
    center, normal = Vector(center), Vector(normal).normalized()
    side, up = a._basis(normal)
    for k, (off, d, ln) in enumerate(((Vector(), up, 1.0), (up * 0.25, up + side, 0.5),
                                      (-up * 0.05, up + side, 0.5))):
        bar = r.box(f"{name}{k}", (size * 0.16, size * 0.05, size * ln))
        a.oriented(bar, center + off * size + d.normalized() * size * ln * 0.5 * (k > 0), normal)
        rig.add(bar, bone, "glow", glow=True)


def ribbon(rig, name, points, bone, radius=0.035, **kw):
    """Gleipnir : ruban torsadé (deux brins lumineux enroulés + âme d'acier)."""
    pts = [Vector(p) for p in points]
    for k in range(2):
        strand = []
        for i, p in enumerate(pts):
            t = tangent(pts, i)
            side, up = a._basis(t)
            ang = i * 1.3 + k * math.pi
            strand.append(tuple(p + (side * math.cos(ang) + up * math.sin(ang)) * radius * 1.4))
        rig.add(r.tube(f"{name}Strand{k}", strand, radius * 0.6, segments=4), bone, "glow", glow=True)
    rig.add(r.tube(f"{name}Core", [tuple(p) for p in pts], radius * 0.7, segments=4), bone, "steel", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", SPINE[0], SPINE[9], "Root")
    rig.bone("Chest", SPINE[9], SPINE[-1], "Hips")
    rig.bone("Neck1", NECK[0], NECK[4], "Chest")
    rig.bone("Neck2", NECK[4], NECK[-1], "Neck1")
    rig.bone("Head", NECK[-1], HEAD_M @ Vector((0, -2.75, 0.0)), "Neck2")
    rig.bone("Jaw", HEAD_M @ Vector(HINGE), HEAD_M @ (_jm @ Vector((0, -2.7, -0.55))), "Head")
    n = len(TAIL) - 1
    parent = "Hips"
    for k in range(3):
        parent = rig.bone(f"Tail{k + 1}", TAIL[k * n // 3], TAIL[(k + 1) * n // 3], parent)
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, parent in (("Front", "Chest"), ("Hind", "Hips")):
            p = leg(prefix, s)
            prev = parent
            for k, nm in enumerate(("Upper", "Lower", "Foot")):
                prev = rig.bone(f"{prefix}{nm}_{side}", p[k], p[k + 1], prev)
        rig.fx(f"Eye{side}", HEAD_M @ Vector((s * 0.35, EYE[0], EYE[1])), "Head")
    rig.fx("Maw", HEAD_M @ Vector((0, -1.5, -0.5)), "Head")
    rig.fx("Heart", (0, -0.4, 3.6), "Chest")
    rig.fx("Mane", NECK[2] + Vector((0, 0, 0.7)), "Neck1")


# ---------------------------------------------------------------- tête + épée

def build_head(rig):
    H, J = "Head", "Jaw"
    before = {o.name for o in bpy.context.scene.objects}
    skull = a.loft_profile("Skull", SKULL, droop=0.05, tip_length=0.15)
    hit = a.surface_caster(skull)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.17, 0.15),
                  a.hole_x((0, -0.3, -0.02), 0.24, 0.2),                    # fosse temporale
                  a.hole_x((0, -1.6, -0.15), 0.3, 0.08),                    # fenêtre maxillaire
                  a.hole_along((0, -2.75, -0.15), (0, 1, 0), (1, 0, 0), 0.1, 0.12, depth=0.4)])
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 5))
        return p

    rig.add(a.band("SagittalCrest", [top(0, y) for y in (-0.05, -0.25, -0.6, -0.85)], [0.1, 0.22, 0.16, 0.05],
                   0.06, offset=0.15), H, "bone_shade", **HEAD)
    rig.add(r.tube("Nasal", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in (-1.15, -1.7, -2.3, -2.65)],
                   [0.05, 0.05, 0.04, 0.03], segments=4), H, "bone_shade", **HEAD)
    rune(rig, "BrowRune", top(0, -1.0) + Vector((0, 0, 0.03)), (0, -0.3, 1), H, size=0.22)
    for s in (-1, 1):
        # Os nasaux, crête maxillaire, foramens, épines jugales, flamme de givre des yeux
        rig.add(r.tube(f"NasalBone{s}", [tuple(top(s * 0.09, y) + Vector((0, 0, 0.012))) for y in (-1.3, -1.9, -2.5)],
                       [0.035, 0.03, 0.025], segments=4), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"MaxillaRidge{s}", [(s * a.side_width(SKULL, y, -0.15) * 1.0, y, -0.15) for y in (-0.9, -1.5, -2.1, -2.5)],
                       [0.05, 0.055, 0.045, 0.035], segments=4), H, "bone_shade", **HEAD)
        for k in range(3):
            y = -1.9 - 0.2 * k
            rig.add(r.ico(f"Foramen{s}{k}", 0.03, subdivisions=1, location=(s * a.side_width(SKULL, y, 0.0) * 1.01, y, 0.0)),
                    H, "ink", **HEAD)
        rig.add(a.claw(f"JugalSpike{s}", (s * 0.7, -0.55, -0.1), (s * 0.5, 1, -0.1), 0.5, 0.06, curl=-0.2, segments=4), H,
                "horn", **HEAD)
        rune(rig, f"CheekRune{s}", (s * a.side_width(SKULL, -1.45, 0.05) * 1.02, -1.45, 0.05), (s, 0, 0.2), H, size=0.16)
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(a.claw(f"EyeFlame{s}", (s * x, EYE[0] + 0.05, EYE[1] + 0.05), (s * 0.3, 1, 0.35), 0.7, 0.06, curl=-0.3,
                       segments=4), H, "glow", glow=True)
    for s in (-1, 1):
        x = a.side_width(SKULL, EYE[0], EYE[1])
        c0 = Vector((s * x, EYE[0], EYE[1]))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=c0 - Vector((s * 0.07, 0, 0))), H, "glow",
                glow=True)
        rig.add(a.ring_around(f"OrbitRim{s}", c0, (s, -0.5, 0.2), 0.17, 0.04, segments=10), H, "bone_shade",
                **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.15, -1.15, 0.38), (s * 0.5, -0.75, 0.42), 0.16, 0.07, width_end=0.1,
                        normal=(0, -0.3, 1)), H, "bone_shade", **HEAD)
        # Arcade zygomatique très écartée (crâne de loup massif)
        rig.add(r.tube(f"Zygomatic{s}", [(s * 0.45, -1.15, -0.12), (s * 0.72, -0.7, -0.1),
                                         (s * 0.68, -0.3, -0.05), (s * 0.42, -0.1, -0.05)],
                       [0.05, 0.08, 0.07, 0.05], segments=5), H, "bone", **HEAD)
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.48, -0.72, 0.38), (s * 0.66, -0.68, 0.08)], 0.04, segments=4),
                H, "bone_shade", **HEAD)
        # Dents du haut : incisives, canine énorme, prémolaires, carnassière
        for k in range(3):
            p = Vector((s * (0.05 + 0.055 * k), -2.75 + 0.04 * k, -0.33))
            rig.add(mr.tooth(f"Incisor{s}{k}", p, p + Vector((0, -0.03, -0.16)), 0.07, 0.06, Vector((0, -1, 0)),
                             curl=0.1), H, "tooth", **HEAD)
        can = Vector((s * 0.2, -2.45, -0.36))
        rig.add(mr.tooth(f"Canine{s}", can, can + Vector((s * 0.03, -0.04, -0.6)), 0.19, 0.15, Vector((s, -0.3, 0)),
                         curl=0.15), H, "tooth", **HEAD)
        for k in range(5):
            y = -2.15 + 0.27 * k
            xx = s * a.side_width(SKULL, y, -0.4) * 0.88
            size = 0.32 if k == 3 else 0.14 + 0.02 * k
            rig.add(mr.tooth(f"UpTooth{s}{k}", (xx, y, -0.4), (xx, y + 0.03, -0.4 - size), size * 0.7, size * 0.4,
                             Vector((s, 0, 0)), curl=0.05), H, "tooth", **HEAD)
        rig.add(r.tube(f"UpperGum{s}", [(s * a.side_width(SKULL, y, -0.4) * 0.8, y, -0.38)
                                        for y in (-2.6, -1.9, -1.2, -0.8)], 0.035, segments=4), H, "gum", **HEAD)
    # Mandibule massive, grande ouverte (bloquée par l'épée)
    jaw_before = {o.name for o in bpy.context.scene.objects}
    for s in (-1, 1):
        line = a.smooth_path([(s * HINGE[0], HINGE[1], HINGE[2]), (s * 0.38, -0.9, -0.46), (s * 0.28, -1.8, -0.5),
                              (s * 0.13, -2.6, -0.5)], 8)
        hs = [0.48, 0.42, 0.34, 0.27, 0.24, 0.26, 0.25, 0.2]
        mand = a.band(f"Mandible{s}", line, hs, [0.12 - 0.005 * i for i in range(8)], offset=1)
        a.cut(mand, [a.hole_along((s * 0.4, -0.75, -0.72), (1, 0, 0), (0, 1, 0), 0.25, 0.08, depth=0.5)])
        rig.add(mand, J, "bone", **HEAD)
        rig.add(r.tube(f"MandibleBase{s}", [tuple(p - Vector((0, 0, h))) for p, h in zip(line, hs)], 0.04,
                       segments=4), J, "bone_shade", **HEAD)
        rig.add(a.blade(f"Coronoid{s}", line[0] + Vector((0, -0.12, 0)), line[0] + Vector((0, -0.02, 0.4)), 0.24,
                        0.06, width_end=0.1, normal=(1, 0, 0)), J, "bone", **HEAD)
        rig.add(r.ico(f"Hinge{s}", 0.09, subdivisions=1, location=line[0]), H, "bone_shade", **HEAD)
        can = mr.along(line, 0.86) + Vector((-s * 0.03, 0, 0))
        rig.add(mr.tooth(f"LowCanine{s}", can, can + Vector((s * 0.03, -0.03, 0.5)), 0.17, 0.14, Vector((s, -0.3, 0)),
                         curl=0.15), J, "tooth", **HEAD)
        for k in range(5):
            p = mr.along(line, 0.2 + 0.12 * k) + Vector((-s * 0.04, 0, 0))
            size = 0.3 if k == 1 else 0.13 + 0.02 * (k % 2)
            rig.add(mr.tooth(f"LowTooth{s}{k}", p, p + Vector((0, 0, size)), size * 0.7, size * 0.4, Vector((s, 0, 0)),
                             curl=0.05), J, "tooth", **HEAD)
        rig.add(r.tube(f"LowerGum{s}", [tuple(q + Vector((-s * 0.04, 0, 0.02))) for q in line[1:]], 0.035,
                       segments=4), J, "gum", **HEAD)
        for k in range(2):
            p = Vector((s * (0.05 + 0.05 * k), -2.62, -0.52))
            rig.add(mr.tooth(f"LowIncisor{s}{k}", p, p + Vector((0, -0.03, 0.14)), 0.06, 0.05, Vector((0, -1, 0)),
                             curl=0.1), J, "tooth", **HEAD)
    rig.add(r.ico("Chin", 0.11, subdivisions=2, location=(0, -2.62, -0.62), scale=(1.5, 1, 0.9)), J, "bone",
            **HEAD)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in jaw_before]:
        o.data.transform(_jm @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)
    # Collerette de piques d'os derrière le crâne (silhouette impressionnante)
    for k in range(9):
        ang = math.radians(-80 + 160 * k / 8)
        d = Vector((math.sin(ang), 0.9, 0.55 + 0.6 * math.cos(ang)))
        base = Vector((0.33 * math.sin(ang), 0.02, 0.1 + 0.3 * math.cos(ang)))
        rig.add(a.claw(f"Ruff{k}", base, d, 0.75 + 0.35 * math.cos(ang), 0.07, curl=-0.25, segments=5), H, "horn",
                **HEAD)
    rig.add(r.ico("Tongue", 0.12, subdivisions=2, location=_jm @ Vector((0, -1.3, -0.6)), scale=(2.6, 3.5, 0.45)), J,
            "gum", **HEAD)
    rig.add(r.ico("Throat", 0.14, subdivisions=2, location=(0, -1.0, -0.45), scale=(1.3, 2.4, 0.6)), H, "glow",
            glow=True)
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]:
        o.data.transform(HEAD_M @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        side, up = a._basis(t)
        bone = "Hips" if i < 9 else "Chest"
        withers = max(0.0, (i - 10) / (n - 10))
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.34, spine=1.2 + 1.2 * withers, lean=0.5), bone, "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.28), bone, "disc")
        # Crinière de piques d'os hérissées (plus longues au garrot)
        if i % 2 == 0 and i > 4:
            ln = 0.4 + 0.6 * withers
            for s in (-1, 1):
                rig.add(a.claw(f"Hackle{i}{s}", SPINE[i] + up * 0.35 + side * s * 0.12, up + side * s * 0.4 + t * 0.6,
                               ln, 0.05, curl=-0.2, segments=4), bone, "horn")
    # Cage profonde (poitrail de loup), sternum, cœur runique
    sternum = []
    for k, i in enumerate(range(5, n - 1)):
        f = k / (n - 7)
        hw = 0.85 + 0.25 * math.sin(math.pi * f)
        depth = 1.05 + 0.85 * f
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{k}{s}", SPINE[i], hw, depth, s, sweep=-0.2, radius=0.08), "Hips" if i < 9 else "Chest",
                    "bone")
        sternum.append(SPINE[i] + Vector((0, -0.2, -depth)))
    rig.add(a.band("Sternum", sternum[::2], 0.1, 0.5), "Chest", "bone_shade")
    for k, (dx, h) in enumerate(((0, 0.6), (0.15, 0.4), (-0.15, 0.45))):
        rig.add(a.crystal(f"RuneHeart{k}", (dx, -0.4, 3.6), 0.12 if k == 0 else 0.08, h, sides=4), "Chest", "glow",
                glow=True)
    # Cou : vertèbres + crinière haute
    for i in range(len(NECK)):
        t = tangent(NECK, i)
        side, up = a._basis(t)
        bone = "Neck1" if i < 4 else "Neck2"
        rig.add(a.vertebra(f"NeckVert{i}", NECK[i], t, 0.26, spine=1.4, lean=0.4), bone, "bone")
        if i < len(NECK) - 1:
            rig.add(a.disc(f"NeckDisc{i}", NECK[i].lerp(NECK[i + 1], 0.5), t, 0.26), bone, "disc")
        for s in (-1, 1):
            rig.add(a.claw(f"NeckHackle{i}{s}", NECK[i] + up * 0.35 + side * s * 0.15, up + side * s * 0.5 + Vector((0, 0.8, 0)),
                           0.9 - 0.04 * i, 0.06, curl=-0.25, segments=4), bone, "horn")
    for k, i in enumerate(range(6, n - 2, 3)):
        for s in (-1, 1):
            rune(rig, f"RibRune{k}{s}", SPINE[i] + Vector((s * 0.72, -0.25, -0.45)), (s, -0.2, 0), "Chest" if i >= 9 else "Hips",
                 size=0.14)
    # Fraise de piques autour du cou
    cc, t = NECK[2], tangent(NECK, 2)
    side, up = a._basis(t)
    for k in range(12):
        ang = 2 * math.pi * k / 12
        d = side * math.cos(ang) + up * math.sin(ang)
        if d.z < -0.6:
            continue
        rig.add(a.claw(f"NeckRuff{k}", cc + d * 0.3, d + Vector((0, 0.9, 0)), 0.8 + 0.3 * max(0, d.z), 0.06, curl=-0.2,
                       segments=4), "Neck1", "horn")
    # Omoplates et bassin runés
    for s in (-1, 1):
        sh = leg("Front", s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[-3] + Vector((s * 0.3, 0.3, 0.2)), sh, 0.55, 0.07, width_end=0.28,
                        mid=0.55, normal=(s, 0, 0.3)), "Chest", "bone")
        rig.add(a.claw(f"ShoulderSpike{s}", SPINE[-3].lerp(sh, 0.4) + Vector((s * 0.3, 0.2, 0.2)), (s * 0.5, 0.6, 1), 0.7, 0.08,
                       curl=-0.2, segments=5), "Chest", "horn")
        rune(rig, f"ScapulaRune{s}", SPINE[-3].lerp(sh, 0.5) + Vector((s * 0.4, 0.25, 0.05)), (s, 0, 0.3), "Chest")
        hp = leg("Hind", s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[2] + Vector((s * 0.2, -0.3, 0.1)), hp + Vector((s * 0.08, 0, 0.15)), 0.5,
                        0.08, width_end=0.3, mid=0.5, normal=(s, 0, 0.5)), "Hips", "bone")
        rig.add(a.long_bone(f"Ischium{s}", hp, (s * 0.25, 2.95, 3.85), 0.07, condyles=False, segments=5), "Hips",
                "bone_shade")
    # Queue touffue : vertèbres + éventails de piques
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        side, up = a._basis(t)
        size = 0.17 - 0.09 * i / (nt - 1)
        bone = f"Tail{min(3, i * 3 // nt + 1)}"
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=0.9, lean=0.4), bone, "bone", **TAILP)
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc", **TAILP)
        if i % 2 == 1:
            for s in (-1, 1):
                rig.add(a.claw(f"TailFur{i}{s}", TAIL[i], side * s + t * 1.2 - up * 0.3, 0.35 + 0.02 * i, 0.04, curl=-0.2,
                               segments=4), bone, "horn", **TAILP)


def build_chain(rig):
    """Gleipnir brisé : collier runique et entraves d'où pendent des fragments de ruban déchirés."""
    cc, t = NECK[4], tangent(NECK, 4)
    side, up = a._basis(t)
    rig.add(a.ring_around("Collar", cc, t, 0.42, 0.08, segments=14), "Neck1", "iron")
    for k in range(6):
        ang = 2 * math.pi * k / 6
        d = side * math.cos(ang) + up * math.sin(ang)
        rune(rig, f"CollarRune{k}", cc + d * 0.48, d, "Neck1", size=0.1)
        rig.add(a.claw(f"CollarSpike{k}", cc + d * 0.48, d, 0.25, 0.04, curl=0, segments=4), "Neck1", "iron")
    for k, (sx, ln) in enumerate(((-1, 1.4), (1, 0.9), (0.3, 1.8))):
        start = cc - up * 0.46 + side * sx * 0.2
        path = a.smooth_path([start, start + Vector((sx * 0.15, -0.1, -ln * 0.5)), start + Vector((sx * 0.3, 0.1, -ln))], 8)
        ribbon(rig, f"Gleipnir{k}", path, "Neck1")
        rig.add(a.claw(f"GleipnirTear{k}", path[-1], (sx * 0.3, 0, -1), 0.15, 0.04, curl=0, segments=4), "Neck1", "glow",
                glow=True)
    for s, side_n in ((1, "L"), (-1, "R")):
        for prefix in ("Front", "Hind"):
            p = leg(prefix, s)
            q = p[2].lerp(p[3], 0.3)
            bone = f"{prefix}Foot_{side_n}"
            rig.add(a.ring_around(f"Fetter{prefix}{s}", q, p[3] - p[2], 0.17, 0.05, segments=10), bone, "iron", **LEGS)
            frag = a.smooth_path([q + Vector((s * 0.17, 0, 0)), q + Vector((s * 0.3, 0.1, -0.3)), q + Vector((s * 0.35, 0.25, -0.55))], 6)
            ribbon(rig, f"Fragment{prefix}{s}", frag, bone, radius=0.025, **LEGS)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix in ("Front", "Hind"):
            p = leg(prefix, s)
            bones = [f"{prefix}{nm}_{side}" for nm in ("Upper", "Lower", "Foot")]
            rig.add(a.long_bone(f"{prefix}Upper{s}", p[0], p[1], 0.21, segments=7), bones[0], "bone", **LEGS)
            off = (p[2] - p[1]).cross(Vector((1, 0, 0))).normalized() * 0.07
            rig.add(a.long_bone(f"{prefix}Lower{s}", p[1] + off, p[2] + off, 0.14, segments=7), bones[1], "bone",
                    **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", p[1] - off, p[2] - off, 0.08, condyles=False, segments=6),
                    bones[1], "bone_shade", **LEGS)
            rune(rig, f"{prefix}LegRune{s}", p[0].lerp(p[1], 0.5) + Vector((s * 0.17, 0, 0)), (s, 0, 0), bones[0])
            rig.add(a.claw(f"{prefix}Point{s}", p[1], (0, 1, 0.3) if prefix == "Front" else (0, -1, 0.3), 0.3, 0.08,
                           curl=0, segments=4), bones[1], "bone_shade", **LEGS)
            rig.add(r.ico(f"{prefix}Wrist{s}", 0.15, subdivisions=1, location=p[2]), bones[2], "bone_shade", **LEGS)
            for k in range(3):
                rig.add(a.claw(f"{prefix}Tuft{s}{k}", p[2] + Vector((s * 0.05 * (k - 1), 0.1, 0)), (s * 0.3 * (k - 1), 1, 0.2),
                               0.3, 0.04, curl=-0.3, segments=4), bones[2], "horn", **LEGS)
            rig.add(a.claw(f"{prefix}ElbowSpike{s}", p[1] + Vector((s * 0.12, 0, 0)), (s * 0.4, 1 if prefix == "Front" else -0.6, 0.5),
                           0.45, 0.06, curl=-0.2, segments=4), bones[1], "horn", **LEGS)
            rig.add(a.long_bone(f"{prefix}Meta{s}", p[2], p[3] + Vector((0, 0, 0.08)), 0.11, segments=6), bones[2],
                    "bone", **LEGS)
            for k in range(4):
                d = Vector((s * (k - 1.5) * 0.25, -1, 0)).normalized()
                toe = p[3] + d * 0.4 + Vector((0, 0, -0.06))
                rig.add(a.long_bone(f"{prefix}Toe{s}{k}", p[3] + Vector((0, 0, 0.06)), toe, 0.05, condyles=False,
                                    segments=5), bones[2], "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{k}", toe, d + Vector((0, 0, -0.7)), 0.22, 0.05, curl=0.4, segments=4),
                        bones[2], "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_chain(rig)
    build_legs(rig)
    # Colosse : tout est agrandi depuis l'origine (les pattes restent au sol)
    m = Matrix.Scale(SCALE, 4)
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            o.data.transform(m @ o.matrix_basis)
            o.matrix_basis = Matrix.Identity(4)
    rig.bones = {k: (h * SCALE, tl * SCALE, par) for k, (h, tl, par) in rig.bones.items()}
    return rig
