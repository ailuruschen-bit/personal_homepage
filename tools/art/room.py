"""The carriage interior.

Drawn on a 720x480 canvas covering scene x in [-120, 600), then cut into the
central 480 plus a 120-wide extension on each side. The window wall is drawn
face-on; everything that recedes is built from the perspective model below.
"""
import random

import numpy as np
from PIL import Image, ImageDraw

import parts
import px
from parts import CYA, MAG
from px import F8, Cv, mix, mul, render, text_mask

OX, W, H = 120, 720, 480

WALL = (88, 104, 140)
WALL_LO = (62, 72, 108)
CEIL = (62, 66, 96)
STEEL = (112, 124, 160)
BRASS = (214, 170, 88)
SEAT = (150, 58, 78)
WOOD = (150, 98, 76)
WARM = (255, 200, 120)
AMBER = (255, 206, 110)

# ------------------------------------------------------------------ Geometry
# Where things are. build.py writes this out to src/scene/geometry.gen.ts and
# geometry.gen.css, and nothing under src/ repeats a coordinate by hand. Scene
# units on the 480 grid throughout.

# Interactive objects, in the order the page lists them. `at` is the object's
# top-left corner. `zone` (the snap region, x0 y0 x1 y1) and `light` (the pool of
# light on focus: centre x y, radii rx ry) are relative to `at`, so moving an
# object moves its focus target with it.
OBJECTS = {
    'projects': dict(at=(148, 288), zone=(-11, -9, 104, 88), light=(47, 40, 62, 52)),
    'about': dict(at=(316, 344), zone=(-10, -8, 42, 26), light=(16, 9, 30, 20)),
    'stack': dict(at=(318, 55), zone=(-10, -9, 78, 45), light=(34, 20, 48, 28)),
    'journey': dict(at=(173, 67), zone=(-7, -7, 127, 27), light=(67, 10, 78, 18)),
}

# The window opening (x y w h) and its corner radius. The page lays .win over it:
# the city is seen through it and the camera flies through it in the opening.
# The opening punched out of the carriage is one unit inside this on every side,
# so the frame overlaps the edge of .win and no seam shows.
WINDOW = (150, 124, 180, 140)
WINDOW_RADIUS = 10

# Where .cam zooms about, as an offset from the opening's top-left corner: the
# middle of the gap between the 9th and 10th blind slats, the gap the camera
# flies through. The blinds are laid out relative to the opening (dom.ts,
# scene.css), so this moves with the window.
CAM_GAP = (90, 85.808)

# ------------------------------------------------------------------ Perspective
# The compartment as a box in metres, seen in one-point perspective. The camera
# stands just inside the door looking straight at the window wall, which is
# therefore drawn face-on; everything that runs toward the camera (side walls,
# floor, ceiling, seats, the rack's underside) converges on the vanishing point.
#
# The vanishing point is the camera's zoom origin: the opening flies into the
# point the room converges on. The scale and the eye height are read off the
# window wall as it was already drawn: the window is 1.0 m wide (180 units) and
# the floor meets the wall at y = 440. That puts the camera at chest height,
# which is where the detective wears it. See docs/13, stage 1.
WALL_SCALE = 180  # scene units per metre on the window wall
WALL_DIST = 2.0  # metres from the camera to the window wall
FOCAL = WALL_SCALE * WALL_DIST
ROOM_HALF_WIDTH = 1.2  # the window wall runs 2.4 m between the side walls
ROOM_CEILING = 2.30


def vanishing_point():
    """Where everything receding meets: the camera's zoom origin."""
    return (WINDOW[0] + CAM_GAP[0], WINDOW[1] + CAM_GAP[1])


EYE = (440 - vanishing_point()[1]) / WALL_SCALE  # camera height, about 1.28 m


def P(X, Y, Z):
    """A point in the compartment (metres: X right of centre, Y up from the
    floor, Z away from the camera) projected into scene units."""
    vx, vy = vanishing_point()
    k = FOCAL / Z
    return (vx + X * k, vy - (Y - EYE) * k)


# The page's animated glows (.g-*), each x y w h. Two sit over light sources on
# the walls, one over the laptop and one over the window; those two are relative
# to the object they belong to.
GLOWS = {
    'lamp': (294, 88, 180, 180),
    'neon': (36, 90, 120, 200),
    'lap': ('projects', -34, -26, 140, 120),
    'out': ('window', -100, 26, 380, 260),
}


def geometry(masks):
    """What build.py writes out for the page: the window, and for every focusable
    object its snap zone, its light and, for drawn objects, the bounding box of
    its silhouette and the sprite cut from it. The window is focusable too: it snaps within 8 of the opening
    and its light is 1.2 times the opening."""
    wx, wy, ww, wh = WINDOW
    objects = {
        'cover': dict(
            zone=(wx - 8, wy - 8, wx + ww + 8, wy + wh + 8),
            light=(wx + ww / 2, wy + wh / 2, ww * 0.6, wh * 0.6),
        )
    }
    for key, o in OBJECTS.items():
        ax, ay = o['at']
        z, li = o['zone'], o['light']
        x0, y0, x1, y1 = masks[key].getbbox()
        objects[key] = dict(
            zone=(ax + z[0], ay + z[1], ax + z[2], ay + z[3]),
            light=(ax + li[0], ay + li[1], li[2], li[3]),
            box=(x0 - OX, y0, x1 - x0, y1 - y0),
            sprite=f'/assets/obj-{key}.webp',
        )
    glows = {}
    for key, gl in GLOWS.items():
        if isinstance(gl[0], str):
            ax, ay = (wx, wy) if gl[0] == 'window' else OBJECTS[gl[0]]['at']
            gl = (ax + gl[1], ay + gl[2], gl[3], gl[4])
        glows[key] = gl
    (bx0, by0), (bx1, by1) = P(-ROOM_HALF_WIDTH, ROOM_CEILING, WALL_DIST), P(ROOM_HALF_WIDTH, 0, WALL_DIST)
    vx, vy = vanishing_point()
    return dict(
        side=OX,
        perspective=dict(vx=vx, vy=vy, wall=(bx0, by0, bx1, by1)),
        window=dict(x=wx, y=wy, w=ww, h=wh, r=WINDOW_RADIUS),
        camera=dict(x=wx + CAM_GAP[0], y=wy + CAM_GAP[1]),
        glows=glows,
        objects=objects,
    )


