import { CAMERA, OBJECTS, PERSPECTIVE, WINDOW } from './geometry.gen';
import { SCENE } from './units';

/**
 * Geometry overlay, loaded only with ?debug=geometry (see index.ts), so the
 * normal bundle never contains it.
 *
 * Draws what tools/art/room.py generated over the scene, in scene units, inside
 * .scene so it moves with the camera: each object's snap zone (dashed), pool of
 * light (ellipse) and sprite box (solid), the window opening and the camera's
 * zoom origin. After any change to the artwork, everything should sit on what
 * it describes. See docs/13, step 0.5.
 */
export function drawGeometry(root: HTMLElement) {
  const scene = root.querySelector<HTMLElement>('.scene');
  if (!scene) return;
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', `0 0 ${SCENE} ${SCENE}`);
  svg.setAttribute('class', 'debug-geometry');
  svg.style.cssText =
    'position:absolute;inset:0;width:100%;height:100%;z-index:99;pointer-events:none;overflow:visible';

  const add = (tag: string, attrs: Record<string, string | number>, text?: string) => {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, String(v));
    if (text) el.textContent = text;
    svg.appendChild(el);
    return el;
  };
  const line = { fill: 'none', 'vector-effect': 'non-scaling-stroke', 'stroke-width': 1.5 };
  const label = (x: number, y: number, text: string, fill: string) =>
    add(
      'text',
      {
        x,
        y,
        fill,
        'font-size': 5,
        'font-family': 'monospace',
        'paint-order': 'stroke',
        stroke: '#000',
        'stroke-width': 1.5,
      },
      text,
    );

  // Perspective guides: the horizon, the vanishing point, the window wall, and
  // the room's receding edges from its corners out past the edge of the scene
  const { vx, vy, wall } = PERSPECTIVE;
  const [wx0, wy0, wx1, wy1] = wall;
  const guide = { ...line, stroke: '#ff9a3b', opacity: 0.85 };
  add('path', { ...guide, d: `M-240 ${vy}H720`, 'stroke-dasharray': '2 3' });
  add('rect', { ...guide, x: wx0, y: wy0, width: wx1 - wx0, height: wy1 - wy0 });
  for (const [cx, cy] of [
    [wx0, wy0],
    [wx1, wy0],
    [wx0, wy1],
    [wx1, wy1],
  ] as const) {
    add('path', { ...guide, d: `M${vx} ${vy}L${vx + (cx - vx) * 6} ${vy + (cy - vy) * 6}` });
  }
  add('circle', { ...guide, cx: vx, cy: vy, r: 3 });
  label(wx0 + 2, wy1 - 2, 'window wall', '#ff9a3b');

  // the window and the camera's zoom origin
  add('rect', {
    ...line,
    x: WINDOW.x,
    y: WINDOW.y,
    width: WINDOW.w,
    height: WINDOW.h,
    rx: WINDOW.r,
    stroke: '#39ff88',
  });
  label(WINDOW.x + 2, WINDOW.y + 6, 'window', '#39ff88');
  add('path', {
    ...line,
    d: `M${CAMERA.x - 6} ${CAMERA.y}h12M${CAMERA.x} ${CAMERA.y - 6}v12`,
    stroke: '#ff3b3b',
  });
  label(CAMERA.x + 4, CAMERA.y - 3, 'camera origin', '#ff3b3b');

  for (const [id, g] of Object.entries(OBJECTS)) {
    const [x0, y0, x1, y1] = g.zone;
    add('rect', {
      ...line,
      x: x0,
      y: y0,
      width: x1 - x0,
      height: y1 - y0,
      stroke: '#ffd23b',
      'stroke-dasharray': '4 3',
    });
    add('ellipse', {
      ...line,
      cx: g.light.x,
      cy: g.light.y,
      rx: g.light.rx,
      ry: g.light.ry,
      stroke: '#ff5ce1',
      opacity: 0.8,
    });
    if (g.box)
      add('rect', {
        ...line,
        x: g.box.x,
        y: g.box.y,
        width: g.box.w,
        height: g.box.h,
        stroke: '#3bd6ff',
      });
    label(x0 + 1, y0 - 1.5, id, '#ffd23b');
  }

  // Legend, fixed to the viewport: the hub framing crops the scene's corners
  const legend = document.createElement('div');
  legend.style.cssText =
    'position:fixed;left:12px;bottom:12px;z-index:1000;pointer-events:none;padding:6px 8px;' +
    'font:11px/1.5 monospace;background:rgba(0,0,0,0.6);border-radius:4px';
  legend.innerHTML = [
    ['#ffd23b', 'snap zone (dashed)'],
    ['#ff5ce1', 'light'],
    ['#3bd6ff', 'sprite box'],
    ['#39ff88', 'window'],
    ['#ff3b3b', 'camera origin'],
    ['#ff9a3b', 'perspective'],
  ]
    .map(([c, t]) => `<div style="color:${c}">■ ${t}</div>`)
    .join('');
  root.appendChild(legend);

  scene.appendChild(svg);
}

