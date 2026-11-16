import './geometry.gen.css';
import './scene.css';
import { sectionById } from '../content/sections';
import { buildScene } from './dom';
import { FocusEngine } from './focus';
import { COVER } from './hotspots';
import { Opening } from './opening';

export interface SceneHandle {
  destroy(): void;
}

export interface SceneOptions {
  /** Open the matching section once an object is chosen */
  onEnter: (sectionId: string) => void;
  /** Skip the opening and land straight in the carriage (used when returning from a section) */
  skipOpening?: boolean;
}

/** Mount the carriage scene: opening -> idle -> hub */
export function mountScene(root: HTMLElement, { onEnter, skipOpening }: SceneOptions): SceneHandle {
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
  // Sync the framing the moment the phase changes, ahead of the style recalc in the same frame
  opening.onPhase = () => focus.syncFrame();
  if (skipOpening) opening.skip();
  focus.syncFrame();
  focus.start();

  let pointerType = 'mouse';

  const enter = (target: string | null) => {
    if (!target) return;
    if (target === COVER) opening.set('peek');
    else onEnter(target);
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
      focus.stop();
      opening.dispose();
      document.removeEventListener('keydown', onKeyDown);
      root.replaceChildren();
    },
  };
}
