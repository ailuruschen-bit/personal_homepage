import type { SceneEls } from './dom';
import { hotspotByTarget } from './hotspots';
import { toScene, unitSize, type Camera } from './units';
import { sectionById } from '../content/sections';

/**
 * The story, docs/10. Two modes that are never on screen together:
 *
 *   scene  the carriage alone. Wheel, touch and keys move a progress value
 *          (there is no tall document) that walks the camera from the hub to
 *          each object in turn and back.
 *   page   an ordinary document, one per chapter, scrolled natively. The
 *          carriage is not rendered at all.
 *
 * Reaching an object (a node on the progress axis) cuts to its page through
 * black; pushing past the top or the bottom of a page cuts back to the
 * carriage just before or just after that node. Nothing is layered over the
 * carriage except the object being lifted: content over the scene is what made
 * Chrome draw rectangular faults (docs/09, F-006).
 */

/** Spans on the progress axis, in wheel pixels. The first approach starts at
 *  0: the camera answers the very first turn of the wheel, or a visitor takes
 *  the carriage for a still that can only be clicked */
const APPROACH = 600;
const RETREAT = 500;
/** Progress below which the carriage still counts as the hub: clicks and focus */
const AT_HUB = 40;
/** The camera never zooms the carriage further than this (docs/10, Performance) */
const DOLLY_MAX = 2.5;
/** Share of the viewport the reached object fills */
const FILL = 0.62;
/** Seconds for the progress to catch up with input: short, or it lags the hand */
const FOLLOW = 0.06;
/** Each cut: to black, and back from it, in ms */
const FADE = 260;
/** Wheel travel up past the hub that goes back out of the window */
const OUT = 140;
/** Wheel travel past a page's top or bottom that leaves it */
const LEAVE = 160;
/** A click's run to an object, at most */
const TRANSPORT_MAX_MS = 900;

export type Present = 'carry' | 'dolly';

/** Chapter order (docs/10, Open questions 2) */
export const CHAPTERS: { id: string; present: Present }[] = [
  { id: 'about', present: 'carry' },
  { id: 'journey', present: 'carry' },
  { id: 'stack', present: 'carry' },
  { id: 'projects', present: 'dolly' },
];

/** What one frame of the story asks of the camera and the light */
export interface StoryFrame {
  /** 1 at the hub, falling to 0 as an object is approached: pointer focus and parallax scale with it */
  hub: number;
  /** Camera framing to use instead of the hub's, as zoom and the scene point to centre */
  camera: { z: number; cx: number; cy: number } | null;
  /** Dimming of the carriage around the object, and where its light lands */
  dim: number;
  pool: { x: number; y: number; rx: number; ry: number } | null;
}

