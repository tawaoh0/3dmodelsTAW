"""Crabe titan squelette des cheminées hydrothermales (≈ 11 studs d'envergure) — animable.
Pack « Abysses », créature 4.

Animaux modèles : le crabe-araignée géant du Japon (longues pattes, carapace bosselée) et le
crabe yéti des sources chaudes (pinces massives, vit sur les fumeurs noirs).

Identité : exosquelette d'obsidienne noire fissuré de lave orange ; carapace **ajourée**
(grandes fenêtres) qui laisse voir l'endosquelette, les branchies et un cœur de lave ; pas de
cornes mais **3 cheminées hydrothermales** encroûtées de soufre qui fument sur le dos ;
silhouette large et basse sur 8 longues pattes, 2 pinces asymétriques (broyeuse à droite,
cisailleuse à gauche) ; thème d'effets « vent » (fumée noire + braises).

Face : rostre à 2 cornes, yeux pédonculés dans des orbites hérissées, antennes en fouet,
bouche démoniaque : portes des maxillipèdes, mandibules et couronne de grosses dents pleines,
gorge de lave.

4 pièces Roblox : corps (carapace), Head (face + bouche), Legs (8 pattes), Claws (pinces),
+ lumineux. Os : Root, Body, Head, Jaw, Leg{0-3}{L,R}_1-4, Claw{L,R}_1-3, Finger{L,R}, FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#3a3230",
    "bone_shade": "#6b4434",
    "tooth": "#f1e6d0",
    "horn": "#b89a6a",
    "horn_tip": "#e0702a",
    "disc": "#3b2a22",
    "membrane": "#2a1f1b",
    "sulfur": "#d9b32b",
    "rock": "#55463f",
    "gum": "#5a2618",
    "ink": "#0c0908",
    "glow": "#ff6a14",
    "glow_hot": "#ffd27a",
}

EFFECT_THEME = "vent"

TEST_POSE = {
    "FingerR": (0, 0, -30),
    "ClawL_1": (0, -25, 0),
    "Jaw": (25, 0, 0),
    "Leg0L_1": (0, 15, 0),
    "Leg2R_2": (0, -20, 0),
}

VIEW = (0.85, -1.0, 0.6)

# Carapace : (y, demi-larg. dessus, flancs, bas, z dessus, z bas) de l'avant vers l'arrière
CARAPACE = [(-1.9, 1.0, 1.4, 1.1, 3.1, 1.8), (-1.3, 1.7, 2.25, 1.85, 3.55, 1.95),
            (-0.4, 2.0, 2.6, 2.1, 3.75, 2.0), (0.5, 1.95, 2.45, 2.0, 3.7, 2.0),
            (1.3, 1.45, 1.85, 1.5, 3.45, 2.1), (1.85, 0.85, 1.15, 0.95, 3.15, 2.3)]
# Fenêtres de la carapace : (x, y, demi-axe x, demi-axe y)
WINDOWS = [(0, -0.75, 0.38, 0.42), (0, 0.55, 0.42, 0.38), (1.15, -0.2, 0.36, 0.5),
           (-1.15, -0.2, 0.36, 0.5), (0.95, 1.05, 0.28, 0.3), (-0.95, 1.05, 0.28, 0.3)]
VENTS = [(0.75, 0.95, 1.7), (-0.6, 1.25, 1.35), (0.05, 1.55, 1.1)]   # (x, y, hauteur)
LEG_Y = (-0.85, -0.1, 0.65, 1.35)
LEG_ANGLE = (-32, -8, 18, 42)
MOUTH = Vector((0, -1.92, 2.3))
EYE = (0.62, 2.85)        # (x, z) des pédoncules sur la face
HEAD = dict(part="Head")
LEGS = dict(part="Legs")
CLAWS = dict(part="Claws")


def leg_points(k, s):
    root = Vector((s * a.side_width(CARAPACE, LEG_Y[k], 2.3) * 0.96, LEG_Y[k], 2.3))
    phi = math.radians(LEG_ANGLE[k])
    out = Vector((s * math.cos(phi), math.sin(phi), 0))
    reach = 1.0 - 0.08 * abs(k - 1.5)
    knee = root + out * 2.0 * reach + Vector((0, 0, 1.5))
    wrist = root + out * 2.9 * reach + Vector((0, 0, 1.1))
    ankle = root + out * 3.6 * reach + Vector((0, 0, -0.9))
    tip = root + out * 3.95 * reach
    tip.z = 0.0
    return [root, knee, wrist, ankle, tip], out


def claw_points(s):
    big = 1.25 if s < 0 else 1.0          # broyeuse à droite (-X), cisailleuse à gauche
    root = Vector((s * a.side_width(CARAPACE, -1.45, 2.4) * 0.95, -1.45, 2.4))
    elbow = root + Vector((s * 1.15, -0.75, 0.75))
    wrist = elbow + Vector((s * 0.25, -0.85, -0.25))
    f = Vector((-s * 0.22, -1, -0.12)).normalized()
    palm_end = wrist + f * 1.05 * big
    return root, elbow, wrist, palm_end, f, big


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Body", (0, 1.2, 2.7), (0, -1.0, 2.7), "Root")
    rig.bone("Head", (0, -1.0, 2.6), (0, -2.3, 2.6), "Body")
    rig.bone("Jaw", (0, -1.9, 2.05), (0, -2.3, 1.85), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(4):
            pts, _ = leg_points(k, s)
            parent = "Body"
            for i in range(4):
                parent = rig.bone(f"Leg{k}{side}_{i + 1}", pts[i], pts[i + 1], parent)
        root, elbow, wrist, palm_end, f, big = claw_points(s)
        rig.bone(f"Claw{side}_1", root, elbow, "Body")
        rig.bone(f"Claw{side}_2", elbow, wrist, f"Claw{side}_1")
        rig.bone(f"Claw{side}_3", wrist, palm_end, f"Claw{side}_2")
        hinge = palm_end + Vector((0, 0, 0.22 * big))
        rig.bone(f"Finger{side}", hinge, hinge + f * 0.9 * big, f"Claw{side}_3")
        rig.fx(f"Eye{side}", (s * 1.0, -2.55, 3.55), "Head")
    for i, (x, y, h) in enumerate(VENTS):
        rig.fx(f"Vent{i}", (x, y, 3.6 + h), "Body")
    rig.fx("Heart", (0, 0.1, 2.75), "Body")
    rig.fx("Mouth", MOUTH + Vector((0, -0.1, 0)), "Head")


# ---------------------------------------------------------------- carapace

def build_carapace(rig):
    B = "Body"
    shell = a.loft_profile("Carapace", CARAPACE, droop=0.05)
    hit = a.surface_caster(shell)

    def top(x, y):
        p, n = hit((x, y, 10))
        return p, n

    cutters = [a.hole_along((x, y, 3.0), (0, 0, 1), (1, 0, 0), rx, ry, depth=2.0)
               for x, y, rx, ry in WINDOWS]
    cutters += [a.hole_along(MOUTH, (0, 1, 0), (1, 0, 0), 0.46, 0.36, depth=0.5)]
    cutters += [a.hole_along((s * EYE[0], -1.9, EYE[1]), (0, 1, 0), (1, 0, 0), 0.17, 0.15,
                             depth=0.4) for s in (-1, 1)]
    a.cut(shell, cutters)
    rig.add(shell, B, "bone")
    # Rebords en relief autour de chaque fenêtre, tubercules sur le rebord
    for w, (x, y, rx, ry) in enumerate(WINDOWS):
        ring = []
        for k in range(12):
            t = 2 * math.pi * k / 12
            p, _ = top(x + rx * 1.08 * math.cos(t), y + ry * 1.08 * math.sin(t))
            if p is not None:
                ring.append(p + Vector((0, 0, 0.02)))
        if len(ring) == 12:
            rig.add(r.tube(f"WindowRim{w}", [tuple(p) for p in ring], 0.06, segments=5,
                           closed=True), B, "bone_shade")
            for k in range(0, 12, 3):
                rig.add(r.ico(f"RimKnob{w}{k}", 0.08, subdivisions=1, location=ring[k]), B,
                        "bone_shade")
    # Endosquelette visible par les fenêtres : arches transversales + poutre médiane
    for i, y in enumerate((-1.1, -0.4, 0.3, 1.0)):
        w = a.width_at(CARAPACE, y, 2) * 0.85
        zt = a.width_at(CARAPACE, y, 4)
        rig.add(r.tube(f"Endo{i}", [(-w, y, 2.2), (-w * 0.5, y, zt - 0.25), (0, y, zt - 0.15),
                                    (w * 0.5, y, zt - 0.25), (w, y, 2.2)], 0.07, segments=5),
                B, "bone_shade")
    rig.add(r.tube("EndoSpine", [(0, -1.5, 2.25), (0, 0, 2.3), (0, 1.5, 2.35)], 0.09,
                   segments=6), B, "bone_shade")
    # Cœur de lave : grappe de cristaux sous les fenêtres centrales
    for i, (dx, dy, h) in enumerate(((0, -0.75, 1.25), (0.18, -0.6, 0.9), (-0.2, -0.9, 0.85),
                                     (0, 0.55, 1.2), (0.2, 0.4, 0.8), (-0.18, 0.7, 0.9),
                                     (0, -0.1, 0.7))):
        rig.add(a.crystal(f"LavaHeart{i}", (dx, dy, 2.3), 0.2 if i % 3 == 0 else 0.13, h,
                          sides=6), B, "glow", glow=True)
    # Branchies en lamelles sous les fenêtres latérales
    for s in (-1, 1):
        for i in range(6):
            y = -0.55 + 0.14 * i
            rig.add(a.blade(f"Gill{s}{i}", (s * 0.75, y, 2.3), (s * 1.4, y + 0.05, 3.2), 0.18,
                            0.04, width_end=0.08, normal=(0, 1, 0), bevel=0), B,
                    "glow" if i % 2 else "gum", glow=bool(i % 2))
    # Bord de la carapace : bourrelet + dents antéro-latérales
    for s in (-1, 1):
        rim = []
        for y in (-1.85, -1.4, -0.9, -0.4, 0.1, 0.6, 1.1, 1.55, 1.85):
            z = 2.45 if y < 1.5 else 2.5
            rim.append(Vector((s * a.side_width(CARAPACE, y, z) * 1.0, y, z)))
        rig.add(r.tube(f"Margin{s}", [tuple(p) for p in rim], 0.08, segments=5), B, "bone_shade")
        for i, p in enumerate(rim[1:6]):
            rig.add(a.claw(f"MarginTooth{s}{i}", p, (s * 1, -0.35, 0.25), 0.42 - 0.04 * i, 0.08,
                           curl=-0.1, segments=5), B, "horn")
        for i, p in enumerate(rim[6:8]):
            rig.add(a.claw(f"MarginSpine{s}{i}", p, (s * 1, 0.4, 0.3), 0.25, 0.05, curl=0,
                           segments=4), B, "horn")
    # Tubercules et cicatrices de lave sur le dessus
    for i, (x, y) in enumerate(((0.55, -1.35), (-0.55, -1.35), (0.0, -1.45), (0.6, 0.0),
                                (-0.6, 0.0), (1.6, -0.9), (-1.6, -0.9), (1.55, 0.6),
                                (-1.55, 0.6), (0.45, 1.55), (-0.45, 1.6), (0, -0.1))):
        p, n = top(x, y)
        if p is not None:
            rig.add(a.claw(f"Tubercle{i}", p, Vector(n) + Vector((0, 0, 1)), 0.22, 0.07, curl=0,
                           segments=5), B, "bone_shade")
    for i, (p0, p1) in enumerate((((0.3, -1.55), (0.85, -1.1)), ((-0.3, -1.55), (-0.85, -1.1)),
                                  ((1.7, 0.2), (1.35, 0.9)), ((-1.7, 0.2), (-1.35, 0.9)))):
        q0, _ = top(*p0)
        q1, _ = top(*p1)
        mr.scar(rig, f"LavaCrack{i}", q0 + Vector((0, 0, 0.02)), q1 + Vector((0, 0, 0.02)), B,
                width=0.07, seed=i)
    # Cheminées hydrothermales (fumeurs noirs) encroûtées de soufre
    for i, (x, y, h) in enumerate(VENTS):
        base, _ = top(x, y)
        pts = [base - Vector((0, 0, 0.1)), base + Vector((0.05, 0.05, h * 0.35)),
               base + Vector((-0.04, 0.12, h * 0.7)), base + Vector((0.02, 0.15, h))]
        rig.add(r.tube(f"Vent{i}", [tuple(p) for p in pts], [0.32, 0.26, 0.2, 0.22], segments=7),
                B, "rock")
        for k, t in enumerate((0.25, 0.55, 0.85)):
            q = mr.along(pts, t)
            rig.add(a.ring_around(f"VentBand{i}{k}", q, (0, 0.1, 1), 0.3 - 0.07 * t * 1.2, 0.05,
                                  segments=8), B, "sulfur")
            ang = 1.3 * k + i
            rig.add(r.ico(f"VentCrust{i}{k}", 0.09, subdivisions=1,
                          location=q + Vector((0.25 * math.cos(ang), 0.25 * math.sin(ang), 0.05))),
                    B, "sulfur")
        rig.add(a.ring_around(f"VentLip{i}", pts[-1], (0, 0.1, 1), 0.22, 0.06, segments=8), B,
                "rock")
        rig.add(r.ico(f"VentGlow{i}", 0.17, subdivisions=1, location=pts[-1] - Vector((0, 0, 0.04))),
                B, "glow", glow=True)
    # Dessous : plastron (sternum) + abdomen replié en plaques
    rig.add(a.blade("Sternum", (0, -1.4, 1.95), (0, 1.2, 1.98), 1.6, 0.12, width_end=1.0,
                    mid=1.9, normal=(0, 0, 1)), B, "bone_shade")
    for i in range(5):
        y = 1.3 - 0.42 * i
        rig.add(a.blade(f"Abdomen{i}", (0, y, 1.84), (0, y - 0.36, 1.84), 0.95 - 0.12 * i, 0.1,
                        width_end=0.85 - 0.12 * i, normal=(0, 0, 1)), B, "bone")
        rig.add(r.tube(f"AbdomenGlow{i}", [(-0.4 + 0.05 * i, y - 0.38, 1.82),
                                           (0.4 - 0.05 * i, y - 0.38, 1.82)], 0.025,
                       segments=4), B, "glow", glow=True)


# ---------------------------------------------------------------- face

def build_face(rig):
    H, J = "Head", "Jaw"
    # Rostre : deux cornes en avant + épine centrale
    for s in (-1, 1):
        rig.add(a.claw(f"Rostrum{s}", (s * 0.22, -1.9, 3.0), (s * 0.3, -1, 0.45), 0.8, 0.11,
                       curl=-0.25, segments=5), H, "horn", **HEAD)
        rig.add(r.ico(f"RostrumBase{s}", 0.14, subdivisions=1, location=(s * 0.22, -1.92, 3.0)),
                H, "bone_shade", **HEAD)
    rig.add(a.claw("RostrumMid", (0, -1.95, 2.95), (0, -1, 0.1), 0.45, 0.07, curl=0, segments=4),
            H, "horn", **HEAD)
    for s in (-1, 1):
        # Pédoncules oculaires dans des orbites hérissées, yeux de lave
        base = Vector((s * EYE[0], -1.85, EYE[1]))
        end = Vector((s * 1.0, -2.55, 3.55))
        stalk = [base, base.lerp(end, 0.5) + Vector((0, 0, 0.08)), end]
        rig.add(r.tube(f"EyeStalk{s}", [tuple(p) for p in stalk], [0.11, 0.09, 0.08], segments=6),
                H, "bone", **HEAD)
        for k, t in enumerate((0.3, 0.65)):
            q = mr.along(stalk, t)
            rig.add(a.ring_around(f"StalkRing{s}{k}", q, end - base, 0.11, 0.03, segments=8), H,
                    "bone_shade", **HEAD)
        rig.add(r.ico(f"Eye{s}", 0.2, subdivisions=2, location=end), H, "glow", glow=True)
        rig.add(r.ico(f"Pupil{s}", 0.08, subdivisions=1,
                      location=end + Vector((s * 0.05, -0.17, 0.02)), scale=(0.5, 0.4, 1.6)), H,
                "ink", **HEAD)
        for k in range(3):   # piques sur le pédoncule
            q = mr.along(stalk, 0.2 + 0.25 * k)
            rig.add(a.claw(f"StalkSpike{s}{k}", q + Vector((0, 0, 0.08)), (s * 0.3, 0.3, 1), 0.16,
                           0.03, curl=-0.1, segments=4), H, "horn", **HEAD)
        rig.add(a.ring_around(f"EyeCup{s}", end + (base - end).normalized() * 0.1, end - base,
                              0.19, 0.045, segments=10), H, "bone", **HEAD)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * EYE[0], -1.92, EYE[1]), (0, -1, 0), 0.2, H,
                       spikes=6, **HEAD)
        rig.add(a.blade(f"Brow{s}", (s * 0.35, -1.95, 3.1), (s * 0.95, -1.75, 3.2), 0.18, 0.08,
                        width_end=0.1, normal=(0, -0.3, 1)), H, "bone_shade", **HEAD)
        # Antennes en fouet annelées, antennules repliées à pointe lumineuse
        ant = a.smooth_path([(s * 0.38, -1.95, 2.6), (s * 0.6, -2.7, 2.9), (s * 1.4, -3.3, 3.7),
                             (s * 2.4, -3.0, 4.3), (s * 3.1, -2.0, 4.5)], 9)
        rig.add(r.tube(f"Antenna{s}", [tuple(p) for p in ant],
                       [0.07 - 0.0065 * i for i in range(9)], segments=5), H, "bone", **HEAD)
        for k in (1, 3, 5):
            rig.add(a.ring_around(f"AntRing{s}{k}", ant[k], ant[k + 1] - ant[k], 0.075 - 0.007 * k,
                                  0.025, segments=6), H, "horn", **HEAD)
        rig.add(r.ico(f"AntTip{s}", 0.05, subdivisions=1, location=ant[-1]), H, "glow", glow=True)
        anl = [(s * 0.2, -1.95, 2.62), (s * 0.28, -2.3, 2.75), (s * 0.22, -2.4, 3.0)]
        rig.add(r.tube(f"Antennule{s}", anl, [0.045, 0.035, 0.025], segments=4), H, "horn",
                **HEAD)
        rig.add(r.ico(f"AntennuleGlow{s}", 0.04, subdivisions=1, location=anl[-1]), H, "glow",
                glow=True)
        # Portes des maxillipèdes (entrouvertes) bordées de soies-crochets
        d0, d1 = Vector((s * 0.68, -1.98, 1.75)), Vector((s * 0.62, -2.25, 2.7))
        door = a.blade(f"Maxilliped{s}", d0, d1, 0.32, 0.08, width_end=0.22, mid=0.38,
                       normal=(s * 0.8, -1, 0))
        rig.add(door, J, "bone", **HEAD)
        for k in range(4):
            q = d0.lerp(d1, 0.15 + 0.22 * k)
            rig.add(a.claw(f"MaxHook{s}{k}", q + Vector((-s * 0.12, -0.08, 0)), (-s, -0.3, -0.2),
                           0.16, 0.03, curl=0.4, segments=4), J, "horn", **HEAD)
        # Mandibules massives à grosses dents
        mand = [Vector((s * 0.62, -1.75, 2.3)), Vector((s * 0.42, -1.97, 2.3))]
        rig.add(r.tube(f"Mandible{s}", [tuple(p) for p in mand], [0.16, 0.13], segments=7), J,
                "bone_shade", **HEAD)
        for k, dz in enumerate((-0.12, 0.0, 0.12)):
            base = mand[1] + Vector((0, -0.02, dz))
            rig.add(mr.tooth(f"MandTooth{s}{k}", base, base + Vector((-s * 0.3, -0.05, 0)),
                             0.17, 0.08, Vector((0, -1, 0))), J, "tooth", **HEAD)
        # Pores et fissures de lave sur la face
        for k in range(4):
            rig.add(r.ico(f"FacePore{s}{k}", 0.035, subdivisions=1,
                          location=(s * (0.45 + 0.12 * k), -1.91, 2.6 - 0.06 * k)), H, "ink",
                    **HEAD)
        mr.scar(rig, f"FaceCrack{s}", (s * 0.85, -1.85, 3.0), (s * 0.95, -1.75, 2.4), H, width=0.05,
                seed=s + 5)
    # Couronne de grosses dents pleines autour de la bouche, pointées vers le centre
    # (2 couronnes : grands crocs au bord, petites dents plus au fond)
    for ring, (n, rx, rz, dy, base_size) in enumerate(((16, 0.46, 0.36, -0.03, 0.19),
                                                       (12, 0.38, 0.3, 0.14, 0.12))):
        for k in range(n):
            t = 2 * math.pi * (k + 0.5 * ring) / n
            rim = MOUTH + Vector((rx * math.cos(t), dy, rz * math.sin(t)))
            inward = (MOUTH - rim).normalized()
            size = base_size + 0.04 * (k % 2) + (0.07 if ring == 0 and k in (3, 4, 11, 12) else 0)
            rig.add(mr.tooth(f"MouthTooth{ring}{k}", rim,
                             rim + inward * size + Vector((0, 0.14 + 0.06 * ring, 0)),
                             size * 0.62, size * 0.28, Vector((0, -1, 0))), H, "tooth", **HEAD)
    rig.add(a.ring_around("MouthGum", MOUTH + Vector((0, 0.02, 0)), (0, 1, 0), 0.47, 0.07,
                          segments=16), H, "gum", **HEAD)
    rig.add(a.ring_around("MouthRim", MOUTH + Vector((0, -0.05, 0)), (0, 1, 0), 0.54, 0.06,
                          segments=16), H, "bone_shade", **HEAD)
    for k in range(8):   # soies-crochets en barbe sous la bouche
        x = -0.35 + 0.1 * k
        rig.add(a.claw(f"Beard{k}", (x, -1.95, 1.9), (x * 0.5, -0.6, -1), 0.2 + 0.05 * (k % 2),
                       0.03, curl=0.3, segments=4), H, "horn", **HEAD)
    for k in range(7):   # piques sur le bord frontal de la carapace
        x = -0.9 + 0.3 * k
        if abs(x) < 0.1:
            continue
        rig.add(a.claw(f"FrontSpike{k}", (x, -1.9, 3.08 - 0.15 * abs(x)), (x * 0.4, -1, 0.8),
                       0.2, 0.045, curl=-0.1, segments=4), H, "horn", **HEAD)
    rig.add(r.ico("Throat", 0.3, subdivisions=2, location=MOUTH + Vector((0, 0.3, 0)),
                  scale=(1.3, 0.5, 1.05)), H, "glow", glow=True)
    rig.add(a.blade("Epistome", (-0.5, -1.97, 2.78), (0.5, -1.97, 2.78), 0.12, 0.07,
                    width_end=0.14, normal=(0, -1, 0.3)), H, "bone_shade", **HEAD)


# ---------------------------------------------------------------- pattes

def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for k in range(4):
            pts, out = leg_points(k, s)
            bones = [f"Leg{k}{side}_{i + 1}" for i in range(4)]
            radii = (0.22, 0.18, 0.15)
            for i in range(3):
                rig.add(a.long_bone(f"Leg{k}{s}Seg{i}", pts[i], pts[i + 1], radii[i], knob=1.35,
                                    segments=7, condyles=False), bones[i], "bone", **LEGS)
            rig.add(a.claw(f"Leg{k}{s}Dactyl", pts[3], pts[4] - pts[3], (pts[4] - pts[3]).length,
                           0.13, curl=0.15, segments=6), bones[3], "horn", **LEGS)
            # Coxa en anneau, genoux de lave, épines de méropodite, soies du propode
            rig.add(a.ring_around(f"Leg{k}{s}Coxa", pts[0] + out * 0.15, out, 0.26, 0.07,
                                  segments=8), bones[0], "bone_shade", **LEGS)
            for j in (1, 2, 3):
                rig.add(a.ring_around(f"Leg{k}{s}Joint{j}", pts[j], pts[j + 1] - pts[j],
                                      radii[min(j, 2)] * 1.15, 0.04, segments=8), bones[j],
                        "glow", glow=True)
            for j, t in enumerate((0.25, 0.5, 0.75)):
                q = pts[0].lerp(pts[1], t)
                rig.add(a.claw(f"Leg{k}{s}Spine{j}", q + Vector((0, 0, 0.18)),
                               out * 0.4 + Vector((0, 0, 1)), 0.3, 0.05, curl=-0.1, segments=4),
                        bones[0], "horn", **LEGS)
            for j, t in enumerate((0.3, 0.6)):
                q = pts[2].lerp(pts[3], t)
                rig.add(a.claw(f"Leg{k}{s}Bristle{j}", q, out + Vector((0, 0, 0.3)), 0.2, 0.035,
                               curl=0.2, segments=4), bones[2], "horn", **LEGS)
            rig.add(r.tube(f"Leg{k}{s}Ridge", [tuple(pts[1].lerp(pts[2], t) + Vector((0, 0, 0.17)))
                                               for t in (0.1, 0.5, 0.9)], 0.04, segments=4),
                    bones[1], "bone_shade", **LEGS)


# ---------------------------------------------------------------- pinces

def build_claws(rig):
    for s, side in ((1, "L"), (-1, "R")):
        root, elbow, wrist, palm_end, f, big = claw_points(s)
        b1, b2, b3, bf = f"Claw{side}_1", f"Claw{side}_2", f"Claw{side}_3", f"Finger{side}"
        rig.add(a.long_bone(f"ClawMerus{s}", root, elbow, 0.26 * big, knob=1.3, segments=8,
                            condyles=False), b1, "bone", **CLAWS)
        rig.add(a.long_bone(f"ClawCarpus{s}", elbow, wrist, 0.28 * big, knob=1.25, segments=8,
                            condyles=False), b2, "bone", **CLAWS)
        for j, t in enumerate((0.3, 0.6, 0.85)):
            q = root.lerp(elbow, t)
            rig.add(a.claw(f"MerusSpine{s}{j}", q + Vector((0, 0, 0.25 * big)),
                           Vector((s * 0.3, -0.3, 1)), 0.32, 0.06, curl=-0.1, segments=4), b1,
                    "horn", **CLAWS)
        for j in range(3):
            ang = j * 2.1
            q = wrist.lerp(elbow, 0.4) + Vector((0.3 * math.cos(ang), 0, 0.3 * math.sin(ang))) * big
            rig.add(a.claw(f"CarpusSpine{s}{j}", q, q - wrist.lerp(elbow, 0.4), 0.28, 0.06,
                           curl=0, segments=4), b2, "horn", **CLAWS)
        for k, q in enumerate((elbow, wrist)):
            rig.add(a.ring_around(f"ClawJoint{s}{k}", q, (wrist - elbow), 0.3 * big, 0.05,
                                  segments=10), b2, "glow", glow=True)
        # Paume bombée et ajourée (2 fenêtres), crête dentelée, fissures de lave
        palm_pts = [wrist, wrist + f * 0.35 * big, wrist + f * 0.75 * big, palm_end]
        palm = r.tube(f"Palm{s}", [tuple(p) for p in palm_pts],
                      [0.3 * big, 0.5 * big, 0.48 * big, 0.34 * big], segments=10)
        r.smooth(palm, 40)
        side_dir = f.cross(Vector((0, 0, 1))).normalized()
        a.cut(palm, [a.hole_along(wrist + f * t * big + Vector((0, 0, 0.05)), side_dir, f,
                                  0.17 * big, 0.12 * big, depth=1.0) for t in (0.35, 0.7)])
        rig.add(palm, b3, "bone", **CLAWS)
        rig.add(r.tube(f"PalmCrest{s}", [tuple(p + Vector((0, 0, 0.47 * big)))
                                         for p in palm_pts[1:3]], 0.05, segments=4), b3,
                "bone_shade", **CLAWS)
        for j in range(4):
            q = wrist.lerp(palm_end, 0.2 + 0.2 * j) + Vector((0, 0, 0.5 * big))
            rig.add(a.claw(f"PalmSpike{s}{j}", q, Vector((0, -0.4, 1)), 0.22, 0.05, curl=-0.1,
                           segments=4), b3, "horn", **CLAWS)
        mr.scar(rig, f"PalmCrack{s}", wrist + f * 0.2 * big - side_dir * 0.48 * big * s,
                palm_end - side_dir * 0.4 * big * s, b3, width=0.06, seed=s)
        # Doigt fixe (bas) et doigt mobile (haut) avec rangées de grosses dents pleines
        fixed = [palm_end - Vector((0, 0, 0.12 * big)),
                 palm_end + f * 0.45 * big - Vector((0, 0, 0.22 * big)),
                 palm_end + f * 0.9 * big - Vector((0, 0, 0.1 * big))]
        hinge = palm_end + Vector((0, 0, 0.22 * big))
        movable = [hinge, hinge + f * 0.45 * big + Vector((0, 0, 0.12 * big)),
                   hinge + f * 0.95 * big - Vector((0, 0, 0.12 * big))]
        rig.add(r.tube(f"FixedFinger{s}", [tuple(p) for p in fixed],
                       [0.2 * big, 0.15 * big, 0.06], segments=7), b3, "bone", **CLAWS)
        rig.add(r.tube(f"MovFinger{s}", [tuple(p) for p in movable],
                       [0.2 * big, 0.15 * big, 0.06], segments=7), bf, "bone", **CLAWS)
        rig.add(r.ico(f"FingerHinge{s}", 0.2 * big, subdivisions=1, location=hinge), bf,
                "bone_shade", **CLAWS)
        for name, pts, bone, up in (("Fixed", fixed, b3, 1), ("Mov", movable, bf, -1)):
            tipdir = pts[2] - pts[1]
            rig.add(a.claw(f"{name}Tip{s}", pts[2], tipdir + Vector((0, 0, up * 0.5)), 0.3 * big,
                           0.07, curl=0.3, segments=5), bone, "horn", **CLAWS)
            n = 5 if s < 0 else 7
            for j in range(n):
                t = 0.12 + 0.75 * j / (n - 1)
                q = mr.along(pts, t) + Vector((0, 0, up * 0.1 * big * (1 - t * 0.5)))
                size = (0.2 if s < 0 else 0.17) * big * (1 - 0.35 * t)
                width = size * (1.0 if s < 0 else 0.7)    # broyeuse : molaires larges
                rig.add(mr.tooth(f"{name}Tooth{s}{j}", q, q + Vector((0, 0, up * size)), width,
                                 width * 0.45, -side_dir * s), bone, "tooth", **CLAWS)
        rig.add(r.tube(f"FingerGlow{s}", [tuple(p) for p in fixed[:2]], 0.03, segments=4), b3,
                "glow", glow=True)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_carapace(rig)
    build_face(rig)
    build_legs(rig)
    build_claws(rig)
    return rig
