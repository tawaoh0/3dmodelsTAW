"""Sculpture de créatures « cartoon massives » avec des metaballs.

On empile des volumes (boules, capsules, ellipsoïdes) qui fusionnent en douceur
→ muscles gonflés, formes rondes, style des pets/boss Roblox.

- Les volumes de même couleur et même `group` fusionnent en UNE peau continue
  (le corps entier, sans coutures aux articulations).
- Chaque volume est lié à un os. Chaque sommet reçoit les poids des 2 os les
  plus proches, avec une transition douce : la peau se plie aux articulations.
- `group` sépare des volumes qui ne doivent pas fusionner (ex. la mâchoire,
  pour que la gueule puisse s'ouvrir).
- Couleurs « glow* » → mesh lumineux.
- Chaque peau est simplifiée (decimate) au budget de triangles demandé.

Les pièces dures (cornes pointues, griffes, dents) se font avec
`lib.creature.spike` et `rig.add`.
"""
import math
from collections import defaultdict

import bpy
from mathutils import Euler, Vector

from lib import roblox as r

# Une metaball de rayon 1 donne une sphère visible de rayon 0.575
K = 1 / 0.575


class _Elem:
    def __init__(self, kind, bone, a, b=None, radii=(1, 1, 1), rot=None, negative=False):
        self.kind, self.bone = kind, bone
        self.a = Vector(a)
        self.b = Vector(b) if b is not None else None
        self.radii = Vector(radii)
        self.rot = rot
        self.negative = negative

    def distance(self, p):
        """Distance approximative à la surface (en studs, ≤ 0 à l'intérieur)."""
        if self.kind == "capsule":
            ab = self.b - self.a
            t = max(0.0, min(1.0, (p - self.a).dot(ab) / (ab.length_squared or 1e-9)))
            return (p - (self.a + ab * t)).length - self.radii.x
        d = p - self.a
        if self.rot is not None:
            d = self.rot.inverted() @ d
        n = Vector((d.x / self.radii.x, d.y / self.radii.y, d.z / self.radii.z)).length
        return (n - 1) * min(self.radii)


class Sculpt:
    def __init__(self, rig, resolution=0.12):
        self.rig = rig
        self.resolution = resolution
        self.elems = defaultdict(list)   # (groupe, couleur) -> [_Elem]

    def _add(self, color, group, elem):
        assert elem.bone in self.rig.bones, f"os inconnu : {elem.bone}"
        self.elems[(group, color)].append(elem)

    def ball(self, bone, color, center, radius, group="body"):
        self._add(color, group, _Elem("ball", bone, center, radii=(radius,) * 3))

    def ellipsoid(self, bone, color, center, radii, rotation=(0, 0, 0), group="body"):
        rot = Euler(rotation).to_quaternion()
        self._add(color, group, _Elem("ellipsoid", bone, center, radii=radii, rot=rot))

    def capsule(self, bone, color, a, b, radius, group="body"):
        self._add(color, group, _Elem("capsule", bone, a, b, radii=(radius,) * 3))

    def limb(self, bone, color, points, radii, group="body"):
        """Suite de capsules de rayon variable. `bone` : un os ou une liste par segment."""
        if not isinstance(radii, (list, tuple)):
            radii = [radii] * len(points)
        bones = bone if isinstance(bone, (list, tuple)) else [bone] * (len(points) - 1)
        for i in range(len(points) - 1):
            a, b = Vector(points[i]), Vector(points[i + 1])
            ra, rb = radii[i], radii[i + 1]
            # Plusieurs boules le long du segment pour une conicité régulière
            n = max(2, math.ceil((b - a).length / (min(ra, rb) * 0.6)))
            for k in range(n + 1):
                t = k / n
                self.ball(bones[i], color, a.lerp(b, t), ra + (rb - ra) * t, group)

    def carve(self, bone, color, center, radius, group="body"):
        """Creuse (metaball négative) dans la peau `color` du `group`."""
        self._add(color, group, _Elem("ball", bone, center, radii=(radius,) * 3,
                                      negative=True))

    # ------------------------------------------------------------ conversion

    def build(self, budget, blend=0.35):
        """Convertit chaque peau en mesh peint et pondéré.

        `budget` : triangles max par peau : {"groupe:couleur" ou "couleur": n},
        avec une clé "*" par défaut.
        `blend` : largeur (studs) de la transition de poids entre deux os.
        """
        objs = []
        for (group, color), elems in self.elems.items():
            solid = [e for e in elems if not e.negative]
            if not solid:
                continue
            obj = self._convert(f"{group}_{color}", elems)
            _decimate(obj, budget.get(f"{group}:{color}", budget.get(color, budget.get("*"))))
            glow = color.startswith("glow")
            self.rig.pal.paint(obj, color, glow=glow)
            r.smooth(obj, 75)
            _weights(obj, solid, blend)
            objs.append(obj)
        return objs

    def _convert(self, name, elems):
        mb = bpy.data.metaballs.new(f"MB_{name}")
        mb.resolution = mb.render_resolution = self.resolution
        mb.threshold = 0.6
        holder = bpy.data.objects.new(f"MB_{name}", mb)
        bpy.context.scene.collection.objects.link(holder)
        for e in elems:
            if e.kind == "capsule":
                el = mb.elements.new(type="CAPSULE")
                d = e.b - e.a
                el.co = (e.a + e.b) / 2
                el.radius = e.radii.x * K
                el.size_x = d.length / 2
                if d.length > 1e-6:
                    el.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized())
            elif e.kind == "ellipsoid":
                el = mb.elements.new(type="ELLIPSOID")
                el.co = e.a
                m = max(e.radii)
                el.radius = m * K
                el.size_x, el.size_y, el.size_z = (e.radii.x / m, e.radii.y / m, e.radii.z / m)
                el.rotation = e.rot
            else:
                el = mb.elements.new(type="BALL")
                el.co = e.a
                el.radius = e.radii.x * K
            el.use_negative = e.negative
        dg = bpy.context.evaluated_depsgraph_get()
        mesh = bpy.data.meshes.new_from_object(holder.evaluated_get(dg))
        bpy.data.objects.remove(holder)
        bpy.data.metaballs.remove(mb)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj


def _weights(obj, elems, blend):
    """Poids de skinning : 2 os les plus proches, transition linéaire sur `blend`."""
    groups = {}
    for v in obj.data.vertices:
        best = {}
        for e in elems:
            d = e.distance(v.co)
            if d < best.get(e.bone, 1e9):
                best[e.bone] = d
        ranked = sorted(best.items(), key=lambda kv: kv[1])
        (b1, d1) = ranked[0]
        if len(ranked) == 1 or ranked[1][1] - d1 >= blend:
            weights = [(b1, 1.0)]
        else:
            b2, d2 = ranked[1]
            w2 = 0.5 * (1 - (d2 - d1) / blend)
            weights = [(b1, 1 - w2), (b2, w2)]
        for bone, w in weights:
            if bone not in groups:
                groups[bone] = obj.vertex_groups.new(name=bone)
            groups[bone].add([v.index], w, "REPLACE")


def _decimate(obj, max_tris):
    tris = r.triangle_count(obj)
    if not max_tris or tris <= max_tris:
        return
    mod = obj.modifiers.new("Decimate", "DECIMATE")
    mod.ratio = max_tris / tris
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.remove(mod)
    old = obj.data
    obj.data = new
    bpy.data.meshes.remove(old)
