"""T-Rex squelette infernal en voxels (≈ 17 studs de long, 8 de haut) — créature animable.

Os calcinés parcourus de fissures de lave, cornes démoniaques, orbites
creusées avec yeux de braise, cœur de cristal dans la cage thoracique.
Os du rig : Root, Hips, Spine, Neck, Head, Jaw, Tail1-4, Thigh/Shin/Foot_L/R,
UpperArm/Forearm_L/R, + FX_* pour les flammes (yeux, cœur, bout de queue).
"""
from mathutils import Vector

from lib import creature as c
from lib import voxel as v

COLORS = v.shades({
    "bone": "#b0a294",
    "bone_dark": "#6e5f56",
    "horn": "#5a1e1a",
    "claw": "#1a1010",
    "socket": "#140606",
    "tooth": "#d8c8a8",
    "glow": "#ff3010",
    "glow_hot": "#ffb030",
})

# Pose de test pour l'aperçu : gueule ouverte, tête levée, queue qui balance, pas en avant
TEST_POSE = {
    "Jaw": (30, 0, 0),
    "Neck": (-8, 0, 0),
    "Tail2": (0, 0, 15),
    "Tail3": (0, 0, 15),
    "Thigh_L": (-25, 0, 0),
    "Shin_L": (20, 0, 0),
}

# Crâne : (y, demi-largeur, demi-hauteur, z centre). Le museau pointe vers -Y.
SKULL = [(-6.9, 0.38, 0.36, 5.8), (-6.3, 0.55, 0.5, 5.85), (-5.4, 0.72, 0.65, 5.95),
         (-4.5, 0.9, 0.82, 6.05), (-3.8, 0.95, 0.88, 6.1), (-3.3, 0.75, 0.72, 6.1)]
JAW = [(-6.7, 0.36, 0.2, 4.95), (-5.6, 0.6, 0.26, 4.9), (-4.5, 0.74, 0.3, 4.95),
       (-3.7, 0.72, 0.32, 5.1)]
TAIL = [(0, 1.0, 4.5), (0, 3.5, 4.25), (0, 6.0, 3.7), (0, 8.3, 3.1), (0, 10.3, 2.5)]


