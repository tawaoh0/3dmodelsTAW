"""Scarabée rhinocéros squelette (exosquelette ajouré, ≈ 3,4 studs de haut, 6 de long) — animable.
Pack « Insectes géants », créature 2.

Animal modèle : le **scarabée Hercule / rhinocéros** — énorme corne céphalique recourbée
vers le haut et fourchue, corne thoracique qui descend à sa rencontre, pronotum bombé,
élytres en dôme, pattes de fouisseur dentelées.

Identité : chitine bronze ; **deux grandes cornes** noires annelées ; dôme d'élytres en
plaques séparées (jours lumineux), stries en relief, **gemmes d'ambre** serties le long des
bords ; organes ambrés ; thème d'effets « amber ».

Pièces Roblox : corps, Head, Legs, + lumineux.
Os : Root, Body, Thorax, Head, Elytron_{L,R}, Leg{1-3}_{L,R}_{1-3}.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import roblox as r
from models import _bugs as b

COLORS = {
    "chitin": "#7a5530",
    "chitin_dark": "#2c1d10",
    "horn": "#151009",
    "tooth": "#efe2c6",
    "ink": "#060403",
    "glow": "#ffae1f",
    "glow_hot": "#fff0c4",
}

EFFECT_THEME = "amber"

TEST_POSE = {
    "Head": (-20, 0, 0),
    "Elytron_L": (0, -35, 0),
    "Elytron_R": (0, 35, 0),
    "Leg1_L_1": (0, 0, 20),
    "Thorax": (10, 0, 0),
}

VIEW = (1.0, -0.9, 0.45)

HEAD = dict(part="Head")
LEGS = dict(part="Legs")


def leg(k, s):
    th = math.radians((-35, 5, 40)[k])
    d = Vector((s * math.cos(th), math.sin(th), 0))
    a0 = Vector((s * 0.55, -0.75 + 0.7 * k, 0.95))
    return [a0, a0 + d * 0.9 + Vector((0, 0, 0.35)), a0 + d * 1.6 + Vector((0, 0, -0.45)), a0 + d * 2.0 + Vector((0, 0, -0.9))]


def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Body", (0, 2.1, 1.3), (0, -0.1, 1.3), "Root")
    rig.bone("Thorax", (0, -0.1, 1.4), (0, -1.1, 1.4), "Body")
    rig.bone("Head", (0, -1.1, 1.25), (0, -1.75, 1.25), "Thorax")
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"Elytron_{side}", (s * 0.1, -0.1, 1.95), (s * 0.4, 2.1, 1.7), "Body")
        for k in range(3):
            p = leg(k, s)
            prev = "Thorax" if k == 0 else "Body"
            for j in range(3):
                prev = rig.bone(f"Leg{k + 1}_{side}_{j + 1}", p[j], p[j + 1], prev)
        rig.fx(f"Eye{side}", (s * 0.32, -1.55, 1.35), "Head")
    rig.fx("HornTip", (0, -2.45, 3.15), "Head")
    rig.fx("Amber", (0, 1.0, 1.4), "Body")


def build_head(rig):
    H, T = "Head", "Thorax"
    # Pronotum : bouclier bombé en plaques + corne thoracique qui descend vers l'avant
    for k, (y, rx, rz) in enumerate(((-0.05, 0.95, 0.7), (-0.4, 1.0, 0.75), (-0.75, 0.9, 0.68), (-1.05, 0.7, 0.55))):
        b.plate(rig, f"Pronotum{k}", (0, y, 1.35), (0, 1, 0), rx, rz, 0.33, T, start=-120, end=120, n=11, **HEAD)
    rig.add(a.ridged_horn("ThoraxHorn", [(0, -0.5, 2.0), (0, -0.9, 2.35), (0, -1.45, 2.45), (0, -1.85, 2.2)], 0.18, ridges=8), T,
            "horn", **HEAD)
    for s in (-1, 1):
        rig.add(a.claw(f"ThoraxTooth{s}", (s * 0.06, -1.6, 2.33), (s * 0.3, -0.3, -1), 0.2, 0.04, curl=0, segments=4), T,
                "horn", **HEAD)
    b.organs(rig, "ThoraxCore", (0, -0.5, 1.3), 0.6, T, n=2)
    rig.add(r.ico("Prosternum", 0.35, subdivisions=1, location=(0, -0.95, 1.3), scale=(1.6, 1.1, 1.6)), T, "chitin_dark", **HEAD)
    # Tête : petite, enfoncée sous le pronotum, énorme corne céphalique fourchue
    rig.add(r.ico("HeadCapsule", 0.38, subdivisions=1, location=(0, -1.35, 1.2), scale=(1.1, 1, 0.75)), H, "chitin", **HEAD)
    horn = [(0, -1.55, 1.3), (0, -2.15, 1.45), (0, -2.6, 1.95), (0, -2.65, 2.6), (0, -2.45, 3.1)]
    rig.add(a.ridged_horn("HeadHorn", horn, 0.22, ridges=10), H, "horn", **HEAD)
    for sx in (-1, 1):
        rig.add(a.claw(f"HornFork{sx}", Vector(horn[-1]) + Vector((0, 0.03, -0.05)), (sx * 0.6, 0.4, 1), 0.3, 0.05, curl=0.2,
                       segments=4), H, "horn", **HEAD)
    for k, t in enumerate((0.25, 0.5)):
        q = Vector(horn[1]).lerp(Vector(horn[3]), t * 1.5)
        rig.add(a.claw(f"HornKnob{k}", q, (0, 1, 0.3), 0.18, 0.05, curl=0, segments=4), H, "horn", **HEAD)
    for s in (-1, 1):
        b.compound_eye(rig, f"Eye{s}", (s * 0.34, -1.5, 1.32), 0.1, (s, -0.4, 0.2), H, **HEAD)
        b.mandible(rig, f"Mandible{s}", (s * 0.2, -1.62, 1.0), (s * 0.05, -1.95, 0.95), (-s, 0, 0), H, width=0.1, teeth=3,
                   **HEAD)
        b.antenna(rig, f"Antenna{s}", [(s * 0.3, -1.62, 1.18), (s * 0.55, -1.85, 1.3), (s * 0.68, -2.05, 1.45)], H,
                  radius=0.025, club=0.06, **HEAD)
        # Massue lamellée : 3 lames en éventail
        for k in range(3):
            rig.add(a.blade(f"Lamella{s}{k}", (s * 0.68, -2.05, 1.45), (s * (0.72 + 0.04 * k), -2.25, 1.5 + 0.08 * (k - 1)),
                            0.06, 0.02, width_end=0.08, normal=(0, 0.3, 1), bevel=0), H, "chitin_dark", **HEAD)


def build_body(rig):
    # Abdomen (dessous) : sternites et organes ambrés
    for k in range(6):
        y = 0.0 + 0.36 * k
        b.plate(rig, f"Sternite{k}", (0, y, 1.25), (0, 1, 0), 0.85 - 0.08 * k, 0.5, 0.3, "Body", start=130, end=230, n=6,
                rim=None)
    b.organs(rig, "AmberGut", (0, 0.9, 1.3), 1.0, "Body", n=4)
    rig.add(r.tube("Spine", [(0, -0.1, 1.35), (0, 1.0, 1.4), (0, 2.1, 1.3)], 0.08, segments=6), "Body", "chitin_dark")
    # Élytres : dôme en plaques séparées par des jours, stries, gemmes d'ambre au bord
    for s, side in ((1, "L"), (-1, "R")):
        bone = f"Elytron_{side}"
        for k in range(7):
            y = -0.05 + 0.34 * k
            f = k / 6
            rz = 0.85 - 0.25 * f * f
            rx = 1.0 - 0.3 * f * f
            b.plate(rig, f"Elytron{s}{k}", (0, y, 1.3), (0, 1, 0), rx, rz, 0.3, bone,
                    start=3 if s > 0 else -105, end=105 if s > 0 else -3, n=7)
        for j, ang in enumerate((25, 55, 85)):
            pts = []
            for k in range(7):
                f = k / 6
                rz = 0.85 - 0.25 * f * f
                rx = 1.0 - 0.3 * f * f
                pts.append((s * rx * 1.04 * math.sin(math.radians(ang)), -0.05 + 0.34 * k, 1.3 + rz * 1.04 * math.cos(math.radians(ang))))
            rig.add(r.tube(f"Stria{s}{j}", pts, 0.025, segments=4), bone, "chitin_dark")
        for k in range(4):
            y = 0.2 + 0.5 * k
            f = (y + 0.05) / 2.04
            rx = 1.0 - 0.3 * f * f
            rig.add(a.crystal(f"AmberGem{s}{k}", (s * rx * 1.03, y, 1.3 + 0.05), 0.07, 0.18, sides=5), bone, "glow", glow=True)
    rig.add(r.tube("Suture", [(0, -0.05, 2.17), (0, 1.0, 2.05), (0, 2.0, 1.85)], 0.035, segments=4), "Body", "chitin_dark")


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(3):
            b.leg_chain(rig, f"Leg{s}{k}", leg(k, s), [f"Leg{k + 1}_{side}_{j}" for j in (1, 2, 3)], 0.11, **LEGS)
            # Tibia de fouisseur : dents externes
            p = leg(k, s)
            for j in range(3):
                q = p[2].lerp(p[3], 0.2 + 0.3 * j)
                rig.add(a.claw(f"DigTooth{s}{k}{j}", q, (s, 0, 0.2), 0.16, 0.035, curl=0, segments=4),
                        f"Leg{k + 1}_{side}_3", "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
