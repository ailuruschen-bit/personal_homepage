import { OBJECTS } from './geometry.gen';
import { SCENE } from './units';

/**
 * The objects in the carriage that can take focus.
 *
 * zone  Snap region [x0, y0, x1, y1] in scene units. A little larger than the
 *       object itself: the pointer snaps on entering and lets go on leaving.
 * light Where the pool of light lands once snapped, and how big it is:
 *       centre (x, y) and radii (rx, ry).
 *       Both come from geometry.gen.ts, which tools/art/room.py generates
 *       along with the artwork: move an object there and they move with it.
 * shape Outline of the object as polygon vertices. Used to cut a copy out of
 *       the carriage artwork, which is then lifted, brightened and given a
 *       shadow on focus. Leave it out to light an object without lifting it
 *       (the window does this).
 *       The outline must hug the object's edge in room.webp exactly: anything
 *       beyond it lifts the surrounding wall or table along with the object.
 *       After changing the artwork, check these against tools/art/room.py.
 */
/** "Outside" is not a section: selecting it returns to the cover */
export const COVER = 'cover';

export interface Hotspot {
  /** Id of the section to open (see content/sections.ts), or COVER */
  target: string;
  /** Object name, shown under the section name while focused */
  object: string;
  zone: [number, number, number, number];
  light: { x: number; y: number; rx: number; ry: number };
  shape?: Array<[number, number]>;
}

/** Zone and light for an object, from the generated geometry */
function geo(target: string): Pick<Hotspot, 'zone' | 'light'> {
  const g = OBJECTS[target];
  if (!g) throw new Error(`geometry.gen.ts has no object "${target}"`);
  return { zone: g.zone, light: g.light };
}

export const hotspots: Hotspot[] = [
  {
    target: COVER,
    object: '车窗',
    ...geo(COVER),
  },
  {
    target: 'projects',
    object: '电脑',
    ...geo('projects'),
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
    ...geo('about'),
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
    ...geo('stack'),
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
    ...geo('journey'),
    shape: [
      [173, 67],
      [307, 67],
      [307, 87],
      [173, 87],
    ],
  },
  // TODO: notes / hobby / chat have no object yet. Draw the artwork, then register them here.
];

export const hotspotByTarget = (target: string): Hotspot | null =>
  hotspots.find((h) => h.target === target) ?? null;

/** The object nearest the pointer, and how far away it is */
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

/** Distance from the pointer to an object's snap region; 0 inside it */
export function zoneDistance(h: Hotspot, p: { X: number; Y: number }): number {
  const [x0, y0, x1, y1] = h.zone;
  const dx = Math.max(x0 - p.X, 0, p.X - x1);
  const dy = Math.max(y0 - p.Y, 0, p.Y - y1);
  return Math.hypot(dx, dy);
}

/**
 * Turn an outline into the CSS for the lifted copy: scale the carriage
 * artwork so it lines up, then clip-path away everything but this object.
 *
 * The clip sits exactly on the outline. The 1-unit margin only makes the
 * element box slightly larger than the object and takes no part in the clip:
 * any pixel beyond the outline would float up with the wall attached.
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
