"""Street-scene parts: wall materials, windows, signs, lanterns, air-conditioning
units and so on. All coordinates are in art pixels.
"""
from PIL import Image

from px import C, F8, F8B, F16, Cv, bitmap_mask, mix, mul, text_mask

# Neon palette
MAG = (255, 64, 178)
CYA = (64, 226, 255)
YEL = (255, 206, 84)
GRN = (96, 255, 150)
RED = (255, 72, 60)
ORG = (255, 142, 56)
VIO = (176, 112, 255)
WHT = (232, 238, 255)
PNK = (255, 130, 200)
NEONS = [MAG, CYA, YEL, GRN, RED, ORG, VIO, PNK]

IRON = (44, 46, 64)
WARM = (255, 206, 128)


# ------------------------------------------------------------------ Walls
def brick(cv, x, y, w, h, base, rnd, var=0.22):
    cv.rect(x, y, w, h, mul(base, 0.7))
    for r, by in enumerate(range(y, y + h, 3)):
        off = 0 if r % 2 == 0 else 3
        for bx in range(x - off, x + w, 6):
            col = mul(base, 1 + (rnd.random() - 0.5) * var)
            x0, x1 = max(bx, x), min(bx + 5, x + w)
            if x1 > x0:
                cv.rect(x0, by, x1 - x0, min(2, y + h - by), col)


