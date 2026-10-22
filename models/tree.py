"""Chêne low-poly détaillé (≈ 13 studs de haut).

Tronc noueux évasé à la base, racines apparentes, branches qui portent
des touffes de feuillage en trois tons, et quelques champignons au pied.
"""
import math
import random

from lib import roblox as r

COLORS = {
    "bark": "#6b4226",
    "bark_dark": "#4a2c18",
    "leaves_dark": "#2e6b30",
    "leaves": "#3f8f3a",
    "leaves_light": "#74b84f",
    "mushroom_cap": "#d84336",
    "mushroom_dot": "#fbeee0",
    "mushroom_stem": "#efe3c8",
    "grass": "#5a9e3a",
}

TRUNK_TOP = 7.0


def trunk_center(z):
    """Léger déhanchement du tronc."""
    return (0.25 * math.sin(z * 0.5), 0.15 * math.sin(z * 0.8 + 1))


def build_trunk(pal):
    rings = []
    profile = [(0.0, 1.25), (0.3, 0.95), (0.9, 0.78), (2.0, 0.68), (3.5, 0.6),
               (5.0, 0.52), (6.2, 0.45), (TRUNK_TOP, 0.38)]
    for i, (z, radius) in enumerate(profile):
        rings.append(r.ring(radius, z, segments=12, center=trunk_center(z),
                            noise=0.08, seed=i))
    trunk = r.loft("Trunk", rings)
    r.smooth(trunk, 35)
    pal.paint(trunk, "bark")

    # Racines qui plongent dans le sol
    rnd = random.Random(3)
    for i in range(6):
        a = 2 * math.pi * i / 6 + rnd.uniform(-0.25, 0.25)
        length = rnd.uniform(1.4, 2.0)
        dx, dy = math.cos(a), math.sin(a)
        path = [(dx * 0.5, dy * 0.5, 0.6),
                (dx * (0.5 + length * 0.4), dy * (0.5 + length * 0.4), 0.25),
                (dx * (0.5 + length * 0.8), dy * (0.5 + length * 0.8), 0.05),
                (dx * (0.5 + length), dy * (0.5 + length), -0.25)]
        root = r.tube(f"Root{i}", path, [0.36, 0.24, 0.14, 0.08], segments=6)
        r.smooth(root, 40)
        pal.paint(root, "bark_dark" if i % 2 else "bark")

    # Nœuds sur l'écorce
    for i, (z, a) in enumerate([(2.4, 0.6), (4.1, 2.7), (5.3, 4.5)]):
        cx, cy = trunk_center(z)
        rad = 0.62 - z * 0.03
        knot = r.ico(f"Knot{i}", 0.17, subdivisions=1, scale=(1, 1, 1.3),
                     location=(cx + math.cos(a) * rad, cy + math.sin(a) * rad, z))
        pal.paint(knot, "bark_dark")


# (angle autour du tronc, hauteur de départ, longueur, élévation)
BRANCHES = [(0.3, 4.6, 3.0, 0.55), (2.4, 5.2, 2.8, 0.6),
            (4.3, 5.6, 2.6, 0.7), (1.3, 6.4, 2.0, 0.85)]


def build_branches(pal):
    tips = []
    for i, (a, z, length, elev) in enumerate(BRANCHES):
        cx, cy = trunk_center(z)
        dx, dy = math.cos(a), math.sin(a)
        path = []
        for k in range(4):
            t = k / 3
            reach = length * t
            path.append((cx + dx * reach, cy + dy * reach,
                         z + length * elev * t + 0.4 * math.sin(t * math.pi)))
        branch = r.tube(f"Branch{i}", path, [0.3, 0.22, 0.15, 0.09], segments=7)
        r.smooth(branch, 40)
        pal.paint(branch, "bark")
        tips.append(path[-1])
    return tips


def build_foliage(pal, tips):
    rnd = random.Random(7)
    shades = ["leaves_dark", "leaves", "leaves_light"]
    clusters = []

    def add_cluster(center, radius, satellites):
        """Une touffe + de petites bosses à sa surface (silhouette irrégulière)."""
        clusters.append((center, radius))
        for _ in range(satellites):
            a = rnd.uniform(0, 2 * math.pi)
            e = rnd.uniform(-0.3, 1.0)
            d = radius * 0.85
            clusters.append(((center[0] + math.cos(a) * math.cos(e) * d,
                              center[1] + math.sin(a) * math.cos(e) * d,
                              center[2] + math.sin(e) * d * 0.85),
                             radius * rnd.uniform(0.4, 0.6)))

    # Grosse masse au sommet du tronc, puis une touffe au bout de chaque branche
    top = trunk_center(TRUNK_TOP)
    add_cluster((top[0], top[1], TRUNK_TOP + 2.0), 2.4, 7)
    add_cluster((top[0] + 0.3, top[1] - 0.2, TRUNK_TOP + 3.9), 1.7, 4)
    for (x, y, z) in tips:
        add_cluster((x, y, z + 0.5), rnd.uniform(1.5, 1.8), 4)

    for i, (loc, radius) in enumerate(clusters):
        # Les touffes du haut sont plus claires (lumière du soleil)
        shade = shades[min(2, int((loc[2] - 6) / 2.5) + rnd.randint(0, 1))]
        blob = r.ico(f"Leaves{i}", radius, subdivisions=2 if radius > 1.2 else 1,
                     location=loc, scale=(1, 1, 0.85))
        r.jitter(blob, radius * 0.12, seed=100 + i)
        pal.paint(blob, shade)


def build_ground_details(pal):
    # Champignons
    for i, (x, y, s) in enumerate([(1.7, -1.3, 1.6), (2.2, -0.6, 1.1), (-1.6, -1.6, 1.3)]):
        stem = r.cylinder(f"MushStem{i}", 0.09 * s, 0.4 * s, segments=8,
                          location=(x, y, 0.2 * s), radius_top=0.07 * s)
        pal.paint(stem, "mushroom_stem")
        cap = r.ico(f"MushCap{i}", 0.26 * s, subdivisions=2,
                    location=(x, y, 0.4 * s), scale=(1, 1, 0.75))
        r.cut_below(cap, 0)
        r.smooth(cap, 60)
        pal.paint(cap, "mushroom_cap")
        for k in range(4):
            a = k * math.pi / 2 + 0.4
            dot = r.ico(f"MushDot{i}{k}", 0.045 * s, subdivisions=1,
                        location=(x + math.cos(a) * 0.15 * s, y + math.sin(a) * 0.15 * s,
                                  0.4 * s + 0.13 * s), scale=(1, 1, 0.5))
            pal.paint(dot, "mushroom_dot")

    # Touffes d'herbe (brins en cônes inclinés)
    rnd = random.Random(11)
    for t, (x, y) in enumerate([(-1.7, 0.9), (0.9, 1.7), (-0.6, -1.9), (2.0, 0.6)]):
        for b in range(5):
            a = rnd.uniform(0, 2 * math.pi)
            lean = rnd.uniform(0.15, 0.35)
            h = rnd.uniform(0.4, 0.7)
            blade = r.tube(f"Grass{t}{b}",
                           [(x, y, 0), (x + math.cos(a) * lean, y + math.sin(a) * lean, h)],
                           [0.06, 0.0], segments=3)
            pal.paint(blade, "grass")


def build(pal):
    build_trunk(pal)
    tips = build_branches(pal)
    build_foliage(pal, tips)
    build_ground_details(pal)
