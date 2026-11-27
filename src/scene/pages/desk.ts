import { nextSilhouette } from './lineside';
/**
 * The table under the papers, lit by what lights the compartment (docs/13):
 * the magenta tube on the left wall, the lamp on the right, the window's
 * slatted city light from the far side, and the dark toward the reader.
 *
 * The pointer is a fountain pen held as if writing, its nib on the table
 * where the pointer is and its barrel rising toward the reader's right. Each
 * light casts its shadow, worked out from where the light is: every point of
 * the pen projected from the light onto the table. So the shadows meet the
 * nib sharp, lengthen and soften up the barrel, point away from each light,
 * are darker near strong lights and take the tint of what each light adds.
 */

interface Light {
  /** position, as a fraction of the viewport; off screen is fine */
  x: number;
  y: number;
  /** height above the table, px at a 900px-high viewport (scaled with it) */
  height: number;
  /** how bright it is where the pen is, before falloff */
  power: number;
  /** its breadth, px: the penumbra grows with it */
  size: number;
  /** the shadow's colour: what is left when this light is blocked */
  shade: [number, number, number];
}

const LIGHTS: Light[] = [
  // the lamp: small and near, the sharpest and darkest shadow, cool
  { x: 0.9, y: 0.24, height: 950, power: 0.62, size: 40, shade: [40, 52, 78] },
  // the tube: tall and low on the left wall, a softer one to the right, green-grey
  { x: -0.05, y: 0.42, height: 1300, power: 0.42, size: 190, shade: [48, 70, 58] },
  // the window: broad and far, a faint, long, very soft one, warm
  { x: 0.5, y: -0.45, height: 2400, power: 0.14, size: 520, shade: [80, 62, 40] },
];

/**
 * What the pointer is on the table. 'cursor': the ordinary pointer, hovering
 * a little above the papers, its arrow's shadow cast from each light. 'pen':
 * a fountain pen drawn in its place, nib on the table (kept for trying again).
 */
const MODE = 'cursor' as 'cursor' | 'pen';

/** The arrow pointer's outline, tip at the origin, px (the usual system arrow) */
const ARROW: [number, number][] = [
  [0, 0],
  [0, 16.5],
  [4.1, 12.7],
  [6.9, 19],
  [9.3, 18],
  [6.6, 11.8],
  [11.6, 11.8],
];
/** The light the pointer's shadow is cast from: the tube, a touch darker
 *  than its share of the pen's, being the only one */
const ARROW_LIGHT: Light = { ...LIGHTS[1]!, power: 0.55 };
/** How far above the table the pointer seems to hover, px at a 900px-high viewport */
const HOVER = 38;

/** The pen: its length, how steeply it is held, and which way its barrel
 *  points from the nib (radians, screen axes: toward the lower right) */
const PEN_LEN = 142;
const ELEVATION = (67 * Math.PI) / 180;
const AZIMUTH = (54 * Math.PI) / 180;
/** Its half-width along its length, from the nib: [distance, half-width] */
const PROFILE: [number, number][] = [
  [0, 0.3],
  [5, 1.5],
  [13, 3.4],
  [16, 4.1],
  [32, 4.7],
  [34, 5.1],
  [104, 5.2],
  [106, 5.9],
  [138, 5.9],
  [142, 3.4],
];

/**
 * The pen as drawn, seen from above: a black lacquer pen with a two-tone nib,
 * gold furniture and its cap posted on the end. Authored along +x in the
 * pen's own length (0 at the nib) and squeezed by the foreshortening; lit as
 * it stands in the room, the lamp catching its upper side and the tube's
 * magenta along the lower edge.
 */
