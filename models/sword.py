"""Épée (outil Roblox, ≈ 5 studs). Poignée en bas, lame vers le haut."""
from lib import roblox as r

COLORS = {
    "blade": "#cfd8dc",
    "edge": "#eceff1",
    "guard": "#ffb300",
    "grip": "#4e342e",
    "pommel": "#e53935",
}


def build(pal):
    grip = r.cylinder("Grip", 0.15, 1.2, segments=8, location=(0, 0, 0.75))
    pal.paint(grip, "grip")

    pommel = r.ico("Pommel", 0.25, subdivisions=1, location=(0, 0, 0.15))
    pal.paint(pommel, "pommel")

    guard = r.box("Guard", (1.6, 0.3, 0.25), location=(0, 0, 1.45))
    pal.paint(guard, "guard")

    blade = r.box("Blade", (0.45, 0.1, 3.2), location=(0, 0, 3.15))
    pal.paint(blade, "blade")

    # Pointe : cône à 4 côtés aplati à l'épaisseur de la lame
    tip = r.cone("Tip", 0.225, 0.6, segments=4, location=(0, 0, 5.05))
    for v in tip.data.vertices:
        v.co.y *= 0.05 / 0.225
    pal.paint(tip, "edge")
