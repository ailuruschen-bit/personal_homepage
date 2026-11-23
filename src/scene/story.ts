import type { SceneEls } from './dom';
import { hotspotByTarget } from './hotspots';
import { toScene, unitSize, type Camera } from './units';
import { sectionById } from '../content/sections';
import { nudge, objectLines } from '../content/lines';

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
/** Hub weight above which the scene counts as at the hub (focus.ts uses the same) */
export const SEATED = 0.8;
/** The camera never zooms the carriage further than this (docs/10, Performance) */
const DOLLY_MAX = 2.5;
/** Share of the viewport the reached object fills */
const FILL = 0.62;
/** Seconds for the progress to catch up with input: short, or it lags the hand */
const FOLLOW = 0.06;
/** Each cut: to black, and back from it, in ms */
const FADE = 260;
/** Typing speed of the caption's line, ms per character */
const CHAR_MS = 28;
/** At the hub with nothing moving this long, the nudge shows, in ms */
const NUDGE_AFTER = 1800;
/** Wheel travel up past the hub that goes back out of the window */
const OUT = 100;
/** A pause in wheel input longer than this starts a new gesture, in ms */
const GESTURE_GAP = 120;
/** ...or the input speeding up by this factor, from at least RISE_MIN */
const RISE = 2;
const RISE_MIN = 6;
/** Wheel travel past a page's top or bottom that leaves it: barely any, so
 *  the scroll that reaches the end carries straight on to the carriage */
const LEAVE = 24;
/** A click plays the approach on its own: this long, in ms... */
const PLAY_MS = 1600;
/** ...then holds on the object this long once its line is typed out, in ms */
const PLAY_READ = 150;
/** Back from a page, the camera glides off the object to the hub this long, in ms */
const GLIDE_MS = 900;
/** After a cut, how long a swipe that keeps going is still ignored, in ms.
 *  Longer onto a page, where the rest of a swipe could run a short page out at
 *  its far end; short back on the carriage, where the hub stop catches it anyway */
