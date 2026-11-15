"""像素画工具：一张「固有色」画布 + 一张「自发光」画布，最后统一打光、加辉光。"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
F16 = ImageFont.truetype(os.path.join(HERE, 'fonts/dot16.ttf'), 16)
F8 = ImageFont.truetype(os.path.join(HERE, 'fonts/silk.ttf'), 8)
F8B = ImageFont.truetype(os.path.join(HERE, 'fonts/silkb.ttf'), 8)


def C(h):
    h = h.lstrip('#')
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def mul(c, k):
    if isinstance(k, (int, float)):
        k = (k, k, k)
    return tuple(max(0, min(255, int(round(c[i] * k[i])))) for i in range(3))


def text_mask(s, font=F16):
    """无抗锯齿的文字蒙版（L 模式，已裁到字形边界）"""
    w = int(font.getlength(s)) + 4
    im = Image.new('L', (w, 24), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((1, 2), s, font=font, fill=255)
    bb = im.getbbox()
    return im.crop(bb) if bb else Image.new('L', (1, 1), 0)


def bitmap_mask(rows):
    """字符串点阵 -> 蒙版，'#' 为实心"""
    h = len(rows)
    w = max(len(r) for r in rows)
    im = Image.new('L', (w, h), 0)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ' ' and ch != '.':
                im.putpixel((x, y), 255)
    return im


class Cv:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.em = Image.new('RGB', (w, h), (0, 0, 0))
        self.lt = Image.new('RGB', (w, h), (0, 0, 0))  # 只照亮周围、自身不可见的光
        self.fi = None  # 精细层：直接在输出分辨率上画，不经过 EPX
        self.sh = Image.new('L', (w, h), 255)  # 软阴影（接触阴影、遮蔽），渲染时模糊后乘到光照上
        self.s = ImageDraw.Draw(self.sh)
        self.d = ImageDraw.Draw(self.im)
        self.e = ImageDraw.Draw(self.em)
        self.l = ImageDraw.Draw(self.lt)

    def fline(self, pts, c, k=0.0, width=1, body=None):
        """在输出分辨率上画一条细线。坐标仍用画素（可以是小数），粗细也按画素算。

        近水平的细线（屏幕上的代码行、票面的横线）要走这里：它们本该是直的，
        只因透视而缓慢下沉，在 1 倍上就成了每十几格跳一格的台阶。
        EPX 会把这种台阶放大成一道斜坡，看起来像线被掰弯了；
        直接在输出分辨率上画，台阶只有半个画素高，才是平滑的下沉。
        """
        s = SCALE
        if self.fi is None:
            self.fi = Image.new('RGBA', (self.w * s, self.h * s), (0, 0, 0, 0))
            self.fem = Image.new('RGB', (self.w * s, self.h * s), (0, 0, 0))
            self.fd = ImageDraw.Draw(self.fi)
            self.fe = ImageDraw.Draw(self.fem)
        # 画素 (x, y) 占据输出像素 [x*s, x*s+s)，取其中心
        off = (s - 1) / 2
        p = [(x * s + off, y * s + off) for x, y in pts]
        w = max(1, round(width * s))
        self.fd.line(p, fill=tuple(body or c) + (255,), width=w)
        if k:
            self.fe.line(p, fill=mul(c, k), width=w)

    def shadow(self, x, y, w, h, k=0.5, ell=False):
        """压一块软阴影，k 越小越黑。之后画上去的实体不受它影响。"""
        box = [x, y, x + w - 1, y + h - 1]
        (self.s.ellipse if ell else self.s.rectangle)(box, fill=int(255 * k))

    def rrect(self, x, y, w, h, r, c):
        box = [x, y, x + w - 1, y + h - 1]
        self.d.rounded_rectangle(box, r, fill=tuple(c) + (255,))
        self.e.rounded_rectangle(box, r, fill=(0, 0, 0))
        self.s.rounded_rectangle(box, r, fill=255)

    def light(self, x, y, w, h, c, k=1.0):
        """一团看不见的光：只参与打光，不画出来（灯下的光池、屋里的灯光）"""
        self.l.ellipse([x, y, x + w - 1, y + h - 1], fill=mul(c, k))

    # ---- 不发光的实体：同时把自发光层对应位置擦黑（遮挡） ----
    def rect(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        box = [x, y, x + w - 1, y + h - 1]
        self.d.rectangle(box, fill=tuple(c) + (255,))
        self.e.rectangle(box, fill=(0, 0, 0))
        self.s.rectangle(box, fill=255)

    def px(self, x, y, c):
        self.rect(x, y, 1, 1, c)

    def line(self, pts, c, width=1):
        self.d.line(pts, fill=tuple(c) + (255,), width=width)
        self.e.line(pts, fill=(0, 0, 0), width=width)

    def poly(self, pts, c):
        self.d.polygon(pts, fill=tuple(c) + (255,))
        self.e.polygon(pts, fill=(0, 0, 0))
        self.s.polygon(pts, fill=255)

    def ellipse(self, x, y, w, h, c):
        box = [x, y, x + w - 1, y + h - 1]
        self.d.ellipse(box, fill=tuple(c) + (255,))
        self.e.ellipse(box, fill=(0, 0, 0))
        self.s.ellipse(box, fill=255)

    def mask(self, x, y, m, c):
        self.im.paste(tuple(c) + (255,), (x, y), m)
        self.em.paste((0, 0, 0), (x, y), m)

    # ---- 发光体：固有色画亮色，自发光层画光色 ----
    def lrect(self, x, y, w, h, c, k=1.0, body=None):
        if w <= 0 or h <= 0:
            return
        box = [x, y, x + w - 1, y + h - 1]
        self.d.rectangle(box, fill=tuple(body or c) + (255,))
        self.e.rectangle(box, fill=mul(c, k))

    def lpx(self, x, y, c, k=1.0):
        self.lrect(x, y, 1, 1, c, k)

    def lline(self, pts, c, k=1.0, width=1, body=None):
        self.d.line(pts, fill=tuple(body or c) + (255,), width=width)
        self.e.line(pts, fill=mul(c, k), width=width)

    def lellipse(self, x, y, w, h, c, k=1.0, body=None):
        box = [x, y, x + w - 1, y + h - 1]
        self.d.ellipse(box, fill=tuple(body or c) + (255,))
        self.e.ellipse(box, fill=mul(c, k))

    def lmask(self, x, y, m, c, k=1.0, body=None):
        self.im.paste(tuple(body or mix(c, (255, 255, 255), 0.45)) + (255,), (x, y), m)
        self.em.paste(mul(c, k), (x, y), m)

    def paste(self, other, x, y):
        self.im.alpha_composite(other.im, (x, y))
        a = other.im.split()[3]
        self.em.paste(other.em, (x, y), a)
        self.lt.paste(ImageChops.lighter(self.lt.crop((x, y, x + other.w, y + other.h)), other.lt), (x, y))

    # ---- 纹理 ----
    def speckle(self, x, y, w, h, amount, rnd, density=0.12):
        """在已有颜色上加明暗噪点"""
        px = self.im.load()
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                if rnd.random() < density:
                    r, g, b, a = px[xx, yy]
                    if a:
                        k = 1 + (rnd.random() * 2 - 1) * amount
                        px[xx, yy] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), a)


# 输出倍率：素材按 1 倍的像素坐标来画，渲染时放大到 SCALE 倍再打光（见 render）
SCALE = 1


def _shift(a, dy, dx, wrap):
    """取每个像素在 (dy, dx) 方向上的邻居；竖直方向边缘重复，水平方向可首尾相接"""
    if dy:
        a = np.roll(a, -dy, axis=0)
        if dy > 0:
            a[-1] = a[-2]
        else:
            a[0] = a[1]
    if dx:
        a = np.roll(a, -dx, axis=1)
        if not wrap:
            if dx > 0:
                a[:, -1] = a[:, -2]
            else:
                a[:, 0] = a[:, 1]
    return a


def epx(arr, wrap=True):
    """EPX / Scale2x：把像素画放大一倍，同时把斜线和弧线上的阶梯削成半格。
    只在邻居颜色完全相同时才连线，所以大色块和直边保持原样。"""
    key = (arr.astype(np.uint64) * np.array([1, 257, 65537, 16777259, 4294967311, 1099511628211, 281474976710677][: arr.shape[2]], np.uint64)).sum(axis=2)
    A, B, C, D = (_shift(key.copy(), *d, wrap) for d in ((-1, 0), (0, 1), (0, -1), (1, 0)))
    aA, aB, aC, aD = (_shift(arr.copy(), *d, wrap) for d in ((-1, 0), (0, 1), (0, -1), (1, 0)))
    out = np.repeat(np.repeat(arr, 2, axis=0), 2, axis=1)
    for (oy, ox), cond, src in (
        ((0, 0), (C == A) & (C != D) & (A != B), aA),
        ((0, 1), (A == B) & (A != C) & (B != D), aB),
        ((1, 0), (D == C) & (D != B) & (C != A), aC),
        ((1, 1), (B == D) & (B != A) & (D != C), aD),
    ):
        view = out[oy::2, ox::2]
        view[cond] = src[cond]
    return out


def wrap_blur(arr, sigma, wrap=True):
    mode = ('nearest', 'wrap' if wrap else 'nearest', 'nearest')
    return gaussian_filter(arr, sigma=(sigma, sigma, 0), mode=mode)


def render(
    cv,
    shadow_blur=2.2,
    ambient=(0.24, 0.25, 0.44),
    amb_grad=None,
    spill=(2.4, 6.0),
    spill2=(1.6, 16.0),
    core=1.0,
    bloom=(0.45, 1.6),
    haze=(0.22, 9.0),
    fog=None,
    wrap=True,
    alpha_glow=1.6,
    scale=None,
):
    """打光并合成。
    最终色 = 固有色 × (环境光 + 自发光模糊后的「溢光」) + 自发光 + 辉光
    fog: (color, strength 0..1, 或随高度变化的数组) 大气雾，用于中远景
    """
    k = SCALE if scale is None else scale
    alb8, em8 = np.asarray(cv.im), np.asarray(cv.em)
    lt_im, sh_im = cv.lt, cv.sh
    w, h = cv.w, cv.h
    n = 1
    while n < k:
        # 固有色与自发光一起判定，轮廓才不会错开
        both = epx(np.ascontiguousarray(np.concatenate([alb8, em8], axis=2)), wrap)
        alb8, em8 = both[..., :4], both[..., 4:]
        n *= 2
    if k > 1:
        w, h = w * k, h * k
        lt_im = lt_im.resize((w, h), Image.BILINEAR)
        sh_im = sh_im.resize((w, h), Image.BILINEAR)
        spill, spill2 = (spill[0], spill[1] * k), (spill2[0], spill2[1] * k)
        bloom, haze = (bloom[0], bloom[1] * k), (haze[0], haze[1] * k)
        shadow_blur *= k
    if cv.fi is not None and k == SCALE:
        base = Image.fromarray(alb8, 'RGBA')
        base.alpha_composite(cv.fi)
        alb8 = np.asarray(base)
        be = Image.fromarray(em8, 'RGB')
        be.paste(cv.fem, (0, 0), cv.fi.split()[3])
        em8 = np.asarray(be)
    alb = alb8.astype(np.float32) / 255
    em = em8.astype(np.float32) / 255
    rgb, a = alb[..., :3], alb[..., 3:4]

    def up(v):
        """按行/按像素给出的 1 倍参数，放大到输出尺寸"""
        v = np.asarray(v, np.float32)
        if v.ndim == 1:
            return np.repeat(v, k).reshape(h, 1, 1)
        return np.repeat(np.repeat(v.reshape(cv.h, cv.w, -1), k, axis=0), k, axis=1)

    amb = np.ones((h, 1, 3), np.float32) * np.array(ambient, np.float32)
    if amb_grad is not None:
        amb = amb * up(amb_grad)

    src = em + np.asarray(lt_im).astype(np.float32) / 255
    light = amb + wrap_blur(src, spill[1], wrap) * spill[0] + wrap_blur(src, spill2[1], wrap) * spill2[0]
    shd = np.asarray(sh_im).astype(np.float32) / 255
    if shd.min() < 1:
        light = light * gaussian_filter(shd, shadow_blur)[..., None]
    # 发光体自身不再吃反射光，否则大面积亮窗会糊成一片白
    emax = em.max(axis=2, keepdims=True)
    out = rgb * light * (1 - np.clip(emax * 1.4, 0, 1))
    glow = wrap_blur(em, bloom[1], wrap) * bloom[0] + wrap_blur(em, haze[1], wrap) * haze[0]
    out = out + em * core + glow * (1 - 0.6 * emax)
    # 高光软压缩：保留亮部层次
    knee = 0.72
    over = np.maximum(out - knee, 0)
    out = np.where(out > knee, knee + (1 - knee) * (1 - np.exp(-over / (1 - knee) * 0.9)), out)

    if fog is not None:
        fc, fs = fog
        fs = up(fs)
        out = out * (1 - fs) + np.array(fc, np.float32) / 255 * fs

    # 透明区域里的辉光：用辉光亮度当 alpha
    glum = glow.max(axis=2, keepdims=True)
    ga = np.clip(glum * alpha_glow, 0, 1)
    gcol = np.where(glum > 1e-4, glow / np.maximum(glum, 1e-4), 0)
    out_a = np.maximum(a, ga * (1 - a))
    out = np.where(a > 0.5, out, gcol)
    res = np.concatenate([np.clip(out, 0, 1), np.clip(out_a, 0, 1)], axis=2)
    return Image.fromarray((res * 255 + 0.5).astype(np.uint8), 'RGBA')


def quantize(im, colors=255):
    """压成调色板 PNG，体积小，也让辉光呈现像素画式的色阶"""
    return im.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)


def preview(im, path, scale=2, bg=(18, 14, 44)):
    b = Image.new('RGBA', im.size, tuple(bg) + (255,))
    b.alpha_composite(im.convert('RGBA'))
    b.resize((im.width * scale, im.height * scale), Image.NEAREST).convert('RGB').save(path)