def hole_mask():
    """The window opening as a 1x mask over the 480 scene, white where the
    carriage is cut away: one unit inside WINDOW, so the frame overlaps .win."""
    x, y, w, h = WINDOW
    m = Image.new('L', (480, 480), 0)
    ImageDraw.Draw(m).rounded_rectangle([x + 1, y + 1, x + w - 1, y + h - 1], WINDOW_RADIUS - 1, fill=255)
    return np.asarray(m)


class Off:
    """Canvas wrapper with an offset, so everything below is written in scene
    coordinates.

    It can also carry a tag. While a tag is set, every solid or lit shape drawn is
    recorded in that tag's silhouette mask as well; shadows, light and texture are
    not, because they are not part of an object's outline. build.py turns the masks
    into the objects' sprites and bounding boxes."""

    def __init__(self, cv, dx=OX, dy=0, tag=None, masks=None):
        self.cv, self.dx, self.dy, self.tag = cv, dx, dy, tag
        self.masks = {} if masks is None else masks

    def at(self, dx, dy, tag=None):
        """The same canvas shifted by (dx, dy), recording into silhouette `tag`."""
        return Off(self.cv, self.dx + dx, self.dy + dy, tag, self.masks)

    def _p(self, pts):
        return [(x + self.dx, y + self.dy) for x, y in pts]

    def _m(self):
        """Drawing handle on this tag's silhouette mask; None when untagged."""
        if self.tag is None:
            return None
        if self.tag not in self.masks:
            self.masks[self.tag] = Image.new('L', (self.cv.w, self.cv.h), 0)
        return ImageDraw.Draw(self.masks[self.tag])

    def _box(self, x, y, w, h):
        return [x + self.dx, y + self.dy, x + self.dx + w - 1, y + self.dy + h - 1]

    def _mrect(self, x, y, w, h):
        m = self._m()
        if m and w > 0 and h > 0:
            m.rectangle(self._box(x, y, w, h), fill=255)

    def _mline(self, pts, width):
        m = self._m()
        if m:
            m.line([(round(x), round(y)) for x, y in self._p(pts)], fill=255, width=max(1, round(width)))

    def rect(self, x, y, w, h, c):
        self.cv.rect(x + self.dx, y + self.dy, w, h, c)
        self._mrect(x, y, w, h)

    def px(self, x, y, c):
        self.cv.px(x + self.dx, y + self.dy, c)
        self._mrect(x, y, 1, 1)

    def line(self, pts, c, width=1):
        self.cv.line(self._p(pts), c, width)
        self._mline(pts, width)

    def poly(self, pts, c):
        self.cv.poly(self._p(pts), c)
        m = self._m()
        if m:
            m.polygon(self._p(pts), fill=255)

    def ellipse(self, x, y, w, h, c):
        self.cv.ellipse(x + self.dx, y + self.dy, w, h, c)
        m = self._m()
        if m:
            m.ellipse(self._box(x, y, w, h), fill=255)

    def rrect(self, x, y, w, h, r, c):
        self.cv.rrect(x + self.dx, y + self.dy, w, h, r, c)
        m = self._m()
        if m:
            m.rounded_rectangle(self._box(x, y, w, h), r, fill=255)

    def mask(self, x, y, m, c):
        self.cv.mask(x + self.dx, y + self.dy, m, c)
        if self._m():
            self.masks[self.tag].paste(255, (x + self.dx, y + self.dy), m)

    def lrect(self, x, y, w, h, c, k=1.0, body=None):
        self.cv.lrect(x + self.dx, y + self.dy, w, h, c, k, body)
        self._mrect(x, y, w, h)

    def lpx(self, x, y, c, k=1.0):
        self.cv.lpx(x + self.dx, y + self.dy, c, k)
        self._mrect(x, y, 1, 1)

    def lline(self, pts, c, k=1.0, width=1, body=None):
        self.cv.lline(self._p(pts), c, k, width, body)
        self._mline(pts, width)

    def fline(self, pts, c, k=0.0, width=1, body=None):
        self.cv.fline(self._p(pts), c, k, width, body)
        self._mline(pts, width)

    def lpoly(self, pts, c, k=1.0, body=None):
        p = self._p(pts)
        self.cv.d.polygon(p, fill=tuple(body or c) + (255,))
        self.cv.e.polygon(p, fill=mul(c, k))
        m = self._m()
        if m:
            m.polygon(p, fill=255)

    def lellipse(self, x, y, w, h, c, k=1.0, body=None):
        self.cv.lellipse(x + self.dx, y + self.dy, w, h, c, k, body)
        m = self._m()
        if m:
            m.ellipse(self._box(x, y, w, h), fill=255)

    # ---- not part of any outline
    def light(self, x, y, w, h, c, k=1.0):
        self.cv.light(x + self.dx, y + self.dy, w, h, c, k)

    def shadow(self, x, y, w, h, k=0.5, ell=False):
        self.cv.shadow(x + self.dx, y + self.dy, w, h, k, ell)

    def shade(self, x, y, w, h, k):
        parts.shade(self.cv, x + self.dx, y + self.dy, w, h, k)

    def speckle(self, x, y, w, h, amount, rnd, density=0.12):
        self.cv.speckle(x + self.dx, y + self.dy, w, h, amount, rnd, density)


def place(g, key, drawn_at):
    """Canvas for drawing interactive object `key`, recording its silhouette.

    The objects below were drawn before OBJECTS existed and still carry the
    absolute coordinates they were first drawn at; `drawn_at` is that top-left
    corner, and the canvas shifts everything to wherever OBJECTS puts the object
    now. An object drawn from scratch is written relative to its own corner and
    passes drawn_at=(0, 0).
    """
    ax, ay = OBJECTS[key]['at']
    return g.at(ax - drawn_at[0], ay - drawn_at[1], key)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ri(p):
    return (int(round(p[0])), int(round(p[1])))