def interp(sections, y):
    sections = sorted(sections)
    for a, b in zip(sections, sections[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return tuple(a[k] + (b[k] - a[k]) * t for k in (1, 2, 3))
    return sections[-1][1:]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Hips", (0, 0.6, 4.5), (0, -0.8, 4.65), "Root")
    rig.bone("Spine", (0, -0.8, 4.65), (0, -2.3, 4.9), "Hips")
    rig.bone("Neck", (0, -2.3, 4.9), (0, -3.4, 6.0), "Spine")
    rig.bone("Head", (0, -3.4, 6.0), (0, -6.6, 6.0), "Neck")
    rig.bone("Jaw", (0, -3.6, 5.3), (0, -6.6, 4.95), "Head")
    parent = "Hips"
    for i in range(4):
        parent = rig.bone(f"Tail{i + 1}", TAIL[i], TAIL[i + 1], parent)
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Thigh_{side}", (s * 0.85, 0.5, 4.2), (s * 1.05, -0.4, 2.5), "Hips")
        rig.bone(f"Shin_{side}", (s * 1.05, -0.4, 2.5), (s * 1.05, 0.6, 1.0), f"Thigh_{side}")
        rig.bone(f"Foot_{side}", (s * 1.05, 0.6, 1.0), (s * 1.05, -0.8, 0.2), f"Shin_{side}")
        rig.bone(f"UpperArm_{side}", (s * 0.6, -2.5, 4.0), (s * 0.85, -2.9, 3.3), "Spine")
        rig.bone(f"Forearm_{side}", (s * 0.85, -2.9, 3.3), (s * 0.8, -3.4, 3.5),
                 f"UpperArm_{side}")
        rig.fx(f"Eye{side}", (s * 0.85, -4.25, 6.35), "Head")
    rig.fx("Heart", (0, -1.4, 3.75), "Spine")
    rig.fx("TailTip", (0, 10.9, 2.4), "Tail4")


def build_skull(vx):
    vx.loft_y(SKULL, "bone", "Head")
    vx.loft_y(JAW, "bone", "Jaw")
    # Arcade sourcilière massive
    for s in (-1, 1):
        vx.ellipsoid((s * 0.62, -4.2, 6.75), (0.38, 0.55, 0.22), "bone_dark", "Head")

    for s in (-1, 1):
        # Orbites creusées, yeux de braise au fond
        vx.carve((s * 0.78, -4.25, 6.35), (0.38, 0.36, 0.34), "socket")
        vx.ellipsoid((s * 0.62, -4.25, 6.35), (0.2, 0.2, 0.2), "glow_hot", "Head")
        vx.ellipsoid((s * 0.7, -4.25, 6.35), (0.12, 0.28, 0.26), "glow", "Head", mode="paint")
        # Fenêtres du crâne (temporale, antorbitale) et narines
        vx.carve((s * 0.85, -3.55, 6.15), (0.3, 0.32, 0.4), "socket")
        vx.carve((s * 0.66, -5.3, 5.95), (0.26, 0.5, 0.26), "socket")
        vx.carve((s * 0.25, -6.85, 5.95), (0.14, 0.2, 0.14), "socket")

        # Grandes cornes démoniaques, pointes incandescentes
        horn = [(s * 0.55, -3.75, 6.7), (s * 0.95, -3.4, 7.3), (s * 1.35, -2.8, 7.75),
                (s * 1.6, -2.15, 7.85)]
        vx.path(horn, [0.3, 0.24, 0.16, 0.1], "horn", "Head")
        vx.capsule(horn[-1], (s * 1.75, -1.8, 7.75), 0.1, 0.06, "glow", "Head")
        # Rangée de petites cornes sur la joue
        for k, y in enumerate((-3.6, -3.25)):
            vx.capsule((s * 0.8, y, 5.7), (s * 1.15, y + 0.3, 5.6 - k * 0.1), 0.13, 0.06,
                       "horn", "Head")

        # Dents : rangée du haut vers le bas, du bas vers le haut
        y = -6.5
        while y < -4.0:
            hw, hh, zc = interp(SKULL, y)
            x = s * hw * 0.78
            top = zc - hh * 0.6
            long = 0.55 if abs(y + 5.3) < 0.2 else 0.4
            vx.capsule((x, y, top), (x, y, top - long), 0.09, 0.04, "tooth", "Head")
            jhw, jhh, jzc = interp(JAW, y + 0.12)
            jx = s * jhw * 0.75
            vx.capsule((jx, y + 0.12, jzc + jhh * 0.5), (jx, y + 0.12, jzc + jhh * 0.5 + 0.35),
                       0.08, 0.04, "tooth", "Jaw")
            y += 0.36

    # Rune lumineuse sur le front : trait central + deux points
    vx.box((-0.09, -5.3, 6.5), (0.09, -4.6, 7.0), "glow", "Head", mode="paint")
    for y in (-5.6, -4.3):
        vx.box((-0.09, y - 0.09, 6.5), (0.09, y + 0.09, 7.0), "glow", "Head", mode="paint")


def build_spine(vx):
    back = c.Chain([(0, 0.8, 4.55), (0, -0.8, 4.7), (0, -2.3, 4.95)])
    n = 8
    for i in range(n):
        t = i / (n - 1)
        p, tan = back.at(t)
        bone = "Hips" if p.y > -0.8 else "Spine"
        vx.ellipsoid(p, (0.3, 0.2, 0.28), "bone", bone)
        h = 0.7 + 0.5 * (1 - abs(t - 0.4))
        vx.capsule(p + Vector((0, 0, 0.2)), p + Vector((0, 0.15, 0.2 + h)), 0.13, 0.08,
                   "bone_dark", bone)
        vx.capsule(p + Vector((0, 0.15, 0.2 + h)), p + Vector((0, 0.25, 0.4 + h)), 0.08, 0.05,
                   "horn", bone)

    neck = c.Chain([(0, -2.3, 4.95), (0, -2.9, 5.5), (0, -3.35, 5.95)])
    for i in range(4):
        p, _ = neck.at(i / 3)
        vx.ellipsoid(p, (0.38, 0.26, 0.34), "bone", "Neck")
        vx.capsule(p, p + Vector((0, 0.1, 0.6)), 0.13, 0.07, "bone_dark", "Neck")
        vx.capsule(p + Vector((0, 0.1, 0.6)), p + Vector((0, 0.15, 0.8)), 0.07, 0.04, "horn",
                   "Neck")

    # Moelle épinière continue : relie les vertèbres entre elles
    vx.capsule((0, 0.8, 4.55), (0, -0.8, 4.7), 0.16, 0.16, "bone_dark", "Hips")
    vx.capsule((0, -0.8, 4.7), (0, -2.3, 4.95), 0.16, 0.16, "bone_dark", "Spine")
    vx.path([(0, -2.3, 4.95), (0, -2.9, 5.5), (0, -3.35, 5.95)], 0.17, "bone_dark", "Neck")
    for i in range(4):
        vx.capsule(TAIL[i], TAIL[i + 1], 0.16 - 0.025 * i, 0.14 - 0.025 * i, "bone_dark",
                   f"Tail{i + 1}")

    tail = c.Chain(TAIL)
    n = 17
    for i in range(n):
        t = i / (n - 1)
        p, tan = tail.at(t)
        bone = f"Tail{min(4, int((p.y - TAIL[0][1]) / 2.33) + 1)}"
        size = 0.32 - 0.2 * t
        vx.ellipsoid(p, (size, size * 0.7, size), "bone", bone)
        vx.capsule(p, p + Vector((0, 0.15, size * 2.4)), size * 0.4, size * 0.2, "horn", bone)
        if i < 12:
            vx.capsule(p, p + Vector((0, 0.3, -size * 2.2)), size * 0.35, size * 0.15,
                       "bone_dark", bone)
    # Pointe de queue : lame de cristal
    tip, tan = tail.at(1.0)
    vx.capsule(tip, tip + tan * 1.0, 0.3, 0.06, "glow", "Tail4")
    vx.capsule(tip, tip + tan * 0.5, 0.16, 0.1, "glow_hot", "Tail4")


def build_ribcage(vx):
    back = c.Chain([(0, 0.8, 4.55), (0, -0.8, 4.7), (0, -2.3, 4.95)])
    n = 7
    for i in range(n):
        t = 0.3 + 0.65 * i / (n - 1)
        p, _ = back.at(t)
        bulge = 1 - abs(i - 3) / 4
        bone = "Hips" if p.y > -0.8 else "Spine"
        w, d = 0.8 + 0.55 * bulge, 1.4 + 0.7 * bulge
        for s in (-1, 1):
            pts = [p + Vector((s * 0.2, 0, -0.1)),
                   p + Vector((s * w * 0.8, 0, -d * 0.12)),
                   p + Vector((s * w, -0.1, -d * 0.45)),
                   p + Vector((s * w * 0.8, -0.25, -d * 0.8)),
                   p + Vector((s * w * 0.3, -0.4, -d))]
            vx.path(pts, 0.13, "bone", bone)
    # Cœur de cristal infernal
    vx.ellipsoid((0, -1.4, 3.75), (0.45, 0.45, 0.65), "glow", "Spine")
    vx.ellipsoid((0, -1.4, 3.75), (0.25, 0.25, 0.4), "glow_hot", "Spine")
    for dx, dz in ((0.6, 0.35), (-0.6, 0.1), (0.15, -0.85)):
        vx.capsule((dx * 0.6, -1.4, 3.75 + dz * 0.6), (dx, -1.45, 3.75 + dz + 0.15), 0.1, 0.06,
                   "glow", "Spine")


def build_pelvis(vx):
    for s in (-1, 1):
        vx.box((s * 0.3 - 0.12, -0.7, 4.3), (s * 0.3 + 0.12, 1.6, 5.15), "bone", "Hips")
        vx.sphere((s * 0.85, 0.5, 4.2), 0.34, "bone_dark", "Hips")
        vx.capsule((s * 0.3, 0.0, 4.3), (s * 0.15, -0.9, 2.7), 0.16, 0.13, "bone", "Hips")
        vx.capsule((s * 0.3, 1.0, 4.3), (s * 0.12, 1.9, 3.1), 0.15, 0.1, "bone", "Hips")
    vx.ellipsoid((0, -1.0, 2.6), (0.32, 0.6, 0.2), "bone_dark", "Hips")


def build_leg(vx, s, side):
    hip, knee, ankle = Vector((s * 0.85, 0.5, 4.2)), Vector((s * 1.05, -0.4, 2.5)), \
        Vector((s * 1.05, 0.6, 1.0))
    thigh, shin, foot = f"Thigh_{side}", f"Shin_{side}", f"Foot_{side}"
    vx.path([hip, hip.lerp(knee, 0.5), knee], [0.4, 0.3, 0.34], "bone", thigh)
    vx.ellipsoid(hip.lerp(knee, 0.5) + Vector((s * 0.3, 0, 0)), (0.08, 0.2, 0.2), "glow", thigh,
                 mode="paint")
    vx.sphere(knee, 0.38, "bone_dark", shin)
    vx.path([knee, knee.lerp(ankle, 0.5), ankle], [0.3, 0.22, 0.26], "bone", shin)
    vx.sphere(ankle, 0.3, "bone_dark", foot)
    for k, dx in enumerate((-0.32, 0.0, 0.32)):
        base = Vector((s * 1.05 + dx, -0.35, 0.3))
        tip = base + Vector((dx * 0.5, -0.55 + abs(dx) * 0.4, -0.08))
        vx.path([ankle, base, tip], [0.17, 0.15, 0.13], "bone", foot)
        vx.capsule(tip, tip + Vector((dx * 0.2, -0.45, -0.15)), 0.12, 0.05, "claw", foot)


def build_arm(vx, s, side):
    shoulder, elbow, wrist = Vector((s * 0.6, -2.5, 4.0)), Vector((s * 0.85, -2.9, 3.3)), \
        Vector((s * 0.8, -3.4, 3.5))
    vx.capsule((s * 0.6, -1.9, 4.75), shoulder, 0.14, 0.12, "bone", "Spine")
    vx.capsule(shoulder, elbow, 0.13, 0.12, "bone", f"UpperArm_{side}")
    vx.capsule(elbow, wrist, 0.12, 0.1, "bone", f"Forearm_{side}")
    for dx in (-0.1, 0.1):
        tip = wrist + Vector((dx, -0.3, -0.05))
        vx.capsule(wrist, tip, 0.08, 0.07, "bone", f"Forearm_{side}")
        vx.capsule(tip, tip + Vector((0, -0.2, -0.18)), 0.08, 0.05, "claw", f"Forearm_{side}")


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    vx = v.Voxels(size=0.18, seed=7)
    build_skull(vx)
    build_spine(vx)
    build_ribcage(vx)
    build_pelvis(vx)
    for s, side in ((1, "L"), (-1, "R")):
        build_leg(vx, s, side)
        build_arm(vx, s, side)
    vx.veins({"bone"}, "glow", density=0.018)
    vx.to_objects(rig)
    return rig