const FORE = Math.cos(ELEVATION);
const PEN_SVG = (() => {
  const W = (PEN_LEN * FORE).toFixed(2);
  return `<svg class="pen" viewBox="0 -7 ${W} 14" width="${W}" height="14" aria-hidden="true">
  <defs>
    <linearGradient id="pen-lac" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#050304"/>
      <stop offset=".1" stop-color="#3b2a20"/>
      <stop offset=".19" stop-color="#ffe7c2"/>
      <stop offset=".25" stop-color="#4a3328"/>
      <stop offset=".42" stop-color="#170d12"/>
      <stop offset=".7" stop-color="#0d070b"/>
      <stop offset=".86" stop-color="#3a1030"/>
      <stop offset=".93" stop-color="#e05aa8"/>
      <stop offset="1" stop-color="#1c0a16"/>
    </linearGradient>
    <linearGradient id="pen-gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#4a3210"/>
      <stop offset=".18" stop-color="#d7ac55"/>
      <stop offset=".3" stop-color="#fff3c8"/>
      <stop offset=".46" stop-color="#c89a43"/>
      <stop offset=".8" stop-color="#7a561e"/>
      <stop offset=".92" stop-color="#c9709a"/>
      <stop offset="1" stop-color="#3b2510"/>
    </linearGradient>
    <linearGradient id="pen-rhod" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#6d7076"/>
      <stop offset=".3" stop-color="#f4f6f8"/>
      <stop offset=".6" stop-color="#a9aeb5"/>
      <stop offset="1" stop-color="#55585e"/>
    </linearGradient>
    <pattern id="pen-guilloche" width="1.1" height="14" patternUnits="userSpaceOnUse" y="-7">
      <rect width="1.1" height="14" fill="url(#pen-gold)"/>
      <rect width=".35" height="14" fill="rgba(60,35,8,.55)"/>
    </pattern>
  </defs>
  <g transform="scale(${FORE.toFixed(4)},1)">
    <!-- the nib: gold, with a rhodium heart, its slit and breather hole -->
    <path d="M0 0 C4 -.9 9 -2.6 13 -3.4 L16 -4.1 L16 4.1 L13 3.4 C9 2.6 4 .9 0 0 Z" fill="url(#pen-gold)"/>
    <path d="M3.5 0 C6 -.8 9 -1.9 11.5 -2.3 C10.8 -1.2 10.8 1.2 11.5 2.3 C9 1.9 6 .8 3.5 0 Z" fill="url(#pen-rhod)"/>
    <line x1=".4" y1="0" x2="9" y2="0" stroke="#2a1a08" stroke-width=".28"/>
    <circle cx="9.6" cy="0" r=".75" fill="#1a1008"/>
    <path d="M12.4 -2.6 q.6 .9 0 1.6 M12.4 2.6 q.6 -.9 0 -1.6" stroke="rgba(70,40,10,.6)" stroke-width=".25" fill="none"/>
    <!-- the section, with a fine gold thread ring where it meets the barrel -->
    <path d="M16 -4.1 L32 -4.7 L32 4.7 L16 4.1 Z" fill="url(#pen-lac)"/>
    <rect x="32" y="-5.1" width="2" height="10.2" rx=".4" fill="url(#pen-gold)"/>
    <!-- the barrel -->
    <rect x="34" y="-5.2" width="72" height="10.4" rx=".8" fill="url(#pen-lac)"/>
    <!-- the cap, posted: a broad engraved band, then the lacquer, the finial -->
    <rect x="104" y="-5.9" width="36" height="11.8" rx="1" fill="url(#pen-lac)"/>
    <rect x="104" y="-5.95" width="6.5" height="11.9" fill="url(#pen-guilloche)"/>
    <rect x="104" y="-5.95" width=".6" height="11.9" fill="#fff0c0" opacity=".7"/>
    <rect x="110" y="-5.95" width=".6" height="11.9" fill="#4a3210"/>
    <path d="M138 -5.9 Q142 -4.6 142 0 Q142 4.6 138 5.9 Z" fill="url(#pen-gold)"/>
    <!-- the clip, along the top of the cap, ending in a ball -->
    <rect x="115" y="-2.6" width="25" height="2.3" rx="1" fill="url(#pen-gold)"/>
    <ellipse cx="115.6" cy="-1.45" rx="1.9" ry="1.75" fill="url(#pen-gold)"/>
    <ellipse cx="115.2" cy="-1.9" rx=".7" ry=".5" fill="#fff6d6" opacity=".9"/>
  </g>
</svg>`;
})();

