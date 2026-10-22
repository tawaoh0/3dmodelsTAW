"""Créatures animables pour Roblox : squelette (armature), mesh « skinné »,
parties lumineuses séparées et script d'effets Luau.

Principe : chaque pièce est rattachée à UN os (poids 1.0, rigide). C'est
simple, robuste, et parfait pour des squelettes (chaque os bouge d'un bloc).

Le FBX exporté contient :
- `<nom>_Rig`  : l'armature (os Root à la racine, os FX_* pour les effets)
- `<nom>`      : le corps (os, cornes, griffes…)
- `<nom>_Glow` : les parties lumineuses (yeux, runes, cristaux) → Neon dans Roblox
"""
import math
import os

import bpy
from mathutils import Vector

from lib import roblox as r

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Rig:
    def __init__(self, pal):
        self.pal = pal
        self.bones = {}   # nom -> (tête, queue, parent)

    def bone(self, name, head, tail, parent=None):
        assert parent is None or parent in self.bones, f"os parent inconnu : {parent}"
        self.bones[name] = (Vector(head), Vector(tail), parent)
        return name

    def fx(self, name, location, parent):
        """Os d'effet (FX_*) : le script Roblox y attache flammes et particules."""
        loc = Vector(location)
        return self.bone(f"FX_{name}", loc, loc + Vector((0, 0, 0.3)), parent)

    def add(self, obj, bone, color, glow=False):
        """Peint `obj` et le rattache à l'os `bone`."""
        assert bone in self.bones, f"os inconnu : {bone}"
        self.pal.paint(obj, color, glow=glow)
        obj["bone"] = bone
        return obj


# ---------------------------------------------------------------- formes d'os

def long_bone(name, a, b, radius, segments=6):
    """Os long façon « dessin animé » : fût fin, extrémités renflées."""
    a, b = Vector(a), Vector(b)
    d = b - a
    pts = [a, a + d * 0.12, a + d * 0.5, b - d * 0.12, b]
    radii = [radius * 1.5, radius * 1.05, radius * 0.85, radius * 1.05, radius * 1.5]
    obj = r.tube(name, [tuple(p) for p in pts], radii, segments=segments)
    r.smooth(obj, 45)
    return obj


def spike(name, a, b, radius, segments=6, bend=(0, 0, 0)):
    """Pointe effilée (corne, griffe, dent), éventuellement courbée."""
    a, b = Vector(a), Vector(b)
    mid = (a + b) / 2 + Vector(bend)
    pts = [a, a.lerp(mid, 0.5), mid, mid.lerp(b, 0.5), b]
    radii = [radius, radius * 0.8, radius * 0.6, radius * 0.35, 0]
    return r.tube(name, [tuple(p) for p in pts], radii, segments=segments)


class Chain:
    """Courbe polyligne (colonne, queue, cou) pour placer vertèbres et côtes."""

    def __init__(self, points):
        self.points = [Vector(p) for p in points]
        self.lengths = [(b - a).length for a, b in zip(self.points, self.points[1:])]
        self.total = sum(self.lengths)

    def at(self, t):
        """Point et tangente à la fraction `t` (0 → 1) de la longueur."""
        d = max(0.0, min(1.0, t)) * self.total
        for i, seg in enumerate(self.lengths):
            if d <= seg or i == len(self.lengths) - 1:
                a, b = self.points[i], self.points[i + 1]
                return a.lerp(b, d / seg if seg else 0), (b - a).normalized()
            d -= seg


