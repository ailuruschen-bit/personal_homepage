import { about } from '../../content/about';
import { tr, type T } from '../../i18n';

const text = (v: T | string) => (typeof v === 'string' ? v : tr(v));

const row = (f: { label: T; value: T | string }) =>
  `<div class="dos__row"><dt>${tr(f.label)}</dt><dd>${text(f.value)}</dd></div>`;

/** A paper clip, drawn on the pixel grid */
const CLIP = `<svg class="dos__clip" viewBox="0 0 10 26" shape-rendering="crispEdges" aria-hidden="true">
  <path d="M3 24V5a2 2 0 0 1 4 0v17a1 1 0 0 1-2 0V7" fill="none" stroke="currentColor" stroke-width="1.4"/>
</svg>`;

/**
 * The 档案 page as papers on a desk: two sheets askew underneath, the
 * personnel file on top with an empty photo slot clipped to it, and the
 * detective's report laid over its lower edge. The page is not over the
 * carriage, so it can be painted freely.
 */
export function renderAbout(): string {
  return `<div class="dos">
    <div class="dos__under dos__under--a" aria-hidden="true"></div>
    <div class="dos__under dos__under--b" aria-hidden="true"></div>

    <section class="dos__sheet dos__file">
      <header class="dos__bar">
        <span>${tr(about.file)}</span>
        <span>${about.caseNo}</span>
      </header>
      <div class="dos__stamp">${tr(about.stamp)}</div>
      <div class="dos__head">
        <figure class="dos__photo">
          ${CLIP}
          <div class="dos__slot"><span>${tr(about.photo)}</span></div>
          <figcaption class="dos__pencil">${tr(about.photoNote)}</figcaption>
        </figure>
        <dl class="dos__fields dos__fields--head">${about.head.map(row).join('')}</dl>
      </div>
      <dl class="dos__fields">${about.fields.map(row).join('')}</dl>
    </section>

    <section class="dos__sheet dos__report">
      <h2>${tr(about.report)}</h2>
      ${about.notes.map((n) => `<p>${tr(n)}</p>`).join('')}
      <p class="dos__signed">${tr(about.signed)}</p>
    </section>
  </div>`;
}
