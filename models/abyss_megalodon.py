"""Mégalodon squelette (≈ 15 studs de long, 6 de haut) — créature animable.
Pack « Abysses », créature 2.

Animal modèle : le grand requin blanc géant — mâchoires en fer à cheval à 3 rangées de
dents triangulaires, rostre arrondi, petits yeux, évents, 5 arcs branchiaux, grande dorsale,
pectorales en ailes, queue en croissant (lobe haut plus long), denticules cutanés.

Identité : os ardoise sombre et dents claires ; pas de cornes mais des harpons et hameçons
rouillés plantés dans le corps et la mâchoire, avec leurs chaînes ; cicatrices rougeoyantes ;
silhouette horizontale en nage ; lueur rouge sang, thème d'effets « blood ».

4 pièces Roblox : corps, tête (crâne + mâchoires + branchies), dents (Teeth), nageoires,
+ lumineux.
Os : Root, Body1-5, Head, Jaw, Caudal, PecFin_L/R, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#56616c",
    "bone_shade": "#3a434c",
    "tooth": "#ece6d6",
    "horn": "#d8d2c4",
    "horn_tip": "#a8323a",
    "disc": "#2a1f24",
    "membrane": "#262c33",
    "gum": "#5a2a30",
    "rust": "#8a4b2a",
    "ink": "#0e0d10",
    "glow": "#ff2d4a",
    "glow_hot": "#ffc2b8",
}

EFFECT_THEME = "blood"

TEST_POSE = {
    "Jaw": (35, 0, 0),
    "Body3": (0, 0, 12),
    "Body4": (0, 0, 15),
    "Caudal": (0, 0, 20),
    "PecFin_L": (0, 25, 0),
}

VIEW = (1.0, -0.7, 0.45)

SPINE = a.smooth_path([(0, -2.8, 3.1), (0, -1.0, 3.15), (0, 1.5, 3.2), (0, 4.0, 3.3),
                       (0, 6.2, 3.5), (0, 7.8, 3.7)], 40)

# Boîte crânienne : (y, demi-larg. dessus, joues, bas, z dessus, z bas) ; le rostre est fait
# de barres ouvertes devant elle
SKULL = [(-2.7, 0.45, 0.62, 0.55, 3.7, 2.85), (-3.2, 0.5, 0.7, 0.58, 3.85, 2.8),
         (-3.8, 0.44, 0.62, 0.5, 3.82, 2.85), (-4.35, 0.3, 0.42, 0.36, 3.62, 2.95)]
EYE = (-3.75, 3.38)
ROSTRUM_NODE = Vector((0, -5.3, 3.22))   # museau court, large et arrondi
HEAD = dict(part="Head")


def I(k):
    """Index de vertèbre exprimé sur une colonne de référence à 26 vertèbres."""
    return round(k * (len(SPINE) - 1) / 25)


def body_bone(i):
    return f"Body{min(5, i * 5 // (len(SPINE) - 1) + 1)}"


def jaw_arc(width, length, z_front, z_back, n=17, y_back=-3.0):
    """Arc de mâchoire en U arrondi ; la ligne de gueule s'incurve (haute devant, qui rejoint
    la charnière à l'arrière) au lieu d'un fer à cheval plat."""
    pts = []
    for i in range(n):
        th = -math.pi / 2 + math.pi * i / (n - 1)
        c = math.cos(th)
        pts.append(Vector((width * math.sin(th) * (1 - 0.1 * c), y_back - length * c,
                           z_back + (z_front - z_back) * c ** 1.5)))
    return pts


def jaw_out(p, width, length, y_back=-3.0):
    """Normale horizontale vers l'extérieur de l'arc (ellipse)."""
    v = Vector((p.x / width ** 2, (p.y - y_back) / length ** 2, 0))
    return v.normalized() if v.length > 1e-6 else Vector((0, -1, 0))


def skull_surface(y, side, frac):
    """Point sur le dessus/flanc du crâne : frac 0 = milieu du dessus, 1 = flanc."""
    zt, zb = a.width_at(SKULL, y, 4), a.width_at(SKULL, y, 5)
    z = zt - (zt - zb) * 0.35 * frac
    return Vector((side * a.side_width(SKULL, y, z) * frac * 0.98, y, z if frac else zt))


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    parent = "Root"
    n = len(SPINE) - 1
    for b in range(5):
        parent = rig.bone(f"Body{b + 1}", SPINE[b * n // 5], SPINE[(b + 1) * n // 5], parent)
    rig.bone("Caudal", SPINE[-1], (0, 9.6, 3.9), "Body5")
    rig.bone("Head", SPINE[0], (0, -5.4, 3.3), "Body1")
    rig.bone("Jaw", (0, -3.0, 2.35), (0, -5.0, 1.95), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        rig.bone(f"PecFin_{side}", (s * 0.6, -1.4, 2.6), (s * 3.0, 0.3, 1.2), "Body1")
        rig.fx(f"Eye{side}", (s * 0.5, EYE[0], EYE[1]), "Head")
    rig.fx("Mouth", (0, -4.2, 2.5), "Head")
    rig.fx("Heart", (0, -1.6, 2.65), "Body1")
    rig.fx("TailTip", (0, 9.6, 5.8), "Caudal")


# ---------------------------------------------------------------- tête

def build_skull(rig):
    """Chondrocrâne de requin ajouré : boîte crânienne percée de part en part (orbites,
    fenêtres), rostre en 3 barres ouvertes qui convergent vers un nœud, capsules nasales,
    visières sus-orbitaires, piliers pré/post-orbitaires."""
    H = "Head"
    skull = a.loft_profile("Skull", SKULL, droop=0.1)
    a.cut(skull, [a.hole_x((0, EYE[0], EYE[1]), 0.3, 0.25),
                  a.hole_x((0, -2.97, 3.08), 0.15, 0.12)]
          + [a.hole_along((sx * 0.2, -3.05, 3.85), (0, 0, 1), (1, 0, 0), 0.07, 0.13, depth=0.3)
             for sx in (-1, 1)]
          + [a.hole_along(skull_surface(-4.05, 0, 0), (0, 0.3, 1), (1, 0, 0), 0.15, 0.17,
                          depth=0.25)])
    rig.add(skull, H, "bone", **HEAD)
    # Crête sagittale qui se prolonge en barre dorsale du rostre
    dorsal = [skull_surface(-2.8, 0, 0), skull_surface(-3.6, 0, 0), skull_surface(-4.2, 0, 0),
              Vector((0, -4.75, 3.58)), Vector((0, -5.1, 3.42)), ROSTRUM_NODE]
    rig.add(r.tube("RostrumDorsal", [tuple(p + Vector((0, 0, 0.03))) for p in dorsal],
                   [0.07, 0.09, 0.1, 0.09, 0.08, 0.07], segments=6), H, "bone", **HEAD)
    for i, yy in enumerate((-3.2, -3.9)):
        rig.add(a.claw(f"CrestSpike{i}", skull_surface(yy, 0, 0) + Vector((0, 0, 0.08)),
                       (0, 0.6, 1), 0.28, 0.05, curl=-0.1, segments=4), H, "horn", **HEAD)
    rig.add(r.ico("RostralNode", 0.22, subdivisions=2, location=ROSTRUM_NODE,
                  scale=(1.7, 1.25, 1.05)), H, "bone", **HEAD)
    rig.add(r.tube("RostralRim", [tuple(ROSTRUM_NODE + Vector((0.4 * math.sin(t), -0.25 * math.cos(t),
                                                               -0.06)))
                                  for t in (-1.5, -0.9, -0.3, 0.3, 0.9, 1.5)], 0.035, segments=4),
            H, "bone_shade", **HEAD)
    for i in range(7):   # ampoules de Lorenzini sur le bout du museau
        x = -0.3 + 0.1 * i
        rig.add(r.ico(f"NodePore{i}", 0.032, subdivisions=1,
                      location=ROSTRUM_NODE + Vector((x, -0.25 * math.sqrt(1 - (x / 0.42) ** 2),
                                                      0.06 if i % 2 else -0.02))), H, "ink",
                **HEAD)
    # Fontanelle précérébrale (grande ouverture sur le dessus, à l'avant du crâne)
    font = skull_surface(-4.05, 0, 0)
    rig.add(a.ring_around("FontanelleRim", font, (0, 0.3, 1), 0.17, 0.04, segments=10), H,
            "bone_shade", **HEAD)
    for s in (-1, 1):
        # Barres latérales du rostre + entretoises (vide visible entre les barres)
        lat = [Vector((s * 0.3, -4.3, 2.98)), Vector((s * 0.33, -4.8, 3.05)),
               Vector((s * 0.31, -5.12, 3.14)), ROSTRUM_NODE + Vector((s * 0.24, 0, -0.02))]
        rig.add(r.tube(f"RostrumLat{s}", [tuple(p) for p in lat], [0.09, 0.085, 0.08, 0.07],
                       segments=6), H, "bone", **HEAD)
        for k, t in enumerate((0.25, 0.55)):   # bagues calcifiées sur les barres
            q, q2 = mr.along(lat, t), mr.along(lat, t + 0.05)
            rig.add(a.ring_around(f"LatBand{s}{k}", q, q2 - q, 0.1, 0.03, segments=8), H,
                    "bone_shade", **HEAD)
        for k in range(3):   # foramens sur le flanc du crâne
            yy = -2.85 - 0.22 * k
            rig.add(r.ico(f"Foramen{s}{k}", 0.04, subdivisions=1,
                          location=(s * a.side_width(SKULL, yy, 3.0), yy, 3.0 + 0.08 * k)), H,
                    "ink", **HEAD)
        for k, t in enumerate((0.35, 0.65)):
            rig.add(r.tube(f"RostrumBrace{s}{k}", [tuple(mr.along(lat, t)),
                                                   tuple(mr.along(dorsal[2:], t))], 0.035,
                           segments=4), H, "bone_shade", **HEAD)
        for i in range(5):
            p = mr.along(lat, 0.12 + 0.15 * i)
            rig.add(r.ico(f"Pore{s}{i}", 0.032, subdivisions=1,
                          location=p + Vector((s * 0.085, 0, -0.02))), H, "ink", **HEAD)
        # Capsule nasale bombée + narine
        rig.add(r.ico(f"NasalCapsule{s}", 0.24, subdivisions=2, location=(s * 0.38, -4.45, 2.95),
                      scale=(1, 1.15, 0.75)), H, "bone", **HEAD)
        rig.add(a.ring_around(f"NasalRidge{s}", (s * 0.38, -4.45, 2.98), (0, 0.2, 1), 0.25, 0.035,
                              segments=10), H, "bone_shade", **HEAD)
        rig.add(a.ring_around(f"NostrilRim{s}", (s * 0.46, -4.62, 2.82), (s * 0.3, -0.5, -0.8),
                              0.1, 0.03, segments=8), H, "bone_shade", **HEAD)
        rig.add(r.ico(f"Nostril{s}", 0.07, subdivisions=1, location=(s * 0.46, -4.62, 2.82)), H,
                "ink", **HEAD)
        # Orbite traversante : anneau hérissé, œil enfoncé, visière sus-orbitaire à denticules
        x = a.side_width(SKULL, EYE[0], EYE[1])
        rig.add(r.ico(f"Eye{s}", 0.14, subdivisions=2, location=(s * (x - 0.16), EYE[0], EYE[1])),
                H, "glow", glow=True)
        mr.spiky_orbit(rig, f"Orbit{s}", (s * x, EYE[0], EYE[1]), (s, 0, 0), 0.27, H, spikes=5,
                       **HEAD)
        shelf = [(s * 0.38, -4.3, 3.68), (s * 0.48, -3.75, 3.8), (s * 0.44, -3.2, 3.8)]
        vu = Vector((s, 0, 0.3)).normalized()
        rig.add(r.tube(f"VisorRim{s}", [tuple(Vector(q) + vu * h) for q, h
                                        in zip(shelf, [0.2, 0.36, 0.26])], 0.04, segments=4), H,
                "bone", **HEAD)
        rig.add(a.band(f"Visor{s}", shelf, [0.2, 0.36, 0.26], 0.08, up=(s, 0, 0.3), offset=0), H,
                "bone_shade", **HEAD)
        for i, (yy, w) in enumerate(((-4.15, 0.24), (-3.85, 0.34), (-3.55, 0.34), (-3.3, 0.28))):
            base = Vector((s * (0.46 + w), yy, 3.82 + 0.3 * w))
            rig.add(a.claw(f"VisorSpike{s}{i}", base, (s * 0.8, 0.5, 0.5), 0.22, 0.04, curl=-0.1,
                           segments=4), H, "horn", **HEAD)
        # Piliers pré- et post-orbitaires
        rig.add(r.tube(f"PostOrbital{s}", [(s * 0.72, -3.28, 3.84), (s * 0.82, -3.3, 3.4),
                                           (s * 0.72, -3.25, 2.95)], [0.09, 0.1, 0.08],
                       segments=6), H, "bone", **HEAD)
        rig.add(r.tube(f"PreOrbital{s}", [(s * 0.68, -4.12, 3.78), (s * 0.66, -4.25, 3.3),
                                          (s * 0.45, -4.4, 3.0)], [0.08, 0.085, 0.07],
                       segments=6), H, "bone", **HEAD)
        # Écailles osseuses, évent, cicatrices rougeoyantes
        pts = [skull_surface(yy, s, 0.3) + Vector((0, 0, 0.01)) for yy in (-2.85, -3.45, -4.15)]
        mr.scutes(rig, f"Scute{s}", pts, [Vector((s * 0.3, 0, 1))] * len(pts), H, size=0.08,
                  **HEAD)
        spir = Vector((s * a.side_width(SKULL, -2.95, 3.5), -2.95, 3.5))
        rig.add(a.ring_around(f"Spiracle{s}", spir, (s, 0, 0), 0.08, 0.03, segments=8), H,
                "bone_shade", **HEAD)
        rig.add(r.ico(f"SpiracleGlow{s}", 0.05, subdivisions=1, location=spir), H, "glow",
                glow=True)
        rig.add(a.ring_around(f"Fenestra{s}", (s * a.side_width(SKULL, -2.97, 3.08), -2.97, 3.08),
                              (s, 0, 0), 0.15, 0.035, segments=10), H, "bone_shade", **HEAD)
        mr.scar(rig, f"Scar{s}", skull_surface(-2.8, s, 0.45), skull_surface(-3.5, s, 0.6), H,
                seed=s + 3)
        mr.scar(rig, f"ScarB{s}", lat[0] + Vector((s * 0.08, 0, 0.02)),
                lat[1] + Vector((s * 0.08, 0, 0.02)), H, width=0.04, seed=s + 7)
        # 5 arcs branchiaux en C, branchiospines, filaments et fentes rougeoyantes
        for g in range(5):
            yy = -2.45 + 0.27 * g
            arc = [(s * 0.5, yy, 3.4), (s * 0.85, yy + 0.05, 2.75), (s * 0.78, yy, 2.15),
                   (s * 0.4, yy - 0.05, 1.95)]
            rig.add(r.tube(f"Gill{s}{g}", arc, [0.05, 0.065, 0.06, 0.04], segments=5), H,
                    "bone_shade", **HEAD)
            for k in range(4):
                p = mr.along(arc, 0.2 + 0.2 * k)
                rig.add(a.claw(f"Raker{s}{g}{k}", p, (-s, 0.1, 0.1), 0.16, 0.025, curl=0,
                               segments=4), H, "horn", **HEAD)
                rig.add(a.claw(f"Filament{s}{g}{k}", p, (s, 0.4, 0), 0.14, 0.02, curl=0.2,
                               segments=4), H, "gum", **HEAD)
            if g < 4:
                rig.add(r.tube(f"GillGlow{s}{g}", [(s * 0.62, yy + 0.13, 3.2),
                                                   (s * 0.86, yy + 0.15, 2.75),
                                                   (s * 0.74, yy + 0.13, 2.2)], 0.025, segments=4),
                        H, "glow", glow=True)


def build_jaws(rig):
    """Mâchoires arrondies : palatocarré et cartilage de Meckel en plaques qui s'évasent en
    bol (inclinées), ligne de gueule incurvée, mâchoire basse renflée vers la charnière.
    Beaucoup de grosses dents pleines et dentelées sur 3 rangées (pièce « Teeth »)."""
    H, J = "Head", "Jaw"
    teeth = dict(part="Teeth")
    UW, UL, LW, LL = 0.8, 2.0, 0.84, 2.05
    upper = jaw_arc(UW, UL, 2.88, 2.5)
    lower = jaw_arc(LW, LL, 1.88, 2.3)
    fr_u = [min(1.0, max(0.0, (-3.0 - p.y) / UL)) for p in upper]     # 1 devant, 0 à la charnière
    fr_l = [min(1.0, max(0.0, (-3.0 - p.y) / LL)) for p in lower]
    out_u = [jaw_out(p, UW, UL) for p in upper]
    out_l = [jaw_out(p, LW, LL) for p in lower]
    up_h = [0.26 + 0.2 * (1 - f) ** 1.5 + 0.08 * math.sin(math.pi * f) for f in fr_u]
    # profond à l'arrière, ventre bombé sur les côtés, menton fin : profil courbe, pas une planche
    lo_h = [0.28 + 0.3 * (1 - f) ** 1.5 + 0.16 * math.sin(math.pi * f) for f in fr_l]
    up_u = [Vector((0, 0, 1)) - o * 0.35 for o in out_u]      # le haut rentre vers le crâne
    lo_u = [Vector((0, 0, 1)) + o * 0.4 for o in out_l]       # le bas rentre : forme de bol
    rig.add(a.band("UpperJaw", upper, up_h, [0.15 + 0.06 * (1 - f) for f in fr_u], up=up_u,
                   offset=0), H, "bone_shade", **HEAD)
    rig.add(r.tube("UpperJawRim", [tuple(p + u.normalized() * h) for p, u, h
                                   in zip(upper, up_u, up_h)], 0.05, segments=5), H, "bone",
            **HEAD)
    rig.add(a.band("LowerJaw", lower, lo_h, [0.17 + 0.08 * (1 - f) for f in fr_l], up=lo_u,
                   offset=1), J, "bone", **HEAD)
    bottom = [p - u.normalized() * h for p, u, h in zip(lower, lo_u, lo_h)]
    rig.add(r.tube("LowerJawBase", [tuple(q) for q in bottom], 0.06, segments=5), J,
            "bone_shade", **HEAD)
    rig.add(r.ico("Symphysis", 0.14, subdivisions=1, location=bottom[8] + Vector((0, -0.04, 0.05)),
                  scale=(1.3, 1, 0.9)), J, "bone_shade", **HEAD)
    # Arêtes externes (mi-hauteur), alvéoles, pores et denticules : aucune face lisse
    for i in range(1, 16):
        p, o = upper[i], out_u[i]
        u = up_u[i].normalized()
        rig.add(r.ico(f"SocketU{i}", 0.065, subdivisions=1, location=p + o * 0.1 + u * 0.08), H,
                "bone", **HEAD)
        p, o = lower[i], out_l[i]
        u = lo_u[i].normalized()
        rig.add(r.ico(f"SocketL{i}", 0.065, subdivisions=1, location=p + o * 0.11 - u * 0.08), J,
                "bone", **HEAD)
        if i % 2:
            rig.add(r.ico(f"JawPore{i}", 0.03, subdivisions=1,
                          location=p + o * 0.15 - u * lo_h[i] * 0.72), J, "ink", **HEAD)
    rig.add(r.tube("UpperJawRidge", [tuple(p + o * 0.12 + u.normalized() * h * 0.6) for p, o, u, h
                                     in zip(upper, out_u, up_u, up_h)], 0.04, segments=4), H,
            "bone", **HEAD)
    rig.add(r.tube("LowerJawRidge", [tuple(p + o * 0.14 - u.normalized() * h * 0.5) for p, o, u, h
                                     in zip(lower, out_l, lo_u, lo_h)], 0.045, segments=4), J,
            "bone_shade", **HEAD)
    for i in (2, 4, 6, 10, 12, 14):
        q = bottom[i]
        rig.add(a.claw(f"ChinDenticle{i}", q, out_l[i] * 0.6 + Vector((0, 0.5, -0.7)), 0.2, 0.04,
                       curl=0, segments=4), J, "horn", **HEAD)
    # Gencives sombres à l'intérieur des arcs
    rig.add(r.tube("UpperGum", [tuple(p - o * 0.1 + Vector((0, 0, 0.05)))
                                for p, o in zip(upper, out_u)], 0.08, segments=5), H, "gum",
            **HEAD)
    rig.add(r.tube("LowerGum", [tuple(p - o * 0.1 - Vector((0, 0, 0.05)))
                                for p, o in zip(lower, out_l)], 0.09, segments=5), J, "gum",
            **HEAD)
    # 3 rangées de grosses dents (17 + 15 + 13 par mâchoire) ; les rangées de remplacement
    # sont couchées vers l'intérieur, comme chez un vrai requin
    for row, n in enumerate((19, 17, 15)):
        sc = 1 - 0.18 * row
        for (w, l, zf, zb), down, bone, big in (((UW, UL, 2.88, 2.5), -1, H, 1.0),
                                                ((LW, LL, 1.88, 2.3), 1, J, 0.85)):
            arc = jaw_arc(w - 0.1 * row, l - 0.14 * row, zf + down * 0.03 * row,
                          zb + down * 0.03 * row, n=n)
            for i in range(1, n - 1):
                p = arc[i]
                o = jaw_out(p, w - 0.1 * row, l - 0.14 * row)
                f = max(0.0, (-3.0 - p.y) / l)
                size = (0.24 + 0.24 * f) * sc * big
                width = size * (0.82 if row == 0 else 0.75)
                tip = p + Vector((0, 0, down * size)) - o * size * (0.12 + 0.45 * row)
                rig.add(mr.tooth(f"Tooth{bone}{row}{i}", p, tip, width, width * 0.38, o),
                        bone, "tooth", **teeth)
    for s in (-1, 1):
        # Charnière, hyomandibulaire, processus orbitaire, cartilages labiaux, cératohyal
        rig.add(r.ico(f"Hinge{s}", 0.2, subdivisions=1, location=(s * 0.8, -3.05, 2.42)), H,
                "bone", **HEAD)
        for k, dz in enumerate((0.16, -0.16)):
            rig.add(r.ico(f"HingeKnob{s}{k}", 0.1, subdivisions=1,
                          location=(s * 0.92, -3.1, 2.42 + dz)), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Hyomandibula{s}", [(s * 0.5, -2.75, 3.25), (s * 0.75, -2.85, 2.85),
                                            (s * 0.82, -3.0, 2.48)], [0.11, 0.09, 0.12],
                       segments=6), H, "bone", **HEAD)
        rig.add(r.tube(f"OrbitalProcess{s}", [(s * 0.62, -4.2, 2.95), (s * 0.52, -4.32, 3.05),
                                              (s * 0.4, -4.42, 3.05)], [0.11, 0.09, 0.08],
                       segments=6), H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Labial{s}", [(s * 0.88, -3.25, 2.95), (s * 0.97, -3.45, 2.45),
                                      (s * 0.9, -3.3, 1.85)], [0.04, 0.06, 0.04], segments=5),
                H, "bone_shade", **HEAD)
        rig.add(r.tube(f"Ceratohyal{s}", [(s * 0.78, -3.1, 2.0), (s * 0.4, -3.5, 1.9),
                                          (0, -3.9, 1.92)], 0.06, segments=5), J, "bone_shade",
                **HEAD)
        for k, dy in enumerate((-0.12, 0.1)):
            rig.add(r.tube(f"Ligament{s}{k}", [(s * 0.78, -3.1 + dy, 2.7), (s * 0.86, -3.1 + dy, 2.42),
                                               (s * 0.8, -3.1 + dy, 2.12)], 0.035, segments=4), J,
                    "gum", **HEAD)
        # Hameçons rouillés plantés dans la mâchoire, avec leur chaîne
        q = bottom[5 if s < 0 else 11]
        mr.hook(rig, f"JawHook{s}", q + Vector((0, 0, 0.05)), (s * 0.3, -0.4, -1), J, chain=3,
                **HEAD)
    # Langue osseuse (basihyal) et gorge rougeoyante
    rig.add(a.blade("Tongue", (0, -3.2, 2.0), (0, -4.3, 1.86), 0.4, 0.08, width_end=0.22,
                    normal=(0, 0, 1)), J, "bone_shade", **HEAD)
    rig.add(r.ico("Throat", 0.3, subdivisions=2, location=(0, -3.4, 2.45), scale=(1.4, 1, 0.5)), H,
            "glow", glow=True)


# ---------------------------------------------------------------- corps

def build_body(rig):
    n = len(SPINE)
    for i, p in enumerate(SPINE):
        t = i / (n - 1)
        nxt, prv = SPINE[min(i + 1, n - 1)], SPINE[max(i - 1, 0)]
        tan = (nxt - prv).normalized()
        size = 0.42 - 0.22 * t
        bone = body_bone(i)
        rig.add(a.vertebra(f"V{i}", p, tan, size, spine=0.8 - 0.4 * t, lean=-0.3,
                           transverse=t < 0.55), bone, "bone")
        if i < n - 1:
            rig.add(a.disc(f"VD{i}", p.lerp(nxt, 0.5), tan, size), bone, "disc")
        top = p + Vector((0, 0, size * 0.7 + size * (0.8 - 0.4 * t)))
        if i % 2 == 0:   # denticules crochus le long du dos
            rig.add(a.claw(f"Dent{i}", top - Vector((0, 0, 0.05)), (0, 0.8, 0.6), 0.22, 0.04,
                           curl=0.2, segments=4), bone, "horn")
        for s in (-1, 1):
            if i % 2 == 1 and t < 0.55:   # ligne latérale lumineuse, au bout des apophyses
                rig.add(r.ico(f"Lateral{i}{s}", 0.05, subdivisions=1,
                              location=p + Vector((s * size * 1.0, 0, size * 0.5))), bone, "glow",
                        glow=True)
            if 0.04 <= t <= 0.36 and i % 2 == 0:   # côtes courtes à petite pique
                rig.add(a.rib(f"Rib{i}{s}", p - Vector((0, 0, 0.1)), 0.55, 0.9, s, sweep=-0.15,
                              radius=0.06, segments=5), bone, "bone")
                rig.add(a.claw(f"RibSpike{i}{s}", p + Vector((s * 0.6, 0, -0.45)), (s, 0.3, 0),
                               0.16, 0.03, curl=0, segments=4), bone, "horn")
        if t >= 0.48 and i % 2 == 0:   # arcs hémaux sous la queue
            down = p - Vector((0, 0, size * 0.4))
            rig.add(a.blade(f"Haemal{i}", down, down + Vector((0, 0.25, -size * 1.6)), size * 0.45,
                            size * 0.15, width_end=size * 0.2, normal=(1, 0, 0), bevel=0), bone,
                    "bone_shade")
    # Ceinture scapulaire : arc sous le ventre qui relie les deux pectorales
    girdle = [(0.6, -1.15, 2.6), (0.5, -1.2, 2.15), (0, -1.25, 1.95), (-0.5, -1.2, 2.15),
              (-0.6, -1.15, 2.6)]
    rig.add(r.tube("ScapularGirdle", girdle, 0.08, segments=6), "Body1", "bone")
    for s in (-1, 1):
        rig.add(r.tube(f"Scapula{s}", [(s * 0.6, -1.15, 2.6), (s * 0.5, -1.0, 3.4)], [0.07, 0.04],
                       segments=5), "Body1", "bone")
    rig.add(r.tube("PelvicGirdle", [tuple(SPINE[I(14)] + Vector((s * 0.35, 0, -0.5))) for s in (1, -1)],
                   0.06, segments=5), body_bone(I(14)), "bone")
    # Cœur de sang derrière les branchies + veines
    rig.add(a.crystal("Heart", (0, -1.6, 2.65), 0.25, 0.7), "Body1", "glow", glow=True)
    for s in (-1, 1):
        rig.add(r.tube(f"Vein{s}", [(0, -1.6, 2.65), (s * 0.3, -2.1, 2.5), (s * 0.4, -2.5, 2.4)],
                       0.03, segments=4), "Body1", "glow", glow=True)


def build_fins(rig):
    F = "Fins"
    top = lambda i, dz=0.55: SPINE[i] + Vector((0, 0, dz))  # noqa: E731
    bot = lambda i: SPINE[i] - Vector((0, 0, 0.45))  # noqa: E731
    mr.fin(rig, "Dorsal", [top(I(7)), top(I(9)), top(I(11))],
           [top(I(7)) + Vector((0, 0.6, 1.5)), top(I(8)) + Vector((0, 1.3, 2.6)),
            top(I(10)) + Vector((0, 1.6, 1.6)), top(I(11)) + Vector((0, 1.1, 0.5))], "Body2",
           part=F, rays=10, seed=1)
    mr.fin(rig, "Dorsal2", [top(I(19), 0.35), top(I(21), 0.35)],
           [top(I(19)) + Vector((0, 0.6, 0.7)), top(I(21)) + Vector((0, 0.5, 0.2))], "Body4",
           part=F, rays=4, seed=2)
    mr.fin(rig, "Anal", [bot(I(19)), bot(I(21))], [bot(I(19)) + Vector((0, 0.6, -0.7)),
                                                    bot(I(21)) + Vector((0, 0.5, -0.25))], "Body4",
           part=F, rays=4, seed=3)
    for s, side in ((1, "L"), (-1, "R")):
        root = [Vector((s * 0.55, -1.6, 2.55)), Vector((s * 0.6, -1.15, 2.55)),
                Vector((s * 0.55, -0.7, 2.6))]
        mr.fin(rig, f"Pec{s}", root, [Vector((s * 1.8, -1.25, 1.95)), Vector((s * 3.1, 0.3, 1.2)),
                                      Vector((s * 2.3, 0.35, 1.55)), Vector((s * 1.2, -0.2, 2.1))],
               f"PecFin_{side}", part=F, rays=10, seed=4 + s)
        root = [SPINE[I(13)] + Vector((s * 0.35, 0, -0.45)), SPINE[I(15)] + Vector((s * 0.3, 0, -0.45))]
        mr.fin(rig, f"Pelvic{s}", root, [root[0] + Vector((s * 0.8, 0.6, -0.65)),
                                         root[1] + Vector((s * 0.4, 0.4, -0.3))], "Body3",
               part=F, rays=4, seed=8 + s)
    base = SPINE[-1]
    mr.fin(rig, "Caudal", [base + Vector((0, -0.45, 0.35)), base, base + Vector((0, -0.45, -0.35))],
           [Vector((0, 8.9, 5.0)), Vector((0, 9.95, 6.35)), Vector((0, 9.15, 4.1)),
            Vector((0, 9.65, 1.75)), Vector((0, 8.7, 2.3))], "Caudal", part=F, rays=14, seed=11)


def build_harpoons(rig):
    """Harpons rouillés plantés dans le dos, avec chaînes qui pendent."""
    for k, (i, s, d) in enumerate(((I(9), 1, (0.55, 0.35, 1)), (I(16), -1, (-0.5, 0.6, 1)))):
        bone = body_bone(i)
        base = SPINE[i] + Vector((s * 0.25, 0, 0.35))
        d = Vector(d).normalized()
        end = base + d * 2.0
        rig.add(r.tube(f"HarpoonShaft{k}", [tuple(base - d * 0.3), tuple(end)], 0.05, segments=6),
                bone, "rust")
        for j, t in enumerate((0.45, 0.7)):   # bagues de fer sur le manche
            rig.add(a.ring_around(f"HarpoonBand{k}{j}", base.lerp(end, t), d, 0.07, 0.02,
                                  segments=8), bone, "rust")
        side, up = a._basis(d)
        for b in (-1, 1):
            rig.add(a.claw(f"HarpoonBarb{k}{b}", base + d * 0.05, d + side * b * 0.8, 0.25, 0.04,
                           curl=0, segments=4), bone, "rust")
        rig.add(a.ring_around(f"HarpoonEye{k}", end, d, 0.1, 0.03, segments=10), bone, "rust")
        p = end + Vector((0, 0, -0.12))
        for j in range(6):
            axis = Vector((1, 0, 0)) if j % 2 == 0 else Vector((0, 1, 0))
            rig.add(a.ring_around(f"Chain{k}{j}", p, axis, 0.1, 0.025, segments=8), bone, "rust")
            p = p + Vector((0.05 * s, 0.04, -0.16))
        rig.add(r.ico(f"BloodGlow{k}", 0.1, subdivisions=1, location=base + d * 0.12), bone,
                "glow", glow=True)
        mr.scar(rig, f"Wound{k}", base + side * 0.1, base + Vector((0, 0.5, -0.25)), bone, seed=k)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_skull(rig)
    build_jaws(rig)
    build_body(rig)
    build_fins(rig)
    build_harpoons(rig)
    return rig
