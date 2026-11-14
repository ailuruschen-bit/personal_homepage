import { SCENE } from './units';

/**
 * 车厢里可聚焦的物件。
 *
 * zone  磁吸判定范围 [x0, y0, x1, y1]，场景单位。比物件本身略大一圈，
 *       指针进入即吸附；离开即脱离。
 * light 吸附后光池落在哪里、多大：中心 (x, y) 与半径 (rx, ry)。
 * shape 物件轮廓（多边形顶点）。用于从车厢底图上抠出一份副本，
 *       聚焦时抬起、提亮、加投影。不填则只打光不抬起（如窗户）。
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
      [147, 293],
      [214, 287],
      [219, 343],
      [242, 358],
      [170, 367],
      [150, 349],
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
      [176, 70],
      [304, 70],
      [304, 84],
      [176, 84],
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
 */
export function popStyle(shape: Array<[number, number]>) {
  const cx = shape.reduce((s, p) => s + p[0], 0) / shape.length;
  const cy = shape.reduce((s, p) => s + p[1], 0) / shape.length;
  // 顶点沿中心向外扩 2.5 单位，避免描边被裁掉
  const out = shape.map(([x, y]) => {
    const d = Math.hypot(x - cx, y - cy) || 1;
    return [x + ((x - cx) / d) * 2.5, y + ((y - cy) / d) * 2.5] as [number, number];
  });
  const x0 = Math.min(...out.map((p) => p[0])) - 1;
  const x1 = Math.max(...out.map((p) => p[0])) + 1;
  const y0 = Math.min(...out.map((p) => p[1])) - 1;
  const y1 = Math.max(...out.map((p) => p[1])) + 1;
  const w = x1 - x0;
  const h = y1 - y0;
  const poly = out
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
