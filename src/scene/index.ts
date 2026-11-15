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
  /** 选中某个物件后进入对应板块 */
  onEnter: (sectionId: string) => void;
  /** 跳过开幕，直接落在车厢（从板块页返回时使用） */
  skipOpening?: boolean;
}

/** 挂载车厢场景：开幕 → 待机 → 主菜单 */
export function mountScene(root: HTMLElement, { onEnter, skipOpening }: SceneOptions): SceneHandle {
  const els = buildScene(root);
  const opening = new Opening(els);
  const focus = new FocusEngine(
    els,
    () => opening.phase,
    (target) => (target === COVER ? '窗外' : (sectionById(target)?.title ?? target)),
  );
  // 阶段一变就同步构图，赶在同一帧的样式计算之前
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
      // 触摸：第一下聚焦，第二下进入
      const target = focus.targetAt(e.clientX, e.clientY);
      if (target && target === focus.focused) enter(target);
      else focus.setFocus(target);
      return;
    }
    // 键盘激活热区按钮时 detail 为 0，此时以按钮自身为准
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
