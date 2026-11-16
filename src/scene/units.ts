/**
 * Scene coordinate system.
 *
 * The carriage is a 480x480 drawing, and every position in the scene is
 * expressed on that grid (referred to below as "scene units"). On screen it is
 * scaled to a 100vmax square, which the camera then pans and zooms.
 */

export const SCENE = 480;

/** How many CSS pixels one scene unit spans, before the camera zoom */
export const unitSize = () => Math.max(window.innerWidth, window.innerHeight) / SCENE;

/** Scene unit -> percentage string, for writing into inline styles */
export const pct = (v: number) => `${((v / SCENE) * 100).toFixed(3)}%`;

export interface Camera {
  /** Zoom */
  z: number;
  /** Vertical offset that sets the framing */
  by: number;
  /** Slight parallax that follows the pointer */
  px: number;
  py: number;
}

export interface ScenePoint {
  X: number;
  Y: number;
}

/** Screen coordinates -> scene coordinates */
export function toScene(px: number, py: number, c: Camera): ScenePoint {
  const u = unitSize();
  return {
    X: 240 + (px - window.innerWidth / 2 - c.px) / (u * c.z),
    Y: 240 + (py - window.innerHeight / 2 - c.by - c.py) / (u * c.z),
  };
}

/** Scene coordinates -> screen coordinates */
export function toScreen(X: number, Y: number, c: Camera): { x: number; y: number } {
  const u = unitSize();
  return {
    x: window.innerWidth / 2 + c.px + (X - 240) * u * c.z,
    y: window.innerHeight / 2 + c.by + c.py + (Y - 240) * u * c.z,
  };
}
