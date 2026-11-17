import type { SceneEls } from './dom';
import type { Phase } from './opening';
import { hotspotByTarget, hotspots, nearestHotspot, zoneDistance } from './hotspots';
import { toScene, toScreen, unitSize, type Camera, type ScenePoint } from './units';
import { CAMERA } from './geometry.gen';

/** How many scene units beyond its region an object still snaps from */
const SNAP_RANGE = 22;
/** Pull range: within this distance the light drifts toward the nearest object */
const PULL_RANGE = 78;
/** How far the light leans toward the object at full pull, as a fraction */
const PULL_MAX = 0.42;
/** Distance must change by at least this much to count as movement; ignores jitter */
const DIRECTION_EPSILON = 1.2;
/** Scene y of .cam's zoom origin; geometry.gen.css sets the same point as its transform-origin */
const CAM_ORIGIN_Y = CAMERA.y;
/** Radius of the free-floating pool in scene units; the snap animation grows from it */
const FREE_RADIUS = 30;

/** Time constants for the exponential smoothing, in seconds. Smaller is snappier */
const TAU = {
  camera: 0.34,
  parallax: 0.09,
  pull: 0.07,
  poolMove: 0.045,
  poolShape: 0.04,
  dim: 0.12,
} as const;

const smoothing = (dt: number, tau: number) => 1 - Math.exp(-dt / tau);
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

type Direction = -1 | 0 | 1; // -1 approaching, 1 moving away

/**
 * Focus system.
 *
 * The camera holds one fixed wide framing and never pushes in with the pointer.
 * What snaps is the light and the object itself: the light is pulled in as the
 * pointer approaches, snaps the moment it enters range, and lets go on leaving.
 */
export class FocusEngine {
  private focus: string | null = null;
  private pointer: { x: number; y: number } | null = null;
  private camera: Camera = { z: 1, by: 0, px: 0, py: 0 };
  private outside = { x: 0, y: 0 };
  private frameKey = '';
  private lookTransform = '';
  private lastPhase: Phase | null = null;
  /** Pool of light resting on the object */
  private pool = { x: 240, y: 240, rx: FREE_RADIUS, ry: FREE_RADIUS, alpha: 0, dim: 0 };
  /** Scene position of the pointer light, the point the pool grows out of */
  private lightAt: ScenePoint = { X: 240, Y: 240 };
  private distanceRef = new Map<string, number>();
  private direction = new Map<string, Direction>();
  private pull = 0;
  private pullTarget = 0;
  private lastFrame = 0;
  private raf = 0;

  constructor(
    private readonly els: SceneEls,
    private readonly phase: () => Phase,
    private readonly labelOf: (target: string) => string,
  ) {}

  start() {
    const loop = (now: number) => {
      this.tick(now);
      this.raf = requestAnimationFrame(loop);
    };
    this.raf = requestAnimationFrame(loop);
  }

  stop() {
    cancelAnimationFrame(this.raf);
  }

  get focused(): string | null {
    return this.focus;
  }

  movePointer(x: number, y: number) {
    this.pointer = { x, y };
    this.setFocus(this.resolveFocus(toScene(x, y, this.camera)));
    this.placeLight();
  }

  /** Record the pointer without resolving focus. Used outside the hub so the
   *  parallax is already in place when the hub arrives. */
  trackPointer(x: number, y: number) {
    this.pointer = { x, y };
  }

  clearPointer() {
    this.pointer = null;
    this.setFocus(null);
  }

  /** Touch has no hover: only a tap inside an object counts as selecting it */
  targetAt(x: number, y: number): string | null {
    const { hotspot, distance } = nearestHotspot(toScene(x, y, this.camera));
    return distance < SNAP_RANGE ? hotspot.target : null;
  }

  setFocus(target: string | null) {
    if (target === this.focus) return;
    this.focus = target;

    for (const el of this.els.pops) el.classList.toggle('on', el.dataset.pop === target);
    this.els.stage.classList.toggle('snap', target !== null);

    const hotspot = target ? hotspotByTarget(target) : null;
    if (hotspot) {
      this.els.cap.replaceChildren(this.labelOf(hotspot.target), small(hotspot.object));
      this.els.cap.classList.add('on');
    } else {
      this.els.cap.classList.remove('on');
    }
  }

