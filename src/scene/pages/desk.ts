/**
 * The table under the papers, lit by what lights the compartment (docs/13):
 * the magenta tube on the left wall, the lamp on the right, the window's
 * slatted city light from the far side, and the room's dark toward the
 * reader.
 *
 * The pointer is something held a little above the table (a hand, a pen),
 * and it casts a shadow from each light: away from that light, longer and
 * softer the lower and broader the light, darker where that light is strong,
 * and tinted by what the light was adding (blocking the magenta tube leaves
 * the green it was hiding).
 */

/** Where each light is, as a fraction of the viewport (y can be off screen,
 *  beyond the far edge of the table), and how high above the table, in
 *  viewport heights */
const LIGHTS = [
  // the tube: a long source low on the left wall, so a soft, sideways shadow
  { x: -0.04, y: 0.42, height: 1.5, power: 0.55, size: 0.5, tint: [0.62, 0.92, 0.72] },
  // the lamp: small and close, so the sharpest, darkest shadow
  { x: 0.9, y: 0.26, height: 1.1, power: 0.75, size: 0.15, tint: [0.5, 0.66, 0.9] },
  // the window: broad and far, so a faint, long, very soft one toward the reader
  { x: 0.5, y: -0.3, height: 2.4, power: 0.32, size: 0.9, tint: [0.9, 0.82, 0.62] },
];
/** How high above the table the pointer's "hand" is, in viewport heights */
const HOLD = 0.16;
/** Its own size, px: the radius of a shadow with no spread */
const RADIUS = 26;

export const DESK_MARKUP = `<div class="desk" aria-hidden="true">
  <div class="desk__wood"></div>
  <div class="desk__ambient"></div>
  <div class="desk__blinds"></div>
  <div class="desk__spec desk__spec--neon"><i></i><i></i><i></i></div>
  <div class="desk__spec desk__spec--lamp"><i></i><i></i><i></i></div>
  <div class="desk__spec desk__spec--window"><i></i><i></i><i></i><i></i></div>
  <div class="desk__shade"></div>
</div>
<div class="desk__shadows" aria-hidden="true">${LIGHTS.map(
  (l) =>
    `<i style="background:radial-gradient(closest-side,rgb(${l.tint.map((c) => Math.round(c * 120)).join(',')}),transparent)"></i>`,
).join('')}</div>
<div class="desk__cast" aria-hidden="true"></div>`;

/** The pointer's shadows on a desk in the page; returns their stop */
export function animateDesk(root: HTMLElement): () => void {
  const layer = root.querySelector<HTMLElement>('.desk__shadows');
  if (!layer) return () => {};
  const shadows = Array.from(layer.querySelectorAll<HTMLElement>('i'));

  let tx = 0;
  let ty = 0;
  let x: number | null = null;
  let y = 0;
  let raf = 0;
  let last = performance.now();

  const place = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const reach = Math.hypot(w, h) * 0.75;
    LIGHTS.forEach((l, i) => {
      const lx = l.x * w;
      const ly = l.y * h;
      const dx = x! - lx;
      const dy = y - ly;
      const d = Math.hypot(dx, dy) || 1;
      // similar triangles: the shadow lands beyond the hand by its height over
      // the light's height above the hand
      const k = HOLD / (l.height - HOLD);
      const off = d * k;
      // a broad light blurs the shadow in proportion to how far it falls
      const soft = 1 + l.size * off * 0.06;
      const across = RADIUS * soft;
      const along = across + off * 0.9;
      // strong near its light, weaker far from it, and thinner as it spreads
      const strength = l.power / (1 + (d / reach) ** 2) / soft;
      const cx = x! + (dx / d) * off * 0.55;
      const cy = y + (dy / d) * off * 0.55;
      const angle = Math.atan2(dy, dx);
      const el = shadows[i]!;
      el.style.width = `${(along * 2).toFixed(1)}px`;
      el.style.height = `${(across * 2).toFixed(1)}px`;
      el.style.transform = `translate3d(${(cx - along).toFixed(1)}px,${(cy - across).toFixed(1)}px,0) rotate(${angle.toFixed(3)}rad)`;
      el.style.opacity = Math.min(1, strength * 1.6).toFixed(3);
    });
  };

  const frame = (now: number) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    // the hand follows the pointer with a little weight
    const ease = 1 - Math.exp(-dt / 0.08);
    x = x === null ? tx : x + (tx - x) * ease;
    y += (ty - y) * ease;
    place();
    if (Math.abs(tx - x) + Math.abs(ty - y) < 0.2) return void (raf = 0);
    raf = requestAnimationFrame(frame);
  };

  const onMove = (e: PointerEvent) => {
    if (e.pointerType === 'touch') return;
    tx = e.clientX;
    ty = e.clientY;
    if (x === null) y = ty;
    layer.classList.add('on');
    if (!raf) {
      last = performance.now();
      raf = requestAnimationFrame(frame);
    }
  };
  const onLeave = () => layer.classList.remove('on');

  window.addEventListener('pointermove', onMove, { passive: true });
  document.documentElement.addEventListener('pointerleave', onLeave);
  return () => {
    window.removeEventListener('pointermove', onMove);
    document.documentElement.removeEventListener('pointerleave', onLeave);
    cancelAnimationFrame(raf);
  };
}
