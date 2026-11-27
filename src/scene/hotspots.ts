import { OBJECTS } from './geometry.gen';

/**
 * The objects in the carriage that can take focus.
 *
 * zone  Snap region [x0, y0, x1, y1] in scene units. A little larger than the
 *       object itself: the pointer snaps on entering and lets go on leaving.
 * light Where the pool of light lands once snapped, and how big it is:
 *       centre (x, y) and radii (rx, ry).
 *       Both come from geometry.gen.ts, which tools/art/room.py generates
 *       along with the artwork: move an object there and they move with it.
 * box, sprite
 *       The object drawn alone, cut out along its own silhouette, and where it
 *       sits. On focus the sprite is lifted, brightened and given a shadow.
 *       Objects without one (the window) are lit without being lifted.
 */
/** "Outside" is not a section: selecting it returns to the cover */
export const COVER = 'cover';

export interface Hotspot {
  /** Id of the section to open (see content/sections.ts), or COVER */
  target: string;
  zone: [number, number, number, number];
  light: { x: number; y: number; rx: number; ry: number };
  box?: { x: number; y: number; w: number; h: number };
  sprite?: string;
  /** What stands in front of the object: drawn above its sprite, never lifted */
  front?: { x: number; y: number; w: number; h: number; sprite: string };
  /** Where the object was, without it: shown while the scroll story carries it away */
  gone?: { x: number; y: number; w: number; h: number; sprite: string };
}

/** Where an object is, from the generated geometry */
function geo(
  target: string,
): Pick<Hotspot, 'zone' | 'light' | 'box' | 'sprite' | 'front' | 'gone'> {
  const g = OBJECTS[target];
  if (!g) throw new Error(`geometry.gen.ts has no object "${target}"`);
  return {
    zone: g.zone,
    light: g.light,
    box: g.box,
    sprite: g.sprite,
    front: g.front,
    gone: g.gone,
  };
}

export const hotspots: Hotspot[] = [
  {
    target: COVER,
    ...geo(COVER),
  },
  {
    target: 'projects',
    ...geo('projects'),
  },
  {
    target: 'about',
    ...geo('about'),
  },
  {
    target: 'stack',
    ...geo('stack'),
  },
  {
    target: 'journey',
    ...geo('journey'),
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
