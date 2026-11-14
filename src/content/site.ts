/**
 * 站点级文案。目前全部是占位，接入正式内容时只改这个文件。
 */
export const site = {
  /** 封面主标题，换行用 \n */
  // TODO: 替换为正式标题
  heroTitle: "Hi, I'm\n[NAME]",

  /** 封面副标题，一句话说明你是谁 */
  // TODO: 替换为正式的一句话自我介绍
  heroLede: '[一句话自我介绍]',

  /** 外部链接，在档案页与页脚使用 */
  links: {
    // TODO: 补齐后启用
    github: '',
    email: '',
  },
} as const;
