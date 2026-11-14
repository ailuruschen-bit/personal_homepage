import { site } from '../content/site';
import { hotspots, popStyle } from './hotspots';
import { pct } from './units';

export interface SceneEls {
  stage: HTMLElement;
  cam: HTMLElement;
  look: HTMLElement;
  ow: HTMLElement;
  hero: HTMLElement;
  spot: HTMLElement;
  beam: HTMLElement;
  cap: HTMLElement;
  ml: HTMLElement;
  hint: HTMLElement;
  pops: HTMLElement[];
}

const BLIND_SLATS = 14;

/** 生成车厢场景的 DOM，并返回需要在运行时操作的节点 */
export function buildScene(root: HTMLElement): SceneEls {
  const slats = Array.from(
    { length: BLIND_SLATS },
    (_, i) => `<i style="top:${((i * 100) / BLIND_SLATS).toFixed(3)}%"></i>`,
  ).join('');

  const pops = hotspots
    .filter((h) => h.shape)
    .map((h, i) => {
      const s = popStyle(h.shape!);
      const css =
        `left:${s.left};top:${s.top};width:${s.width};height:${s.height};` +
        `background-size:${s.backgroundSize};background-position:${s.backgroundPosition};` +
        `clip-path:${s.clipPath};animation-delay:${i}s`;
      return `<div class="pop" data-pop="${h.target}" style="${css}"></div>`;
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

  const [l1, l2] = site.heroTitle.split('\n');

  root.innerHTML = `
<div class="stage intro" id="stage">
  <div class="sky"></div><div class="stars"></div>

  <!-- 窗外：三层城市做视差 -->
  <div class="ow" id="ow"><div class="out">
    <div class="ly c1"></div><div class="ly c2"></div><div class="ly c3"></div><div class="base"></div>
  </div></div>
  <div class="rain2"></div>

  <!-- 车厢。cam 负责开幕的推进，look 负责主菜单的构图与视差 -->
  <div class="cam" id="cam"><div class="look" id="look"><div class="sway"><div class="scene">
    <div class="win">
      <div class="rain"></div><div class="glass"></div>
      <div class="blinds">${slats}<b style="left:22%"></b><b style="right:22%"></b></div>
      <div class="pass"></div>
    </div>

    <div class="ext l"></div><div class="ext r"></div><div class="ext t"></div><div class="ext b"></div>
    <div class="room"></div>
    ${pops}

    <div class="glow g-out"></div><div class="glow g-lamp"></div>
    <div class="glow g-neon"></div><div class="glow g-lap"></div>
    <div class="steam"></div><div class="steam s2"></div><div class="steam s3"></div>
    <div class="cur"></div>
    <div class="vig"></div>
    <div class="spot" id="spot"></div><div class="beam" id="beam"></div>
    <!-- 压暗层之上再放一遍光源，聚焦时霓虹与台灯不被压掉 -->
    <div class="glow g-lamp"></div><div class="glow g-neon"></div><div class="glow g-out"></div>
    ${zones}
  </div></div></div></div>

  <!-- 封面标题 -->
  <div class="hero" id="hero"><div class="txt">
    <h1>${l1}<br>${l2}<span style="color:var(--leica)">_</span></h1>
    <p>${site.heroLede}</p>
  </div></div>

  <!-- 待机时的回车厢引导 -->
  <div class="ghost gt"></div><div class="ghost gb"></div>
  <div class="hint" id="hint"><i>▼</i><span id="hintt">点击 · 回到车厢</span></div>

  <button class="skip" id="skip" type="button">跳过 →</button>
  <div class="ml" id="ml"><i></i></div>
  <div class="cap" id="cap"></div>
  <button class="re" id="re" type="button">↻ 重播开幕</button>
</div>`;

  const $ = <T extends HTMLElement>(id: string) => root.querySelector<T>(`#${id}`)!;
  return {
    stage: $('stage'),
    cam: $('cam'),
    look: $('look'),
    ow: $('ow'),
    hero: $('hero'),
    spot: $('spot'),
    beam: $('beam'),
    cap: $('cap'),
    ml: $('ml'),
    hint: $('hint'),
    pops: Array.from(root.querySelectorAll<HTMLElement>('.pop')),
  };
}
