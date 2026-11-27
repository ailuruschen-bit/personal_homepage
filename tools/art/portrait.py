"""The portrait on the 档案 page, from the photo on his 履歴書: cut out of its
white ground, relit as if sitting in the compartment (the lamp warm on the
right, the left in shadow with the tube's magenta along its edge), set on the
dark of the carriage, and brought down to 84x112 pixels in a fixed palette
with a light ordered dither (heavier on the ground than on him).

    python3 tools/art/portrait.py   # reads img-000.png (pdfimages of the PDF)

Writes portrait-px.png; copy it to public/assets/portrait.png.
"""
import numpy as np
from PIL import Image, ImageFilter
from collections import deque

src = Image.open('img-000.png').convert('RGB')
a = np.asarray(src).astype(np.float32) / 255
H, W = a.shape[:2]

# --- background mask: near-white, flood-filled in from the top and sides
white = (a.min(axis=2) > 0.86) & (a.max(axis=2) - a.min(axis=2) < 0.08)
bg = np.zeros((H, W), bool)
q = deque()
for x in range(W):
    if white[0, x]: q.append((0, x))
for y in range(H):
    for x in (0, W - 1):
        if white[y, x]: q.append((y, x))
while q:
    y, x = q.popleft()
    if bg[y, x] or not white[y, x]: continue
    bg[y, x] = True
    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and not bg[ny, nx] and white[ny, nx]:
            q.append((ny, nx))
m = Image.fromarray((~bg * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
subj = np.asarray(m).astype(np.float32)[..., None] / 255

# --- crop to 3:4, head and shoulders
y0 = 34; h = int(W / 0.75)
a = a[y0:y0 + h]; subj = subj[y0:y0 + h]
H = a.shape[0]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u = xx / W; v = yy / H

# --- relight as if in the compartment: warm key from the right (the lamp),
# the left side falling into shadow, a magenta rim along the left edge
lum = a @ np.array([0.3, 0.59, 0.11], np.float32)
key = np.clip(0.48 + 0.7 * u, 0, 1.12)[..., None]            # dark left, lit right
warm = np.array([1.06, 0.95, 0.82], np.float32)
cool = np.array([0.72, 0.68, 0.92], np.float32)
tint = cool * (1 - u[..., None]) + warm * u[..., None]
lit = a * key * tint
# contrast: a print, not a scan
lit = np.clip((lit - 0.5) * 1.18 + 0.47, 0, 1)

# rim: distance in from the subject's left edge
sm = subj[..., 0]
edge = np.zeros_like(sm)
run = np.zeros(W, np.float32)
for y in range(H):
    row = sm[y]
    inside = row > 0.5
    if inside.any():
        x0 = np.argmax(inside)
        d = np.arange(W) - x0
        edge[y] = np.clip(1 - d / 7.0, 0, 1) * (d >= 0)
rim = (edge * np.clip(1.1 - v * 0.9, 0.2, 1))[..., None] * np.array([1.0, 0.25, 0.7], np.float32) * 0.85
lit = np.clip(lit + rim * sm[..., None], 0, 1)

# --- the background: the dark carriage behind him, a little light falling across
bgc = np.stack([
    0.10 + 0.07 * u + 0.05 * (1 - v),
    0.07 + 0.03 * u,
    0.15 + 0.06 * (1 - u) + 0.04 * (1 - v),
], -1)
glow = np.exp(-(((u - 0.82) / 0.35) ** 2 + ((v - 0.28) / 0.4) ** 2))[..., None] * np.array([0.22, 0.12, 0.05])
bgc = bgc + glow
img = lit * subj + bgc * (1 - subj)
# vignette
vig = 1 - 0.55 * (((u - 0.52) / 0.75) ** 2 + ((v - 0.45) / 0.8) ** 2)
img = np.clip(img * np.clip(vig, 0.35, 1)[..., None], 0, 1)

# --- to pixels: small, a fixed palette, ordered dither
PW, PH = 84, 112
small = Image.fromarray((img * 255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(2, 80, 2)).resize((PW, PH), Image.LANCZOS)
s = np.asarray(small).astype(np.float32) / 255
ms = np.asarray(Image.fromarray((subj[..., 0] * 255).astype(np.uint8)).resize((PW, PH), Image.BILINEAR)).astype(np.float32) / 255
PAL = np.array([
    (18, 12, 26), (34, 22, 44), (52, 34, 62), (78, 46, 82),        # shadows, purple
    (120, 52, 120), (210, 70, 160), (255, 120, 200),               # magenta rim
    (96, 62, 56), (150, 98, 82), (196, 140, 112), (232, 182, 148), (250, 220, 190),  # skin, warm
    (70, 46, 66), (104, 70, 92), (140, 96, 112), (176, 126, 132),   # skin in the cool shadow
    (28, 22, 30), (58, 44, 48),                                     # hair
    (226, 220, 210), (178, 176, 190),                               # shirt
    (110, 104, 78), (150, 140, 104), (78, 74, 58),                  # cardigan
    (214, 132, 46), (240, 178, 80), (46, 52, 96), (150, 86, 40),                   # tie
], np.float32) / 255
bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.5
out = np.zeros_like(s)
for y in range(PH):
    for x in range(PW):
        c = s[y, x] + bayer[y % 4, x % 4] * (0.045 - 0.03 * ms[y, x])
        d = ((PAL - c) ** 2 @ np.array([0.35, 0.45, 0.2], np.float32))
        out[y, x] = PAL[np.argmin(d)]
px = Image.fromarray((out * 255).astype(np.uint8))
px.save('portrait-px.png')
px.resize((PW * 4, PH * 4), Image.NEAREST).save('portrait-x4.png')
print('ok', px.size)
