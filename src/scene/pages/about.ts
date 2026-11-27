import { about } from '../../content/about';
import { tr, type T } from '../../i18n';
import { wornEdge } from './paper';

const text = (v: T | string) => (typeof v === 'string' ? v : tr(v));

const row = (f: { label: T; value: T | string }) =>
  `<div class="dos__row"><dt>${tr(f.label)}</dt><dd>${text(f.value)}</dd></div>`;

/** A paper clip, drawn as wire */
const CLIP = `<svg class="dos__clip" viewBox="0 0 12 34" aria-hidden="true">
  <path d="M4 31V6.5a3.2 3.2 0 0 1 6.4 0V27a1.9 1.9 0 0 1-3.8 0V9" fill="none" stroke="url(#wire)" stroke-width="1.3" stroke-linecap="round"/>
  <defs><linearGradient id="wire" x1="0" x2="1"><stop offset="0" stop-color="#7d858f"/><stop offset=".45" stop-color="#e4e8ec"/><stop offset="1" stop-color="#8d959e"/></linearGradient></defs>
</svg>`;

/** One sheet: the wrapper casts the shadow, the face is cut to its worn edge */
const paper = (cls: string, seed: number, body = '', fold = 0) =>
  `<div class="paper ${cls}"><div class="paper__face" style="${wornEdge(seed, { fold })}">${body}</div>${
    fold ? `<i class="paper__fold" style="--fold:${fold}px"></i>` : ''
  }</div>`;

/**
 * The 档案 page as papers on a desk: two sheets askew underneath, the
 * personnel file on top with an empty photo slot clipped to it, and the
 * detective's report laid over its lower edge. The page is not over the
 * carriage, so it can be painted freely.
 */
export function renderAbout(): string {
  const file = `
    <header class="dos__bar"><span>${tr(about.file)}</span><span>${about.caseNo}</span></header>
    <div class="dos__stamp">${tr(about.stamp)}</div>
    <i class="dos__holes" aria-hidden="true"></i>
    <div class="dos__head">
      <figure class="dos__photo">
        <div class="dos__slot"><span>${tr(about.photo)}</span></div>
        <figcaption class="dos__pencil">${tr(about.photoNote)}</figcaption>
      </figure>
      <dl class="dos__fields dos__fields--head">${about.head.map(row).join('')}</dl>
    </div>
    <dl class="dos__fields">${about.fields.map(row).join('')}</dl>`;
  const report = `
    <h2>${tr(about.report)}</h2>
    ${about.notes.map((n) => `<p>${tr(n)}</p>`).join('')}
    <p class="dos__signed">${tr(about.signed)}</p>
    <i class="dos__ring" aria-hidden="true"></i>`;
  return `<div class="dos">
    ${paper('dos__under dos__under--a', 11)}
    ${paper('dos__under dos__under--b', 23)}
    <div class="dos__filewrap">
      ${CLIP}
      ${paper('dos__file', 37, file, 30)}
    </div>
    ${paper('dos__report', 53, report)}
  </div>`;
}
