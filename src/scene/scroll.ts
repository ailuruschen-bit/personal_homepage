import type { SceneEls } from './dom';
import { hotspotByTarget } from './hotspots';
import { toScreen, toScene, unitSize, type Camera } from './units';
import { without } from './probe';

/**
 * The scroll story, docs/10: the scroll offset is the only clock once the
 * visitor is seated. This is the skeleton: the hub and four chapters on one
 * axis, carry and dolly, the content panel, and the transport. The cover, the
 * porches and the window transits on the same axis come later.
 *
 * Every visual here is a pure function of `s`, the scroll offset, evaluated
 * once per frame from the focus engine's loop. Nothing here starts an
 * animation of its own except the transport, which is a locked segment that
 * any scroll input cancels.
 */

/** Spans in scroll pixels (docs/10, Chapter spans) */
const HUB = 420;
const APPROACH = 560;
const OPEN = 420;
const READ_MIN = 600;
const CLOSE = 360;
/** Content fades in over the end of the open beat, from this fraction */
const CONTENT_FROM = 0.55;
/** Share of the viewport the opened aperture fills */
const FILL = 0.86;
/** The dolly never zooms the carriage further than this (docs/10, Performance) */
const DOLLY_MAX = 2.5;
/** The transport's longest run */
const TRANSPORT_MAX_MS = 800;

export type Present = 'carry' | 'dolly';

export interface ChapterDef {
  /** Section id, and the hotspot it opens from */
  id: string;
  present: Present;
}

/** Chapter order (docs/10, Open questions 2) */
export const CHAPTERS: ChapterDef[] = [
  { id: 'about', present: 'carry' },
  { id: 'journey', present: 'carry' },
  { id: 'stack', present: 'carry' },
  { id: 'projects', present: 'dolly' },
];

interface Span {
  def: ChapterDef;
  start: number;
  read: number;
  end: number;
  panel: HTMLElement;
  inner: HTMLElement;
  /** How far the panel's text has to travel during the read, measured in layout() */
  overflow: number;
}

/** What one frame of the story asks of the camera and the light */
export interface StoryFrame {
  /** 1 at the hub, falling to 0 as a chapter is approached: pointer focus and parallax scale with it */
  hub: number;
  /** Camera framing to use instead of the hub's, as zoom and the scene point to centre */
  camera: { z: number; cx: number; cy: number } | null;
  /** Dimming of the carriage around the open object, and where its light lands */
  dim: number;
  pool: { x: number; y: number; rx: number; ry: number } | null;
}

/** A stand-in panel outside the document, when panels are left out (probe.ts) */
function detachedPanel(): HTMLElement {
  const el = document.createElement('section');
  el.append(document.createElement('div'));
  return el;
}