  /** Track whether the pointer is approaching or leaving each object */
  private trackDirections(p: ScenePoint) {
    for (const h of hotspots) {
      const d = zoneDistance(h, p);
      const ref = this.distanceRef.get(h.target);
      if (ref === undefined) {
        this.distanceRef.set(h.target, d);
        this.direction.set(h.target, 0);
      } else if (d < ref - DIRECTION_EPSILON) {
        this.distanceRef.set(h.target, d);
        this.direction.set(h.target, -1);
      } else if (d > ref + DIRECTION_EPSILON) {
        this.distanceRef.set(h.target, d);
        this.direction.set(h.target, 1);
      }
    }
  }

  /** Snap rule: only snap while approaching, let go on leaving, hold when still */
  private resolveFocus(p: ScenePoint): string | null {
    this.trackDirections(p);

    const current = this.focus ? hotspotByTarget(this.focus) : null;
    if (current) {
      const leaving = zoneDistance(current, p) > 0 && this.direction.get(current.target) === 1;
      if (!leaving) return current.target;
    }

    let best: string | null = null;
    let bestDistance = Infinity;
    for (const h of hotspots) {
      const d = zoneDistance(h, p);
      const approaching = this.direction.get(h.target) === -1;
      if (d < bestDistance && (d === 0 || (d < SNAP_RANGE && approaching))) {
        bestDistance = d;
        best = h.target;
      }
    }
    return best;
  }

