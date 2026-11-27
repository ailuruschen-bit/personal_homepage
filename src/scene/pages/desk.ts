/**
 * The table under the papers, lit by what lights the compartment (docs/13):
 * the magenta tube on the left wall, the lamp on the right, the window's
 * slatted city light from the far side, and the room's dark toward the
 * reader. The diffuse light stays put; the reflections in the varnish move
 * against the pointer, as reflections do when the eye moves, and a quick
 * movement scatters them for a moment before they settle back.
 */

/** Each reflection: its blobs, how far it moves with the eye, how much it scatters */
const SPECS = [
  { cls: 'desk__spec--neon', blobs: 3, view: 26, scatter: 1 },
  { cls: 'desk__spec--lamp', blobs: 3, view: 18, scatter: 0.8 },
  { cls: 'desk__spec--window', blobs: 4, view: 34, scatter: 1.2 },
];

/** Spring back to rest: stiffness, damping, per second */
const K = 26;
const C = 7.5;
/** How hard pointer speed pushes the reflections, and their top speed, px/s */
const GAIN = 3.5;
const MAX_V = 320;

export const DESK_MARKUP = `<div class="desk" aria-hidden="true">
  <div class="desk__wood"></div>
  <div class="desk__ambient"></div>
  <div class="desk__blinds"></div>
  ${SPECS.map((s) => `<div class="desk__spec ${s.cls}">${'<i></i>'.repeat(s.blobs)}</div>`).join(
    '',
  )}
  <div class="desk__shade"></div>
</div>
<div class="desk__cast" aria-hidden="true"></div>`;

interface Blob {
  el: HTMLElement;
  view: number;
  scatter: number;
  /** displacement from rest and its velocity, in px */
  x: number;
  y: number;
  vx: number;
  vy: number;
  /** its own direction of scatter, so the blobs part rather than move as one */
  dir: number;
}

/** Bring a desk in the page to life; returns its stop */
export function animateDesk(root: HTMLElement): () => void {
  const blobs: Blob[] = [];
  SPECS.forEach((s) => {
    root.querySelectorAll<HTMLElement>(`.${s.cls} i`).forEach((el, n) => {
      blobs.push({
        el,
        view: s.view * (1 + n * 0.18),
        scatter: s.scatter,
        x: 0,
        y: 0,
        vx: 0,
        vy: 0,
        dir: (n * 2.39 + s.view) % (Math.PI * 2),
      });
    });
  });
  if (!blobs.length) return () => {};

  // the eye: where the pointer is, eased, from -1 to 1 across the window
  let ex = 0;
  let ey = 0;
  let tx = 0;
  let ty = 0;
  let px: number | null = null;
  let py = 0;
  let last = performance.now();
  let raf = 0;
  let still = 0;

  const onMove = (e: PointerEvent) => {
    tx = (e.clientX / window.innerWidth) * 2 - 1;
    ty = (e.clientY / window.innerHeight) * 2 - 1;
    if (px !== null) {
      // a push to every blob, from how fast the pointer went, each its own way
      const dx = e.clientX - px;
      const dy = e.clientY - py;
      const speed = Math.min(60, Math.hypot(dx, dy));
      const a = Math.atan2(dy, dx);
      for (const b of blobs) {
        const d = a + b.dir;
        b.vx += Math.cos(d) * speed * GAIN * b.scatter;
        b.vy += Math.sin(d) * speed * GAIN * b.scatter;
        // soft, not thrown: the scatter never runs away however fast the hand
        const v = Math.hypot(b.vx, b.vy);
        if (v > MAX_V) {
          b.vx *= MAX_V / v;
          b.vy *= MAX_V / v;
        }
      }
    }
    px = e.clientX;
    py = e.clientY;
    wake();
  };

  const frame = (now: number) => {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const ease = 1 - Math.exp(-dt / 0.35);
    ex += (tx - ex) * ease;
    ey += (ty - ey) * ease;
    let energy = Math.abs(tx - ex) + Math.abs(ty - ey);
    for (const b of blobs) {
      b.vx += (-K * b.x - C * b.vx) * dt;
      b.vy += (-K * b.y - C * b.vy) * dt;
      b.x += b.vx * dt;
      b.y += b.vy * dt;
      energy += Math.abs(b.vx) + Math.abs(b.vy) + Math.abs(b.x) + Math.abs(b.y);
      // against the eye, plus the scatter; spread out a little as it scatters
      const spread = Math.min(0.35, Math.hypot(b.x, b.y) / 160);
      const x = -ex * b.view + b.x;
      const y = -ey * b.view * 0.6 + b.y;
      b.el.style.transform = `translate3d(${x.toFixed(1)}px,${y.toFixed(1)}px,0) scale(${(1 + spread).toFixed(3)})`;
      b.el.style.opacity = (1 - spread * 1.1).toFixed(3);
    }
    // sleep once everything has settled
    if (energy < 0.05) {
      still++;
      if (still > 10) return void (raf = 0);
    } else still = 0;
    raf = requestAnimationFrame(frame);
  };

  const wake = () => {
    if (raf) return;
    last = performance.now();
    raf = requestAnimationFrame(frame);
  };

  window.addEventListener('pointermove', onMove, { passive: true });
  return () => {
    window.removeEventListener('pointermove', onMove);
    cancelAnimationFrame(raf);
  };
}
