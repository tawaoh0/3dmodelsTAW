"""Utilitaires communs pour générer des modèles Roblox avec Blender en headless.

Convention : 1 unité Blender = 1 stud Roblox. Dans le 3D Importer de Roblox,
choisir « File Dimensions : Studs ».

Couleurs : chaque modèle utilise une palette. Toutes les faces d'une même
couleur sont mappées (UV) sur un pixel de la texture `palette.png`, qui est
embarquée dans le FBX. Un seul matériau = un seul MeshPart léger dans Roblox.
"""
import math
import os

import bpy  # doit être importé avant bmesh (module pip `bpy`)
import bmesh

# Limite Roblox par MeshPart
MAX_TRIANGLES = 20000


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0


# ---------------------------------------------------------------- palette

class Palette:
    """Texture de palette : une couleur = une case de PALETTE_SIZE px."""

    CELL = 4

    def __init__(self, colors: dict):
        self.names = list(colors)
        self.colors = colors
        self.cols = max(1, math.ceil(math.sqrt(len(colors))))
        self.rows = math.ceil(len(colors) / self.cols)
        w, h = self.cols * self.CELL, self.rows * self.CELL
        img = bpy.data.images.new("palette", w, h, alpha=False)
        pixels = [0.0] * (w * h * 4)
        for i, name in enumerate(self.names):
            r, g, b = _srgb_hex(colors[name])
            cx, cy = i % self.cols, i // self.cols
            for y in range(cy * self.CELL, (cy + 1) * self.CELL):
                for x in range(cx * self.CELL, (cx + 1) * self.CELL):
                    p = (y * w + x) * 4
                    pixels[p:p + 4] = (r, g, b, 1.0)
        img.pixels = pixels
        self.image = img
        self.material = self._make_material()

    def uv(self, name):
        i = self.names.index(name)
        cx, cy = i % self.cols, i // self.cols
        return ((cx + 0.5) / self.cols, (cy + 0.5) / self.rows)

    def _make_material(self):
        mat = bpy.data.materials.new("PaletteMat")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = self.image
        tex.interpolation = "Closest"
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.8
        return mat

    def paint(self, obj, name):
        """Assigne la couleur `name` à toutes les faces de `obj`."""
        u, v = self.uv(name)
        mesh = obj.data
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="UVMap")
        for loop in mesh.uv_layers.active.data:
            loop.uv = (u, v)
        mesh.materials.clear()
        mesh.materials.append(self.material)

    def save(self, path):
        self.image.filepath_raw = path
        self.image.file_format = "PNG"
        self.image.save()


def _srgb_hex(hexstr):
    hexstr = hexstr.lstrip("#")
    return tuple(int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4))


# ---------------------------------------------------------------- primitives

def _link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _from_bmesh(name, bm, location=(0, 0, 0), rotation=(0, 0, 0)):
    from mathutils import Euler
    # La rotation est appliquée directement aux sommets
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                     matrix=Euler(rotation).to_matrix())
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    return _link(obj)


def box(name, size, location=(0, 0, 0), rotation=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    return _from_bmesh(name, bm, location, rotation)


def cylinder(name, radius, depth, segments=8, location=(0, 0, 0),
             rotation=(0, 0, 0), radius_top=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                          radius1=radius,
                          radius2=radius if radius_top is None else radius_top,
                          depth=depth)
    return _from_bmesh(name, bm, location, rotation)


def cone(name, radius, depth, segments=8, location=(0, 0, 0), rotation=(0, 0, 0)):
    return cylinder(name, radius, depth, segments, location, rotation, radius_top=0)


def ico(name, radius, subdivisions=1, location=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    return _from_bmesh(name, bm, location)


def cut_below(obj, z=0.0):
    """Coupe le mesh sous la hauteur locale `z` et referme le trou."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z),
                                 plane_no=(0, 0, 1), clear_inner=True)
    cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    bmesh.ops.holes_fill(bm, edges=cut_edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def jitter(obj, amount, seed=0):
    """Déforme légèrement les sommets pour un look low-poly organique."""
    import random
    rnd = random.Random(seed)
    for v in obj.data.vertices:
        v.co.x += rnd.uniform(-amount, amount)
        v.co.y += rnd.uniform(-amount, amount)
        v.co.z += rnd.uniform(-amount, amount)


def flat_shade(obj):
    for p in obj.data.polygons:
        p.use_smooth = False


# ---------------------------------------------------------------- finalisation

def join_all(name):
    """Fusionne tous les meshes de la scène en un seul objet `name`."""
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = obj.data.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj


def set_origin_bottom_center(obj):
    """Origine au centre de la base : le modèle se pose au sol dans Roblox."""
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    offset = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs))
    for v in obj.data.vertices:
        v.co.x -= offset[0]
        v.co.y -= offset[1]
        v.co.z -= offset[2]
    obj.location = (0, 0, 0)


def triangle_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def stats(obj):
    dims = obj.dimensions
    return {
        "triangles": triangle_count(obj),
        "size_studs": tuple(round(d, 2) for d in dims),
    }


def export_fbx(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        global_scale=1.0,
        axis_forward="-Z",
        axis_up="Y",
        mesh_smooth_type="FACE",
        use_triangles=True,
        path_mode="COPY",
        embed_textures=True,
    )


def export_obj(obj, path):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.wm.obj_export(
        filepath=path,
        export_selected_objects=True,
        forward_axis="NEGATIVE_Z",
        up_axis="Y",
        export_triangulated_mesh=True,
        path_mode="COPY",
    )


def render_preview(obj, path, resolution=512):
    """Rend un aperçu PNG (Cycles CPU, fonctionne sans GPU)."""
    scene = bpy.context.scene
    dims = obj.dimensions
    radius = (dims.length / 2) or 1.0
    center = (0, 0, dims.z / 2)

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    _link(cam)
    # Distance pour que la sphère englobante tienne dans le champ de vision
    from mathutils import Vector
    dist = radius / math.sin(cam_data.angle / 2) * 1.05
    offset = Vector((0.8, -1.0, 0.6)).normalized() * dist
    cam.location = Vector(center) + offset
    cam.rotation_euler = (-offset).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    _link(sun)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.7, 0.85, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)
