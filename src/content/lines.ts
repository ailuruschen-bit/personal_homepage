/**
 * The detective's lines the story shows on the way to each object and back
 * (docs/12). Chinese, because they are content. `name` is what the object is,
 * said before the cut, so the visitor knows what is in their hands.
 */
export interface ObjectLines {
  name: string;
  open: string;
  close: string;
}

export const objectLines: Record<string, ObjectLines> = {
  about: {
    name: '车票',
    open: '一张票，折过两次，边上起毛了。',
    close: '位置差一厘米他都看得出来。这种人我惹不起。',
  },
  journey: {
    name: '卷起来的线路图',
    open: '自己带的线路图。橡皮筋都勒出印子了。这年头还有人用纸。',
    close: '一个随身带着自己走过的路的人。要么念旧，要么还没走到地方。',
  },
  stack: {
    name: '公文包',
    open: '没上锁。打开之前我总盼着里面有点刺激的。',
    close: '摆得整整齐齐。这人要是干我这行，早就发财了。',
  },
  projects: {
    name: '电脑',
    open: '屏幕没锁，连睡眠都没进。他是真的以为自己一分钟就回来。',
    close: '我看不懂他在写什么。但看得懂一个人半夜还在写。',
  },
};

/** At the hub, when nothing has moved for a while: the site's only nudge */
export const nudge = {
  line: '我站着也不会有人替我翻。',
  hint: '↓ 滚动，一件件看过去 · 或者直接点一件',
};