# ------------------------------------------------------------------ Shell
def shell(g, rnd):
    L, Wd = -120, 720
    # ceiling
    g.rect(L, 0, Wd, 48, CEIL)
    for x in range(L, 600, 80):
        g.rect(x, 0, 1, 48, mul(CEIL, 0.7))
        g.rect(x + 1, 0, 1, 48, mul(CEIL, 1.15))
    g.speckle(L, 0, Wd, 48, 0.08, rnd, 0.2)
    for x0, w in ((-116, 100), (40, 400), (496, 100)):
        g.rect(x0 - 4, 27, w + 8, 12, (38, 40, 62))
        g.rect(x0 - 4, 27, w + 8, 1, (84, 88, 120))
        g.lrect(x0, 30, w, 6, (255, 222, 164), 0.85, body=(255, 240, 208))
        g.lrect(x0, 35, w, 1, (255, 196, 120), 0.7, body=(240, 200, 150))
        for x in range(x0 + 49, x0 + w, 50):
            g.rect(x, 29, 2, 8, (38, 40, 62))
    # ventilation grilles
    for x0 in (-60, 150, 300, 470):
        g.rect(x0, 8, 30, 10, (40, 42, 66))
        for y in range(10, 17, 2):
            g.rect(x0 + 2, y, 26, 1, (24, 26, 44))
    # cornice
    g.rect(L, 48, Wd, 10, (50, 54, 84))
    g.rect(L, 48, Wd, 1, (96, 102, 140))
    g.rect(L, 56, Wd, 2, (30, 32, 54))
    # upper wall: panelling with a faint diamond pattern
    g.rect(L, 58, Wd, 238, WALL)
    cvp = g.cv.im.load()
    d1, d2 = mul(WALL, 0.9), mul(WALL, 1.06)
    for y in range(58, 290):
        for x in range(0, W):
            a, b = (x + y) % 12, (x - y) % 12
            if a == 0 or b == 0:
                cvp[x, y] = d1 + (255,)
            elif a == 6 and b == 6:
                cvp[x, y] = d2 + (255,)
    g.speckle(L, 58, Wd, 238, 0.07, rnd, 0.3)
    # panel seams and rivets
    for x in (-92, -8, 30, 116, 364, 450, 488, 572):
        g.rect(x, 58, 1, 232, mul(WALL, 0.62))
        g.rect(x + 1, 58, 1, 232, mul(WALL, 1.18))
        for y in range(70, 288, 26):
            g.px(x - 3, y, mul(WALL, 1.35))
            g.px(x - 3, y + 1, mul(WALL, 0.6))
            g.px(x + 4, y, mul(WALL, 1.35))
            g.px(x + 4, y + 1, mul(WALL, 0.6))
    # water stains and scratches
    for _ in range(60):
        x, y = rnd.randrange(L, 600), rnd.randrange(60, 250)
        for i in range(rnd.randrange(8, 40)):
            g.shade(x, y + i, rnd.choice([1, 1, 2]), 1, 0.9)
    for _ in range(26):
        x, y = rnd.randrange(L, 600), rnd.randrange(110, 288)
        g.line([(x, y), (x + rnd.randrange(3, 12), y - rnd.randrange(1, 4))], mul(WALL, 1.16))
    # string course plus light strip
    g.rect(L, 288, Wd, 8, (70, 80, 118))
    g.rect(L, 288, Wd, 1, (128, 138, 176))
    g.rect(L, 294, Wd, 2, (36, 42, 70))
    g.lrect(L, 296, Wd, 2, (95, 242, 230), 0.8, body=(170, 250, 244))
    # lower wall: vertical ribbed panelling
    g.rect(L, 298, Wd, 142, WALL_LO)
    for x in range(L, 600, 6):
        g.rect(x, 298, 1, 138, mul(WALL_LO, 0.84))
        g.rect(x + 1, 298, 1, 138, mul(WALL_LO, 1.08))
    g.rect(L, 298, Wd, 2, mul(WALL_LO, 0.6))
    g.speckle(L, 298, Wd, 142, 0.08, rnd, 0.25)
    for x in (-8, 30, 116, 364, 450, 488):
        g.rect(x, 300, 2, 136, mul(WALL_LO, 0.6))
    # skirting and floor
    g.rect(L, 434, Wd, 6, (38, 42, 68))
    g.rect(L, 434, Wd, 1, (84, 90, 126))
    g.rect(L, 440, Wd, 40, (46, 48, 76))
    for x0 in range(-360, 840, 30):
        x1 = 240 + (x0 - 240) * 1.42
        g.line([(x0, 440), (x1, 480)], (28, 30, 50))
    for y in (449, 462):
        g.rect(L, y, Wd, 1, (28, 30, 50))
    g.speckle(L, 440, Wd, 40, 0.12, rnd, 0.3)
    # heater grille
    g.rect(168, 388, 146, 46, (52, 58, 90))
    g.rect(168, 388, 146, 1, (104, 112, 150))
    g.rect(171, 391, 140, 40, (20, 22, 40))
    for y in range(393, 430, 4):
        g.rect(172, y, 138, 2, (56, 62, 96))
        g.rect(172, y, 138, 1, (84, 92, 130))
        g.lrect(172, y + 2, 138, 1, (255, 120, 50), 0.16, body=(70, 36, 34))
    for x in (171, 310):
        g.px(x, 391, (130, 138, 170))
        g.px(x, 430, (130, 138, 170))


