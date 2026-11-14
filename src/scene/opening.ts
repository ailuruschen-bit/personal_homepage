import type { SceneEls } from './dom';

/**
 * 场景的阶段机。时长写在 scene.css 里，这里只负责切换 class 和回调。
 *
 *   intro  开幕：车厢 → 叶片翻开 → 穿过缝隙 → 窗外
 *   idle   待机：窗外城市 + 标题，等用户示意
 *   back   回程：镜头倒退穿回车厢
 *   hub    主菜单：坐在座位上，物件可聚焦
 *   peek   从主菜单再看向窗外，回到 idle
 */
export type Phase = 'intro' | 'idle' | 'back' | 'hub' | 'peek';

export class Opening {
  private _phase: Phase = 'intro';
  private hintTimer = 0;
  private readonly touch = window.matchMedia?.('(hover:none)').matches ?? false;

  constructor(private readonly els: SceneEls) {
    if (this.touch) {
      const label = els.hint.querySelector('#hintt');
      if (label) label.textContent = '轻点 · 回到车厢';
    }

    // 标题浮现结束 -> 待机；回程镜头结束 -> 主菜单
    els.hero.addEventListener('animationend', (e) => {
      if ((e as AnimationEvent).animationName === 'heroin') this.set('idle');
    });
    els.cam.addEventListener('animationend', (e) => {
      if ((e as AnimationEvent).animationName === 'pull') this.set('hub');
    });

    // 无障碍：系统开启「减少动态效果」时跳过开幕
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) this.set('hub');
  }

  get phase() {
    return this._phase;
  }

  set(p: Phase) {
    this._phase = p;
    this.els.stage.className = `stage ${p}`;
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

  /** 跳过开幕，直接进主菜单 */
  skip() {
    this.set('hub');
  }

  dispose() {
    clearTimeout(this.hintTimer);
  }

  replay() {
    this.els.stage.className = 'stage';
    void this.els.stage.offsetWidth; // 强制重排，重启动画
    this.set('intro');
  }
}
