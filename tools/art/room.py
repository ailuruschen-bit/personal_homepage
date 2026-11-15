"""车厢内景。在 720×480 的画布上画（场景坐标 x∈[-120,600)），再切成中间 480 与左右各 120 的延伸段。"""
import random

import numpy as np
from PIL import Image

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


class Off:
    """带水平偏移的画布包装：下面所有坐标都写场景坐标"""

    def __init__(self, cv):
        self.cv = cv

    def _p(self, pts):
        return [(x + OX, y) for x, y in pts]

    def rect(self, x, y, w, h, c):
        self.cv.rect(x + OX, y, w, h, c)

    def px(self, x, y, c):
        self.cv.px(x + OX, y, c)

    def line(self, pts, c, width=1):
        self.cv.line(self._p(pts), c, width)

    def poly(self, pts, c):
        self.cv.poly(self._p(pts), c)

    def ellipse(self, x, y, w, h, c):
        self.cv.ellipse(x + OX, y, w, h, c)

    def rrect(self, x, y, w, h, r, c):
        self.cv.rrect(x + OX, y, w, h, r, c)

    def mask(self, x, y, m, c):
        self.cv.mask(x + OX, y, m, c)

    def lrect(self, x, y, w, h, c, k=1.0, body=None):
        self.cv.lrect(x + OX, y, w, h, c, k, body)

    def lpx(self, x, y, c, k=1.0):
        self.cv.lpx(x + OX, y, c, k)

    def lline(self, pts, c, k=1.0, width=1, body=None):
        self.cv.lline(self._p(pts), c, k, width, body)

    def fline(self, pts, c, k=0.0, width=1, body=None):
        self.cv.fline([(x + OX, y) for x, y in pts], c, k, width, body)

    def lpoly(self, pts, c, k=1.0, body=None):
        p = self._p(pts)
        self.cv.d.polygon(p, fill=tuple(body or c) + (255,))
        self.cv.e.polygon(p, fill=mul(c, k))

    def lellipse(self, x, y, w, h, c, k=1.0, body=None):
        self.cv.lellipse(x + OX, y, w, h, c, k, body)

    def light(self, x, y, w, h, c, k=1.0):
        self.cv.light(x + OX, y, w, h, c, k)

    def shadow(self, x, y, w, h, k=0.5, ell=False):
        self.cv.shadow(x + OX, y, w, h, k, ell)

    def shade(self, x, y, w, h, k):
        parts.shade(self.cv, x + OX, y, w, h, k)

    def speckle(self, x, y, w, h, amount, rnd, density=0.12):
        self.cv.speckle(x + OX, y, w, h, amount, rnd, density)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ri(p):
    return (int(round(p[0])), int(round(p[1])))


