"""Modélisation voxel (style MagicaVoxel) pour les créatures animables.

On remplit une grille de cubes avec des formes (sphères, capsules, profils…),
chaque voxel porte une couleur et un os. Le maillage final :
- ne garde que les faces visibles (un voxel collé à un voxel du même os cache sa face) ;
- fusionne les faces voisines de même nuance (greedy meshing) → peu de triangles ;
- crée un objet Blender par (os, lumineux) pour `lib.creature.finalize`.

Les faces entre deux os différents sont conservées : quand la mâchoire
s'ouvre, on ne voit pas de trou.

Couleurs : `shades()` décline chaque couleur en 3 nuances ; chaque voxel en
prend une au hasard (stable) → grain de matière. Les couleurs dont le nom
commence par « glow » vont dans le mesh lumineux (Neon dans Roblox).
"""
import colorsys
import math
import random
from collections import defaultdict

import bpy
import bmesh
from mathutils import Vector

SHADES = (("d", 0.88), ("", 1.0), ("l", 1.08))


def shades(colors):
    """{nom: hex} → palette avec nom, nom@d (sombre), nom@l (clair)."""
    out = {}
    for name, hexstr in colors.items():
        h = hexstr.lstrip("#")
        rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        hh, ll, ss = colorsys.rgb_to_hls(*rgb)
        for suffix, f in SHADES:
            r, g, b = colorsys.hls_to_rgb(hh, min(1.0, ll * f), ss)
            key = f"{name}@{suffix}" if suffix else name
            out[key] = "#%02x%02x%02x" % tuple(round(x * 255) for x in (r, g, b))
    return out


def is_glow(color):
    return color.startswith("glow")


