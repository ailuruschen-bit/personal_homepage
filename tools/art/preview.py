"""Review images for the art redraw, written to .review/<label>/.

Usage: npm run art:preview -- [label] [--against DIR]

Reads the built assets in public/assets and the generated geometry in
src/scene/geometry.gen.ts (so run `npm run art` first) and writes:

  hub.png          the carriage composited the way the page lays it out
  hub-debug.png    the same with the geometry drawn over it, as ?debug=geometry
  luma.png         luminance only, for judging values (docs/13, stage 3)
  objects.png      every object sprite at 3x on magenta, so stray pixels show
  crops/*.png      the areas the review keeps returning to, at 3x
  compare-*.png    baseline on the left, now on the right, for the hub and crops

The baseline is .review/baseline/assets unless --against names another asset
folder. The label defaults to the current commit. See docs/13, step 0.6.
"""
import os
import re
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
K = 2  # px.SCALE: assets are written at 2x the 480 scene
SIDE = 120  # width of each side extension, in scene units

# Areas to crop, in scene units, x0 y0 x1 y1 over the full 720-wide composite
# (so the room's own x runs from 120 to 600)
CROPS = {
    'seat-left': (40, 220, 260, 480),
    'seat-right': (460, 220, 680, 480),
    'table': (230, 280, 490, 440),
    'rack': (120, 0, 600, 110),
    'wall-left': (130, 100, 270, 290),
    'wall-right': (460, 100, 600, 290),
    'window': (260, 110, 460, 300),
}


def composite(assets):
    """The carriage as the page lays it out: sky and city behind, room and side
    extensions over them. 720 x 480 scene units at 2x."""
    W, H = (480 + 2 * SIDE) * K, 480 * K
    out = Image.new('RGBA', (W, H), (10, 6, 20, 255))
    sky = Image.open(os.path.join(assets, 'sky.webp')).convert('RGBA').resize((W, H))
    out.alpha_composite(sky)
    for name in ('c1', 'c2', 'c3'):
        layer = Image.open(os.path.join(assets, f'{name}.webp')).convert('RGBA')
        out.alpha_composite(layer.crop((0, 0, W, layer.height)), (0, H - layer.height - 60))
    for name, x in (('room-l', 0), ('room', SIDE * K), ('room-r', (SIDE + 480) * K)):
        out.alpha_composite(Image.open(os.path.join(assets, f'{name}.webp')).convert('RGBA'), (x, 0))
    return out


def geometry():
    """Window, camera and objects, read back from geometry.gen.ts."""
    src = open(os.path.join(ROOT, 'src', 'scene', 'geometry.gen.ts')).read()
    nums = lambda s: [float(v) for v in re.findall(r'-?[\d.]+', s)]
    win = nums(re.search(r'WINDOW = \{([^}]*)\}', src).group(1))
    cam = nums(re.search(r'CAMERA = \{([^}]*)\}', src).group(1))
    objects = {}
    for m in re.finditer(r'^ {2}(\w+): \{ (.*) \},$', src, re.M):
        body = m.group(2)
        o = {'zone': nums(re.search(r'zone: \[([^\]]*)\]', body).group(1)),
             'light': nums(re.search(r'light: \{([^}]*)\}', body).group(1))}
        box = re.search(r'box: \{([^}]*)\}', body)
        if box:
            o['box'] = nums(box.group(1))
        sprite = re.search(r"sprite: '([^']+)'", body)
        if sprite:
            o['sprite'] = sprite.group(1)
        objects[m.group(1)] = o
    return win, cam, objects


