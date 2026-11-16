import { CAMERA, OBJECTS, WINDOW } from './geometry.gen';
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
  ]
    .map(([c, t]) => `<div style="color:${c}">■ ${t}</div>`)
    .join('');
  root.appendChild(legend);

  scene.appendChild(svg);
}
