/**
 * 场景坐标系。
 *
 * 车厢是一张 480×480 的画，场景里所有位置都用这个尺度描述（下称「场景单位」）。
 * 屏幕上它被缩放成 100vmax 的正方形，再由相机做平移与缩放。
 */

export const SCENE = 480;

/** 1 场景单位等于多少 CSS 像素（未计相机缩放） */
export const unitSize = () => Math.max(window.innerWidth, window.innerHeight) / SCENE;

/** 场景单位 -> 百分比字符串，用于写入 style */
export const pct = (v: number) => `${((v / SCENE) * 100).toFixed(3)}%`;

export interface Camera {
  /** 缩放 */
  z: number;
  /** 垂直基准位移（构图用） */
  by: number;
  /** 跟随指针的轻微视差 */
  px: number;
  py: number;
}

export interface ScenePoint {
  X: number;
  Y: number;
}

/** 屏幕坐标 -> 场景坐标 */
export function toScene(px: number, py: number, c: Camera): ScenePoint {
  const u = unitSize();
  return {
    X: 240 + (px - window.innerWidth / 2 - c.px) / (u * c.z),
    Y: 240 + (py - window.innerHeight / 2 - c.by - c.py) / (u * c.z),
  };
}

/** 场景坐标 -> 屏幕坐标 */
export function toScreen(X: number, Y: number, c: Camera): { x: number; y: number } {
  const u = unitSize();
  return {
    x: window.innerWidth / 2 + c.px + (X - 240) * u * c.z,
    y: window.innerHeight / 2 + c.by + c.py + (Y - 240) * u * c.z,
  };
}
