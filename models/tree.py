"""Arbre low-poly (≈ 12 studs de haut)."""
from lib import roblox as r

COLORS = {
    "trunk": "#6b4226",
    "leaves_dark": "#2e7d32",
    "leaves_light": "#66bb6a",
}


def build(pal):
    trunk = r.cylinder("Trunk", 0.6, 5, segments=7, location=(0, 0, 2.5), radius_top=0.4)
    r.jitter(trunk, 0.05, seed=1)
    pal.paint(trunk, "trunk")

    blobs = [
        ((0, 0, 6.5), 2.8, "leaves_dark"),
        ((1.4, 0.6, 8.2), 2.0, "leaves_light"),
        ((-1.2, -0.8, 8.0), 2.1, "leaves_dark"),
        ((0.2, 0.3, 9.8), 1.7, "leaves_light"),
    ]
    for i, (loc, radius, color) in enumerate(blobs):
        blob = r.ico(f"Leaves{i}", radius, subdivisions=1, location=loc)
        r.jitter(blob, radius * 0.12, seed=10 + i)
        pal.paint(blob, color)