const BRAKE_PAGE = 700;
const BRAKE_SCENE = 150;
/** Dots on each stretch of the route between two stops */
const RAIL = 3;

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
const easeOut = (t: number) => 1 - (1 - t) * (1 - t);
const easeInOut = (t: number) => (t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t));
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
  private touchY: number | null = null;
  private last = performance.now();
  /** True while the carriage is seated (phase hub); scene input is ignored otherwise */
  enabled = false;
  /** Called at each cut, so the scene can stop and start its loop */
  onMode: (mode: 'scene' | 'page') => void = () => {};
  /** Whether the pointer has an object in focus at the hub (index.ts) */
  focused: () => boolean = () => false;
  /** Scrolling up past the hub: out of the window again (index.ts) */
  onOut: () => void = () => {};
  private out = 0;
  /** Going out takes a fresh gesture, or a moment, once the camera is home */
  private armed = true;
  private lastInput = 0;
  private quietSince = performance.now();
  private talkKey = '';
  private talkLine = '';
  private typed = -1;
  private typeStart = 0;
  private lineEl: HTMLElement | null = null;
  private routeKey = '';
  private brakeSince = 0;
  /** Back from a page: the camera easing off the object to the hub by itself */
  private glide: { from: number; to: number; start: number } | null = null;
  /** A clicked object's approach, playing by itself (play) */
  private playing: { i: number; from: number; start: number; read: number } | null = null;
  private edgeArmed = false;
  private lastMag = 0;
  private brakeHold = BRAKE_PAGE;
  private stopSince = 0;
  /** The hub between chapters: where each retreat ends and the next approach starts */
  private readonly stops: number[] = [];
  private hintEl: HTMLElement | null = null;

  constructor(private readonly els: SceneEls) {
    let s = 0;
    for (let i = 0; i < CHAPTERS.length; i++) {
      this.nodes.push(s + APPROACH);
      s += APPROACH + RETREAT;
    }
    this.end = s;
    this.stops = this.nodes.slice(0, -1).map((n) => n + RETREAT);
    window.addEventListener('wheel', this.onWheel, { passive: true });
    window.addEventListener('touchstart', this.onTouchStart, { passive: true });
    window.addEventListener('touchmove', this.onTouchMove, { passive: true });
    window.addEventListener('keydown', this.onKey);
    this.els.route.innerHTML = renderRoute();
    this.els.route.addEventListener('click', this.onRoute);
    this.els.page.addEventListener('click', this.onPageClick);
  }

  /** At the hub: where pointer focus, clicks and the window belong */
  get atHub() {
    return this.mode === 'scene' && !this.busy && !this.playing && !this.glide && this.seated;
  }

  /** A clicked object's approach is playing: the pointer picks nothing meanwhile */
  get isPlaying() {
    return this.playing !== null;
  }

  /**
   * Clicking an object at the hub: its approach plays by itself at an even
   * pace, the line is typed out in full, then the cut to its page. It starts
   * from the hub framing at the head of that object's own approach, so no
   * other object's approach or retreat plays on the way.
   */
  play(id: string) {
    const i = CHAPTERS.findIndex((c) => c.id === id);
    if (i < 0 || this.busy || this.mode !== 'scene' || this.playing) return;
    const from = this.nodes[i]! - APPROACH;
    this.p = this.target = from;
    this.stopSince = 0;
    this.playing = { i, from, start: performance.now(), read: 0 };
  }
  /** The camera is back at the hub framing: at the start, or between two
   *  chapters. Pointer focus and clicks share this, so whatever lights up
   *  under the pointer also answers a click */
  private seated = true;

  /** Clicking an object at the hub: straight to its page through black */
  goTo(id: string) {
    const i = CHAPTERS.findIndex((c) => c.id === id);
    if (i < 0 || this.busy || this.mode !== 'scene') return;
    this.p = this.target = this.nodes[i]!;
    void this.toPage(i);
  }

  /** Back to the very start of the story at once, with no move: for leaving
   *  through the window, which is clicked only from a hub framing, the same
   *  at every stop, so the jump does not show */
  reset() {
    if (this.mode !== 'scene' || this.busy) return;
    this.p = this.target = 0;
    this.stopSince = 0;
    this.playing = null;
    this.glide = null;
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

  /** A stop on the route: the carriage, or a chapter's page through black */
  private readonly onRoute = (e: MouseEvent) => {
    const el = (e.target as HTMLElement).closest<HTMLElement>('[data-stop]');
    if (!el || this.busy) return;
    const k = Number(el.dataset.stop);
    if (k < 0) return this.home();
    if (this.mode === 'scene') return this.goTo(CHAPTERS[k]!.id);
    if (k === this.chapter) window.scrollTo({ top: 0, behavior: 'smooth' });
    else void this.toOtherPage(k);
  };

  /** The page's own way back: to the carriage at the very start, unlike
   *  scrolling out, which keeps the place in the story */
  private readonly onPageClick = (e: MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-home]') && !this.busy) this.home();
  };

  private async toOtherPage(i: number) {
    this.busy = true;
    await this.fade(this.els.page, 0);
    this.p = this.target = this.nodes[i]!;
    this.showPage(i);
    await nextFrame();
    await this.fade(this.els.page, 1);
    this.busy = false;
    this.brakeSince = performance.now();
    this.brakeHold = BRAKE_PAGE;
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
    const now = performance.now();
    this.quietSince = now;
    // Gestures are timed through the cuts too, so the inertia of the swipe
    // that made a cut is still known as the same gesture on the far side
    // A new gesture: a pause in the input, or a swipe speeding up again where
    // inertia only ever slows (a trackpad swipe begun while the last one's
    // inertia still trickles in). Nothing else counts, however long the
    // inertia runs: it never triggers anything on its own
    const mag = Math.abs(dy);
    const fresh =
      now - this.lastInput > GESTURE_GAP || (mag > RISE_MIN && mag > this.lastMag * RISE);
    this.lastInput = now;
    this.lastMag = mag;
    if (this.busy || this.playing || this.glide) return;
    // The brake after every cut: the rest of the swipe that made it is
    // dropped, until a new gesture starts or it has run on for the hold,
    // so one fast swipe never carries through several chapters
    if (this.brakeSince) {
      if (fresh || now - this.brakeSince > this.brakeHold) this.brakeSince = 0;
      else return;
    }
    if (this.mode === 'page') return this.pageInput(dy, fresh);
    if (!this.enabled) return;
    // Pushing up at the hub goes back out of the window, but only in a new
    // gesture begun once the camera is home: the scroll that brought it home,
    // and its inertia, stop there (a pause between paragraphs)
    const home = this.target <= 0 && this.p < 1;
    if (!home) this.armed = false;
    else if (fresh) this.armed = true;
    if (dy < 0 && home) {
      if (!this.armed) return;
      this.out -= dy;
      if (this.out >= OUT) {
        this.out = 0;
        this.onOut();
      }
      return;
    }
    this.out = 0;
    // A stop at the hub between two chapters: the camera all the way back on
    // the carriage, with time to look around or click before the next object.
    // Only a new gesture leaves it: however long a swipe and its inertia run
    // on, they end here
    if (this.stopSince) {
      if (fresh) this.stopSince = 0;
      else return;
    }
    const next = clamp(this.target + dy, 0, this.end);
    const stop = this.stops.find(
      (h) => (this.target < h && next > h) || (this.target > h && next < h),
    );
    if (stop !== undefined) {
      this.target = stop;
      this.stopSince = now;
    } else this.target = next;
  }

  /** On a page the document scrolls itself; pushing on past its top or bottom leaves it */
  private pageInput(dy: number, fresh: boolean) {
    const doc = document.documentElement;
    const atTop = window.scrollY <= 0;
    const atBottom = window.scrollY + window.innerHeight >= doc.scrollHeight - 2;
    const pushing = (dy < 0 && atTop) || (dy > 0 && atBottom);
    // The scroll that reaches an end stops there: the page rests on it. Only
    // a gesture begun at the end, pushing on, leaves for the carriage
    if (!pushing) {
      this.edgeArmed = false;
      this.leave = 0;
      return;
    }
    if (fresh) this.edgeArmed = true;
    if (!this.edgeArmed) return;
    this.leave += dy;
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
    // Nor is it quiet while the carriage is not yet the visitor's: the opening,
    // the view outside, a page, a cut. The wait starts when the hub is theirs
    if (!this.enabled || this.mode !== 'scene' || this.busy) this.quietSince = now;
    if (this.mode !== 'scene') return frame;

    const play = this.playing;
    const glide = this.glide;
    if (glide) {
      const k = clamp((now - glide.start) / GLIDE_MS);
      this.p = this.target = lerp(glide.from, glide.to, easeInOut(k));
      if (k >= 1) {
        this.glide = null;
        // resting at the hub: the swipe that left the page goes no further
        this.stopSince = now;
      }
    } else if (play) {
      // the clicked object's approach, on its own clock; it stops just short
      // of the node until the line is read, then the cut
      const n = this.nodes[play.i]!;
      const k = clamp((now - play.start) / PLAY_MS);
      this.p = this.target = lerp(play.from, n - 0.5, easeInOut(k));
      if (
        k >= 1 &&
        !play.read &&
        this.talkKey.endsWith(':in') &&
        this.typed >= this.talkLine.length
      )
        play.read = now;
      if (play.read && now - play.read > PLAY_READ) {
        this.playing = null;
        this.p = this.target = n;
        void this.toPage(play.i);
      }
    } else {
      const prev = this.p;
      this.p += (this.target - this.p) * (1 - Math.exp(-dt / FOLLOW));
      // Reaching a node cuts to its page, either way: going back up, the page
      // opens at its end, as if read back up to it
      if (!this.busy) {
        const fwd = this.nodes.findIndex((n) => prev < n && this.p >= n);
        const back = this.nodes.findIndex((n) => prev > n && this.p <= n);
        const i = fwd >= 0 ? fwd : back;
        if (i >= 0) {
          this.p = this.target = this.nodes[i]!;
          void this.toPage(i, fwd < 0);
        }
      }
    }

    // The nudge waits for a quiet spell: no scroll, and no object in focus.
    // Focus counts as activity, so the wait starts again when it is lost
    if (this.focused() || this.playing || this.glide) this.quietSince = now;

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
    this.seated = frame.hub > SEATED;
    this.showLines(i, clamp(t), i >= 0 && this.p > this.nodes[i]!, now);
    this.showRoute();
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

  /** The detective's line on the way to an object, in the focus caption that
   *  names objects at the hub. On the way in: the object's name, his first
   *  look typed out under it, then a prompt naming the page ahead; on the way
   *  out: his last word on it. At the hub, after a while and with nothing in
   *  focus, the nudge. The caption only ever changes its text and its `on`
   *  class: anything painted over the carriage made Chrome fault (docs/09). */
  /**
   * The route: the carriage, then each chapter as a stop, with dots between
   * that fill as the progress runs from one stop to the next. Text only, its
   * classes changed only when the state does (docs/09, F-007).
   */
  private showRoute() {
    const page = this.mode === 'page';
    const visible = page || this.enabled;
    const stops: string[] = [];
    const rails: number[] = [];
    let next = true;
    stops.push(page || this.p >= 1 ? 'done' : 'here');
    for (let k = 0; k < this.nodes.length; k++) {
      const from = k ? this.nodes[k - 1]! : 0;
      const to = this.nodes[k]!;
      if (page) {
        rails.push(k <= this.chapter ? RAIL : 0);
        stops.push(k < this.chapter ? 'done' : k === this.chapter ? 'here' : '');
      } else {
        rails.push(Math.floor(clamp((this.p - from) / (to - from)) * RAIL + 0.001));
        // Reaching a node holds the progress on it through the cut: that stop
        // is where the visitor is arriving, not one passed with the next lit
        const arriving = this.p >= to && this.p < to + 1;
        const done = this.p >= to;
        stops.push(arriving ? 'here' : done ? 'done' : next ? 'next' : '');
        if (!done || arriving) next = false;
      }
    }
    const key = `${visible}|${stops.join()}|${rails.join()}`;
    if (key === this.routeKey) return;
    this.routeKey = key;
    const route = this.els.route;
    route.classList.toggle('on', visible);
    route.querySelectorAll<HTMLElement>('[data-stop]').forEach((el, n) => {
      el.className = `route__stop ${stops[n] ?? ''}`;
    });
    route.querySelectorAll<HTMLElement>('.route__rail').forEach((el, n) => {
      el.querySelectorAll('b').forEach((b, d) => b.classList.toggle('lit', d < rails[n]!));
    });
  }

  private showLines(i: number, t: number, leaving: boolean, now: number) {
    let key = '';
    let title = '';
    let line = '';
    let hint = '';
    if (i >= 0 && t > 0.2 && !this.glide) {
      const id = CHAPTERS[i]!.id;
      const l = objectLines[id];
      if (l && !leaving) {
        key = `${id}:in`;
        title = l.name;
        line = l.open;
        // not in a click's approach, nor in the cut that follows any approach
        if (t > 0.7 && !this.playing && !this.busy)
          hint = `继续下滑 ▼ 翻开${sectionById(id)?.title ?? ''}`;
      } else if (l && t > 0.5) {
        key = `${id}:out`;
        line = l.close;
      }
    } else if (
      this.enabled &&
      !this.playing &&
      !this.glide &&
      !this.focused() &&
      now - this.quietSince > NUDGE_AFTER
    ) {
      key = 'nudge';
      line = nudge.line;
      hint = nudge.hint;
    }
    const cap = this.els.cap;
    if (!key) {
      if (this.talkKey) {
        this.talkKey = '';
        // the pointer may have taken the caption for an object meanwhile
        if (!this.focused()) cap.classList.remove('on');
      }
      return;
    }
    // the caption's own elements, rebuilt if anything else wrote the caption since
    if (key !== this.talkKey || !this.lineEl?.isConnected || !this.hintEl?.isConnected) {
      this.talkKey = key;
      this.talkLine = line;
      this.typed = -1;
      this.typeStart = now;
      const lineEl = document.createElement('small');
      lineEl.className = 'cap__line';
      const hintEl = document.createElement('small');
      hintEl.className = 'cap__hint';
      cap.replaceChildren(title, lineEl, hintEl);
      cap.classList.add('on');
      this.lineEl = lineEl;
      this.hintEl = hintEl;
    }
    const lineEl = this.lineEl!;
    const hintEl = this.hintEl!;
    const n = Math.min(this.talkLine.length, Math.floor((now - this.typeStart) / CHAR_MS));
    if (n !== this.typed) {
      this.typed = n;
      lineEl.textContent = this.talkLine.slice(0, n) + (n < this.talkLine.length ? '▍' : '');
    }
    const h = n >= this.talkLine.length ? hint : '';
    if (hintEl.textContent !== h) hintEl.textContent = h;
  }

  /** Size the carried element again after a resize */
  layout() {
    delete this.els.carry.dataset.id;
  }

  // ---- the cuts -----------------------------------------------------------

  private async toPage(i: number, atEnd = false) {
    if (this.busy) return;
    this.busy = true;
    await this.fade(this.els.stage, 0);
    this.showPage(i);
    if (atEnd) window.scrollTo(0, document.documentElement.scrollHeight);
    this.els.page.style.opacity = '0';
    await nextFrame();
    await this.fade(this.els.page, 1);
    this.busy = false;
    this.brakeSince = performance.now();
    this.brakeHold = BRAKE_PAGE;
  }

  private showPage(i: number) {
    this.chapter = i;
    this.mode = 'page';
    this.leave = 0;
    this.edgeArmed = false;
    this.onMode('page');
    this.els.page.innerHTML = renderPage(i);
    this.els.page.hidden = false;
    this.els.stage.hidden = true;
    document.documentElement.classList.add('reading');
    window.scrollTo(0, 0);
    history.replaceState(null, '', `#/${CHAPTERS[i]!.id}`);
    this.showRoute();
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
    // Back to the hub on its own, already moving as the black lifts, so the
    // camera never rests on the object: past the node, to the stop after it;
    // before it, to where this object's approach began
    const node = this.nodes[this.chapter];
    if (node !== undefined && p !== 0) {
      const to = p > node ? Math.min(node + RETREAT, this.end) : node - APPROACH;
      this.glide = { from: p, to, start: performance.now() };
    }
    // let the carriage draw twice behind black before it is shown
    await nextFrame();
    await nextFrame();
    await this.fade(this.els.stage, 1);
    this.busy = false;
    this.brakeSince = performance.now();
    this.brakeHold = BRAKE_SCENE;
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
    this.els.route.removeEventListener('click', this.onRoute);
    this.els.page.removeEventListener('click', this.onPageClick);
  }
}

