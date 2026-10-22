"""Pièces anatomiques de squelettes stylisés (style boss Roblox) : formes
nettes, os épais, articulations renflées, arêtes vives là où il faut.

Toutes les fonctions renvoient des objets Blender ; on les rattache ensuite
à un os du rig avec `rig.add(obj, os, couleur)`.
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import roblox as r

# ---------------------------------------------------------------- outils


def _basis(t):
    """Deux vecteurs perpendiculaires à `t` (le premier le plus « vertical » possible)."""
    t = Vector(t).normalized()
    up = Vector((0, 0, 1)) if abs(t.z) < 0.95 else Vector((0, 1, 0))
    side = t.cross(up).normalized()
    up = side.cross(t).normalized()
    return side, up


def cut(obj, cutters):
    """Découpe (booléen) `obj` avec les objets `cutters`, qui sont ensuite supprimés."""
    for c in cutters:
        mod = obj.modifiers.new("Cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = c
        c.hide_render = True
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    old = obj.data
    obj.data = mesh
    bpy.data.meshes.remove(old)
    for c in cutters:
        bpy.data.objects.remove(c)
    return obj


def hole_x(center, ry, rz, width=6.0, segments=12):
    """Cutter : tunnel elliptique traversant selon X (orbites, fenêtres du crâne)."""
    pts = []
    for x in (-width / 2, width / 2):
        pts.append([(center[0] + x, center[1] + math.cos(a) * ry, center[2] + math.sin(a) * rz)
                    for a in (2 * math.pi * k / segments for k in range(segments))])
    return r.loft("Cutter", pts)


def profile_ring(y, wt, wm, wb, zt, zb, pinch=0.1):
    """Section de crâne à 12 points : dessus plat, joues bombées, bord dentaire net."""
    h = zt - zb
    half = [(wt * 0.55, zt), (wt, zt - h * 0.12), (wm, zt - h * 0.5),
            (wb, zb + h * 0.12), (wb * 0.75, zb)]
    right = [(x, z) for x, z in half]
    left = [(-x, z) for x, z in reversed(half)]
    ring = [(0, zt + h * 0.03)] + right + [(0, zb + h * pinch)] + left
    return [(x, y, z) for x, z in ring]


def loft_profile(name, sections):
    """Crâne / mâchoire : loft de sections `profile_ring(*s)`."""
    obj = r.loft(name, [profile_ring(*s) for s in sections])
    r.smooth(obj, 32)
    return obj


# ---------------------------------------------------------------- os


def long_bone(name, a, b, radius, knob=1.6, segments=8, condyles=True):
    """Os long : fût légèrement cintré, épiphyses en double renflement (condyles).

    `condyles=False` pour les petits os (phalanges) : extrémités simplement renflées.
    """
    a, b = Vector(a), Vector(b)
    d = b - a
    side, _ = _basis(d)
    pts = [a + d * t for t in (0.0, 0.08, 0.22, 0.5, 0.78, 0.92, 1.0)]
    radii = [radius * 0.9, radius * knob, radius * 1.05, radius * 0.88, radius * 1.05,
             radius * knob, radius * 0.9]
    shaft = r.tube(name, [tuple(p) for p in pts], radii, segments=segments)
    r.smooth(shaft, 40)
    parts = [shaft]
    if not condyles:
        return shaft
    # Condyles : deux boules côte à côte à chaque extrémité
    for end, inward in ((a, d.normalized()), (b, -d.normalized())):
        for s in (-1, 1):
            k = r.ico(f"{name}_condyle", radius * knob * 0.78, subdivisions=1,
                      location=end + inward * radius * 0.5 + side * s * radius * 0.55)
            r.smooth(k, 60)
            parts.append(k)
    return r.join(parts, name)


def blade(name, a, b, width, thickness, width_end=None, normal=(1, 0, 0), bevel=0.04,
          mid=None):
    """Os plat (omoplate, épine de vertèbre, ilium) : lame effilée de a vers b.

    `normal` : direction de l'épaisseur. `mid` : largeur au milieu (forme de feuille).
    """
    a, b = Vector(a), Vector(b)
    d = (b - a)
    n = Vector(normal).normalized()
    w_dir = d.cross(n).normalized()
    width_end = width * 0.5 if width_end is None else width_end
    rings = []
    mid = (width + width_end) / 2 * 1.05 if mid is None else mid
    for t, w in ((0.0, width), (0.25, width + (mid - width) * 0.75), (0.5, mid),
                 (0.75, width_end + (mid - width_end) * 0.75), (1.0, width_end)):
        c = a + d * t
        th = thickness * (1 - 0.35 * t)
        rings.append([tuple(c + w_dir * sw * w / 2 + n * sn * th / 2)
                      for sw, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    obj = r.loft(name, rings)
    if bevel:
        r.bevel(obj, min(bevel, thickness * 0.3))
    r.smooth(obj, 35)
    return obj


def vertebra(name, center, tangent, size, spine=1.6, lean=0.35, transverse=True):
    """Vertèbre : corps cylindrique, disques, épine neurale en lame, apophyses."""
    c, t = Vector(center), Vector(tangent).normalized()
    side, up = _basis(t)
    parts = []
    body = r.tube(f"{name}_c", [tuple(c - t * size * 0.42), tuple(c + t * size * 0.42)],
                  [size * 0.5, size * 0.5], segments=8)
    r.smooth(body, 40)
    parts.append(body)
    # Arc neural + épine en lame inclinée vers l'arrière
    arch = r.tube(f"{name}_a", [tuple(c + up * size * 0.3), tuple(c + up * size * 0.75)],
                  [size * 0.3, size * 0.22], segments=5)
    parts.append(arch)
    if spine:
        top = c + up * (size * 0.7 + size * spine) - t * size * spine * lean
        parts.append(blade(f"{name}_s", c + up * size * 0.6, top, size * 0.75, size * 0.22,
                           width_end=size * 0.4, normal=side, bevel=0.02 if size > 0.3 else 0))
    if transverse:
        for s in (-1, 1):
            parts.append(blade(f"{name}_t{s}", c + up * size * 0.45,
                               c + up * size * 0.55 + side * s * size * 1.0,
                               size * 0.32, size * 0.14, width_end=size * 0.2, normal=up,
                               bevel=0))
    return r.join(parts, name)


def disc(name, center, tangent, size):
    """Disque intervertébral (couleur plus sombre, entre deux vertèbres)."""
    c, t = Vector(center), Vector(tangent).normalized()
    obj = r.tube(name, [tuple(c - t * size * 0.08), tuple(c + t * size * 0.08)],
                 [size * 0.44, size * 0.44], segments=6)
    return obj


def rib(name, root, half_width, depth, side, sweep=-0.35, radius=0.1, segments=6):
    """Côte : sort de la colonne, s'arrondit vers l'extérieur et redescend vers l'avant."""
    root = Vector(root)
    pts = []
    for k in range(8):
        t = k / 7
        a = t * math.pi * 0.95
        x = side * (0.12 + half_width * math.sin(a) * (1 - 0.25 * t))
        z = -depth * (1 - math.cos(a)) / 2
        pts.append(root + Vector((x, sweep * t * t, z)))
    radii = [radius * (1.25 - 0.55 * k / 7) for k in range(8)]
    obj = r.tube(name, [tuple(p) for p in pts], radii, segments=segments)
    r.smooth(obj, 45)
    return obj


