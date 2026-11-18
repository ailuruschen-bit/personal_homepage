"""The carriage interior.

Drawn on a 720x480 canvas covering scene x in [-120, 600), then cut into the
central 480 plus a 120-wide extension on each side. The window wall is drawn
face-on; everything that recedes is built from the perspective model below.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

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
    'about': dict(at=(318, 352), zone=(-10, -8, 42, 26), light=(16, 9, 30, 20)),
    'stack': dict(at=(326, 52), zone=(-10, -9, 78, 45), light=(34, 20, 48, 28), on_rack=1),
    # the map, half open on the table; the line display on the wall is the
    # railway's, and only a decoy
    'journey': dict(at=(245, 323), zone=(-5, -6, 67, 25), light=(28, 9, 32, 12)),
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
# The luggage racks: one over each bench end, either side of the line display
# above the window. Shallow enough to reach from the seat below.
RACK_DEPTH = 0.13
RACK_INNER = 0.46  # each rack runs from here to the side wall
# The luggage's front on each rack. On the left it stands just past the front
# rail; the briefcase on the right is slim and stands against the wall, inside
# the rack.
LUGGAGE_Z = {-1: WALL_DIST - RACK_DEPTH - 0.01, 1: WALL_DIST - 0.07}
LUGGAGE_FLAT = 1.0  # height of the luggage relative to how it was written; 1 is unchanged


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


# The cup and saucer were drawn too large for the laptop beside them: they are
# drawn at COFFEE_SCALE about the middle of the saucer's foot.
COFFEE_AT = (283, 367)
COFFEE_SCALE = 0.62

# Small animated things the page lays over the art, each x y relative to what
# they belong to: the steam over the cup (in the cup's own coordinates, before
# it was scaled) and the cursor on the laptop's screen.
MARKS = {'steam': ('coffee', 284, 322), 'cur': ('projects', 48, 44)}


def mark(key):
    """Where a mark sits in the scene."""
    owner, x, y = MARKS[key]
    if owner == 'coffee':
        (cx, cy), k = COFFEE_AT, COFFEE_SCALE
        return (cx + (x - cx) * k, cy + (y - cy) * k)
    ax, ay = OBJECTS[owner]['at']
    return (ax + x, ay + y)


def scaled(g, k, cx, cy):
    """A canvas on which art keeps its written coordinates but comes out k
    times its size about the point (cx, cy): for things drawn at the wrong
    size relative to their neighbours."""
    vx, vy = vanishing_point()
    d = ((cx - vx) * (1 - k) / k, (cy - vy) * (1 - k) / k)
    return g.at(*d).depth(WALL_DIST / k)


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
        # an object on the rack stands nearer than the wall it was written on:
        # its zone and light scale about the vanishing point with it
        k = WALL_DIST / LUGGAGE_Z[o['on_rack']] if o.get('on_rack') else 1.0
        vx, vy = vanishing_point()
        sx, sy = (lambda v: vx + (v - vx) * k), (lambda v: vy + (v - vy) * k)
        objects[key] = dict(
            zone=(sx(ax + z[0]), sy(ay + z[1]), sx(ax + z[2]), sy(ay + z[3])),
            light=(sx(ax + li[0]), sy(ay + li[1]), li[2] * k, li[3] * k),
            box=(x0 - OX, y0, x1 - x0, y1 - y0),
            sprite=f'/assets/obj-{key}.webp',
        )
        front = masks.get(f'{key}/front')
        if front:
            fx0, fy0, fx1, fy1 = front.getbbox()
            objects[key]['front'] = dict(box=(fx0 - OX, fy0, fx1 - fx0, fy1 - fy0), sprite=f'/assets/obj-{key}-front.webp')
    glows = {}
    for key, gl in GLOWS.items():
        if isinstance(gl[0], str):
            ax, ay = (wx, wy) if gl[0] == 'window' else OBJECTS[gl[0]]['at']
            gl = (ax + gl[1], ay + gl[2], gl[3], gl[4])
        glows[key] = gl
    marks = {key: mark(key) for key in MARKS}
    (bx0, by0), (bx1, by1) = P(-ROOM_HALF_WIDTH, ROOM_CEILING, WALL_DIST), P(ROOM_HALF_WIDTH, 0, WALL_DIST)
    vx, vy = vanishing_point()
    return dict(
        side=OX,
        perspective=dict(vx=vx, vy=vy, wall=(bx0, by0, bx1, by1)),
        window=dict(x=wx, y=wy, w=ww, h=wh, r=WINDOW_RADIUS),
        camera=dict(x=wx + CAM_GAP[0], y=wy + CAM_GAP[1]),
        glows=glows,
        marks=marks,
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
    """Canvas wrapper, so everything below is written in scene coordinates.

    It carries a shift, and optionally a depth: art written as if it were on the
    window wall is scaled about the vanishing point to stand nearer the camera
    instead (see depth()).

    It can also carry a tag. While a tag is set, every solid or lit shape drawn is
    recorded in that tag's silhouette mask as well; shadows, light and texture are
    not, because they are not part of an object's outline. build.py turns the masks
    into the objects' sprites and bounding boxes."""

    def __init__(self, cv, dx=0, dy=0, tag=None, masks=None, k=1.0, flat=(1.0, 0)):
        self.cv, self.dx, self.dy, self.tag, self.k, self.flat = cv, dx, dy, tag, k, flat
        self.masks = {} if masks is None else masks

    def at(self, dx, dy, tag=None):
        """The same canvas shifted by (dx, dy), recording into silhouette `tag`."""
        return Off(self.cv, self.dx + dx, self.dy + dy, tag, self.masks, self.k, self.flat)

    def depth(self, z):
        """The same canvas for art standing z metres from the camera instead of
        on the window wall: everything is scaled about the vanishing point."""
        return Off(self.cv, self.dx, self.dy, self.tag, self.masks, WALL_DIST / z, self.flat)

    def flatten(self, f, foot):
        """The same canvas with art squashed to f of its height toward the line
        y = foot it stands on, in the coordinates the art was written in."""
        return Off(self.cv, self.dx, self.dy, self.tag, self.masks, self.k, (f, foot))

    @property
    def plain(self):
        return self.k == 1.0 and self.flat[0] == 1.0

    # ---- scene coordinates to canvas pixels
    def _xy(self, x, y):
        f, foot = self.flat
        x, y = x + self.dx, foot + (y - foot) * f + self.dy
        if self.k != 1.0:
            vx, vy = vanishing_point()
            x, y = vx + (x - vx) * self.k, vy + (y - vy) * self.k
        return (x + OX, y)

    def _r(self, x, y, w, h):
        """A rectangle as canvas x, y, w, h; whole pixels once scaled."""
        if self.plain:
            return (x + self.dx + OX, y + self.dy, w, h)
        (x0, y0), (x1, y1) = self._xy(x, y), self._xy(x + w, y + h)
        x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
        return (x0, y0, max(1, x1 - x0) if w > 0 else 0, max(1, y1 - y0) if h > 0 else 0)

    def _p(self, pts):
        if self.plain:
            return [self._xy(x, y) for x, y in pts]
        return [tuple(round(v) for v in self._xy(x, y)) for x, y in pts]

    def _m(self):
        """Drawing handle on this tag's silhouette mask; None when untagged."""
        if self.tag is None:
            return None
        if self.tag not in self.masks:
            self.masks[self.tag] = Image.new('L', (self.cv.w, self.cv.h), 0)
        return ImageDraw.Draw(self.masks[self.tag])

    def _box(self, x, y, w, h):
        x, y, w, h = self._r(x, y, w, h)
        return [x, y, x + w - 1, y + h - 1]

    def _mrect(self, x, y, w, h):
        m = self._m()
        if m and w > 0 and h > 0:
            m.rectangle(self._box(x, y, w, h), fill=255)

    def _mline(self, pts, width):
        m = self._m()
        if m:
            m.line([(round(x), round(y)) for x, y in self._p(pts)], fill=255, width=max(1, round(width * self.k)))

    def rect(self, x, y, w, h, c):
        self.cv.rect(*self._r(x, y, w, h), c)
        self._mrect(x, y, w, h)

    def px(self, x, y, c):
        self.cv.rect(*self._r(x, y, 1, 1), c)
        self._mrect(x, y, 1, 1)

    def line(self, pts, c, width=1):
        self.cv.line(self._p(pts), c, max(1, round(width * self.k)))
        self._mline(pts, width)

    def poly(self, pts, c):
        self.cv.poly(self._p(pts), c)
        m = self._m()
        if m:
            m.polygon(self._p(pts), fill=255)

    def ellipse(self, x, y, w, h, c):
        self.cv.ellipse(*self._r(x, y, w, h), c)
        m = self._m()
        if m:
            m.ellipse(self._box(x, y, w, h), fill=255)

    def rrect(self, x, y, w, h, r, c):
        self.cv.rrect(*self._r(x, y, w, h), round(r * self.k), c)
        m = self._m()
        if m:
            m.rounded_rectangle(self._box(x, y, w, h), round(r * self.k), fill=255)

    def mask(self, x, y, m, c):
        cx, cy = (round(v) for v in self._xy(x, y))
        self.cv.mask(cx, cy, m, c)
        if self._m():
            self.masks[self.tag].paste(255, (cx, cy), m)

    def lrect(self, x, y, w, h, c, k=1.0, body=None):
        self.cv.lrect(*self._r(x, y, w, h), c, k, body)
        self._mrect(x, y, w, h)

    def lpx(self, x, y, c, k=1.0):
        self.cv.lrect(*self._r(x, y, 1, 1), c, k)
        self._mrect(x, y, 1, 1)

    def lline(self, pts, c, k=1.0, width=1, body=None):
        self.cv.lline(self._p(pts), c, k, max(1, round(width * self.k)), body)
        self._mline(pts, width)

    def fline(self, pts, c, k=0.0, width=1, body=None):
        self.cv.fline([self._xy(x, y) for x, y in pts], c, k, width * self.k, body)
        self._mline(pts, width)

    def fpoly(self, pts, c, k=0.0, body=None):
        """A polygon on the fine layer (Cv.fpoly), recorded in the silhouette."""
        self.cv.fpoly([self._xy(x, y) for x, y in pts], c, k, body)
        m = self._m()
        if m:
            m.polygon(self._p(pts), fill=255)

    def frect(self, x, y, w, h, c, k=0.0):
        self.fpoly([(x, y), (x + w - 1, y), (x + w - 1, y + h - 1), (x, y + h - 1)], c, k)

    def lpoly(self, pts, c, k=1.0, body=None):
        p = self._p(pts)
        self.cv.d.polygon(p, fill=tuple(body or c) + (255,))
        self.cv.e.polygon(p, fill=mul(c, k))
        m = self._m()
        if m:
            m.polygon(p, fill=255)

    def lellipse(self, x, y, w, h, c, k=1.0, body=None):
        self.cv.lellipse(*self._r(x, y, w, h), c, k, body)
        m = self._m()
        if m:
            m.ellipse(self._box(x, y, w, h), fill=255)

    # ---- not part of any outline
    def light(self, x, y, w, h, c, k=1.0):
        self.cv.light(*self._r(x, y, w, h), c, k)

    def shadow(self, x, y, w, h, k=0.5, ell=False):
        self.cv.shadow(*self._r(x, y, w, h), k, ell)

    def light_poly(self, pts, c, k=1.0):
        """An invisible polygon of light, like light(): a cone, a beam."""
        self.cv.l.polygon(self._p(pts), fill=mul(c, k))

    def shade(self, x, y, w, h, k):
        parts.shade(self.cv, *self._r(x, y, w, h), k)

    def speckle(self, x, y, w, h, amount, rnd, density=0.12):
        self.cv.speckle(*self._r(x, y, w, h), amount, rnd, density)


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
def rounded_side(g, xr, r, c, zl):
    """The end of a piece of luggage whose front is a rounded rectangle (the
    holdall, written at x .. xr, y 68 .. 92 with corner radius r), carried back
    from its front at depth zl to the wall. The profile is taken from the very
    outline the front is drawn with, so the side meets the rounded corners
    exactly: each step of the outline becomes a strip running back, shaded by
    which way it faces."""
    base = g.flatten(LUGGAGE_FLAT, 92).at(0, -3)
    front, back = base.depth(zl), base
    y0, y1 = 68, 92
    prof = []
    for k in range(7):  # top corner, from the top round to the side
        a = math.radians(-90 + 15 * k)
        prof.append((xr - r + r * math.cos(a), y0 + r + r * math.sin(a), 'top' if k < 3 else 'edge'))
    for k in range(7):  # bottom corner, from the side round to the bottom
        a = math.radians(15 * k)
        prof.append((xr - r + r * math.cos(a), y1 - r + r * math.sin(a), 'side' if k < 4 else 'under'))
    tone = {'top': 0.95, 'edge': 0.78, 'side': 0.6, 'under': 0.48}
    sc = lambda o, x, y: (o._xy(x, y)[0] - OX, o._xy(x, y)[1])
    for (xa, ya, _), (xb, yb, kind) in zip(prof, prof[1:]):
        g.poly([sc(front, xa, ya), sc(front, xb, yb), sc(back, xb, yb), sc(back, xa, ya)], mul(c, tone[kind]))
    # the lit line along the top of the rounded edge
    g.line([ri(sc(front, xr - r, y0)), ri(sc(back, xr - r, y0))], mul(c, 1.05))