def plaster(cv, x, y, w, h, base, rnd, stains=True):
    cv.rect(x, y, w, h, base)
    cv.speckle(x, y, w, h, 0.10, rnd, 0.25)
    if stains:
        for _ in range(max(1, w // 14)):
            sx = x + rnd.randrange(w)
            sy = y + rnd.randrange(max(1, h - 10))
            ln = rnd.randrange(8, 30)
            for i in range(ln):
                if sy + i < y + h:
                    shade(cv, sx, sy + i, rnd.choice([1, 1, 2]), 1, 0.86 + 0.12 * i / ln)
        # flaking render
        for _ in range(w // 30):
            px_, py_ = x + rnd.randrange(w), y + rnd.randrange(h)
            for _ in range(rnd.randrange(3, 9)):
                cv.rect(
                    min(x + w - 2, max(x, px_ + rnd.randrange(-3, 4))),
                    min(y + h - 1, max(y, py_ + rnd.randrange(-2, 3))),
                    2,
                    1,
                    mul(base, 0.8),
                )


def tiles(cv, x, y, w, h, base, rnd):
    cv.rect(x, y, w, h, mul(base, 0.74))
    for by in range(y, y + h, 4):
        for bx in range(x, x + w, 4):
            cv.rect(bx, by, min(3, x + w - bx), min(3, y + h - by), mul(base, 1 + (rnd.random() - 0.5) * 0.16))


def metal(cv, x, y, w, h, base, rnd):
    cv.rect(x, y, w, h, base)
    for bx in range(x, x + w, 3):
        cv.rect(bx, y, 1, h, mul(base, 0.8))
    for by in range(y + 9, y + h, 14):
        cv.rect(x, by, w, 1, mul(base, 0.66))
        for bx in range(x + 2, x + w, 9):
            cv.px(bx, by - 1, mul(base, 1.25))
    cv.speckle(x, y, w, h, 0.12, rnd, 0.15)


def shade(cv, x, y, w, h, k):
    box = (max(0, x), max(0, y), min(cv.w, x + w), min(cv.h, y + h))
    if box[2] <= box[0] or box[3] <= box[1]:
        return
    if isinstance(k, (int, float)):
        k = (k, k, k)
    reg = cv.im.crop(box)
    r, g, b, a = reg.split()
    r = r.point(lambda v: min(255, int(v * k[0])))
    g = g.point(lambda v: min(255, int(v * k[1])))
    b = b.point(lambda v: min(255, int(v * k[2])))
    cv.im.paste(Image.merge('RGBA', (r, g, b, a)), box)


# ------------------------------------------------------------------ Windows
LIT = [
    (255, 214, 132),
    (255, 196, 112),
    (255, 176, 96),
    (255, 222, 160),
    (204, 232, 255),
    (255, 140, 180),
    (140, 255, 214),
    (255, 120, 80),
]


def window(cv, rnd, x, y, w, h, frame, lit=None, arch=False, shutters=None, wall=None, sill=None):
    """x, y is the top-left of the glass. Pass a colour as lit for a lit window,
    anything falsy for a dark one."""
    cv.rect(x - 1, y - 1, w + 2, h + 2, frame)
    if lit:
        top = mix(lit, (255, 255, 255), 0.25)
        cv.lrect(x, y, w, h, lit, 0.62)
        cv.lrect(x, y, w, h // 3, top, 0.7)
        r = rnd.random()
        if r < 0.3:  # curtains
            cw = rnd.randrange(2, max(3, w // 2))
            side = rnd.choice([0, 1])
            cx = x if side == 0 else x + w - cw
            cv.lrect(cx, y, cw, h, mul(lit, 0.62), 0.3)
            for yy in range(y, y + h, 3):
                cv.lrect(cx + (cw - 1 if side == 0 else 0), yy, 1, 2, mul(lit, 0.5), 0.22)
        elif r < 0.45:  # blinds
            for yy in range(y + 1, y + h, 2):
                cv.lrect(x, yy, w, 1, mul(lit, 0.6), 0.3)
        elif r < 0.6:  # a silhouette
            px_ = x + rnd.randrange(1, max(2, w - 5))
            cv.rect(px_ + 1, y + h - 8, 3, 3, (30, 22, 40))
            cv.rect(px_, y + h - 5, 5, 5, (30, 22, 40))
        elif r < 0.75:  # a potted plant
            px_ = x + rnd.randrange(1, max(2, w - 4))
            cv.rect(px_, y + h - 2, 4, 2, (60, 36, 40))
            cv.rect(px_ + 1, y + h - 5, 2, 3, (30, 70, 50))
            cv.px(px_, y + h - 4, (30, 70, 50))
            cv.px(px_ + 3, y + h - 6, (30, 70, 50))
    else:
        cv.rect(x, y, w, h, (20, 24, 50))
        cv.rect(x, y, w, 2, (14, 16, 36))
        # reflection on the glass
        for i in range(min(w, h) - 2):
            if i % 2 == 0:
                cv.px(x + 1 + i, y + h - 2 - i, (46, 58, 108))
        if rnd.random() < 0.18:  # the cold flicker of a television
            cv.lrect(x + 1, y + h - 5, w - 2, 4, (90, 130, 255), 0.3, body=(50, 70, 150))
    # window bars
    cv.rect(x + w // 2, y, 1, h, mul(frame, 0.8))
    cv.rect(x, y + h // 3, w, 1, mul(frame, 0.8))
    if arch and wall:
        cv.px(x - 1, y - 1, wall)
        cv.px(x + w, y - 1, wall)
        cv.px(x, y, frame)
        cv.px(x + w - 1, y, frame)
        cv.rect(x, y - 2, w, 1, mul(frame, 1.5))
    if shutters:
        for sx in (x - 4, x + w + 1):
            cv.rect(sx, y - 1, 3, h + 2, shutters)
            for yy in range(y, y + h, 2):
                cv.rect(sx, yy, 3, 1, mul(shutters, 0.72))
    s = sill or mul(frame, 1.2)
    cv.rect(x - 2, y + h + 1, w + 4, 2, s)
    cv.rect(x - 2, y + h + 2, w + 4, 1, mul(s, 0.7))


def ac_unit(cv, x, y):
    cv.rect(x, y, 11, 8, (146, 152, 168))
    cv.rect(x, y, 11, 1, (196, 202, 214))
    cv.rect(x, y + 7, 11, 1, (92, 96, 114))
    cv.ellipse(x + 1, y + 1, 6, 6, (52, 56, 78))
    cv.px(x + 3, y + 3, (120, 126, 146))
    cv.px(x + 4, y + 4, (120, 126, 146))
    cv.rect(x + 8, y + 2, 2, 1, (92, 96, 114))
    cv.rect(x + 8, y + 4, 2, 1, (92, 96, 114))
    cv.rect(x + 1, y + 8, 1, 2, IRON)
    cv.rect(x + 9, y + 8, 1, 2, IRON)
    cv.rect(x + 5, y + 8, 1, 5, mul((146, 152, 168), 0.6))  # condensate pipe


def pipe(cv, x, y0, y1, c=(84, 96, 112), w=2):
    cv.rect(x, y0, w, y1 - y0, c)
    cv.rect(x, y0, 1, y1 - y0, mul(c, 1.3))
    for yy in range(y0 + 5, y1, 16):
        cv.rect(x - 1, yy, w + 2, 2, mul(c, 0.6))


def balcony(cv, rnd, x, y, w, trim):
    """y is the top edge of the balcony floor."""
    cv.rect(x - 1, y, w + 2, 2, trim)
    cv.rect(x - 1, y + 2, w + 2, 1, mul(trim, 0.6))
    cv.rect(x, y - 9, w, 1, IRON)
    for xx in range(x, x + w, 2):
        cv.rect(xx, y - 8, 1, 8, IRON)
    cv.rect(x, y - 5, w, 1, mul(IRON, 0.8))
    # plants and laundry hung out to dry
    for _ in range(rnd.randrange(0, 3)):
        px_ = x + rnd.randrange(1, max(2, w - 5))
        g = rnd.choice([(40, 96, 66), (56, 112, 60), (36, 84, 84)])
        cv.rect(px_, y - 12, 4, 3, g)
        cv.rect(px_ + 1, y - 14, 2, 2, mul(g, 1.25))
        cv.px(px_ - 1, y - 11, g)
        cv.px(px_ + 4, y - 12, mul(g, 0.8))
    if rnd.random() < 0.4:
        for i in range(rnd.randrange(1, 4)):
            c = rnd.choice([(190, 190, 204), (150, 88, 96), (96, 120, 160), (190, 160, 96)])
            cv.rect(x + 2 + i * 5, y - 8, 4, rnd.randrange(4, 7), c)


# ------------------------------------------------------------------ Signs
def vsign(cv, x, y, chars, col, border=True, board=(22, 18, 40), side='r'):
    """Vertical sign; x, y is the top-left corner. Returns (w, h)."""
    n = len(chars)
    w, h = 20, n * 17 + 5
    # bracket
    bx = x + w if side == 'l' else x - 3
    cv.rect(bx, y + 3, 3, 1, IRON)
    cv.rect(bx, y + h - 5, 3, 1, IRON)
    cv.rect(x, y, w, h, board)
    cv.rect(x, y, w, 1, mul(board, 1.6))
    if border:
        dim = mul(col, 0.45)
        cv.lline([(x + 1, y + 1), (x + w - 2, y + 1), (x + w - 2, y + h - 2), (x + 1, y + h - 2), (x + 1, y + 1)], col, 0.8, body=mix(col, (255, 255, 255), 0.3))
        cv.px(x + 1, y + 1, dim)
        cv.px(x + w - 2, y + 1, dim)
        cv.px(x + 1, y + h - 2, dim)
        cv.px(x + w - 2, y + h - 2, dim)
    for i, ch in enumerate(chars):
        m = text_mask(ch)
        cv.lmask(x + (w - m.width) // 2, y + 3 + i * 17 + (16 - m.height) // 2, m, col)
    return w, h


def lightbox_v(cv, x, y, chars, bg=(255, 232, 190), fg=(120, 20, 30), k=0.8):
    n = len(chars)
    w, h = 18, n * 16 + 4
    cv.rect(x - 1, y - 1, w + 2, h + 2, (40, 36, 52))
    cv.lrect(x, y, w, h, bg, k)
    for i, ch in enumerate(chars):
        m = text_mask(ch)
        cv.im.paste(tuple(fg) + (255,), (x + (w - m.width) // 2, y + 2 + i * 16 + (16 - m.height) // 2), m)
        cv.em.paste(mul(fg, 0.25), (x + (w - m.width) // 2, y + 2 + i * 16 + (16 - m.height) // 2), m)
    return w, h


def hsign(cv, x, y, text, col, font=F16, pad=3, board=(22, 18, 40), border=True, w=None):
    m = text_mask(text, font)
    bw = w or (m.width + pad * 2 + 2)
    bh = m.height + pad * 2
    cv.rect(x, y, bw, bh, board)
    cv.rect(x, y, bw, 1, mul(board, 1.6))
    if border:
        cv.lline([(x + 1, y + 1), (x + bw - 2, y + 1), (x + bw - 2, y + bh - 2), (x + 1, y + bh - 2), (x + 1, y + 1)], col, 0.7, body=mix(col, (255, 255, 255), 0.3))
    cv.lmask(x + (bw - m.width) // 2, y + pad, m, col)
    return bw, bh


def lightbox_h(cv, x, y, text, bg=(255, 232, 190), fg=(120, 20, 30), font=F16, pad=2, k=0.8, w=None):
    m = text_mask(text, font)
    bw = w or (m.width + pad * 2 + 4)
    bh = m.height + pad * 2
    cv.rect(x - 1, y - 1, bw + 2, bh + 2, (40, 36, 52))
    cv.lrect(x, y, bw, bh, bg, k)
    pos = (x + (bw - m.width) // 2, y + pad)
    cv.im.paste(tuple(fg) + (255,), pos, m)
    cv.em.paste(mul(fg, 0.25), pos, m)
    return bw, bh


def neon_text(cv, x, y, text, col, font=F8B):
    m = text_mask(text, font)
    cv.lmask(x, y, m, col)
    return m.width, m.height


ICONS = {
    'bowl': [
        '  # #  #   ',
        ' #  # #    ',
        '  # #  #   ',
        '           ',
        '###########',
        '#         #',
        ' #       # ',
        '  #######  ',
        '   #   #   ',
    ],
    'glass': [
        '#########',
        ' #     # ',
        '  #   #  ',
        '   # #   ',
        '    #    ',
        '    #    ',
        '    #    ',
        '  #####  ',
    ],
    'arrow': [
        '    #    ',
        '    #    ',
        '    #    ',
        '#   #   #',
        ' #  #  # ',
        '  # # #  ',
        '   ###   ',
        '    #    ',
    ],
    'moon': [
        '  ####   ',
        ' ##      ',
        '##       ',
        '##       ',
        '##       ',
        '###     #',
        ' ####### ',
        '  #####  ',
    ],
    'star': [
        '    #    ',
        '   ###   ',
        '#########',
        ' ####### ',
        '  #####  ',
        ' ### ### ',
        ' #     # ',
    ],
    'cup': [
        '  #  #   ',
        '   #  #  ',
        '  #  #   ',
        '         ',
        '####### ',
        '#     ###',
        '#     # #',
        '#     ###',
        ' ##### ',
    ],
    'fish': [
        '   ####    #',
        ' ##    ## ##',
        '#  #     # #',
        ' ##    ## ##',
        '   ####    #',
    ],
    'heart': [
        ' ##   ## ',
        '#  # #  #',
        '#   #   #',
        ' #     # ',
        '  #   #  ',
        '   # #   ',
        '    #    ',
    ],
}


def icon(cv, x, y, name, col, scale=1):
    m = bitmap_mask(ICONS[name])
    if scale != 1:
        m = m.resize((m.width * scale, m.height * scale), Image.NEAREST)
    cv.lmask(x, y, m, col)
    return m.width, m.height


def lantern(cv, x, y, c=(255, 76, 52)):
    cv.rect(x + 3, y - 3, 1, 3, (30, 26, 40))
    cv.rect(x + 2, y, 3, 1, (214, 172, 84))
    cv.lellipse(x, y + 1, 7, 9, c, 0.9, body=mix(c, (255, 226, 150), 0.3))
    cv.lrect(x + 3, y + 2, 1, 7, (255, 214, 130), 0.95)
    cv.lrect(x + 1, y + 4, 5, 1, mix(c, (255, 230, 160), 0.55), 0.9)
    cv.rect(x + 2, y + 10, 3, 1, (214, 172, 84))
    cv.rect(x + 3, y + 11, 1, 2, (220, 64, 50))


def vending(cv, rnd, x, y, tint=(210, 234, 255)):
    """12x18, with y as the bottom edge."""
    y0 = y - 18
    cv.rect(x, y0, 12, 18, (60, 66, 88))
    cv.lrect(x + 1, y0 + 1, 10, 11, tint, 0.85)
    for r in range(3):
        for c in range(4):
            cv.lrect(x + 2 + c * 2, y0 + 2 + r * 3, 1, 2, rnd.choice([RED, ORG, GRN, CYA, YEL, MAG]), 0.6)
    cv.lrect(x + 1, y0 + 13, 7, 2, rnd.choice([RED, CYA, GRN]), 0.5)
    cv.rect(x + 9, y0 + 13, 2, 3, (26, 26, 40))
    cv.rect(x, y0 + 17, 12, 1, (30, 32, 48))


def awning(cv, x, y, w, c1, c2, h=6):
    for i in range(w):
        c = c1 if (i // 4) % 2 == 0 else c2
        hh = h + (1 if (i % 4) in (1, 2) else 0)
        cv.rect(x + i, y, 1, hh, c)
    cv.rect(x, y, w, 1, mul(c1, 1.25))
    shade(cv, x, y + h - 1, w, 2, 0.8)


def street_lamp(cv, x, y, h=58, c=(255, 196, 110)):
    """y is the ground line."""
    cv.rect(x, y - h, 2, h, (40, 44, 62))
    cv.rect(x, y - h, 1, h, (64, 70, 92))
    cv.rect(x - 1, y - 4, 4, 4, (34, 36, 52))
    cv.rect(x, y - h, 9, 1, (40, 44, 62))
    cv.rect(x + 6, y - h + 1, 5, 2, (52, 56, 76))
    cv.lrect(x + 7, y - h + 3, 3, 1, c, 1.0, body=(255, 240, 210))
    cv.light(x - 4, y - h + 6, 26, 18, c, 0.8)
    cv.light(x - 8, y - 6, 34, 10, c, 0.55)


def person(cv, rnd, x, y, umbrella=True):
    """Silhouette of a passer-by; y is the sole of the foot."""
    coat = rnd.choice([(40, 44, 70), (70, 44, 52), (44, 64, 66), (84, 70, 50)])
    cv.rect(x + 1, y - 13, 3, 3, (196, 150, 130))
    cv.rect(x, y - 10, 5, 6, coat)
    cv.rect(x + 1, y - 4, 1, 4, mul(coat, 0.6))
    cv.rect(x + 3, y - 4, 1, 4, mul(coat, 0.6))
    if umbrella:
        uc = rnd.choice([(190, 60, 80), (60, 120, 170), (200, 180, 90), (40, 40, 60), (150, 90, 170)])
        cv.rect(x - 3, y - 18, 11, 1, mul(uc, 0.8))
        cv.rect(x - 2, y - 19, 9, 1, uc)
        cv.rect(x, y - 20, 5, 1, mul(uc, 1.2))
        cv.rect(x + 5, y - 17, 1, 7, (30, 30, 44))
