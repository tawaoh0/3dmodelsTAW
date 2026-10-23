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


def width_at(sections, y, idx=3):
    """Valeur interpolée d'une colonne de sections de crâne à la profondeur y
    (idx : 1 demi-larg. dessus, 2 joues, 3 bord dentaire, 4 z dessus, 5 z bas)."""
    for s0, s1 in zip(sections, sections[1:]):
        if s1[0] <= y <= s0[0]:
            t = (s0[0] - y) / (s0[0] - s1[0])
            return s0[idx] + (s1[idx] - s0[idx]) * t
    return sections[-1][idx]


def side_width(sections, y, z):
    """Demi-largeur réelle du crâne à la hauteur z (le profil se rétrécit vers le haut et le
    bas) : pour poser un anneau d'orbite, une bosse ou une veine SUR la paroi."""
    wt, wm, wb = (width_at(sections, y, i) for i in (1, 2, 3))
    zt, zb = width_at(sections, y, 4), width_at(sections, y, 5)
    zm = (zt + zb) / 2
    if z >= zm:
        return wm + (wt - wm) * min(1.0, (z - zm) / max(zt - zm, 1e-6))
    return wm + (wb - wm) * min(1.0, (zm - z) / max(zm - zb, 1e-6))


def loft_profile(name, sections, tip="round", tip_length=None, droop=0.15):
    """Crâne / mâchoire : loft de sections `profile_ring(*s)`.

    `tip="round"` (défaut) prolonge la dernière section par un bout de museau arrondi en
    dôme (sinon le museau « se coupe net » sur une face plate). `tip_length` : longueur du
    dôme (défaut : la moitié de la hauteur de la dernière section). `droop` : le bout
    s'abaisse légèrement (nez qui plonge, comme un vrai museau). `tip=None` : face plate.
    """
    rings = [profile_ring(*s) for s in sections]
    if tip == "round":
        y, wt, wm, wb, zt, zb = sections[-1]
        length = tip_length or (zt - zb) * 0.5
        direction = 1 if sections[-1][0] > sections[0][0] else -1
        zc = (zt + zb) / 2
        for u in (0.35, 0.6, 0.8, 0.93):
            sc = math.sqrt(1 - u * u)
            dz = -droop * (zt - zb) * u * u
            rings.append(profile_ring(y + direction * length * u, wt * sc, wm * sc, wb * sc,
                                      zc + (zt - zc) * sc + dz, zc + (zb - zc) * sc + dz))
        rings.append([(0, y + direction * length, zc - droop * (zt - zb))])
    obj = r.loft(name, rings)
    r.smooth(obj, 32)
    return obj


def hole_along(center, axis, side, ra, rb, depth=1.0, segments=12):
    """Cutter : tunnel elliptique selon un axe quelconque (narines creusées vers l'avant,
    fenêtres d'une collerette inclinée…). `ra` selon `side`, `rb` selon la 3e direction."""
    center, axis, side = Vector(center), Vector(axis).normalized(), Vector(side).normalized()
    other = axis.cross(side).normalized()
    rings = [[tuple(center + axis * d + side * math.cos(t) * ra + other * math.sin(t) * rb)
              for t in (2 * math.pi * k / segments for k in range(segments))]
             for d in (-depth, depth)]
    return r.loft("Cutter", rings)


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


def claw_point(base, direction, length, curl, t):
    """Point et tangente à la fraction `t` d'une `claw` courbée (pour y poser une pointe,
    une goutte, un anneau… exactement sur la courbe)."""
    base, d = Vector(base), Vector(direction).normalized()
    _, up = _basis(d)
    point = base + d * length * t - up * curl * length * t * t
    return point, (d * length - up * 2 * curl * length * t).normalized()


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


def spiral_points(base, side, back, up, coil=0.55, turns=1.1, spread=0.5, n=14):
    """Chemin d'une corne de bélier (voir `spiral_horn`) : liste de Vector, de la base à la
    pointe. Sert aussi à poser des bagues ou des gemmes exactement sur la corne."""
    base, side, back, up = (Vector(v) for v in (base, side, back, up))
    side, back, up = side.normalized(), back.normalized(), up.normalized()
    pts = []
    for k in range(n + 1):
        th = 2 * math.pi * turns * k / n
        rad = coil * (1 - 0.3 * k / n)
        pts.append(base + (up * math.sin(th) + back * (1 - math.cos(th))) * rad
                   + side * spread * k / n)
    return pts


def spiral_horn(name, base, side, back, up, radius, coil=0.55, turns=1.1, spread=0.5,
                ridges=7):
    """Corne de bélier enroulée : monte, part vers `back`, redescend et revient vers l'avant
    en s'écartant vers `side` pour ne pas se recouper. `coil` = rayon de l'enroulement.
    Rayon de la corne à la fraction t du chemin ≈ radius × (1 − t)^0.9."""
    pts = spiral_points(base, side, back, up, coil, turns, spread)
    return ridged_horn(name, [tuple(p) for p in pts], radius, ridges=ridges)


