import './sections.css';
import type { SectionDef } from '../content/sections';

/**
 * Shell for a section page.
 *
 * Every section currently shares this one layout: top bar, title, placeholder
 * blocks. Once real content lands, individual sections can get their own
 * render function.
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
