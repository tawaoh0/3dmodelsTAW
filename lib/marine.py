"""Pièces détaillées pour les créatures marines (et toute créature à nageoires / membranes).

Toutes les fonctions posent directement les pièces sur le rig (`rig.add` / membranes).
"""
import math
import random

from mathutils import Vector

from lib import anatomy as a
from lib import roblox as r


def along(poly, f):
    """Point à la fraction f (0 → 1) de la longueur d'une polyligne."""
    poly = [Vector(p) for p in poly]
    if len(poly) == 1:
        return poly[0]
    lengths = [(q - p).length for p, q in zip(poly, poly[1:])]
    d = max(0.0, min(1.0, f)) * sum(lengths)
    for (p, q), seg in zip(zip(poly, poly[1:]), lengths):
        if d <= seg or seg == lengths[-1]:
            return p.lerp(q, d / seg if seg else 0)
        d -= seg
    return poly[-1]


def fin(rig, name, root, edge, bone, part=None, rays=8, membrane="membrane",
        ray_color="bone_shade", spine_color="horn", tattered=True, leading_spine=True,
        glow_tips=True, radials=True, seed=0):
    """Nageoire détaillée.

    root : points de la racine (sur le corps), du bord d'attaque vers l'arrière.
    edge : points du bord libre, de la pointe d'attaque vers l'arrière.
    Couches : membrane au bord arrière déchiré, rayons articulés (nœuds), épine d'attaque à
    piques, radiaux à la racine (ancrage dans le corps), pointes lumineuses.
    """
    kw = dict(part=part) if part else {}
    root = [Vector(p) for p in root]
    edge = [Vector(p) for p in edge]
    # Bord libre déchiré entre les points du bord
    outline_edge = [edge[0]]
    for i, (p, q) in enumerate(zip(edge, edge[1:])):
        if tattered and i > 0:
            toward = along(root, (i + 0.5) / len(edge))
            outline_edge += [Vector(pt) for pt, _ in a.tattered_edge(p, q, {bone: 1}, {bone: 1},
                                                                     toward, depth=0.18,
                                                                     notches=1, seed=seed + i)]
        outline_edge.append(q)
    pts = [root[0]] + outline_edge + [root[-1]] + list(reversed(root[1:-1]))
    m = a.membrane(name, [(tuple(p), {bone: 1}) for p in pts], thickness=0.04)
    rig.pal.paint(m, membrane)
    if part:
        m["part"] = part
    # Rayons articulés
    for i in range(rays):
        f = (i + 0.5) / rays if not leading_spine else (i + 1) / (rays + 1)
        start, end = along(root, f), along(edge, f)
        end = start.lerp(end, 0.94)
        length = (end - start).length
        rad = max(0.022, min(0.05, length * 0.03))
        rig.add(r.tube(f"{name}Ray{i}", [tuple(start), tuple(end)], [rad, rad * 0.45],
                       segments=4), bone, ray_color, **kw)
        for j, t in enumerate((0.35, 0.65)):
            rig.add(r.ico(f"{name}Joint{i}{j}", rad * 1.5, subdivisions=1,
                          location=start.lerp(end, t)), bone, ray_color, **kw)
        if glow_tips and i % 2 == 0:
            rig.add(r.ico(f"{name}Tip{i}", rad * 1.3, subdivisions=1, location=end), bone, "glow",
                    glow=True)
        if radials:
            inward = (start - end).normalized()
            rig.add(r.tube(f"{name}Radial{i}", [tuple(start), tuple(start + inward * 0.22)],
                           [rad * 1.2, rad * 0.8], segments=4), bone, ray_color, **kw)
    # Épine d'attaque épaisse, hérissée de petites piques vers l'arrière
    if leading_spine:
        a0, a1 = root[0], edge[0]
        rig.add(r.tube(f"{name}Spine", [tuple(a0), tuple(a0.lerp(a1, 0.6)), tuple(a1)],
                       [0.07, 0.05, 0.02], segments=5), bone, spine_color, **kw)
        back = (along(root, 1.0) - a0).normalized()
        for j, t in enumerate((0.3, 0.55, 0.8)):
            p = a0.lerp(a1, t)
            rig.add(a.claw(f"{name}SpineBarb{j}", p, back + (a1 - a0).normalized() * 0.5,
                           0.14, 0.03, curl=0, segments=4), bone, spine_color, **kw)


def scar(rig, name, start, end, bone, width=0.08, seed=0, **kw):
    """Cicatrice / fissure lumineuse en zigzag entre deux points (posée sur une surface)."""
    rnd = random.Random(seed)
    start, end = Vector(start), Vector(end)
    d = end - start
    side = d.cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    pts = [start + d * (k / 4) + side * (width * rnd.uniform(-1, 1) if 0 < k < 4 else 0)
           for k in range(5)]
    rig.add(r.tube(name, [tuple(p) for p in pts], 0.022, segments=4), bone, "glow", glow=True)


def spiky_orbit(rig, name, center, axis, radius, bone, spikes=6, color="horn", rim="bone_shade",
                **kw):
    """Orbite renforcée : double anneau + couronne de petites piques rayonnantes."""
    center, axis = Vector(center), Vector(axis).normalized()
    rig.add(a.ring_around(f"{name}Rim", center, axis, radius, 0.045, segments=12), bone, rim, **kw)
    rig.add(a.ring_around(f"{name}Rim2", center + axis * 0.05, axis, radius * 1.18, 0.03,
                          segments=12), bone, rim, **kw)
    side, up = a._basis(axis)
    for i in range(spikes):
        ang = 2 * math.pi * i / spikes + 0.3
        out = side * math.cos(ang) + up * math.sin(ang)
        rig.add(a.claw(f"{name}Spike{i}", center + out * radius * 1.15, out + axis * 0.4,
                       radius * 0.7, 0.03, curl=0, segments=4), bone, color, **kw)


def scutes(rig, name, points, normals, bone, size=0.09, color="bone_shade", **kw):
    """Rangée d'écailles osseuses en losange posées sur une surface."""
    for i, (p, n) in enumerate(zip(points, normals)):
        obj = r.ico(f"{name}{i}", size, subdivisions=1, location=(0, 0, 0), scale=(1, 1.6, 0.4))
        a.oriented(obj, p, n)
        rig.add(obj, bone, color, **kw)


def hook(rig, name, base, direction, bone, chain=3, color="rust", **kw):
    """Hameçon rouillé planté, avec quelques maillons de chaîne qui pendent."""
    base, d = Vector(base), Vector(direction).normalized()
    rig.add(a.claw(f"{name}Hook", base, d, 0.45, 0.04, curl=0.8, segments=5), bone, color, **kw)
    eye = base - d * 0.08
    rig.add(a.ring_around(f"{name}Eye", eye, d, 0.06, 0.02, segments=8), bone, color, **kw)
    p = eye + Vector((0, 0, -0.08))
    for j in range(chain):
        axis = Vector((1, 0, 0)) if j % 2 == 0 else Vector((0, 1, 0))
        rig.add(a.ring_around(f"{name}Link{j}", p, axis, 0.07, 0.018, segments=8), bone, color,
                **kw)
        p = p + Vector((0.02, 0.02, -0.11))
