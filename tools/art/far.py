"""远景天际线、近景轨旁设施、天空。"""
import random

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from street import H
from parts import *
import px
from px import Cv, mix, mul, render, text_mask

W1 = 720


def _tower(cv, rnd, x, top, w, c, kind, lit_p, bottom=H):
    cv.rect(x, top, w, bottom - top, c)
    cv.rect(x, top, 1, bottom - top, mul(c, 1.25))
    cv.rect(x + w - 2, top, 2, bottom - top, mul(c, 0.78))
    if kind == 'step':
        s = max(3, w // 5)
        cv.rect(x + s, top - 10, w - 2 * s, 10, c)
        cv.rect(x + 2 * s, top - 18, max(2, w - 4 * s), 8, c)
        cv.rect(x + w // 2, top - 34, 1, 16, c)
        cv.lpx(x + w // 2, top - 35, RED, 1.0)
    elif kind == 'spire':
        cv.poly([(x, top), (x + w // 2, top - 22), (x + w - 1, top)], c)
        cv.rect(x + w // 2, top - 40, 1, 20, c)
        cv.lpx(x + w // 2, top - 41, RED, 1.0)
    elif kind == 'slant':
        cv.poly([(x, top), (x + w - 1, top - 14), (x + w - 1, top)], c)
    elif kind == 'crown':
        cv.rect(x - 2, top - 3, w + 4, 3, mul(c, 1.2))
        for xx in range(x + 2, x + w - 2, 6):
            cv.rect(xx, top - 9, 1, 6, c)
    # 窗：远景只画成小光点，成组出现
    cols = [(255, 196, 120), (255, 214, 160), (150, 220, 255), (255, 130, 200), (200, 170, 255)]
    gx = rnd.choice([3, 4, 5])
    gy = rnd.choice([4, 5, 6])
    for yy in range(top + 5, bottom - 4, gy):
        row_on = rnd.random() < 0.7
        for xx in range(x + 3, x + w - 3, gx):
            if row_on and rnd.random() < lit_p:
                cv.lpx(xx, yy, rnd.choice(cols), rnd.uniform(0.5, 0.9))


def build_c1(seed=5):
    rnd = random.Random(seed)
    # ---- 最远一层：被霓虹染成品红的巨楼剪影
    far = Cv(W1, H)
    x = -10
    while x < W1:
        w = rnd.randrange(26, 64)
        top = rnd.randrange(24, 150)
        _tower(far, rnd, x, top, w, (52, 32, 98), rnd.choice(['step', 'spire', 'slant', 'flat', 'crown', 'flat']), 0.07)
        x += w + rnd.randrange(-6, 14)
    # 两座通体发光的霓虹塔
    for tx, col in ((150, MAG), (520, (120, 110, 255))):
        tw = 30
        far.lrect(tx, 30, tw, H - 30, col, 0.34, body=mul(col, 0.6))
        for yy in range(34, H, 5):
            far.rect(tx, yy, tw, 1, mul(col, 0.34))
        for xx in range(tx + 5, tx + tw, 6):
            far.rect(xx, 30, 1, H - 30, mul(col, 0.34))
        far.poly([(tx, 30), (tx + tw // 2, 4), (tx + tw - 1, 30)], mul(col, 0.5))
        far.rect(tx + tw // 2, 0, 1, 6, mul(col, 0.6))
    # 吊桥
    bx0, bx1, by = 280, 470, 196
    for px_ in (bx0 + 30, bx1 - 30):
        far.rect(px_, by - 62, 4, 110, (56, 32, 104))
        far.rect(px_ - 2, by - 40, 8, 2, (56, 32, 104))
        far.lpx(px_ + 1, by - 64, RED, 1.0)
    far.rect(bx0, by, bx1 - bx0, 3, (56, 32, 104))
    for i in range(bx0, bx1):
        t = (i - (bx0 + 30)) / (bx1 - bx0 - 60)
        if 0 <= t <= 1:
            yy = by - 62 + int(58 * 4 * t * (1 - t))
            far.px(i, yy, (90, 56, 150))
            if i % 6 == 0:
                far.rect(i, yy, 1, by - yy, (72, 44, 128))
        elif t < 0:
            yy = by - 62 + int(62 * (-t) / 0.4)
            if yy < by:
                far.px(i, yy, (90, 56, 150))
        else:
            yy = by - 62 + int(62 * (t - 1) / 0.4)
            if yy < by:
                far.px(i, yy, (90, 56, 150))
    for i in range(bx0, bx1, 5):
        far.lpx(i, by - 1, (255, 190, 120), 0.8)
    fog = np.clip(np.linspace(0.0, 0.66, H) ** 1.5, 0, 1).astype(np.float32)
    im_far = render(far, ambient=(0.8, 0.78, 0.9), spill=(0.6, 4.0), spill2=(0.5, 14.0), bloom=(0.6, 1.4), haze=(0.5, 12.0), fog=((214, 70, 170), fog))

    # ---- 稍近一层：更暗、更大的楼，带窗格与全息广告
    mid = Cv(W1, H)
    x = -20
    while x < W1:
        w = rnd.randrange(44, 96)
        top = rnd.randrange(84, 190)
        c = rnd.choice([(44, 34, 92), (38, 40, 96), (52, 34, 86)])
        _tower(mid, rnd, x, top, w, c, rnd.choice(['step', 'flat', 'crown', 'slant', 'flat']), 0.16)
        r = rnd.random()
        if r < 0.45 and w > 50:
            # 楼身上的全息广告屏
            col = rnd.choice([MAG, CYA, VIO, ORG, GRN])
            bw, bh = rnd.randrange(22, 34), rnd.randrange(30, 54)
            bx, byy = x + rnd.randrange(4, w - bw - 4), top + rnd.randrange(8, 30)
            mid.lrect(bx, byy, bw, bh, col, 0.5, body=mul(col, 0.55))
            for yy in range(byy, byy + bh, 2):
                mid.lrect(bx, yy, bw, 1, col, 0.3, body=mul(col, 0.4))
            ch = rnd.choice(['夢', '光', '星', '酒', '楽', '海', '月', '電'])
            m = text_mask(ch)
            mid.lmask(bx + (bw - m.width) // 2, byy + 5, m, mix(col, (255, 255, 255), 0.6), 0.95)
            mid.lrect(bx + 3, byy + bh - 8, bw - 6, 1, mix(col, (255, 255, 255), 0.5), 0.9)
            mid.lrect(bx + 3, byy + bh - 5, bw - 12, 1, mix(col, (255, 255, 255), 0.5), 0.9)
        elif r < 0.7:
            col = rnd.choice(NEONS)
            for i in range(rnd.randrange(3, 6)):
                mid.lrect(x + w - 6, top + 10 + i * 9, 3, 6, col, 0.8)
        x += w + rnd.randrange(-4, 18)
    fog2 = np.clip(np.linspace(0.02, 0.5, H) ** 1.4, 0, 1).astype(np.float32)
    im_mid = render(mid, ambient=(1, 1, 1), spill=(0.8, 4.0), spill2=(0.6, 14.0), bloom=(0.6, 1.5), haze=(0.4, 10.0), fog=((150, 60, 170), fog2))
    out = Image.alpha_composite(im_far, im_mid)
    # 探照灯光柱
    a = np.asarray(out).astype(np.float32) / 255
    k = px.SCALE
    yy, xx = np.mgrid[0 : H * k, 0 : W1 * k] / k
    for bx, ang, col in ((90, -0.32, (0.5, 0.8, 1.0)), (360, 0.22, (1.0, 0.5, 0.9)), (610, -0.12, (0.6, 0.7, 1.0))):
        d = np.abs((xx - bx) - (190 - yy) * ang) / (1 + (190 - yy) * 0.035)
        beam = np.clip(1 - d / 3.0, 0, 1) * np.clip((190 - yy) / 150, 0, 1) * np.clip(yy / 60, 0, 1) * 0.16
        beam = np.where(yy < 190, beam, 0)
        a[..., :3] = np.clip(a[..., :3] + beam[..., None] * np.array(col, np.float32), 0, 1)
        a[..., 3] = np.maximum(a[..., 3], np.clip(beam * 2.5, 0, 1))
    return Image.fromarray((a * 255 + 0.5).astype(np.uint8), 'RGBA')


def build_c3(seed=9):
    """近景：接触网立柱、电线、信号灯、高架护栏。很暗，只在边缘吃一点城市的光。"""
    rnd = random.Random(seed)
    cv = Cv(W1, H)
    steel = (40, 42, 66)
    rim = (150, 110, 190)
    # 护栏
    py = H - 22
    cv.rect(0, py, W1, 22, (26, 26, 46))
    cv.rect(0, py, W1, 2, (70, 72, 104))
    cv.rect(0, py + 2, W1, 1, (16, 16, 30))
    for xx in range(0, W1, 24):
        cv.rect(xx, py + 3, 1, 19, (18, 18, 34))
        cv.rect(xx + 1, py + 3, 1, 19, (40, 40, 64))
    for xx in range(12, W1, 48):
        cv.lrect(xx, py + 6, 3, 1, (95, 242, 230), 0.9)
    cv.rect(0, py + 14, W1, 1, (48, 50, 78))
    # 立柱与悬臂
    for i, px_ in enumerate(range(60, W1, 240)):
        top = 40
        cv.rect(px_, top, 5, py - top, steel)
        cv.rect(px_, top, 1, py - top, rim)
        cv.rect(px_ + 4, top, 1, py - top, (20, 20, 36))
        for yy in range(top + 10, py, 14):
            cv.line([(px_ + 1, yy), (px_ + 3, yy + 7)], (24, 24, 42))
            cv.line([(px_ + 3, yy + 7), (px_ + 1, yy + 14)], (24, 24, 42))
        cv.rect(px_ - 3, py - 8, 11, 8, (30, 30, 52))
        cv.rect(px_ - 3, py - 8, 11, 1, (70, 72, 104))
        # 悬臂
        cv.rect(px_ - 34, top + 6, 74, 2, steel)
        cv.rect(px_ - 34, top + 6, 74, 1, mul(rim, 0.7))
        cv.line([(px_ + 2, top), (px_ - 30, top + 6)], steel)
        cv.line([(px_ + 2, top), (px_ + 36, top + 6)], steel)
        for ix in (px_ - 30, px_ - 14, px_ + 20, px_ + 34):
            cv.rect(ix, top + 8, 2, 5, (120, 124, 150))
            cv.rect(ix, top + 9, 2, 1, (60, 62, 90))
            cv.rect(ix, top + 11, 2, 1, (60, 62, 90))
        if i == 1:
            # 信号机
            cv.rect(px_ + 8, 150, 9, 22, (16, 16, 30))
            cv.rect(px_ + 5, 158, 3, 2, steel)
            cv.lellipse(px_ + 10, 153, 5, 5, (80, 255, 150), 1.0, body=(190, 255, 220))
            cv.ellipse(px_ + 10, 162, 5, 5, (70, 20, 26))
            cv.rect(px_ + 7, 148, 11, 2, (40, 42, 66))
        if i == 2:
            cv.rect(px_ - 12, 120, 9, 12, (20, 20, 36))
            cv.lrect(px_ - 10, 122, 5, 3, (255, 190, 90), 0.9)
            cv.rect(px_ - 3, 124, 3, 2, steel)
    # 电线：两根承力索 + 接触线，带吊弦
    for off, sag in ((53, 9), (58, 6)):
        pts = []
        for x in range(0, W1 + 1, 6):
            t = ((x - 60) % 240) / 240
            pts.append((x, int(round(off + sag * 4 * t * (1 - t)))))
        cv.line(pts, (14, 14, 28))
    cv.line([(0, 74), (W1, 74)], (14, 14, 28))
    for x in range(0, W1, 20):
        t = ((x - 60) % 240) / 240
        y0 = int(round(58 + 6 * 4 * t * (1 - t)))
        cv.rect(x, y0, 1, 74 - y0, (22, 22, 40))
    im = render(cv, ambient=(0.8, 0.8, 0.95), spill=(1.2, 3.0), spill2=(0.8, 10.0), bloom=(0.6, 1.4), haze=(0.35, 7.0))
    return im


def build_sky(seed=4):
    """夜空：分层的云带，底部被城市的霓虹染成紫红。"""
    w, h = 480 * px.SCALE, 270 * px.SCALE
    rs = np.random.RandomState(seed)

    def fbm(wx, hy):
        acc = np.zeros((h, w), np.float32)
        amp, tot = 1.0, 0.0
        for o in range(5):
            gw, gh = max(2, int(wx * 2**o)), max(2, int(hy * 2**o))
            g = rs.rand(gh, gw).astype(np.float32)
            acc += zoom(g, (h / gh, w / gw), order=3, mode='wrap')[:h, :w] * amp
            tot += amp
            amp *= 0.55
        return acc / tot

    n = fbm(3, 5)
    n2 = fbm(5, 9)
    yy = np.linspace(0, 1, h).reshape(h, 1)
    # 云量：中下部更多
    dens = n * 0.7 + n2 * 0.3 + (yy - 0.55) * 0.35
    ramp = [
        (0.00, (8, 7, 24)),
        (0.30, (14, 11, 40)),
        (0.55, (28, 18, 66)),
        (0.75, (56, 26, 96)),
        (0.90, (104, 40, 124)),
        (1.00, (150, 58, 140)),
    ]

    def grad(t):
        out = np.zeros(t.shape + (3,), np.float32)
        for (t0, c0), (t1, c1) in zip(ramp, ramp[1:]):
            m = (t >= t0) & (t <= t1)
            k = ((t - t0) / (t1 - t0))[m]
            out[m] = np.array(c0, np.float32) * (1 - k[:, None]) + np.array(c1, np.float32) * k[:, None]
        return out

    base = grad(np.clip(yy ** 1.15 + (n2 - 0.5) * 0.05, 0, 1) * np.ones((1, w), np.float32))
    # 云：三档明度，硬边
    cloud = np.zeros((h, w), np.float32)
    for th, v in ((0.50, 0.33), (0.56, 0.66), (0.62, 1.0)):
        cloud = np.where(dens > th, v, cloud)
    lit = grad(np.clip(yy * 0.9 + 0.22, 0, 1) * np.ones((1, w), np.float32))
    img = base * (1 - cloud[..., None] * 0.7) + lit * cloud[..., None] * 0.7
    # 云底的品红勾边：云的下缘更亮
    edge = np.clip(cloud - np.roll(cloud, -2 * px.SCALE, axis=0), 0, 1)
    img += edge[..., None] * np.array([70, 24, 60], np.float32) * yy[..., None]
    # 星
    for _ in range(90 * px.SCALE):
        sx, sy = rs.randint(0, w), int(rs.rand() ** 1.8 * h * 0.6)
        if cloud[sy, sx] < 0.3:
            b = rs.choice([110, 150, 200, 255])
            img[sy, sx] = np.array([b, b, min(255, b + 30)], np.float32) * 0.9
    out = np.clip(img, 0, 255).astype(np.uint8)
    im = Image.fromarray(out, 'RGB')
    return im.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