def rack(g, rnd, over_rack=True):
    # the railway's line display: a decoy, not an object
    o = g
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
    # Luggage. Each piece was written as if it stood on the window wall with its
    # foot at y = 92; it is drawn LUGGAGE_Z from the camera instead, standing on
    # the rack, so it is scaled about the vanishing point and lifted to the
    # rack's level. From below, its underside shows between its front and the wall.
    # It is also flattened: bags laid on a rack are lower than they are wide.
    D = WALL_DIST
    lug = g.flatten(LUGGAGE_FLAT, 92).at(0, -3, '_rim').depth(LUGGAGE_Z[-1])
    bx = lug.at(24, 0, '_rim')
    um = g.flatten(LUGGAGE_FLAT, 92).at(2, -3).depth(LUGGAGE_Z[1])
    # x0, x1, height as written, colour, silhouette tag
    pieces = ((52, 88, 20, (176, 138, 98), None, 0), (96, 151, 24, (60, 140, 138), None, 7),
              (326, 394, 34, (150, 96, 62), 'stack', 0), (400, 448, 4, (44, 50, 84), None, 0))
    for x0, x1, h, c, tag, r_ in pieces:
        xa, xb = (x0 - 240) / WALL_SCALE, (x1 - 240) / WALL_SCALE
        zl = LUGGAGE_Z[-1 if x1 < 240 else 1]
        quad(g, [(xa, RACK_Y, D), (xb, RACK_Y, D), (xb, RACK_Y, zl), (xa, RACK_Y, zl)], mul(c, 0.34))
    # The left rack goes in before its luggage's visible faces: that luggage
    # overhangs the front rail, so nothing of the rack crosses it. The right
    # rack is drawn last, at the end of this function.
    rack_frame(g, -1)
    # each piece's side that faces the middle of the compartment, running back
    # to the wall: its body colour in shade, a lit top edge, and a band or two
    # carried round from the front
    for x0, x1, h, c, tag, r_ in pieces:
        xs = (x1 if x1 < 240 else x0)
        zl = LUGGAGE_Z[-1 if x1 < 240 else 1]
        X, top = (xs - 240) / WALL_SCALE, RACK_Y + h * LUGGAGE_FLAT / WALL_SCALE
        t = g.at(0, 0, tag) if tag else g
        if r_:
            rounded_side(g, x1, r_, c, zl)
            continue
        quad(t, [(X, RACK_Y, D), (X, top, D), (X, top, zl), (X, RACK_Y, zl)], mul(c, 0.6))
        t.line([ri(P(X, top, D)), ri(P(X, top, zl))], mul(c, 0.95))
        t.line([ri(P(X, RACK_Y + 0.004, D)), ri(P(X, RACK_Y + 0.004, zl))], mul(c, 0.4))
        if h >= 20:
            for f in (0.3, 0.7):
                z = zl + (D - zl) * f
                quad(t, [(X, RACK_Y, z), (X, top, z), (X, top, z + 0.025), (X, RACK_Y, z + 0.025)], mul(c, 0.42))
    # Seen from below, the rack is nearer than the bottoms of the sides: what
    # of them shows below the rail shows through the slats, behind the rail.
    # The fronts, nearer still, are drawn after and stay over the rail.
    rack_frame(g, -1)
    # cardboard box
    bx.rect(28, 72, 36, 20, (176, 138, 98))
    bx.rect(28, 72, 36, 2, (210, 174, 130))
    bx.rect(28, 90, 36, 2, (120, 90, 66))
    bx.rect(43, 72, 6, 20, (206, 186, 150))
    bx.rect(52, 78, 9, 6, (236, 230, 214))
    bx.rect(53, 80, 6, 1, (120, 60, 60))
    bx.rect(53, 82, 4, 1, (90, 90, 110))
    bx.shade(60, 72, 4, 20, 0.8)
    # holdall
    c = (60, 140, 138)
    lug.rrect(96, 68, 55, 24, 7, c)
    lug.rrect(98, 69, 51, 8, 4, mul(c, 1.28))
    lug.rect(100, 84, 47, 7, mul(c, 0.74))
    lug.rect(98, 77, 51, 1, mul(c, 0.6))
    # Material marks (docs/13, R-04). Fabric: the nylon's twill, a diagonal
    # weave of darker threads across the body
    for y in range(78, 91):
        for x in range(99 + (y % 3), 149, 3):
            lug.px(x, y, mul(c, 0.84 if y < 84 else 0.62))
    for x in (110, 134):
        lug.rect(x, 68, 4, 24, mul(c, 0.62))
        lug.rect(x, 68, 1, 24, mul(c, 0.9))
        lug.rect(x, 79, 4, 3, BRASS)
    lug.line([(113, 68), (116, 63), (133, 63), (136, 68)], mul(c, 0.5))
    lug.line([(114, 68), (117, 64), (132, 64), (135, 68)], mul(c, 0.8))
    lug.rect(146, 78, 5, 9, (236, 226, 200))
    lug.rect(147, 80, 3, 1, (150, 60, 60))
    lug.px(148, 77, (40, 40, 56))
    # briefcase (the stack object)
    o = place(g.flatten(LUGGAGE_FLAT, 92).depth(LUGGAGE_Z[1]), 'stack', (318, 55))
    lb = (150, 96, 62)
    o.rect(318, 58, 68, 34, lb)
    o.rect(318, 58, 68, 3, mul(lb, 1.3))
    o.rect(318, 61, 68, 6, mul(lb, 1.14))
    o.rect(318, 84, 68, 8, mul(lb, 0.74))
    o.rect(318, 58, 1, 34, mul(lb, 0.6))
    o.rect(385, 58, 1, 34, mul(lb, 0.55))
    o.rect(318, 91, 68, 1, mul(lb, 0.5))
    o.speckle(318, 58, 68, 34, 0.1, rnd, 0.3)
    # Leather: a broad, soft sheen across the lid, brightest toward the lamp
    o.ellipse(326, 66, 58, 12, mul(lb, 1.12))
    o.ellipse(340, 68, 36, 7, mul(lb, 1.26))
    o.ellipse(352, 69, 16, 3, mul(lb, 1.42))
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
    um.rect(398, 88, 42, 4, (44, 50, 84))
    um.rect(398, 88, 42, 1, (84, 92, 136))
    um.rect(412, 88, 2, 4, (150, 60, 70))
    um.rect(394, 89, 4, 2, (160, 166, 190))
    um.line([(440, 89), (446, 89), (447, 86), (445, 84)], BRASS)
    # The briefcase stands inside the right rack, so the rack's floor and rail
    # cross its foot. The page lifts the briefcase's sprite on focus, and a
    # briefcase cut off at the rail looks sawn in two. So its silhouette stays
    # whole, and the part of the rack that crosses it is recorded as a second
    # silhouette, 'stack/front', which the page keeps on top of the sprite: the
    # briefcase lifts behind the rail. build.py cuts the briefcase's sprite from
    # a second render made with over_rack=False, where the rack is not in its way.
    if over_rack:
        rack_frame(g.at(0, 0, '_rack'), 1)
        over = g.masks.pop('_rack')
        x0, y0, x1, y1 = g.masks['stack'].getbbox()
        near = Image.new('L', over.size, 0)
        ImageDraw.Draw(near).rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 3], fill=255)
        g.masks['stack/front'] = ImageChops.multiply(over, near)


