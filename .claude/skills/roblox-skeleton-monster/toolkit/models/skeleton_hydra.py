"""Hydre squelette dorée à 3 têtes (≈ 12 studs de long, 7 de haut) — créature animable.

Identité propre (différente du T-Rex, du dragon, du raptor et du tricératops) :
- os dorés, incrustés de pièces d'or ;
- cornes de bélier enroulées (bronze sombre, pointes dorées), une variante par tête ;
- corps bas qui rampe, pattes écartées en crocodile, queue enroulée au sol,
  trois longs cous en éventail à des hauteurs différentes ;
- trois têtes identiques, très détaillées : cornes de bélier baguées d'or à gemme,
  couronne de piques à gemmes, diadème d'or, sourcils hérissés, pommettes à piques et
  boucles d'oreille, barbe d'épines, collier d'or hérissé en haut du cou ;
- thème or : idole de cristal entourée de pièces en orbite, gemmes, effets Roblox « gold ».

4 pièces Roblox : corps, HeadA, HeadB, HeadC (chaque tête avec son cou), plus le mesh lumineux.
Os du rig : Root, Hips, Spine, Chest, Neck{A,B,C}1-2, Head{A,B,C}, Jaw{A,B,C}, Tail1-5,
UpperArm/Forearm/Hand_L/R, Thigh/Shin/Foot_L/R, + FX_* (yeux, gueules, cœur, queue).
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r

COLORS = {
    "bone": "#e3c068",
    "bone_shade": "#a8842e",
    "tooth": "#fff2c8",
    "horn": "#2b1d12",
    "horn_tip": "#d9a531",
    "coin": "#ffd94a",
    "disc": "#5a3a10",
    "membrane": "#6b4a16",
    "glow": "#ffc21a",
    "glow_hot": "#fff3b0",
}

EFFECT_THEME = "gold"

TEST_POSE = {
    "JawA": (30, 0, 0),
    "NeckA2": (-12, 0, 0),
    "NeckB1": (0, 0, 20),
    "JawB": (35, 0, 0),
    "HeadC": (20, 0, 0),
    "JawC": (25, 0, 0),
    "UpperArm_L": (-30, 0, 0),
    "Tail3": (0, 0, -20),
}

VIEW = (0.35, -1.0, 0.75)   # de face, plongeant : on voit l'éventail des 3 cous

BACK = [(0, 1.5, 2.1), (0, 0.0, 2.25), (0, -1.6, 2.2)]
TAIL = [(0, 1.5, 2.1), (0, 3.1, 1.65), (0.6, 4.6, 1.05), (1.7, 5.7, 0.6), (3.0, 6.1, 0.42),
        (4.1, 5.5, 0.4)]

# Cous : points de la base (avant du thorax) jusqu'à l'articulation de la tête,
# lacet (rotation de la tête autour de Z) et tangage (museau vers le bas si > 0)
NECKS = {
    "A": ([(0, -1.9, 2.45), (0, -2.6, 3.6), (0, -2.9, 5.0), (0, -3.3, 6.1)], 0.0, 0.2),
    "B": ([(0.4, -1.8, 2.4), (1.5, -2.2, 3.1), (2.5, -2.6, 4.0), (3.1, -3.0, 4.5)], 0.6, 0.1),
    "C": ([(-0.4, -1.8, 2.4), (-1.5, -2.3, 2.75), (-2.4, -2.9, 3.2), (-2.9, -3.4, 3.4)], -0.55,
          0.3),
}
HEAD_SCALE = 0.8


def head_matrix(key):
    pts, yaw, pitch = NECKS[key]
    return (Matrix.Translation(pts[-1]) @ Matrix.Rotation(yaw, 4, "Z")
            @ Matrix.Rotation(pitch, 4, "X") @ Matrix.Scale(HEAD_SCALE, 4))


width_at, side_width = a.width_at, a.side_width


def place(objs, m):
    """Déplace des pièces modélisées en repère local de tête vers leur place dans le monde."""
    for o in objs:
        o.data.transform(m @ o.matrix_basis)
        o.matrix_basis = Matrix.Identity(4)


def new_objects(before):
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in before]


def coin(rig, name, location, normal, bone, radius=0.13, float_ok=False, **kw):
    """Pièce d'or (disque épais) incrustée, tournée vers `normal`.
    `float_ok` : pièce volontairement suspendue (orbite magique autour du cœur)."""
    n = Vector(normal).normalized()
    obj = r.cylinder(name, radius, 0.05, segments=10)
    rot = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(location) @ rot)
    obj["float_ok"] = float_ok
    return rig.add(obj, bone, "coin", **kw)


def eye_and_rim(rig, k, s, y, z, x, radius, bone, **kw):
    rig.add(r.ico(f"Eye{k}{s}", radius, subdivisions=2, location=(s * x * 0.7, y, z)), bone,
            "glow", glow=True)
    ring = [(s * x, y + math.cos(t) * radius * 1.7, z + math.sin(t) * radius * 1.7)
            for t in (2 * math.pi * i / 12 for i in range(12))]
    rig.add(r.tube(f"OrbitRim{k}{s}", ring, 0.045, segments=4, closed=True), bone, "bone_shade",
            **kw)


def teeth(rig, k, skull, jaw, y0, y1, step, fang_rows, bone_h, bone_j, z_up, z_low, **kw):
    for is_jaw, sections, z, direction, bone in ((False, skull, z_up, (0, 0.2, -1), bone_h),
                                                 (True, jaw, z_low, (0, -0.2, 1), bone_j)):
        y, i = y0, 0
        while y < y1:
            for s in (-1, 1):
                x = s * width_at(sections, y) * (0.72 if is_jaw else 0.86)
                length = (0.42 if i in fang_rows else 0.2) * (0.8 if is_jaw else 1)
                rig.add(a.claw(f"Tooth{k}{bone}{s}{i}", (x, y, z), direction, length, 0.06,
                               curl=-0.08, segments=4), bone, "tooth", **kw)
            y += step
            i += 1


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 1.5, 2.1), (0, 0.0, 2.25), "Root")
    rig.bone("Spine", (0, 0.0, 2.25), (0, -1.0, 2.25), "Hips")
    rig.bone("Chest", (0, -1.0, 2.25), (0, -1.9, 2.4), "Spine")
    for key, (pts, yaw, pitch) in NECKS.items():
        rig.bone(f"Neck{key}1", pts[0], pts[2], "Chest")
        rig.bone(f"Neck{key}2", pts[2], pts[3], f"Neck{key}1")
        m = head_matrix(key)
        rig.bone(f"Head{key}", m @ Vector((0, 0, 0)), m @ Vector((0, -1.9, 0)), f"Neck{key}2")
        rig.bone(f"Jaw{key}", m @ Vector((0, 0.05, -0.38)), m @ Vector((0, -1.9, -0.55)),
                 f"Head{key}")
        rig.fx(f"Mouth{key}", m @ Vector((0, -0.9, -0.35)), f"Head{key}")
    parent = "Hips"
    for i in range(5):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"UpperArm_{side}", (s * 0.7, -1.5, 1.9), (s * 1.6, -1.7, 1.5), "Chest")
        rig.bone(f"Forearm_{side}", (s * 1.6, -1.7, 1.5), (s * 1.75, -2.0, 0.35),
                 f"UpperArm_{side}")
        rig.bone(f"Hand_{side}", (s * 1.75, -2.0, 0.35), (s * 1.8, -2.6, 0.1), f"Forearm_{side}")
        rig.bone(f"Thigh_{side}", (s * 0.7, 1.4, 1.9), (s * 1.7, 1.0, 1.4), "Hips")
        rig.bone(f"Shin_{side}", (s * 1.7, 1.0, 1.4), (s * 1.8, 1.5, 0.35), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 1.8, 1.5, 0.35), (s * 1.85, 0.9, 0.1), f"Shin_{side}")
    rig.fx("Heart", (0, -0.6, 1.55), "Spine")
    rig.fx("TailTip", TAIL[-1], "Tail5")


# ---------------------------------------------------------------- têtes (repère local)
# Articulation de la tête à l'origine, museau vers -Y, Z vers le haut.

# Une seule tête, répétée sur les 3 cous (repère local : articulation à l'origine, museau -Y).
# Crâne de bélier démoniaque : front large et plat entre les cornes, orbites qui ressortent,
# nez busqué qui plonge vers un museau étroit et arrondi (pas une face plate).
SKULL = [(0.1, 0.5, 0.7, 0.6, 0.55, -0.35), (-0.25, 0.6, 0.8, 0.62, 0.72, -0.4),
         (-0.6, 0.62, 0.84, 0.6, 0.75, -0.4), (-0.95, 0.42, 0.6, 0.5, 0.68, -0.38),
         (-1.3, 0.3, 0.44, 0.4, 0.58, -0.36), (-1.6, 0.26, 0.38, 0.36, 0.45, -0.34),
         (-1.85, 0.22, 0.32, 0.3, 0.27, -0.32), (-2.0, 0.17, 0.25, 0.23, 0.1, -0.3)]
JAW = [(0.0, 0.45, 0.66, 0.55, -0.38, -0.8), (-0.8, 0.4, 0.56, 0.46, -0.4, -0.8),
       (-1.5, 0.27, 0.38, 0.32, -0.38, -0.66), (-1.95, 0.17, 0.24, 0.2, -0.36, -0.56)]
EYE_Y, EYE_Z = -0.6, 0.35


def build_head(rig, k):
    """Tête d'hydre : cornes de bélier baguées d'or, couronne, diadème, collier."""
    H, J, kw = f"Head{k}", f"Jaw{k}", dict(part=f"Head{k}")
    skull = a.loft_profile(f"Skull{k}", SKULL, droop=0.25)
    # Ouvertures : orbites, fenêtres, tempes, et naseaux creusés dans le bout du museau
    a.cut(skull, [a.hole_x((0, EYE_Y, EYE_Z), 0.2, 0.2), a.hole_x((0, -1.15, 0.05), 0.28, 0.11),
                  a.hole_x((0, -0.02, 0.2), 0.1, 0.24)]
          + [a.hole_along((sx * 0.08, -2.15, -0.06), (0, 1, 0.35), (1, 0, 0), 0.055, 0.08,
                          depth=0.25) for sx in (-1, 1)])
    rig.add(skull, H, "bone", **kw)
    jaw = a.loft_profile(f"Jaw{k}", JAW, droop=-0.1)
    a.cut(jaw, [a.hole_x((0, -0.6, -0.6), 0.28, 0.08)])
    rig.add(jaw, J, "bone", **kw)

    for s in (-1, 1):
        # --- Cornes de bélier, baguées d'or, gemme en pointe
        spiral = dict(side=(s, 0, 0), back=(0, 1, 0), up=(0, 0, 1), coil=0.55, turns=1.15,
                      spread=0.55)
        base = (s * 0.42, -0.25, 0.62)
        rig.add(a.spiral_horn(f"Ram{k}{s}", base, radius=0.24, **spiral), H, "horn", **kw)
        path = a.spiral_points(base, **spiral)
        for i in (2, 5, 8, 11):
            t = i / (len(path) - 1)
            tan = path[i + 1] - path[i - 1]
            rig.add(a.ring_around(f"RamBand{k}{s}{i}", path[i], tan, 0.24 * (1 - t) ** 0.9 + 0.035,
                                  0.035), H, "coin", **kw)
        tip, tan = path[-2], path[-1] - path[-2]
        rig.add(a.claw(f"RamGem{k}{s}", tip, tan, 0.22, 0.06, curl=0, segments=4), H, "glow",
                glow=True)
        # --- Œil, bourrelet d'orbite, sourcil hérissé
        x = side_width(SKULL, EYE_Y, EYE_Z)
        rig.add(r.ico(f"Eye{k}{s}", 0.14, subdivisions=2, location=(s * (x - 0.02), EYE_Y, EYE_Z)),
                H, "glow", glow=True)
        ring = [(s * x, EYE_Y + math.cos(t) * 0.24, EYE_Z + math.sin(t) * 0.24)
                for t in (2 * math.pi * i / 12 for i in range(12))]
        rig.add(r.tube(f"OrbitRim{k}{s}", ring, 0.045, segments=4, closed=True), H, "bone_shade",
                **kw)
        # Orbite saillante (comme chez le bélier) : un manchon d'os qui ressort de la tempe
        socket = [[(s * (x + dx), EYE_Y + math.cos(t) * rad, EYE_Z + math.sin(t) * rad)
                   for t in (2 * math.pi * i / 12 for i in range(12))]
                  for dx, rad in ((-0.06, 0.25), (0.04, 0.27), (0.08, 0.25))]
        rig.add(r.loft(f"OrbitSocket{k}{s}", socket, cap=False), H, "bone_shade", **kw)
        ring = [(s * (x + 0.08), EYE_Y + math.cos(t) * 0.25, EYE_Z + math.sin(t) * 0.25)
                for t in (2 * math.pi * i / 12 for i in range(12))]
        rig.add(r.tube(f"OrbitLip{k}{s}", ring, 0.04, segments=4, closed=True), H, "bone", **kw)
        rig.add(a.blade(f"Brow{k}{s}", (s * 0.15, -0.9, 0.62), (s * 0.55, -0.45, 0.78), 0.26, 0.13,
                        width_end=0.2, mid=0.32, normal=(0, 0.25, 1)), H, "bone_shade", **kw)
        for i, (yy, ln) in enumerate(((-0.85, 0.18), (-0.65, 0.24), (-0.45, 0.3))):
            rig.add(a.claw(f"BrowSpike{k}{s}{i}", (s * (0.25 + 0.15 * i), yy, 0.72),
                           (s * 0.4, 0.6, 0.8), ln, 0.045, curl=-0.15, segments=4), H, "horn",
                    **kw)
        rig.fx(f"Eye{k}{s}", head_matrix(k) @ Vector((s * (x + 0.05), EYE_Y, EYE_Z)), H)
        # --- Pommette en arche avec piques + bosse
        cheek = [(s * 0.5, -1.15, -0.22), (s * 0.78, -0.75, -0.2), (s * 0.82, -0.3, -0.1),
                 (s * 0.65, 0.05, 0.12)]
        arch = r.tube(f"Zygomatic{k}{s}", cheek, [0.06, 0.09, 0.09, 0.06], segments=6)
        r.smooth(arch, 40)
        rig.add(arch, H, "bone_shade", **kw)
        for i, (p, ln) in enumerate(((cheek[1], 0.28), (cheek[2], 0.42))):
            rig.add(a.claw(f"CheekSpike{k}{s}{i}", p, (s * 0.8, 0.6, -0.25), ln, 0.06, curl=-0.1,
                           segments=4), H, "horn", **kw)
        # Boucle d'oreille : anneau d'or suspendu à l'arche
        rig.add(a.ring_around(f"Earring{k}{s}", Vector(cheek[2]) + Vector((s * 0.06, 0.05, -0.17)),
                              (0, 1, 0), 0.12, 0.03), H, "coin", **kw)
        # --- Museau : bosses de narines, bosses alignées, nodules du bord dentaire
        rig.add(r.ico(f"NostrilBoss{k}{s}", 0.08, subdivisions=1, location=(s * 0.15, -2.05, 0.06),
                      scale=(0.8, 1.2, 1.1)), H, "bone_shade", **kw)
        # Tubercule facial (bosse sous l'œil, typique du bélier)
        rig.add(r.ico(f"FacialTuber{k}{s}", 0.1, subdivisions=1,
                      location=(s * side_width(SKULL, -1.05, 0.15), -1.05, 0.15), scale=(0.6, 1.4, 0.8)),
                H, "bone_shade", **kw)
        for i, yy in enumerate((-1.2, -1.45, -1.7)):
            rig.add(r.ico(f"SnoutKnob{k}{s}{i}", 0.065, subdivisions=1,
                          location=(s * side_width(SKULL, yy, 0.12), yy, 0.12), scale=(0.6, 1, 1)),
                    H, "bone_shade", **kw)
        yy = SKULL[0][0] - 0.25
        while yy > SKULL[-1][0] + 0.2:
            rig.add(r.ico(f"Rim{k}{s}{yy:.2f}", 0.05, subdivisions=1,
                          location=(s * width_at(SKULL, yy, 3), yy, width_at(SKULL, yy, 5) + 0.12),
                          scale=(0.6, 1, 0.8)), H, "bone_shade", **kw)
            yy -= 0.26
        # Veine d'or lumineuse de l'œil vers la nuque
        vein = [(s * x * 0.98, EYE_Y + 0.22, EYE_Z + 0.04), (s * x * 0.97, EYE_Y + 0.4, EYE_Z + 0.14),
                (s * x * 0.95, EYE_Y + 0.58, EYE_Z + 0.02)]
        rig.add(r.tube(f"GoldVein{k}{s}", vein, 0.025, segments=4), H, "glow", glow=True)
        # Collerette de nuque : 3 piques en éventail
        for i in range(3):
            rig.add(a.claw(f"NapeSpike{k}{s}{i}", (s * 0.4, 0.08, 0.35 - i * 0.2),
                           (s * 0.6, 1, 0.5 - i * 0.45), 0.38 - i * 0.06, 0.06, curl=-0.1,
                           segments=4), H, "horn", **kw)
        # --- Mâchoire : apophyse, crête, épines d'angle, bosses
        rig.add(a.blade(f"Coronoid{k}{s}", (s * 0.5, -0.25, -0.62), (s * 0.52, -0.05, -0.3), 0.26,
                        0.08, width_end=0.14, normal=(1, 0, 0), bevel=0), J, "bone_shade", **kw)
        rig.add(r.tube(f"JawRidge{k}{s}", [(s * width_at(JAW, yy, 2) * 0.98, yy, -0.6)
                                           for yy in (-0.2, -0.9, -1.6)], [0.05, 0.06, 0.04],
                       segments=4), J, "bone_shade", **kw)
        rig.add(a.claw(f"JawSpike{k}{s}", (s * 0.55, 0.0, -0.75), (s * 0.6, 0.7, -0.5), 0.4, 0.08,
                       curl=-0.1, segments=5), J, "horn", **kw)
        for i, yy in enumerate((-0.5, -1.1)):
            rig.add(r.ico(f"JawKnob{k}{s}{i}", 0.08, subdivisions=1,
                          location=(s * width_at(JAW, yy, 2) * 0.98, yy, -0.68), scale=(0.6, 1, 0.9)),
                    J, "bone_shade", **kw)

    # --- Couronne de 5 piques à gemmes dorées
    for i, x in enumerate((-0.32, -0.16, 0.0, 0.16, 0.32)):
        h = 0.5 - abs(x) * 0.6
        base = Vector((x, -0.35, width_at(SKULL, -0.35, 4) - 0.04))
        d = Vector((x * 0.8, 0.15, 1))
        rig.add(a.claw(f"Crown{k}{i}", base, d, h, 0.07, curl=0, segments=5), H, "horn", **kw)
        tip, tan = a.claw_point(base, d, h, 0, 0.75)
        rig.add(a.claw(f"CrownGem{k}{i}", tip, tan, h * 0.28, 0.035, curl=0, segments=4), H, "glow",
                glow=True)
    # Diadème : bandeau d'or qui court sur le front d'une corne à l'autre, gemme au centre
    band = [(x, -0.62 - 0.12 * (1 - abs(x) / 0.5), side_top + 0.03)
            for x in (-0.5, -0.25, 0.0, 0.25, 0.5)
            for side_top in [width_at(SKULL, -0.62 - 0.12 * (1 - abs(x) / 0.5), 4)
                             - 0.06 * (abs(x) / 0.5) ** 2]]
    rig.add(r.tube(f"Diadem{k}", band, 0.04, segments=4), H, "coin", **kw)
    gem_c = Vector(band[2]) + Vector((0, -0.02, 0.05))
    rig.add(a.crystal(f"DiademGem{k}", gem_c, 0.08, 0.2, sides=4), H, "glow", glow=True)
    rig.add(a.ring_around(f"GemSetting{k}", gem_c - Vector((0, 0, 0.04)), (0, 0, 1), 0.11, 0.03),
            H, "coin", **kw)
    # Arête nasale, petite corne de nez, barbe d'épines sous le menton
    rig.add(r.tube(f"NasalRidge{k}", [(0, yy, width_at(SKULL, yy, 4) + 0.02)
                                      for yy in (-1.05, -1.4, -1.75)], [0.07, 0.08, 0.05],
                   segments=5), H, "bone_shade", **kw)
    rig.add(a.claw(f"NoseHorn{k}", (0, -1.55, width_at(SKULL, -1.55, 4)), (0, -0.4, 1), 0.3, 0.08,
                   curl=-0.2, segments=5), H, "horn", **kw)
    for i, xx in enumerate((-0.12, 0.0, 0.12)):
        rig.add(a.claw(f"Beard{k}{i}", (xx, -1.55 + abs(xx), -0.78), (xx * 2, 0.5, -1),
                       0.32 - abs(xx), 0.05, curl=0.15, segments=4), J, "horn", **kw)
    # Gorge de feu doré (visible gueule ouverte)
    rig.add(r.ico(f"Throat{k}", 0.2, subdivisions=2, location=(0, -0.45, -0.42),
                  scale=(1.3, 1.2, 0.5)), H, "glow", glow=True)
    teeth(rig, k, SKULL, JAW, -1.95, -0.4, 0.22, (1, 2), H, J, -0.32, -0.4, **kw)


def build_heads(rig):
    for key in NECKS:
        before = {o.name for o in bpy.context.scene.objects}
        build_head(rig, key)
        place(new_objects(before), head_matrix(key))


def build_necks(rig):
    for key, (pts, _, _) in NECKS.items():
        # Collier d'or hérissé sur le cou, juste sous la mâchoire (pas caché dedans)
        collar_c, tan = c.Chain(pts).at(0.72)
        rig.add(a.ring_around(f"Collar{key}", collar_c, tan, 0.33, 0.06, segments=14),
                f"Neck{key}2", "coin", part=f"Head{key}")
        side, up = a._basis(tan)
        for i in range(6):
            ang = 2 * math.pi * i / 6
            out = side * math.cos(ang) + up * math.sin(ang)
            rig.add(a.claw(f"CollarSpike{key}{i}", collar_c + out * 0.33, out + tan * 0.3, 0.22,
                           0.05, curl=0, segments=4), f"Neck{key}2", "horn", part=f"Head{key}")
        neck = c.Chain(pts)
        n = 9
        for i in range(n):
            t = i / (n - 1)
            p, tan = neck.at(t)
            bone = f"Neck{key}1" if t < 0.62 else f"Neck{key}2"
            size = 0.34 - 0.08 * t
            rig.add(a.vertebra(f"Neck{key}{i}", p, -tan, size, spine=0.55, lean=0.2,
                               transverse=i % 2 == 0), bone, "bone", part=f"Head{key}")
            if i < n - 1:
                q, tq = neck.at((i + 0.5) / (n - 1))
                rig.add(a.disc(f"NeckDisc{key}{i}", q, tq, size), bone, "disc", part=f"Head{key}")
            if i % 2 == 1:
                up = Vector((0, 0, 1))
                rig.add(a.claw(f"NeckSpike{key}{i}", p + up * size * 1.15, (0, 0.5, 1), 0.25, 0.06,
                               curl=-0.1, segments=4), bone, "horn", part=f"Head{key}")


# ---------------------------------------------------------------- corps

def build_spine(rig):
    back = c.Chain(BACK)
    for i in range(9):
        p, t = back.at(i / 8)
        bone = "Hips" if p.y > 0.0 else ("Spine" if p.y > -1.0 else "Chest")
        rig.add(a.vertebra(f"Back{i}", p, -t, 0.38, spine=0.75, lean=0.25), bone, "bone")
        if i < 8:
            q, tq = back.at((i + 0.5) / 8)
            rig.add(a.disc(f"BackDisc{i}", q, tq, 0.38), bone, "disc")
        if i % 2 == 0:
            tip = p + Vector((0, 0.08, 0.38 * 0.7 + 0.38 * 0.75 - 0.05))
            rig.add(a.claw(f"BackSpike{i}", tip, (0, 0.4, 1), 0.35, 0.08, curl=-0.1), bone, "horn")
    tail = c.Chain(TAIL)
    n = 24   # queue longue et enroulée : assez de vertèbres pour qu'elles se touchent
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(5, int(t * 5 * 0.999) + 1)}"
        size = 0.36 - 0.22 * t
        rig.add(a.vertebra(f"Tail{i}", p, tan, size, spine=0.6 - 0.25 * t, lean=-0.25,
                           transverse=i < 12), bone, "bone")
        if i < n - 1:
            q, tq = tail.at((i + 0.5) / (n - 1))
            rig.add(a.disc(f"TailDisc{i}", q, tq, size), bone, "disc")
        if i % 3 == 1:
            coin(rig, f"TailCoin{i}", p + Vector((0, 0, size * 0.55)), (0, 0, 1), bone,
                 radius=size * 0.35)
    # Bout de queue : massue de spirales dorées autour d'une gemme
    tip, tan = tail.at(1.0)
    rig.add(a.crystal("TailGem", tip + tan * 0.2, 0.18, 0.5), "Tail5", "glow", glow=True)
    for s in (-1, 1):
        rig.add(a.claw(f"TailSpike{s}", tip, tan + Vector((0, 0, 0)) + Vector((-tan.y, tan.x, 0)) * s
                       * 0.8, 0.45, 0.08, curl=0), "Tail5", "horn")


def build_ribcage(rig):
    back = c.Chain(BACK)
    for i in range(8):
        t = 0.12 + 0.82 * i / 7
        p, _ = back.at(t)
        bone = "Hips" if p.y > 0.0 else ("Spine" if p.y > -1.0 else "Chest")
        bulge = math.sin((i + 1) / 9 * math.pi)
        hw, depth = 0.8 + 0.4 * bulge, 1.0 + 0.4 * bulge
        for s in (-1, 1):
            rig.add(a.rib(f"Rib{i}{s}", p + Vector((0, 0, -0.08)), hw, depth, s, sweep=-0.2,
                          radius=0.09), bone, "bone")
            if i in (2, 5):
                coin(rig, f"RibCoin{i}{s}", p + Vector((s * hw * 0.97, -0.08, -depth * 0.45)),
                     (s, 0, 0), bone, radius=0.1)
    for i in range(6):
        y = -1.3 + i * 0.45
        for s in (-1, 1):
            rig.add(r.tube(f"Gastralia{i}{s}", [(0, y, 1.05), (s * 0.5, y + 0.1, 1.1),
                                                (s * 0.85, y + 0.18, 1.35)], [0.05, 0.05, 0.03],
                           segments=4), "Spine" if y < 0 else "Hips", "bone_shade")
    # Idole de cristal dorée, entourée de pièces en orbite
    rig.add(a.crystal("Heart", (0, -0.6, 1.55), 0.3, 0.85), "Spine", "glow", glow=True)
    for i in range(6):
        ang = 2 * math.pi * i / 6
        p = Vector((math.cos(ang) * 0.5, -0.6 + math.sin(ang) * 0.5, 1.55 + 0.12 * math.sin(2 * ang)))
        coin(rig, f"OrbitCoin{i}", p, (math.cos(ang), math.sin(ang), 0.4), "Spine", radius=0.09,
             float_ok=True)


def toes(rig, name, wrist, side_x, base_y, bone, count=5, spread=0.16, length=0.32):
    for i in range(count):
        dx = (i - (count - 1) / 2) * spread
        base = Vector((side_x + dx * 1.2, base_y, 0.15))
        rig.add(a.long_bone(f"{name}Meta{i}", wrist, base, 0.055, knob=1.5, condyles=False), bone,
                "bone")
        tip = base + Vector((dx * 0.8, -length, -0.04))
        rig.add(a.long_bone(f"{name}Phal{i}", base, tip, 0.045, knob=1.4, condyles=False), bone,
                "bone")
        rig.add(a.claw(f"{name}Claw{i}", tip, (dx, -1, -0.1), 0.25, 0.055, curl=0.35), bone, "horn")


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        sh, el, wr = Vector((s * 0.7, -1.5, 1.9)), Vector((s * 1.6, -1.7, 1.5)), \
            Vector((s * 1.75, -2.0, 0.35))
        rig.add(a.blade(f"Scapula{s}", (s * 0.65, -1.5, 2.0), (s * 0.7, -0.6, 2.55), 0.5, 0.12,
                        width_end=0.35, normal=(s, 0, 0.5)), "Chest", "bone")
        rig.add(a.long_bone(f"Humerus{s}", sh, el, 0.16), f"UpperArm_{side}", "bone")
        rig.add(a.long_bone(f"Radius{s}", el, wr, 0.13), f"Forearm_{side}", "bone")
        rig.add(a.claw(f"ElbowSpike{s}", el + Vector((s * 0.1, 0.1, 0.05)), (s * 0.5, 1, 0.4), 0.35,
                       0.08, curl=-0.1), f"Forearm_{side}", "horn")
        toes(rig, f"Hand{s}", wr, s * 1.8, -2.3, f"Hand_{side}")

        hip, kn, an = Vector((s * 0.7, 1.4, 1.9)), Vector((s * 1.7, 1.0, 1.4)), \
            Vector((s * 1.8, 1.5, 0.35))
        rig.add(a.blade(f"Ilium{s}", (s * 0.45, 0.6, 2.15), (s * 0.45, 2.2, 2.2), 0.4, 0.12,
                        width_end=0.32, mid=0.8, normal=(1, 0, 0.3)), "Hips", "bone")
        rig.add(r.ico(f"Acetabulum{s}", 0.22, subdivisions=1, location=hip), "Hips", "bone_shade")
        rig.add(a.long_bone(f"Femur{s}", hip, kn, 0.18), f"Thigh_{side}", "bone")
        coin(rig, f"FemurCoin{s}", hip.lerp(kn, 0.5) + Vector((0, 0, 0.17)), (0, 0, 1),
             f"Thigh_{side}", radius=0.1)
        rig.add(a.long_bone(f"Tibia{s}", kn, an, 0.14), f"Shin_{side}", "bone")
        rig.add(r.ico(f"Knee{s}", 0.17, subdivisions=1, location=kn), f"Shin_{side}", "bone_shade")
        toes(rig, f"Foot{s}", an, s * 1.85, 1.1, f"Foot_{side}", count=4, spread=0.18)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_heads(rig)
    build_necks(rig)
    build_spine(rig)
    build_ribcage(rig)
    build_legs(rig)
    return rig
