// Check that the generated geometry, the hotspots and the built assets agree.
//
// Run as `npm run art:check`, and as the first step of `npm run build`. It needs
// nothing but Node, so it runs anywhere the site builds. Every failure names the
// file to fix. See docs/13, step 0.4.

import { readFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const SCENE = 480;
const SCALE = 2; // px.SCALE in build.py: assets are drawn at 1x and written at 2x
// ...and the carriage's are doubled again (CARRIAGE_UP in build.py)
const CARRIAGE = SCALE * 2;
const read = (p) => readFileSync(join(ROOT, p), 'utf8');
const problems = [];
const fail = (msg) => problems.push(msg);

/** Pixel size of a PNG or WebP, read from its header */
function imageSize(path) {
  const b = readFileSync(join(ROOT, path));
  if (b.toString('ascii', 1, 4) === 'PNG') return [b.readUInt32BE(16), b.readUInt32BE(20)];
  if (b.toString('ascii', 0, 4) !== 'RIFF' || b.toString('ascii', 8, 12) !== 'WEBP') {
    throw new Error(`${path}: not a PNG or WebP`);
  }
  const chunk = b.toString('ascii', 12, 16);
  if (chunk === 'VP8 ') return [b.readUInt16LE(26) & 0x3fff, b.readUInt16LE(28) & 0x3fff];
  if (chunk === 'VP8L') {
    const v = b.readUInt32LE(21);
    return [(v & 0x3fff) + 1, ((v >> 14) & 0x3fff) + 1];
  }
  if (chunk === 'VP8X') return [b.readUIntLE(24, 3) + 1, b.readUIntLE(27, 3) + 1];
  throw new Error(`${path}: unknown WebP chunk ${chunk}`);
}

function expectSize(path, w, h, why) {
  if (!existsSync(join(ROOT, path))) return fail(`${path} is missing. Run \`npm run art\`.`);
  const [aw, ah] = imageSize(path);
  if (aw !== w || ah !== h) fail(`${path} is ${aw}x${ah}, but ${why} expects ${w}x${h}.`);
}

// ---- the generated geometry
const gen = read('src/scene/geometry.gen.ts');
const objects = new Map();
for (const m of gen.matchAll(/^ {2}(\w+): \{ (.*) \},$/gm)) {
  const body = m[2];
  const box = body.match(/box: \{ x: ([\d.]+), y: ([\d.]+), w: ([\d.]+), h: ([\d.]+) \}/);
  const sprite = body.match(/sprite: '([^']+)'/);
  objects.set(m[1], { box: box && box.slice(1).map(Number), sprite: sprite && sprite[1] });
}
if (!objects.size) fail('src/scene/geometry.gen.ts lists no objects. Run `npm run art`.');
const win = gen.match(/WINDOW = \{ x: ([\d.]+), y: ([\d.]+), w: ([\d.]+), h: ([\d.]+)/);
if (!win) fail('src/scene/geometry.gen.ts has no WINDOW. Run `npm run art`.');

// ---- every object has exactly one hotspot, and every hotspot an object
const hs = read('src/scene/hotspots.ts');
const targets = [...hs.matchAll(/^ {4}target: (COVER|'(\w+)'),$/gm)].map((m) => m[2] ?? 'cover');
for (const t of new Set(targets)) {
  const n = targets.filter((x) => x === t).length;
  if (n > 1) fail(`src/scene/hotspots.ts lists "${t}" ${n} times.`);
  if (!objects.has(t))
    fail(`src/scene/hotspots.ts has "${t}", which tools/art/room.py does not draw.`);
}
for (const id of objects.keys()) {
  if (!targets.includes(id))
    fail(`tools/art/room.py draws "${id}", but src/scene/hotspots.ts has no entry for it.`);
}

// ---- sprites exist and cover their boxes
for (const [id, o] of objects) {
  if (!o.sprite) continue;
  const [, , w, h] = o.box ?? [];
  expectSize(
    join('public', o.sprite),
    w * CARRIAGE,
    h * CARRIAGE,
    `the box of "${id}" in geometry.gen.ts`,
  );
}

// ---- the window sits inside the scene
if (win) {
  const [x, y, w, h] = win.slice(1).map(Number);
  if (x < 0 || y < 0 || x + w > SCENE || y + h > SCENE) {
    fail(`WINDOW in tools/art/room.py (${x}, ${y}, ${w}x${h}) runs outside the ${SCENE} scene.`);
  }
}

// ---- assets have the sizes scene.css lays them out at
const css = read('src/scene/scene.css');
expectSize('public/assets/room.webp', SCENE * CARRIAGE, SCENE * CARRIAGE, '.room in scene.css');
expectSize(
  'public/assets/room-l.webp',
  120 * CARRIAGE,
  SCENE * CARRIAGE,
  'the side extensions in scene.css',
);
expectSize(
  'public/assets/room-r.webp',
  120 * CARRIAGE,
  SCENE * CARRIAGE,
  'the side extensions in scene.css',
);
const layerHeight = Number(css.match(/background-size: auto (\d+)px;/)?.[1]);
for (const m of css.matchAll(
  /--tile: (\d+)px;\s*background-image: url\(\/assets\/(c\d)\.webp\);/g,
)) {
  expectSize(
    `public/assets/${m[2]}.webp`,
    Number(m[1]),
    layerHeight,
    `.${m[2]} in scene.css (--tile and background-size)`,
  );
}

if (problems.length) {
  console.error(`art:check found ${problems.length} problem${problems.length > 1 ? 's' : ''}:\n`);
  for (const p of problems) console.error(`  - ${p}`);
  process.exit(1);
}
console.log(
  `art:check ok: ${objects.size} objects, ${targets.length} hotspots, sprites and assets agree.`,
);
