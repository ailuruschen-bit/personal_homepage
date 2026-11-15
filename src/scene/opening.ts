import type { SceneEls } from './dom';

/**
 * 场景的阶段机。固定开场时长写在 scene.css；中途跳过的回位补间由这里管理。
 *
 *   intro  开幕：车厢 → 叶片翻开 → 穿过缝隙 → 窗外
 *   idle   待机：窗外城市 + 标题，等用户示意
 *   back   回程：镜头倒退穿回车厢
 *   settling  跳过开幕：从当前画面回位，完成后才开放主菜单交互
 *   hub    主菜单：坐在座位上，物件可聚焦
 *   peek   从主菜单再看向窗外，回到 idle
 */
export type Phase = 'intro' | 'idle' | 'back' | 'settling' | 'hub' | 'peek';

export class Opening {
  private _phase: Phase = 'intro';
  private hintTimer = 0;
  private skipAnimations: Animation[] = [];
  /** 阶段切换时同步回调（在改完 class 之后、浏览器计算样式之前） */
  onPhase?: (p: Phase) => void;
  private readonly touch = window.matchMedia?.('(hover:none)').matches ?? false;
  /** 跳过开幕时要一起接上的两层：窗外的城市、窗外的雨 */
  private readonly out: HTMLElement;
  private readonly rain: HTMLElement;

  constructor(private readonly els: SceneEls) {
    this.out = els.ow.querySelector<HTMLElement>('.out')!;
    this.rain = els.stage.querySelector<HTMLElement>('.rain2')!;
    if (this.touch) {
      const label = els.hint.querySelector('#hintt');
      if (label) label.textContent = '轻点 · 回到车厢';
    }

    // 标题浮现结束 -> 待机；回程镜头结束 -> 主菜单
    els.hero.addEventListener('animationend', (e) => {
      if (
        e.target === els.hero &&
        (e as AnimationEvent).animationName === 'heroin' &&
        (this._phase === 'intro' || this._phase === 'peek')
      )
        this.set('idle');
    });
    els.cam.addEventListener('animationend', (e) => {
      // 回程是 push 倒放；子元素的动画事件也会冒泡上来，只认镜头自己的
      const own = e.target === els.cam && (e as AnimationEvent).animationName === 'push';
      if (own && this._phase === 'back') this.set('hub');
    });

    // 无障碍：系统开启「减少动态效果」时跳过开幕
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) this.set('hub');
  }

  get phase() {
    return this._phase;
  }

  set(p: Phase) {
    this.cancelSkipAnimations();
    this._phase = p;
    this.els.stage.className = `stage ${p}`;
    // 立刻把这个阶段的样式算出来，别攒到下一帧。
    // 两次切换挤在同一帧时中间那个阶段会被整个跳过，而回程和开幕用的是同一条 push 动画：
    // 动画名没变，浏览器就把它当成同一段接着算，进度还停在上一段的结尾，
    // 于是回程一帧都不走，画面卡在半路。
    void this.els.stage.offsetWidth;
    this.onPhase?.(p);
    clearTimeout(this.hintTimer);
    // 触摸设备没有「移动鼠标」这个信号，待机 2 秒后自动给提示
    if (p === 'idle' && this.touch) {
      this.hintTimer = window.setTimeout(() => this.els.stage.classList.add('hinted'), 2000);
    }
  }

  /** 待机时首次移动指针：显示回车厢的引导 */
  hintOnMove() {
    if (this._phase === 'idle') this.els.stage.classList.add('hinted');
  }

  /** 待机 -> 回车厢 */
  back() {
    if (this._phase === 'idle') this.set('back');
  }

  /**
   * 从当前画面补间到落座构图。回位期间不启用主菜单的循环动画和交互，
   * 避免镜头仍在缩放时，物品的滤镜与视差已经开始切换。
   */
  skip() {
    if (this._phase !== 'intro') return;
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
      this.set('hub');
      return;
    }
    const resume = [this.els.cam, this.out, this.rain].map((el) => {
      const now = getComputedStyle(el);
      const from: Keyframe = { transform: now.transform, opacity: now.opacity };
      // 末帧留空表示「元素在新阶段里本该是的样子」，由浏览器填
      return () =>
        el.animate([from, {}], { duration: 700, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
    });
    this.set('settling');
    const animations = resume.map((play) => play());
    this.skipAnimations = animations;
    void Promise.all(animations.map((animation) => animation.finished)).then(
      () => {
        // 重播、销毁或其它阶段切换后，旧回调不得再把场景切回主菜单。
        if (this.skipAnimations === animations && this._phase === 'settling') this.set('hub');
      },
      () => {
        /* 阶段切换主动取消动画，finished 的拒绝属于正常清理。 */
      },
    );
  }

  private cancelSkipAnimations() {
    for (const animation of this.skipAnimations) animation.cancel();
    this.skipAnimations = [];
  }

  dispose() {
    this.cancelSkipAnimations();
    clearTimeout(this.hintTimer);
  }

  replay() {
    this.cancelSkipAnimations();
    this.els.stage.className = 'stage';
    void this.els.stage.offsetWidth; // 强制重排，重启动画
    this.set('intro');
  }
}