def vertebra(rig, name, center, tangent, size, bone, color, spine_height=None,
             spine_color=None):
    """Vertèbre : corps cylindrique + épine dorsale + apophyses latérales."""
    c, t = Vector(center), Vector(tangent)
    body = r.tube(name, [tuple(c - t * size * 0.45), tuple(c + t * size * 0.45)],
                  [size * 0.55, size * 0.55], segments=7)
    rig.add(body, bone, color)
    up = Vector((0, 0, 1))
    up = (up - t * up.dot(t)).normalized()
    h = size * 1.6 if spine_height is None else spine_height
    sp = spike(f"{name}_spine", c + up * size * 0.3, c + up * (size * 0.3 + h) + t * h * 0.25,
               size * 0.32, segments=4)
    rig.add(sp, bone, spine_color or color)
    side = t.cross(up).normalized()
    for s in (-1, 1):
        pr = r.tube(f"{name}_proc{s}", [tuple(c + up * size * 0.15),
                                        tuple(c + up * size * 0.25 + side * s * size * 1.0)],
                    [size * 0.18, size * 0.1], segments=4)
        rig.add(pr, bone, color)


def rib(name, top, half_width, depth, side, forward=Vector((0, -1, 0)), radius=0.08):
    """Côte : arc qui part de la colonne, s'écarte puis revient sous le ventre."""
    top = Vector(top)
    f = forward * 0.15
    pts = [top + Vector((side * 0.15, 0, 0)),
           top + Vector((side * half_width * 0.75, 0, -depth * 0.12)),
           top + Vector((side * half_width, 0, -depth * 0.45)) + f,
           top + Vector((side * half_width * 0.8, 0, -depth * 0.8)) + f * 2,
           top + Vector((side * half_width * 0.3, 0, -depth)) + f * 3]
    obj = r.tube(name, [tuple(p) for p in pts], [radius] * 4 + [radius * 0.6], segments=5)
    r.smooth(obj, 45)
    return obj


# ---------------------------------------------------------------- finalisation

def finalize(rig, name):
    """Fusionne les pièces (corps / lumineux), crée l'armature et la lie aux meshes."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in meshes:
        assert "bone" in o, f"pièce sans os : {o.name} (utiliser rig.add)"
        vg = o.vertex_groups.new(name=o["bone"])
        vg.add(range(len(o.data.vertices)), 1.0, "REPLACE")

    body_parts = [o for o in meshes if not o.get("glow")]
    glow_parts = [o for o in meshes if o.get("glow")]
    body = r.join(body_parts, name)
    glow = r.join(glow_parts, f"{name}_Glow") if glow_parts else None

    arm_data = bpy.data.armatures.new(f"{name}_Rig")
    arm = bpy.data.objects.new(f"{name}_Rig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for bname, (head, tail, parent) in rig.bones.items():
        eb = arm_data.edit_bones.new(bname)
        eb.head, eb.tail = head, tail
        if parent:
            eb.parent = arm_data.edit_bones[parent]
    bpy.ops.object.mode_set(mode="OBJECT")

    for mesh in (body, glow):
        if mesh is None:
            continue
        mesh.parent = arm
        mod = mesh.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
    return body, glow, arm


def pose(arm, rotations):
    """Applique une pose de test : {os: (rx, ry, rz) en degrés}."""
    for bname, rot in rotations.items():
        pb = arm.pose.bones[bname]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = tuple(math.radians(a) for a in rot)
    bpy.context.view_layer.update()


def export_fbx(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        if o is not None:
            o.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        object_types={"ARMATURE", "MESH"},
        apply_unit_scale=True,
        global_scale=1.0,
        axis_forward="-Z",
        axis_up="Y",
        mesh_smooth_type="FACE",
        use_triangles=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="COPY",
        embed_textures=True,
    )


def write_effects_script(name, colors, path):
    """Génère le script Luau d'effets avec les couleurs de la créature."""
    with open(os.path.join(ROOT, "lib", "CreatureEffects.server.lua")) as f:
        src = f.read()

    def rgb(hexstr):
        h = hexstr.lstrip("#")
        return ", ".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))

    src = (src.replace("{{NAME}}", name)
              .replace("{{GLOW}}", rgb(colors["glow"]))
              .replace("{{GLOW_HOT}}", rgb(colors["glow_hot"])))
    with open(path, "w") as f:
        f.write(src)