const clamp = (v: number, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => t * t * (3 - 2 * t);
const range = (s: number, a: number, b: number) => clamp((s - a) / (b - a));

export class ScrollStory {
  private spans: Span[] = [];
  private total = 0;
  private enabled = false;
  private transport = 0;
  private active: Span | null = null;
  private lastHash = '';
  private readonly cancelTransport = () => this.stopTransport();

  constructor(
    private readonly els: SceneEls,
    private readonly track: HTMLElement,
  ) {
    for (const def of CHAPTERS) {
      const panel =
        els.stage.querySelector<HTMLElement>(`.panel[data-ch="${def.id}"]`) ?? detachedPanel();
      this.spans.push({
        def,
        start: 0,
        read: 0,
        end: 0,
        panel,
        inner: panel.firstElementChild as HTMLElement,
        overflow: 0,
      });
    }
    this.layout();
  }

  /** Recompute the segment map; call on resize and when content changes.
   *  All layout is read here, never in the per-frame path. */
  layout() {
    let s = HUB;
    const vh = window.innerHeight;
    for (const sp of this.spans) {
      sp.overflow = Math.max(0, sp.inner.scrollHeight - sp.panel.clientHeight);
      sp.read = sp.overflow + READ_MIN;
      sp.start = s;
      sp.end = s + APPROACH + OPEN + sp.read + CLOSE;
      s = sp.end;
    }
    this.total = s;
    this.track.style.height = `${Math.round(this.total + vh)}px`;
    this.sizeCarry();
  }

  /** The carried object's element is sized once per chapter and resize; frames only transform it */
  private sizeCarry() {
    const sp = this.active;
    if (!sp || sp.def.present !== 'carry') return;
    const box = hotspotByTarget(sp.def.id)!.box!;
    const u = unitSize();
    this.els.carry.style.width = `${box.w * u}px`;
    this.els.carry.style.height = `${box.h * u}px`;
  }

  /** The scroll offset at which a chapter is open and ready to read */
  readStart(id: string): number {
    const sp = this.spans.find((x) => x.def.id === id);
    return sp ? sp.start + APPROACH + OPEN : 0;
  }

  /** Seated: the document scrolls. Anywhere else the page is held at the top. */
  setEnabled(on: boolean) {
    if (without('story')) return;
    if (on === this.enabled) return;
    this.enabled = on;
    document.documentElement.classList.toggle('story', on);
    if (!on) {
      this.stopTransport();
      window.scrollTo(0, 0);
    }
  }

  get offset() {
    return this.enabled ? window.scrollY : 0;
  }

  /** Clicking an object: a time-based run to its read start, cancelled by any scroll input */
  transportTo(target: number) {
    this.stopTransport();
    const from = window.scrollY;
    const dist = Math.abs(target - from);
    if (dist < 1) return;
    const duration = Math.min(TRANSPORT_MAX_MS, 300 + dist * 0.08);
    const t0 = performance.now();
    for (const ev of ['wheel', 'touchstart', 'keydown'] as const)
      window.addEventListener(ev, this.cancelTransport, { passive: true, once: true });
    const step = (now: number) => {
      const t = clamp((now - t0) / duration);
      window.scrollTo(0, Math.round(lerp(from, target, ease(t))));
      this.transport = t < 1 ? requestAnimationFrame(step) : 0;
      if (!this.transport) this.removeCancel();
    };
    this.transport = requestAnimationFrame(step);
  }

  private stopTransport() {
    cancelAnimationFrame(this.transport);
    this.transport = 0;
    this.removeCancel();
  }

  private removeCancel() {
    for (const ev of ['wheel', 'touchstart', 'keydown'] as const)
      window.removeEventListener(ev, this.cancelTransport);
  }

  /** One frame: everything the story drives, from the scroll offset alone */
  update(hubCamera: Camera): StoryFrame {
    const s = this.offset;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const frame: StoryFrame = { hub: 1, camera: null, dim: 0, pool: null };

    const sp = this.spans.find((x) => s >= x.start && s < x.end) ?? null;
    if (sp !== this.active) this.activate(sp);
    if (!sp) {
      frame.hub = 1 - range(s, HUB * 0.5, HUB);
      return frame;
    }

    const a = range(s, sp.start, sp.start + APPROACH);
    const o = range(s, sp.start + APPROACH, sp.start + APPROACH + OPEN);
    const r = range(s, sp.start + APPROACH + OPEN, sp.start + APPROACH + OPEN + sp.read);
    const c = range(s, sp.end - CLOSE, sp.end);
    // presence: 0 at rest on the table, 1 fully presented; the close runs it back
    const presence = ease(a) * (1 - ease(c));
    const opened = o * (1 - c);
    const content = range(opened, CONTENT_FROM, 1) * (1 - range(c, 0, 0.45));

    const h = hotspotByTarget(sp.def.id)!;
    const box = h.box!;
    const u = unitSize();
    // the rectangle the open object fills, in screen pixels
    const fit = Math.min((vw * 0.62) / (box.w * u), (vh * 0.7) / (box.h * u));

    frame.hub = 1 - presence;
    if (sp.def.present === 'carry') {
      const rest = toScreen(box.x + box.w / 2, box.y + box.h / 2, hubCamera);
      const restScale = hubCamera.z;
      const k = lerp(restScale, fit * FILL, presence);
      const x = lerp(rest.x, vw / 2, ease(presence));
      const y = lerp(rest.y, vh / 2, ease(presence));
      const el = this.els.carry;
      el.style.transform = `translate3d(${(x - (box.w * u) / 2).toFixed(1)}px,${(y - (box.h * u) / 2).toFixed(1)}px,0) scale(${k.toFixed(4)})`;
      el.style.opacity = presence > 0.001 ? '1' : '0';
      frame.dim = presence;
      const centre = toScene(vw / 2, vh / 2, hubCamera);
      frame.pool = {
        x: lerp(h.light.x, centre.X, presence),
        y: lerp(h.light.y, centre.Y, presence),
        rx: lerp(h.light.rx, (box.w * fit) / hubCamera.z, presence),
        ry: lerp(h.light.ry, (box.h * fit) / hubCamera.z, presence),
      };
    } else {
      const z = lerp(hubCamera.z, Math.min(fit * FILL * hubCamera.z, DOLLY_MAX), ease(presence));
      const hubCentre = toScene(vw / 2, vh / 2, { ...hubCamera, px: 0, py: 0 });
      frame.camera = {
        z,
        cx: lerp(hubCentre.X, box.x + box.w / 2, ease(presence)),
        cy: lerp(hubCentre.Y, box.y + box.h / 2, ease(presence)),
      };
      frame.dim = presence * 0.6;
      frame.pool = { ...h.light };
    }
    // while carried, the object is gone from where it lay: its sprite hides and
    // the patch of the room without it shows
    const away = sp.def.present === 'carry' && presence > 0.001;
    for (const el of this.els.pops)
      el.style.opacity = away && el.dataset.pop === sp.def.id ? '0' : '';
    for (const el of this.els.gones)
      el.style.opacity = away && el.dataset.gone === sp.def.id ? '1' : '0';

    // the panel: fades in late in the open beat; its text moves through the read beat
    sp.panel.style.opacity = content.toFixed(3);
    sp.panel.classList.toggle('on', content > 0.02);
    sp.inner.style.transform = `translate3d(0,${(-r * sp.overflow).toFixed(1)}px,0)`;

    const hash = content > 0.5 ? `#/${sp.def.id}` : '#/';
    if (hash !== this.lastHash) {
      this.lastHash = hash;
      history.replaceState(null, '', hash);
    }
    return frame;
  }

  private activate(sp: Span | null) {
    if (this.active) {
      this.active.panel.style.opacity = '0';
      this.active.panel.classList.remove('on');
    }
    this.active = sp;
    const el = this.els.carry;
    if (sp && sp.def.present === 'carry') {
      el.style.backgroundImage = `url(${hotspotByTarget(sp.def.id)!.sprite})`;
      this.sizeCarry();
    } else {
      el.style.opacity = '0';
      for (const p of this.els.pops) p.style.opacity = '';
      for (const p of this.els.gones) p.style.opacity = '0';
    }
    if (!sp && this.lastHash !== '#/') {
      this.lastHash = '#/';
      history.replaceState(null, '', '#/');
    }
  }

  dispose() {
    this.stopTransport();
    this.setEnabled(false);
  }
}
