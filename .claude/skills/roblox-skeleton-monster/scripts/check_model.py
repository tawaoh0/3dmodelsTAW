"""Contrôle automatique d'une créature, AVANT de regarder les images.

Usage (depuis la racine du projet) :
    <python> check_model.py <modele>

Vérifie :
- pièces flottantes : chaque pièce doit toucher (à TOL près) une autre pièce (les lueurs
  suspendues — œil au centre d'une orbite, éclats autour du cœur — et les pièces marquées
  `obj["float_ok"] = True`, ex. pièces d'or en orbite, sont seulement signalées) ;
- couleurs : toutes les couleurs utilisées existent dans COLORS, `glow` et `glow_hot` présents ;
- os : chaque pièce est rattachée à un os qui existe ;
- budget : triangles par pièce Roblox (≤ 20 000) ;
- détail de la tête : nombre de pièces rattachées aux os Head*/Jaw*, par tête (HeadA, HeadB…).

Code de sortie 1 s'il y a un problème bloquant. Les pièces signalées sont listées avec leur
position : corriger leur placement (souvent une rotation autour du mauvais pivot, ou un
point posé sur une droite au lieu de la courbe d'une corne : voir `anatomy.claw_point`).
"""
import importlib
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.getcwd())
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from lib import roblox  # noqa: E402

TOL = 0.12          # studs : distance max entre une pièce et sa voisine la plus proche
MAX_TRIS = 20000
HEAD_PREFIXES = ("Head", "Jaw")   # Head, HeadA, JawB… : une tête par suffixe
MIN_HEAD_PIECES = 45


def world_mesh(obj):
    mesh = obj.data
    verts = [obj.matrix_world @ v.co for v in mesh.vertices]
    polys = [tuple(p.vertices) for p in mesh.polygons]
    return verts, polys


def main():
    name = sys.argv[1]
    module = importlib.import_module(f"models.{name}")
    problems, warnings, infos = [], [], []

    colors = module.COLORS
    for key in ("glow", "glow_hot"):
        if key not in colors:
            problems.append(f"COLORS ne contient pas « {key} » (requis par le script d'effets)")

    roblox.reset_scene()
    pal = roblox.Palette(colors)
    rig = module.build(pal)
    bpy.context.view_layer.update()   # sinon matrix_world des pièces posées avec location= est périmée
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]

    # Os et pièces Roblox
    tris_by_part = defaultdict(int)
    head_pieces = defaultdict(int)
    for o in objs:
        bone = o.get("bone")
        groups = [g.name for g in o.vertex_groups]
        for b in ([bone] if bone else groups):
            if b not in rig.bones:
                problems.append(f"{o.name} : os inconnu « {b} »")
        if not bone and not groups:
            problems.append(f"{o.name} : aucun os (utiliser rig.add, ou des poids pour une membrane)")
        part = "_Glow" if o.get("glow") else (o.get("part") or "corps")
        tris_by_part[part] += roblox.triangle_count(o)
        for b in ([bone] if bone else groups):
            for prefix in HEAD_PREFIXES:
                if b and b.startswith(prefix):
                    head_pieces[b[len(prefix):]] += 1
                    break
            else:
                continue
            break
    for part, tris in sorted(tris_by_part.items()):
        flag = "OK" if tris <= MAX_TRIS else "TROP"
        print(f"  pièce {part:<10} {tris:>6} triangles  {flag}")
        if tris > MAX_TRIS:
            problems.append(f"pièce {part} : {tris} triangles > {MAX_TRIS} (alléger ou répartir avec part=)")
    if not head_pieces:
        warnings.append("aucune pièce rattachée à un os Head*/Jaw* : nommer les os de tête ainsi")
    for key, n in sorted(head_pieces.items()):
        label = f"tête {key}" if key else "tête"
        print(f"  pièces de {label} : {n}")
        if n < MIN_HEAD_PIECES:
            warnings.append(f"{label} peu détaillée ({n} pièces < {MIN_HEAD_PIECES}) : "
                            "voir « Densité de détails » dans style-guide.md")

    # Pièces flottantes : BVH global, chaque pièce doit avoir une autre pièce à moins de TOL
    all_verts, all_polys, owner = [], [], []
    for i, o in enumerate(objs):
        verts, polys = world_mesh(o)
        base = len(all_verts)
        all_verts += verts
        for p in polys:
            all_polys.append(tuple(base + k for k in p))
            owner.append(i)
    bvh = BVHTree.FromPolygons(all_verts, all_polys)
    for i, o in enumerate(objs):
        verts, _ = world_mesh(o)
        step = max(1, len(verts) // 60)
        touching = False
        for v in verts[::step]:
            for _, _, idx, _ in bvh.find_nearest_range(v, TOL):
                if idx is not None and owner[idx] != i:
                    touching = True
                    break
            if touching:
                break
        if not touching:
            c = sum(verts, Vector()) / len(verts)
            msg = (f"{o.name} flotte (aucune pièce à moins de {TOL} stud) — centre "
                   f"({c.x:.2f}, {c.y:.2f}, {c.z:.2f})")
            # Une lueur suspendue (œil au centre de l'orbite, éclats autour du cœur) peut être
            # voulue ; un os ou une corne qui flotte est toujours une erreur.
            (infos if o.get("glow") or o.get("float_ok") else problems).append(msg)

    for i in infos:
        print(f"  info (lueur suspendue, vérifier que c'est voulu) : {i}")
    for w in warnings:
        print(f"  ATTENTION : {w}")
    for p in problems:
        print(f"  PROBLÈME : {p}")
    print("Contrôle OK" if not problems else f"{len(problems)} problème(s)")
    sys.exit(1 if problems else 0)


main()