def rack_frame(g, s):
    """One luggage rack, seen from below: slats running out from the wall, a
    front rail with a lip that the luggage stands behind, and a bracket at each
    end. s = -1 for the left-hand rack, +1 for the right."""
    HW, D = ROOM_HALF_WIDTH, WALL_DIST
    zf = D - RACK_DEPTH
    dark, mid, lite = (64, 72, 106), STEEL, (176, 186, 214)
    at = lambda x, z, y=RACK_Y: ri(P(s * x, y, z))
    # slats, and the wire that ties them halfway out
    x = RACK_INNER
    while x < HW - 0.01:
        g.line([at(x, D), at(x, zf)], mul(mid, 0.82))
        x += 0.055
    g.line([at(RACK_INNER, (D + zf) / 2), at(HW, (D + zf) / 2)], mul(mid, 0.7))
    g.line([at(RACK_INNER, D), at(HW, D)], dark)
    # the front rail: a low lip the luggage stands behind
    quad(g, [(s * RACK_INNER, RACK_Y - 0.008, zf), (s * HW, RACK_Y - 0.008, zf), (s * HW, RACK_Y + 0.014, zf), (s * RACK_INNER, RACK_Y + 0.014, zf)], mid)
    g.line([at(RACK_INNER, zf, RACK_Y + 0.014), at(HW, zf, RACK_Y + 0.014)], lite)
    g.line([at(RACK_INNER, zf, RACK_Y - 0.008), at(HW, zf, RACK_Y - 0.008)], dark)
    # the inner end: a side rail, and a bracket down to the wall
    g.line([at(RACK_INNER, D), at(RACK_INNER, zf)], mid, width=2)
    g.line([at(RACK_INNER, D, RACK_Y - 0.17), at(RACK_INNER, zf)], dark, width=2)
    g.line([at(RACK_INNER, D, RACK_Y - 0.17), at(RACK_INNER, D)], dark, width=2)
    bx, by = at(RACK_INNER, zf)
    g.rect(bx - 1, by - 1, 3, 3, lite)


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
    # Metal: sharp speculars where the brass faces a light, small and hard
    for x in (138, 139, 182, 318, 342, 343):
        g.lpx(x, 101, (255, 250, 230), 0.5)
    g.rect(120, 103, 240, 1, (130, 96, 50))
    for x in (114, 358):
        g.ellipse(x, 97, 9, 9, BRASS)
        g.px(x + 2, 99, (255, 240, 190))
        g.px(x + 3, 99, (255, 240, 190))
        g.rect(x + 2, 104, 5, 1, (130, 96, 50))
    # curtains, tied back on both sides
    cc = (58, 110, 96)
    # Each curtain is two round folds. Across a fold, from the side away from
    # its light: a reflected edge, the core shadow, the half-tone, the
    # highlight and back (docs/13, L-03). The left curtain is lit from the
    # neon on its left, the right one from the lamp on its right.
    FOLDS = [0.78, 0.58, 0.86, 1.16, 1.32, 1.08, 0.74, 0.82, 0.6, 0.94, 1.24, 1.12, 0.76]
    for x0 in (123, 344):
        g.shadow(x0 - 1, 106, 16, 168, 0.62)
        folds = FOLDS[::-1] if x0 < 240 else FOLDS
        cg = g.at(0, 0, '_rim')
        for i in range(13):
            cg.rect(x0 + i, 104, 1, 164, mul(cc, folds[i]))
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


def cast(g, x, y, w, h, dx, dy, k=0.3, steps=6):
    """The shadow an object standing off the wall throws on it (docs/13, L-01):
    its outline (x, y, w, h) slid (dx, dy) away from the light that casts it,
    darkest and hardest against the object and fading along its length. Draw
    it before the object, which covers the part beneath itself."""
    for i in range(steps, 0, -1):  # far and pale first; nearer steps cover them
        t = i / steps
        g.shadow(round(x + dx * t), round(y + dy * t), w, h, k + (1 - k) * 0.7 * t)


