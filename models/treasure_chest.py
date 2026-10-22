"""Coffre au trésor (≈ 4.3 x 3 x 3.2 studs).

Corps et couvercle en planches, cerclages en fer rivetés, coins renforcés,
serrure dorée avec trou de serrure, poignées latérales et pieds.
"""
import math

from lib import roblox as r

COLORS = {
    "wood": "#9c6232",
    "wood_light": "#b57a45",
    "wood_dark": "#4a2e15",
    "iron": "#45464f",
    "iron_light": "#6b6d78",
    "gold": "#e8b730",
    "gold_dark": "#a87c12",
    "hole": "#111111",
}

W, D, H = 4.0, 2.6, 1.8   # corps
R = D / 2                 # rayon du couvercle
T = 0.12                  # épaisseur des planches
FOOT = 0.18               # hauteur des pieds


def rivet(pal, name, location):
    obj = r.ico(name, 0.045, subdivisions=1, location=location)
    pal.paint(obj, "iron_light")


def build_body(pal):
    z0 = FOOT
    core = r.box("Core", (W - 0.2, D - 0.2, H), location=(0, 0, z0 + H / 2))
    pal.paint(core, "wood_dark")

    rows = 3
    ph = H / rows
    for i in range(rows):
        z = z0 + ph * (i + 0.5)
        color = "wood" if i % 2 == 0 else "wood_light"
        for side in (-1, 1):
            front = r.box(f"PlankFB{i}{side}", (W - 0.02, T, ph - 0.05),
                          location=(0, side * (D / 2 - T / 2), z), bevel_width=0.025)
            pal.paint(front, color)
            lateral = r.box(f"PlankLR{i}{side}", (T, D - 2 * T - 0.02, ph - 0.05),
                            location=(side * (W / 2 - T / 2), 0, z), bevel_width=0.025)
            pal.paint(lateral, "wood_light" if color == "wood" else "wood")

    # Coins renforcés en fer (équerres) avec rivets
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (W / 2 + 0.015), sy * (D / 2 + 0.015)
            a = r.box(f"CornerA{sx}{sy}", (0.4, 0.05, H + 0.02),
                      location=(cx - sx * 0.19, cy, z0 + H / 2), bevel_width=0.012)
            b = r.box(f"CornerB{sx}{sy}", (0.05, 0.4, H + 0.02),
                      location=(cx, cy - sy * 0.19, z0 + H / 2), bevel_width=0.012)
            pal.paint(a, "iron")
            pal.paint(b, "iron")
            for k in range(3):
                z = z0 + 0.25 + k * (H - 0.5) / 2
                rivet(pal, f"RivA{sx}{sy}{k}", (cx - sx * 0.22, cy + sy * 0.03, z))
                rivet(pal, f"RivB{sx}{sy}{k}", (cx + sx * 0.03, cy - sy * 0.22, z))

            foot = r.box(f"Foot{sx}{sy}", (0.45, 0.45, FOOT),
                         location=(sx * (W / 2 - 0.2), sy * (D / 2 - 0.2), FOOT / 2),
                         bevel_width=0.04)
            pal.paint(foot, "iron")

    # Cerclages verticaux sur le corps (dans le prolongement de ceux du couvercle)
    for bx in (-W / 2 + 0.75, W / 2 - 0.75):
        for side in (-1, 1):
            band = r.box(f"BodyBand{bx}{side}", (0.3, 0.05, H),
                         location=(bx, side * (D / 2 + 0.02), z0 + H / 2), bevel_width=0.012)
            pal.paint(band, "iron")
            for k in range(3):
                rivet(pal, f"RivBand{bx}{side}{k}",
                      (bx, side * (D / 2 + 0.05), z0 + 0.3 + k * (H - 0.6) / 2))

    # Poignées latérales : platine + anneau
    for sx in (-1, 1):
        plate = r.box(f"HandlePlate{sx}", (0.05, 0.5, 0.3),
                      location=(sx * (W / 2 + 0.03), 0, z0 + H * 0.72), bevel_width=0.012)
        pal.paint(plate, "iron")
        handle = r.torus(f"Handle{sx}", 0.24, 0.04, segments=10, minor_segments=5,
                         arc=math.pi, location=(sx * (W / 2 + 0.08), 0, z0 + H * 0.72),
                         rotation=(math.radians(90), 0, 0))
        handle.data.transform(_flip_down())
        pal.paint(handle, "iron_light")