# ------------------------------------------------------------------ 壳体
def shell(g, rnd):
    L, Wd = -120, 720
    # 天花
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
    # 通风格栅
    for x0 in (-60, 150, 300, 470):
        g.rect(x0, 8, 30, 10, (40, 42, 66))
        for y in range(10, 17, 2):
            g.rect(x0 + 2, y, 26, 1, (24, 26, 44))
    # 顶角线
    g.rect(L, 48, Wd, 10, (50, 54, 84))
    g.rect(L, 48, Wd, 1, (96, 102, 140))
    g.rect(L, 56, Wd, 2, (30, 32, 54))
    # 上墙：带菱形暗纹的墙板
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
    # 墙板接缝与铆钉
    for x in (-92, -8, 30, 116, 364, 450, 488, 572):
        g.rect(x, 58, 1, 232, mul(WALL, 0.62))
        g.rect(x + 1, 58, 1, 232, mul(WALL, 1.18))
        for y in range(70, 288, 26):
            g.px(x - 3, y, mul(WALL, 1.35))
            g.px(x - 3, y + 1, mul(WALL, 0.6))
            g.px(x + 4, y, mul(WALL, 1.35))
            g.px(x + 4, y + 1, mul(WALL, 0.6))
    # 水渍与划痕
    for _ in range(60):
        x, y = rnd.randrange(L, 600), rnd.randrange(60, 250)
        for i in range(rnd.randrange(8, 40)):
            g.shade(x, y + i, rnd.choice([1, 1, 2]), 1, 0.9)
    for _ in range(26):
        x, y = rnd.randrange(L, 600), rnd.randrange(110, 288)
        g.line([(x, y), (x + rnd.randrange(3, 12), y - rnd.randrange(1, 4))], mul(WALL, 1.16))
    # 腰线 + 灯带
    g.rect(L, 288, Wd, 8, (70, 80, 118))
    g.rect(L, 288, Wd, 1, (128, 138, 176))
    g.rect(L, 294, Wd, 2, (36, 42, 70))
    g.lrect(L, 296, Wd, 2, (95, 242, 230), 0.8, body=(170, 250, 244))
    # 下墙：竖向压型板
    g.rect(L, 298, Wd, 142, WALL_LO)
    for x in range(L, 600, 6):
        g.rect(x, 298, 1, 138, mul(WALL_LO, 0.84))
        g.rect(x + 1, 298, 1, 138, mul(WALL_LO, 1.08))
    g.rect(L, 298, Wd, 2, mul(WALL_LO, 0.6))
    g.speckle(L, 298, Wd, 142, 0.08, rnd, 0.25)
    for x in (-8, 30, 116, 364, 450, 488):
        g.rect(x, 300, 2, 136, mul(WALL_LO, 0.6))
    # 踢脚与地板
    g.rect(L, 434, Wd, 6, (38, 42, 68))
    g.rect(L, 434, Wd, 1, (84, 90, 126))
    g.rect(L, 440, Wd, 40, (46, 48, 76))
    for x0 in range(-360, 840, 30):
        x1 = 240 + (x0 - 240) * 1.42
        g.line([(x0, 440), (x1, 480)], (28, 30, 50))
    for y in (449, 462):
        g.rect(L, y, Wd, 1, (28, 30, 50))
    g.speckle(L, 440, Wd, 40, 0.12, rnd, 0.3)
    # 采暖格栅
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


