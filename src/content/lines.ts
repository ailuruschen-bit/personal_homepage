import type { T } from '../i18n';

/**
 * The detective's lines the story shows on the way to each object and back
 * (docs/12), in every language. `name` is what the object is, said before the
 * cut, so the visitor knows what is in their hands.
 */
export interface ObjectLines {
  name: T;
  open: T;
  close: T;
}

export const objectLines: Record<string, ObjectLines> = {
  about: {
    name: { zh: '车票', ja: '切符', en: 'The ticket' },
    open: {
      zh: '一张票，折过两次，边上起毛了。',
      ja: '二度折られた切符。縁が毛羽立ってる。',
      en: 'A ticket. Folded twice, frayed at the edges.',
    },
    close: {
      zh: '位置差一厘米他都看得出来。这种人我惹不起。',
      ja: '一センチずれても気づく男だ。こういう相手は厄介だ。',
      en: "He'd notice if it moved a centimetre. I don't cross people like that.",
    },
  },
  journey: {
    name: { zh: '卷起来的线路图', ja: '丸めた路線図', en: 'A rolled-up route map' },
    open: {
      zh: '自己带的线路图。橡皮筋都勒出印子了。这年头还有人用纸。',
      ja: '自前の路線図。輪ゴムの跡までついてる。今どき紙とはね。',
      en: "His own route map. The rubber band's left a mark. Who still uses paper?",
    },
    close: {
      zh: '一个随身带着自己走过的路的人。要么念旧，要么还没走到地方。',
      ja: '歩いてきた道を持ち歩く男。懐かしんでるのか、まだ着いてないのか。',
      en: "A man who carries the road he's travelled. Sentimental, or not there yet.",
    },
  },
  stack: {
    name: { zh: '公文包', ja: 'ブリーフケース', en: 'The briefcase' },
    open: {
      zh: '没上锁。打开之前我总盼着里面有点刺激的。',
      ja: '鍵はかかってない。開ける前は、いつも何か刺激的なのを期待しちまう。',
      en: 'Unlocked. I always hope for something exciting before I open one.',
    },
    close: {
      zh: '摆得整整齐齐。这人要是干我这行，早就发财了。',
      ja: 'きっちり整頓されてる。こいつが俺の商売をやってたら、とっくに稼いでるな。',
      en: "Everything squared away. If he did my job, he'd be rich by now.",
    },
  },
  projects: {
    name: { zh: '电脑', ja: 'ノートPC', en: 'The laptop' },
    open: {
      zh: '屏幕没锁，连睡眠都没进。他是真的以为自己一分钟就回来。',
      ja: '画面ロックなし、スリープすらしてない。本気で一分で戻るつもりだったらしい。',
      en: "No lock screen, not even asleep. He really thought he'd be back in a minute.",
    },
    close: {
      zh: '我看不懂他在写什么。但看得懂一个人半夜还在写。',
      ja: '何を書いてるのかは分からん。だが、夜中にまだ書いてる男のことは分かる。',
      en: "I can't read what he's writing. I can read a man still writing at this hour.",
    },
  },
};

/** At the hub with nothing moving: the one nudge, in character */
export const nudge: { line: T; hint: T } = {
  line: {
    zh: '我站着也不会有人替我翻。',
    ja: '突っ立ってても、誰も代わりに調べちゃくれない。',
    en: "Standing here won't search the place for me.",
  },
  hint: {
    zh: '向下滚动 ▼ 一件件看过去，或者直接点一件',
    ja: '下へスクロール ▼ 順に見ていくか、ひとつクリック',
    en: 'Scroll down ▼ to go through them, or click one',
  },
};
