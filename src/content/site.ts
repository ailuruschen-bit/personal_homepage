/**
 * Site-wide copy. Everything here is still a placeholder; wiring up the real
 * content means editing this file and nothing else.
 */
export const site = {
  /**
   * The detective's monologue over the city, typed out line by line on the
   * cover (scene/monologue.ts). {braces} mark the occupant's name.
   */
  monologue: [
    '委托书上只有一行：查查 {Ailurus} 是个什么样的人。',
    '人刚离开包厢，时间不多。',
    '干活吧。',
  ],

  /** External links, used on the about page and in the footer */
  links: {
    // TODO: fill in and enable
    github: '',
    email: '',
  },
} as const;