def overlay(im, geo):
    """The geometry drawn over a composite, in the overlay's colours."""
    win, cam, objects = geo
    out = im.copy()
    d = ImageDraw.Draw(out)
    S = lambda v: (v + SIDE) * K  # scene x to composite pixels
    Y = lambda v: v * K
    x, y, w, h, r = win
    d.rounded_rectangle([S(x), Y(y), S(x + w), Y(y + h)], r * K, outline=(57, 255, 136), width=2)
    d.line([S(cam[0] - 6), Y(cam[1]), S(cam[0] + 6), Y(cam[1])], fill=(255, 59, 59), width=2)
    d.line([S(cam[0]), Y(cam[1] - 6), S(cam[0]), Y(cam[1] + 6)], fill=(255, 59, 59), width=2)
    for key, o in objects.items():
        x0, y0, x1, y1 = o['zone']
        for i in range(int(S(x0)), int(S(x1)), 10):  # dashed
            d.line([i, Y(y0), min(i + 5, S(x1)), Y(y0)], fill=(255, 210, 59), width=2)
            d.line([i, Y(y1), min(i + 5, S(x1)), Y(y1)], fill=(255, 210, 59), width=2)
        for j in range(int(Y(y0)), int(Y(y1)), 10):
            d.line([S(x0), j, S(x0), min(j + 5, Y(y1))], fill=(255, 210, 59), width=2)
            d.line([S(x1), j, S(x1), min(j + 5, Y(y1))], fill=(255, 210, 59), width=2)
        lx, ly, rx, ry = o['light']
        d.ellipse([S(lx - rx), Y(ly - ry), S(lx + rx), Y(ly + ry)], outline=(255, 92, 225), width=2)
        if 'box' in o:
            bx, by, bw, bh = o['box']
            d.rectangle([S(bx), Y(by), S(bx + bw) - 1, Y(by + bh) - 1], outline=(59, 214, 255), width=2)
        d.text((S(x0) + 2, Y(y0) - 12), key, fill=(255, 210, 59))
    return out


def luma(im):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    y = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    return Image.fromarray(np.clip(y, 0, 255).astype(np.uint8), 'L')


def zoom(im, box, k=3):
    x0, y0, x1, y1 = (v * K for v in box)
    c = im.crop((x0, y0, x1, y1))
    return c.resize((c.width * k // K, c.height * k // K), Image.NEAREST)


def side_by_side(a, b, gap=12):
    out = Image.new('RGBA', (a.width + b.width + gap, max(a.height, b.height)), (255, 0, 255, 255))
    out.alpha_composite(a.convert('RGBA'), (0, 0))
    out.alpha_composite(b.convert('RGBA'), (a.width + gap, 0))
    return out


def sprites_sheet(assets, objects):
    ims = [Image.open(os.path.join(ROOT, 'public', o['sprite'].lstrip('/'))).convert('RGBA')
           for o in objects.values() if 'sprite' in o]
    big = [i.resize((i.width * 3, i.height * 3), Image.NEAREST) for i in ims]
    sheet = Image.new('RGBA', (sum(b.width for b in big) + 15 * (len(big) + 1), max(b.height for b in big) + 30),
                      (255, 0, 255, 255))
    x = 15
    for b in big:
        sheet.alpha_composite(b, (x, 15))
        x += b.width + 15
    return sheet


def main(argv):
    against = os.path.join(ROOT, '.review', 'baseline', 'assets')
    if '--against' in argv:
        i = argv.index('--against')
        against = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    label = argv[0] if argv else subprocess.run(
        ['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip() or 'latest'
    out = os.path.join(ROOT, '.review', label)
    os.makedirs(os.path.join(out, 'crops'), exist_ok=True)

    assets = os.path.join(ROOT, 'public', 'assets')
    now = composite(assets)
    geo = geometry()
    now.convert('RGB').save(os.path.join(out, 'hub.png'))
    overlay(now, geo).convert('RGB').save(os.path.join(out, 'hub-debug.png'))
    luma(now).save(os.path.join(out, 'luma.png'))
    sprites_sheet(assets, geo[2]).convert('RGB').save(os.path.join(out, 'objects.png'))
    for name, box in CROPS.items():
        zoom(now, box).convert('RGB').save(os.path.join(out, 'crops', f'{name}.png'))

    if os.path.isdir(against):
        then = composite(against)
        side_by_side(then, now).convert('RGB').save(os.path.join(out, 'compare-hub.png'))
        for name, box in CROPS.items():
            side_by_side(zoom(then, box), zoom(now, box)).convert('RGB').save(
                os.path.join(out, f'compare-{name}.png'))
    print(f'preview written to {os.path.relpath(out, ROOT)}/')


if __name__ == '__main__':
    main(sys.argv[1:])
