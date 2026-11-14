import './sections.css';
import type { SectionDef } from '../content/sections';

/**
 * 板块页的外壳。
 *
 * 目前所有板块共用这一个版式：顶栏 + 标题 + 占位块。
 * 正式内容接入时，可以给个别板块写自己的渲染函数（见 index.ts 的 renderers）。
 */
export function renderSection(section: SectionDef, onBack: () => void): HTMLElement {
  const page = document.createElement('div');
  page.className = 'page';
  page.innerHTML = `
  <header class="page__bar">
    <button class="page__back" type="button" data-back>← 回车厢</button>
    <span class="page__kicker">${section.id.toUpperCase()}</span>
  </header>
  <main class="page__body">
    <h1 class="page__title">${section.title}</h1>
    <p class="page__lede">${section.lede}</p>
    ${section.blocks
      .map(
        (b) => `
    <section class="ph">
      <span class="ph__tag">PLACEHOLDER</span>
      <p>${b}</p>
    </section>`,
      )
      .join('')}
  </main>`;

  page.querySelector<HTMLButtonElement>('[data-back]')!.addEventListener('click', onBack);
  return page;
}
