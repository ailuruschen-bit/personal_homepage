/**
 * What stands by the line, as shadow silhouettes for the desk (desk.ts). Each
 * is drawn fresh, a little different every time, in a box 1000 units high
 * that is stretched to the window's light on the table. Shadows only: one
 * colour, the softness is the element's own blur.
 */

const rand = (a: number, b: number) => a + Math.random() * (b - a);
const pick = <T>(xs: T[]) => xs[Math.floor(Math.random() * xs.length)]!;

export interface Silhouette {
  /** the SVG's inner markup, in a viewBox of `width` x 1000 */
  svg: string;
  width: number;
  /** how close to the window it passes: nearer is bigger, softer and darker */
  near: number;
}

/** A wooden pole: a tapering trunk, a crossarm with insulators, its stays */
function pole(): Silhouette {
  const w = 120;
  const x = 60;
  const top = rand(40, 120);
  const arm = top + rand(40, 70);
  const lean = rand(-6, 6);
  const ins = [-44, -16, 16, 44]
    .map((d) => `<rect x="${x + d - 3}" y="${arm - 22}" width="6" height="20" rx="2"/>`)
    .join('');
  return {
    width: w,
    near: rand(0.35, 0.6),
    svg: `<path d="M${x - 7 + lean} ${top} L${x + 7 + lean} ${top} L${x + 10} 1000 L${x - 10} 1000 Z"/>
      <rect x="${x - 52}" y="${arm}" width="104" height="9" rx="2" transform="rotate(${rand(-3, 3)} ${x} ${arm})"/>
      ${ins}
      <path d="M${x - 40} ${arm + 9} L${x} ${arm + 60} M${x + 40} ${arm + 9} L${x} ${arm + 60}" stroke="currentColor" stroke-width="4" fill="none"/>`,
  };
}

/** A catenary mast: a lattice of two uprights and their bracing, and the
 *  cantilever arm reaching over the track */
function mast(): Silhouette {
  const w = 150;
  const l = 52;
  const r = 82;
  let brace = '';
  for (let y = 120; y < 980; y += 60)
    brace += `M${l} ${y} L${r} ${y + 60} M${r} ${y} L${l} ${y + 60} `;
  const armY = rand(130, 190);
  return {
    width: w,
    near: rand(0.45, 0.7),
    svg: `<rect x="${l - 4}" y="100" width="8" height="900"/><rect x="${r - 4}" y="100" width="8" height="900"/>
      <path d="${brace}" stroke="currentColor" stroke-width="3" fill="none"/>
      <path d="M${r} ${armY} L${w} ${armY - 30} M${r} ${armY + 50} L${w} ${armY - 26}" stroke="currentColor" stroke-width="6" fill="none"/>
      <rect x="${l - 10}" y="92" width="${r - l + 20}" height="14"/>`,
  };
}

/** A branch reaching in from above: a crooked limb, forking into twigs,
 *  with leaves in clumps. Passes close, so it is big and soft */
function branch(): Silhouette {
  const w = rand(300, 460);
  let paths = '';
  let leaves = '';
  const grow = (x: number, y: number, a: number, len: number, wid: number, depth: number) => {
    let cx = x;
    let cy = y;
    let d = `M${cx.toFixed(1)} ${cy.toFixed(1)}`;
    const steps = 5;
    for (let i = 0; i < steps; i++) {
      a += rand(-0.35, 0.35);
      cx += Math.cos(a) * (len / steps);
      cy += Math.sin(a) * (len / steps);
      d += ` L${cx.toFixed(1)} ${cy.toFixed(1)}`;
    }
    paths += `<path d="${d}" stroke="currentColor" stroke-width="${wid.toFixed(1)}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
    if (depth === 0 || len < 40) {
      // a clump of leaves at the tip
      for (let k = 0; k < 7; k++) {
        const lx = cx + rand(-28, 28);
        const ly = cy + rand(-24, 24);
        leaves += `<ellipse cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" rx="${rand(9, 16).toFixed(1)}" ry="${rand(5, 9).toFixed(1)}" transform="rotate(${rand(0, 180).toFixed(0)} ${lx.toFixed(1)} ${ly.toFixed(1)})"/>`;
      }
      return;
    }
    const forks = depth > 2 ? 2 : pick([2, 3]);
    for (let f = 0; f < forks; f++)
      grow(cx, cy, a + rand(-0.9, 0.9), len * rand(0.55, 0.75), wid * 0.62, depth - 1);
  };
  grow(rand(0.3, 0.7) * w, -20, Math.PI / 2 + rand(-0.4, 0.4), rand(260, 340), rand(14, 20), 4);
  return { width: w, near: rand(0.75, 1), svg: paths + leaves };
}

/** A tree further off: a trunk and a broad, broken crown */
function tree(): Silhouette {
  const w = rand(220, 320);
  const cx = w / 2;
  let crown = '';
  for (let k = 0; k < 22; k++) {
    const a = rand(0, Math.PI * 2);
    const r = rand(0, 1) ** 0.6;
    const x = cx + Math.cos(a) * r * w * 0.42;
    const y = 300 + Math.sin(a) * r * 190;
    crown += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rand(24, 52).toFixed(1)}"/>`;
  }
  return {
    width: w,
    near: rand(0.2, 0.4),
    svg: `<path d="M${cx - 9} 1000 L${cx - 6} 360 L${cx + 6} 360 L${cx + 11} 1000 Z"/>${crown}`,
  };
}

/** A signal: a post, a ladder, the head with its hood */
function signal(): Silhouette {
  const w = 90;
  const x = 45;
  let rungs = '';
  for (let y = 300; y < 960; y += 34) rungs += `M${x + 8} ${y} L${x + 24} ${y} `;
  return {
    width: w,
    near: rand(0.4, 0.6),
    svg: `<rect x="${x - 5}" y="180" width="10" height="820"/>
      <path d="M${x + 8} 300 L${x + 8} 1000 M${x + 24} 300 L${x + 24} 1000 ${rungs}" stroke="currentColor" stroke-width="3" fill="none"/>
      <rect x="${x - 22}" y="120" width="44" height="90" rx="10"/>
      <path d="M${x - 26} 120 L${x + 26} 120 L${x + 20} 100 L${x - 20} 100 Z"/>`,
  };
}

/** A billboard by the line, gone dark: a frame on two legs */
function board(): Silhouette {
  const w = rand(260, 360);
  return {
    width: w,
    near: rand(0.2, 0.35),
    svg: `<rect x="10" y="${rand(120, 200)}" width="${w - 20}" height="150"/>
      <rect x="${w * 0.25}" y="250" width="12" height="750"/><rect x="${w * 0.72}" y="250" width="12" height="750"/>
      <path d="M${w * 0.25 + 6} 420 L${w * 0.72 + 6} 640 M${w * 0.72 + 6} 420 L${w * 0.25 + 6} 640" stroke="currentColor" stroke-width="5" fill="none"/>`,
  };
}

/** What comes next, roughly as often as it would: poles and masts most,
 *  trees and branches in runs, the odd signal and board */
export function nextSilhouette(): Silhouette {
  const r = Math.random();
  if (r < 0.34) return mast();
  if (r < 0.56) return pole();
  if (r < 0.74) return branch();
  if (r < 0.86) return tree();
  if (r < 0.94) return signal();
  return board();
}