# ------------------------------------------------------------------ 行李架
def rack(g, rnd):
    g.shadow(-120, 96, 720, 12, 0.5)
    # 路线图
    g.shadow(172, 86, 136, 6, 0.6)
    g.rect(173, 67, 134, 20, (60, 66, 100))
    g.rect(173, 67, 134, 1, (120, 130, 170))
    g.rect(173, 86, 134, 1, (30, 32, 54))
    g.rect(176, 70, 128, 14, (16, 18, 36))
    g.lrect(186, 76, 108, 1, (150, 162, 214), 0.55)
    for i in range(7):
        x = 186 + i * 18
        if i == 2:
            g.lrect(x - 2, 74, 5, 5, (255, 70, 80), 1.0, body=(255, 150, 150))
            g.lpx(x, 76, (255, 230, 230), 1.0)
        else:
            c = (220, 226, 255) if i < 2 else (120, 130, 180)
            g.lrect(x - 1, 75, 3, 3, c, 0.9 if i < 2 else 0.5)
        g.lrect(x - 2, 81, 5, 1, (96, 104, 150), 0.3)
    g.lpx(298, 76, (150, 162, 214), 0.6)
    g.lpx(297, 75, (150, 162, 214), 0.6)
    g.lpx(297, 77, (150, 162, 214), 0.6)
    for x in (175, 304):
        g.px(x, 69, (150, 158, 190))
        g.px(x, 84, (150, 158, 190))
    # 托架
    for x in (-100, -30, 70, 164, 346, 440, 510, 580):
        g.rect(x, 60, 3, 37, (84, 94, 130))
        g.rect(x, 60, 1, 37, (136, 146, 182))
        g.rect(x - 2, 60, 7, 3, (64, 72, 106))
        g.line([(x + 3, 84), (x + 9, 93)], (64, 72, 106))
    # 行李（底边 y=92）
    # 纸箱
    g.rect(28, 72, 36, 20, (176, 138, 98))
    g.rect(28, 72, 36, 2, (210, 174, 130))
    g.rect(28, 90, 36, 2, (120, 90, 66))
    g.rect(43, 72, 6, 20, (206, 186, 150))
    g.rect(52, 78, 9, 6, (236, 230, 214))
    g.rect(53, 80, 6, 1, (120, 60, 60))
    g.rect(53, 82, 4, 1, (90, 90, 110))
    g.shade(60, 72, 4, 20, 0.8)
    # 卷起来的图纸
    g.rect(6, 86, 24, 6, (226, 222, 210))
    g.rect(6, 86, 24, 1, (250, 248, 240))
    g.rect(6, 90, 24, 2, (170, 166, 160))
    g.ellipse(27, 86, 5, 6, (190, 186, 178))
    g.px(29, 88, (90, 88, 96))
    g.rect(14, 86, 2, 6, (200, 70, 70))
    # 旅行袋
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
    # 公文包（聚焦轮廓：318-386 × 55-92）
    lb = (150, 96, 62)
    g.rect(318, 58, 68, 34, lb)
    g.rect(318, 58, 68, 3, mul(lb, 1.3))
    g.rect(318, 61, 68, 6, mul(lb, 1.14))
    g.rect(318, 84, 68, 8, mul(lb, 0.74))
    g.rect(318, 58, 1, 34, mul(lb, 0.6))
    g.rect(385, 58, 1, 34, mul(lb, 0.55))
    g.rect(318, 91, 68, 1, mul(lb, 0.5))
    g.speckle(318, 58, 68, 34, 0.1, rnd, 0.3)
    for x in range(321, 384, 3):
        g.px(x, 63, mul(lb, 1.45))
        g.px(x, 88, mul(lb, 1.2))
    for x in (331, 368):
        g.rect(x, 58, 6, 34, mul(lb, 0.58))
        g.rect(x, 58, 1, 34, mul(lb, 0.8))
        g.rect(x, 70, 6, 5, BRASS)
        g.rect(x + 1, 71, 4, 3, mul(BRASS, 0.6))
        g.px(x + 1, 70, (255, 236, 170))
    g.rect(346, 55, 12, 3, (70, 42, 34))
    g.rect(347, 55, 10, 1, (120, 78, 56))
    g.rect(349, 61, 6, 5, BRASS)
    g.px(351, 63, (90, 60, 30))
    g.px(349, 61, (255, 236, 170))
    for x, y in ((318, 58), (384, 58), (318, 90), (384, 90)):
        g.rect(x, y, 2, 2, BRASS)
    g.ellipse(340, 74, 9, 9, (70, 170, 160))
    g.rect(343, 77, 3, 3, (236, 240, 240))
    g.rect(354, 78, 10, 7, (214, 70, 70))
    g.rect(354, 80, 10, 2, (240, 232, 220))
    # 长柄伞
    g.rect(398, 88, 42, 4, (44, 50, 84))
    g.rect(398, 88, 42, 1, (84, 92, 136))
    g.rect(412, 88, 2, 4, (150, 60, 70))
    g.rect(394, 89, 4, 2, (160, 166, 190))
    g.line([(440, 89), (446, 89), (447, 86), (445, 84)], BRASS)
    # 搁板：两道横杆
    g.rect(-120, 92, 720, 2, STEEL)
    g.rect(-120, 92, 720, 1, (170, 180, 210))
    g.rect(-120, 96, 720, 1, (64, 72, 106))
    for x in range(-120, 600, 4):
        g.px(x, 94, (84, 94, 130))
        g.px(x + 2, 95, (84, 94, 130))