# ------------------------------------------------------------------ Luggage rack
def rack(g, rnd):
    # route map (the journey object)
    o = place(g, 'journey', (173, 67))
    o.shadow(172, 86, 136, 6, 0.6)
    o.rect(173, 67, 134, 20, (60, 66, 100))
    o.rect(173, 67, 134, 1, (120, 130, 170))
    o.rect(173, 86, 134, 1, (30, 32, 54))
    o.rect(176, 70, 128, 14, (16, 18, 36))
    o.lrect(186, 76, 108, 1, (150, 162, 214), 0.55)
    for i in range(7):
        x = 186 + i * 18
        if i == 2:
            o.lrect(x - 2, 74, 5, 5, (255, 70, 80), 1.0, body=(255, 150, 150))
            o.lpx(x, 76, (255, 230, 230), 1.0)
        else:
            c = (220, 226, 255) if i < 2 else (120, 130, 180)
            o.lrect(x - 1, 75, 3, 3, c, 0.9 if i < 2 else 0.5)
        o.lrect(x - 2, 81, 5, 1, (96, 104, 150), 0.3)
    o.lpx(298, 76, (150, 162, 214), 0.6)
    o.lpx(297, 75, (150, 162, 214), 0.6)
    o.lpx(297, 77, (150, 162, 214), 0.6)
    for x in (175, 304):
        o.px(x, 69, (150, 158, 190))
        o.px(x, 84, (150, 158, 190))
    # luggage, sitting on y = 92
    # cardboard box
    g.rect(28, 72, 36, 20, (176, 138, 98))
    g.rect(28, 72, 36, 2, (210, 174, 130))
    g.rect(28, 90, 36, 2, (120, 90, 66))
    g.rect(43, 72, 6, 20, (206, 186, 150))
    g.rect(52, 78, 9, 6, (236, 230, 214))
    g.rect(53, 80, 6, 1, (120, 60, 60))
    g.rect(53, 82, 4, 1, (90, 90, 110))
    g.shade(60, 72, 4, 20, 0.8)
    # rolled-up drawings
    g.rect(6, 86, 24, 6, (226, 222, 210))
    g.rect(6, 86, 24, 1, (250, 248, 240))
    g.rect(6, 90, 24, 2, (170, 166, 160))
    g.ellipse(27, 86, 5, 6, (190, 186, 178))
    g.px(29, 88, (90, 88, 96))
    g.rect(14, 86, 2, 6, (200, 70, 70))
    # holdall
    c = (60, 140, 138)
    g.rrect(96, 68, 55, 24, 7, c)
    g.rrect(98, 69, 51, 8, 4, mul(c, 1.28))
    g.rect(100, 84, 47, 7, mul(c, 0.74))
    g.rect(98, 77, 51, 1, mul(c, 0.6))
    for x in (110, 134):
        g.rect(x, 68, 4, 24, mul(c, 0.62))
        g.rect(x, 68, 1, 24, mul(c, 0.9))
        g.rect(x, 79, 4, 3, BRASS)
    g.line([(113, 68), (116, 63), (133, 63), (136, 68)], mul(c, 0.5))
    g.line([(114, 68), (117, 64), (132, 64), (135, 68)], mul(c, 0.8))
    g.rect(146, 78, 5, 9, (236, 226, 200))
    g.rect(147, 80, 3, 1, (150, 60, 60))
    g.px(148, 77, (40, 40, 56))
    # briefcase (the stack object)
    o = place(g, 'stack', (318, 55))
    lb = (150, 96, 62)
    o.rect(318, 58, 68, 34, lb)
    o.rect(318, 58, 68, 3, mul(lb, 1.3))
    o.rect(318, 61, 68, 6, mul(lb, 1.14))
    o.rect(318, 84, 68, 8, mul(lb, 0.74))
    o.rect(318, 58, 1, 34, mul(lb, 0.6))
    o.rect(385, 58, 1, 34, mul(lb, 0.55))
    o.rect(318, 91, 68, 1, mul(lb, 0.5))
    o.speckle(318, 58, 68, 34, 0.1, rnd, 0.3)
    for x in range(321, 384, 3):
        o.px(x, 63, mul(lb, 1.45))
        o.px(x, 88, mul(lb, 1.2))
    for x in (331, 368):
        o.rect(x, 58, 6, 34, mul(lb, 0.58))
        o.rect(x, 58, 1, 34, mul(lb, 0.8))
        o.rect(x, 70, 6, 5, BRASS)
        o.rect(x + 1, 71, 4, 3, mul(BRASS, 0.6))
        o.px(x + 1, 70, (255, 236, 170))
    o.rect(346, 55, 12, 3, (70, 42, 34))
    o.rect(347, 55, 10, 1, (120, 78, 56))
    o.rect(349, 61, 6, 5, BRASS)
    o.px(351, 63, (90, 60, 30))
    o.px(349, 61, (255, 236, 170))
    for x, y in ((318, 58), (384, 58), (318, 90), (384, 90)):
        o.rect(x, y, 2, 2, BRASS)
    o.ellipse(340, 74, 9, 9, (70, 170, 160))
    o.rect(343, 77, 3, 3, (236, 240, 240))
    o.rect(354, 78, 10, 7, (214, 70, 70))
    o.rect(354, 80, 10, 2, (240, 232, 220))
    # umbrella
    g.rect(398, 88, 42, 4, (44, 50, 84))
    g.rect(398, 88, 42, 1, (84, 92, 136))
    g.rect(412, 88, 2, 4, (150, 60, 70))
    g.rect(394, 89, 4, 2, (160, 166, 190))
    g.line([(440, 89), (446, 89), (447, 86), (445, 84)], BRASS)