def ring_around(name, center, tangent, radius, thickness, segments=10):
    """Anneau (bague, collier, sertissage) autour d'un axe `tangent` passant par `center`."""
    center, t = Vector(center), Vector(tangent).normalized()
    side, up = _basis(t)
    pts = [tuple(center + (side * math.cos(a) + up * math.sin(a)) * radius)
           for a in (2 * math.pi * i / segments for i in range(segments))]
    return r.tube(name, pts, thickness, segments=4, closed=True)


def crystal(name, center, radius, height, sides=6):
    """Cristal facetté (bipyramide) : cœur, pointe de queue, gemmes."""
    c = Vector(center)
    ring = [(c.x + math.cos(2 * math.pi * k / sides) * radius,
             c.y + math.sin(2 * math.pi * k / sides) * radius, c.z) for k in range(sides)]
    return r.loft(name, [[tuple(c - Vector((0, 0, height * 0.45)))], ring,
                         [tuple(c + Vector((0, 0, height * 0.55)))]])


def smooth_path(points, samples):
    """Courbe lisse (Catmull-Rom) passant par `points` : liste de `samples` Vector régulièrement
    répartis. Pour tentacules, queues souples, cous de serpent."""
    pts = [Vector(p) for p in points]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    dense = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(20):
            t = k / 20
            dense.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t))
    dense.append(pts[-1])
    lengths = [0.0]
    for a_, b_ in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + (b_ - a_).length)
    out, j = [], 0
    for k in range(samples):
        target = lengths[-1] * k / (samples - 1)
        while j < len(lengths) - 2 and lengths[j + 1] < target:
            j += 1
        seg = lengths[j + 1] - lengths[j] or 1e-9
        out.append(dense[j].lerp(dense[j + 1], (target - lengths[j]) / seg))
    return out


def oriented(obj, location, normal):
    """Oriente un objet modélisé selon +Z vers `normal`, puis le place à `location`
    (balanes, ventouses, pièces…)."""
    rot = Vector((0, 0, 1)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(location)) @ rot)
    return obj


def rotate_obj(obj, axis, angle, pivot):
    """Fait tourner les sommets de `obj` autour de `pivot`."""
    pivot = Vector(pivot)
    m = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-pivot)
    obj.data.transform(m)
    return obj


# ---------------------------------------------------------------- ailes


def membrane(name, outline, thickness=0.05):
    """Membrane d'aile (2 faces, visible des deux côtés dans Roblox).

    `outline` : [(position, {os: poids})] ; triangulée en éventail depuis le
    1er point. Les poids sont posés directement (pas de `rig.add` d'os unique) :
    la membrane s'étire entre les doigts quand l'aile bouge.
    """
    import bmesh
    pts = [Vector(p) for p, _ in outline]
    normal = Vector()
    for i, p in enumerate(pts):            # normale de Newell
        q = pts[(i + 1) % len(pts)]
        normal += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x),
                          (p.x - q.x) * (p.y + q.y)))
    normal.normalize()
    bm = bmesh.new()
    front = [bm.verts.new(p + normal * thickness / 2) for p in pts]
    back = [bm.verts.new(p - normal * thickness / 2) for p in pts]
    n = len(pts)
    for i in range(1, n - 1):
        bm.faces.new((front[0], front[i], front[i + 1]))
        bm.faces.new((back[0], back[i + 1], back[i]))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], back[i], back[j], front[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    groups = {}
    for i, (_, weights) in enumerate(outline):
        for bone, w in weights.items():
            if bone not in groups:
                groups[bone] = obj.vertex_groups.new(name=bone)
            groups[bone].add([i, i + n], w, "REPLACE")
    return obj


def tattered_edge(a, b, wa, wb, toward, depth=0.35, notches=4, seed=0):
    """Points d'un bord de membrane festonné et déchiré entre deux pointes.

    Le bord se creuse vers `toward` (arc) avec des encoches irrégulières.
    Renvoie [(position, poids)] sans les extrémités.
    """
    import random
    rnd = random.Random(seed)
    a, b, toward = Vector(a), Vector(b), Vector(toward)
    out = []
    steps = notches * 2 + 1
    for k in range(1, steps):
        t = k / steps
        p = a.lerp(b, t)
        pull = math.sin(t * math.pi) * depth
        if k % 2 == 0:   # encoche : on creuse davantage
            pull += rnd.uniform(0.15, 0.4) * depth
        p = p.lerp(toward, pull / max(1e-6, (toward - p).length) * 1.0)
        w = {}
        for bone, val in wa.items():
            w[bone] = w.get(bone, 0) + val * (1 - t)
        for bone, val in wb.items():
            w[bone] = w.get(bone, 0) + val * t
        out.append((tuple(p), w))
    return out