# ------------------------------------------------------------------ 车窗与窗帘
def window(g, rnd):
    # 铜杆
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
    # 窗帘（束在两侧）
    cc = (58, 110, 96)
    for x0 in (123, 344):
        g.shadow(x0 - 1, 106, 16, 168, 0.62)
        for i in range(13):
            k = [0.72, 0.9, 1.15, 1.3, 1.05, 0.8, 0.66, 0.84, 1.1, 1.26, 1.0, 0.78, 0.62][i]
            g.rect(x0 + i, 104, 1, 164, mul(cc, k))
        for x in range(x0, x0 + 13, 2):
            g.rect(x, 100, 1, 5, (150, 112, 56))
        # 束带
        g.rect(x0, 196, 13, 3, BRASS)
        g.rect(x0, 196, 13, 1, (255, 232, 160))
        g.rect(x0, 200, 13, 2, mul(cc, 0.5))
        for i in range(13):
            hh = [0, 2, 4, 5, 4, 2, 0, 1, 3, 5, 4, 2, 0][i]
            g.rect(x0 + i, 268, 1, hh + 1, mul(cc, 0.9))
        g.rect(x0 + 6, 199, 1, 6, (190, 146, 70))
        g.rect(x0 + 5, 205, 3, 3, (230, 190, 100))
    # 窗框
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
    # 把手
    g.rect(232, 269, 16, 4, (60, 68, 104))
    g.rect(234, 270, 12, 2, (160, 170, 204))
    # 窗台
    g.shadow(129, 283, 222, 9, 0.5)
    g.rect(130, 277, 220, 6, mul(fr, 0.95))
    g.rect(130, 277, 220, 1, (184, 196, 228))
    g.rect(130, 282, 220, 1, (50, 56, 88))
    g.rect(132, 283, 216, 2, (40, 46, 74))
    # 窗台上的小物：一盆多肉、一枚硬币
    g.rect(154, 271, 9, 6, (176, 96, 70))
    g.rect(153, 270, 11, 2, (208, 124, 90))
    g.rect(155, 266, 2, 4, (86, 160, 110))
    g.rect(158, 264, 3, 6, (106, 184, 124))
    g.rect(161, 267, 2, 3, (76, 140, 100))
    g.px(159, 263, (150, 220, 160))
    # 铭牌
    g.rect(221, 284, 39, 6, (26, 28, 48))
    g.rect(221, 284, 39, 1, (70, 76, 110))
    g.lrect(224, 286, 9, 2, AMBER, 0.85)
    g.lrect(236, 286, 4, 1, (120, 130, 170), 0.3)
    g.lrect(242, 286, 8, 1, (120, 130, 170), 0.3)
    g.lrect(236, 288, 12, 1, (120, 130, 170), 0.2)


