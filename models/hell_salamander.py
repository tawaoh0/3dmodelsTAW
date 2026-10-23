"""Salamandre géante squelette (≈ 9 studs de long, rampante) — créature animable.
Pack « Enfers volcaniques », créature 4.

Animal modèle : la salamandre géante de Chine (Andrias) — crâne très plat et large, troué de
grandes fenêtres, minuscules yeux sur le dessus, museau arrondi, gueule en U bordée de
nombreuses dents (+ rangée vomérienne au palais) ; pattes courtes écartées, 4 doigts devant,
5 derrière ; longue queue aplatie. Emprunts : glandes parotoïdes (salamandre tachetée) et
branchies externes plumeuses (axolotl), ici en flammes.

Identité : os ocre-ambre tachetés de noir (motif de salamandre de feu) ; pas de cornes mais
une **crête de flammes** espacée (grandes épines neurales + langues de feu), branchies de
feu et glandes de poison lumineuses derrière les yeux ; silhouette basse et rampante ;
thème d'effets « sulfur » (fumée de soufre + flammèches).

5 pièces Roblox : corps, Head, Tail, Legs, + lumineux.
Os : Root, Spine1-3, Head, Jaw, Tail1-4, Front/Hind{Upper,Lower,Hand}_{L,R}, + FX_*.
"""
import math

from mathutils import Vector

from lib import anatomy as a
from lib import creature as c
from lib import marine as mr
from lib import roblox as r

COLORS = {
    "bone": "#b4772c",
    "bone_shade": "#5a3216",
    "tooth": "#f6eedb",
    "horn": "#171010",
    "horn_tip": "#ff3a10",
    "disc": "#3a1c0e",
    "gum": "#6a1a12",
    "ink": "#120c08",
    "glow": "#ff3a10",
    "glow_hot": "#ffe27a",
}

EFFECT_THEME = "sulfur"

TEST_POSE = {
    "Jaw": (25, 0, 0),
    "Head": (-10, 0, 15),
    "Tail2": (0, 0, 25),
    "Tail3": (0, 0, -30),
    "FrontUpper_L": (0, 0, 30),
}

VIEW = (0.85, -1.0, 0.65)

SPINE = a.smooth_path([(0, -2.15, 1.25), (0, -1.2, 1.32), (0, 0.0, 1.35), (0, 1.2, 1.3)], 16)
TAIL = a.smooth_path([(0, 1.2, 1.3), (0.35, 2.6, 1.15), (-0.25, 4.0, 0.92), (0.3, 5.2, 0.72),
                      (0.1, 6.3, 0.55)], 24)
# Crâne plat et large : (y, demi-larg. dessus, flancs, bord dentaire, z dessus, z bas)
SKULL = [(-2.1, 0.55, 0.7, 0.65, 1.55, 1.05), (-2.6, 0.7, 0.86, 0.8, 1.62, 1.0),
         (-3.2, 0.68, 0.8, 0.78, 1.54, 1.02), (-3.7, 0.52, 0.6, 0.6, 1.44, 1.05),
         (-3.95, 0.35, 0.42, 0.42, 1.38, 1.08)]
EYE = (0.38, -2.75)            # (x, y) des petits yeux, dans les grandes fenêtres
WIN = (0.38, -2.75, 0.24, 0.5)  # fenêtre orbito-temporale (x, y, demi-axes)
Y_BACK = -2.2
UPPER = (0.8, 1.72, 1.04, 1.04)
LOWER = (0.84, 1.78, 0.78, 0.98)
HEAD = dict(part="Head")
TAILP = dict(part="Tail")
LEGS = dict(part="Legs")