export const DESK_MARKUP = `<div class="desk" aria-hidden="true">
  <div class="desk__wood"></div>
  <div class="desk__ambient"></div>
  <div class="desk__lamp"></div>
  <div class="desk__window"></div>
  <div class="desk__blinds"></div>
  <div class="desk__spec desk__spec--neon"></div>
  <div class="desk__spec desk__spec--lamp"></div>
  <div class="desk__spec desk__spec--window"></div>
  <div class="desk__shade"></div>
</div>
<div class="desk__sweep" aria-hidden="true"></div>
<div class="desk__sweep desk__sweep--light" aria-hidden="true"></div>
<canvas class="desk__shadows" aria-hidden="true"></canvas>
${MODE === 'pen' ? `<div class="desk__pen" aria-hidden="true">${PEN_SVG}</div>` : ''}
<div class="desk__cast" aria-hidden="true"></div>`;

/**
 * The train is moving: what stands by the line outside throws its shadow
 * through the window as it passes, across the far end of the table and the
 * papers on it, from right to left as the city outside goes (lineside.ts).
 * Nearer things are bigger, softer and darker and pass quicker. Now and then
 * a lamp by the line throws light instead. Returns its stop.
 */
function passing(layer: HTMLElement, lights: HTMLElement): () => void {
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return () => {};
  let timer = 0;
  let live = true;
  const rand = (a: number, b: number) => a + Math.random() * (b - a);

  const run = (el: HTMLElement, width: number, ms: number, into: HTMLElement) => {
    into.append(el);
    const w = window.innerWidth;
    const a = el.animate(
      [
        { transform: `translate3d(${w + width * 0.2}px,0,0) skewX(-16deg)` },
        { transform: `translate3d(${-width * 1.6}px,0,0) skewX(-16deg)` },
      ],
      { duration: ms, easing: 'linear' },
    );
    a.onfinish = () => el.remove();
  };

  const shadow = () => {
    const s = nextSilhouette();
    const h = window.innerHeight * 0.95;
    // the box is 1000 units high, stretched to the window's light
    const k = (h / 1000) * (0.8 + s.near * 0.7);
    const width = s.width * k;
    const el = document.createElement('i');
    el.className = 'pass';
    el.style.width = `${width}px`;
    el.style.height = `${h * (0.8 + s.near * 0.7)}px`;
    // Two of it: the shadow itself, soft (light from a broad source, nearer
    // things softer), and over it a wide, faint haze where the glass scatters
    // the light round its edges
    const svg = `<svg viewBox="0 0 ${s.width.toFixed(0)} 1000" preserveAspectRatio="none" width="100%" height="100%">${s.svg}</svg>`;
    el.innerHTML = `<b style="filter:blur(${(14 + s.near * 22).toFixed(1)}px);opacity:.5">${svg}</b><b style="filter:blur(${(4 + s.near * 9).toFixed(1)}px)">${svg}</b>`;
    el.style.opacity = (0.26 + s.near * 0.26).toFixed(2);
    // nearer passes quicker, and the train itself is never at one speed
    run(el, width, rand(700, 820) * (1.25 - s.near * 0.5) * pace, layer);
  };

  const lamp = () => {
    const el = document.createElement('i');
    el.className = 'pass pass--lamp';
    const width = rand(180, 260);
    el.style.width = `${width}px`;
    run(el, width, rand(480, 560) * pace, lights);
  };

  // the train's pace, wandering slowly: 1 is the usual
  let pace = 1;
  // what is left of a run of things close together (a stand of trees, a yard)
  let runLeft = 0;

  const next = () => {
    if (!live) return;
    pace = Math.min(1.35, Math.max(0.75, pace + rand(-0.08, 0.08)));
    if (Math.random() < 0.08) lamp();
    else shadow();
    // No beat: things by the line come as they come. Sometimes several close
    // together, mostly a second or so apart, sometimes nothing for a while
    let gap: number;
    if (runLeft > 0) {
      runLeft--;
      gap = rand(180, 520);
    } else {
      const r = Math.random();
      if (r < 0.12) {
        runLeft = Math.floor(rand(1, 4));
        gap = rand(180, 520);
      } else if (r < 0.62) gap = rand(600, 1700);
      else if (r < 0.9) gap = rand(1700, 3400);
      else gap = rand(3600, 6500);
    }
    timer = window.setTimeout(next, gap * pace);
  };
  timer = window.setTimeout(next, 500);
  return () => {
    live = false;
    clearTimeout(timer);
    layer.replaceChildren();
    lights.replaceChildren();
  };
}

