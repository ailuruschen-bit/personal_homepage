import numpy as np
from PIL import Image
img = np.load('base.npy'); L = np.load('L.npy')
PH, PW = L.shape
hexc = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
SK = ['#7a5068', '#b47c80', '#dca084', '#f3c7a3']
def put(x, y, c):
    if 0 <= x < PW and 0 <= y < PH: img[y, x] = hexc(c)

# --- the face, shaded as a form: an egg lit from the upper right, the left
# turning into shadow along a curve; the neck in the jaw's shadow
cx, cy, rx, ry = 32.5, 38.0, 12.5, 20.0
Ld = np.array([0.62, -0.38, 0.69]); Ld /= np.linalg.norm(Ld)
for y in range(PH):
    for x in range(PW):
        if L[y, x] != 2: continue
        e = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        if y >= 58 and (x < 27 or x > 38):
            img[y, x] = hexc('#24182c')                    # his hair falls beside the neck
            continue
        if y > 46 and e > 1 and y < 58:
            k = 0                                          # under the jaw
        elif y >= 58:
            k = 0 if x < 35 else 1                         # the neck
        else:
            nx_, ny_ = (x - cx) / rx, (y - cy) / ry
            nz = np.sqrt(max(0.0, 1 - nx_ ** 2 - ny_ ** 2))
            n = np.array([nx_, ny_, nz]); n /= np.linalg.norm(n) + 1e-6
            d = float(n @ Ld)
            k = 0 if d < 0.12 else 1 if d < 0.42 else 2 if d < 0.8 else 3
            if y <= 20: k = max(0, k - 1)                  # under the fringe
        img[y, x] = hexc(SK[k])
# the jaw: a line of shadow where the chin meets the neck
for x in range(26, 39): 
    if L[57, x] == 2: put(x, 57, SK[1] if x > 33 else SK[0])

# --- brows
for x, y in [(23, 32), (24, 31), (25, 31), (26, 31), (27, 31)]: put(x, y, '#2a1b2a')
for x, y in [(35, 31), (36, 31), (37, 31), (38, 31), (39, 32)]: put(x, y, '#3a2634')
# --- eyes: the upper lid line, the iris with a catch light, the white, a soft lower lid
def eye(a, y, right):
    for x in range(a, a + 5): put(x, y - 1, '#1a1020')
    put(a, y, '#1a1020')
    put(a + 1, y, '#3a2240'); put(a + 2, y, '#3a2240')
    put(a + 1, y + 1, '#2a1830'); put(a + 2, y + 1, '#4a2e50')
    put(a + 1, y - 1, '#2a1830')
    put(a + 2, y - 1, '#e6dcf4')                         # the catch light
    put(a + 3, y, '#e9dfdc' if right else '#bfb2b8')
    put(a + 4, y, SK[1] if not right else SK[2])
    put(a + 3, y + 1, SK[1] if not right else SK[2])
    put(a + 2, y + 2, SK[1] if not right else SK[2])
eye(23, 36, False)
eye(35, 36, True)
# --- nose: the shadow down its left, a lit tip
for x, y in [(31, 41), (31, 43), (30, 45), (30, 46)]: put(x, y, SK[1])
put(31, 47, '#9a6470'); put(32, 47, SK[1]); put(33, 46, SK[3])
# --- mouth: a slight smile
for x in range(29, 35): put(x, 51, '#8e4e58')
put(28, 50, '#a46068'); put(35, 50, '#a46068')
for x in range(30, 34): put(x, 52, '#d08a80')
# --- a little warmth on the lit cheek
put(38, 46, '#eaa48e'); put(39, 46, '#eaa48e')

# --- hair: the parting, strands catching the lamp on the right, a few on the left
for y in range(13, 19): put(31, y, '#120c18')
def stroke(pts, c):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
            if L[y, x] == 1: put(x, y, c)
stroke([(33, 14), (38, 16), (42, 21), (44, 28), (44, 34)], '#5a3f58')
stroke([(34, 16), (37, 19), (40, 24), (41, 31)], '#45304c')
stroke([(32, 17), (34, 21), (35, 24)], '#38283f')
stroke([(29, 14), (25, 16), (21, 21), (19, 28)], '#38283f')
stroke([(28, 17), (26, 20), (24, 24)], '#2e2036')
stroke([(45, 38), (46, 46), (46, 54)], '#45304c')
stroke([(18, 38), (17, 46), (18, 55)], '#2e2036')

Image.fromarray(img).save('portrait-art.png')
Image.fromarray(img).resize((PW * 6, PH * 6), Image.NEAREST).save('portrait-art-x6.png')
