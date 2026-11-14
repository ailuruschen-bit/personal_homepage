import type { SceneEls } from './dom';
import { hotspotByTarget, hotspots, nearestHotspot, zoneDistance } from './hotspots';
import { toScene, toScreen, unitSize, type Camera, type ScenePoint } from './units';

/** 判定框外多少场景单位内仍然吸附 */
const SNAP_RANGE = 22;
/** 牵引范围：这个距离内，光点会朝最近的物件偏过去 */
const PULL_RANGE = 78;
/** 牵引最强时，光点朝物件偏移的比例 */
const PULL_MAX = 0.42;
/** 距离变化超过这个量才算「在移动」，用来忽略抖动 */
const DIRECTION_EPSILON = 1.2;
/** 自由状态下光池的半径（场景单位），吸附动画从这个大小展开 */
const FREE_RADIUS = 30;

/** 各项指数平滑的时间常数（秒），越小越跟手 */
const TAU = {
  camera: 0.45,
  parallax: 0.09,
  pull: 0.07,
  poolMove: 0.045,
  poolShape: 0.04,
  dim: 0.12,
} as const;

const smoothing = (dt: number, tau: number) => 1 - Math.exp(-dt / tau);
const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

type Direction = -1 | 0 | 1; // -1 靠近，1 远离

/**
 * 聚焦系统。
 *
 * 镜头保持一个固定的宽构图，不随指针推拉；吸附的是光与物件本身。
 * 指针靠近物件时光点被牵引，进入范围瞬间吸附；离开物件立刻脱离。
 */
export class FocusEngine {
  private focus: string | null = null;
  private pointer: { x: number; y: number } | null = null;
  private camera: Camera = { z: 1, by: 0, px: 0, py: 0 };
  /** 物件上的光池 */
  private pool = { x: 240, y: 240, rx: FREE_RADIUS, ry: FREE_RADIUS, alpha: 0, dim: 0 };
  /** 光点（跟随指针）所在的场景坐标，光池从这里展开 */
  private lightAt: ScenePoint = { X: 240, Y: 240 };
  private distanceRef = new Map<string, number>();
  private direction = new Map<string, Direction>();
  private pull = 0;
  private pullTarget = 0;
  private lastFrame = 0;
  private raf = 0;

  constructor(
    private readonly els: SceneEls,
    private readonly isActive: () => boolean,
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

  clearPointer() {
    this.pointer = null;
    this.setFocus(null);
  }

  /** 触摸没有悬停：点在物件范围内才算选中 */
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

  /** 记录指针相对每个物件是在靠近还是远离 */
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

  /** 吸附判定：靠近才吸，离开即脱离，停住则维持现状 */
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

  /** 光点：一比一跟随指针；朝物件靠近时被它牵引 */
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
    const active = this.isActive();

    this.updateCamera(dt, active);

    this.pull += (this.pullTarget - this.pull) * smoothing(dt, TAU.pull);
    if (active && this.pointer) this.placeLight();
    this.els.ml.style.opacity = active && this.pointer ? '1' : '0';

    this.updatePool(dt, active);
  }

  /** 主菜单下略微拉远，让行李架到桌面都在一屏内；之后只有几像素视差 */
  private updateCamera(dt: number, active: boolean) {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const u = unitSize();

    const zoom = active ? clamp(Math.min(vw / (u * 300), vh / (u * 335)), 0.72, 1) : 1;
    const baseY = active ? (240 - 216) * u * zoom : 0;
    const parallaxX = active && this.pointer ? -(this.pointer.x - vw / 2) * 0.02 : 0;
    const parallaxY = active && this.pointer ? -(this.pointer.y - vh / 2) * 0.02 : 0;

    const c = this.camera;
    const slow = smoothing(dt, TAU.camera);
    const fast = smoothing(dt, TAU.parallax);
    c.z += (zoom - c.z) * slow;
    c.by += (baseY - c.by) * slow;
    c.px += (parallaxX - c.px) * fast;
    c.py += (parallaxY - c.py) * fast;

    this.els.look.style.transform = `translate3d(${c.px.toFixed(2)}px,${(c.by + c.py).toFixed(2)}px,0) scale(${c.z.toFixed(4)})`;
    // 窗外移动得比车厢少，形成前后层次
    this.els.ow.style.transform = `translate3d(${(c.px * 0.5).toFixed(2)}px,${(c.by * 0.35 + c.py * 0.5).toFixed(2)}px,0)`;
  }

  private updatePool(dt: number, active: boolean) {
    const p = this.pool;
    const light = active && this.focus ? hotspotByTarget(this.focus)?.light : undefined;

    let target = { x: p.x, y: p.y, rx: p.rx, ry: p.ry, alpha: 0 };
    if (light) {
      target = { ...light, alpha: 1 };
      if (this.pointer) {
        // 吸住后光池朝指针方向略偏，保留「光还跟着手」的感觉
        const q = toScene(this.pointer.x, this.pointer.y, this.camera);
        target.x += clamp((q.X - light.x) * 0.14, -light.rx * 0.22, light.rx * 0.22);
        target.y += clamp((q.Y - light.y) * 0.14, -light.ry * 0.22, light.ry * 0.22);
      }
    } else if (active && this.pointer) {
      // 未吸附时光池藏在光点下面，吸附瞬间从这里展开
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