/** The route's markup: the carriage and the chapters as stops, rails between */
function renderRoute(): string {
  const stop = (k: number, label: string) =>
    `<button class="route__stop" type="button" data-stop="${k}"><i></i><span>${label}</span></button>`;
  const rail = `<span class="route__rail" aria-hidden="true">${'<b>·</b>'.repeat(RAIL)}</span>`;
  return [
    stop(-1, '车厢'),
    ...CHAPTERS.map((c, k) => rail + stop(k, sectionById(c.id)?.title ?? c.id)),
  ].join('');
}

/** A chapter's page: plain document content, with the ways back and on */
function renderPage(i: number): string {
  const ch = CHAPTERS[i]!;
  const sec = sectionById(ch.id);
  const next = CHAPTERS[i + 1] ? sectionById(CHAPTERS[i + 1]!.id) : null;
  const blocks = (sec?.blocks ?? []).map((b) => `<p class="page__block">${b}</p>`).join('');
  return `<article class="page__in">
    <div class="page__top">
      <button class="page__home" type="button" data-home>← 回到车厢</button>
      <p class="page__hint">↑ 向上滚动，回到车厢</p>
    </div>
    <span class="page__kicker">${objectLines[ch.id]?.name ?? ''} · ${ch.id.toUpperCase()}</span>
    <h1>${sec?.title ?? ch.id}</h1>
    <p class="page__lede">${sec?.lede ?? ''}</p>
    ${blocks}
    <p class="page__hint page__hint--end">↓ 继续向下${next ? `：${next.title}` : '，回到车厢'}</p>
  </article>`;
}
