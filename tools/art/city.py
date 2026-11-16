"""The mid-distance outside the window: a neon district and a stretch of derelict
blocks, assembled into one long strip that loops seamlessly.
"""
import random

import numpy as np
from PIL import Image

from street import GY, H, SH, cable, neon_district, street
from parts import *
import px
from px import Cv, mix, mul, render, text_mask

CONC = (86, 78, 108)  # concrete, on the purple-grey side
CONC_D = (52, 46, 72)


# ------------------------------------------------------------------ Back row
def back_row(cv, rnd, x0, x1):
    """The row of taller buildings behind the front one: only their upper half shows,
    darkened and pushed toward blue."""
    x = x0
    while x < x1:
        w = rnd.randrange(70, 130)
        top = rnd.randrange(34, 110)
        base = rnd.choice([(70, 66, 104), (60, 74, 104), (84, 62, 92), (58, 80, 96), (74, 70, 88)])
        cv.rect(x, top, w, GY - top, base)
        cv.speckle(x, top, w, GY - top, 0.1, rnd, 0.2)
        shade(cv, x + w - 5, top, 5, GY - top, 0.72)
        shade(cv, x, top, 2, GY - top, 1.2)
        # roof
        cv.rect(x - 1, top - 3, w + 2, 3, mul(base, 1.3))
        cv.rect(x - 1, top - 1, w + 2, 1, mul(base, 0.6))
        kind = rnd.choice(['grid', 'grid', 'band', 'tall'])
        lit_p = rnd.uniform(0.12, 0.3)
        if kind == 'band':
            for fy in range(top + 6, GY - 20, 11):
                cv.rect(x + 4, fy, w - 8, 5, mul(base, 0.45))
                for wx in range(x + 5, x + w - 8, 6):
                    if rnd.random() < lit_p:
                        cv.lrect(wx, fy + 1, 4, 3, rnd.choice(LIT[:5]), 0.5)
        else:
            ww, wh, gx, gy = (4, 6, 9, 12) if kind == 'grid' else (3, 9, 7, 15)
            for fy in range(top + 6, GY - 20, gy):
                for wx in range(x + 5, x + w - 6, gx):
                    if rnd.random() < lit_p:
                        cv.lrect(wx, fy, ww, wh, rnd.choice(LIT), 0.5)
                    else:
                        cv.rect(wx, fy, ww, wh, mul(base, 0.5))
                        cv.px(wx, fy + wh - 1, mul(base, 0.8))
        # rooftop structures
        r = rnd.random()
        if r < 0.4:
            hgt = rnd.randrange(18, 44)
            ax = x + rnd.randrange(8, w - 8)
            cv.rect(ax, top - 3 - hgt, 1, hgt, (50, 50, 76))
            cv.rect(ax - 3, top - hgt + 6, 7, 1, (50, 50, 76))
            cv.lpx(ax, top - 4 - hgt, RED, 1.0)
        elif r < 0.75:
            # large rooftop sign, one character per box
            t = rnd.choice(['夜航', '東雲', '銀河', '大安', '雨巷', '南風', '白鯨'])
            col = rnd.choice([MAG, CYA, RED, YEL, VIO])
            sx = x + (w - len(t) * 22) // 2
            for i, ch in enumerate(t):
                bx = sx + i * 22
                cv.rect(bx + 9, top - 8, 2, 5, IRON)
                cv.rect(bx, top - 28, 20, 20, (26, 22, 46))
                cv.rect(bx, top - 28, 20, 1, (60, 54, 90))
                m = text_mask(ch)
                cv.lmask(bx + (20 - m.width) // 2, top - 26 + (16 - m.height) // 2, m, col, 0.9)
        # vertical sign down the side
        if rnd.random() < 0.5:
            chars = rnd.choice(['旅館', '麻雀', '酒', '湯', '質', '薬'])
            vsign(cv, x + rnd.choice([3, w - 23]), top + rnd.randrange(8, 30), chars, rnd.choice(NEONS), side='r')
        x += w + rnd.choice([-6, 0, 4, 10])


# ------------------------------------------------------------------ Derelict blocks
ROOM_WALLS = [(66, 96, 72), (96, 70, 128), (62, 110, 112), (104, 86, 70), (78, 80, 110)]


def crack(cv, rnd, x, y, n, c):
    for _ in range(n):
        cv.px(x, y, c)
        x += rnd.choice([-1, 0, 1])
        y += 1


def broken_edge(cv, rnd, x, y0, y1, c, side):
    """Chew a vertical wall edge into a ragged break and leave some rebar sticking out."""
    for y in range(y0, y1):
        d = rnd.randrange(0, 4)
        if d:
            if side == 'r':
                cv.im.paste((0, 0, 0, 0), (x - d, y, x, y + 1))
                cv.em.paste((0, 0, 0), (x - d, y, x, y + 1))
            else:
                cv.im.paste((0, 0, 0, 0), (x, y, x + d, y + 1))
                cv.em.paste((0, 0, 0), (x, y, x + d, y + 1))
    for _ in range(max(1, (y1 - y0) // 14)):
        ry = rnd.randrange(y0, y1)
        ln = rnd.randrange(3, 8)
        xs = x if side == 'r' else x - ln
        cv.rect(xs, ry, ln, 1, (94, 58, 48))


def cutaway_room(cv, rnd, x, y, w, h, lit=True):
    """A room laid open where the outer wall has fallen away. x, y is the top-left and
    h includes the floor slab."""
    wall = rnd.choice(ROOM_WALLS)
    back = mul(wall, 0.8 if lit else 0.36)
    cv.rect(x, y, w, h - 4, back)
    cv.speckle(x, y, w, h - 4, 0.14, rnd, 0.2)
    # skirting and dado
    cv.rect(x, y + h - 12, w, 8, mul(back, 0.78))
    cv.rect(x, y + h - 13, w, 1, mul(back, 1.25))
    # shadow under the ceiling
    shade(cv, x, y, w, 3, 0.6)
    for _ in range(2):
        crack(cv, rnd, x + rnd.randrange(3, w - 3), y + rnd.randrange(2, 8), rnd.randrange(5, 12), mul(back, 0.55))
    # door
    if w > 26 and rnd.random() < 0.7:
        dx = x + rnd.randrange(4, w - 14)
        cv.rect(dx, y + h - 24, 10, 20, mul(back, 0.5))
        cv.rect(dx + 1, y + h - 23, 8, 19, (74, 52, 46) if lit else (40, 30, 34))
        cv.px(dx + 7, y + h - 13, (200, 170, 110))
    # furniture
    fx = x + 3
    while fx < x + w - 12:
        f = rnd.choice(['sofa', 'shelf', 'tv', 'fridge', 'box', 'none', 'none'])
        fy = y + h - 4
        dk = 1.0 if lit else 0.5
        if f == 'sofa' and fx + 20 < x + w:
            c = mul(rnd.choice([(96, 70, 150), (130, 60, 70), (60, 100, 96)]), dk)
            cv.rect(fx, fy - 9, 20, 5, c)
            cv.rect(fx, fy - 5, 20, 4, mul(c, 0.75))
            cv.rect(fx - 1, fy - 7, 2, 6, mul(c, 1.2))
            cv.rect(fx + 19, fy - 7, 2, 6, mul(c, 1.2))
            cv.rect(fx + 1, fy - 1, 2, 1, (30, 26, 40))
            cv.rect(fx + 17, fy - 1, 2, 1, (30, 26, 40))
            fx += 24
        elif f == 'shelf':
            c = mul((92, 66, 54), dk)
            cv.rect(fx, fy - 18, 10, 18, c)
            for yy in range(fy - 15, fy - 1, 5):
                cv.rect(fx + 1, yy, 8, 3, mul(c, 0.5))
                for xx in range(fx + 1, fx + 8, 2):
                    if rnd.random() < 0.6:
                        cv.rect(xx, yy, 1, 3, mul(rnd.choice([(170, 80, 70), (80, 120, 150), (190, 170, 110), (110, 150, 100)]), dk))
            fx += 13
        elif f == 'tv' and lit:
            cv.rect(fx, fy - 5, 10, 5, (50, 42, 50))
            cv.rect(fx + 1, fy - 13, 9, 8, (34, 32, 46))
            cv.lrect(fx + 2, fy - 12, 6, 5, (130, 170, 255), 0.75)
            cv.lrect(fx + 2, fy - 10, 6, 1, (220, 230, 255), 0.8)
            fx += 14
        elif f == 'fridge':
            c = mul((170, 176, 186), dk)
            cv.rect(fx, fy - 16, 8, 16, c)
            cv.rect(fx, fy - 10, 8, 1, mul(c, 0.6))
            cv.rect(fx + 6, fy - 14, 1, 3, mul(c, 0.5))
            cv.rect(fx + 7, fy - 16, 1, 16, mul(c, 0.7))
            fx += 11
        elif f == 'box':
            c = mul((150, 116, 78), dk)
            cv.rect(fx, fy - 6, 8, 6, c)
            cv.rect(fx, fy - 6, 8, 1, mul(c, 1.25))
            cv.rect(fx + 3, fy - 6, 2, 6, mul(c, 0.8))
            if rnd.random() < 0.5:
                cv.rect(fx + 2, fy - 11, 7, 5, mul(c, 0.85))
            fx += 11
        else:
            fx += rnd.randrange(6, 14)
    # poster on the wall
    if rnd.random() < 0.6:
        px_ = x + rnd.randrange(3, max(4, w - 10))
        pc = rnd.choice([(190, 80, 110), (220, 190, 120), (90, 150, 190)])
        cv.rect(px_, y + 7, 6, 8, mul(pc, 0.8 if lit else 0.4))
        cv.rect(px_ + 1, y + 9, 4, 2, mul(pc, 0.45))
    if lit:
        # a single pendant lamp
        lx = x + w // 2 + rnd.randrange(-6, 7)
        col = rnd.choice([(255, 196, 110), (190, 255, 190), (255, 160, 90), (200, 180, 255)])
        cv.rect(lx, y, 1, 6, (20, 18, 30))
        cv.rect(lx - 2, y + 6, 5, 2, (40, 36, 52))
        cv.lrect(lx - 1, y + 8, 3, 2, col, 1.0, body=(255, 250, 230))
        cv.light(lx - 9, y + 8, 19, 12, col, 0.9)


def ruin_block(cv, rnd, x, w, nfl, fh=30):
    """A concrete building stripped back to its frame."""
    top = GY - nfl * fh
    cv.rect(x, top, w, GY - top, CONC)
    cv.speckle(x, top, w, GY - top, 0.16, rnd, 0.3)
    # water staining
    for _ in range(w // 8):
        sx = x + rnd.randrange(w)
        sy = top + rnd.randrange(GY - top - 12)
        for i in range(rnd.randrange(8, 36)):
            shade(cv, sx, sy + i, rnd.choice([1, 2]), 1, 0.8)
    bays = max(1, w // rnd.choice([30, 36, 44]))
    bw = w / bays
    for f in range(nfl):
        fy = top + f * fh
        for b in range(bays):
            bx = int(x + b * bw) + 4
            ww = int(bw) - 8
            r = rnd.random()
            if r < 0.42:
                cutaway_room(cv, rnd, bx, fy + 4, ww, fh - 4, lit=rnd.random() < 0.45)
            elif r < 0.75:
                # a surviving window, either boarded up or with broken glass
                wx, wy, w2, h2 = bx + ww // 2 - 7, fy + 9, 14, 14
                cv.rect(wx - 1, wy - 1, w2 + 2, h2 + 2, CONC_D)
                cv.rect(wx, wy, w2, h2, (14, 12, 26))
                k = rnd.random()
                if k < 0.4:
                    for i in range(3):
                        yy = wy + 2 + i * 4 + rnd.randrange(-1, 2)
                        cv.rect(wx - 2, yy, w2 + 4, 3, (110, 84, 62))
                        cv.rect(wx - 2, yy + 2, w2 + 4, 1, (74, 56, 44))
                        cv.px(wx - 1, yy + 1, (40, 34, 40))
                        cv.px(wx + w2, yy + 1, (40, 34, 40))
                elif k < 0.7:
                    for i in range(6):
                        cv.px(wx + rnd.randrange(w2), wy + rnd.randrange(h2), (70, 90, 130))
                    cv.line([(wx + 2, wy + h2 - 1), (wx + 6, wy + 5), (wx + 9, wy + h2 - 3)], (46, 60, 100))
                else:
                    c = rnd.choice([(255, 150, 80), (150, 255, 190), (200, 150, 255)])
                    cv.lrect(wx, wy, w2, h2, c, 0.35, body=mul(c, 0.6))
                    cv.rect(wx + w2 // 2, wy, 1, h2, CONC_D)
                    cv.rect(wx + 3, wy + h2 - 7, 4, 7, (24, 18, 30))
                    cv.rect(wx + 4, wy + h2 - 10, 2, 3, (24, 18, 30))
            else:
                # a blank wall, with cracks and graffiti
                for _ in range(2):
                    crack(cv, rnd, bx + rnd.randrange(ww), fy + 6 + rnd.randrange(8), rnd.randrange(6, 16), CONC_D)
                if rnd.random() < 0.5:
                    gc = rnd.choice([MAG, CYA, YEL, GRN, RED])
                    gx, gy = bx + rnd.randrange(2, max(3, ww - 16)), fy + 10 + rnd.randrange(6)
                    pts = [(gx + i * 4, gy + rnd.randrange(0, 9)) for i in range(5)]
                    cv.line(pts, mul(gc, 0.6))
                    cv.line([(p[0], p[1] + 1) for p in pts], mul(gc, 0.42))
        # floor slab
        cv.rect(x - 2, fy, w + 4, 4, mul(CONC, 1.12))
        cv.rect(x - 2, fy, w + 4, 1, mul(CONC, 1.4))
        cv.rect(x - 2, fy + 3, w + 4, 1, CONC_D)
    # columns
    for b in range(bays + 1):
        cx_ = int(x + b * bw) - (3 if b == bays else 0)
        cv.rect(cx_, top, 4, GY - top, mul(CONC, 1.05))
        cv.rect(cx_, top, 1, GY - top, mul(CONC, 1.3))
        cv.rect(cx_ + 3, top, 1, GY - top, CONC_D)
    # roof: a broken parapet, rebar and a water tank
    for xx in range(x, x + w, 5):
        hh = rnd.choice([0, 2, 3, 5, 6])
        if hh:
            cv.rect(xx, top - hh, 5, hh, mul(CONC, 0.9))
    for _ in range(w // 16):
        rx = x + rnd.randrange(w)
        cv.rect(rx, top - rnd.randrange(6, 14), 1, 12, (94, 58, 48))
    return top


def ladder(cv, x, y0, y1, c=(70, 96, 150)):
    cv.rect(x, y0, 1, y1 - y0, c)
    cv.rect(x + 6, y0, 1, y1 - y0, c)
    for yy in range(y0 + 2, y1, 4):
        cv.rect(x + 1, yy, 5, 1, mul(c, 0.8))


def fence(cv, rnd, x0, x1, y, h=20):
    """Chain-link fence; y is the ground line."""
    c = (70, 78, 98)
    for xx in range(x0, x1, 28):
        cv.rect(xx, y - h - 3, 2, h + 3, (56, 60, 80))
        cv.px(xx, y - h - 4, (56, 60, 80))
    cv.rect(x0, y - h, x1 - x0, 1, c)
    for xx in range(x0, x1):
        for yy in range(y - h + 1, y):
            if (xx + yy) % 4 == 0 or (xx - yy) % 4 == 0:
                if rnd.random() < 0.9:
                    cv.px(xx, yy, mul(c, 0.82))
    # barbed wire
    for xx in range(x0, x1, 3):
        cv.px(xx, y - h - 2 - (xx // 3) % 2, (96, 100, 120))


def barrel_fire(cv, rnd, x, y):
    cv.rect(x, y - 11, 8, 11, (86, 62, 58))
    cv.rect(x, y - 11, 2, 11, (120, 84, 70))
    cv.rect(x, y - 8, 8, 1, (56, 40, 44))
    cv.rect(x, y - 4, 8, 1, (56, 40, 44))
    cv.lrect(x + 1, y - 13, 6, 2, (255, 150, 50), 1.0, body=(255, 200, 90))
    cv.lrect(x + 2, y - 16, 2, 3, (255, 120, 40), 1.0, body=(255, 170, 70))
    cv.lrect(x + 5, y - 15, 1, 2, (255, 120, 40), 1.0, body=(255, 220, 120))
    cv.lpx(x + 3, y - 19, (255, 110, 40), 0.9)
    cv.lpx(x + 6, y - 21, (255, 90, 40), 0.7)
    cv.light(x - 12, y - 30, 32, 30, (255, 130, 50), 1.0)


def rubble(cv, rnd, x, y, w):
    for _ in range(w // 2):
        rx = x + int(rnd.triangular(0, w, w / 2))
        hh = max(1, int(6 * (1 - abs(rx - x - w / 2) / (w / 2))) + rnd.randrange(-1, 2))
        c = mul(CONC, rnd.uniform(0.6, 1.1))
        cv.rect(rx, y - hh, rnd.randrange(2, 5), hh, c)
    for _ in range(w // 10):
        cv.rect(x + rnd.randrange(w), y - rnd.randrange(3, 9), rnd.randrange(3, 7), 1, (94, 58, 48))


def wreck(cv, rnd, x, y):
    """A wrecked car."""
    c = rnd.choice([(92, 70, 66), (64, 80, 96), (96, 90, 66)])
    cv.rect(x, y - 8, 30, 6, c)
    cv.rect(x + 6, y - 14, 16, 6, mul(c, 0.9))
    cv.rect(x + 8, y - 13, 5, 4, (22, 22, 38))
    cv.rect(x + 15, y - 13, 5, 4, (22, 22, 38))
    cv.rect(x, y - 8, 30, 1, mul(c, 1.3))
    for xx in (x + 4, x + 21):
        cv.ellipse(xx, y - 5, 6, 6, (20, 18, 28))
        cv.px(xx + 2, y - 3, (70, 70, 84))
    shade(cv, x + 22, y - 8, 8, 6, 0.7)
    cv.speckle(x, y - 14, 30, 12, 0.3, rnd, 0.3)


def bunker_bar(cv, rnd, x, w=132):
    """A bunker-like concrete bar: the only place still lit in the whole stretch."""
    top = GY - 62
    cv.rect(x, top, w, 62, mul(CONC, 0.8))
    cv.speckle(x, top, w, 62, 0.14, rnd, 0.3)
    cv.rect(x - 3, top - 6, w + 6, 6, mul(CONC, 1.05))
    cv.rect(x - 3, top - 6, w + 6, 1, mul(CONC, 1.4))
    cv.rect(x - 3, top - 1, w + 6, 1, CONC_D)
    # the open frontage
    ox, ow_, oy, oh = x + 18, w - 36, top + 22, 37
    cv.rect(ox - 2, oy - 2, ow_ + 4, oh + 2, CONC_D)
    cv.rect(ox, oy, ow_, oh, (52, 22, 36))
    # bottle shelves
    for r in range(3):
        yy = oy + 4 + r * 6
        cv.lrect(ox + 6, yy + 4, ow_ - 12, 1, (150, 40, 60), 0.5)
        for xx in range(ox + 7, ox + ow_ - 7, 2):
            if rnd.random() < 0.8:
                cv.lrect(xx, yy + 4 - rnd.choice([3, 4]), 1, rnd.choice([3, 4]), rnd.choice([(255, 90, 90), (255, 160, 120), (255, 210, 160), (220, 90, 140)]), 0.55)
    # counter and customers
    cv.rect(ox, oy + 24, ow_, 3, (150, 92, 104))
    cv.rect(ox, oy + 24, ow_, 1, (214, 150, 150))
    cv.rect(ox, oy + 27, ow_, 10, (66, 36, 56))
    for xx in range(ox + 6, ox + ow_ - 8, 13):
        cv.rect(xx + 1, oy + 29, 3, 1, (120, 110, 130))
        cv.rect(xx + 2, oy + 30, 1, 7, (90, 84, 104))
        if rnd.random() < 0.5:
            cv.rect(xx, oy + 17, 4, 4, (24, 16, 28))
            cv.rect(xx - 1, oy + 21, 6, 8, (24, 16, 28))
    for xx in (ox + 4, ox + ow_ - 11, ox + ow_ // 2 - 3):
        lantern(cv, xx, oy + 3, c=(255, 60, 60))
    # red neon sign
    t = '赤提灯'
    sw = len(t) * 17 + 8
    sx = x + (w - sw) // 2
    cv.rect(sx, top + 1, sw, 20, (30, 16, 30))
    cv.lline([(sx + 1, top + 2), (sx + sw - 2, top + 2), (sx + sw - 2, top + 19), (sx + 1, top + 19), (sx + 1, top + 2)], RED, 0.8)
    for i, ch in enumerate(t):
        m = text_mask(ch)
        cv.lmask(sx + 5 + i * 17 + (16 - m.width) // 2, top + 3 + (16 - m.height) // 2, m, RED, 1.0)
    # side door and exit light
    cv.rect(x + 3, GY - 26, 10, 26, (28, 22, 40))
    cv.rect(x + 2, GY - 34, 13, 6, (40, 20, 28))
    m = text_mask('EXIT', F8)
    cv.lmask(x + 3, GY - 33, m.crop((0, 0, min(m.width, 11), m.height)), RED, 0.9)
    # ventilation duct
    cv.rect(x + w - 12, top - 20, 8, 14, (74, 76, 96))
    cv.rect(x + w - 14, top - 22, 12, 3, (96, 98, 118))
    return top


def dead_billboard(cv, rnd, x, top, w=84):
    """A dead billboard on the roof, with half of its letters no longer lit."""
    bh = 26
    by = top - bh - 12
    for xx in (x + 6, x + w - 8):
        cv.rect(xx, by + bh, 2, 12, IRON)
    cv.line([(x + 7, top - 1), (x + w - 7, by + bh)], IRON)
    cv.line([(x + w - 7, top - 1), (x + 7, by + bh)], IRON)
    cv.rect(x, by, w, bh, (34, 30, 50))
    cv.rect(x, by, w, 1, (70, 64, 96))
    t = rnd.choice(['HOTEL', 'CINEMA', 'MOTEL', 'DISCO', 'GARAGE'])
    dead = rnd.sample(range(len(t)), k=2)
    col = rnd.choice([(255, 80, 120), (255, 150, 70), (120, 200, 255)])
    m = text_mask(t, F8B)
    m = m.resize((m.width * 2, m.height * 2), Image.NEAREST)
    ox = x + (w - m.width) // 2
    oy = by + (bh - m.height) // 2
    cw = m.width // len(t)
    for i in range(len(t)):
        part = m.crop((i * cw, 0, (i + 1) * cw if i < len(t) - 1 else m.width, m.height))
        if i in dead:
            cv.mask(ox + i * cw, oy, part, (70, 40, 60))  # the letters that no longer light
        else:
            cv.lmask(ox + i * cw, oy, part, col, 0.9)
    # holes punched through it
    for _ in range(3):
        hx, hy = x + rnd.randrange(4, w - 8), by + rnd.randrange(3, bh - 6)
        cv.rect(hx, hy, rnd.randrange(3, 7), rnd.randrange(2, 5), (14, 12, 24))


def overpass(cv, rnd, x, w=96):
    """An overpass crossing the view: the divide between the two districts."""
    deck_y = 92
    c = (78, 76, 100)
    # pier
    px_ = x + w // 2 - 15
    cv.rect(px_, deck_y, 30, GY - deck_y, c)
    cv.rect(px_, deck_y, 3, GY - deck_y, mul(c, 1.3))
    cv.rect(px_ + 24, deck_y, 6, GY - deck_y, mul(c, 0.62))
    cv.speckle(px_, deck_y, 30, GY - deck_y, 0.14, rnd, 0.3)
    for yy in range(deck_y + 30, GY, 34):
        cv.rect(px_, yy, 30, 1, mul(c, 0.6))
    cv.poly([(px_ - 12, deck_y + 14), (px_, deck_y + 30), (px_, deck_y + 14)], mul(c, 0.8))
    cv.poly([(px_ + 42, deck_y + 14), (px_ + 30, deck_y + 30), (px_ + 30, deck_y + 14)], mul(c, 0.55))
    # graffiti and hazard stripes on the pier
    for i in range(6):
        cv.rect(px_ + i * 5, GY - 12 + (0 if i % 2 else 0), 5, 5, (220, 180, 60) if i % 2 == 0 else (30, 28, 40))
    for _ in range(3):
        gc = rnd.choice([MAG, CYA, GRN, YEL])
        gx, gy = px_ + 4, GY - 60 + rnd.randrange(30)
        pts = [(gx + i * 4, gy + rnd.randrange(0, 10)) for i in range(6)]
        cv.line(pts, mul(gc, 0.7))
    # box girder carrying the deck
    cv.rect(x, deck_y - 4, w, 20, c)
    cv.rect(x, deck_y - 4, w, 2, mul(c, 1.35))
    cv.rect(x, deck_y + 12, w, 4, mul(c, 0.55))
    cv.speckle(x, deck_y - 4, w, 20, 0.12, rnd, 0.3)
    # railing and noise barrier
    cv.rect(x, deck_y - 14, w, 10, (50, 56, 84))
    for xx in range(x, x + w, 12):
        cv.rect(xx, deck_y - 14, 1, 10, (34, 38, 60))
    cv.rect(x, deck_y - 15, w, 1, (96, 104, 140))
    # sodium lamps
    for xx in (x + 14, x + w - 16):
        cv.rect(xx, deck_y - 40, 1, 26, (50, 52, 72))
        cv.rect(xx - 4, deck_y - 40, 5, 1, (50, 52, 72))
        cv.lrect(xx - 5, deck_y - 39, 3, 1, (255, 170, 70), 1.0, body=(255, 230, 180))
        cv.light(xx - 16, deck_y - 36, 26, 22, (255, 170, 70), 0.9)
    # road sign
    cv.rect(x + w // 2 - 22, deck_y - 6, 44, 20, (26, 92, 78))
    cv.rect(x + w // 2 - 22, deck_y - 6, 44, 1, (200, 220, 210))
    cv.rect(x + w // 2 - 22, deck_y + 13, 44, 1, (16, 56, 50))
    m = text_mask('出口', F16)
    cv.mask(x + w // 2 - m.width // 2, deck_y - 4 + (16 - m.height) // 2, m, (224, 240, 230))
    cv.light(x + w // 2 - 20, deck_y - 6, 40, 20, (150, 220, 255), 0.5)
    # cold light under the girder
    cv.lrect(x + 8, deck_y + 16, 10, 1, (150, 220, 255), 0.9)
    cv.lrect(x + w - 18, deck_y + 16, 10, 1, (150, 220, 255), 0.9)
    cv.light(px_ - 14, deck_y + 20, 58, 60, (150, 220, 255), 0.5)
    cv.light(px_ - 6, GY - 40, 42, 40, (255, 170, 70), 0.45)


def ruin_back(cv, rnd, x0, x1):
    """Silhouettes behind the derelict blocks: unfinished towers, a crane, a chimney,
    a gas holder."""
    c = (52, 44, 78)
    x = x0
    while x < x1:
        kind = rnd.choice(['slab', 'slab', 'crane', 'chimney', 'tank'])
        if kind == 'slab':
            w = rnd.randrange(60, 120)
            top = rnd.randrange(60, 150)
            cv.rect(x, top, w, GY - top, c)
            for fy in range(top + 6, GY - 10, 12):
                cv.rect(x + 3, fy, w - 6, 6, mul(c, 0.55))
                for wx in range(x + 5, x + w - 8, 9):
                    if rnd.random() < 0.06:
                        cv.lrect(wx, fy + 1, 4, 4, rnd.choice([(255, 170, 90), (170, 255, 200)]), 0.5)
            for xx in range(x, x + w, 9):
                cv.rect(xx, top - rnd.randrange(2, 12), 2, 12, c)
            x += w + rnd.randrange(0, 20)
        elif kind == 'crane':
            bx = x + 20
            cv.rect(bx, 30, 3, GY - 30, c)
            for yy in range(34, GY - 10, 6):
                cv.line([(bx, yy), (bx + 2, yy + 5)], mul(c, 1.3))
            cv.rect(bx - 22, 34, 80, 2, c)
            cv.line([(bx + 1, 24), (bx + 56, 34)], c)
            cv.line([(bx + 1, 24), (bx - 20, 34)], c)
            cv.rect(bx + 1, 22, 1, 10, c)
            cv.rect(bx + 40, 36, 1, 30, mul(c, 0.8))
            cv.lpx(bx + 1, 21, RED, 1.0)
            x += 66
        elif kind == 'chimney':
            cv.poly([(x + 6, GY), (x + 9, 50), (x + 17, 50), (x + 20, GY)], c)
            for yy in range(56, 80, 8):
                cv.rect(x + 9, yy, 8, 3, mul(c, 1.35) if (yy // 8) % 2 else (120, 50, 60))
            cv.lpx(x + 13, 48, RED, 1.0)
            x += 40
        else:
            cv.ellipse(x, GY - 110, 64, 64, c)
            cv.rect(x + 8, GY - 60, 3, 60, c)
            cv.rect(x + 52, GY - 60, 3, 60, c)
            cv.line([(x + 10, GY - 20), (x + 52, GY - 56)], c)
            cv.rect(x, GY - 80, 64, 1, mul(c, 1.3))
            x += 80


def ruin_district(cv, rnd, x0, x1):
    # the pavement is broken up
    for _ in range((x1 - x0) // 12):
        cv.rect(x0 + rnd.randrange(x1 - x0), GY + rnd.randrange(0, 5), rnd.randrange(2, 6), 1, (50, 50, 70))
    x = x0 + 4
    tops = []
    plan = ['block', 'gap', 'bar', 'block', 'gap', 'block']
    for kind in plan:
        if x > x1 - 70:
            break
        if kind == 'block':
            w = min(rnd.randrange(104, 150), x1 - 6 - x)
            nfl = rnd.choice([3, 4, 5])
            top = ruin_block(cv, rnd, x, w, nfl)
            ladder(cv, x + w + 1, top + 8, GY - 20)
            if rnd.random() < 0.7:
                dead_billboard(cv, rnd, x + rnd.randrange(4, max(5, w - 88)), top)
            tops.append((x, w, top))
            x += w + 12
        elif kind == 'bar':
            top = bunker_bar(cv, rnd, x)
            tops.append((x, 132, top))
            x += 132 + 10
        else:
            w = rnd.randrange(50, 76)
            # vacant lot: fence, rubble, a burning barrel, a wreck
            cv.rect(x - 4, GY - 30, w + 8, 30, (40, 36, 58))
            cv.speckle(x - 4, GY - 30, w + 8, 30, 0.2, rnd, 0.3)
            for xx in range(x - 4, x + w + 4, 6):
                cv.rect(xx, GY - 30 - rnd.choice([0, 2, 5, 8]), 6, 8, (40, 36, 58))
            rubble(cv, rnd, x, GY, w)
            if rnd.random() < 0.6:
                wreck(cv, rnd, x + 6, GY)
            barrel_fire(cv, rnd, x + w - 14, GY)
            fence(cv, rnd, x - 6, x + w + 6, GY + 1, 22)
            x += w + 6
    # cables drooping between the buildings
    for i in range(len(tops) - 1):
        ax, aw, at = tops[i]
        bx, bw_, bt = tops[i + 1]
        cable(cv, ax + aw - 4, at + 6, bx + 4, bt + 10, rnd.randrange(10, 22))
    # street lamps, some of them dead
    for xx in range(x0 + 40, x1 - 20, 150):
        street_lamp(cv, xx, GY, h=54, c=(255, 150, 80) if rnd.random() < 0.5 else (60, 50, 40))
    return tops


# ------------------------------------------------------------------ Composition
def wet_road(im, strength=0.5, seed=3):
    """Mirror everything above the road into the standing water on it.
    im has already been upscaled by px.SCALE."""
    k = px.SCALE
    gy = (GY + 7) * k
    a = np.asarray(im).astype(np.float32) / 255
    h, w = a.shape[:2]
    rnd = np.random.RandomState(seed)
    out = a.copy()
    for y in range(gy, h):
        d = (y - gy) / k
        sy = gy - 8 * k - int(d * 2.6 * k)
        if sy < 0:
            break
        row = a[sy]
        # jitter each row sideways to break the reflection into ripples
        sh = int(round((np.sin(d * 1.7) * 1.5 + rnd.randint(-1, 2)) * k))
        row = np.roll(row, sh, axis=0)
        f = strength * (1 - (y - gy) / (h - gy)) ** 0.6
        lum = row[:, :3].max(axis=1, keepdims=True)
        refl = row[:, :3] * row[:, 3:4] * (0.35 + 0.65 * lum)
        out[y, :, :3] = np.clip(out[y, :, :3] + refl * f, 0, 1)
    # vertical smearing
    from scipy.ndimage import uniform_filter1d

    band = out[gy:, :, :3]
    out[gy:, :, :3] = band * 0.55 + uniform_filter1d(band, size=5 * k, axis=0, mode='nearest') * 0.45
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')


def build_c2(seed=11, w_neon=1440, w_ruin=720):
    """The mid-distance strip: [overpass][neon district...][overpass][derelict...],
    joining seamlessly end to end."""
    rnd = random.Random(seed)
    W = w_neon + w_ruin
    back = Cv(W, H)
    back_row(back, rnd, 0, w_neon)
    ruin_back(back, rnd, w_neon + 20, W - 20)
    fog_row = np.linspace(0.34, 0.2, H).astype(np.float32)
    im_back = render(back, ambient=(0.12, 0.13, 0.30), fog=((58, 36, 96), fog_row), bloom=(0.5, 1.6), haze=(0.3, 10.0))

    cv = Cv(W, H)
    street(cv, rnd, 0, W)
    neon_district(cv, rnd, 48, w_neon)
    ruin_district(cv, rnd, w_neon + 48, W)
    op = Cv(96, H)
    overpass(op, rnd, 0, 96)
    for ox in (-48, W - 48, w_neon - 48):
        cv.paste(op, ox, 0) if 0 <= ox <= W - 96 else None
    # the overpass that straddles the seam: half pasted at each end
    half_l, half_r = Cv(48, H), Cv(48, H)
    for dst, sx in ((half_r, 0), (half_l, 48)):
        dst.im = op.im.crop((sx, 0, sx + 48, H))
        dst.em = op.em.crop((sx, 0, sx + 48, H))
        dst.lt = op.lt.crop((sx, 0, sx + 48, H))
    cv.paste(half_r, W - 48, 0)
    cv.paste(half_l, 0, 0)
    # Ambient light dims toward the top. The derelict stretch has no neon of its own,
    # so it is carried by brighter, more cyan moonlight
    amb = np.ones((H, W, 3), np.float32)
    amb[:GY] *= np.linspace(0.62, 1.0, GY).reshape(GY, 1, 1)
    t = np.clip((np.arange(W) - w_neon) / 60.0, 0, 1) * np.clip((W - np.arange(W)) / 60.0, 0, 1)
    amb *= (1 + t.reshape(1, W, 1) * np.array([0.9, 1.25, 1.1], np.float32).reshape(1, 1, 3))
    im = render(cv, ambient=(0.15, 0.16, 0.34), amb_grad=amb, spill=(2.6, 6.0), spill2=(2.0, 18.0), bloom=(0.5, 1.6), haze=(0.26, 10.0))
    out = Image.alpha_composite(im_back, im)
    return wet_road(out)
