"""Boîte à outils du pack « Insectes géants » : exosquelette ajouré en plaques d'os.

Un insecte n'a pas d'os internes : on traite l'exosquelette comme un squelette — anneaux de
plaques séparées (tergites dessus, sternites dessous) avec des jours entre elles qui laissent
voir les organes lumineux, pattes articulées en segments d'os, mandibules à dents.
Couleurs attendues dans COLORS : chitin, chitin_dark, horn, tooth, glow.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import marine as mr
from lib import roblox as r


def basis(axis, up=(0, 0, 1)):
    """Axe normalisé, dos (perpendiculaire à l'axe, vers `up`) et côté."""
    axis, up = Vector(axis).normalized(), Vector(up)
    dorsal = up - axis * axis.dot(up)
    if dorsal.length < 1e-4:
        dorsal = Vector((0, 1, 0)) - axis * axis.y
    dorsal.normalize()
    return axis, dorsal, axis.cross(dorsal).normalized()


def plate(rig, name, center, axis, rx, rz, length, bone, color="chitin", up=(0, 0, 1), start=-105, end=105,
          thickness=0.05, rim="chitin_dark", n=9, **kw):
    """Plaque d'exosquelette en arc (tergite) autour de l'axe du corps, bord ourlé."""
    center = Vector(center)
    axis, dorsal, side = basis(axis, up)
    pts = [center + side * rx * math.sin(math.radians(d)) + dorsal * rz * math.cos(math.radians(d))
           for d in (start + (end - start) * k / (n - 1) for k in range(n))]
    rig.add(a.band(name, pts, length, thickness, up=tuple(axis), offset=0.5), bone, color, **kw)
    if rim:
        rig.add(r.tube(f"{name}Rim", [tuple(p + axis * length * 0.5) for p in pts], thickness * 0.7, segments=4), bone,
                rim, **kw)
    return pts


def ring_segment(rig, name, center, axis, rx, rz, length, bone, up=(0, 0, 1), color="chitin", under="chitin_dark",
                 spikes=0, **kw):
    """Anneau complet : tergite + sternite séparés par des jours latéraux, épines dorsales."""
    plate(rig, f"{name}Terg", center, axis, rx, rz, length, bone, color, up=up, start=-110, end=110, **kw)
    plate(rig, f"{name}Stern", center, axis, rx * 0.85, rz * 0.8, length * 0.8, bone, under, up=up, start=135, end=225,
          n=5, rim=None, **kw)
    axis_, dorsal, side = basis(axis, up)
    for k in range(spikes):
        sx = 0 if spikes == 1 else (k / (spikes - 1) * 2 - 1)
        p = Vector(center) + dorsal * rz + side * rx * 0.5 * sx
        rig.add(a.claw(f"{name}Spike{k}", p, dorsal + side * sx * 0.5 - axis_ * 0.3, rz * 0.9, 0.04, curl=0, segments=4),
                bone, "horn", **kw)


def leg_chain(rig, name, pts, bones, radius, color="chitin", joint="chitin_dark", claw="horn", spines=True, **kw):
    """Patte articulée : segments d'os, rotules, épines, griffe tarsale double."""
    pts = [Vector(p) for p in pts]
    for j in range(len(pts) - 1):
        rad = radius * (1 - 0.18 * j)
        bone = bones[min(j, len(bones) - 1)]
        rig.add(a.long_bone(f"{name}Seg{j}", pts[j], pts[j + 1], rad, condyles=False, segments=5), bone, color, **kw)
        rig.add(r.ico(f"{name}Joint{j}", rad * 1.25, subdivisions=1, location=pts[j]), bone, joint, **kw)
        if spines and j >= 1:
            d = (pts[j + 1] - pts[j]).normalized()
            out = d.cross(Vector((0, 0, 1)))
            if out.length < 1e-3:
                out = Vector((1, 0, 0))
            for f in (0.35, 0.7):
                rig.add(a.claw(f"{name}Spine{j}{f}", pts[j].lerp(pts[j + 1], f), out.normalized() * 0.5 + d * 0.8 + Vector((0, 0, 0.3)),
                               rad * 2.2, rad * 0.35, curl=0, segments=4), bone, claw, **kw)
    tip, d = pts[-1], (pts[-1] - pts[-2]).normalized()
    for sx in (-1, 1):
        rig.add(a.claw(f"{name}Claw{sx}", tip, d + Vector((0.4 * sx, 0, -0.6)), radius * 2.0, radius * 0.4, curl=0.5, segments=4),
                bones[-1], claw, **kw)


def compound_eye(rig, name, center, radius, normal, bone, **kw):
    """Œil composé lumineux serti, facettes en relief."""
    center, normal = Vector(center), Vector(normal).normalized()
    rig.add(r.ico(name, radius, subdivisions=2, location=center), bone, "glow", glow=True)
    rig.add(a.ring_around(f"{name}Rim", center - normal * radius * 0.3, normal, radius * 1.02, radius * 0.16, segments=12),
            bone, "chitin_dark", **kw)
    side, up = a._basis(normal)
    for k in range(6):
        ang = 2 * math.pi * k / 6
        p = center + normal * radius * 0.82 + (side * math.cos(ang) + up * math.sin(ang)) * radius * 0.5
        rig.add(r.ico(f"{name}Facet{k}", radius * 0.13, subdivisions=1, location=p), bone, "chitin_dark", **kw)


def mandible(rig, name, base, tip, inward, bone, width=0.14, teeth=4, color="chitin", **kw):
    """Mandibule en faucille : deux lames qui se courbent vers l'intérieur, dents pleines côté interne."""
    base, tip, inward = Vector(base), Vector(tip), Vector(inward).normalized()
    mid = base.lerp(tip, 0.5) - inward * (base - tip).length * 0.18
    up = (tip - base).cross(inward).normalized()
    rig.add(a.blade(f"{name}A", base, mid, width, width * 0.45, width_end=width * 0.8, normal=up), bone, color, **kw)
    rig.add(a.blade(f"{name}B", mid, tip, width * 0.8, width * 0.4, width_end=width * 0.15, normal=up), bone, color, **kw)
    rig.add(a.claw(f"{name}Tip", tip, (tip - mid).normalized() + inward * 0.6, width * 1.6, width * 0.3, curl=0, segments=4),
            bone, "horn", **kw)
    for k in range(teeth):
        p = base.lerp(mid, 0.4 + 0.3 * k) if k < 2 else mid.lerp(tip, 0.2 + 0.3 * (k - 2))
        p = p + inward * width * 0.35
        rig.add(mr.tooth(f"{name}Tooth{k}", p, p + inward * width * (0.9 - 0.1 * k), width * 0.55, width * 0.3, up, curl=0.05),
                bone, "tooth", **kw)


def antenna(rig, name, points, bone, radius=0.03, club=None, **kw):
    """Antenne annelée ; `club` = rayon d'une massue lumineuse au bout."""
    pts = a.smooth_path(points, 10)
    rig.add(r.tube(f"{name}", [tuple(p) for p in pts], [radius * (1 - 0.05 * k) for k in range(10)], segments=4), bone,
            "chitin_dark", **kw)
    for k in range(2, 10, 2):
        rig.add(a.ring_around(f"{name}Ring{k}", pts[k], pts[min(k + 1, 9)] - pts[k - 1], radius * 1.4, radius * 0.4,
                              segments=6), bone, "chitin", **kw)
    if club:
        rig.add(r.ico(f"{name}Club", club, subdivisions=1, location=pts[-1], scale=(1, 1, 1.5)), bone, "glow", glow=True)


def organs(rig, name, center, size, bone, n=3):
    """Organes lumineux visibles à travers les jours de l'exosquelette."""
    center = Vector(center)
    for k in range(n):
        off = Vector((0.25 * math.cos(2.1 * k), 0.35 * math.sin(1.7 * k), 0.15 * math.cos(k))) * size
        rig.add(a.crystal(f"{name}{k}", center + off, size * (0.32 if k == 0 else 0.22), size * (1.1 if k == 0 else 0.8),
                          sides=5), bone, "glow", glow=True)
