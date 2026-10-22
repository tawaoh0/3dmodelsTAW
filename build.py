"""Génère les modèles Roblox en headless.

Usage :
    blender -b -P build.py -- [modele ...] [--no-preview]
    python build.py [modele ...] [--no-preview]      # avec `pip install bpy`

Sans nom de modèle, tous les fichiers de models/ sont générés.
Sorties : exports/<modele>.fbx (+ .obj, palette .png) et previews/<modele>.png
"""
import importlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from lib import roblox  # noqa: E402


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    preview = "--no-preview" not in argv
    names = [a for a in argv if not a.startswith("--")]
    if not names:
        names = sorted(f[:-3] for f in os.listdir(os.path.join(ROOT, "models"))
                       if f.endswith(".py") and not f.startswith("_"))
    return names, preview


def build(name, preview):
    module = importlib.import_module(f"models.{name}")
    roblox.reset_scene()
    pal = roblox.Palette(module.COLORS)
    module.build(pal)
    obj = roblox.join_all(name)
    roblox.set_origin_bottom_center(obj)

    out_dir = os.path.join(ROOT, "exports", name)
    os.makedirs(out_dir, exist_ok=True)
    pal.save(os.path.join(out_dir, f"{name}_palette.png"))
    roblox.export_fbx(obj, os.path.join(out_dir, f"{name}.fbx"))
    roblox.export_obj(obj, os.path.join(out_dir, f"{name}.obj"))

    info = roblox.stats(obj)
    status = "OK" if info["triangles"] <= roblox.MAX_TRIANGLES else "TROP DE TRIANGLES"
    print(f"[{name}] {info['triangles']} triangles, taille {info['size_studs']} studs — {status}")

    if preview:
        os.makedirs(os.path.join(ROOT, "previews"), exist_ok=True)
        roblox.render_preview(obj, os.path.join(ROOT, "previews", f"{name}.png"))


def main():
    names, preview = parse_args()
    for name in names:
        build(name, preview)


main()
