"""Gros plan sur une pièce d'une créature (pour contrôler la tête, les ailes…).

Usage (depuis la racine du projet) :
    <python> closeup.py <modele> <piece> <sortie.png> [vx vy vz]
    <python> closeup.py <modele> <piece> <prefixe> trio
<piece> : Head, Wings… (suffixe du mesh), ou Body pour le corps principal.
vx vy vz : direction d'où regarde la caméra (défaut 1 -0.6 0.35, profil 3/4).
trio : 3 vues en un seul passage → <prefixe>_profil.png, <prefixe>_face.png, <prefixe>_dessus.png
"""
import importlib
import os
import sys

sys.path.insert(0, os.getcwd())
from lib import creature, roblox  # noqa: E402

TRIO = {"profil": (1.0, -0.55, 0.45), "face": (0.3, -1.0, 0.3), "dessus": (0.35, -0.6, 1.0)}

name, part, out = sys.argv[1:4]
module = importlib.import_module(f"models.{name}")
roblox.reset_scene()
pal = roblox.Palette(module.COLORS)
rig = module.build(pal)
parts, arm = creature.finalize(rig, name)
target = [p for p in parts if p.name == (name if part == "Body" else f"{name}_{part}")]
if not target:
    sys.exit(f"Pièce inconnue « {part} ». Pièces : {[p.name for p in parts]}")

if len(sys.argv) > 4 and sys.argv[4] == "trio":
    for label, view in TRIO.items():
        path = os.path.abspath(f"{out}_{label}.png")
        roblox.render_preview(target, path, dark=True, view=view)
        print(f"Gros plan écrit : {path}")
else:
    view = tuple(float(v) for v in sys.argv[4:7]) if len(sys.argv) > 6 else (1.0, -0.6, 0.35)
    roblox.render_preview(target, os.path.abspath(out), dark=True, view=view)
    print(f"Gros plan écrit : {out}")
