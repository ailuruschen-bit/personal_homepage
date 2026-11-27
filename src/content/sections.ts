import type { T } from '../i18n';

/**
 * Section registry.
 *
 * To add a section, add an entry here. To make it reachable from the carriage,
 * also register an object in scene/hotspots.ts whose target is this id.
 */
export interface SectionDef {
  /** Route id, that is the #/about part of the URL */
  id: string;
  /** Section name, shown in the focus caption and as the page title */
  title: T;
  /** Page lede */
  lede: string;
  /** Placeholder blocks on the page, replaced once real content lands */
  blocks: string[];
}

export const sections: SectionDef[] = [
  {
    id: 'about',
    title: { zh: '档案', ja: 'プロフィール', en: 'Profile' },
    lede: '[TODO: 自我介绍导语]',
    blocks: ['[TODO: 基本信息]', '[TODO: 自述]', '[TODO: 头像与照片]'],
  },
  {
    id: 'journey',
    title: { zh: '经历', ja: '経歴', en: 'Journey' },
    lede: '[TODO: 经历导语]',
    blocks: ['[TODO: 学习经历]', '[TODO: 工作经历]', '[TODO: 里程碑]'],
  },
  {
    id: 'stack',
    title: { zh: '技术栈', ja: '技術スタック', en: 'Stack' },
    lede: '[TODO: 技术栈导语]',
    blocks: ['[TODO: 技能分组]', '[TODO: 技能与项目、笔记的关联]', '[TODO: 正在学习]'],
  },
  {
    id: 'projects',
    title: { zh: '项目', ja: 'プロジェクト', en: 'Projects' },
    lede: '[TODO: 项目导语]',
    blocks: ['[TODO: 项目 1]', '[TODO: 项目 2]', '[TODO: 项目 3]'],
  },
  {
    id: 'notes',
    title: { zh: '笔记', ja: 'ノート', en: 'Notes' },
    lede: '[TODO: 笔记导语]',
    blocks: ['[TODO: 分类]', '[TODO: 列表]', '[TODO: 搜索]', '[TODO: 阅读页]'],
  },
  {
    id: 'hobby',
    title: { zh: '兴趣', ja: '趣味', en: 'Hobbies' },
    lede: '[TODO: 兴趣导语]',
    blocks: ['[TODO: 兴趣 1]', '[TODO: 兴趣 2]', '[TODO: 兴趣 3]'],
  },
  {
    id: 'chat',
    title: { zh: '聊聊', ja: '話そう', en: 'Chat' },
    lede: '[TODO: 对话板块导语]',
    blocks: ['[TODO: 对话界面]', '[TODO: 机器可读入口]'],
  },
];

export const sectionById = (id: string): SectionDef | null =>
  sections.find((s) => s.id === id) ?? null;