def claw(name, base, direction, length, radius, curl=0.35, segments=6):
    """Griffe / corne / croc courbé(e) : pointe recourbée vers le bas (`curl`)."""
    base, d = Vector(base), Vector(direction).normalized()
    side, up = _basis(d)
    pts, radii = [], []
    for k in range(7):
        t = k / 6
        p = base + d * length * t - up * curl * length * t * t
        pts.append(tuple(p))
        radii.append(radius * (1 - t) ** 0.8 if k < 6 else 0)
    obj = r.tube(name, pts, radii, segments=segments)
    r.smooth(obj, 50)
    return obj


def ridged_horn(name, points, radius, ridges=6, depth=0.12, segments=8):
    """Corne démoniaque annelée qui suit `points`, effilée jusqu'à la pointe."""
    pts = [Vector(p) for p in points]
    # Rééchantillonnage fin le long du chemin
    dense = []
    n = 6 * (len(pts) - 1)
    for k in range(n + 1):
        f = k / n * (len(pts) - 1)
        i = min(int(f), len(pts) - 2)
        dense.append(pts[i].lerp(pts[i + 1], f - i))
    radii = []
    for k, _ in enumerate(dense):
        t = k / n
        base = radius * (1 - t) ** 0.9
        ring = 1 + depth * max(0.0, math.sin(t * ridges * math.pi * 2)) * (1 - t)
        radii.append(base * ring if k < n else 0)
    obj = r.tube(name, [tuple(p) for p in dense], radii, segments=segments)
    r.smooth(obj, 50)
    return obj


def crystal(name, center, radius, height, sides=6):
    """Cristal facetté (bipyramide) : cœur, pointe de queue, gemmes."""
    c = Vector(center)
    ring = [(c.x + math.cos(2 * math.pi * k / sides) * radius,
             c.y + math.sin(2 * math.pi * k / sides) * radius, c.z) for k in range(sides)]
    return r.loft(name, [[tuple(c - Vector((0, 0, height * 0.45)))], ring,
                         [tuple(c + Vector((0, 0, height * 0.55)))]])


def rotate_obj(obj, axis, angle, pivot):
    """Fait tourner les sommets de `obj` autour de `pivot`."""
    pivot = Vector(pivot)
    m = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-pivot)
    obj.data.transform(m)
    return obj
