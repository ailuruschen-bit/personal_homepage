import { site } from '../content/site';
import { hotspots } from './hotspots';
import { pct } from './units';

export interface SceneEls {
  stage: HTMLElement;
  cam: HTMLElement;
  look: HTMLElement;
  ow: HTMLElement;
  hero: HTMLElement;
  /** The cover's monologue lines (monologue.ts) */
  mono: HTMLElement;
  spot: HTMLElement;
  beam: HTMLElement;
  cap: HTMLElement;
  ml: HTMLElement;
  hint: HTMLElement;
  pops: HTMLElement[];
  /** The object lifted toward the lens as the camera reaches it (story.ts) */
  carry: HTMLElement;
  /** Patches of the room without each carried object (story.ts) */
  gones: HTMLElement[];
  /** A chapter's page: an ordinary document, shown instead of the stage (story.ts) */
  page: HTMLElement;
  /** The route: where the visitor is among the chapters, and a way to each (story.ts) */
  route: HTMLElement;
}

const BLIND_SLATS = 14;

/** Build the DOM for the carriage scene and return the nodes touched at runtime */
export function buildScene(root: HTMLElement): SceneEls {
  const slats = Array.from(
    { length: BLIND_SLATS },
    (_, i) => `<i style="top:${((i * 100) / BLIND_SLATS).toFixed(3)}%"></i>`,
  ).join('');

  const pops = hotspots
    .filter((h) => h.box && h.sprite)
    .map((h, i) => {
      const b = h.box!;
      const box = `left:${pct(b.x)};top:${pct(b.y)};width:${pct(b.w)};height:${pct(b.h)};animation-delay:${i}s`;
      return `<div class="pop" data-pop="${h.target}" style="${box}"><i style="background-image:url(${h.sprite})"></i></div>`;
    })
    .join('');

  // Where a carried object was, without it: under the sprites, shown only while
  // the scroll story has the object in the middle of the frame (scroll.ts)
  const gones = hotspots
    .filter((h) => h.gone)
    .map((h) => {
      const f = h.gone!;
      return `<div class="gone" data-gone="${h.target}" style="left:${pct(f.x)};top:${pct(f.y)};width:${pct(f.w)};height:${pct(f.h)};background-image:url(${f.sprite})"></div>`;
    })
    .join('');

  // What stands in front of an object (the rack's rail across the briefcase)
  // goes above the sprites and never moves, so the object lifts behind it
  const fronts = hotspots
    .filter((h) => h.front)
    .map((h) => {
      const f = h.front!;
      return `<div class="pop-front" style="left:${pct(f.x)};top:${pct(f.y)};width:${pct(f.w)};height:${pct(f.h)};background-image:url(${f.sprite})"></div>`;
    })
    .join('');

  const zones = hotspots
    .map((h) => {
      const [x0, y0, x1, y1] = h.zone;
      return (
        `<button type="button" class="hs" data-go="${h.target}" aria-label="${h.object}" ` +
        `style="left:${pct(x0)};top:${pct(y0)};width:${pct(x1 - x0)};height:${pct(y1 - y0)}"></button>`
      );
    })
    .join('');

  root.innerHTML = `
<div class="stage intro" id="stage">
  <div class="sky"></div>

  <!-- Outside: three city layers for parallax -->
  <div class="ow" id="ow"><div class="out">
    <div class="ly c1"></div><div class="ly c2"></div><div class="ly c3"></div><div class="base"></div>
  </div></div>
  <div class="rain2"></div>

  <!-- The carriage. cam drives the opening push, look holds the hub framing and parallax -->
  <div class="cam" id="cam"><div class="look" id="look"><div class="sway"><div class="scene">
    <div class="win">
      <div class="rain"></div><div class="glass"></div>
      <div class="blinds">${slats}<b style="left:22%"></b><b style="right:22%"></b></div>
      <div class="pass"></div>
    </div>

    <div class="ext l"></div><div class="ext r"></div><div class="ext t"></div><div class="ext b"></div>
    <div class="room"></div>
    ${gones}
    ${pops}
    ${fronts}

    <div class="glow g-out"></div><div class="glow g-lamp"></div>
    <div class="glow g-neon"></div><div class="glow g-lap"></div>
    <div class="steam"></div><div class="steam s2"></div><div class="steam s3"></div>
    <div class="cur"></div>
    <div class="vig"></div>
    <div class="spot" id="spot"></div><div class="beam" id="beam"></div>
    <!-- Light sources again above the dimming layer, so the neon and the lamp
         are not dimmed along with everything else while an object is focused -->
    <div class="glow g-lamp"></div><div class="glow g-neon"></div><div class="glow g-out"></div>
    ${zones}
  </div></div></div></div>

  <!-- Cover: the detective's monologue, typed out (monologue.ts) -->
  <div class="hero" id="hero"><div class="txt" id="mono" aria-label="${site.monologue.join(' ').replace(/[{}]/g, '')}"></div></div>

  <!-- The story: the object lifted toward the lens (story.ts) -->
  <div class="carry" id="carry"></div>

  <!-- Idle-state hint for getting back to the carriage -->
  <div class="ghost gt"></div><div class="ghost gb"></div>
  <div class="lens"></div><div class="grain"></div>
  <div class="hint" id="hint"><i>▼</i><span id="hintt">点击 · 回到车厢</span></div>

  <button class="skip" id="skip" type="button">跳过 →</button>
  <div class="ml" id="ml"><i></i></div>
  <div class="cap" id="cap"></div>
  <button class="re" id="re" type="button">↻ 重播开幕</button>
</div>
<main class="page" id="page" hidden></main>
<nav class="route" id="route" aria-label="阅读进度"></nav>`;

  const $ = <T extends HTMLElement>(id: string) => root.querySelector<T>(`#${id}`)!;
  return {
    stage: $('stage'),
    cam: $('cam'),
    look: $('look'),
    ow: $('ow'),
    hero: $('hero'),
    mono: $('mono'),
    spot: $('spot'),
    beam: $('beam'),
    cap: $('cap'),
    ml: $('ml'),
    hint: $('hint'),
    pops: Array.from(root.querySelectorAll<HTMLElement>('.pop')),
    carry: $('carry'),
    gones: Array.from(root.querySelectorAll<HTMLElement>('.gone')),
    page: $('page'),
    route: $('route'),
  };
}