/**
 * Layer switchboard, loaded with ?debug=layers. Each checkbox removes one
 * suspect from the page so a compositing fault can be narrowed down by eye in
 * the browser that shows it. Choices persist across reloads in sessionStorage,
 * so faults that only appear during the opening can be tested too.
 */
export function layerSwitches(root: HTMLElement) {
  // The classes go on the mount, not on .stage: Opening rewrites .stage's
  // className on every phase change
  const stage = root;
  const switches: Array<[string, string, string]> = [
    ['x-pops', 'object sprites (.pop)', '.x-pops .pop{display:none}'],
    ['x-glint', 'sprite glint animation', '.x-glint .pop{animation:none!important}'],
    ['x-extfx', 'side panel shading', '.x-extfx .ext::before,.x-extfx .ext::after{display:none}'],
    ['x-sides', 'side panels', '.x-sides .ext.l,.x-sides .ext.r{display:none}'],
    ['x-glow', 'glows', '.x-glow .glow{display:none}'],
    [
      'x-vig',
      'vignette and focus light',
      '.x-vig .vig,.x-vig .beam{display:none}',
    ],
    ['x-grain', 'film grain', '.x-grain .grain{display:none}'],
  ];
  const style = document.createElement('style');
  style.textContent = switches.map((s) => s[2]).join('\n');
  document.head.appendChild(style);

  const KEY = 'debug-layers';
  let off: string[] = [];
  try {
    off = JSON.parse(sessionStorage.getItem(KEY) ?? '[]') as string[];
  } catch {
    off = [];
  }
  const panel = document.createElement('div');
  panel.style.cssText =
    'position:fixed;left:12px;top:12px;z-index:1000;padding:8px 10px;color:#fff;' +
    'font:12px/1.7 monospace;background:rgba(0,0,0,0.75);border-radius:4px';
  panel.innerHTML = '<div>tick to REMOVE:</div>';
  for (const ev of ['click', 'pointerdown', 'pointerup', 'mousedown', 'wheel']) {
    panel.addEventListener(ev, (e) => e.stopPropagation());
  }
  for (const [cls, label] of switches) {
    const row = document.createElement('label');
    row.style.display = 'block';
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.checked = off.includes(cls);
    stage.classList.toggle(cls, box.checked);
    box.addEventListener('change', () => {
      stage.classList.toggle(cls, box.checked);
      off = box.checked ? [...off, cls] : off.filter((c) => c !== cls);
      try {
        sessionStorage.setItem(KEY, JSON.stringify(off));
      } catch {
        /* storage unavailable: the choice lasts until reload */
      }
    });
    row.append(box, ` ${label}`);
    panel.appendChild(row);
  }
  root.appendChild(panel);
}