/**
 * The carriage's power is not steady. The tube stutters and sags, at no
 * regular interval: a few quick drops, a buzz, sometimes a long dip the lamp
 * feels too. Its light, its reflection and the pointer's shadow (which it
 * casts) all go with it. Returns its stop.
 */
function power(root: HTMLElement): () => void {
  const tube = ['.desk__ambient', '.desk__spec--neon']
    .map((q) => root.querySelector<HTMLElement>(q))
    .filter((e): e is HTMLElement => !!e);
  const shade = root.querySelector<HTMLElement>('.desk__shadows');
  const lamp = ['.desk__lamp', '.desk__spec--lamp']
    .map((q) => root.querySelector<HTMLElement>(q))
    .filter((e): e is HTMLElement => !!e);
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return () => {};
  let timer = 0;
  let live = true;
  const rand = (a: number, b: number) => a + Math.random() * (b - a);

  const play = (levels: [number, number][], lampToo: boolean) => {
    // levels: [brightness, ms held]
    const total = levels.reduce((t, [, ms]) => t + ms, 0);
    let at = 0;
    const frames = levels.map(([v, ms]) => {
      const f = { offset: at / total, v };
      at += ms;
      return f;
    });
    frames.push({ offset: 1, v: 1 });
    const opts = { duration: total, easing: 'steps(1, end)' as string };
    for (const el of tube)
      el.animate(
        frames.map((f) => ({ offset: f.offset, opacity: f.v })),
        opts,
      );
    shade?.animate(
      frames.map((f) => ({ offset: f.offset, filter: `opacity(${f.v})` })),
      opts,
    );
    if (lampToo)
      for (const el of lamp)
        el.animate(
          frames.map((f) => ({
            offset: f.offset,
            filter: `brightness(${(0.7 + f.v * 0.3).toFixed(2)})`,
          })),
          { duration: total, easing: 'ease-in-out' },
        );
  };

  const next = () => {
    if (!live) return;
    const r = Math.random();
    if (r < 0.55) {
      // a stutter: a few quick drops
      const n = Math.floor(rand(2, 6));
      const lv: [number, number][] = [];
      for (let i = 0; i < n; i++)
        lv.push([rand(0.1, 0.6), rand(30, 90)], [rand(0.75, 1), rand(30, 110)]);
      play(lv, false);
    } else if (r < 0.85) {
      // a buzz: fast and shallow, a while
      const lv: [number, number][] = [];
      for (let i = 0; i < 14; i++) lv.push([rand(0.6, 0.95), rand(25, 45)]);
      play(lv, false);
    } else {
      // a sag: the whole carriage dims, the tube nearly out, then catches
      play(
        [
          [0.7, 140],
          [0.45, 200],
          [0.25, 160],
          [0.05, 90],
          [0.6, 60],
          [0.15, 70],
          [0.85, 120],
        ],
        true,
      );
    }
    timer = window.setTimeout(next, rand(1200, 4200));
  };
  timer = window.setTimeout(next, rand(800, 2000));
  return () => {
    live = false;
    clearTimeout(timer);
  };
}

/** Over these the pen gives way to the ordinary pointer */
const PLAIN = 'a, button, .route, .langs';

