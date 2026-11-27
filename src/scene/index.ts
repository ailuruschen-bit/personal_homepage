import './geometry.gen.css';
import { relabel } from './dom';
import { ui } from '../content/ui';
import { lang, onLang, setLang, tr, type Lang } from '../i18n';

import { Monologue } from './monologue';
import './scene.css';
import { sectionById } from '../content/sections';
import { buildScene } from './dom';
import { FocusEngine } from './focus';
import { COVER } from './hotspots';
import { Opening } from './opening';
import { Story } from './story';

/** Each half of the language switch's cut through black, in ms */
const LANG_FADE = 220;

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
    (target) => {
      const sec = sectionById(target);
      return target === COVER ? tr(ui.outside) : sec ? tr(sec.title) : target;
    },
  );
  // The story: once seated, wheel and touch walk the camera to each object,
  // and reaching one cuts to its page (docs/10)
  history.scrollRestoration = 'manual';
  const story = new Story(els);
  focus.story = () => story.update(focus.hubCamera);
  // the carriage is not rendered while a page is read
  story.onMode = (mode) => (mode === 'page' ? focus.stop() : focus.start());
  // scrolling up at the hub looks back out of the window; scrolling down out there returns
  story.onOut = () => opening.set('peek');
  story.focused = () => focus.focused !== null;
  // for poking at the story from the console while developing
  if (import.meta.env.DEV) Object.assign(window, { __story: story });
  // Sync the framing the moment the phase changes, ahead of the style recalc in the same frame
  const monologue = new Monologue(els.mono);
  // Languages: every label now, and again in place on each change
  relabel(els, opening.touch);
  // The switch goes through black: Chrome faults when the labels over the
  // carriage change in sight (docs/09, F-009)
  let switching = false;
  const onLangClick = async (e: MouseEvent) => {
    const l = (e.target as HTMLElement).closest<HTMLElement>('[data-lang]')?.dataset.lang as
      Lang | undefined;
    if (!l || l === lang() || switching) return;
    switching = true;
    root.style.transition = `opacity ${LANG_FADE}ms ease`;
    root.style.opacity = '0';
    await new Promise((r) => setTimeout(r, LANG_FADE));
    setLang(l);
    // drawn twice behind black before it is shown
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    root.style.opacity = '1';
    await new Promise((r) => setTimeout(r, LANG_FADE));
    root.style.transition = '';
    root.style.opacity = '';
    switching = false;
  };
  els.langs.addEventListener('click', onLangClick);
  const offLang = onLang(() => {
    relabel(els, opening.touch);
    monologue.relabel();
    if (focus.focused && story.atHub) focus.relabel();
  });
  opening.onPhase = (p) => {
    story.enabled = p === 'hub';
    // the city is reached: the detective's monologue
    if (p === 'idle') monologue.play();
    focus.syncFrame();
  };
  if (startAt) {
    // A link straight to a chapter: no opening, its page on the first frame
    opening.set('hub');
    story.openNow(startAt);
  } else if (skipOpening) opening.skip();
  focus.syncFrame();
  if (!startAt) focus.start();
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
    // out through the window, and back in at the start of the story
    if (target === COVER) {
      story.reset();
      opening.set('peek');
    } else story.play(target);
  };

  const onPointerMove = (e: PointerEvent) => {
    pointerType = e.pointerType;
    if (e.pointerType === 'touch') return;
    opening.hintOnMove();
    if (opening.phase === 'hub' && !story.isPlaying) focus.movePointer(e.clientX, e.clientY);
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
    if (!story.atHub) return;

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

  // Out of the window, scrolling down comes back in; up does nothing, so the
  // tail of the scroll that took the visitor out does not bring them straight back
  const onWheel = (e: WheelEvent) => {
    if (e.deltaY > 0) opening.back();
  };

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
      document.removeEventListener('visibilitychange', onVisibilityChange);
      cancelAnimationFrame(grainResume);
      root.classList.remove('grain-suspended');
      focus.stop();
      story.dispose();
      monologue.dispose();
      offLang();
      els.langs.removeEventListener('click', onLangClick);
      window.removeEventListener('resize', onResize);
      opening.dispose();
      document.removeEventListener('keydown', onKeyDown);
      root.replaceChildren();
    },
  };
}
