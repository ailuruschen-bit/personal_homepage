/**
 * Three languages: Chinese, Japanese, English. The visitor's choice is kept in
 * localStorage; before they choose, the browser's own languages decide, and
 * anything else gets English. Changing it re-labels the page in place: the
 * scene keeps its state (onLang).
 */
export type Lang = 'zh' | 'ja' | 'en';
export const LANGS: readonly Lang[] = ['zh', 'ja', 'en'];
/** A piece of copy in every language */
export type T = Record<Lang, string>;

const KEY = 'lang';
const HTML_LANG: Record<Lang, string> = { zh: 'zh-CN', ja: 'ja', en: 'en' };

function detect(): Lang {
  try {
    const saved = localStorage.getItem(KEY);
    if (saved && (LANGS as readonly string[]).includes(saved)) return saved as Lang;
  } catch {
    // storage may be off; fall through to the browser's languages
  }
  for (const l of navigator.languages ?? [navigator.language]) {
    const tag = l.toLowerCase();
    if (tag.startsWith('zh')) return 'zh';
    if (tag.startsWith('ja')) return 'ja';
    if (tag.startsWith('en')) return 'en';
  }
  return 'en';
}

let current = detect();
document.documentElement.lang = HTML_LANG[current];
const listeners = new Set<() => void>();

export const lang = (): Lang => current;

/** The copy in the current language */
export const tr = <V>(t: Record<Lang, V>): V => t[current];

export function setLang(l: Lang) {
  if (l === current) return;
  current = l;
  try {
    localStorage.setItem(KEY, l);
  } catch {
    // not remembered, still switched
  }
  document.documentElement.lang = HTML_LANG[l];
  for (const f of listeners) f();
}

/** Called after every change of language; returns the unsubscribe */
export function onLang(f: () => void): () => void {
  listeners.add(f);
  return () => listeners.delete(f);
}