def _flip_down():
    from mathutils import Matrix
    return Matrix.Rotation(math.pi, 4, "Y")


def build_lid(pal):
    zc = FOOT + H          # axe du couvercle
    n = 7
    step = math.pi / n
    rp = R * math.cos(step / 2) - T / 2

    # Planches du couvercle disposées en arc
    for i in range(n):
        theta = step * (i + 0.5)
        chord = 2 * R * math.sin(step / 2) + 0.01
        plank = r.box(f"LidPlank{i}", (W - 0.02, chord, T),
                      location=(0, rp * math.cos(theta), zc + rp * math.sin(theta)),
                      rotation=(theta - math.pi / 2, 0, 0), bevel_width=0.02)
        pal.paint(plank, "wood" if i % 2 == 0 else "wood_light")

    # Flancs en demi-disque
    for sx in (-1, 1):
        cap = r.cylinder(f"LidCap{sx}", R - 0.02, T, segments=14,
                         location=(sx * (W / 2 - T / 2), 0, zc),
                         rotation=(0, math.radians(90), 0))
        r.cut_below(cap, 0)
        pal.paint(cap, "wood_light")

    # Cerclages en arc avec rivets
    for bx in (-W / 2 + 0.75, W / 2 - 0.75):
        arc = r.torus(f"LidBand{bx}", R + 0.01, 0.05, segments=14, minor_segments=4,
                      arc=math.pi, location=(bx, 0, zc),
                      rotation=(math.radians(90), 0, math.radians(90)))
        pal.paint(arc, "iron")
        flat = r.cylinder(f"LidBandFlat{bx}", R + 0.03, 0.3, segments=14,
                          location=(bx, 0, zc), rotation=(0, math.radians(90), 0))
        r.cut_below(flat, 0)
        pal.paint(flat, "iron")
        for k in range(5):
            a = math.pi * (k + 0.5) / 5
            rivet(pal, f"RivLid{bx}{k}",
                  (bx, (R + 0.06) * math.cos(a), zc + (R + 0.06) * math.sin(a)))

    # Bordure de fer à la jonction couvercle / corps
    for side in (-1, 1):
        rim = r.box(f"LidRim{side}", (W + 0.04, 0.06, 0.14),
                    location=(0, side * (D / 2 + 0.01), zc + 0.03), bevel_width=0.015)
        pal.paint(rim, "iron")


def build_lock(pal):
    zc = FOOT + H
    y = -D / 2 - 0.05
    plate = r.box("LockPlate", (0.7, 0.08, 0.8), location=(0, y, zc - 0.25),
                  bevel_width=0.04)
    pal.paint(plate, "gold")
    hasp = r.box("Hasp", (0.32, 0.08, 0.5), location=(0, y - 0.02, zc + 0.2),
                 bevel_width=0.03)
    pal.paint(hasp, "gold_dark")
    hole = r.cylinder("KeyholeTop", 0.07, 0.04, segments=8,
                      location=(0, y - 0.05, zc - 0.2), rotation=(math.radians(90), 0, 0))
    pal.paint(hole, "hole")
    slot = r.box("KeyholeSlot", (0.06, 0.04, 0.18), location=(0, y - 0.05, zc - 0.32))
    pal.paint(slot, "hole")
    for sx in (-1, 1):
        for sz in (-1, 1):
            stud = r.ico(f"LockStud{sx}{sz}", 0.04, subdivisions=1,
                         location=(sx * 0.26, y - 0.05, zc - 0.25 + sz * 0.31))
            pal.paint(stud, "gold_dark")


def build(pal):
    build_body(pal)
    build_lid(pal)
    build_lock(pal)
