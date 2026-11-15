import { SCENE } from './units';

/**
 * 车厢里可聚焦的物件。
 *
 * zone  磁吸判定范围 [x0, y0, x1, y1]，场景单位。比物件本身略大一圈，
 *       指针进入即吸附；离开即脱离。
 * light 吸附后光池落在哪里、多大：中心 (x, y) 与半径 (rx, ry)。
 * shape 物件轮廓（多边形顶点）。用于从车厢底图上抠出一份副本，
 *       聚焦时抬起、提亮、加投影。不填则只打光不抬起（如窗户）。
 *       必须严格贴着物件在 room.webp 上的边缘：多出来的部分会连同周围的
 *       墙面、桌面一起被抬起来。改动画面后要回到 tools/art/room.py 核对。
 */
/** 「窗外」不是板块：选中它是回到封面 */
export const COVER = 'cover';

export interface Hotspot {
  /** 进入的板块 id（见 content/sections.ts），或 COVER */
  target: string;
  /** 物件名，聚焦时显示在板块名下方 */
  object: string;
  zone: [number, number, number, number];
  light: { x: number; y: number; rx: number; ry: number };
  shape?: Array<[number, number]>;
}

export const hotspots: Hotspot[] = [
  {
    target: COVER,
    object: '车窗',
    zone: [142, 116, 338, 272],
    light: { x: 240, y: 194, rx: 108, ry: 84 },
  },
  {
    target: 'projects',
    object: '电脑',
    zone: [137, 279, 252, 376],
    light: { x: 195, y: 328, rx: 62, ry: 52 },
    shape: [
      [148, 292],
      [214, 288],
      [218, 343],
      [241, 357],
      [241, 359],
      [170, 368],
      [151, 348],
    ],
  },
  {
    target: 'about',
    object: '车票',
    zone: [306, 336, 358, 370],
    light: { x: 332, y: 353, rx: 30, ry: 20 },
    shape: [
      [316, 346],
      [344, 344],
      [348, 358],
      [320, 361],
    ],
  },
  {
    target: 'stack',
    object: '公文包',
    zone: [308, 46, 396, 100],
    light: { x: 352, y: 75, rx: 48, ry: 28 },
    shape: [
      [318, 58],
      [346, 58],
      [346, 55],
      [358, 55],
      [358, 58],
      [386, 58],
      [386, 92],
      [318, 92],
    ],
  },
  {
    target: 'journey',
    object: '线路图',
    zone: [166, 60, 300, 94],
    light: { x: 240, y: 77, rx: 78, ry: 18 },
    shape: [
      [173, 67],
      [307, 67],
      [307, 87],
      [173, 87],
    ],
  },
  // TODO: notes / hobby / chat 还没有对应物件，素材画好后在这里注册。
];

export const hotspotByTarget = (target: string): Hotspot | null =>
  hotspots.find((h) => h.target === target) ?? null;

/** 距离指针最近的物件及其距离 */
export function nearestHotspot(p: { X: number; Y: number }): {
  hotspot: Hotspot;
  distance: number;
} {
  let best = hotspots[0]!;
  let bd = Infinity;
  for (const h of hotspots) {
    const d = zoneDistance(h, p);
    if (d < bd) {
      bd = d;
      best = h;
    }
  }
  return { hotspot: best, distance: bd };
}

/** 指针到某个物件判定框的距离，框内为 0 */
export function zoneDistance(h: Hotspot, p: { X: number; Y: number }): number {
  const [x0, y0, x1, y1] = h.zone;
  const dx = Math.max(x0 - p.X, 0, p.X - x1);
  const dy = Math.max(y0 - p.Y, 0, p.Y - y1);
  return Math.hypot(dx, dy);
}

/**
 * 由轮廓算出「抬起副本」的 CSS：
 * 把底图按原比例放大，再用 clip-path 只留下这个物件。
 *
 * 裁剪严格落在轮廓上。外面那圈 1 单位只是让元素框比物件大一点，
 * 并不参与裁剪：多出来的像素会连着墙一起浮起来。
 */
export function popStyle(shape: Array<[number, number]>) {
  const x0 = Math.min(...shape.map((p) => p[0])) - 1;
  const x1 = Math.max(...shape.map((p) => p[0])) + 1;
  const y0 = Math.min(...shape.map((p) => p[1])) - 1;
  const y1 = Math.max(...shape.map((p) => p[1])) + 1;
  const w = x1 - x0;
  const h = y1 - y0;
  const poly = shape
    .map(([x, y]) => `${(((x - x0) / w) * 100).toFixed(2)}% ${(((y - y0) / h) * 100).toFixed(2)}%`)
    .join(',');
  return {
    left: `${((x0 / SCENE) * 100).toFixed(3)}%`,
    top: `${((y0 / SCENE) * 100).toFixed(3)}%`,
    width: `${((w / SCENE) * 100).toFixed(3)}%`,
    height: `${((h / SCENE) * 100).toFixed(3)}%`,
    backgroundSize: `${((SCENE / w) * 100).toFixed(3)}% ${((SCENE / h) * 100).toFixed(3)}%`,
    backgroundPosition: `${((x0 / (SCENE - w)) * 100).toFixed(3)}% ${((y0 / (SCENE - h)) * 100).toFixed(3)}%`,
    clipPath: `polygon(${poly})`,
  };
}
