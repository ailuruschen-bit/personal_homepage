import type { T } from '../i18n';

/** The same in every language */
const all = (s: string): T => ({ zh: s, ja: s, en: s });

/**
 * The 档案 page: his own papers, as the detective finds them on the table.
 * Nothing here is the detective's: a résumé of the occupant's own, and the
 * certificates under it (scene/pages/about.ts). From his 履歴書; the address,
 * phone, date of birth, family and residence status are left out on purpose.
 */
export const about = {
  /** What he calls it himself: a passenger's own account of who he is */
  title: { zh: '乘客自述', ja: '乗客の自己申告', en: 'In his own words' },
  photoAlt: {
    zh: '陈靖的证件照（像素风）',
    ja: '陳靖の証明写真（ピクセルアート）',
    en: 'Portrait of Jing Chen, in pixel art',
  },

  name: {
    label: { zh: '姓名', ja: '氏名', en: 'Name' },
    reading: { zh: 'Chén Jìng', ja: 'ちん せい', en: 'Ailurus' },
    value: { zh: '陈 靖', ja: '陳 靖', en: 'Jing Chen' },
  },
  fields: [
    {
      label: { zh: '现居', ja: '所在地', en: 'Based in' },
      value: { zh: '日本 · 东京', ja: '東京都', en: 'Tokyo, Japan' },
    },
    { label: { zh: '邮箱', ja: 'E-mail', en: 'Email' }, value: all('ailuruschen@gmail.com') },
    {
      label: { zh: '语言', ja: '語学', en: 'Languages' },
      value: {
        zh: '中文（母语） · 日语 N1 · 英语 CET-6',
        ja: '中国語（母語）・日本語 N1・英語 CET-6',
        en: 'Chinese (native) · Japanese N1 · English CET-6',
      },
    },
  ],

  education: {
    label: { zh: '学历', ja: '学歴', en: 'Education' },
    rows: [
      {
        when: '2020.09 – 2024.06',
        what: {
          zh: '华中师范大学 · 日语专业',
          ja: '華中師範大学 日本語学科 卒業',
          en: 'Central China Normal University — Japanese',
        },
      },
    ],
  },
  work: {
    label: { zh: '工作经历', ja: '職歴', en: 'Experience' },
    rows: [
      {
        when: '2026.04 –',
        what: {
          zh: '株式会社アルプス技研 · 至今',
          ja: '株式会社アルプス技研 入社 現在に至る',
          en: 'Alps Giken Co., Ltd. — present',
        },
      },
      {
        when: '2024.11 – 2026.03',
        what: {
          zh: '株式会社青凌 · 东京总部',
          ja: '株式会社青凌 東京本部',
          en: 'Seiryo Co., Ltd. — Tokyo head office',
        },
      },
      {
        when: '2023.12 – 2024.08',
        what: {
          zh: '株式会社青凌 · 武汉分公司 编程研修',
          ja: '株式会社青凌 中国・武漢支社 プログラミング研修',
          en: 'Seiryo Co., Ltd. — Wuhan branch, programming training',
        },
      },
    ],
  },

  certs: {
    label: { zh: '资格证书', ja: '免許・資格', en: 'Certifications' },
    rows: [
      { when: '2026.05', what: all('AWS Certified Solutions Architect – Professional') },
      { when: '2026.04', what: all('AWS Certified Solutions Architect – Associate') },
      {
        when: '2023.08',
        what: {
          zh: '大学英语六级（CET-6）',
          ja: '中国大学英語六級（CET-6）',
          en: 'College English Test Band 6 (CET-6)',
        },
      },
      {
        when: '2022.06',
        what: {
          zh: '日本语能力测试 N1',
          ja: '日本語能力試験 N1',
          en: 'Japanese-Language Proficiency Test N1',
        },
      },
    ],
  },
  awards: {
    label: { zh: '获奖', ja: '受賞歴', en: 'Awards' },
    rows: [
      {
        when: '2026.05',
        what: {
          zh: 'Unbound Creativity with TRAE SOLO（Japan Productivity Enhancement 赛道）第一名',
          ja: 'Unbound Creativity with TRAE SOLO（Japan Productivity Enhancement Track）1位',
          en: '1st place, Unbound Creativity with TRAE SOLO — Japan Productivity Enhancement Track',
        },
        note: {
          zh: '团队作品 StyleAI，负责用 FastAPI 集成 AI 模型',
          ja: 'チーム作品 StyleAI／FastAPI による AI モデル統合を担当',
          en: 'Team entry StyleAI; I integrated the AI models with FastAPI',
        },
      },
    ],
  },
} as const;
