"""Coffre au trésor (4 x 2.5 x 3 studs)."""
import math

from lib import roblox as r

COLORS = {
    "wood": "#8d5524",
    "wood_dark": "#5d3a1a",
    "gold": "#f4c430",
    "lock": "#c0c0c0",
}


def build(pal):
    w, d, h = 4.0, 2.5, 1.8
    body = r.box("Body", (w, d, h), location=(0, 0, h / 2))
    pal.paint(body, "wood")

    lid = r.cylinder("Lid", d / 2, w, segments=10, location=(0, 0, h),
                     rotation=(0, math.radians(90), 0))
    r.cut_below(lid, 0)  # demi-cylindre : on garde le dessus
    pal.paint(lid, "wood_dark")

    # Bandes dorées
    for x in (-w / 2 + 0.4, w / 2 - 0.4):
        band = r.box(f"Band{x}", (0.3, d + 0.08, h), location=(x, 0, h / 2))
        pal.paint(band, "gold")
        arc = r.cylinder(f"BandArc{x}", d / 2 + 0.04, 0.3, segments=10,
                         location=(x, 0, h), rotation=(0, math.radians(90), 0))
        r.cut_below(arc, 0)
        pal.paint(arc, "gold")

    lock = r.box("Lock", (0.5, 0.2, 0.6), location=(0, -d / 2 - 0.1, h - 0.1))
    pal.paint(lock, "lock")