# ------------------------------------------------------------------ Window and curtains
def window(g, rnd):
    # Drawn around an opening at (150, 124); shifted to wherever WINDOW is
    g = g.at(WINDOW[0] - 150, WINDOW[1] - 124)
    # brass rail
    g.shadow(118, 104, 244, 5, 0.6)
    for x in (128, 240, 352):
        g.rect(x, 97, 2, 5, (120, 92, 50))
    g.rect(120, 100, 240, 4, BRASS)
    g.rect(120, 100, 240, 1, (255, 232, 160))
    g.rect(120, 103, 240, 1, (130, 96, 50))
    for x in (114, 358):
        g.ellipse(x, 97, 9, 9, BRASS)
        g.px(x + 2, 99, (255, 240, 190))
        g.px(x + 3, 99, (255, 240, 190))
        g.rect(x + 2, 104, 5, 1, (130, 96, 50))
    # curtains, tied back on both sides
    cc = (58, 110, 96)
    for x0 in (123, 344):
        g.shadow(x0 - 1, 106, 16, 168, 0.62)
        for i in range(13):
            k = [0.72, 0.9, 1.15, 1.3, 1.05, 0.8, 0.66, 0.84, 1.1, 1.26, 1.0, 0.78, 0.62][i]
            g.rect(x0 + i, 104, 1, 164, mul(cc, k))
        for x in range(x0, x0 + 13, 2):
            g.rect(x, 100, 1, 5, (150, 112, 56))
        # tieback
        g.rect(x0, 196, 13, 3, BRASS)
        g.rect(x0, 196, 13, 1, (255, 232, 160))
        g.rect(x0, 200, 13, 2, mul(cc, 0.5))
        for i in range(13):
            hh = [0, 2, 4, 5, 4, 2, 0, 1, 3, 5, 4, 2, 0][i]
            g.rect(x0 + i, 268, 1, hh + 1, mul(cc, 0.9))
        g.rect(x0 + 6, 199, 1, 6, (190, 146, 70))
        g.rect(x0 + 5, 205, 3, 3, (230, 190, 100))
    # window frame
    fr = (104, 118, 158)
    g.shadow(133, 108, 214, 174, 0.55)
    g.rrect(136, 110, 208, 168, 18, (44, 50, 80))
    g.rrect(137, 111, 206, 166, 17, fr)
    g.rrect(139, 112, 202, 160, 16, mul(fr, 1.22))
    g.rrect(140, 115, 200, 160, 15, fr)
    g.rrect(144, 119, 192, 152, 13, mul(fr, 0.8))
    g.rrect(147, 121, 186, 146, 12, (36, 40, 66))
    g.speckle(137, 111, 206, 166, 0.07, rnd, 0.3)
    g.line([(156, 112), (324, 112)], (176, 188, 220))
    g.line([(156, 276), (324, 276)], (60, 68, 104))
    for x, y in ((145, 119), (334, 119), (145, 268), (334, 268), (240, 115), (240, 273), (141, 194), (338, 194)):
        g.rect(x, y, 2, 2, (190, 200, 228))
        g.px(x + 1, y + 2, (50, 56, 88))
        g.px(x + 2, y + 1, (50, 56, 88))
    # handle
    g.rect(232, 269, 16, 4, (60, 68, 104))
    g.rect(234, 270, 12, 2, (160, 170, 204))
    # sill
    g.shadow(129, 283, 222, 9, 0.5)
    g.rect(130, 277, 220, 6, mul(fr, 0.95))
    g.rect(130, 277, 220, 1, (184, 196, 228))
    g.rect(130, 282, 220, 1, (50, 56, 88))
    g.rect(132, 283, 216, 2, (40, 46, 74))
    # odds and ends on the sill: a succulent and a coin
    g.rect(154, 271, 9, 6, (176, 96, 70))
    g.rect(153, 270, 11, 2, (208, 124, 90))
    g.rect(155, 266, 2, 4, (86, 160, 110))
    g.rect(158, 264, 3, 6, (106, 184, 124))
    g.rect(161, 267, 2, 3, (76, 140, 100))
    g.px(159, 263, (150, 220, 160))
    # nameplate
    g.rect(221, 284, 39, 6, (26, 28, 48))
    g.rect(221, 284, 39, 1, (70, 76, 110))
    g.lrect(224, 286, 9, 2, AMBER, 0.85)
    g.lrect(236, 286, 4, 1, (120, 130, 170), 0.3)
    g.lrect(242, 286, 8, 1, (120, 130, 170), 0.3)
    g.lrect(236, 288, 12, 1, (120, 130, 170), 0.2)