def tangent(path, i):
    return (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()


def spine_bone(i):
    return ("Spine1", "Spine2", "Spine3")[min(2, i * 3 // len(SPINE))]


def tail_bone(i):
    return f"Tail{min(4, i * 4 // len(TAIL) + 1)}"


def arc(width, length, z_front, z_back, n=17):
    pts = []
    for i in range(n):
        th = -math.pi / 2 + math.pi * i / (n - 1)
        cth = math.cos(th)
        pts.append(Vector((width * math.sin(th) * (1 - 0.05 * cth), Y_BACK - length * cth,
                           z_back + (z_front - z_back) * cth ** 1.3)))
    return pts


def out_of(p, width, length):
    v = Vector((p.x / width ** 2, (p.y - Y_BACK) / length ** 2, 0))
    return v.normalized() if v.length > 1e-6 else Vector((0, -1, 0))


def front_leg(s):
    return (Vector((s * 0.62, -1.35, 1.2)), Vector((s * 1.45, -1.55, 1.4)),
            Vector((s * 1.7, -1.85, 0.3)), Vector((s * 1.85, -2.1, 0.08)))


def hind_leg(s):
    return (Vector((s * 0.55, 0.95, 1.22)), Vector((s * 1.45, 1.1, 1.45)),
            Vector((s * 1.75, 1.3, 0.3)), Vector((s * 1.95, 1.5, 0.08)))


def spots(rig, name, hit, points, bone, size=0.08, **kw):
    """Taches noires de salamandre de feu posées sur une surface (lancer de rayons)."""
    for k, (x, y) in enumerate(points):
        p, _ = hit((x, y, 9))
        if p is not None:
            rig.add(r.ico(f"{name}{k}", size, subdivisions=1, location=p,
                          scale=(1.2, 1.0, 0.35)), bone, "ink", **kw)


# ---------------------------------------------------------------- rig

def build_rig(rig):
    rig.bone("Root", (0, 0, 0), (0, 0, 1))
    rig.bone("Spine3", SPINE[-1], SPINE[10], "Root")
    rig.bone("Spine2", SPINE[10], SPINE[5], "Spine3")
    rig.bone("Spine1", SPINE[5], SPINE[0], "Spine2")
    rig.bone("Head", SPINE[0], (0, -3.95, 1.3), "Spine1")
    rig.bone("Jaw", (0, Y_BACK, 1.0), (0, -3.95, 0.82), "Head")
    parent = "Spine3"
    n = len(TAIL) - 1
    for k in range(4):
        parent = rig.bone(f"Tail{k + 1}", TAIL[k * n // 4], TAIL[(k + 1) * n // 4], parent)
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, parent in (("Front", front_leg(s), "Spine1"), ("Hind", hind_leg(s), "Spine3")):
            rig.bone(f"{prefix}Upper_{side}", pts[0], pts[1], parent)
            rig.bone(f"{prefix}Lower_{side}", pts[1], pts[2], f"{prefix}Upper_{side}")
            rig.bone(f"{prefix}Hand_{side}", pts[2], pts[3], f"{prefix}Lower_{side}")
        rig.fx(f"Eye{side}", (s * EYE[0], EYE[1], 1.38), "Head")
        rig.fx(f"Gills{side}", (s * 0.95, -2.0, 1.75), "Head")
    rig.fx("Heart", (0, -0.6, 0.95), "Spine2")
    rig.fx("Mouth", (0, -3.3, 0.95), "Head")
    rig.fx("TailFlame", TAIL[-1] + Vector((0, 0, 0.5)), "Tail4")


# ---------------------------------------------------------------- tête

def build_head(rig):
    H, J = "Head", "Jaw"
    skull = a.loft_profile("Skull", SKULL, droop=0.08)
    hit = a.surface_caster(skull)
    # Crâne de salamandre = cadre osseux : immenses fenêtres orbito-temporales (l'œil y est
    # suspendu), narines, foramen pariétal — on voit à travers
    holes = [a.hole_along((0, -2.35, 1.5), (0, 0, 1), (1, 0, 0), 0.06, 0.06, depth=0.6)]
    for s in (-1, 1):
        holes += [a.hole_along((s * WIN[0], WIN[1], 1.4), (0, 0, 1), (1, 0, 0), WIN[2], WIN[3],
                               depth=0.8),
                  a.hole_along((s * 0.2, -3.62, 1.4), (0, 0, 1), (1, 0, 0), 0.09, 0.1, depth=0.6)]
    a.cut(skull, holes)
    rig.add(skull, H, "bone", **HEAD)

    def top(x, y):
        p, _ = hit((x, y, 9))
        return p

    # Rebords des fenêtres, arête médiane, crêtes latérales à verrues
    rig.add(r.tube("Midline", [tuple(top(0, y) + Vector((0, 0, 0.01))) for y in
                               (-2.15, -2.6, -3.1, -3.6, -3.85)], [0.04, 0.05, 0.05, 0.04, 0.03],
                   segments=4), H, "bone_shade", **HEAD)
    for s in (-1, 1):
        # Rebord épais des grandes fenêtres, épines sur le rebord, œil suspendu sur un pédoncule
        ring = [top(s * (WIN[0] + WIN[2] * 1.12 * math.cos(t)), WIN[1] + WIN[3] * 1.08 * math.sin(t))
                for t in (2 * math.pi * k / 14 for k in range(14))]
        if all(p is not None for p in ring):
            rig.add(r.tube(f"WinRim{s}", [tuple(p + Vector((0, 0, 0.02))) for p in ring], 0.05,
                           segments=5, closed=True), H, "bone_shade", **HEAD)
            for k in (2, 5, 9, 12):
                rig.add(a.claw(f"RimSpike{s}{k}", ring[k], (s * 0.3, 0.3, 1), 0.18, 0.035, curl=-0.1,
                               segments=4), H, "horn", **HEAD)
        eye_c = Vector((s * EYE[0], EYE[1], 1.38))
        rig.add(r.ico(f"Eye{s}", 0.11, subdivisions=2, location=eye_c), H, "glow", glow=True)
        rig.add(r.tube(f"EyeStalk{s}", [tuple(eye_c - Vector((0, 0, 0.08))),
                                        (s * EYE[0], EYE[1], 1.12)], [0.05, 0.06], segments=5), H,
                "bone_shade", **HEAD)
        rig.add(a.ring_around(f"EyeCup{s}", eye_c - Vector((0, 0, 0.03)), (0, 0, 1), 0.12, 0.03,
                              segments=10), H, "bone", **HEAD)
        # Barre osseuse (os ptérygoïde) visible au fond de la fenêtre
        rig.add(r.tube(f"Pterygoid{s}", [(s * 0.2, -2.25, 1.12), (s * 0.4, -2.75, 1.1),
                                         (s * 0.5, -3.2, 1.12)], 0.045, segments=4), H, "bone",
                **HEAD)
        rig.add(a.ring_around(f"NarisRim{s}", top(s * 0.2, -3.5) or Vector((s * 0.2, -3.5, 1.42)),
                              (0, 0, 1), 0.1, 0.03, segments=8), H, "bone_shade", **HEAD)
        # Glandes parotoïdes lumineuses derrière les yeux, bourrelet osseux autour
        par = top(s * 0.45, -2.15) + Vector((0, 0, 0.02))
        rig.add(r.ico(f"Parotoid{s}", 0.17, subdivisions=2, location=par, scale=(0.9, 1.5, 0.55)),
                H, "glow", glow=True)
        rig.add(a.ring_around(f"ParotoidRim{s}", par, (0, 0, 1), 0.2, 0.035, segments=10), H,
                "bone_shade", **HEAD)
        # Verrues de la ligne latérale le long du bord du crâne
        for k in range(7):
            yy = -2.3 - 0.22 * k
            p = Vector((s * a.side_width(SKULL, yy, 1.3) * 1.0, yy, 1.3))
            rig.add(r.ico(f"Wart{s}{k}", 0.06 - 0.003 * k, subdivisions=1, location=p), H,
                    "bone_shade", **HEAD)
        # Branchies de feu plumeuses (3 de chaque côté)
        for k in range(3):
            base = Vector((s * 0.72, -2.15 + 0.18 * k, 1.2 + 0.06 * k))
            d = Vector((s * 0.7, 0.35 + 0.25 * k, 0.55 - 0.15 * k)).normalized()
            stalk = [base, base + d * 0.35, base + d * 0.7 + Vector((0, 0.1, 0.05))]
            rig.add(r.tube(f"GillStalk{s}{k}", [tuple(p) for p in stalk], [0.05, 0.04, 0.025],
                           segments=4), H, "bone", **HEAD)
            for j in range(3):
                q = mr.along(stalk, 0.35 + 0.3 * j)
                rig.add(a.crystal(f"GillFlame{s}{k}{j}", q, 0.04, 0.3, sides=4), H, "glow",
                        glow=True)
        mr.scar(rig, f"Crack{s}", top(s * 0.12, -2.25), top(s * 0.15, -2.9), H, width=0.04, seed=s)
    spots(rig, "SkullSpot", hit, [(0.12, -2.55), (-0.1, -3.0), (0.08, -3.35), (-0.45, -3.55),
                                  (0.45, -3.6), (0.7, -2.2), (-0.72, -2.3)], H, size=0.06, **HEAD)
    # Rangée du haut + rangée vomérienne au palais, gencive
    upper = arc(*UPPER)
    rig.add(a.band("Maxilla", upper, 0.1, 0.12, offset=0), H, "bone_shade", **HEAD)
    rig.add(r.tube("UpperGum", [tuple(p - out_of(p, UPPER[0], UPPER[1]) * 0.06) for p in upper],
                   0.05, segments=4), H, "gum", **HEAD)
    for i, p in enumerate(upper[1:-1], 1):
        o = out_of(p, UPPER[0], UPPER[1])
        f = max(0.0, (Y_BACK - p.y) / UPPER[1])
        size = 0.14 + 0.12 * f + (0.1 if i in (6, 10) else 0)
        rig.add(mr.tooth(f"UpTooth{i}", p, p + Vector((0, 0, -size)) - o * 0.05, size * 0.42,
                         size * 0.36, o, curl=0.12), H, "tooth", **HEAD)
    vomer = arc(UPPER[0] - 0.3, UPPER[1] - 0.35, 1.07, 1.07, n=11)
    for i, p in enumerate(vomer[2:-2]):
        rig.add(mr.tooth(f"VomerTooth{i}", p, p + Vector((0, 0.03, -0.13)), 0.08, 0.04,
                         out_of(p, UPPER[0] - 0.3, UPPER[1] - 0.35)), H, "tooth", **HEAD)
    # Mâchoire en U entrouverte, bombée, avec dents
    lower = arc(*LOWER)
    lo = [out_of(p, LOWER[0], LOWER[1]) for p in lower]
    fr = [max(0.0, min(1.0, (Y_BACK - p.y) / LOWER[1])) for p in lower]
    lh = [0.2 + 0.06 * math.sin(math.pi * f) for f in fr]
    lu = [Vector((0, 0, 1)) + o * 0.4 for o in lo]
    rig.add(a.band("Mandible", lower, lh, 0.14, up=lu, offset=1), J, "bone", **HEAD)
    rig.add(r.tube("MandibleBase", [tuple(p - u.normalized() * h) for p, u, h in zip(lower, lu, lh)],
                   0.045, segments=4), J, "bone_shade", **HEAD)
    rig.add(r.tube("LowerGum", [tuple(p - o * 0.06) for p, o in zip(lower, lo)], 0.05, segments=4),
            J, "gum", **HEAD)
    for i, p in enumerate(lower[1:-1], 1):
        f = fr[i]
        size = 0.13 + 0.1 * f + (0.09 if i in (5, 11) else 0)
        rig.add(mr.tooth(f"LowTooth{i}", p, p + Vector((0, 0, size)) - lo[i] * 0.05, size * 0.42,
                         size * 0.36, lo[i], curl=0.12), J, "tooth", **HEAD)
        if i % 3 == 0:
            rig.add(r.ico(f"JawPore{i}", 0.03, subdivisions=1,
                          location=p + lo[i] * 0.08 - Vector((0, 0, 0.11))), J, "ink", **HEAD)
    for s, i in ((-1, 0), (1, 16)):
        rig.add(r.ico(f"Hinge{s}", 0.11, subdivisions=1, location=lower[i] + Vector((0, 0.03, 0.08))),
                H, "bone_shade", **HEAD)
    rig.add(r.ico("Throat", 0.3, subdivisions=2, location=(0, -2.8, 1.0), scale=(1.6, 1.4, 0.4)),
            H, "glow", glow=True)


# ---------------------------------------------------------------- corps et queue

def build_body(rig):
    n = len(SPINE)
    for i in range(n):
        t = tangent(SPINE, i)
        side, up = a._basis(t)
        rig.add(a.vertebra(f"Vert{i}", SPINE[i], t, 0.22, spine=0.9, lean=0.3), spine_bone(i),
                "bone")
        if i < n - 1:
            rig.add(a.disc(f"Disc{i}", SPINE[i].lerp(SPINE[i + 1], 0.5), t, 0.22), spine_bone(i),
                    "disc")
        # Côtes courtes de salamandre, recourbées vers le bas
        if 2 <= i <= 13:
            for s in (-1, 1):
                rig.add(a.rib(f"Rib{i}{s}", SPINE[i], 0.42, 0.32, s, sweep=0.05, radius=0.05,
                              segments=5), spine_bone(i), "bone")
        # Crête de flammes espacée : grande épine neurale + langue de feu
        if i % 2 == 0 and i > 0:
            h = 0.45 + 0.25 * math.sin(math.pi * i / (n - 1))
            rig.add(a.claw(f"CrestSpine{i}", SPINE[i] + up * 0.15, up - t * 0.25, h, 0.05, curl=0,
                           segments=4), spine_bone(i), "bone_shade")
            rig.add(a.crystal(f"CrestFlame{i}", SPINE[i] + up * 0.25 + t * 0.15, 0.07, h * 1.3,
                              sides=5), spine_bone(i), "glow", glow=True)
        if i % 3 == 1:
            rig.add(r.ico(f"BackSpot{i}", 0.06, subdivisions=1,
                          location=SPINE[i] + up * 0.12 + side * 0.16 * (-1) ** i,
                          scale=(1, 1, 0.4)), spine_bone(i), "ink")
    # Ceintures : omoplates et bassin plats
    for s in (-1, 1):
        sh = front_leg(s)[0]
        rig.add(a.blade(f"Scapula{s}", SPINE[3] + Vector((s * 0.2, 0, 0.05)), sh, 0.4, 0.06,
                        width_end=0.22, normal=(0, 0.3, 1)), "Spine1", "bone")
        hp = hind_leg(s)[0]
        rig.add(a.blade(f"Ilium{s}", SPINE[-2] + Vector((s * 0.15, 0, 0.05)), hp, 0.38, 0.06,
                        width_end=0.22, normal=(0, -0.3, 1)), "Spine3", "bone")
    # Cœur de feu sous la colonne
    for k, (dx, dy, h) in enumerate(((0, -0.6, 0.5), (0.15, -0.4, 0.35), (-0.15, -0.8, 0.35))):
        rig.add(a.crystal(f"FireHeart{k}", (dx, dy, 0.82), 0.1, h, sides=6), "Spine2", "glow",
                glow=True)
    rig.add(r.tube("HeartHang", [(0, -0.6, 1.25), (0, -0.6, 0.95)], 0.03, segments=4), "Spine2",
            "bone_shade")
    # Queue aplatie : vertèbres, épines hautes en haut, chevrons en bas, flammes espacées
    nt = len(TAIL)
    for i in range(nt):
        t = tangent(TAIL, i)
        side, up = a._basis(t)
        size = 0.2 - 0.12 * i / (nt - 1)
        bone = tail_bone(i)
        rig.add(a.vertebra(f"TailVert{i}", TAIL[i], t, size, spine=1.6, lean=0.4,
                           transverse=i < 8), bone, "bone", **TAILP)
        if i < nt - 1:
            rig.add(a.disc(f"TailDisc{i}", TAIL[i].lerp(TAIL[i + 1], 0.5), t, size), bone, "disc",
                    **TAILP)
        rig.add(a.claw(f"Chevron{i}", TAIL[i] - up * size * 0.4, -up + t * 0.5, size * 1.8,
                       size * 0.2, curl=0, segments=4), bone, "bone", **TAILP)
        if i % 3 == 0:
            rig.add(a.crystal(f"TailFlame{i}", TAIL[i] + up * size * 1.8, 0.06, 0.55 - 0.012 * i,
                              sides=5), bone, "glow", glow=True)
        if i % 4 == 2:
            rig.add(r.ico(f"TailSpot{i}", size * 0.4, subdivisions=1,
                          location=TAIL[i] + up * size * 0.5 + side * size * 0.45,
                          scale=(1, 1, 0.5)), bone, "ink", **TAILP)
    rig.add(a.crystal("TailTipFlame", TAIL[-1], 0.1, 0.7, sides=6), "Tail4", "glow", glow=True)


def build_legs(rig):
    for s, side in ((1, "L"), (-1, "R")):
        for prefix, pts, n_toes in (("Front", front_leg(s), 4), ("Hind", hind_leg(s), 5)):
            ub, lb, hb = (f"{prefix}Upper_{side}", f"{prefix}Lower_{side}",
                          f"{prefix}Hand_{side}")
            rig.add(a.long_bone(f"{prefix}Upper{s}", pts[0], pts[1], 0.12, segments=7), ub,
                    "bone", **LEGS)
            off = (pts[2] - pts[1]).cross(Vector((0, 1, 0))).normalized() * 0.07
            rig.add(a.long_bone(f"{prefix}Lower{s}", pts[1] + off, pts[2] + off, 0.08,
                                condyles=False, segments=6), lb, "bone", **LEGS)
            rig.add(a.long_bone(f"{prefix}Lower2{s}", pts[1] - off, pts[2] - off, 0.065,
                                condyles=False, segments=6), lb, "bone_shade", **LEGS)
            rig.add(a.ring_around(f"{prefix}Elbow{s}", pts[1], pts[2] - pts[1], 0.15, 0.035,
                                  segments=8), lb, "glow", glow=True)
            rig.add(r.ico(f"{prefix}Wrist{s}", 0.11, subdivisions=1, location=pts[2]), hb,
                    "bone_shade", **LEGS)
            # Doigts écartés à plat sur le sol, griffes noires
            for j in range(n_toes):
                ang = math.radians(-70 + 140 * j / (n_toes - 1))
                d = Vector((s * math.sin(ang + 0.4), -math.cos(ang + 0.4), 0))
                base = pts[2] + d * 0.08
                mid = base + d * 0.28 + Vector((0, 0, -0.17))
                end = mid + d * 0.22 + Vector((0, 0, -0.04))
                rig.add(a.long_bone(f"{prefix}Finger{s}{j}", base, mid, 0.04, condyles=False,
                                    segments=5), hb, "bone", **LEGS)
                rig.add(a.long_bone(f"{prefix}Finger2{s}{j}", mid, end, 0.035, condyles=False,
                                    segments=5), hb, "bone", **LEGS)
                rig.add(a.claw(f"{prefix}Claw{s}{j}", end, d + Vector((0, 0, -0.4)), 0.16, 0.035,
                               curl=0.3, segments=4), hb, "horn", **LEGS)


def build(pal):
    rig = c.Rig(pal)
    build_rig(rig)
    build_head(rig)
    build_body(rig)
    build_legs(rig)
    return rig