const clamp = (v: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => t * t * (3 - 2 * t);
const easeOut = (t: number) => 1 - (1 - t) * (1 - t);
const nextFrame = () => new Promise<void>((r) => requestAnimationFrame(() => r()));
const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

export class Story {
  /** Progress on the axis: where input has asked to be, and where the scene is */
  private target = 0;
  private p = 0;
  private readonly nodes: number[] = [];
  private readonly end: number;
  private mode: 'scene' | 'page' = 'scene';
  private busy = false;
  private chapter = -1;
  private leave = 0;
  private transport = 0;
  private touchY: number | null = null;
  private last = performance.now();
  /** True while the carriage is seated (phase hub); scene input is ignored otherwise */
  enabled = false;
  /** Called at each cut, so the scene can stop and start its loop */
  onMode: (mode: 'scene' | 'page') => void = () => {};
  /** Scrolling up past the hub: out of the window again (index.ts) */
  onOut: () => void = () => {};
  private out = 0;

  constructor(private readonly els: SceneEls) {
    let s = 0;
    for (let i = 0; i < CHAPTERS.length; i++) {
      this.nodes.push(s + APPROACH);
      s += APPROACH + RETREAT;
    }
    this.end = s;
    window.addEventListener('wheel', this.onWheel, { passive: true });
    window.addEventListener('touchstart', this.onTouchStart, { passive: true });
    window.addEventListener('touchmove', this.onTouchMove, { passive: true });
    window.addEventListener('keydown', this.onKey);
  }

  /** At the hub: where pointer focus, clicks and the window belong */
  get atHub() {
    return this.mode === 'scene' && !this.busy && this.p < AT_HUB;
  }

  /** Clicking an object at the hub: a time-based run to it, then its page */
  goTo(id: string) {
    const i = CHAPTERS.findIndex((c) => c.id === id);
    if (i < 0 || this.busy || this.mode !== 'scene') return;
    cancelAnimationFrame(this.transport);
    const from = this.p;
    const to = this.nodes[i]! - 1;
    const duration = Math.min(TRANSPORT_MAX_MS, 400 + Math.abs(to - from) * 0.15);
    const t0 = performance.now();
    const step = (now: number) => {
      const t = clamp((now - t0) / duration);
      this.target = this.p = lerp(from, to, ease(t));
      if (t < 1) this.transport = requestAnimationFrame(step);
      else {
        this.transport = 0;
        void this.toPage(i);
      }
    };
    this.transport = requestAnimationFrame(step);
  }

  /** Back to the hub, from anywhere */
  home() {
    if (this.mode === 'page') void this.toScene(0);
    else this.target = 0;
  }

  /** Land on a chapter's page directly, with no cut (a #/id link on load) */
  openNow(id: string) {
    const i = CHAPTERS.findIndex((c) => c.id === id);
    if (i < 0) return;
    this.p = this.target = this.nodes[i]!;
    this.showPage(i);
  }

  // ---- input --------------------------------------------------------------

  private readonly onWheel = (e: WheelEvent) => {
    this.input(e.deltaMode === 1 ? e.deltaY * 32 : e.deltaY);
  };

  private readonly onTouchStart = (e: TouchEvent) => {
    this.touchY = e.touches[0]?.clientY ?? null;
  };

  private readonly onTouchMove = (e: TouchEvent) => {
    const y = e.touches[0]?.clientY;
    if (y == null || this.touchY == null) return;
    this.input((this.touchY - y) * 1.5);
    this.touchY = y;
  };

  private readonly onKey = (e: KeyboardEvent) => {
    if (this.mode === 'page') {
      if (e.key === 'Escape') this.home();
      return;
    }
    if (!this.enabled) return;
    const step = (
      { ArrowDown: 120, PageDown: 400, ArrowUp: -120, PageUp: -400 } as Record<string, number>
    )[e.key];
    if (step) this.input(step);
    if (e.key === 'Escape' && this.p > 0) this.home();
  };

  private input(dy: number) {
    if (this.busy) return;
    if (this.mode === 'page') return this.pageInput(dy);
    if (!this.enabled) return;
    cancelAnimationFrame(this.transport);
    this.transport = 0;
    // pushing up at the hub, with the camera already home, goes back out of the window
    if (dy < 0 && this.target <= 0 && this.p < 1) {
      this.out -= dy;
      if (this.out >= OUT) {
        this.out = 0;
        this.onOut();
      }
      return;
    }
    this.out = 0;
    this.target = clamp(this.target + dy, 0, this.end);
  }

  /** On a page the document scrolls itself; pushing on past its top or bottom leaves it */
  private pageInput(dy: number) {
    const doc = document.documentElement;
    const atTop = window.scrollY <= 0;
    const atBottom = window.scrollY + window.innerHeight >= doc.scrollHeight - 2;
    if ((dy < 0 && atTop) || (dy > 0 && atBottom)) this.leave += dy;
    else this.leave = 0;
    const node = this.nodes[this.chapter]!;
    if (this.leave <= -LEAVE) void this.toScene(node - 2);
    else if (this.leave >= LEAVE) void this.toScene(node + 2);
  }

  // ---- the per-frame story ------------------------------------------------

  /** One frame of the scene, from the progress alone */
  update(hub: Camera): StoryFrame {
    const now = performance.now();
    const dt = Math.min(0.05, (now - this.last) / 1000);
    this.last = now;
    const frame: StoryFrame = { hub: 1, camera: null, dim: 0, pool: null };
    if (this.mode !== 'scene') return frame;

    const prev = this.p;
    if (!this.transport) this.p += (this.target - this.p) * (1 - Math.exp(-dt / FOLLOW));
    // Reaching a node going forward cuts to its page
    if (!this.busy && !this.transport) {
      const i = this.nodes.findIndex((n) => prev < n && this.p >= n);
      if (i >= 0) {
        this.p = this.target = this.nodes[i]!;
        void this.toPage(i);
      }
    }

    // Which object the camera is with, and how far: up to it, then away
    let i = -1;
    let t = 0;
    for (let k = 0; k < this.nodes.length; k++) {
      const n = this.nodes[k]!;
      if (this.p >= n - APPROACH && this.p <= n) [i, t] = [k, (this.p - (n - APPROACH)) / APPROACH];
      else if (this.p > n && this.p <= n + RETREAT) [i, t] = [k, 1 - (this.p - n) / RETREAT];
    }
    // eased out, not in: the first of the wheel moves the camera most
    this.showObject(i, easeOut(clamp(t)), hub, frame);
    return frame;
  }

  /** The camera closes on object i, presence t from 0 (hub) to 1 (reached) */
  private showObject(i: number, t: number, hub: Camera, frame: StoryFrame) {
    const id = i >= 0 && t > 0.001 ? CHAPTERS[i]!.id : null;
    const carried = id && CHAPTERS[i]!.present === 'carry' ? id : null;
    // while carried, the object is gone from where it lay: its sprite hides and
    // the patch of the room without it shows
    for (const el of this.els.pops)
      el.style.opacity = carried && el.dataset.pop === carried ? '0' : '';
    for (const el of this.els.gones)
      el.style.opacity = carried && el.dataset.gone === carried ? '1' : '0';
    const carry = this.els.carry;
    carry.classList.toggle('on', !!carried);
    if (!id) return;

    const h = hotspotByTarget(id)!;
    const box = h.box!;
    const u = unitSize();
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // the camera: from the hub's framing to the object, filling FILL of the frame
    const fit = Math.min((vw * FILL) / (box.w * u), (vh * FILL) / (box.h * u));
    const hubCentre = toScene(vw / 2, vh / 2, { ...hub, px: 0, py: 0 });
    const z = lerp(hub.z, Math.min(fit, DOLLY_MAX), t);
    const cx = lerp(hubCentre.X, box.x + box.w / 2, t);
    const cy = lerp(hubCentre.Y, box.y + box.h / 2, t);
    frame.camera = { z, cx, cy };
    frame.hub = 1 - t;
    frame.dim = t * 0.55;
    frame.pool = { ...h.light };
    if (!carried) return;

    // a portable object also lifts toward the lens as the camera arrives
    if (carry.dataset.id !== id) {
      carry.dataset.id = id;
      carry.style.backgroundImage = `url(${h.sprite})`;
      carry.style.width = `${box.w * u}px`;
      carry.style.height = `${box.h * u}px`;
    }
    const lift = t * 0.12;
    const sx = vw / 2 + (box.x + box.w / 2 - cx) * u * z;
    const sy = vh / 2 + (box.y + box.h / 2 - cy) * u * z - lift * box.h * u * z;
    carry.style.transform = `translate3d(${(sx - (box.w * u) / 2).toFixed(1)}px,${(sy - (box.h * u) / 2).toFixed(1)}px,0) scale(${(z * (1 + lift)).toFixed(4)})`;
  }

  /** Size the carried element again after a resize */
  layout() {
    delete this.els.carry.dataset.id;
  }

  // ---- the cuts -----------------------------------------------------------

  private async toPage(i: number) {
    if (this.busy) return;
    this.busy = true;
    await this.fade(this.els.stage, 0);
    this.showPage(i);
    this.els.page.style.opacity = '0';
    await nextFrame();
    await this.fade(this.els.page, 1);
    this.busy = false;
  }

  private showPage(i: number) {
    this.chapter = i;
    this.mode = 'page';
    this.leave = 0;
    this.onMode('page');
    this.els.page.innerHTML = renderPage(i);
    this.els.page.hidden = false;
    this.els.stage.hidden = true;
    document.documentElement.classList.add('reading');
    window.scrollTo(0, 0);
    history.replaceState(null, '', `#/${CHAPTERS[i]!.id}`);
  }

  private async toScene(p: number) {
    if (this.busy) return;
    this.busy = true;
    await this.fade(this.els.page, 0);
    this.els.page.hidden = true;
    document.documentElement.classList.remove('reading');
    window.scrollTo(0, 0);
    this.p = this.target = p;
    this.mode = 'scene';
    this.els.stage.style.opacity = '0';
    this.els.stage.hidden = false;
    this.onMode('scene');
    history.replaceState(null, '', '#/');
    // let the carriage draw twice behind black before it is shown
    await nextFrame();
    await nextFrame();
    await this.fade(this.els.stage, 1);
    this.busy = false;
  }

  private async fade(el: HTMLElement, to: number) {
    el.style.transition = `opacity ${FADE}ms ease`;
    el.style.opacity = String(to);
    await wait(FADE);
    el.style.transition = '';
    if (to === 1) el.style.opacity = '';
  }

  dispose() {
    window.removeEventListener('wheel', this.onWheel);
    window.removeEventListener('touchstart', this.onTouchStart);
    window.removeEventListener('touchmove', this.onTouchMove);
    window.removeEventListener('keydown', this.onKey);
    cancelAnimationFrame(this.transport);
  }
}

/** A chapter's page: plain document content, with the ways back and on */
function renderPage(i: number): string {
  const ch = CHAPTERS[i]!;
  const sec = sectionById(ch.id);
  const next = CHAPTERS[i + 1] ? sectionById(CHAPTERS[i + 1]!.id) : null;
  const blocks = (sec?.blocks ?? []).map((b) => `<p class="page__block">${b}</p>`).join('');
  return `<article class="page__in">
    <p class="page__hint">↑ 向上滚动，回到车厢</p>
    <span class="page__kicker">${ch.id.toUpperCase()}</span>
    <h1>${sec?.title ?? ch.id}</h1>
    <p class="page__lede">${sec?.lede ?? ''}</p>
    ${blocks}
    <p class="page__hint page__hint--end">↓ 继续向下${next ? `：${next.title}` : '，回到车厢'}</p>
  </article>`;
}
