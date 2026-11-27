import type { T } from '../i18n';

/** Not filled in yet, in every language */
export const TBD: T = { zh: '[待填]', ja: '[未記入]', en: '[TBD]' };

/**
 * The 档案 page: a personnel file, laid on the table with the other papers
 * under it (scene/pages/about.ts). The values are still to come; the codename
 * is the one on the cover.
 */
export const about = {
  file: { zh: '人员档案', ja: '人物調書', en: 'Personnel file' },
  caseNo: 'No. 001',
  stamp: { zh: '调查中', ja: '調査中', en: 'Under review' },
  photo: { zh: '照片', ja: '写真', en: 'Photo' },
  /** The detective's pencil note by the empty photo slot */
  photoNote: { zh: '照片：待取证', ja: '写真：未入手', en: 'Photo: not yet obtained' },
  /** Beside the photo: who he is at a glance */
  head: [
    { label: { zh: '代号', ja: 'コードネーム', en: 'Codename' }, value: 'Ailurus' },
    { label: { zh: '姓名', ja: '氏名', en: 'Name' }, value: TBD },
    { label: { zh: '职业', ja: '職業', en: 'Occupation' }, value: TBD },
  ],
  /** Under it, the rest of the form */
  fields: [
    { label: { zh: '所在地', ja: '所在地', en: 'Based in' }, value: TBD },
    { label: { zh: '语言', ja: '言語', en: 'Languages' }, value: TBD },
    { label: { zh: '专长', ja: '専門', en: 'Speciality' }, value: TBD },
    { label: { zh: '联系方式', ja: '連絡先', en: 'Contact' }, value: TBD },
  ],
  report: { zh: '调查报告', ja: '調査報告', en: 'Field report' },
  /** The report's paragraphs, in the detective's voice */
  notes: [TBD, TBD, TBD],
  signed: { zh: '—— 记录人：侦探', ja: '—— 記録：探偵', en: '— Filed by: the detective' },
} as const;
