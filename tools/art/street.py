"""霓虹街区：密集招牌、砖墙骑楼、暖光店面。"""
import random

from PIL import Image

from parts import *
from px import C, F8, F8B, F16, Cv, bitmap_mask, mix, mul, text_mask

H = 320
GY = 274  # 人行道顶边
SH = 38  # 店面层高
FH = 28  # 楼层高

STYLES = {
    'brick_red': dict(tex=brick, base=(156, 82, 68), trim=(196, 164, 134), frame=(64, 42, 46), arch=True),
    'brick_dark': dict(tex=brick, base=(108, 74, 100), trim=(156, 134, 158), frame=(42, 34, 56), arch=True),
    'brick_brown': dict(tex=brick, base=(132, 96, 72), trim=(186, 160, 120), frame=(58, 44, 40), arch=False),
    'teal': dict(tex=plaster, base=(72, 122, 122), trim=(134, 176, 164), frame=(38, 60, 66), shutters=(36, 88, 84)),
    'blue': dict(tex=plaster, base=(86, 98, 152), trim=(152, 162, 204), frame=(44, 48, 86)),
    'ochre': dict(tex=plaster, base=(178, 142, 90), trim=(214, 190, 144), frame=(92, 62, 46), shutters=(56, 104, 84)),
    'rose': dict(tex=plaster, base=(152, 98, 114), trim=(204, 160, 168), frame=(70, 44, 60)),
    'tile': dict(tex=tiles, base=(72, 120, 98), trim=(156, 186, 156), frame=(40, 64, 56)),
    'metal': dict(tex=metal, base=(98, 102, 124), trim=(150, 154, 176), frame=(48, 50, 68)),
}

V_SIGNS = ['珈琲', '麺処', '酒場', '旅館', '雀荘', '質屋', '薬局', '銭湯', '書店', '電脳', '夜食', '茶房', '写真館', '理髪', '古本', '時計', '餃子', '焼鳥', '按摩', '占', '湯', '宿', '酒', '麺', '花', '鍵']
H_SIGNS_CJK = ['夜市', '食堂', '電気', '喫茶', '洋食', '麻雀', '大衆', '茶', '氷']
H_SIGNS_LAT = ['HOTEL', 'BAR', 'CAFE', 'OPEN', '24H', 'NOODLE', 'ARCADE', 'PAWN', 'SAUNA', 'LIVE', 'BOOKS', 'TAXI', 'RENT', 'TEA']