def _hash(i, j, k, seed=0):
    return ((i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (seed * 2654435761)) & 0xFFFFFFFF


class Voxels:
    def __init__(self, size=0.25, seed=0):
        self.s = size
        self.seed = seed
        self.v = {}   # (i, j, k) -> [couleur, os]

    # ------------------------------------------------------------ remplissage

    def _fill(self, lo, hi, inside, color, bone, mode):
        s = self.s
        rng = [range(math.floor(lo[a] / s) - 1, math.floor(hi[a] / s) + 2) for a in range(3)]
        for i in rng[0]:
            x = (i + 0.5) * s
            for j in rng[1]:
                y = (j + 0.5) * s
                for k in rng[2]:
                    z = (k + 0.5) * s
                    if k < 0 or not inside(x, y, z):
                        continue
                    key = (i, j, k)
                    if mode == "add":
                        self.v[key] = [color, bone]
                    elif mode == "erase":
                        self.v.pop(key, None)
                    elif mode == "paint" and key in self.v:
                        self.v[key][0] = color
                        if bone:
                            self.v[key][1] = bone

    def ellipsoid(self, center, radii, color=None, bone=None, mode="add"):
        cx, cy, cz = center
        rx, ry, rz = (max(r, self.s * 0.55) for r in radii)

        def inside(x, y, z):
            return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1

        self._fill((cx - rx, cy - ry, cz - rz), (cx + rx, cy + ry, cz + rz), inside,
                   color, bone, mode)

    def sphere(self, center, radius, color=None, bone=None, mode="add"):
        self.ellipsoid(center, (radius, radius, radius), color, bone, mode)

    def capsule(self, a, b, ra, rb=None, color=None, bone=None, mode="add"):
        """Cylindre arrondi de a à b, rayon ra → rb (cône si rb petit)."""
        a, b = Vector(a), Vector(b)
        rb = ra if rb is None else rb
        ra, rb = max(ra, self.s * 0.55), max(rb, self.s * 0.55)
        ab = b - a
        l2 = ab.length_squared or 1e-9

        def inside(x, y, z):
            p = Vector((x, y, z))
            t = max(0.0, min(1.0, (p - a).dot(ab) / l2))
            r = ra + (rb - ra) * t
            return (p - (a + ab * t)).length_squared <= r * r

        m = max(ra, rb)
        lo = [min(a[i], b[i]) - m for i in range(3)]
        hi = [max(a[i], b[i]) + m for i in range(3)]
        self._fill(lo, hi, inside, color, bone, mode)

    def path(self, points, radii, color=None, bone=None, mode="add"):
        """Suite de capsules (os longs, côtes, cornes, queue…)."""
        if not isinstance(radii, (list, tuple)):
            radii = [radii] * len(points)
        for (a, ra), (b, rb) in zip(zip(points, radii), zip(points[1:], radii[1:])):
            self.capsule(a, b, ra, rb, color, bone, mode)

    def box(self, lo, hi, color=None, bone=None, mode="add"):
        self._fill(lo, hi, lambda x, y, z: all(lo[i] <= p <= hi[i] for i, p in
                                                enumerate((x, y, z))), color, bone, mode)

    def loft_y(self, sections, color=None, bone=None, mode="add"):
        """Volume à sections elliptiques le long de Y : [(y, demi-largeur, demi-hauteur, z)]."""
        sections = sorted(sections)

        def inside(x, y, z):
            if not sections[0][0] <= y <= sections[-1][0]:
                return False
            for a, b in zip(sections, sections[1:]):
                if a[0] <= y <= b[0]:
                    t = (y - a[0]) / ((b[0] - a[0]) or 1)
                    hw, hh, zc = (a[n] + (b[n] - a[n]) * t for n in (1, 2, 3))
                    return (x / hw) ** 2 + ((z - zc) / hh) ** 2 <= 1
            return False

        hw = max(s[1] for s in sections)
        lo = (-hw, sections[0][0], min(s[3] - s[2] for s in sections))
        hi = (hw, sections[-1][0], max(s[3] + s[2] for s in sections))
        self._fill(lo, hi, inside, color, bone, mode)

    def carve(self, center, radii, rim_color):
        """Creuse un trou (orbite, narine…) dont le fond est teinté `rim_color`."""
        self.ellipsoid(center, [r * 1.45 for r in radii], rim_color, mode="paint")
        self.ellipsoid(center, radii, mode="erase")

    # ------------------------------------------------------------ effets

    def surface(self, key):
        i, j, k = key
        return any((i + di, j + dj, k + dk) not in self.v
                   for di, dj, dk in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0),
                                      (0, 0, 1), (0, 0, -1)))

    def veins(self, colors, glow_color, density=0.06, scale=0.9):
        """Fissures de lave : motif ondulé sur la surface des voxels `colors`."""
        for key, val in self.v.items():
            if val[0] not in colors or not self.surface(key):
                continue
            x, y, z = (c * self.s * scale for c in key)
            n = math.sin(x * 1.7 + math.sin(z * 2.1)) + math.sin(y * 1.3 + math.sin(x * 1.9)) \
                + math.sin(z * 1.5 + math.sin(y * 2.3))
            if abs(n) < density * 3:
                val[0] = glow_color

    # ------------------------------------------------------------ maillage

    def shade(self, key, color):
        h = _hash(*key, self.seed) % 100
        if h < 18:
            return f"{color}@d"
        if h > 84:
            return f"{color}@l"
        return color

    def to_objects(self, rig):
        """Crée les objets Blender (un par os × lumineux), rattachés à leurs os."""
        groups = defaultdict(list)
        for key, (color, bone) in self.v.items():
            assert bone in rig.bones, f"voxel sans os valide : {key} {bone}"
            groups[(bone, is_glow(color))].append(key)

        objs = []
        for (bone, glow), keys in groups.items():
            obj = self._mesh(f"Vox_{bone}_{'glow' if glow else 'body'}", keys, bone, rig.pal)
            mat = rig.pal.glow_material if glow else rig.pal.material
            obj.data.materials.append(mat)
            obj["bone"] = bone
            obj["glow"] = glow
            objs.append(obj)
        return objs

    def _mesh(self, name, keys, bone, pal):
        s = self.s
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new("UVMap")
        verts = {}

        def vert(p):
            if p not in verts:
                verts[p] = bm.verts.new((p[0] * s, p[1] * s, p[2] * s))
            return verts[p]

        for axis in range(3):
            u, w = (axis + 1) % 3, (axis + 2) % 3
            for d in (1, -1):
                slices = defaultdict(dict)
                for key in keys:
                    n = list(key)
                    n[axis] += d
                    nb = self.v.get(tuple(n))
                    if nb is not None and nb[1] == bone:
                        continue
                    slices[key[axis]][(key[u], key[w])] = self.shade(key, self.v[key][0])
                for sl, cells in slices.items():
                    plane = sl + (1 if d > 0 else 0)
                    for (a, b, wa, wb, shade) in _greedy(cells):
                        corners = [(a, b), (a + wa, b), (a + wa, b + wb), (a, b + wb)]
                        if d < 0:
                            corners.reverse()
                        vs = []
                        for ca, cb in corners:
                            p = [0, 0, 0]
                            p[axis], p[u], p[w] = plane, ca, cb
                            vs.append(vert(tuple(p)))
                        face = bm.faces.new(vs)
                        uv = pal.uv(shade)
                        for loop in face.loops:
                            loop[uv_layer].uv = uv
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj


def _greedy(cells):
    """Fusionne des cases 2D de même valeur en rectangles : (a, b, largeur, hauteur, valeur)."""
    cells = dict(cells)
    out = []
    for (a, b) in sorted(cells):
        if (a, b) not in cells:
            continue
        val = cells[(a, b)]
        wa = 1
        while cells.get((a + wa, b)) == val:
            wa += 1
        wb = 1
        while all(cells.get((a + x, b + wb)) == val for x in range(wa)):
            wb += 1
        for x in range(wa):
            for y in range(wb):
                del cells[(a + x, b + y)]
        out.append((a, b, wa, wb, val))
    return out