  /** The light follows the pointer one to one, and is pulled toward an object as it nears */
  private placeLight() {
    if (!this.pointer) return;
    let { x, y } = this.pointer;

    this.pullTarget = 0;
    if (!this.focus) {
      const { hotspot, distance } = nearestHotspot(toScene(x, y, this.camera));
      const approaching = this.direction.get(hotspot.target) === -1;
      if (distance < PULL_RANGE && approaching) {
        const t = 1 - (distance - SNAP_RANGE) / (PULL_RANGE - SNAP_RANGE);
        this.pullTarget = PULL_MAX * t * t;
      }
      if (this.pull > 0.002) {
        const anchor = toScreen(hotspot.light.x, hotspot.light.y, this.camera);
        x += (anchor.x - x) * this.pull;
        y += (anchor.y - y) * this.pull;
      }
    }

    this.lightAt = toScene(x, y, this.camera);
    this.els.ml.style.transform = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0)`;
  }

  private tick(now: number) {
    const dt = Math.min(0.05, (now - this.lastFrame) / 1000 || 0.016);
    this.lastFrame = now;
    const active = this.phase() === 'hub';

    this.syncFrame();
    this.updateParallax(dt);

    this.pull += (this.pullTarget - this.pull) * smoothing(dt, TAU.pull);
    if (active && this.pointer) this.placeLight();
    this.els.ml.style.opacity = active && this.pointer ? '1' : '0';

    this.updatePool(dt, active);
  }

  /**
   * The hub framing: pull back slightly so everything from the luggage rack to
   * the table fits on screen.
   *
   * This is not driven frame by frame. It is written to --fz / --fy on .stage and
   * consumed by .cam in CSS, so the return animation lands exactly on this framing
   * and a skipped opening tweens to it. The opening keeps the original close-up.
   */
  syncFrame() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const u = unitSize();
    const framed = this.phase() !== 'intro';

    const zoom = framed ? clamp(Math.min(vw / (u * 300), vh / (u * 335)), 0.72, 1) : 1;
    const baseY = framed ? (240 - 216) * u * zoom : 0;
    this.camera.z = zoom;
    this.camera.by = baseY;

    // .cam's zoom origin sits at the gap in the blinds rather than the centre of the
    // frame, so convert the framing offset into the equivalent translation
    const shift = baseY + (240 - CAM_ORIGIN_Y) * u * (1 - zoom);
    const key = `${zoom.toFixed(4)},${shift.toFixed(2)}`;
    if (key === this.frameKey) return;
    this.frameKey = key;
    this.els.stage.style.setProperty('--fz', zoom.toFixed(4));
    this.els.stage.style.setProperty('--fy', `${shift.toFixed(2)}px`);
  }

  /** A few pixels of pointer parallax: the carriage moves more, the city outside less */
  private updateParallax(dt: number) {
    const phase = this.phase();
    const seated = phase === 'hub' || phase === 'back';
    const c = this.camera;
    const tx = seated && this.pointer ? -(this.pointer.x - window.innerWidth / 2) * 0.02 : 0;
    const ty = seated && this.pointer ? -(this.pointer.y - window.innerHeight / 2) * 0.02 : 0;

    // .look is only updated per frame inside the hub, where it is its own compositing
    // layer. Touching it while the camera is still zooming would repaint the whole
    // carriage every frame, so in every other phase it jumps straight to its target
    // while out of sight: aimed at the pointer on the first frame of the return, held
    // still while looking outside, zeroed otherwise.
    if (phase === 'hub') {
      const fast = smoothing(dt, TAU.parallax);
      c.px += (tx - c.px) * fast;
      c.py += (ty - c.py) * fast;
    } else if (phase === 'back' ? phase !== this.lastPhase : phase !== 'peek') {
      c.px = tx;
      c.py = ty;
    }
    this.lastPhase = phase;
    const look = `translate3d(${c.px.toFixed(2)}px,${c.py.toFixed(2)}px,0)`;
    if (look !== this.lookTransform) {
      this.lookTransform = look;
      this.els.look.style.transform = look;
    }

    // The city outside is always visible, so its offset is always eased
    const slow = smoothing(dt, TAU.camera);
    const o = this.outside;
    o.x += (tx * 0.5 - o.x) * slow;
    o.y += ((seated ? c.by * 0.35 : 0) + ty * 0.5 - o.y) * slow;
    this.els.ow.style.transform = `translate3d(${o.x.toFixed(2)}px,${o.y.toFixed(2)}px,0)`;
  }

  private updatePool(dt: number, active: boolean) {
    const p = this.pool;
    const light = active && this.focus ? hotspotByTarget(this.focus)?.light : undefined;

    let target = { x: p.x, y: p.y, rx: p.rx, ry: p.ry, alpha: 0 };
    if (light) {
      target = { ...light, alpha: 1 };
      if (this.pointer) {
        // Once snapped the pool still leans toward the pointer, so the light keeps
        // feeling attached to the hand
        const q = toScene(this.pointer.x, this.pointer.y, this.camera);
        target.x += clamp((q.X - light.x) * 0.14, -light.rx * 0.22, light.rx * 0.22);
        target.y += clamp((q.Y - light.y) * 0.14, -light.ry * 0.22, light.ry * 0.22);
      }
    } else if (active && this.pointer) {
      // While unsnapped the pool hides under the pointer light and grows out of it
      p.x = target.x = this.lightAt.X;
      p.y = target.y = this.lightAt.Y;
      p.rx = p.ry = target.rx = target.ry = FREE_RADIUS;
    }

    const move = smoothing(dt, TAU.poolMove);
    const shape = smoothing(dt, TAU.poolShape);
    p.x += (target.x - p.x) * move;
    p.y += (target.y - p.y) * move;
    p.rx += (target.rx - p.rx) * shape;
    p.ry += (target.ry - p.ry) * shape;
    p.alpha += (target.alpha - p.alpha) * shape;
    p.dim += ((light ? 1 : 0) - p.dim) * smoothing(dt, TAU.dim);

    this.els.beam.style.opacity = p.alpha.toFixed(3);
    // .spot dims the 480 scene around the focused object and stops at its
    // edges; the side images are a dark foreground, so the edge is where the
    // room ends anyway (docs/13, D-01a)
    this.els.spot.style.opacity = p.dim.toFixed(3);
    if (p.alpha < 0.004 && p.dim < 0.004) return;

    for (const el of [this.els.spot, this.els.beam]) {
      el.style.setProperty('--sx', `${(p.x / 4.8).toFixed(2)}%`);
      el.style.setProperty('--sy', `${(p.y / 4.8).toFixed(2)}%`);
      el.style.setProperty('--rx', `${(p.rx / 4.8).toFixed(2)}%`);
      el.style.setProperty('--ry', `${(p.ry / 4.8).toFixed(2)}%`);
    }
  }
}

function small(text: string): HTMLElement {
  const el = document.createElement('small');
  el.textContent = text;
  return el;
}
