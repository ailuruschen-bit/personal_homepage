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
  { x: 0.5, y: -0.45, height: 2400, power: 0.2, size: 520, shade: [80, 62, 40] },
];

/** The pen: its length, how steeply it is held, and which way its barrel
 *  points from the nib (radians, screen axes: toward the lower right) */
const PEN_LEN = 150;
const ELEVATION = (50 * Math.PI) / 180;
const AZIMUTH = (52 * Math.PI) / 180;
/** Its half-width along its length, from the nib: [distance, half-width] */
const PROFILE: [number, number][] = [
  [0, 0.4],
  [6, 1.6],
  [14, 3.2],
  [16, 4.2],
  [34, 4.8],
  [38, 5.6],
  [138, 5.8],
  [146, 5.0],
  [150, 3.2],
];

/** The pen as drawn: seen from above, so its length is foreshortened. Drawn
 *  along +x from the nib at the origin, rotated into place */
const FORE = PEN_LEN * Math.cos(ELEVATION);
const PEN_SVG = (() => {
  const s = (d: number) => ((d / PEN_LEN) * FORE).toFixed(2);
  return `<svg class="pen" viewBox="0 -8 ${FORE.toFixed(1)} 16" width="${FORE.toFixed(1)}" height="16" aria-hidden="true">
  <defs>
    <linearGradient id="pen-body" x1="0" y1="-1" x2="0" y2="1" gradientUnits="objectBoundingBox">
      <stop offset="0" stop-color="#1a1418"/><stop offset=".28" stop-color="#4a3a44"/>
      <stop offset=".42" stop-color="#2a2027"/><stop offset="1" stop-color="#0c090c"/>
    </linearGradient>
    <linearGradient id="pen-gold" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#7a5a22"/><stop offset=".35" stop-color="#f3d58a"/>
      <stop offset=".6" stop-color="#b48a3c"/><stop offset="1" stop-color="#5e4318"/>
    </linearGradient>
  </defs>
  <path d="M0 0 L${s(14)} -2.6 L${s(15)} 2.6 Z" fill="url(#pen-gold)"/>
  <line x1="0.6" y1="0" x2="${s(11)}" y2="0" stroke="#3d2a10" stroke-width=".35"/>
  <rect x="${s(14)}" y="-4.2" width="${(Number(s(38)) - Number(s(14))).toFixed(2)}" height="8.4" rx="1.6" fill="url(#pen-body)"/>
  <rect x="${s(37)}" y="-5.1" width="${s(2.4)}" height="10.2" fill="url(#pen-gold)"/>
  <rect x="${s(39)}" y="-5.6" width="${(Number(s(146)) - Number(s(39))).toFixed(2)}" height="11.2" rx="2" fill="url(#pen-body)"/>
  <rect x="${s(120)}" y="-1.3" width="${s(24)}" height="2.6" rx="1.2" fill="url(#pen-gold)"/>
  <rect x="${s(145)}" y="-4.6" width="${s(5)}" height="9.2" rx="2.2" fill="#140f12"/>
</svg>`;
})();

export const DESK_MARKUP = `<div class="desk" aria-hidden="true">
  <div class="desk__wood"></div>
  <div class="desk__ambient"></div>
  <div class="desk__blinds"></div>
  <div class="desk__spec desk__spec--neon"></div>
  <div class="desk__spec desk__spec--lamp"></div>
  <div class="desk__spec desk__spec--window"></div>
  <div class="desk__shade"></div>
</div>
<canvas class="desk__shadows" aria-hidden="true"></canvas>
<div class="desk__pen" aria-hidden="true">${PEN_SVG}</div>
<div class="desk__cast" aria-hidden="true"></div>`;

/** Over these the pen gives way to the ordinary pointer */
const PLAIN = 'a, button, .route, .langs';

/** The pen and its shadows on a desk in the page; returns their stop */
export function animateDesk(root: HTMLElement): () => void {
  const canvas = root.querySelector<HTMLCanvasElement>('.desk__shadows');
  const pen = root.querySelector<HTMLElement>('.desk__pen');
  if (!canvas || !pen) return () => {};
  const ctx = canvas.getContext('2d')!;
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
    for (const l of LIGHTS) shadow(l, x!, y);
    ctx.globalCompositeOperation = 'source-over';
    // the nib's own contact: a touch of dark right under it
    const c = ctx.createRadialGradient(x!, y, 0, x!, y, 5);
    c.addColorStop(0, 'rgba(20,12,16,0.45)');
    c.addColorStop(1, 'rgba(20,12,16,0)');
    ctx.fillStyle = c;
    ctx.fillRect(x! - 6, y - 6, 12, 12);
    pen.style.transform = `translate3d(${x!.toFixed(1)}px,${(y - 8).toFixed(1)}px,0) rotate(${AZIMUTH}rad)`;
  };

  const frame = (now: number) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    // the hand has a little weight
    const ease = 1 - Math.exp(-dt / 0.05);
    x = x === null ? tx : x + (tx - x) * ease;
    y += (ty - y) * ease;
    draw();
    if (Math.abs(tx - x) + Math.abs(ty - y) < 0.1) return void (raf = 0);
    raf = requestAnimationFrame(frame);
  };

  const show = (on: boolean) => {
    canvas.classList.toggle('on', on);
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
    page.classList.remove('with-pen');
  };
}
