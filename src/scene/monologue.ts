import { site } from '../content/site';

/** Typing speed, ms per character, and the pause after each line */
const CHAR_MS = 45;
const LINE_PAUSE = 420;

type Run = { text: string; name: boolean };

/** A line split at its {braces}: the name is set apart in brass */
const runs = (line: string): Run[] =>
  line
    .split(/(\{[^}]*\})/)
    .filter(Boolean)
    .map((t) =>
      t.startsWith('{') ? { text: t.slice(1, -1), name: true } : { text: t, name: false },
    );

const escape = (t: string) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');

/** The first n characters of a line, as markup */
function partial(line: Run[], n: number): string {
  let out = '';
  for (const r of line) {
    if (n <= 0) break;
    const t = escape(r.text.slice(0, n));
    out += r.name ? `<b>${t}</b>` : t;
    n -= r.text.length;
  }
  return out;
}

/**
 * The detective's monologue on the cover. Typed out the first time the city is
 * reached; every later visit outside shows it whole at once. It sits over the
 * city, never over the carriage, so its text can change per frame (docs/09).
 */
export class Monologue {
  private readonly lines = site.monologue.map(runs);
  private readonly els: HTMLElement[];
  private played = false;
  private timer = 0;

  constructor(private readonly root: HTMLElement) {
    this.els = this.lines.map(() => {
      const p = document.createElement('p');
      root.append(p);
      return p;
    });
  }

  /** The city is on screen: type the lines out, or show them if seen before */
  play() {
    if (this.played) return this.showAll();
    this.played = true;
    let i = 0;
    let n = 0;
    const tick = () => {
      const line = this.lines[i]!;
      const len = line.reduce((a, r) => a + r.text.length, 0);
      n++;
      this.els[i]!.innerHTML = partial(line, n) + '<i class="caret"></i>';
      if (n < len) return void (this.timer = window.setTimeout(tick, CHAR_MS));
      if (i === this.lines.length - 1) return this.root.classList.add('done');
      this.els[i]!.innerHTML = partial(line, len);
      i++;
      n = 0;
      this.timer = window.setTimeout(tick, LINE_PAUSE);
    };
    this.root.classList.remove('done');
    this.timer = window.setTimeout(tick, 200);
  }

  showAll() {
    clearTimeout(this.timer);
    this.played = true;
    this.lines.forEach((line, i) => {
      const last = i === this.lines.length - 1;
      this.els[i]!.innerHTML = partial(line, Infinity) + (last ? '<i class="caret"></i>' : '');
    });
    this.root.classList.add('done');
  }

  dispose() {
    clearTimeout(this.timer);
  }
}
