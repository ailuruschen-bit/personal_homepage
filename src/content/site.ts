import type { Lang } from '../i18n';

/**
 * Site-wide copy. Everything here is still a placeholder; wiring up the real
 * content means editing this file and nothing else.
 */
export const site = {
  /**
   * The detective's monologue over the city, typed out line by line on the
   * cover (scene/monologue.ts). {braces} mark the occupant's name.
   */
  monologue: {
    zh: ['调查对象：{Ailurus}。', '人刚走。干活吧。'],
    ja: ['調査対象：{Ailurus}。', '本人は席を外した。さて、仕事だ。'],
    en: ['Subject: {Ailurus}.', 'He just stepped out. Time to work.'],
  } as Record<Lang, readonly string[]>,

  /** External links, used on the about page and in the footer */
  links: {
    // TODO: fill in and enable
    github: '',
    email: '',
  },
} as const;
