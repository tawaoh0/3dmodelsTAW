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
        self.glow_material = self._make_material(glow=True)

    def uv(self, name):
        i = self.names.index(name)
        cx, cy = i % self.cols, i // self.cols
        return ((cx + 0.5) / self.cols, (cy + 0.5) / self.rows)

    def _make_material(self, glow=False):
        mat = bpy.data.materials.new("GlowMat" if glow else "PaletteMat")
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = self.image
        tex.interpolation = "Closest"
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.8
        if glow:
            # Émissif dans les aperçus ; dans Roblox → matériau Neon (script d'effets)
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 6.0
        return mat

    def paint(self, obj, name, glow=False):
        """Assigne la couleur `name` à toutes les faces de `obj`.

        `glow=True` : pièce lumineuse (yeux, runes…), exportée dans un mesh à part.
        """
        obj["glow"] = glow
        u, v = self.uv(name)
        mesh = obj.data
        if not mesh.uv_layers:
            mesh.uv_layers.new(name="UVMap")
        for loop in mesh.uv_layers.active.data:
            loop.uv = (u, v)
        mesh.materials.clear()
        mesh.materials.append(self.glow_material if glow else self.material)

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


def box(name, size, location=(0, 0, 0), rotation=(0, 0, 0), bevel_width=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    obj = _from_bmesh(name, bm, location, rotation)
    if bevel_width:
        bevel(obj, bevel_width)
    return obj


def loft(name, rings, location=(0, 0, 0), rotation=(0, 0, 0), closed=False, cap=True):
    """Relie une suite d'anneaux de points (même nombre de points chacun).

    Un anneau d'un seul point fait une pointe. `closed` relie le dernier
    anneau au premier (tore). `cap` ferme les extrémités.
    """
    bm = bmesh.new()
    vrings = [[bm.verts.new(p) for p in ring] for ring in rings]
    pairs = list(zip(vrings, vrings[1:]))
    if closed:
        pairs.append((vrings[-1], vrings[0]))
    for a, b in pairs:
        n = max(len(a), len(b))
        for i in range(n):
            j = (i + 1) % n
            if len(a) == 1:
                bm.faces.new((a[0], b[i], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[i], a[j], b[0]))
            else:
                bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap and not closed:
        for ring in (vrings[0], vrings[-1]):
            if len(ring) >= 3:
                bm.faces.new(ring)
    return _from_bmesh(name, bm, location, rotation)


def ring(radius, z=0.0, segments=8, center=(0, 0), noise=0.0, seed=0, scale=(1, 1)):
    """Anneau horizontal de points (pour `loft`)."""
    import random
    rnd = random.Random(seed)
    pts = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        rr = radius * (1 + rnd.uniform(-noise, noise))
        pts.append((center[0] + math.cos(a) * rr * scale[0],
                    center[1] + math.sin(a) * rr * scale[1], z))
    return pts


def tube(name, points, radius, segments=8, closed=False, cap=True):
    """Tube qui suit un chemin de points. `radius` : nombre ou liste par point
    (0 = pointe)."""
    from mathutils import Vector
    pts = [Vector(p) for p in points]
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    rings, normal = [], None
    for i, p in enumerate(pts):
        if closed:
            t = pts[(i + 1) % len(pts)] - pts[i - 1]
        else:
            t = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        t.normalize()
        if normal is None:
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            normal = t.cross(ref).normalized()
        else:
            normal = (normal - t * normal.dot(t)).normalized()
        binormal = t.cross(normal)
        if radii[i] <= 0:
            rings.append([tuple(p)])
            continue
        rings.append([tuple(p + (normal * math.cos(a) + binormal * math.sin(a)) * radii[i])
                      for a in (2 * math.pi * k / segments for k in range(segments))])
    return loft(name, rings, closed=closed, cap=cap)


def torus(name, major, minor, segments=16, minor_segments=6, arc=2 * math.pi,
          location=(0, 0, 0), rotation=(0, 0, 0)):
    """Tore (anneau) dans le plan XY. `arc` < 2π donne un arc ouvert."""
    full = abs(arc - 2 * math.pi) < 1e-6
    n = segments if full else segments + 1
    path = [(math.cos(arc * i / segments) * major, math.sin(arc * i / segments) * major, 0)
            for i in range(n)]
    obj = tube(name, path, minor, minor_segments, closed=full)
    obj.location = location
    if any(rotation):
        from mathutils import Euler
        obj.data.transform(Euler(rotation).to_matrix().to_4x4())
    return obj


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


def ico(name, radius, subdivisions=1, location=(0, 0, 0), scale=(1, 1, 1)):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
    return _from_bmesh(name, bm, location)


def bevel(obj, width, segments=1):
    """Biseaute toutes les arêtes (adoucit les angles des boîtes)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.bevel(bm, geom=bm.edges[:] + bm.verts[:], offset=width,
                    offset_type="OFFSET", segments=segments, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    bm.to_mesh(obj.data)
    bm.free()


def smooth(obj, angle=40):
    """Ombrage lisse, en gardant nettes les arêtes plus vives que `angle`°."""
    limit = math.radians(angle)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        e.smooth = e.is_manifold and e.calc_face_angle(0) <= limit
    bm.to_mesh(obj.data)
    bm.free()


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
    return join([o for o in bpy.context.scene.objects if o.type == "MESH"], name)


def join(objs, name):
    """Fusionne les objets `objs` en un seul objet `name`."""
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


def render_preview(obj, path, resolution=1024, dark=False, view=(0.8, -1.0, 0.6)):
    """Rend un aperçu PNG (Cycles CPU, fonctionne sans GPU).

    `dark=True` : fond sombre opaque, pour faire ressortir les parties lumineuses.
    `view` : direction (depuis le modèle) d'où regarde la caméra.
    `obj` : un objet ou une liste d'objets à cadrer ensemble.
    """
    from mathutils import Vector
    scene = bpy.context.scene
    objs = obj if isinstance(obj, (list, tuple)) else [obj]
    # Sommets réels (après déformation par l'armature) pour un cadrage serré
    dg = bpy.context.evaluated_depsgraph_get()
    corners = []
    for o in objs:
        ev = o.evaluated_get(dg)
        mesh = ev.to_mesh()
        step = max(1, len(mesh.vertices) // 4000)
        corners += [o.matrix_world @ mesh.vertices[i].co
                    for i in range(0, len(mesh.vertices), step)]
        ev.to_mesh_clear()
    lo = Vector([min(p[i] for p in corners) for i in range(3)])
    hi = Vector([max(p[i] for p in corners) for i in range(3)])
    center = (lo + hi) / 2

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    _link(cam)
    # Distance minimale pour que les 8 coins de la boîte englobante soient dans le cadre
    d = Vector(view).normalized()
    rot = (-d).to_track_quat("-Z", "Y")
    right, up = rot @ Vector((1, 0, 0)), rot @ Vector((0, 1, 0))
    tan = math.tan(cam_data.angle / 2)
    dist = max(max(abs((c - center).dot(right)), abs((c - center).dot(up))) / tan
               + (c - center).dot(d) for c in corners) * 1.04
    cam.location = center + d * dist
    cam.rotation_euler = rot.to_euler()
    scene.camera = cam

    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))
    _link(sun)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = (0.16, 0.16, 0.2, 1) if dark else (0.6, 0.7, 0.85, 1)
    world.node_tree.nodes["Background"].inputs["Color"].default_value = bg
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    scene.world = world
    if dark:
        sun_data.energy = 3.5
        # Lumière d'appoint pour lire les formes sur fond sombre
        fill_data = bpy.data.lights.new("Fill", "SUN")
        fill_data.energy = 2.0
        fill = bpy.data.objects.new("Fill", fill_data)
        fill.rotation_euler = (math.radians(60), 0, math.radians(200))
        _link(fill)

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 64
    scene.render.resolution_x = scene.render.resolution_y = resolution
    scene.render.film_transparent = not dark
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)
    if dark:
        bpy.data.objects.remove(fill)