# ------------------------------------------------------------------ Things on the walls
def poster(g, x, y, w, h, kind):
    g.shadow(x - 1, y + 1, w + 4, h + 3, 0.6)
    g.rect(x - 2, y - 2, w + 4, h + 4, (84, 60, 54))
    g.rect(x - 2, y - 2, w + 4, 1, (130, 98, 84))
    g.rect(x - 2, y + h + 1, w + 4, 1, (50, 36, 36))
    g.rect(x, y, w, h, (236, 226, 204))
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 14
    if kind == 'sunset':
        bands = [(52, 40, 110), (110, 52, 130), (190, 72, 120), (240, 120, 96), (252, 176, 110)]
        for i, c in enumerate(bands):
            g.rect(ix, iy + i * ih // 5, iw, ih // 5 + 1, c)
        g.ellipse(ix + iw // 2 - 8, iy + ih // 2 - 4, 16, 16, (255, 226, 150))
        for i in range(0, 16, 3):
            g.rect(ix + iw // 2 - 8, iy + ih // 2 + 5 + i, 16, 1, (240, 120, 96))
        g.poly([(ix, iy + ih), (ix, iy + ih - 14), (ix + 12, iy + ih - 26), (ix + 24, iy + ih - 12), (ix + 34, iy + ih - 20), (ix + iw, iy + ih - 6), (ix + iw, iy + ih)], (40, 30, 70))
        g.poly([(ix, iy + ih), (ix + 10, iy + ih - 8), (ix + 22, iy + ih - 3), (ix + 36, iy + ih - 10), (ix + iw, iy + ih - 2), (ix + iw, iy + ih)], (24, 20, 48))
        g.rect(ix, iy + ih, iw, 1, (24, 20, 48))
    elif kind == 'map':
        g.rect(ix, iy, iw, ih, (30, 44, 80))
        cols = [(255, 90, 110), (95, 242, 230), (255, 206, 110), (150, 220, 120)]
        for i, c in enumerate(cols):
            y0 = iy + 6 + i * (ih - 12) // 3
            pts = [(ix + 3, y0), (ix + iw // 3, y0), (ix + iw // 2, y0 + (6 if i % 2 else -5)), (ix + iw - 4, y0 + (6 if i % 2 else -5))]
            g.line(pts, c)
            for px_, py_ in pts:
                g.rect(px_ - 1, py_ - 1, 2, 2, (240, 240, 250))
    else:
        g.rect(ix, iy, iw, ih, (40, 60, 70))
        g.ellipse(ix + 4, iy + 4, iw - 8, ih - 8, (230, 120, 80))
        g.rect(ix, iy + ih - 8, iw, 8, (30, 44, 56))
    g.rect(x + 4, y + h - 8, w - 14, 2, (70, 60, 70))
    g.rect(x + 4, y + h - 4, w - 22, 1, (150, 130, 130))
    g.rect(x + w - 8, y + h - 8, 4, 5, (200, 70, 70))


def walls(g, rnd):
    # ---- left wall
    poster(g, 30, 118, 48, 70, 'sunset')
    # neon tube
    g.line([(97, 58), (97, 96)], (30, 30, 50))
    g.line([(97, 104), (97, 123)], (30, 30, 50))
    g.rect(91, 121, 12, 8, (64, 68, 100))
    g.rect(91, 121, 12, 1, (120, 126, 162))
    g.rect(91, 252, 12, 8, (64, 68, 100))
    g.rect(91, 259, 12, 1, (30, 32, 54))
    g.rect(90, 130, 1, 122, (44, 48, 76))
    g.lrect(93, 129, 8, 123, MAG, 0.95, body=(255, 150, 215))
    g.lrect(95, 129, 4, 123, (255, 200, 235), 1.0, body=(255, 226, 244))
    g.lrect(96, 131, 2, 119, (255, 255, 255), 1.0)
    g.light(56, 110, 84, 176, MAG, 0.6)
    # instant photos
    for x, y, c in ((106, 146, (90, 130, 170)), (109, 166, (190, 120, 90))):
        g.shadow(x, y + 1, 13, 15, 0.7)
        g.rect(x, y, 12, 14, (238, 234, 224))
        g.rect(x + 1, y + 1, 10, 9, c)
        g.rect(x + 1, y + 7, 10, 3, mul(c, 0.6))
        g.px(x + 6, y - 1, (220, 70, 70))
    # speaker
    g.rect(84, 264, 24, 16, (52, 58, 90))
    g.rect(84, 264, 24, 1, (110, 118, 156))
    for y in range(267, 278, 2):
        for x in range(87, 106, 2):
            g.px(x + (y // 2) % 2, y, (22, 24, 42))
    # ---- right wall
    # wall lamp
    g.rect(379, 132, 10, 7, (84, 90, 126))
    g.rect(379, 132, 10, 1, (150, 156, 190))
    g.rect(382, 139, 4, 9, (150, 116, 60))
    g.rect(382, 139, 1, 9, (230, 190, 110))
    g.rect(370, 147, 28, 3, BRASS)
    g.rect(370, 147, 28, 1, (255, 236, 170))
    g.lpoly([(372, 150), (396, 150), (403, 172), (365, 172)], (255, 176, 90), 0.5, body=(250, 196, 120))
    g.lpoly([(376, 152), (386, 152), (386, 170), (371, 170)], (255, 200, 120), 0.6, body=(255, 222, 160))
    for x in range(369, 402, 4):
        g.line([(384 + (x - 384) * 0.62, 150), (x, 172)], (214, 150, 84))
    g.rect(364, 172, 40, 2, BRASS)
    g.rect(364, 172, 40, 1, (255, 236, 170))
    g.lrect(376, 174, 16, 2, (255, 214, 150), 0.8, body=(255, 244, 214))
    for y in range(176, 196, 2):
        g.px(400, y, (214, 180, 110))
    g.rect(399, 196, 3, 3, BRASS)
    g.light(348, 176, 72, 84, (255, 160, 80), 0.34)
    g.light(362, 116, 44, 30, (255, 160, 80), 0.2)
    # control panel (outside any focus region, decorative only)
    g.shadow(365, 204, 42, 38, 0.6)
    g.rect(365, 203, 40, 36, (92, 104, 142))
    g.rect(365, 203, 40, 1, (160, 172, 206))
    g.rect(365, 238, 40, 1, (44, 50, 80))
    g.rect(367, 205, 36, 32, (30, 34, 58))
    g.rect(369, 207, 32, 13, (12, 20, 38))
    for i in range(3):
        g.lrect(371 + i * 10, 209, 8, 8, (95, 242, 230), 0.75, body=(150, 246, 238))
        g.rect(373 + i * 10 + i % 2, 211 + (i + 1) % 2, 2, 2, (20, 60, 70))
    g.lrect(371, 224, 26, 1, MAG, 0.8)
    g.lrect(371, 228, 16, 1, (130, 140, 190), 0.5)
    g.lrect(371, 232, 20, 1, (130, 140, 190), 0.35)
    g.lrect(397, 231, 3, 3, (255, 80, 80), 0.8)
    g.lrect(392, 231, 3, 3, (90, 255, 150), 0.7)
    # small picture frame and emergency hammer
    poster(g, 420, 114, 34, 30, 'moon')
    g.shadow(423, 188, 26, 30, 0.6)
    g.rect(422, 186, 24, 28, (196, 56, 62))
    g.rect(422, 186, 24, 1, (255, 120, 120))
    g.rect(422, 213, 24, 1, (110, 30, 40))
    g.rect(425, 189, 18, 16, (70, 22, 34))
    g.rect(428, 192, 12, 3, (220, 220, 230))
    g.rect(433, 195, 2, 9, (190, 150, 100))
    g.line([(426, 203), (431, 190)], (255, 170, 170))
    g.rect(425, 207, 18, 4, (240, 232, 226))
    g.rect(427, 208, 10, 1, (150, 50, 50))
    g.rect(427, 210, 6, 1, (150, 50, 50))


# ------------------------------------------------------------------ Structure
# Everything that recedes, built from the perspective model rather than drawn by
# eye. Heights in metres. The dado is where the light strip runs along the
# window wall, and the rack meets the wall where the luggage already sits.
DADO = EYE - (296 - vanishing_point()[1]) / WALL_SCALE
RACK_Y = EYE + (vanishing_point()[1] - 89) / WALL_SCALE
RACK_DEPTH = 0.34
SEAT_H = 0.45  # cushion top
SEAT_INNER = 0.60  # front edge of the cushion, from the centre line
BACK_FACE = 1.05  # the backrest's face; the side wall is at ROOM_HALF_WIDTH
BACK_TOP = 1.18
Z_NEAR = 0.5  # far enough forward that everything runs off the scene


def quad(g, pts, c):
    """A flat polygon given in compartment coordinates."""
    g.poly([P(*p) for p in pts], c)


def receding(g, x0, y0, x1, y1, c, z0=None, z1=Z_NEAR):
    """A surface running from the window wall toward the camera, between two
    edges given as (X, Y) pairs: (x0, y0) to (x1, y1) across it."""
    z0 = WALL_DIST if z0 is None else z0
    quad(g, [(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)], c)


def structure(g):
    """Block-in, docs/13 step 1.1: the ceiling, side walls, floor and the
    luggage rack's rails, in flat colour."""
    HW, C, D = ROOM_HALF_WIDTH, ROOM_CEILING, WALL_DIST
    receding(g, -HW, C, HW, C, CEIL)
    for s in (-1, 1):
        receding(g, s * HW, DADO, s * HW, C, mul(WALL, 0.78))
        receding(g, s * HW, 0, s * HW, DADO, mul(WALL_LO, 0.78))
    receding(g, -HW, 0, HW, 0, (46, 48, 76))
    # the rack, seen from below: rails across the compartment at four depths
    # and its ends along the side walls
    for i, z in enumerate((D - 0.01, D - RACK_DEPTH * 0.34, D - RACK_DEPTH * 0.67, D - RACK_DEPTH)):
        g.line([ri(P(-HW, RACK_Y, z)), ri(P(HW, RACK_Y, z))], STEEL, width=3 if i == 3 else 1)
    for s in (-1, 1):
        g.line([ri(P(s * HW, RACK_Y, D)), ri(P(s * HW, RACK_Y, D - RACK_DEPTH))], STEEL, width=2)


def bench(g, s):
    """A bench along a side wall, s = -1 on the left and +1 on the right, from
    the window wall to beyond the edge of the scene."""
    HW = ROOM_HALF_WIDTH
    receding(g, s * SEAT_INNER, 0, s * SEAT_INNER, SEAT_H, mul(SEAT, 0.55))  # front of the base
    receding(g, s * BACK_FACE, SEAT_H, s * SEAT_INNER, SEAT_H, SEAT)  # cushion
    receding(g, s * BACK_FACE, SEAT_H, s * BACK_FACE, BACK_TOP, mul(SEAT, 0.8))  # backrest
    receding(g, s * BACK_FACE, BACK_TOP - 0.2, s * BACK_FACE, BACK_TOP, (196, 190, 214))  # headrest cover
    receding(g, s * HW, BACK_TOP, s * BACK_FACE, BACK_TOP, mul(SEAT, 1.2))  # top of the backrest


# ------------------------------------------------------------------ Table and what is on it
def table(g, rnd):
    BL, BR, FL, FR = (150, 327), (330, 327), (118, 372), (362, 372)
    # table leg
    g.shadow(196, 420, 88, 16, 0.5, ell=True)
    g.rect(232, 382, 16, 36, (64, 72, 108))
    g.rect(232, 382, 3, 36, (120, 130, 168))
    g.rect(244, 382, 4, 36, (36, 40, 66))
    g.poly([(224, 418), (256, 418), (262, 426), (218, 426)], (54, 60, 94))
    g.line([(224, 418), (256, 418)], (120, 130, 168))
    g.shadow(120, 384, 240, 14, 0.42)
    # table top
    g.poly([BL, BR, FR, FL], WOOD)
    for k in range(1, 7):
        a, b = lerp(BL, BR, k / 7), lerp(FL, FR, k / 7)
        g.line([ri(a), ri(b)], mul(WOOD, 0.74))
        g.line([(ri(a)[0] + 1, ri(a)[1]), (ri(b)[0] + 1, ri(b)[1])], mul(WOOD, 1.1))
    for _ in range(90):
        u, v = rnd.random(), rnd.random()
        a = lerp(lerp(BL, BR, u), lerp(FL, FR, u), v)
        b = lerp(lerp(BL, BR, u), lerp(FL, FR, u), min(1, v + rnd.uniform(0.05, 0.2)))
        g.line([ri(a), ri(b)], mul(WOOD, rnd.choice([0.86, 0.9, 1.1, 1.16])))
    g.line([BL, BR], mul(WOOD, 0.6))
    g.line([(BL[0], BL[1] + 1), (BR[0], BR[1] + 1)], mul(WOOD, 0.8))
    g.line([BL, FL], mul(WOOD, 1.25))
    g.line([BR, FR], mul(WOOD, 0.7))
    # edging and apron
    g.rect(118, 372, 245, 2, BRASS)
    g.rect(118, 372, 245, 1, (255, 236, 170))
    g.rect(118, 374, 245, 9, mul(WOOD, 0.6))
    g.rect(118, 374, 245, 1, mul(WOOD, 0.42))
    g.rect(118, 382, 245, 1, mul(WOOD, 0.36))
    for x in range(124, 360, 12):
        g.px(x, 378, mul(WOOD, 0.9))
    # ---- laptop (the projects object)
    o = place(g, 'projects', (148, 288))
    o.shadow(152, 350, 96, 20, 0.5)
    S = [(148, 292), (214, 288), (218, 343), (151, 348)]
    o.poly(S, (44, 48, 76))
    o.line([S[0], S[1]], (120, 128, 166))
    o.line([S[0], S[3]], (84, 92, 130))
    D = [(151, 295), (212, 291), (215, 340), (154, 345)]
    o.lpoly(D, (40, 70, 160), 0.42, body=(22, 30, 62))
    colors = [MAG, CYA, (255, 206, 110), (150, 255, 170), (226, 232, 255), (176, 130, 255)]
    tilt = (D[0][1] - D[1][1]) / (D[1][0] - D[0][0])  # follow the slope of the screen top edge
    for r in range(10):
        y0 = 299 + r * 4.4
        x = 157 + rnd.choice([0, 0, 4, 8, 4])
        n = rnd.choice([2, 3, 3, 4])
        if r == 8:
            x, n = 157, 2
        for _ in range(n):
            ln = rnd.randrange(4, 13)
            if r == 8 and x + ln > 190:
                break
            c = rnd.choice(colors)
            x1 = min(x + ln, 210) - 1
            # Each run is horizontal in itself and the row sinks run by run with the
            # perspective. Sloping within a run would add a hard step and read as a
            # bent line instead.
            yc = y0 - ((x + x1) / 2 - 157) * tilt
            o.fline([(x, yc), (x1, yc)], c, 0.95)
            x += ln + 2
            if x > 204:
                break
    for r in range(10):
        o.lpx(154, int(round(299 + r * 4.4)), (90, 110, 170), 0.5)
    o.px(181, 290, (20, 22, 40))
    # body
    Bq = [(151, 348), (218, 343), (241, 357), (170, 366)]
    o.poly(Bq, (160, 168, 198))
    o.line([Bq[0], Bq[1]], (40, 44, 70))
    o.poly([(170, 366), (241, 357), (241, 359), (170, 368)], (92, 98, 132))
    for t in (0.14, 0.32, 0.5, 0.68):
        a, b = lerp(Bq[0], Bq[3], t), lerp(Bq[1], Bq[2], t)
        n = 13
        for i in range(n):
            p = lerp(a, b, (i + 0.5) / n)
            x, y = ri(p)
            o.rect(x - 1, y, 3, 2, (104, 112, 148))
            o.px(x - 1, y, (128, 136, 172))
    tp = lerp(lerp(Bq[0], Bq[3], 0.86), lerp(Bq[1], Bq[2], 0.86), 0.5)
    o.rect(int(tp[0]) - 7, int(tp[1]) - 1, 14, 3, (182, 190, 216))
    o.light(150, 336, 100, 40, (90, 150, 255), 0.5)
    o.light(146, 286, 76, 60, (80, 120, 255), 0.25)
    # ---- coffee
    g.shadow(256, 354, 62, 14, 0.5, ell=True)
    g.ellipse(258, 351, 58, 13, (232, 230, 244))
    g.ellipse(258, 351, 58, 11, (248, 246, 255))
    g.ellipse(266, 353, 42, 7, (196, 194, 220))
    g.line([(262, 357), (273, 360)], (190, 196, 214))
    g.rect(261, 356, 3, 2, (220, 224, 238))
    # handle
    hc = (232, 230, 246)
    g.rect(301, 337, 7, 2, hc)
    g.rect(307, 338, 3, 9, hc)
    g.rect(301, 346, 7, 2, hc)
    g.px(309, 338, (190, 188, 214))
    g.px(309, 346, (190, 188, 214))
    g.rect(301, 348, 6, 1, (176, 174, 204))
    # cup body
    body = (240, 238, 250)
    g.rect(272, 333, 30, 20, body)
    g.ellipse(272, 344, 30, 14, body)
    g.rect(272, 333, 4, 20, (198, 196, 224))
    g.rect(276, 333, 2, 22, (222, 220, 240))
    g.rect(297, 333, 5, 19, (206, 204, 230))
    g.rect(292, 335, 2, 12, (255, 255, 255))
    g.rect(273, 346, 28, 2, (150, 120, 206))
    g.rect(273, 346, 3, 2, (120, 96, 176))
    g.line([(275, 355), (280, 357), (294, 357), (299, 355)], (176, 174, 204))
    g.ellipse(271, 328, 32, 10, (252, 250, 255))
    g.ellipse(273, 329, 28, 8, (150, 96, 70))
    g.ellipse(274, 330, 26, 6, (116, 66, 48))
    g.ellipse(279, 331, 13, 3, (196, 130, 84))
    g.px(284, 331, (236, 190, 140))
    g.px(293, 333, (150, 96, 70))
    # ---- ticket (the about object)
    o = place(g, 'about', (316, 344))
    o.shadow(318, 349, 32, 15, 0.6)
    T = [(316, 346), (344, 344), (348, 358), (320, 361)]
    o.poly(T, (240, 228, 198))
    o.line([T[0], T[1]], (255, 250, 232))
    o.line([T[3], T[2]], (170, 156, 130))
    o.fline([(319, 349.2), (336, 349.2)], (206, 60, 66), width=2)
    o.fline([(321, 352.8), (333, 352.8)], (96, 90, 104))
    o.fline([(322, 355.6), (330, 355.6)], (150, 140, 140))
    for y in range(346, 359, 2):
        o.px(338 + (y - 346) // 4, y, (170, 156, 130))
    o.rect(341, 349, 4, 4, (60, 56, 76))
    o.px(342, 350, (240, 228, 198))
    o.px(344, 352, (240, 228, 198))
    # ---- pen
    g.line([(254, 366), (267, 363)], (40, 60, 120))
    g.line([(254, 367), (267, 364)], (24, 36, 80))
    g.px(268, 363, BRASS)
    g.px(258, 365, BRASS)


def build_room(seed=21):
    """The carriage as one RGBA image at output resolution, and the silhouette
    mask of every interactive object at 1x, keyed by object id."""
    # One random stream per section, so that changing one part of the room does
    # not reshuffle the texture of every part drawn after it
    rng = lambda name: random.Random(f'{seed}:{name}')
    cv = Cv(W, H)
    g = Off(cv)
    shell(g, rng('shell'))
    walls(g, rng('walls'))
    rack(g, rng('rack'))
    window(g, rng('window'))
    structure(g)
    bench(g, -1)
    bench(g, 1)
    table(g, rng('table'))
    # Overall lighting: the ceiling strip washing the walls, cold light from outside
    g.light(-120, 40, 720, 50, (255, 214, 160), 0.26)
    wx, wy, ww, wh = WINDOW
    g.light(wx, wy + 1, ww, wh - 2, (120, 150, 255), 0.55)
    g.light(110, 300, 260, 80, (120, 150, 255), 0.22)
    # the strip washing downward, warm lamp light landing on the table, floor
    # lights along the aisle
    g.light(-120, 300, 720, 50, (95, 242, 230), 0.16)
    g.light(250, 318, 150, 70, (255, 180, 100), 0.26)
    g.light(-20, 380, 180, 90, (255, 120, 170), 0.14)
    g.light(330, 380, 180, 90, (255, 190, 120), 0.16)
    g.light(140, 430, 200, 60, (120, 150, 255), 0.18)

    amb = np.ones((H, W, 3), np.float32)
    yy = np.arange(H, dtype=np.float32).reshape(H, 1, 1)
    amb *= np.clip(1.05 - np.abs(yy - 250) / 760, 0.6, 1.05)
    # No darkening toward the left and right edges here. The extensions used to
    # be a dark periphery and were faded out in the art; now they show the side
    # walls and benches, which are part of the room, and the page's vignette
    # (scene.css .vig) shades the whole width as one picture.
    im = render(
        cv,
        ambient=(0.36, 0.36, 0.56),
        amb_grad=amb,
        spill=(1.5, 7.0),
        spill2=(1.7, 30.0),
        bloom=(0.5, 1.4),
        haze=(0.2, 7.0),
        wrap=False,
        shadow_blur=2.6,
    )
    k = px.SCALE
    a = np.asarray(im).copy()
    a[..., 3] = 255
    # Punch out the window opening
    hole = hole_mask()[..., None]
    n = 1
    while n < k:
        hole = px.epx(hole, wrap=False)
        n *= 2
    a[:, OX * k : (OX + 480) * k, 3] = np.where(hole[..., 0] > 127, 0, 255)
    return Image.fromarray(a, 'RGBA'), g.masks
