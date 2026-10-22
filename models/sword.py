"""Épée de chevalier (outil Roblox, ≈ 5.5 studs). Poignée en bas, lame vers le haut.

Lame à section hexagonale avec gouttière, garde courbée avec gemme,
poignée en cuir tressé et pommeau serti.
"""
import math

from lib import roblox as r

COLORS = {
    "blade": "#cfd8dc",
    "fuller": "#90a4ae",
    "gold": "#e8b730",
    "gold_dark": "#a87c12",
    "leather": "#4e342e",
    "leather_dark": "#2e1d18",
    "gem": "#d32f2f",
    "gem_blue": "#1e88e5",
}

GUARD_Z = 1.55   # hauteur de la garde
BLADE_LEN = 3.6


def blade_section(width, thick, z):
    """Section hexagonale : tranchants sur les côtés, méplats devant/derrière."""
    e = width * 0.22
    return [(-width / 2, 0, z), (-width / 2 + e, -thick / 2, z),
            (width / 2 - e, -thick / 2, z), (width / 2, 0, z),
            (width / 2 - e, thick / 2, z), (-width / 2 + e, thick / 2, z)]


def build(pal):
    # --- Lame
    z0 = GUARD_Z + 0.1
    rings = [blade_section(0.5, 0.11, z0),
             blade_section(0.48, 0.11, z0 + 0.25),
             blade_section(0.44, 0.10, z0 + BLADE_LEN * 0.6),
             blade_section(0.40, 0.09, z0 + BLADE_LEN)]
    rings.append([(0, 0, z0 + BLADE_LEN + 0.55)])  # pointe
    blade = r.loft("Blade", rings)
    pal.paint(blade, "blade")

    # Gouttière (rainure centrale) sur les deux faces
    for side in (-1, 1):
        fuller = r.box(f"Fuller{side}", (0.1, 0.02, BLADE_LEN * 0.65),
                       location=(0, side * 0.05, z0 + 0.25 + BLADE_LEN * 0.325),
                       bevel_width=0.008)
        pal.paint(fuller, "fuller")

    # --- Garde : barre courbée vers la lame, extrémités en boule
    path = [(x, 0, GUARD_Z + 0.22 * (abs(x) / 0.85) ** 2)
            for x in [-0.85 + 0.17 * i for i in range(11)]]
    radii = [0.07 + 0.05 * (1 - abs(p[0]) / 0.85) for p in path]
    guard = r.tube("Guard", path, radii, segments=8)
    r.smooth(guard, 50)
    pal.paint(guard, "gold")
    for side in (-1, 1):
        knob = r.ico(f"GuardKnob{side}", 0.11, subdivisions=2,
                     location=(side * 0.88, 0, GUARD_Z + 0.24))
        r.smooth(knob, 80)
        pal.paint(knob, "gold")

    # Bloc central de la garde avec une gemme de chaque côté
    block = r.box("GuardBlock", (0.42, 0.26, 0.34),
                  location=(0, 0, GUARD_Z + 0.02), bevel_width=0.04)
    pal.paint(block, "gold_dark")
    for side in (-1, 1):
        gem = r.ico(f"Gem{side}", 0.1, subdivisions=1,
                    location=(0, side * 0.13, GUARD_Z + 0.02), scale=(1, 0.5, 1.3))
        pal.paint(gem, "gem")

    # --- Poignée en cuir avec lanières enroulées
    grip_bottom, grip_top = 0.35, GUARD_Z - 0.17
    grip = r.cylinder("Grip", 0.12, grip_top - grip_bottom, segments=10,
                      location=(0, 0, (grip_top + grip_bottom) / 2))
    r.smooth(grip, 50)
    pal.paint(grip, "leather")
    n_wraps = 7
    for i in range(n_wraps):
        z = grip_bottom + 0.08 + i * (grip_top - grip_bottom - 0.16) / (n_wraps - 1)
        wrap = r.torus(f"Wrap{i}", 0.125, 0.025, segments=12, minor_segments=4,
                       location=(0, 0, z), rotation=(math.radians(12), 0, 0))
        pal.paint(wrap, "leather_dark")

    # Viroles dorées aux deux extrémités de la poignée
    for i, z in enumerate((grip_top + 0.02, grip_bottom - 0.02)):
        ferrule = r.cylinder(f"Ferrule{i}", 0.15, 0.1, segments=10, location=(0, 0, z))
        r.bevel(ferrule, 0.02)
        pal.paint(ferrule, "gold")

    # --- Pommeau serti d'une gemme bleue
    pommel = r.ico("Pommel", 0.22, subdivisions=2, location=(0, 0, 0.18),
                   scale=(1, 0.75, 1))
    r.smooth(pommel, 80)
    pal.paint(pommel, "gold")
    for side in (-1, 1):
        pgem = r.ico(f"PommelGem{side}", 0.08, subdivisions=1,
                     location=(0, side * 0.16, 0.18), scale=(1, 0.5, 1))
        pal.paint(pgem, "gem_blue")
