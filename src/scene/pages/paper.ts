/**
 * Worn paper edges: a clip-path polygon that nibbles a few pixels in from each
 * side at irregular steps, the same every time for the same seed. An optional
 * dog-eared corner is cut off the bottom right.
 */
export function wornEdge(seed: number, { amp = 2.2, fold = 0 } = {}): string {
  let s = seed >>> 0 || 1;
  const rand = () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 2 ** 32;
  };
  const j = () => (rand() * amp).toFixed(2);
  const pts: string[] = [];
  const steps = (n: number) => Array.from({ length: n + 1 }, (_, i) => (i / n) * 100);
  // along the top, left to right
  for (const x of steps(40)) pts.push(`${x.toFixed(2)}% ${j()}px`);
  // down the right side
  for (const y of steps(40)) {
    if (fold && y > 0 && y === 100) break;
    pts.push(`calc(100% - ${j()}px) ${y.toFixed(2)}%`);
  }
  if (fold) {
    pts.push(`calc(100% - ${j()}px) calc(100% - ${fold}px)`);
    pts.push(`calc(100% - ${fold}px) calc(100% - ${j()}px)`);
  }
  // along the bottom, right to left
  for (const x of steps(40).reverse()) {
    if (fold && x === 100) continue;
    pts.push(`${x.toFixed(2)}% calc(100% - ${j()}px)`);
  }
  // up the left side
  for (const y of steps(40).reverse()) pts.push(`${j()}px ${y.toFixed(2)}%`);
  return `clip-path:polygon(${pts.join(',')})`;
}
