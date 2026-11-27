import type { T } from '../i18n';

/** Interface copy, in every language. The story's lines are in lines.ts */
export const ui = {
  hintClick: { zh: '点击 · 回到车厢', ja: 'クリック · 車内へ戻る', en: 'Click · back inside' },
  hintTap: { zh: '轻点 · 回到车厢', ja: 'タップ · 車内へ戻る', en: 'Tap · back inside' },
  skip: { zh: '跳过 →', ja: 'スキップ →', en: 'Skip →' },
  replay: { zh: '↻ 重播开幕', ja: '↻ オープニング再生', en: '↻ Replay opening' },
  progress: { zh: '阅读进度', ja: '進行状況', en: 'Progress' },
  language: { zh: '语言', ja: '言語', en: 'Language' },
  /** The first stop on the route: the carriage itself */
  carriage: { zh: '车厢', ja: '車内', en: 'Carriage' },
  /** The caption for the window at the hub */
  outside: { zh: '窗外', ja: '窓の外', en: 'Outside' },
  pageHome: { zh: '← 回到车厢', ja: '← 車内へ戻る', en: '← Back to the carriage' },
  pageUp: {
    zh: '↑ 向上滚动，回到车厢',
    ja: '↑ 上へスクロールで車内へ',
    en: '↑ Scroll up to go back',
  },
  pageEnd: {
    zh: '↓ 继续向下，回到车厢',
    ja: '↓ 下へスクロールで車内へ',
    en: '↓ Scroll on to go back',
  },
} satisfies Record<string, T>;

/** "↓ on to the next chapter" */
export const pageNext: Record<keyof T, (title: string) => string> = {
  zh: (t) => `↓ 继续向下：${t}`,
  ja: (t) => `↓ 次へ：${t}`,
  en: (t) => `↓ Next: ${t}`,
};

/** The brass prompt under a line, naming the page ahead */
export const openPrompt: Record<keyof T, (title: string) => string> = {
  zh: (t) => `继续下滑 ▼ 翻开${t}`,
  ja: (t) => `下へスクロール ▼ ${t}を開く`,
  en: (t) => `Keep scrolling ▼ to open ${t}`,
};

/** What each object at the hub is called in the caption, by target */
export const objectNames: Record<string, T> = {
  cover: { zh: '车窗', ja: '窓', en: 'Window' },
  projects: { zh: '电脑', ja: 'ノートPC', en: 'Laptop' },
  about: { zh: '车票', ja: '切符', en: 'Ticket' },
  stack: { zh: '公文包', ja: 'ブリーフケース', en: 'Briefcase' },
  journey: { zh: '线路图', ja: '路線図', en: 'Route map' },
};
