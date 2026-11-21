import './geometry.gen.css';
import './scene.css';
import { sectionById } from '../content/sections';
import { buildScene } from './dom';
import { FocusEngine } from './focus';
import { COVER } from './hotspots';
import { Opening } from './opening';
import { ScrollStory } from './scroll';

export interface SceneHandle {
  destroy(): void;
}

export interface SceneOptions {
  /** Skip the opening and land straight in the carriage */
  skipOpening?: boolean;
  /** Land with this chapter already open, skipping the opening (a #/id link) */
  startAt?: string;
}

/** Mount the carriage scene: opening -> idle -> hub */
export function mountScene(root: HTMLElement, { skipOpening, startAt }: SceneOptions): SceneHandle {
  const els = buildScene(root);
  // ?debug=geometry overlays the generated geometry, ?debug=layers adds switches
  // that remove one layer at a time; both are loaded only when asked for
  const debug = new URLSearchParams(location.search).get('debug');
  if (debug === 'geometry') void import('./debug').then((m) => m.drawGeometry(root));
  if (debug === 'layers') void import('./debug').then((m) => m.layerSwitches(root));
  const opening = new Opening(els);
  const focus = new FocusEngine(
    els,
    () => opening.phase,
    (target) => (target === COVER ? '窗外' : (sectionById(target)?.title ?? target)),
  );
  // The scroll story: once seated, the scroll offset drives the chapters (docs/10)
  history.scrollRestoration = 'manual';
  const story = new ScrollStory(els, els.track);
  focus.story = () => story.update(focus.hubCamera);
  // Sync the framing the moment the phase changes, ahead of the style recalc in the same frame
  opening.onPhase = (p) => {
    story.setEnabled(p === 'hub');
    focus.syncFrame();
  };
  if (startAt) {
    // A link straight to a chapter: no opening, no flash of the carriage, the
    // chapter open on the first frame
    opening.set('hub');
    story.layout();
    window.scrollTo(0, story.readStart(startAt));
  } else if (skipOpening) opening.skip();
  focus.syncFrame();
  focus.start();
  const onResize = () => story.layout();
  window.addEventListener('resize', onResize);

  // Drop the grain's moving compositor layer before Chrome hides the tab, then
  // let the visible carriage paint twice before starting that layer again.
  let grainResume = 0;
  const onVisibilityChange = () => {
    cancelAnimationFrame(grainResume);
    if (document.hidden) {
      root.classList.add('grain-suspended');
    } else {
      grainResume = requestAnimationFrame(() => {
        grainResume = requestAnimationFrame(() => root.classList.remove('grain-suspended'));
      });
    }
  };
  document.addEventListener('visibilitychange', onVisibilityChange);
  onVisibilityChange();

  let pointerType = 'mouse';

  const enter = (target: string | null) => {
    if (!target) return;
    if (target === COVER) opening.set('peek');
    else story.transportTo(story.readStart(target));
  };

  const onPointerMove = (e: PointerEvent) => {
    pointerType = e.pointerType;
    if (e.pointerType === 'touch') return;
    opening.hintOnMove();
    if (opening.phase === 'hub') focus.movePointer(e.clientX, e.clientY);
    else focus.trackPointer(e.clientX, e.clientY);
  };

  const onPointerLeave = () => focus.clearPointer();

  const onPointerDown = (e: PointerEvent) => {
    pointerType = e.pointerType;
  };

  const onClick = (e: MouseEvent) => {
    const el = e.target as HTMLElement;
    if (el.id === 'skip') return opening.skip();
    if (el.id === 're') return opening.replay();
    if (opening.phase !== 'hub') return opening.back();

    if (pointerType === 'touch') {
      // Touch: the first tap focuses, the second one enters
      const target = focus.targetAt(e.clientX, e.clientY);
      if (target && target === focus.focused) enter(target);
      else focus.setFocus(target);
      return;
    }
    // Keyboard activation of a hotspot button reports detail 0; trust the button itself there
    enter(e.detail === 0 ? (el.dataset.go ?? null) : focus.focused);
  };

  const onFocusIn = (e: FocusEvent) => {
    const el = e.target as HTMLElement;
    const target = el.dataset.go;
    if (target && opening.phase === 'hub' && el.matches(':focus-visible')) focus.setFocus(target);
  };

  const onWheel = () => opening.back();

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && opening.phase === 'hub' && story.offset > 0) story.transportTo(0);
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') opening.back();
  };

  els.stage.addEventListener('pointermove', onPointerMove);
  els.stage.addEventListener('pointerleave', onPointerLeave);
  els.stage.addEventListener('pointerdown', onPointerDown);
  els.stage.addEventListener('click', onClick);
  els.stage.addEventListener('focusin', onFocusIn);
  els.stage.addEventListener('wheel', onWheel, { passive: true });
  document.addEventListener('keydown', onKeyDown);

  return {
    destroy() {
      document.removeEventListener('visibilitychange', onVisibilityChange);
      cancelAnimationFrame(grainResume);
      root.classList.remove('grain-suspended');
      focus.stop();
      story.dispose();
      window.removeEventListener('resize', onResize);
      opening.dispose();
      document.removeEventListener('keydown', onKeyDown);
      root.replaceChildren();
    },
  };
}
