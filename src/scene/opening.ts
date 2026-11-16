import type { SceneEls } from './dom';

/**
 * Phase machine for the scene. The fixed opening timings live in scene.css;
 * the tween that settles the camera after a mid-opening skip is managed here.
 *
 *   intro     opening: carriage -> blinds tilt open -> through the gap -> outside
 *   idle      standby: city outside plus the headline, waiting for the visitor
 *   back      return: the camera retreats back through the window
 *   settling  skip: ease from wherever the opening was; the hub stays inert until done
 *   hub       main menu: seated, objects can take focus
 *   peek      look back out of the window from the hub, ending in idle
 */
export type Phase = 'intro' | 'idle' | 'back' | 'settling' | 'hub' | 'peek';

export class Opening {
  private _phase: Phase = 'intro';
  private hintTimer = 0;
  private skipAnimations: Animation[] = [];
  /** Called synchronously on a phase change, after the class is set and before style recalc */
  onPhase?: (p: Phase) => void;
  private readonly touch = window.matchMedia?.('(hover:none)').matches ?? false;
  /** The two layers that must be eased along when the opening is skipped: city and rain */
  private readonly out: HTMLElement;
  private readonly rain: HTMLElement;

  constructor(private readonly els: SceneEls) {
    this.out = els.ow.querySelector<HTMLElement>('.out')!;
    this.rain = els.stage.querySelector<HTMLElement>('.rain2')!;
    if (this.touch) {
      const label = els.hint.querySelector('#hintt');
      if (label) label.textContent = '轻点 · 回到车厢';
    }

    // Headline finished fading in -> idle; return camera finished -> hub
    els.hero.addEventListener('animationend', (e) => {
      if (
        e.target === els.hero &&
        (e as AnimationEvent).animationName === 'heroin' &&
        (this._phase === 'intro' || this._phase === 'peek')
      )
        this.set('idle');
    });
    els.cam.addEventListener('animationend', (e) => {
      // The return plays push in reverse. Child animation events bubble up here too,
      // so only accept the camera's own.
      const own = e.target === els.cam && (e as AnimationEvent).animationName === 'push';
      if (own && this._phase === 'back') this.set('hub');
    });

    // Accessibility: skip the opening when the system asks for reduced motion
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) this.set('hub');
  }

  get phase() {
    return this._phase;
  }

  set(p: Phase) {
    this.cancelSkipAnimations();
    this._phase = p;
    this.els.stage.className = `stage ${p}`;
    // Force this phase's styles to be computed now rather than next frame.
    // Two phase changes landing in the same frame skip the middle phase entirely, and
    // the return reuses the same push animation as the opening: with the animation name
    // unchanged the browser treats it as the same run and keeps the progress from the
    // previous one, which has already finished. The return would then never advance a
    // single frame and the scene would stay stuck halfway.
    void this.els.stage.offsetWidth;
    this.onPhase?.(p);
    clearTimeout(this.hintTimer);
    // Touch devices have no "pointer moved" signal, so hint automatically after 2s of idle
    if (p === 'idle' && this.touch) {
      this.hintTimer = window.setTimeout(() => this.els.stage.classList.add('hinted'), 2000);
    }
  }

  /** First pointer move while idle: reveal the hint for getting back to the carriage */
  hintOnMove() {
    if (this._phase === 'idle') this.els.stage.classList.add('hinted');
  }

  /** idle -> back to the carriage */
  back() {
    if (this._phase === 'idle') this.set('back');
  }

  /**
   * Tween from whatever is on screen to the seated framing. The hub's looping
   * animations and interactions stay off while this runs, so the objects' filters
   * and the parallax do not start switching while the camera is still zooming.
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
      // An empty final keyframe means "whatever this element should look like in the
      // new phase"; the browser fills it in
      return () =>
        el.animate([from, {}], { duration: 700, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
    });
    this.set('settling');
    const animations = resume.map((play) => play());
    this.skipAnimations = animations;
    void Promise.all(animations.map((animation) => animation.finished)).then(
      () => {
        // After a replay, a destroy or any other phase change, a stale callback
        // must not drag the scene back into the hub.
        if (this.skipAnimations === animations && this._phase === 'settling') this.set('hub');
      },
      () => {
        /* A phase change cancels these animations on purpose, so a rejected
           finished promise is ordinary cleanup. */
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
    void this.els.stage.offsetWidth; // force reflow so the animations restart
    this.set('intro');
  }
}
