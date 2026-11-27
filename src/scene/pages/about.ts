import { about } from '../../content/about';
import { tr, type T } from '../../i18n';
import { wornEdge } from './paper';
import { DESK_MARKUP } from './desk';

const PORTRAIT = `${import.meta.env.BASE_URL}assets/portrait.png`;

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

type Row = { when: string; what: T; note?: T };

/** A section of the form: its heading cell, and dated lines ruled under it */
const section = (s: { label: T; rows: readonly Row[] }) => `
  <section class="dos__sec">
    <h3>${tr(s.label)}</h3>
    ${s.rows
      .map(
        (r) =>
          `<div class="dos__line"><span class="dos__when">${r.when}</span><span class="dos__what">${tr(r.what)}${
            r.note ? `<small>${tr(r.note)}</small>` : ''
          }</span></div>`,
      )
      .join('')}
  </section>`;

/**
 * The 档案 page as his own papers on the table: a résumé form with his
 * photo's place clipped at the top right, and his certificates on a second
 * sheet laid over its lower edge, two more askew underneath. Printed rules,
 * typed entries; nothing written by the detective. The page is not over the
 * carriage, so it can be painted freely.
 */
export function renderAbout(): string {
  const n = about.name;
  const form = `
    <header class="dos__title"><h2>${tr(about.title)}</h2></header>
    <i class="dos__holes" aria-hidden="true"></i>
    <div class="dos__head">
      <div class="dos__id">
        <div class="dos__cell dos__cell--name">
          <span class="dos__label">${tr(n.label)}</span>
          <span class="dos__reading">${tr(n.reading)}</span>
          <span class="dos__name">${tr(n.value)}</span>
        </div>
        ${about.fields
          .map(
            (f) =>
              `<div class="dos__cell"><span class="dos__label">${tr(f.label)}</span><span class="dos__value">${tr(f.value)}</span></div>`,
          )
          .join('')}
      </div>
      <figure class="dos__photo">
        <div class="dos__slot">
          <img src="${PORTRAIT}" alt="${tr(about.photoAlt)}" width="84" height="112" />
          <i class="dos__scan" aria-hidden="true"></i>
        </div>
      </figure>
    </div>
    ${section(about.education)}
    ${section(about.work)}`;
  const certs = `${section(about.certs)}${section(about.awards)}<i class="dos__ring" aria-hidden="true"></i>`;
  return `${DESK_MARKUP}<div class="dos">
    ${paper('dos__under dos__under--a', 11)}
    ${paper('dos__under dos__under--b', 23)}
    <div class="dos__filewrap">
      ${CLIP}
      ${paper('dos__file', 37, form, 30)}
    </div>
    ${paper('dos__report', 53, certs)}
  </div>`;
}