def walls(g, rnd):
    # Every fitting throws a shadow away from its nearest light: the neon tube
    # on the left, the lamp on the right, the ceiling strip over the racks.
    # ---- the racks' shadow on the wall below them, from the ceiling strip
    for x0, x1 in ((24, 158), (322, 456)):
        cast(g, x0, 86, x1 - x0, 5, 0, 9, 0.4)
    # ---- left wall
    cast(g, 37, 115, 54, 76, -10, 4)  # the poster, left of the tube
    poster(g, 40, 118, 48, 70, 'sunset')
    # neon tube
    g.line([(97, 58), (97, 96)], (30, 30, 50))
    g.line([(97, 104), (97, 123)], (30, 30, 50))
    # The two sockets are shallow boxes on the wall, so the tube sits close to
    # it. The tube is left of and
    # level with the vanishing point, so each shows its face, its side toward
    # the middle of the room, and the face toward the tube: the underside of
    # the top one and the top of the bottom one, lit by the tube itself.
    cap, side, rim = (64, 68, 100), (38, 40, 66), (120, 126, 162)
    # top socket
    g.poly([(103, 121), (104, 122), (104, 130), (103, 129)], side)
    g.poly([(91, 129), (103, 129), (104, 130), (92, 130)], (150, 104, 170))
    g.rect(91, 121, 12, 8, cap)
    g.rect(91, 121, 12, 1, rim)
    g.rect(91, 121, 1, 8, mul(cap, 1.25))
    g.rect(91, 128, 12, 1, mul(cap, 0.7))
    g.px(103, 121, rim)
    # bottom socket
    g.poly([(103, 252), (104, 251), (104, 259), (103, 260)], side)
    g.poly([(91, 252), (103, 252), (104, 251), (92, 251)], (176, 116, 190))
    g.rect(91, 252, 12, 8, cap)
    g.rect(91, 252, 12, 1, (210, 150, 220))
    g.rect(91, 252, 1, 8, mul(cap, 1.25))
    g.rect(91, 259, 12, 1, (30, 32, 54))
    g.rect(90, 130, 1, 122, (44, 48, 76))
    g.lrect(94, 129, 8, 123, MAG, 0.95, body=(255, 150, 215))
    g.lrect(96, 129, 4, 123, (255, 200, 235), 1.0, body=(255, 226, 244))
    g.lrect(97, 131, 2, 119, (255, 255, 255), 1.0)
    g.light(56, 110, 84, 176, MAG, 0.6)
    # instant photos
    for x, y, c in ((106, 146, (90, 130, 170)), (109, 166, (190, 120, 90))):
        cast(g, x, y, 12, 14, 5, 2, 0.3, 3)  # right beside the tube: short, hard
        g.rect(x, y, 12, 14, (238, 234, 224))
        g.rect(x + 1, y + 1, 10, 9, c)
        g.rect(x + 1, y + 7, 10, 3, mul(c, 0.6))
        g.px(x + 6, y - 1, (220, 70, 70))
    # speaker
    cast(g, 84, 264, 24, 16, -3, 6, 0.35, 4)
    g.rect(84, 264, 24, 16, (52, 58, 90))
    g.rect(84, 264, 24, 1, (110, 118, 156))
    for y in range(267, 278, 2):
        for x in range(87, 106, 2):
            g.px(x + (y // 2) % 2, y, (22, 24, 42))
    # ---- right wall
    # wall lamp
    # its wall plate, a box right of and above the vanishing point: its face,
    # the side toward the middle of the room, and its underside, warm from the
    # shade below; then the stem as a round rod, and a collar where they meet
    plate = (84, 90, 126)
    g.poly([(379, 132), (376, 135), (376, 142), (379, 139)], (48, 52, 80))
    g.poly([(379, 139), (389, 139), (386, 142), (376, 142)], (128, 104, 96))
    g.rect(379, 132, 10, 7, plate)
    g.rect(379, 132, 10, 1, (150, 156, 190))
    g.rect(388, 132, 1, 7, mul(plate, 1.2))
    g.rect(379, 138, 10, 1, mul(plate, 0.72))
    for x, c in ((382, (120, 90, 46)), (383, (240, 204, 124)), (384, (200, 160, 88)), (385, (128, 96, 50))):
        g.rect(x, 140, 1, 8, c)
    g.rect(381, 139, 6, 2, mul(BRASS, 0.7))
    g.rect(382, 139, 4, 1, BRASS)
    g.rect(370, 147, 28, 3, BRASS)
    g.rect(370, 147, 28, 1, (255, 236, 170))
    g.lpoly([(372, 150), (396, 150), (403, 172), (365, 172)], (255, 176, 90), 0.5, body=(250, 196, 120))
    g.lpoly([(376, 152), (386, 152), (386, 170), (371, 170)], (255, 200, 120), 0.6, body=(255, 222, 160))
    for x in range(369, 402, 4):
        g.line([(384 + (x - 384) * 0.62, 150), (x, 172)], (214, 150, 84))
    g.rect(364, 172, 40, 2, BRASS)
    g.rect(364, 172, 40, 1, (255, 236, 170))
    for x in (368, 369, 392):
        g.lpx(x, 172, (255, 252, 236), 0.6)
    g.lrect(376, 174, 16, 2, (255, 214, 150), 0.8, body=(255, 244, 214))
    for y in range(176, 196, 2):
        g.px(400, y, (214, 180, 110))
    g.rect(399, 196, 3, 3, BRASS)
    # The light it throws (docs/13, L-04): a cone down the wall from the open
    # bottom of the shade, starting just below it so the lamp itself stays as
    # it was, brightest near the shade; a pool on the panel below and on the
    # top of the right-hand backrest by the wall, and a little up the wall
    warm = (255, 128, 40)  # saturated: the wall is blue, a paler warm only greys it
    g.light_poly([(360, 184), (408, 184), (452, 330), (318, 330)], warm, 0.3)
    g.light_poly([(364, 184), (404, 184), (434, 300), (336, 300)], warm, 0.46)
    g.light_poly([(368, 184), (400, 184), (414, 250), (354, 250)], warm, 0.64)
    g.light(348, 176, 72, 84, (255, 160, 80), 0.34)
    g.light(404, 214, 70, 34, warm, 0.45)
    g.light(362, 116, 44, 30, (255, 160, 80), 0.2)
    # control panel (outside any focus region, decorative only)
    cast(g, 365, 203, 40, 36, 1, 9)  # straight under the lamp
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
    cast(g, 406, 110, 38, 34, 7, -6, 0.4)  # above and right of the lamp
    poster(g, 408, 112, 34, 30, 'moon')
    cast(g, 422, 186, 24, 28, 7, 7)  # below and right of it
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
    # where the ceiling meets the window wall: a cove, three bands each a
    # step lighter, so the corner is a curve rather than a crease
    for z0, z1, k in ((D, D - 0.03, 0.62), (D - 0.03, D - 0.06, 0.78), (D - 0.06, D - 0.1, 0.9)):
        receding(g, -HW, C, HW, C, mul(CEIL, k), z0, z1)
    # ventilation grilles on the ceiling either side of the light. Only the
    # ceiling within about 25 cm of the wall is in the picture, so that is
    # where they go
    for x0, x1 in ((-0.9, -0.5), (0.5, 0.9)):
        receding(g, x0, C, x1, C, (34, 36, 58), 1.92, 1.80)
        for z in (1.9, 1.87, 1.84, 1.81):
            g.line([ri(P(x0 + 0.02, C, z)), ri(P(x1 - 0.02, C, z))], (22, 24, 40))
        g.line([ri(P(x0, C, 1.80)), ri(P(x1, C, 1.80))], mul(CEIL, 1.3))
    # the ceiling light: a strip running down the middle of the ceiling toward
    # the camera, in a housing
    receding(g, -0.2, C, 0.2, C, (38, 40, 62), D - 0.04)
    g.lpoly([ri(P(x, C, z)) for x, z in ((-0.15, D - 0.07), (0.15, D - 0.07), (0.15, Z_NEAR), (-0.15, Z_NEAR))],
            (255, 222, 164), 0.85, body=(255, 240, 208))
    for z in (1.78, 1.6, 1.44, 1.3):
        g.line([ri(P(-0.2, C, z)), ri(P(0.2, C, z))], (38, 40, 62))


BERTH = (1.42, 1.90, 0.06)  # folded upper berth: bottom, top, thickness off the wall


def side_wall(g, s):
    """What makes the side walls a sleeper compartment's partitions rather than
    blank planes: the upper berth folded up against each one, held by straps,
    with a strip of wall between it and the backrest for the small fittings.
    s = -1 on the left, +1 on the right."""
    HW, C, D = ROOM_HALF_WIDTH, ROOM_CEILING, WALL_DIST
    y0, y1, t = BERTH
    wall = mul(WALL, 0.78)
    on = lambda z, y, inset=0.0: ri(P(s * (HW - inset), y, z))
    # partition panel seams
    for z in (1.62, 1.24, 0.9):
        g.line([on(z, BACK_TOP), on(z, C)], mul(wall, 0.7))
    # the berth: its shadow on the wall, its underside, its face
    receding(g, s * HW, y0 - 0.07, s * HW, y0, mul(wall, 0.62))
    receding(g, s * HW, y0, s * (HW - t), y0, mul(WALL, 0.4))
    face = (92, 102, 136)
    receding(g, s * (HW - t), y0, s * (HW - t), y1, face)
    g.line([on(D, y1, t), on(Z_NEAR, y1, t)], mul(face, 1.35))
    g.line([on(D, y0, t), on(Z_NEAR, y0, t)], mul(face, 0.55))
    g.line([on(D, y0 + 0.06, t), on(Z_NEAR, y0 + 0.06, t)], mul(face, 0.8))
    g.line([on(D, y1 - 0.06, t), on(Z_NEAR, y1 - 0.06, t)], mul(face, 0.8))
    # retaining straps and the pull handle
    for z in (1.9, 1.5, 1.1):
        quad(g, [(s * (HW - t), y0, z), (s * (HW - t), y1, z), (s * (HW - t), y1, z - 0.045), (s * (HW - t), y0, z - 0.045)], (150, 96, 62))
        bx, by = on(z - 0.022, y0 + 0.1, t)
        g.rect(bx - 1, by - 1, 3, 3, BRASS)
    g.line([on(1.78, 1.66, t), on(1.62, 1.66, t)], BRASS, width=2)
    # The strip of wall between the backrest and the berth, by the window, is
    # what the scene shows of each side wall: a fitting on each, drawn as a
    # small object with a face, an edge and a shadow
    w = lambda z, y, d=0.0: P(s * (HW - d), y, z)
    poly = lambda pts, c: g.poly([ri(w(*q)) for q in pts], c)
    if s > 0:
        # reading lamp: a brass wall plate, a hood with its open underside lit,
        # and the light it throws on the wall and the backrest below
        poly([(1.92, 1.25), (1.92, 1.37), (1.70, 1.37), (1.70, 1.25)], (64, 52, 40))
        poly([(1.91, 1.26), (1.91, 1.36), (1.71, 1.36), (1.71, 1.26)], BRASS)
        poly([(1.88, 1.3, 0.05), (1.88, 1.35, 0.05), (1.74, 1.35, 0.05), (1.74, 1.3, 0.05)], (58, 52, 70))
        poly([(1.88, 1.35, 0.05), (1.88, 1.35, 0.0), (1.74, 1.35, 0.0), (1.74, 1.35, 0.05)], (90, 82, 104))
        g.lpoly([ri(w(*q)) for q in ((1.88, 1.3, 0.05), (1.88, 1.3, 0.0), (1.74, 1.3, 0.0), (1.74, 1.3, 0.05))],
                (255, 196, 120), 0.9, body=(255, 236, 190))
        for z0, z1, y in ((1.86, 1.76, 1.24), (1.9, 1.72, 1.2)):
            g.lpoly([ri(w(z0, y)), ri(w(z0, y + 0.02)), ri(w(z1, y + 0.02)), ri(w(z1, y))], (255, 170, 90), 0.18, body=mul(WALL, 0.9))
        lx, ly = w(1.81, 1.22)
        g.light(int(lx) - 34, int(ly) - 10, 60, 70, (255, 170, 90), 0.34)
    else:
        # net pocket: a frame on the wall, the net drawn as a lattice over the
        # dark wall behind it, and a folded timetable standing out of it
        poly([(1.88, 1.18), (1.88, 1.36), (1.56, 1.36), (1.56, 1.18)], (36, 40, 66))
        for k in range(1, 9):
            z = 1.88 - k * 0.04
            g.line([ri(w(z, 1.18, 0.02)), ri(w(z + 0.04, 1.33, 0.02))], (88, 96, 132))
            g.line([ri(w(z + 0.04, 1.18, 0.02)), ri(w(z, 1.33, 0.02))], (70, 78, 112))
        poly([(1.80, 1.30, 0.01), (1.80, 1.43, 0.01), (1.66, 1.43, 0.01), (1.66, 1.30, 0.01)], (226, 220, 200))
        for y in (1.405, 1.385, 1.365):
            g.line([ri(w(1.78, y, 0.012)), ri(w(1.69, y, 0.012))], (150, 120, 120))
        g.line([ri(w(1.88, 1.335, 0.02)), ri(w(1.56, 1.335, 0.02))], STEEL, width=2)
        g.line([ri(w(1.88, 1.18, 0.02)), ri(w(1.56, 1.18, 0.02))], mul(STEEL, 0.7))

def floor_and_ceiling(g):
    """Seams that run toward the camera and across it, so the floor and ceiling
    read as planes with depth."""
    HW, C, D = ROOM_HALF_WIDTH, ROOM_CEILING, WALL_DIST
    dark = (30, 32, 54)
    for x in (-0.3, 0.0, 0.3):
        g.line([ri(P(x, 0, D)), ri(P(x, 0, Z_NEAR))], dark)
    for z in (1.7, 1.42, 1.18, 0.98, 0.82):
        g.line([ri(P(-HW, 0, z)), ri(P(HW, 0, z))], dark)
    for x in (-0.6, 0.0, 0.6):
        g.line([ri(P(x, C, D)), ri(P(x, C, Z_NEAR))], mul(CEIL, 0.7))
    for z in (1.6, 1.25):
        g.line([ri(P(-HW, C, z)), ri(P(HW, C, z))], mul(CEIL, 0.7))


def extrude(g, s, profile, shades, base, z0=None, z1=Z_NEAR):
    """A cross-section swept along the bench. `profile` is a polyline of (X, Y)
    points for the right-hand bench (mirrored by s) and `shades` gives one
    brightness per segment, applied to `base`. Rounding an edge is a matter of
    giving the profile a few short segments round the corner, each a step
    lighter or darker: upholstery has no hard edges."""
    for (xa, ya), (xb, yb), k in zip(profile, profile[1:], shades):
        receding(g, s * xa, ya, s * xb, yb, mul(base, k), z0, z1)


# Cross-sections. The cushion's top runs flat from the backrest, then rolls
# over a soft shoulder down its front; the backrest's face rolls over into its
# top the same way.
CUSHION = [
    (BACK_FACE, SEAT_H), (BACK_FACE - 0.05, SEAT_H), (BACK_FACE - 0.12, SEAT_H + 0.006),
    (SEAT_INNER + 0.16, SEAT_H + 0.006), (SEAT_INNER + 0.10, SEAT_H), (SEAT_INNER + 0.06, SEAT_H - 0.006),
    (SEAT_INNER + 0.03, SEAT_H - 0.02), (SEAT_INNER + 0.01, SEAT_H - 0.045), (SEAT_INNER, SEAT_H - 0.075),
    (SEAT_INNER + 0.012, SEAT_H - 0.105), (SEAT_INNER + 0.04, SEAT_H - 0.12),
]
CUSHION_SHADES = [0.5, 0.82, 0.9, 1.0, 1.14, 1.32, 1.18, 0.94, 0.72, 0.52]
BACK_ROLL = [
    (BACK_FACE, BACK_TOP - 0.05), (BACK_FACE + 0.003, BACK_TOP - 0.03), (BACK_FACE + 0.01, BACK_TOP - 0.014),
    (BACK_FACE + 0.022, BACK_TOP - 0.004), (BACK_FACE + 0.04, BACK_TOP), (ROOM_HALF_WIDTH, BACK_TOP),
]
BACK_ROLL_SHADES = [0.9, 1.04, 1.22, 1.38, 1.26]


def table_map(g, T):
    """The journey object: a paper map lying half open on the table between
    the laptop and the cup. The far half is still rolled into a tube along its
    back edge; the near corner on the right has curled up and shows the paper's
    back. T(u, v) is a point on the table top, u across, v from back to front."""
    o = g.at(0, 0, 'journey')
    paper = (232, 222, 196)
    # the flat sheet, a little askew
    A, B, C, D = T(0.53, 0.08), T(0.8, 0.05), T(0.81, 0.28), T(0.54, 0.31)
    o.poly([A, B, C, D], paper)
    g.line([(D[0], D[1] + 1), (C[0], C[1] + 1)], mul(WOOD, 0.55))  # its shadow on the wood

    def at(u, v):
        top = lerp(A, B, u)
        bot = lerp(D, C, u)
        return ri(lerp(top, bot, v))

    # printed: a river, a park, streets, the line and its stations
    o.poly([at(0.0, 0.38), at(0.45, 0.3), at(1.0, 0.42), at(1.0, 0.54), at(0.5, 0.42), at(0.0, 0.5)], (150, 186, 210))
    o.poly([at(0.62, 0.62), at(0.92, 0.6), at(0.94, 0.86), at(0.64, 0.88)], (166, 200, 148))
    for u in (0.25, 0.5, 0.76):
        o.line([at(u, 0.06), at(u + 0.02, 0.95)], (210, 200, 176))
    for v in (0.22, 0.7):
        o.line([at(0.03, v), at(0.97, v)], (210, 200, 176))
    route = [at(0.1, 0.12), at(0.32, 0.3), at(0.4, 0.55), at(0.66, 0.5), at(0.72, 0.76), at(0.9, 0.9)]
    o.line(route, (204, 60, 66), width=2)
    for k, (sx, sy) in enumerate(route):
        o.px(sx, sy, (250, 244, 226))
    for sx, sy in (route[2], route[4]):  # circled, and circled again
        o.line([(sx - 3, sy - 1), (sx + 2, sy - 2), (sx + 3, sy + 1), (sx, sy + 2), (sx - 3, sy + 1), (sx - 2, sy - 2)], (196, 36, 48))
    # a crease from being folded, and a coffee ring
    o.line([at(0.0, 0.72), at(1.0, 0.68)], mul(paper, 0.86))
    rx, ry = at(0.22, 0.8)
    o.line([(rx - 3, ry), (rx - 1, ry - 1), (rx + 2, ry - 1), (rx + 3, ry), (rx + 1, ry + 1), (rx - 2, ry + 1), (rx - 3, ry)], (176, 140, 100))
    # the near right corner curling up off the table: the paper's back, and
    # the light along its lip
    curl = [at(0.72, 1.0), C, (C[0] - 2, C[1] - 7), (at(0.8, 0.86)[0], at(0.8, 0.86)[1] - 2)]
    o.poly([ri(c) for c in curl], mul(paper, 0.8))
    o.line([ri(curl[2]), ri(curl[3])], (252, 248, 232))
    # the rest, rolled into a tube along the back edge, with a rubber band
    for dy, c in ((0, (168, 158, 138)), (-1, (196, 186, 162)), (-2, (222, 214, 192)), (-3, (240, 234, 212)), (-4, (248, 242, 224)), (-5, (232, 224, 202)), (-6, (206, 196, 172))):
        o.line([(A[0] - 1, A[1] + dy), (B[0] + 1, B[1] + dy)], c)
    o.ellipse(B[0] + 1, B[1] - 3, 3, 4, (214, 204, 180))
    o.ellipse(B[0] + 1, B[1] - 3, 1, 2, (176, 164, 140))
    mx, my = lerp(A, B, 0.35)
    o.rect(round(mx), round(my) - 6, 2, 7, (190, 60, 62))


def bench(g, s):
    """A bench along a side wall, s = -1 on the left and +1 on the right, from
    the window wall to beyond the edge of the scene: a base, a cushion with a
    rolled front edge, and a quilted backrest slab with a rolled top and a
    headrest cover per seat. Everything is placed in compartment coordinates,
    so the quilting and every seam converge with the room."""
    HW, D = ROOM_HALF_WIDTH, WALL_DIST
    xi, xb = s * SEAT_INNER, s * BACK_FACE
    face = mul(SEAT, 0.8)
    on_face = lambda z, y: ri(P(xb, y, z))
    on_top = lambda x, z: ri(P(s * x, SEAT_H, z))

    # base, set back under the cushion, with the cushion's shadow along its top
    receding(g, s * (SEAT_INNER + 0.04), 0, s * (SEAT_INNER + 0.04), SEAT_H - 0.11, mul(SEAT, 0.42))
    receding(g, s * (SEAT_INNER + 0.04), SEAT_H - 0.17, s * (SEAT_INNER + 0.04), SEAT_H - 0.11, mul(SEAT, 0.26))
    g.line([ri(P(s * (SEAT_INNER + 0.04), 0.04, D)), ri(P(s * (SEAT_INNER + 0.04), 0.04, Z_NEAR))], mul(SEAT, 0.6))

    # cushion: a soft-shouldered cross-section swept along the bench
    extrude(g, s, CUSHION, CUSHION_SHADES, SEAT)

    # backrest face with the crease at its foot
    # the flat face stops where the roll begins: run to the very top, its
    # square corner shows behind the rounded roll
    receding(g, xb, SEAT_H, xb, BACK_ROLL[0][1], face)
    receding(g, xb, SEAT_H, xb, SEAT_H + 0.035, mul(SEAT, 0.42))
    # diamond quilting: two families of diagonals on the face, and a button
    # where they cross
    y0, y1, pitch = SEAT_H + 0.035, BACK_TOP - 0.05, 0.17
    n = 0
    while True:
        c = Z_NEAR - (y1 - y0) + n * pitch
        if c > D:
            break
        for sign in (1, -1):
            # z runs from c to c + (y1 - y0) as y climbs (sign 1) or falls (-1)
            za, zb = c, c + (y1 - y0)
            ya, yb = (y0, y1) if sign > 0 else (y1, y0)
            if zb > D:  # clip at the window wall
                t = (D - za) / (zb - za)
                zb, yb = D, ya + (yb - ya) * t
            if za < Z_NEAR:
                t = (Z_NEAR - za) / (zb - za)
                za, ya = Z_NEAR, ya + (yb - ya) * t
            if zb > za:
                g.line([on_face(za, ya), on_face(zb, yb)], mul(SEAT, 0.58))
        n += 1
    k = 0
    while Z_NEAR - (y1 - y0) + k * pitch / 2 <= D:
        z = Z_NEAR - (y1 - y0) + k * pitch / 2
        for m in range(8):
            y = y0 + (m + (k % 2) * 0.5) * pitch
            # the two diagonals through (z, y) only cross on this lattice
            if y0 < y < y1 and Z_NEAR < z < D and abs(((z - y0) - (y - y0)) / pitch % 1) < 1e-6:
                bx, by = on_face(z, y)
                g.px(bx, by, mul(SEAT, 0.4))
                g.px(bx, by - 1, mul(SEAT, 1.25))
        k += 1

    # the top of the backrest rolls over instead of ending in an edge
    extrude(g, s, BACK_ROLL, BACK_ROLL_SHADES, SEAT)

    # seat divisions, across the cushion and up the backrest
    for z in (1.42, 0.84):
        g.line([on_top(SEAT_INNER, z), on_top(BACK_FACE, z)], mul(SEAT, 0.5))
        g.line([on_face(z, SEAT_H), on_face(z, BACK_TOP - 0.03)], mul(SEAT, 0.45))
        g.line([ri(P(xi, SEAT_H - 0.105, z)), ri(P(s * (SEAT_INNER + 0.03), SEAT_H - 0.02, z))], mul(SEAT, 0.45))

    # headrest covers: one per seat, draped over the roll so they follow its
    # curve, with a hem along the bottom
    cloth = (178, 172, 198)  # held below the wall in value (L-06)
    drape = [(BACK_FACE, BACK_TOP - 0.25), (BACK_FACE, BACK_TOP - 0.225)] + [(x - 0.004, y + 0.004) for x, y in BACK_ROLL]
    drape[2] = (BACK_FACE - 0.004, BACK_TOP - 0.05)
    tones = [0.7, 0.9] + [0.96, 1.04, 1.12, 1.2, 1.14]
    drape[-1] = (ROOM_HALF_WIDTH, BACK_TOP + 0.004)
    # the covers stop short of the window wall and of each other, so the
    # backrest's own rolled edge shows between them
    for z0, z1 in ((1.94, 1.5), (1.34, 0.92), (0.76, Z_NEAR)):
        extrude(g, s, drape, tones, cloth, z0, z1)
        g.line([on_face(z1, BACK_TOP - 0.25), on_face(z1, BACK_TOP - 0.05)], mul(cloth, 0.62))

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
    # The table is hinged to the wall under the window. Under it, a steel strut
    # runs from a plate on the wall up to the underside of the top on each side,
    # and the wall under the table is in its shadow
    g.shadow(130, 383, 220, 30, 0.55)
    for x, d in ((176, 1), (304, -1)):
        g.rect(x - 4, 404, 8, 6, (44, 50, 80))
        g.rect(x - 4, 404, 8, 1, (96, 104, 140))
        g.line([(x, 406), (x + 14 * d, 384)], (60, 66, 100), width=2)
        g.line([(x - d, 405), (x + 14 * d - d, 384)], (112, 120, 158))
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
    for x in (194, 195, 298, 299, 300):
        g.lpx(x, 372, (255, 252, 236), 0.5)
    # Wood: an edge highlight along the top's front edge, where the varnish
    # turns down to the brass
    g.line([(119, 371), (361, 371)], mul(WOOD, 1.32))
    g.rect(118, 374, 245, 9, mul(WOOD, 0.6))
    g.rect(118, 374, 245, 1, mul(WOOD, 0.42))
    g.rect(118, 382, 245, 1, mul(WOOD, 0.36))
    for x in range(124, 360, 12):
        g.px(x, 378, mul(WOOD, 0.9))
    T = lambda u, v: lerp(lerp(BL, BR, u), lerp(FL, FR, u), v)
    table_map(g, T)
    # ---- laptop (the projects object)
    # Built in the compartment model, in metres, and projected with P(), so it
    # keeps true perspective however it is turned: the table top is 1.0 m wide,
    # 0.555 m deep and 0.629 m high (from its corners on screen). The laptop is
    # turned a little toward the left-hand seat, as if someone had just been
    # working at it from there. All of it on the fine layer, whose straight
    # edges EPX would tear (docs/13, R-03, O-06).
    o = place(g, 'projects', (148, 288))
    TY = EYE - (327 - vanishing_point()[1]) / WALL_SCALE  # the table top's height
    cx, cz, turn = -0.2, 1.665, math.radians(-11)
    w, d, th = 0.33, 0.225, 0.016  # base width, depth, thickness
    lid_h, lean = 0.215, math.radians(12)

    def at(lx, ly, lz):
        """A point in the laptop's own frame: x across, y up from the table, z
        back from the base's middle, turned and placed on the table."""
        x = lx * math.cos(turn) - lz * math.sin(turn)
        z = lx * math.sin(turn) + lz * math.cos(turn)
        return P(cx + x, TY + ly, cz + z)

    K = lambda a, b: at((a - 0.5) * w, th, (0.5 - b) * d)  # on the base's top, b from the back
    BLb, BRb, FRb, FLb = K(0, 0), K(1, 0), K(1, 1), K(0, 1)
    gl = lambda a, b: at((a - 0.5) * w, 0, (0.5 - b) * d)  # the same on the table
    # contact shadow along its front edge and its left side
    xs = [q[0] for q in (gl(0, 0), gl(1, 0), gl(1, 1), gl(0, 1))]
    ys = [q[1] for q in (gl(0, 0), gl(1, 0), gl(1, 1), gl(0, 1))]
    o.shadow(round(min(xs)) - 3, round(max(ys)) - 3, round(max(xs) - min(xs)) + 6, 6, 0.45)
    o.shadow(round(min(xs)) - 4, round(min(ys)), 7, round(max(ys) - min(ys)), 0.6)
    # the base: its front and the side toward the middle of the room, then its top
    o.fpoly([FLb, FRb, gl(1, 1), gl(0, 1)], (88, 94, 130))
    o.fpoly([BRb, FRb, gl(1, 1), gl(1, 0)], (68, 74, 106))
    o.fline([gl(0, 1), gl(1, 1)], (18, 16, 28))
    o.fpoly([BLb, BRb, FRb, FLb], (150, 158, 190))
    o.fline([FLb, FRb], (132, 140, 176))
    # the keyboard well, and the keys at their size: five rows
    o.fpoly([K(0.06, 0.06), K(0.94, 0.06), K(0.95, 0.6), K(0.05, 0.6)], (92, 100, 138))
    for r in range(5):
        n = 15
        for i in range(n):
            x, y = K(0.09 + (i + 0.5) * 0.82 / n, 0.1 + r * 0.1)
            o.frect(round(x) - 1, round(y), 2, 1, (196, 204, 234))
    o.fline([K(0.32, 0.56), K(0.68, 0.56)], (196, 204, 234))  # the space bar
    # the trackpad
    o.fpoly([K(0.355, 0.67), K(0.645, 0.67), K(0.65, 0.91), K(0.35, 0.91)], (110, 118, 154))
    o.fpoly([K(0.36, 0.68), K(0.64, 0.68), K(0.645, 0.9), K(0.355, 0.9)], (172, 180, 212))
    # the lid, hinged at the back edge and leaning back
    Lp = lambda a, c: at((a - 0.5) * w, th + c * lid_h * math.cos(lean), d / 2 + c * lid_h * math.sin(lean))
    L = [Lp(0, 1), Lp(1, 1), Lp(1, 0), Lp(0, 0)]
    o.fpoly(L, (40, 44, 70))
    o.fline([L[0], L[1]], (120, 128, 166))
    o.fline([L[1], L[2]], (70, 76, 108))
    # the screen inside a bezel: narrow at the sides and top, wider at the foot
    D = [Lp(0.05, 0.93), Lp(0.95, 0.93), Lp(0.95, 0.13), Lp(0.05, 0.13)]
    o.fpoly(D, (40, 70, 160), 0.42, body=(22, 30, 62))
    Sp = lambda a, b: Lp(0.05 + 0.9 * a, 0.93 - 0.8 * b)
    cam = Lp(0.5, 0.965)
    o.frect(round(cam[0]), round(cam[1]), 1, 1, (16, 18, 30))
    # hinge: a dark seam across the lid's foot, a barrel at each end
    o.fline([Lp(0.02, 0.03), Lp(0.98, 0.03)], (22, 24, 38), width=1.5)
    for a in (0.12, 0.8):
        hx, hy = Lp(a, 0.02)
        o.frect(round(hx), round(hy) - 1, 5, 2, (96, 102, 136))
    # code on the screen, its rows following the screen's slope, each run level
    # in itself at the height of its middle (a sloping run would show a step)
    colors = [MAG, CYA, (255, 206, 110), (150, 255, 170), (226, 232, 255), (176, 130, 255)]
    rows = 9
    for r in range(rows):
        b = 0.08 + r * 0.84 / (rows - 1)
        nx, ny = Sp(0.03, b)
        o.frect(round(nx), round(ny), 1, 1, (90, 110, 170), 0.5)
        a = 0.09 + rnd.choice([0, 0, 0.06, 0.12, 0.06])
        n = rnd.choice([2, 3, 3, 4])
        if r == 7:
            a, n = 0.09, 2
        for _ in range(n):
            ln = rnd.randrange(4, 13) / 62
            if r == 7 and a + ln > 0.55:
                break
            a1 = min(a + ln, 0.96)
            (xa, ya), (xb, yb) = Sp(a, b), Sp(a1, b)
            o.fline([(xa, (ya + yb) / 2), (xb, (ya + yb) / 2)], rnd.choice(colors), 0.95)
            a = a1 + 2 / 62
            if a > 0.9:
                break
    # the screen's light on the keys and on the table in front
    top = round(min(q[1] for q in L))
    o.light(round(min(xs)), round(min(ys)) - 6, round(max(xs) - min(xs)), 30, (90, 150, 255), 0.5)
    o.light(round(min(xs)) - 6, top - 6, round(max(xs) - min(xs)) + 12, round(min(ys)) - top + 12, (80, 120, 255), 0.25)
    # ---- coffee
    # the cup stands in front of the map; it is cut out of the map's sprite
    cg = scaled(g, COFFEE_SCALE, *COFFEE_AT).at(0, 0, '_cup')
    cg.shadow(256, 354, 62, 14, 0.5, ell=True)
    cg.ellipse(258, 351, 58, 13, (232, 230, 244))
    cg.ellipse(258, 351, 58, 11, (248, 246, 255))
    cg.ellipse(266, 353, 42, 7, (196, 194, 220))
    cg.line([(262, 357), (273, 360)], (190, 196, 214))
    cg.rect(261, 356, 3, 2, (220, 224, 238))
    # handle
    hc = (232, 230, 246)
    cg.rect(301, 337, 7, 2, hc)
    cg.rect(307, 338, 3, 9, hc)
    cg.rect(301, 346, 7, 2, hc)
    cg.px(309, 338, (190, 188, 214))
    cg.px(309, 346, (190, 188, 214))
    cg.rect(301, 348, 6, 1, (176, 174, 204))
    # cup body
    body = (240, 238, 250)
    cg.rect(272, 333, 30, 20, body)
    cg.ellipse(272, 344, 30, 14, body)
    cg.rect(272, 333, 4, 20, (198, 196, 224))
    cg.rect(276, 333, 2, 22, (222, 220, 240))
    cg.rect(297, 333, 5, 19, (206, 204, 230))
    cg.rect(292, 335, 2, 12, (255, 255, 255))
    cg.rect(273, 346, 28, 2, (150, 120, 206))
    cg.rect(273, 346, 3, 2, (120, 96, 176))
    cg.line([(275, 355), (280, 357), (294, 357), (299, 355)], (176, 174, 204))
    cg.ellipse(271, 328, 32, 10, (252, 250, 255))
    cg.ellipse(273, 329, 28, 8, (150, 96, 70))
    cg.ellipse(274, 330, 26, 6, (116, 66, 48))
    cg.ellipse(279, 331, 13, 3, (196, 130, 84))
    cg.px(284, 331, (236, 190, 140))
    cg.px(293, 333, (150, 96, 70))
    cup = g.masks['_cup']
    g.masks['journey'] = ImageChops.multiply(g.masks['journey'], ImageChops.invert(cup))
    # ---- ticket (the about object)
    o = place(g, 'about', (316, 344))
    o.shadow(318, 349, 32, 15, 0.6)
    # the business card tucked behind it, one corner showing
    C_ = [(310, 341), (334, 339), (337, 350), (313, 352)]
    o.poly(C_, (236, 236, 242))
    o.line([C_[0], C_[1]], (255, 255, 255))
    o.line([C_[0], C_[3]], (190, 190, 204))
    o.fline([(312.5, 342.6), (322, 341.9)], (60, 60, 80))
    o.fline([(313, 344.6), (320, 344.1)], (140, 140, 160))
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
    # ---- pen, about 14 cm against the laptop, left of it
    g.line([(124, 370), (150, 364)], (40, 60, 120), width=2)
    g.line([(124, 371), (150, 365)], (24, 36, 80))
    g.line([(125, 369), (143, 365)], (90, 110, 170))
    g.line([(150, 364), (153, 363)], (200, 200, 214))
    g.line([(128, 368), (135, 366)], BRASS)
    g.px(124, 370, BRASS)


# ------------------------------------------------------------------ Foreground
# room-l.webp and room-r.webp are not a continuation of the room. They are a
# foreground standing in front of it, so that the page's focus dimming, which
# covers the 480 scene and stops at its edges, stops exactly where the room
# stops: a near, dark object beside a lit room is expected to differ in tone.
# See docs/13, D-01a. Which foreground is drawn is FOREGROUND, or the
# FOREGROUND environment variable when trying variants.
FOREGROUND = os.environ.get('FOREGROUND', 'velvet')

# Curtain colours: the benches' red, or the window curtains' green
FG_CURTAIN = {'velvet': mul(SEAT, 0.84), 'teal': (58, 110, 96)}


# Size of the curtain's diamond quilting, in units of the cloth
FG_QUILT = 26

# A 3 on the pilaster's plate, as (row, column) from the glyph's top-left
FG_NUMBER = ((47, 0), (47, 1), (47, 2), (48, 2), (49, 2), (50, 1), (50, 2), (51, 2), (52, 2), (53, 2), (53, 1), (53, 0))


def foreground_rgb(style):
    """The foreground as an RGB array, 480 rows by 120 columns. Column u is u
    units out from the edge of the scene, so the left image is this mirrored.

    It is built from the interior's own materials so that it reads as the end
    of the same carriage: a pilaster in the wall panelling, edged in brass, with
    the dado rail and ribbed lower panel of the walls; a cornice across the top;
    and beyond it a curtain on a brass rod under a pelmet, tied back with a
    brass rope and tassel."""
    H_, U = 480, 120
    f32 = lambda c: np.array(c, np.float32)
    out = np.zeros((H_, U, 3), np.float32)
    uu, yy = np.meshgrid(np.arange(U), np.arange(H_))
    LIFT = 1.18  # the foreground is out of the room's lights: lift its colours

    # beyond the curtain: the corridor, dim, with a handrail
    out[:] = f32(WALL_LO) * 0.62
    out[300:304] = f32(BRASS) * 0.5
    out[300] = f32(BRASS) * 0.75

    # the curtain
    curtain = f32(FG_CURTAIN[style]) * LIFT
    u_in, top, tie, bottom, y_top = 22, 60, 44, 70, 48
    for row in range(y_top, H_):
        if row < 258:
            t = (row - y_top) / (258 - y_top)
            uo = top + (tie - top) * t * t
        else:
            t = (row - 258) / (H_ - 258)
            uo = tie + (bottom - tie) * np.sqrt(t)
        uo = u_in + uo
        cols = np.arange(u_in, min(U, int(round(uo))))
        f = (cols + 0.5 - u_in) / (uo - u_in)
        wave = 0.5 + 0.5 * np.cos(2 * np.pi * (f * 4.5 + 0.1))
        k = 0.5 + 0.72 * wave**1.3
        k *= 1 - 0.45 * np.clip(1 - f / 0.14, 0, 1)  # in the pilaster's shadow
        k *= 1 - 0.35 * np.clip((f - 0.82) / 0.18, 0, 1)  # turning away at the edge
        if style == 'velvet':
            # the benches' upholstery: the same red in the same tones as their
            # backrests, and their diamond quilting with a button at each
            # crossing, laid out across the cloth so that it gathers into the
            # folds with it
            cu = f * 56.0
            P_ = FG_QUILT
            m = np.full(len(cols), 1.0, np.float32)
            d1, d2 = (cu + row) % P_, (cu - row) % P_
            m[(d1 < 1) | (d2 < 1)] = 0.62
            btn = (np.abs(d1 - P_ / 2) < 0.5) & (np.abs(d2 - P_ / 2) < 0.5)
            m[btn] = 0.45
            out[row, cols] = curtain[None, :] * (k * m)[:, None]
            if row > y_top:
                up = (np.abs(((cu + row - 1) % P_) - P_ / 2) < 0.5) & (np.abs(((cu - row + 1) % P_) - P_ / 2) < 0.5)
                out[row - 1, cols[up]] = curtain * 1.25 * k[up, None]
            # piping down the leading edge, as along the cushions' front
            out[row, cols[f < 0.035]] = curtain * 0.4
        else:
            c = curtain[None, :] * k[:, None]
            sheen = np.clip((wave - 0.9) / 0.1, 0, 1)[:, None] * 0.22  # velvet catches light on the crests
            out[row, cols] = c * (1 - sheen) + f32((255, 196, 206)) * sheen * 0.8
    # tie-back: a brass rope across the folds, and its tassel at the outer end
    rope = [0.62, 0.86, 1.08, 1.22, 1.12, 0.92, 0.7]
    for r, k in enumerate(rope):
        out[255 + r, u_in : u_in + tie + 3] = f32(BRASS) * k
    for r in range(262, 294):
        w = 2 + min(4, (r - 262) // 5)
        x0 = u_in + tie - 1
        out[r, x0 - w // 2 : x0 + w // 2 + 1] = f32(BRASS) * (0.9 if r % 3 else 0.6)
    # pelmet over the rod, with brass piping and a scalloped edge. Over the
    # velvet it is the headrest covers' pale cloth, laid over the red the way
    # they are laid over the backrests
    pel = f32((204, 198, 222)) * 0.9 if style == 'velvet' else curtain * 0.92
    out[34:46, 22:] = pel
    for c in range(22, U, 4):
        out[34:46, c] = pel * 0.78
    out[46, 22:] = f32(BRASS) * 1.1
    out[47, 22:] = f32(BRASS) * 0.75
    for c0 in range(22, U, 12):
        for d in range(min(12, U - c0)):
            depth = int(round(4 * np.sin(np.pi * (d + 0.5) / 12)))
            out[48 : 48 + depth, c0 + d : c0 + d + 1] = pel * 0.85
            if depth:
                out[48 + depth - 1, c0 + d] = pel * 0.6

    # the pilaster: wall panelling with the walls' diamond pattern, edged in brass
    P = 22
    wall = f32(WALL) * LIFT
    a, b = (uu + yy) % 12, (uu - yy) % 12
    pat = np.where((a == 0) | (b == 0), 0.9, np.where((a == 6) & (b == 6), 1.06, 1.0)).astype(np.float32)
    out[:, :P] = wall * pat[:, :P, None]
    out[:, 2:4] *= 1.22  # the face turning toward the room catches its light
    out[:, 17:19] *= 0.8
    out[:, 19:22] *= 0.55
    for x in (7, 14):
        for y in range(70, 290, 26):
            out[y, x] = wall * 1.35
            out[y + 1, x] = wall * 0.6
    # dado rail and the ribbed lower panel, as on the walls
    out[288:296, :P] = f32((70, 80, 118)) * LIFT
    out[288, :P] = f32((128, 138, 176)) * LIFT
    out[294:296, :P] = f32((36, 42, 70)) * LIFT
    low = f32(WALL_LO) * LIFT
    out[296:, :P] = low
    for x in range(2, P - 3, 3):
        out[296:, x] *= 0.84
        out[296:, x + 1] *= 1.08
    out[296:, 17:22] *= 0.7
    # brass edge on the scene side, and a brass number plate
    out[:, 0] = f32(BRASS) * 1.12
    out[:, 1] = f32(BRASS) * 0.72
    out[44:58, 5:17] = f32(BRASS) * 0.85
    out[44, 5:17] = f32(BRASS) * 1.15
    out[46:56, 7:15] = f32((40, 30, 24))

    # cornice across the top, as on the walls
    out[:34] = f32((50, 54, 84)) * LIFT
    out[30] = f32((96, 102, 140)) * LIFT
    out[32:34] = f32((30, 32, 54)) * LIFT
    return np.clip(out, 0, 255).astype(np.uint8)


def foreground(g, style=None):
    """Paint the foreground over both side extensions and clear any shadow left
    there by what was drawn before. The room's invisible lights are left alone:
    they reach into the room through the render's blur, and clearing them here
    would change the room as well as the foreground."""
    a = foreground_rgb(style or FOREGROUND)
    cv = g.cv
    for side, img in ((-1, a[:, ::-1].copy()), (1, a)):
        x0 = 0 if side < 0 else OX + 480
        # the carriage number on the plate, written after mirroring so that it
        # reads the right way round on both sides
        c0 = 9 if side > 0 else 120 - 12
        for y, x in FG_NUMBER:
            img[y, c0 + x] = (255, 214, 140)
        cv.im.paste(Image.fromarray(np.ascontiguousarray(img), 'RGB').convert('RGBA'), (x0, 0))
        cv.em.paste((0, 0, 0), (x0, 0, x0 + 120, H))
        cv.sh.paste(255, (x0, 0, x0 + 120, H))


# The value plan (docs/13, L-06): each depth plane keeps to its own band of
# values, judged on the luminance view. The window wall is the lightest plane
# and the coolest; the benches sit a step below it; the foreground (the side
# images) is the darkest and is already drawn that way. The brightest values are
# kept for the window and the light sources, which only clip if pushed.
# Gains on the rendered picture: (multiplier, per-channel tint).
VALUE_PLAN = {
    'far': (1.16, (0.96, 1.0, 1.06)),
    'bench': (0.86, (1.0, 1.0, 1.0)),
}
FAR_WALL = (24, 26, 456)  # the window wall's left, top and right, in scene units
FAR_FADE = (326, 400)  # below the table the wall goes into shade: the lift fades out


def value_plan(a, near, objects, k):
    """near: silhouettes of the benches, the table and the cup, which stand in
    front of the wall; objects: the table's interactive objects."""
    h, w = a.shape[:2]
    up = lambda m: np.asarray(m.resize((w, h), Image.NEAREST)) > 127
    bench = up(near[0])
    front = np.zeros((h, w), bool)
    for m in near + objects:
        front |= up(m)
    x0, y0, x1 = FAR_WALL
    ys = (np.arange(h, dtype=np.float32) + 0.5) / k
    fade = np.clip((FAR_FADE[1] - ys) / (FAR_FADE[1] - FAR_FADE[0]), 0, 1)[:, None]
    far = np.zeros((h, w), np.float32)
    far[y0 * k :, (OX + x0) * k : (OX + x1) * k] = 1
    far = far * fade * ~front
    gain = np.ones((h, w, 3), np.float32)
    g_, tint = VALUE_PLAN['far']
    gain += far[..., None] * (g_ * np.array(tint, np.float32) - 1)
    g_, tint = VALUE_PLAN['bench']
    gain[bench] = g_ * np.array(tint, np.float32)
    a[..., :3] = np.clip(a[..., :3] * gain, 0, 255).astype(np.uint8)


# Occlusion (docs/13, L-02): where two surfaces meet, each darkens the other.
# The creases are written in compartment coordinates, (X, Y, Z) pairs, and
# drawn as soft dark lines over the rendered picture. Things standing on the
# table are left out of it: they are in front of every crease they overlap.
OCCLUSION_STRENGTH = 0.5
OCCLUSION_BLUR = 2.4  # scene units


def creases():
    HW, C, D, N = ROOM_HALF_WIDTH, ROOM_CEILING, WALL_DIST, Z_NEAR
    # each crease: points, width, and whether the benches stand in front of it
    lines = [
        # the window wall's edges: floor, ceiling and the two corners
        ([(-HW, 0, D), (HW, 0, D)], 3, True),
        ([(-HW, C, D), (HW, C, D)], 3, True),
        ([(-HW, 0, D), (-HW, C, D)], 3, True),
        ([(HW, 0, D), (HW, C, D)], 3, True),
    ]
    for s in (-1, 1):
        base = s * (SEAT_INNER + 0.04)
        lines += [
            # the side walls' ceiling edge, and the backrest's top against the side wall
            ([(s * HW, C, D), (s * HW, C, N)], 3, True),
            ([(s * HW, BACK_TOP, D), (s * HW, BACK_TOP, N)], 2, False),
            # the bench's base on the floor
            ([(base, 0, D), (base, 0, N)], 2, False),
            # the bench's end against the window wall
            ([(base, 0, D), (base, SEAT_H - 0.12, D), (s * SEAT_INNER, SEAT_H - 0.075, D),
              (s * (SEAT_INNER + 0.16), SEAT_H, D), (s * BACK_FACE, SEAT_H, D),
              (s * BACK_FACE, BACK_TOP - 0.05, D), (s * (BACK_FACE + 0.04), BACK_TOP, D),
              (s * HW, BACK_TOP, D)], 3, False),
        ]
    return lines


def occlusion(a, bench, front, k):
    h, w = a.shape[:2]
    up = lambda f: np.asarray(f.resize((w, h), Image.NEAREST)) > 127
    to = lambda q: ((P(*q)[0] + OX) * k, P(*q)[1] * k)
    layers = {True: Image.new('L', (w, h), 0), False: Image.new('L', (w, h), 0)}
    for pts, width, behind in creases():
        ImageDraw.Draw(layers[behind]).line([to(q) for q in pts], fill=255, width=round(width * k), joint='curve')
    # the table's back edge against the wainscot (scene units)
    ImageDraw.Draw(layers[True]).line([((150 + OX) * k, 327 * k), ((330 + OX) * k, 327 * k)], fill=200, width=2 * k)
    blur = lambda im: np.asarray(im.filter(ImageFilter.GaussianBlur(OCCLUSION_BLUR * k)), np.float32) / 255
    behind, on = blur(layers[True]), blur(layers[False])
    behind[up(bench)] = 0  # creases behind the benches do not show through them
    m = np.maximum(behind, on)
    for f in front:
        m[up(f)] = 0
    a[..., :3] = (a[..., :3] * (1 - OCCLUSION_STRENGTH * m)[..., None]).astype(np.uint8)


# Rim light (docs/13, L-03): a thin edge of a light's colour on the side of a
# rounded form that faces it. What a neon scene is lit by shows on its edges.
# Each light: scene position, colour, strength, and reach in scene units.
RIMS = [
    ((97, 190), MAG, 1.3, 170),
    ((384, 172), (255, 170, 90), 0.9, 100),
]


def rim(a, masks, k):
    h, w = a.shape[:2]
    m = np.zeros((h, w), bool)
    for f in masks:
        m |= np.asarray(f.resize((w, h), Image.NEAREST)) > 127
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    sx, sy = xs / k - OX, ys / k
    add = np.zeros((h, w, 3), np.float32)
    for (lx, ly), c, strength, reach in RIMS:
        dx, dy = lx - sx, ly - sy
        dist = np.hypot(dx, dy) + 1e-6
        fall = np.clip(1 - dist / reach, 0, 1) ** 2 * strength
        # the neighbour two pixels toward the light: an edge if it is outside
        ox, oy = np.rint(dx / dist * 2).astype(int), np.rint(dy / dist * 2).astype(int)
        nx, ny = np.clip(xs.astype(int) + ox, 0, w - 1), np.clip(ys.astype(int) + oy, 0, h - 1)
        edge = m & ~m[ny, nx]
        add += (edge * fall)[..., None] * np.array(c, np.float32)
    a[..., :3] = np.clip(a[..., :3] + add, 0, 255).astype(np.uint8)


# Reflections (docs/13, L-05) on the varnished table: the laptop screen's
# light on the top in front of it, the lamp's sheen toward the back right, and
# a specular along the brass front edge where those lights catch it. Each:
# centre, radii in scene units, colour, strength. They are added to the
# rendered picture on the table only, never on what stands on it. The floor's
# reflections of the neon and the lamp would fall below the frame, and the
# glass's lies under the blinds (scene.css .glass).
TABLE_SHEEN = [
    ((196, 360), (44, 9), (90, 130, 255), 0.42),
    ((318, 334), (22, 5), (255, 196, 130), 0.34),
    ((196, 372), (40, 1.6), (150, 190, 255), 0.6),
    ((300, 372), (34, 1.6), (255, 220, 160), 0.7),
]


def reflections(a, table, front, k):
    h, w = a.shape[:2]
    up = lambda f: np.asarray(f.resize((w, h), Image.NEAREST)) > 127
    on = up(table)
    for f in front:
        on &= ~up(f)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    sx, sy = xs / k - OX, ys / k
    add = np.zeros((h, w, 3), np.float32)
    for (cx, cy), (rx, ry), c, strength in TABLE_SHEEN:
        f = np.exp(-(((sx - cx) / rx) ** 2 + ((sy - cy) / ry) ** 2)) * strength
        add += f[..., None] * np.array(c, np.float32)
    add *= on[..., None]
    a[..., :3] = np.clip(a[..., :3] + add, 0, 255).astype(np.uint8)


# The step between bands of light on the room (px.render, docs/13 R-02)
BANDS = float(os.environ.get('BANDS', '0.2')) or None


def build_room(seed=21, over_rack=True):
    """The carriage as one RGBA image at output resolution, and the silhouette
    mask of every interactive object at 1x, keyed by object id. A key ending in
    '/front' is what stands in front of that object and must stay on top of its
    sprite. With over_rack=False the right-hand rack is left out, which is how
    the briefcase is rendered without the rack across it."""
    # One random stream per section, so that changing one part of the room does
    # not reshuffle the texture of every part drawn after it
    rng = lambda name: random.Random(f'{seed}:{name}')
    cv = Cv(W, H)
    g = Off(cv)
    shell(g, rng('shell'))
    walls(g, rng('walls'))
    rack(g, rng('rack'), over_rack)
    window(g, rng('window'))
    structure(g)
    floor_and_ceiling(g)
    side_wall(g, -1)
    side_wall(g, 1)
    # the benches record a silhouette for the value plan below
    bench(g.at(0, 0, '_bench'), -1)
    bench(g.at(0, 0, '_bench'), 1)
    table(g.at(0, 0, '_table'), rng('table'))
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

    foreground(g)

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
        bands=BANDS,
    )
    k = px.SCALE
    a = np.asarray(im).copy()
    near = [g.masks.pop(t) for t in ('_bench', '_table', '_cup')]
    occlusion(a, near[0], near[1:] + [g.masks[t] for t in ('projects', 'about', 'journey')], k)
    value_plan(a, near, [g.masks[t] for t in ('projects', 'about', 'journey')], k)
    rim(a, [g.masks.pop('_rim'), near[0], near[2], g.masks['stack']], k)
    reflections(a, near[1], [near[2]] + [g.masks[t] for t in ('projects', 'about', 'journey')], k)
    # The page lays a vignette over the 480 scene (scene.css .vig) and must not
    # be made to cover the side extensions as well: overlays wider than the
    # scene, and gradients painted inside the extensions, both flickered in
    # Chrome (docs/09, F-002). So the extensions get the same vignette baked in
    # here. It is .vig's gradient exactly: an ellipse about (240, 201.6) reaching
    # the scene's farthest corner, clear to 38% and rgba(5, 4, 14, 0.5) by 82%.
    ys, xs = np.mgrid[0 : H * k, 0 : W * k].astype(np.float32)
    sx, sy = (xs + 0.5) / k - OX, (ys + 0.5) / k
    t = np.sqrt(((sx - 240) / (240 * 2**0.5)) ** 2 + ((sy - 201.6) / (278.4 * 2**0.5)) ** 2)
    va = (0.5 * np.clip((t - 0.38) / (0.82 - 0.38), 0, 1))[..., None]
    # half strength over the foreground: it is near the camera, and the change
    # of tone at the room's edge is now an object's edge
    va = np.where((sx < 0) | (sx >= 480), 0.5, 0)[..., None] * va
    a[..., :3] = (a[..., :3] * (1 - va) + np.array([5, 4, 14], np.float32) * va).astype(np.uint8)
    a[..., 3] = 255
    # Punch out the window opening
    hole = hole_mask()[..., None]
    n = 1
    while n < k:
        hole = px.epx(hole, wrap=False)
        n *= 2
    a[:, OX * k : (OX + 480) * k, 3] = np.where(hole[..., 0] > 127, 0, 255)
    return Image.fromarray(a, 'RGBA'), g.masks