def roof(cv, rnd, x, top, w, st, feature=None):
    trim = st['trim']
    cv.rect(x - 1, top - 4, w + 2, 4, trim)
    cv.rect(x - 1, top - 4, w + 2, 1, mul(trim, 1.25))
    cv.rect(x - 1, top - 1, w + 2, 1, mul(trim, 0.6))
    shade(cv, x, top, w, 2, 0.7)
    feats = feature or rnd.sample(['tank', 'antenna', 'vent', 'shack', 'dish', 'billboard', 'rail'], k=rnd.randrange(2, 4))
    cx = x + 4
    for f in feats:
        if cx > x + w - 16:
            break
        if f == 'tank':
            ty = top - 4
            cv.rect(cx + 1, ty - 6, 1, 6, IRON)
            cv.rect(cx + 12, ty - 6, 1, 6, IRON)
            cv.rect(cx + 1, ty - 3, 12, 1, IRON)
            cv.rect(cx, ty - 19, 14, 13, (94, 82, 78))
            cv.rect(cx, ty - 19, 3, 13, (124, 108, 100))
            cv.rect(cx + 11, ty - 19, 3, 13, (66, 58, 60))
            for yy in (ty - 16, ty - 11):
                cv.rect(cx, yy, 14, 1, (58, 50, 54))
            cv.poly([(cx - 1, ty - 19), (cx + 7, ty - 24), (cx + 14, ty - 19)], (70, 62, 68))
            cx += 20
        elif f == 'antenna':
            hgt = rnd.randrange(16, 34)
            cv.rect(cx + 2, top - 4 - hgt, 1, hgt, (60, 62, 84))
            for i, yy in enumerate(range(top - hgt, top - 8, 6)):
                ww = 3 + (i % 2) * 2
                cv.rect(cx + 2 - ww // 2, yy, ww, 1, (60, 62, 84))
            cv.lpx(cx + 2, top - 5 - hgt, RED, 1.0)
            cx += 9
        elif f == 'vent':
            cv.rect(cx, top - 11, 9, 7, (86, 90, 106))
            cv.rect(cx, top - 11, 9, 1, (126, 130, 146))
            for yy in range(top - 9, top - 4, 2):
                cv.rect(cx + 1, yy, 7, 1, (50, 52, 70))
            cx += 13
        elif f == 'dish':
            cv.rect(cx + 3, top - 9, 1, 5, IRON)
            cv.ellipse(cx, top - 14, 8, 7, (150, 154, 170))
            cv.ellipse(cx + 1, top - 13, 6, 5, (96, 100, 120))
            cv.px(cx + 4, top - 11, (200, 204, 220))
            cx += 12
        elif f == 'shack':
            sw = rnd.randrange(18, 28)
            if cx + sw > x + w - 2:
                continue
            cv.rect(cx, top - 20, sw, 16, mul(st['base'], 0.85))
            cv.rect(cx - 1, top - 22, sw + 2, 2, (70, 60, 70))
            window(cv, rnd, cx + 4, top - 16, 6, 7, st['frame'], lit=rnd.choice(LIT) if rnd.random() < 0.6 else None)
            cv.rect(cx + sw - 8, top - 14, 5, 10, (50, 40, 50))
            cx += sw + 4
        elif f == 'rail':
            rw = min(30, x + w - cx - 2)
            cv.rect(cx, top - 10, rw, 1, IRON)
            for xx in range(cx, cx + rw, 3):
                cv.rect(xx, top - 9, 1, 5, IRON)
            cx += rw + 3
        elif f == 'billboard':
            bw = min(rnd.randrange(46, 70), x + w - cx - 2)
            if bw < 40:
                continue
            bh = rnd.randrange(22, 30)
            by = top - 4 - bh - 8
            for xx in (cx + 4, cx + bw - 6):
                cv.rect(xx, by + bh, 2, 8, IRON)
            cv.line([(cx + 5, top - 5), (cx + bw - 5, by + bh)], IRON)
            cv.rect(cx - 1, by - 1, bw + 2, bh + 2, (32, 28, 48))
            col = rnd.choice(NEONS)
            bg = mul(col, 0.16)
            cv.lrect(cx, by, bw, bh, bg, 0.6, body=mul(col, 0.22))
            kind = rnd.random()
            if kind < 0.55:
                t = rnd.choice(H_SIGNS_CJK)
                m = text_mask(t)
                m = m.resize((int(m.width * 1.0), m.height), Image.NEAREST)
                cv.lmask(cx + (bw - m.width) // 2, by + (bh - m.height) // 2, m, col)
            else:
                t = rnd.choice(H_SIGNS_LAT)
                m = text_mask(t, F8B)
                m = m.resize((m.width * 2, m.height * 2), Image.NEAREST)
                if m.width > bw - 4:
                    m = text_mask(t, F8B)
                cv.lmask(cx + (bw - m.width) // 2, by + (bh - m.height) // 2, m, col)
            # 一圈跑马灯
            for xx in range(cx + 1, cx + bw - 1, 3):
                cv.lpx(xx, by, WARM, 0.9)
                cv.lpx(xx, by + bh - 1, WARM, 0.9)
            cx += bw + 4


def shop(cv, rnd, x, w, st, kind):
    y0 = GY - SH
    base = st['base']
    # 店面层换一种更深的底色，上沿一条腰线
    cv.rect(x, y0, w, SH, mul(base, 0.62))
    cv.rect(x, y0, w, 2, st['trim'])
    cv.rect(x, y0 + 2, w, 1, mul(st['trim'], 0.55))
    cv.rect(x, GY - 3, w, 3, mul(base, 0.4))
    if kind == 'glass':
        wc = rnd.choice([(255, 214, 140), (255, 226, 170), (214, 238, 255)])
        cv.rect(x + 3, y0 + 10, w - 6, 24, (50, 40, 52))
        dw = 11
        dx = x + w - 5 - dw if rnd.random() < 0.5 else x + 5
        gx0, gx1 = (x + 5, dx - 3) if dx > x + w // 2 else (dx + dw + 3, x + w - 5)
        cv.lrect(gx0, y0 + 12, gx1 - gx0, 20, wc, 0.8)
        cv.lrect(gx0, y0 + 12, gx1 - gx0, 5, mix(wc, (255, 255, 255), 0.4), 0.85)
        for xx in range(gx0 + 8, gx1 - 2, 12):
            cv.rect(xx, y0 + 12, 1, 20, (50, 40, 52))
        # 货架与商品
        for yy in (y0 + 20, y0 + 26):
            cv.lrect(gx0, yy, gx1 - gx0, 1, mul(wc, 0.55), 0.4)
            for xx in range(gx0 + 1, gx1 - 2, 3):
                if rnd.random() < 0.7:
                    cv.lrect(xx, yy - 3, 2, 3, rnd.choice([RED, ORG, GRN, CYA, MAG, WHT, YEL]), 0.45)
        cv.lrect(dx, y0 + 13, dw, 22, mul(wc, 0.85), 0.6)
        cv.rect(dx + dw // 2, y0 + 13, 1, 22, (50, 40, 52))
        cv.rect(dx + dw // 2 - 2, y0 + 24, 1, 3, (220, 200, 150))
        awning(cv, x + 2, y0 + 4, w - 4, *rnd.choice([((170, 60, 70), (230, 220, 210)), ((60, 120, 110), (220, 220, 200)), ((90, 70, 150), (240, 210, 120)), ((200, 130, 60), (240, 230, 200))]))
    elif kind == 'noodle':
        wood = (120, 78, 56)
        cv.rect(x + 2, y0 + 4, w - 4, SH - 7, wood)
        for xx in range(x + 2, x + w - 2, 4):
            cv.rect(xx, y0 + 4, 1, SH - 7, mul(wood, 0.75))
        ox, ow_ = x + 8, w - 16
        cv.lrect(ox, y0 + 12, ow_, 23, (255, 196, 110), 0.85)
        cv.lrect(ox, y0 + 26, ow_, 9, (255, 220, 150), 0.7)
        # 柜台与食客
        cv.rect(ox, y0 + 28, ow_, 2, (90, 54, 40))
        for xx in range(ox + 3, ox + ow_ - 5, 9):
            cv.rect(xx + 1, y0 + 22, 3, 3, (40, 28, 36))
            cv.rect(xx, y0 + 25, 5, 4, (40, 28, 36))
        # 暖帘
        nc = rnd.choice([(40, 50, 110), (120, 36, 44), (36, 80, 76)])
        for i, xx in enumerate(range(ox, ox + ow_ - 1, 7)):
            cv.rect(xx, y0 + 11, 6, 9, nc)
            cv.px(xx + 2, y0 + 14, (230, 230, 230))
            cv.px(xx + 3, y0 + 15, (230, 230, 230))
            cv.px(xx + 2, y0 + 16, (230, 230, 230))
        cv.rect(ox - 1, y0 + 10, ow_ + 2, 1, (60, 40, 30))
        lantern(cv, x + 1, y0 + 11)
        lantern(cv, x + w - 8, y0 + 11)
    elif kind == 'shutter':
        sc = rnd.choice([(110, 114, 128), (96, 110, 104), (120, 100, 96)])
        cv.rect(x + 4, y0 + 8, w - 8, SH - 11, sc)
        for yy in range(y0 + 9, GY - 3, 2):
            cv.rect(x + 4, yy, w - 8, 1, mul(sc, 0.72))
        # 涂鸦
        for _ in range(3):
            gc = rnd.choice([MAG, CYA, YEL, GRN])
            pts = [(x + 8 + rnd.randrange(w - 16), y0 + 12 + rnd.randrange(18)) for _ in range(4)]
            cv.line(pts, mul(gc, 0.75))
        cv.rect(x + 6, y0 + 12, 6, 8, (214, 204, 180))
        cv.rect(x + 7, y0 + 14, 4, 1, (120, 60, 60))
    elif kind == 'arcade':
        col = rnd.choice([MAG, CYA, VIO])
        cv.rect(x + 3, y0 + 6, w - 6, SH - 9, (26, 20, 44))
        cv.lrect(x + 6, y0 + 16, w - 12, 18, mul(col, 0.5), 0.9, body=mul(col, 0.6))
        for xx in range(x + 8, x + w - 10, 8):
            cv.rect(xx, y0 + 22, 5, 12, (20, 16, 36))
            cv.lrect(xx + 1, y0 + 23, 3, 3, rnd.choice([CYA, GRN, YEL, MAG]), 0.8)
        cv.lline([(x + 4, y0 + 7), (x + w - 5, y0 + 7)], col, 0.9)
        cv.lline([(x + 4, y0 + 14), (x + w - 5, y0 + 14)], col, 0.9)
    elif kind == 'bar':
        cv.rect(x + 3, y0 + 6, w - 6, SH - 9, (40, 26, 40))
        cv.rect(x + 7, y0 + 14, 12, 21, (70, 36, 40))
        cv.rect(x + 8, y0 + 15, 10, 19, (96, 48, 48))
        cv.lrect(x + 10, y0 + 17, 6, 5, (255, 150, 90), 0.7)
        cv.px(x + 16, y0 + 25, (230, 200, 140))
        if w > 46:
            cv.lrect(x + 24, y0 + 16, w - 32, 10, (255, 90, 110), 0.65, body=(200, 70, 90))
            for xx in range(x + 26, x + w - 10, 4):
                cv.rect(xx, y0 + 21, 2, 5, (60, 20, 36))
    elif kind == 'stairs':
        cv.rect(x + 3, y0 + 6, w - 6, SH - 9, mul(base, 0.5))
        dx = x + w // 2 - 8
        cv.rect(dx, y0 + 10, 16, 25, (14, 12, 26))
        for i in range(5):
            cv.rect(dx + 1 + i, y0 + 31 - i * 4, 14 - i * 2, 1, (56, 52, 80))
        cv.lrect(dx + 6, y0 + 11, 4, 1, (120, 220, 255), 0.9)
    elif kind == 'konbini':
        cv.lrect(x + 2, y0 + 3, w - 4, 6, (240, 244, 255), 0.85)
        cv.lrect(x + 2, y0 + 5, w - 4, 1, (255, 190, 60), 0.8)
        cv.lrect(x + 2, y0 + 7, w - 4, 1, (150, 90, 230), 0.8)
        cv.rect(x + 3, y0 + 10, w - 6, 25, (60, 64, 84))
        cv.lrect(x + 4, y0 + 11, w - 8, 23, (224, 240, 255), 0.9)
        for xx in range(x + 14, x + w - 6, 14):
            cv.rect(xx, y0 + 11, 1, 23, (60, 64, 84))
        for yy in (y0 + 19, y0 + 25, y0 + 31):
            for xx in range(x + 5, x + w - 6, 2):
                if rnd.random() < 0.75:
                    cv.lrect(xx, yy - 3, 1, 3, rnd.choice([RED, ORG, GRN, CYA, MAG, YEL, VIO]), 0.5)
            cv.lrect(x + 4, yy, w - 8, 1, (150, 170, 200), 0.4)


def building(cv, rnd, x, w, nfl, style, shop_kind, signs=2, roof_feats=None):
    st = STYLES[style]
    top = GY - SH - nfl * FH
    base = st['base']
    st['tex'](cv, x, top, w, GY - top, base, rnd)
    # 两侧压暗一条，给体积感
    shade(cv, x, top, 2, GY - top, 1.18)
    shade(cv, x + w - 3, top, 3, GY - top, 0.72)
    # 窗
    n = max(1, (w - 10) // 19)
    gap = (w - n * 11) / (n + 1)
    lit_p = rnd.uniform(0.3, 0.6)
    for f in range(nfl):
        fy = top + f * FH
        if f > 0:
            cv.rect(x, fy, w, 1, mul(st['trim'], 0.9))
            cv.rect(x, fy + 1, w, 1, mul(base, 0.55))
        has_balc = rnd.random() < 0.28 and f > 0
        for i in range(n):
            wx = int(x + gap + i * (11 + gap))
            lit = rnd.choice(LIT[:5] if rnd.random() < 0.8 else LIT) if rnd.random() < lit_p else None
            window(cv, rnd, wx, fy + 6, 11, 15, st['frame'], lit=lit, arch=st.get('arch'), shutters=st.get('shutters') if gap > 9 else None, wall=base)
            if not has_balc and rnd.random() < 0.3:
                ac_unit(cv, wx, fy + 25 - 1)
        if has_balc:
            balcony(cv, rnd, int(x + gap) - 3, fy + FH - 4, int(w - 2 * gap) + 6, st['trim'])
    # 水管
    if rnd.random() < 0.7:
        pipe(cv, x + (3 if rnd.random() < 0.5 else w - 6), top + 2, GY - SH)
    shop(cv, rnd, x, w, st, shop_kind)
    roof(cv, rnd, x, top, w, st, roof_feats)
    return top


def sign_set(cv, rnd, x, w, top, shop_kind):
    """给一栋楼挂招牌：竖招牌挂在楼侧，横招牌压在店面腰线上"""
    y0 = GY - SH
    used = []
    # 竖招牌
    for side in rnd.sample(['l', 'r'], k=rnd.choice([1, 1, 2])):
        chars = rnd.choice(V_SIGNS)
        col = rnd.choice(NEONS)
        hh = len(chars) * 17 + 5
        sy = rnd.randrange(top + 8, max(top + 9, y0 - hh - 2))
        sx = x - 14 if side == 'l' else x + w - 6
        if rnd.random() < 0.3:
            lightbox_v(cv, sx + 1, sy, chars, bg=rnd.choice([(255, 232, 190), (255, 244, 220), (220, 240, 255)]), fg=rnd.choice([(130, 20, 30), (30, 40, 110), (20, 80, 60)]))
        else:
            vsign(cv, sx, sy, chars, col, side=side)
    # 店招
    if shop_kind in ('glass', 'noodle', 'bar', 'arcade', 'stairs'):
        if rnd.random() < 0.5:
            t = rnd.choice(H_SIGNS_CJK)
            m = text_mask(t)
            bw = m.width + 10
            bx = x + (w - bw) // 2
            if rnd.random() < 0.5:
                lightbox_h(cv, bx, y0 - 14, t, bg=rnd.choice([(255, 232, 190), (255, 244, 220)]), fg=rnd.choice([(130, 20, 30), (30, 40, 110)]), w=bw)
            else:
                hsign(cv, bx, y0 - 15, t, rnd.choice(NEONS), w=bw)
        else:
            t = rnd.choice(H_SIGNS_LAT)
            col = rnd.choice(NEONS)
            m = text_mask(t, F8B)
            bx = x + (w - m.width - 8) // 2
            hsign(cv, bx, y0 - 9, t, col, font=F8B, pad=3)
        # 霓虹小图标
        if rnd.random() < 0.6:
            ic = {'noodle': 'bowl', 'bar': 'glass', 'stairs': 'arrow', 'glass': rnd.choice(['cup', 'star', 'fish', 'heart']), 'arcade': rnd.choice(['star', 'moon', 'heart'])}[shop_kind]
            icon(cv, x + rnd.choice([4, w - 16]), y0 - 26 - rnd.randrange(0, 6), ic, rnd.choice(NEONS))


def cable(cv, x0, y0, x1, y1, sag, c=(18, 16, 30), bulbs=None, rnd=None):
    pts = []
    n = max(8, abs(x1 - x0) // 4)
    for i in range(n + 1):
        t = i / n
        pts.append((round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t + sag * 4 * t * (1 - t))))
    cv.line(pts, c)
    if bulbs:
        for i, (px_, py_) in enumerate(pts):
            if i % 2 == 1:
                col = bulbs if isinstance(bulbs, tuple) else rnd.choice(bulbs)
                cv.lpx(px_, py_ + 1, col, 1.0)


def street(cv, rnd, x0, x1):
    side = (96, 98, 116)
    cv.rect(x0, GY, x1 - x0, 5, side)
    for xx in range(x0, x1, 8):
        cv.rect(xx, GY, 1, 5, mul(side, 0.72))
    cv.rect(x0, GY, x1 - x0, 1, mul(side, 1.25))
    cv.rect(x0, GY + 5, x1 - x0, 2, (58, 58, 76))
    cv.rect(x0, GY + 7, x1 - x0, H - GY - 7, (30, 30, 46))


def neon_district(cv, rnd, x0, x1):
    pass
    x = x0 + 6
    styles = list(STYLES)
    shops = ['glass', 'noodle', 'bar', 'arcade', 'konbini', 'stairs', 'shutter', 'glass', 'noodle', 'bar', 'glass', 'noodle', 'arcade']
    last_style = None
    tops = []
    while x < x1 - 60:
        w = rnd.randrange(58, 118)
        if x + w > x1 - 8:
            w = x1 - 8 - x
        nfl = rnd.choice([2, 3, 3, 4, 4, 5, 5])
        style = rnd.choice([s for s in styles if s != last_style])
        last_style = style
        kind = rnd.choice(shops)
        if kind == 'konbini' and w < 70:
            kind = 'glass'
        top = building(cv, rnd, x, w, nfl, style, kind)
        tops.append((x, w, top, kind))
        x += w + rnd.choice([0, 0, 5, 9, 14])
    for bx, bw, top, kind in tops:
        sign_set(cv, rnd, bx, bw, top, kind)
    # 街面：路灯、售货机、行人
    xx = x0 + 30
    while xx < x1 - 20:
        r = rnd.random()
        if r < 0.3:
            street_lamp(cv, xx, GY, h=rnd.randrange(50, 62))
        elif r < 0.55:
            vending(cv, rnd, xx, GY)
            if rnd.random() < 0.5:
                vending(cv, rnd, xx + 13, GY, tint=(255, 236, 200))
        elif r < 0.85:
            person(cv, rnd, xx, GY + 2, umbrella=rnd.random() < 0.7)
        else:
            cv.rect(xx, GY - 7, 6, 7, (60, 74, 70))
            cv.rect(xx - 1, GY - 8, 8, 1, (84, 100, 96))
        xx += rnd.randrange(34, 80)
    # 横跨街面的电线与小灯串
    for bi in range(len(tops) - 1):
        ax, aw, at, _ = tops[bi]
        bx2, bw2, bt, _ = tops[bi + 1]
        if rnd.random() < 0.6:
            y = max(at, bt) + rnd.randrange(10, 40)
            cable(cv, ax + aw // 2, y, bx2 + bw2 // 2, y + rnd.randrange(-6, 7), rnd.randrange(4, 10))
        if rnd.random() < 0.3:
            y = GY - SH - rnd.randrange(4, 16)
            cable(cv, ax + 10, y, ax + aw - 10, y, 5, bulbs=[WARM, WARM, RED, GRN, CYA], rnd=rnd)
    return tops
