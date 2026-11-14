/**
 * 板块注册表。
 *
 * 新增板块：在这里加一条；需要从车厢进入的话，再去 scene/hotspots.ts
 * 注册一个 target 为该 id 的物件。
 */
export interface SectionDef {
  /** 路由 id，对应 #/about 这样的地址 */
  id: string;
  /** 板块名，显示在车厢聚焦提示与页面标题 */
  title: string;
  /** 页面导语 */
  lede: string;
  /** 页面里预留的内容块，正式内容接入后替换 */
  blocks: string[];
}

export const sections: SectionDef[] = [
  {
    id: 'about',
    title: '档案',
    lede: '[TODO: 自我介绍导语]',
    blocks: ['[TODO: 基本信息]', '[TODO: 自述]', '[TODO: 头像与照片]'],
  },
  {
    id: 'journey',
    title: '经历',
    lede: '[TODO: 经历导语]',
    blocks: ['[TODO: 学习经历]', '[TODO: 工作经历]', '[TODO: 里程碑]'],
  },
  {
    id: 'stack',
    title: '技术栈',
    lede: '[TODO: 技术栈导语]',
    blocks: ['[TODO: 技能分组]', '[TODO: 技能与项目、笔记的关联]', '[TODO: 正在学习]'],
  },
  {
    id: 'projects',
    title: '项目',
    lede: '[TODO: 项目导语]',
    blocks: ['[TODO: 项目 1]', '[TODO: 项目 2]', '[TODO: 项目 3]'],
  },
  {
    id: 'notes',
    title: '笔记',
    lede: '[TODO: 笔记导语]',
    blocks: ['[TODO: 分类]', '[TODO: 列表]', '[TODO: 搜索]', '[TODO: 阅读页]'],
  },
  {
    id: 'hobby',
    title: '兴趣',
    lede: '[TODO: 兴趣导语]',
    blocks: ['[TODO: 兴趣 1]', '[TODO: 兴趣 2]', '[TODO: 兴趣 3]'],
  },
  {
    id: 'chat',
    title: '聊聊',
    lede: '[TODO: 对话板块导语]',
    blocks: ['[TODO: 对话界面]', '[TODO: 机器可读入口]'],
  },
];

export const sectionById = (id: string): SectionDef | null =>
  sections.find((s) => s.id === id) ?? null;