/** The pen and its shadows on a desk in the page; returns their stop */
export function animateDesk(root: HTMLElement): () => void {
  const canvas = root.querySelector<HTMLCanvasElement>('.desk__shadows');
  const pen = root.querySelector<HTMLElement>('.desk__pen');
  if (!canvas) return () => {};
  const ctx = canvas.getContext('2d')!;
  const sweepLayer = root.querySelector<HTMLElement>('.desk__sweep');
  const lightLayer = root.querySelector<HTMLElement>('.desk__sweep--light');
  const stopPassing = sweepLayer && lightLayer ? passing(sweepLayer, lightLayer) : () => {};
  const stopPower = power(root);
  const page = root.closest<HTMLElement>('.page') ?? root;

  let dpr = 1;
  const size = () => {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.round(window.innerWidth * dpr);
    canvas.height = Math.round(window.innerHeight * dpr);
  };
  size();

  // the pen's axis on the table and across it
  const ax = Math.cos(AZIMUTH);
  const ay = Math.sin(AZIMUTH);
  const nx = -ay;
  const ny = ax;

  /** One light's shadow of the pen with its nib at (x, y) */
  const shadow = (l: Light, x: number, y: number) => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const scale = h / 900;
    const H = l.height * scale;
    const lx = l.x * w;
    const ly = l.y * h;
    const proj = (u: number, v: number) => {
      // a point of the pen: along it by u, across it by v
      const z = u * Math.sin(ELEVATION);
      const px = x + ax * u * Math.cos(ELEVATION) + nx * v;
      const py = y + ay * u * Math.cos(ELEVATION) + ny * v;
      const k = H / (H - z);
      return [lx + (px - lx) * k, ly + (py - ly) * k] as const;
    };
    const left = PROFILE.map(([u, r]) => proj(u, -r));
    const right = PROFILE.map(([u, r]) => proj(u, r)).reverse();
    const pts = [...left, ...right];
    const end = proj(PEN_LEN, 0);

    const d = Math.hypot(x - lx, y - ly);
    const strength = l.power / (1 + (d / (Math.hypot(w, h) * 0.8)) ** 2);
    // the penumbra at the top of the pen, where it is widest
    const zTop = PEN_LEN * Math.sin(ELEVATION);
    const blur = Math.min(46, l.size * scale * (zTop / (H - zTop)));

    const path = () => {
      ctx.beginPath();
      pts.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)));
      ctx.closePath();
    };
    const [r, g, b] = l.shade;
    const grad = (a0: number, aMid: number, a1: number, mid: number) => {
      const gr = ctx.createLinearGradient(x, y, end[0], end[1]);
      gr.addColorStop(0, `rgba(${r},${g},${b},${a0})`);
      gr.addColorStop(mid, `rgba(${r},${g},${b},${aMid})`);
      gr.addColorStop(1, `rgba(${r},${g},${b},${a1})`);
      return gr;
    };
    // Drawn off canvas and thrown back on by its shadow: canvas shadows blur in
    // every browser, where ctx.filter does not
    const FAR = 20000;
    const soft = (fill: CanvasGradient, b: number) => {
      ctx.save();
      ctx.translate(-FAR, 0);
      ctx.shadowOffsetX = FAR * dpr;
      ctx.shadowBlur = b * dpr;
      ctx.shadowColor = 'rgba(0,0,0,1)';
      ctx.fillStyle = fill;
      path();
      ctx.fill();
      ctx.restore();
    };
    ctx.globalAlpha = Math.min(1, strength * 1.9);
    // the whole shadow, soft and fading up the pen as it leaves the table...
    soft(grad(0.75, 0.55, 0.12, 0.45), blur);
    // ...and sharp where the nib meets it
    soft(grad(0.85, 0.2, 0, 0.3), 1.2);
    ctx.globalAlpha = 1;
  };

  /** One light's shadow of the pointer's arrow, hovering with its tip over (x, y) */
  const arrowShadow = (l: Light, x: number, y: number) => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const scale = h / 900;
    const H = l.height * scale;
    const z = HOVER * scale;
    const lx = l.x * w;
    const ly = l.y * h;
    // flat and level, so its shadow is its own shape, pushed away from the
    // light and a touch larger; softer the broader the light
    const k = H / (H - z);
    const pts = ARROW.map(([u, v]) => [lx + (x + u - lx) * k, ly + (y + v - ly) * k] as const);
    const d = Math.hypot(x - lx, y - ly);
    const strength = l.power / (1 + (d / (Math.hypot(w, h) * 0.8)) ** 2);
    const blur = Math.max(0.8, Math.min(30, l.size * scale * (z / (H - z))));
    const [r, g, b] = l.shade;
    const FAR = 20000;
    ctx.save();
    ctx.globalAlpha = Math.min(1, strength * 1.9);
    ctx.translate(-FAR, 0);
    ctx.shadowOffsetX = FAR * dpr;
    ctx.shadowBlur = blur * dpr;
    ctx.shadowColor = `rgba(${r},${g},${b},0.85)`;
    ctx.fillStyle = '#000';
    ctx.beginPath();
    pts.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py)));
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  };

  let tx = 0;
  let ty = 0;
  let x: number | null = null;
  let y = 0;
  let raf = 0;
  let last = performance.now();

  const draw = () => {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    ctx.globalCompositeOperation = 'multiply';
    if (MODE === 'cursor') {
      // only the tube's: one clear shadow to the right reads as the room's
      // light; three read as a rendering trick
      arrowShadow(ARROW_LIGHT, x!, y);
      ctx.globalCompositeOperation = 'source-over';
      return;
    }
    for (const l of LIGHTS) shadow(l, x!, y);
    ctx.globalCompositeOperation = 'source-over';
    // the nib's own contact: a touch of dark right under it
    const c = ctx.createRadialGradient(x!, y, 0, x!, y, 5);
    c.addColorStop(0, 'rgba(20,12,16,0.45)');
    c.addColorStop(1, 'rgba(20,12,16,0)');
    ctx.fillStyle = c;
    ctx.fillRect(x! - 6, y - 6, 12, 12);
    if (pen)
      pen.style.transform = `translate3d(${x!.toFixed(1)}px,${(y - 7).toFixed(1)}px,0) rotate(${AZIMUTH}rad)`;
  };

  const frame = (now: number) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    // the hand has a little weight; a shadow of the pointer itself has none
    const ease = MODE === 'pen' ? 1 - Math.exp(-dt / 0.05) : 1;
    x = x === null ? tx : x + (tx - x) * ease;
    y += (ty - y) * ease;
    draw();
    if (Math.abs(tx - x) + Math.abs(ty - y) < 0.1) return void (raf = 0);
    raf = requestAnimationFrame(frame);
  };

  const show = (on: boolean) => {
    canvas.classList.toggle('on', on);
    if (!pen) return;
    pen.classList.toggle('on', on);
    page.classList.toggle('with-pen', on);
  };

  const onMove = (e: PointerEvent) => {
    if (e.pointerType === 'touch') return;
    show(!(e.target as Element).closest?.(PLAIN));
    tx = e.clientX;
    ty = e.clientY;
    if (x === null) y = ty;
    if (!raf) {
      last = performance.now();
      raf = requestAnimationFrame(frame);
    }
  };
  const onLeave = () => show(false);
  const onResize = () => {
    size();
    if (x !== null) draw();
  };

  window.addEventListener('pointermove', onMove, { passive: true });
  document.documentElement.addEventListener('pointerleave', onLeave);
  window.addEventListener('resize', onResize);
  return () => {
    window.removeEventListener('pointermove', onMove);
    document.documentElement.removeEventListener('pointerleave', onLeave);
    window.removeEventListener('resize', onResize);
    cancelAnimationFrame(raf);
    stopPassing();
    stopPower();
    page.classList.remove('with-pen');
  };
}
