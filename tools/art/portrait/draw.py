"""His portrait as pixel art (a 立绘, not a filtered photo): the photo gives only
the shapes - where the hair, face, collar, cardigan and tie are - and the
drawing is done here, flat, in bands of colour lit as in the compartment, with
the features drawn in by hand."""
import numpy as np
from PIL import Image, ImageFilter

lab = np.load('lab.npy'); lum = np.load('lum.npy')
H, W = lab.shape
# the cardigan: what the colour test took for skin below the collar line,
# except the neck between the collar points
yy, xx = np.mgrid[0:H, 0:W]
neck = (xx > 104) & (xx < 162) & (yy < 300)
lab[(lab == 2) & (yy > 262) & ~neck] = 4
lab[(lab == 2) & (yy > 300)] = 4

PW, PH = 63, 84
def down(lab):
    # majority vote per cell
    out = np.zeros((PH, PW), np.uint8)
    for y in range(PH):
        for x in range(PW):
            y0, y1 = int(y * H / PH), int((y + 1) * H / PH)
            x0, x1 = int(x * W / PW), int((x + 1) * W / PW)
            c = np.bincount(lab[y0:y1, x0:x1].ravel(), minlength=6)
            out[y, x] = np.argmax(c)
    return out
L = down(lab)
# tidy: a mode filter, twice
for _ in range(2):
    P = np.pad(L, 1, mode='edge'); N = L.copy()
    for y in range(PH):
        for x in range(PW):
            c = np.bincount(P[y:y + 3, x:x + 3].ravel(), minlength=6)
            if c.max() >= 5: N[y, x] = np.argmax(c)
    L = N
lum_s = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)).resize((PW, PH), Image.BOX)).astype(np.float32) / 255

hexc = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
PAL = {
    'out': '#120c18',
    1: ['#160f1c', '#24182c', '#38283f', '#5a3f58'],          # hair: shadow .. sheen
    2: ['#7a5068', '#b47c80', '#dca084', '#f3c7a3'],          # skin: cool shadow .. light
    3: ['#7d7896', '#b9b3c6', '#e2ddd8', '#f6f1e8'],          # shirt
    4: ['#3e3a30', '#5e5844', '#827a58', '#a2976c'],          # cardigan
    5: ['#7a3c22', '#c06a2a', '#e2963c', '#f4c070'],          # tie
}
img = np.zeros((PH, PW, 3), np.uint8)
u = np.linspace(0, 1, PW)[None, :].repeat(PH, 0)
v = np.linspace(0, 1, PH)[:, None].repeat(PW, 1)

# background: the dark of the carriage, the lamp's warmth up on the right,
# light through the blinds in faint bands, dithered
bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16
BG = [hexc(c) for c in ('#0e0a16', '#171022', '#20162e', '#2c1d36', '#3d2738')]
g = 0.25 + 0.35 * u * (1 - v) + 0.25 * np.exp(-(((u - 0.85) / 0.3) ** 2 + ((v - 0.25) / 0.3) ** 2))
g -= 0.25 * (((u - 0.5) / 0.7) ** 2 + ((v - 0.5) / 0.8) ** 2)
g += 0.06 * (((np.arange(PH)[:, None] + np.arange(PW)[None, :] // 6) // 3) % 2 == 0) * (v < 0.55)
for y in range(PH):
    for x in range(PW):
        k = int(np.clip(g[y, x] * 5 + bayer[y % 4, x % 4] - 0.5, 0, 4))
        img[y, x] = BG[k]

# the figure in bands: lit from the right and above, the photo's own light
# and shade kept only as a soft hint of form
for y in range(PH):
    for x in range(PW):
        m = L[y, x]
        if m == 0: continue
        light = 0.62 * u[y, x] + 0.18 * (1 - v[y, x]) + 0.45 * (lum_s[y, x] - 0.5)
        if m == 1: light = 0.45 * u[y, x] + 0.5 * (lum_s[y, x] - 0.1) - 0.1
        k = int(np.clip(light * 3.2 + 0.5, 0, 3))
        tie_navy = m == 5 and lum_s[y, x] < 0.42
        c = '#2e3460' if tie_navy else PAL[m][k]
        img[y, x] = hexc(c)

# outline: the figure against the ground, and the collar against the cardigan
subj = L > 0
for y in range(PH):
    for x in range(PW):
        if not subj[y, x]: continue
        nb = [(y + dy, x + dx) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if any(0 <= a < PH and 0 <= b < PW and not subj[a, b] for a, b in nb) and y < PH - 1:
            img[y, x] = hexc(PAL['out'])
        elif L[y, x] == 3 and any(0 <= a < PH and 0 <= b < PW and L[a, b] == 4 for a, b in nb):
            img[y, x] = hexc('#4a4560')

# the tube's magenta along his left edge, the lamp's warmth catching the right of the hair
for y in range(PH):
    row = np.where(subj[y])[0]
    if len(row) == 0 or y > PH - 3: continue
    x0, x1 = row[0], row[-1]
    if v[y, 0] < 0.8:
        img[y, x0 + 1] = hexc('#c2409a') if L[y, x0 + 1] == 1 else hexc('#d0609a')
        if v[y, 0] < 0.45 and L[y, x0 + 2] == 1: img[y, x0 + 2] = hexc('#6e2e62')
    if L[y, x1 - 1] == 1 and v[y, 0] < 0.5: img[y, x1 - 1] = hexc('#8a5a4c')
np.save('base.npy', img); np.save('L.npy', L)
Image.fromarray(img).save('cel.png')
Image.fromarray(img).resize((PW * 6, PH * 6), Image.NEAREST).save('cel-x6.png')
