"""Modèle de départ : copier ce fichier dans models/<nom>.py.

- COLORS : palette nom -> couleur hex
- build(pal) : crée les pièces avec les primitives de lib.roblox et les peint.
Unités : 1 = 1 stud. Z est vers le haut dans Blender (converti en Y pour Roblox).
"""
from lib import roblox as r

COLORS = {
    "main": "#3a7bd5",
}


def build(pal):
    cube = r.box("Cube", (2, 2, 2), location=(0, 0, 1))
    pal.paint(cube, "main")