# ------------------------------------------------------------------ 墙上的东西
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
    # ---- 左墙
    poster(g, 22, 118, 48, 70, 'sunset')
    # 霓虹灯管
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
    # 拍立得
    for x, y, c in ((106, 146, (90, 130, 170)), (109, 166, (190, 120, 90))):
        g.shadow(x, y + 1, 13, 15, 0.7)
        g.rect(x, y, 12, 14, (238, 234, 224))
        g.rect(x + 1, y + 1, 10, 9, c)
        g.rect(x + 1, y + 7, 10, 3, mul(c, 0.6))
        g.px(x + 6, y - 1, (220, 70, 70))
    # 喇叭
    g.rect(84, 264, 24, 16, (52, 58, 90))
    g.rect(84, 264, 24, 1, (110, 118, 156))
    for y in range(267, 278, 2):
        for x in range(87, 106, 2):
            g.px(x + (y // 2) % 2, y, (22, 24, 42))
    # ---- 右墙
    # 壁灯
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
    # 控制面板（聚焦区外，仅装饰）
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
    # 小画框与应急锤
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


# ------------------------------------------------------------------ 座椅
def seat(g, rnd, mirror):
    def X(x):
        return 480 - x if mirror else x

    def P(pts):
        return [(X(x), y) for x, y in pts]

    def R(x, y, w, h, c):
        g.rect(X(x + w - 1) if mirror else x, y, w, h, c)

    back = SEAT
    # 椅背投在墙上的影子
    g.shadow(X(84) if mirror else 68, 236, 16, 120, 0.55)
    g.shadow(X(146) if mirror else 10, 346, 136, 14, 0.6)
    # 底座
    R(10, 428, 124, 52, (56, 30, 50))
    R(10, 428, 124, 2, (30, 16, 30))
    R(14, 436, 116, 1, (84, 48, 70))
    # 坐垫正面
    R(10, 404, 124, 24, mul(back, 0.72))
    R(10, 404, 124, 2, mul(back, 1.25))
    R(10, 424, 124, 4, mul(back, 0.5))
    for x in range(16, 130, 9):
        g.px(X(x), 407, mul(back, 1.5))
    # 坐垫顶面
    g.poly(P([(70, 352), (141, 352), (133, 404), (10, 404)]), mul(back, 1.12))
    g.poly(P([(70, 352), (141, 352), (140, 358), (63, 358)]), mul(back, 0.8))
    g.line(P([(52, 368), (138, 368)]), mul(back, 0.94))
    g.line(P([(34, 384), (136, 384)]), mul(back, 0.94))
    g.line(P([(14, 402), (132, 402)]), mul(back, 1.4))
    for x, y in ((92, 364), (112, 376), (72, 378), (96, 392), (50, 394), (120, 396)):
        g.px(X(x), y, mul(back, 0.6))
        g.px(X(x), y + 1, mul(back, 1.5))
    # 椅背正面
    g.poly(P([(10, 249), (70, 238), (70, 352), (10, 404)]), back)
    # 菱形拉扣
    def ty(x):
        return 286 - (x - 10) * 22 / 60

    pts = {}
    for j in range(5):
        for i in range(5):
            x = 16 + i * 13 + (6 if j % 2 else 0)
            y = ty(x) + 10 + j * 17
            pts[(i, j)] = (x, y)
    for (i, j), (x, y) in pts.items():
        for di in ((0, 1), (-1, 1)) if j % 2 == 0 else ((0, 1), (1, 1)):
            q = pts.get((i + di[0], j + di[1]))
            if q and q[0] < 70 and x < 70:
                g.line([(X(x), int(y)), (X(q[0]), int(q[1]))], mul(back, 0.78))
    for (i, j), (x, y) in pts.items():
        if 12 < x < 68 and y < 392 - (70 - x) * 0.8:
            g.rect(X(x) - (1 if mirror else 0), int(y), 2, 2, mul(back, 0.5))
            g.px(X(x), int(y) - 1, mul(back, 1.5))
    # 外侧立面与顶面
    g.poly(P([(0, 252), (10, 249), (10, 480), (0, 480)]), mul(back, 0.5))
    g.poly(P([(0, 250), (10, 247), (70, 236), (70, 238), (10, 249), (0, 252)]), mul(back, 1.5))
    # 靠近墙的一侧压暗
    g.poly(P([(66, 262), (70, 261), (70, 352), (66, 355)]), mul(back, 0.7))
    # 头枕巾
    cloth = (196, 192, 212)
    g.poly(P([(10, 249), (70, 238), (70, 264), (10, 286)]), cloth)
    g.poly(P([(10, 249), (70, 238), (70, 242), (10, 253)]), (226, 224, 240))
    for x in range(12, 70, 3):
        y = 286 - (x - 10) * 22 / 60
        g.px(X(x), int(y) - 1, (170, 164, 190))
        g.px(X(x + 1), int(y), cloth)
    for x in (24, 40, 56):
        y = 249 - (x - 10) * 11 / 60
        g.line(P([(x, int(y) + 5), (x - 1, int(y) + 24 - (x - 10) // 6)]), (198, 192, 214))
    g.poly(P([(0, 252), (10, 249), (10, 286), (0, 290)]), (176, 170, 194))


# ------------------------------------------------------------------ 桌子与桌上的东西
def table(g, rnd):
    BL, BR, FL, FR = (150, 327), (330, 327), (118, 372), (362, 372)
    # 桌腿
    g.shadow(196, 420, 88, 16, 0.5, ell=True)
    g.rect(232, 382, 16, 36, (64, 72, 108))
    g.rect(232, 382, 3, 36, (120, 130, 168))
    g.rect(244, 382, 4, 36, (36, 40, 66))
    g.poly([(224, 418), (256, 418), (262, 426), (218, 426)], (54, 60, 94))
    g.line([(224, 418), (256, 418)], (120, 130, 168))
    g.shadow(120, 384, 240, 14, 0.42)
    # 桌面
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
    # 包边与侧板
    g.rect(118, 372, 245, 2, BRASS)
    g.rect(118, 372, 245, 1, (255, 236, 170))
    g.rect(118, 374, 245, 9, mul(WOOD, 0.6))
    g.rect(118, 374, 245, 1, mul(WOOD, 0.42))
    g.rect(118, 382, 245, 1, mul(WOOD, 0.36))
    for x in range(124, 360, 12):
        g.px(x, 378, mul(WOOD, 0.9))
    # ---- 电脑（轮廓见 hotspots.ts 的 projects）
    g.shadow(152, 350, 96, 20, 0.5)
    S = [(148, 292), (214, 288), (218, 343), (151, 348)]
    g.poly(S, (44, 48, 76))
    g.line([S[0], S[1]], (120, 128, 166))
    g.line([S[0], S[3]], (84, 92, 130))
    D = [(151, 295), (212, 291), (215, 340), (154, 345)]
    g.lpoly(D, (40, 70, 160), 0.42, body=(22, 30, 62))
    colors = [MAG, CYA, (255, 206, 110), (150, 255, 170), (226, 232, 255), (176, 130, 255)]
    tilt = (D[0][1] - D[1][1]) / (D[1][0] - D[0][0])  # 跟着屏幕上边的斜率走
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
            # 每段本身是水平的，整行跟着透视逐段下沉：
            # 段内一旦带上斜率，就会多出一道硬台阶，反而像线被掰弯
            yc = y0 - ((x + x1) / 2 - 157) * tilt
            g.fline([(x, yc), (x1, yc)], c, 0.95)
            x += ln + 2
            if x > 204:
                break
    for r in range(10):
        g.lpx(154, int(round(299 + r * 4.4)), (90, 110, 170), 0.5)
    g.px(181, 290, (20, 22, 40))
    # 机身
    Bq = [(151, 348), (218, 343), (241, 357), (170, 366)]
    g.poly(Bq, (160, 168, 198))
    g.line([Bq[0], Bq[1]], (40, 44, 70))
    g.poly([(170, 366), (241, 357), (241, 359), (170, 368)], (92, 98, 132))
    for t in (0.14, 0.32, 0.5, 0.68):
        a, b = lerp(Bq[0], Bq[3], t), lerp(Bq[1], Bq[2], t)
        n = 13
        for i in range(n):
            p = lerp(a, b, (i + 0.5) / n)
            x, y = ri(p)
            g.rect(x - 1, y, 3, 2, (104, 112, 148))
            g.px(x - 1, y, (128, 136, 172))
    tp = lerp(lerp(Bq[0], Bq[3], 0.86), lerp(Bq[1], Bq[2], 0.86), 0.5)
    g.rect(int(tp[0]) - 7, int(tp[1]) - 1, 14, 3, (182, 190, 216))
    g.light(150, 336, 100, 40, (90, 150, 255), 0.5)
    g.light(146, 286, 76, 60, (80, 120, 255), 0.25)
    # ---- 咖啡
    g.shadow(256, 354, 62, 14, 0.5, ell=True)
    g.ellipse(258, 351, 58, 13, (232, 230, 244))
    g.ellipse(258, 351, 58, 11, (248, 246, 255))
    g.ellipse(266, 353, 42, 7, (196, 194, 220))
    g.line([(262, 357), (273, 360)], (190, 196, 214))
    g.rect(261, 356, 3, 2, (220, 224, 238))
    # 把手
    hc = (232, 230, 246)
    g.rect(301, 337, 7, 2, hc)
    g.rect(307, 338, 3, 9, hc)
    g.rect(301, 346, 7, 2, hc)
    g.px(309, 338, (190, 188, 214))
    g.px(309, 346, (190, 188, 214))
    g.rect(301, 348, 6, 1, (176, 174, 204))
    # 杯身
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
    # ---- 车票（轮廓见 hotspots.ts 的 about）
    g.shadow(318, 349, 32, 15, 0.6)
    T = [(316, 346), (344, 344), (348, 358), (320, 361)]
    g.poly(T, (240, 228, 198))
    g.line([T[0], T[1]], (255, 250, 232))
    g.line([T[3], T[2]], (170, 156, 130))
    g.fline([(319, 349.2), (336, 349.2)], (206, 60, 66), width=2)
    g.fline([(321, 352.8), (333, 352.8)], (96, 90, 104))
    g.fline([(322, 355.6), (330, 355.6)], (150, 140, 140))
    for y in range(346, 359, 2):
        g.px(338 + (y - 346) // 4, y, (170, 156, 130))
    g.rect(341, 349, 4, 4, (60, 56, 76))
    g.px(342, 350, (240, 228, 198))
    g.px(344, 352, (240, 228, 198))
    # ---- 钢笔
    g.line([(254, 366), (267, 363)], (40, 60, 120))
    g.line([(254, 367), (267, 364)], (24, 36, 80))
    g.px(268, 363, BRASS)
    g.px(258, 365, BRASS)


# ------------------------------------------------------------------ 两侧延伸段
def extensions(g, rnd):
    back = mul(SEAT, 0.82)
    for mirror in (False, True):
        def X(x):
            return 480 - x if mirror else x

        def R(x, y, w, h, c):
            g.rect(X(x + w - 1) if mirror else x, y, w, h, c)

        # 背靠背的邻座：只看到椅背背面
        R(-56, 252, 56, 228, back)
        R(-56, 250, 56, 3, mul(back, 1.5))
        R(-56, 252, 2, 228, mul(back, 0.6))
        R(-2, 252, 2, 228, mul(back, 0.55))
        R(-56, 428, 56, 52, (56, 30, 50))
        # 头枕巾背面
        R(-54, 253, 52, 26, (196, 190, 212))
        R(-54, 278, 52, 1, (150, 144, 170))
        # 网兜与报纸
        R(-48, 330, 40, 40, mul(back, 0.7))
        R(-40, 322, 22, 30, (226, 220, 204))
        R(-38, 326, 18, 2, (70, 66, 80))
        for y in range(331, 348, 3):
            R(-38, y, 16, 1, (150, 144, 140))
        for y in range(334, 370, 4):
            R(-48, y, 40, 1, (60, 30, 44))
        for x in range(-48, -8, 4):
            R(x, 334, 1, 36, (60, 30, 44))
        R(-49, 329, 42, 2, (110, 100, 110))
        # 扶手吊环
        for x in (-86, -70):
            R(x, 58, 1, 30, (190, 190, 206))
            g.ellipse(X(x + 4) if mirror else x - 4, 88, 9, 10, (200, 200, 216))
            g.ellipse(X(x + 2) if mirror else x - 2, 90, 5, 6, WALL)
    # 左：线路海报、灭火器
    poster(g, -110, 130, 44, 60, 'map')
    g.shadow(-101, 306, 16, 44, 0.6)
    g.rect(-100, 304, 12, 40, (200, 56, 60))
    g.rect(-100, 304, 3, 40, (255, 120, 110))
    g.rect(-91, 304, 3, 40, (120, 30, 40))
    g.rect(-98, 298, 8, 6, (60, 60, 80))
    g.rect(-96, 294, 10, 3, (40, 40, 60))
    g.rect(-98, 316, 8, 8, (240, 232, 226))
    g.rect(-102, 310, 16, 2, (84, 94, 130))
    g.rect(-102, 336, 16, 2, (84, 94, 130))
    # 右：衣钩上的外套与挎包
    g.rect(536, 148, 56, 3, BRASS)
    g.rect(536, 148, 56, 1, (255, 236, 170))
    for x in (544, 564, 584):
        g.rect(x, 151, 2, 5, BRASS)
        g.px(x - 1, 155, BRASS)
    g.shadow(538, 158, 34, 110, 0.6)
    coat = (190, 150, 84)
    g.poly([(548, 156), (562, 156), (572, 176), (574, 262), (538, 262), (538, 178)], coat)
    g.poly([(555, 156), (552, 200), (558, 262), (538, 262), (538, 178), (548, 156)], mul(coat, 0.8))
    g.line([(555, 160), (554, 262)], mul(coat, 0.56))
    g.rect(548, 154, 14, 4, mul(coat, 1.2))
    for y in (190, 210, 230):
        g.rect(557, y, 2, 2, (90, 60, 40))
    g.rect(540, 222, 12, 2, mul(coat, 0.6))
    g.rect(562, 222, 10, 2, mul(coat, 0.6))
    g.line([(585, 156), (580, 196)], (60, 44, 44))
    g.line([(585, 156), (592, 196)], (60, 44, 44))
    g.rrect(574, 196, 24, 22, 4, (96, 70, 110))
    g.rect(574, 200, 24, 2, (130, 100, 150))
    g.rect(584, 204, 4, 4, BRASS)


def build_room(seed=21):
    rnd = random.Random(seed)
    cv = Cv(W, H)
    g = Off(cv)
    shell(g, rnd)
    walls(g, rnd)
    rack(g, rnd)
    window(g, rnd)
    extensions(g, rnd)
    seat(g, rnd, False)
    seat(g, rnd, True)
    table(g, rnd)
    # 整体的光：顶灯洗墙、窗外的冷光
    g.light(-120, 40, 720, 50, (255, 214, 160), 0.26)
    g.light(150, 125, 180, 138, (120, 150, 255), 0.55)
    g.light(110, 300, 260, 80, (120, 150, 255), 0.22)
    # 灯带往下洗、桌面吃到的壁灯暖光、过道的地脚灯
    g.light(-120, 300, 720, 50, (95, 242, 230), 0.16)
    g.light(250, 318, 150, 70, (255, 180, 100), 0.26)
    g.light(-20, 380, 180, 90, (255, 120, 170), 0.14)
    g.light(330, 380, 180, 90, (255, 190, 120), 0.16)
    g.light(140, 430, 200, 60, (120, 150, 255), 0.18)

    amb = np.ones((H, W, 3), np.float32)
    yy = np.arange(H, dtype=np.float32).reshape(H, 1, 1)
    amb *= np.clip(1.05 - np.abs(yy - 250) / 760, 0.6, 1.05)
    xx = np.arange(W, dtype=np.float32).reshape(1, W, 1) - OX
    edge = np.clip(np.minimum(xx + 120, 600 - xx) / 150, 0, 1)
    amb *= 0.42 + 0.58 * edge**0.8
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
    # 延伸段的光也跟着边缘衰减
    fall = np.repeat(0.4 + 0.6 * edge[0, :, 0] ** 0.7, k).reshape(1, W * k, 1)
    a[..., :3] = (a[..., :3] * fall).astype(np.uint8)
    a[..., 3] = 255
    # 抠出窗洞：沿用原图的洞形，位置与 .win 对齐
    hole = np.asarray(Image.open('hole.png').convert('L'))[..., None]
    n = 1
    while n < k:
        hole = px.epx(hole, wrap=False)
        n *= 2
    a[:, OX * k : (OX + 480) * k, 3] = np.where(hole[..., 0] > 127, 0, 255)
    return Image.fromarray(a, 'RGBA')
