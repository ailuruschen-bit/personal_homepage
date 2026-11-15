"""生成全部场景素材，写到 public/assets/。用法：python3 tools/art/build.py [输出目录]"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

import px  # noqa: E402

# 所有素材按 1 倍的像素坐标来画，输出时放大到 2 倍：
# 固有色用 EPX 削掉斜线上的阶梯，光照和辉光直接在 2 倍分辨率上算，所以是平滑的。
px.SCALE = 2

from city import build_c2  # noqa: E402
from far import build_c1, build_c3, build_sky  # noqa: E402
from room import OX, build_room  # noqa: E402


def save(im, path):
    if path.endswith('.webp'):
        im.save(path, quality=90, method=6, alpha_quality=100)
    else:
        im.save(path, optimize=True)
    print(f'{os.path.basename(path):12s} {im.size[0]}x{im.size[1]}  {os.path.getsize(path) / 1024:.0f} KB')


def build_grain(size=192, seed=7):
    """胶片颗粒：一张可平铺的黑白噪点，亮点和暗点各半，强弱写在 alpha 里"""
    rs = np.random.RandomState(seed)
    v = rs.normal(0, 1, (size, size))
    lum = np.where(v > 0, 255, 0).astype(np.uint8)
    alpha = (np.clip(np.abs(v) * 20, 0, 60) // 6 * 6).astype(np.uint8)
    return Image.fromarray(np.dstack([lum, alpha]), 'LA')


def main(out):
    os.makedirs(out, exist_ok=True)
    k = px.SCALE
    save(build_sky(), os.path.join(out, 'sky.webp'))
    save(build_c1(), os.path.join(out, 'c1.webp'))
    save(build_c2(), os.path.join(out, 'c2.webp'))
    save(build_c3(), os.path.join(out, 'c3.webp'))
    room = build_room()
    save(room.crop((OX * k, 0, (OX + 480) * k, 480 * k)), os.path.join(out, 'room.webp'))
    save(room.crop((0, 0, OX * k, 480 * k)).convert('RGB'), os.path.join(out, 'room-l.webp'))
    save(room.crop(((OX + 480) * k, 0, (OX + 600) * k, 480 * k)).convert('RGB'), os.path.join(out, 'room-r.webp'))
    save(build_grain(), os.path.join(out, 'grain.png'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'public', 'assets'))
