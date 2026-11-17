# 04 Focus system

> **Planned change.** Pointer focus narrows to the hub, the snap becomes a continuous scroll-driven value inside a chapter, and the camera gains a horizontal axis (`--fx`). See [10 Scroll narrative](10-scroll-narrative.md).

`src/scene/focus.ts` is the largest module in the project and the one with the
most judgement baked into it. It runs one `requestAnimationFrame` loop and is
responsible for four things: the framing, the parallax, which object has focus,
and where the light is.

## The design it is imitating

Two references, both deliberate:

- **The iPadOS pointer.** The cursor is not a fixed arrow; it deforms and is
  attracted to what it is near. Here the light is pulled toward an object as
  the pointer approaches, and snaps onto it on arrival.
- **tvOS focus.** The focused element is lifted and brightened rather than
  everything else being dimmed. Here the object is lifted, brightened and given
  a shadow, and a pool of light lands on it.

What it deliberately does _not_ do is push the camera in toward the pointer.
The framing is fixed; only the light and the objects react.

## The frame loop

```ts
tick(now) {
  dt = min(0.05, elapsed);          // clamp, so a stalled tab does not jump
  active = phase() === 'hub';
  syncFrame();                      // framing, early-outs unless it changed
  updateParallax(dt);
  pull += (pullTarget - pull) * smoothing(dt, TAU.pull);
  if (active && pointer) placeLight();
  ml.style.opacity = active && pointer ? '1' : '0';
  updatePool(dt, active);
}
```

Every easing in the module is the same exponential smoothing:

```ts
smoothing = (dt, tau) => 1 - Math.exp(-dt / tau);
value += (target - value) * smoothing(dt, tau);
```

This is frame-rate independent — the same `tau` produces the same real-time
response at 60 or 120 Hz — which a naive `value += (target - value) * 0.1`
would not be. The time constants live in `TAU`; smaller is snappier.

## Snapping

Each hotspot has a rectangular `zone` in scene units. `zoneDistance` returns 0
inside it and the Euclidean distance to its edge outside.

The rule, in `resolveFocus`, is not simply "nearest wins". It is
direction-aware:

1. **Keep what you have.** If an object currently has focus and the pointer is
   not actively moving away from it, it keeps focus. Moving away means
   `zoneDistance > 0` _and_ the recorded direction is "receding".
2. **Only snap while approaching.** A candidate is eligible if the pointer is
   inside its zone, or within `SNAP_RANGE` (22 units) _and_ approaching it.
3. Among eligible candidates, the nearest wins.

Direction is tracked per object in `trackDirections`, against a remembered
reference distance, with a `DIRECTION_EPSILON` of 1.2 units of hysteresis so
hand tremor does not register as movement.

The effect is that focus feels sticky: it does not flicker between two objects
when the pointer sits between them, and it does not grab an object you are
clearly moving past.

## Pulling the light

While nothing is focused, the light does not follow the pointer exactly. In
`placeLight`, if the nearest object is within `PULL_RANGE` (78 units) and the
pointer is approaching it:

```ts
t = 1 - (distance - SNAP_RANGE) / (PULL_RANGE - SNAP_RANGE);
pullTarget = PULL_MAX * t * t; // PULL_MAX = 0.42
```

`t` ramps from 0 at the edge of the pull range to 1 at the snap boundary, and
is squared so the pull stays nearly absent until you are close. The light is
then interpolated that fraction of the way toward the object's light anchor.
`pull` itself is smoothed, so entering and leaving the pull range is not a
step change.

## The spotlight pool

`.beam` is a warm, full-scene light overlay positioned by four custom
properties. The earlier dark `.spot` and side dimming were removed after Chrome
flicker and latency checks; see [F-003](09-fix-log.md#f-003-chrome-focus-shading-flicker-and-slow-pointer-light).

`updatePool` eases five numbers toward a target: centre `x`/`y`, radii
`rx`/`ry`, and `alpha`. The target comes from the focused hotspot's `light` entry.

Two details are worth keeping:

- **The pool leans toward the pointer.** Even when snapped, the centre is
  offset by up to 22% of the radius in the pointer's direction, so the light
  still feels attached to the hand rather than locked to the object.
- **It grows out of the pointer.** While nothing is focused, the pool is parked
  under the pointer light at `FREE_RADIUS`, so the snap animation expands from
  where the cursor was rather than appearing from nowhere.

The loop skips writing the custom properties once the beam's opacity is below
0.004, which is the common case while browsing without focus.

Note the `/ 4.8` in those writes: it converts scene units to a percentage of
the 480-unit square.

## Parallax

A few pixels, 2% of the pointer's offset from centre, moving the carriage one
way and the city outside half as far.

The carriage parallax is only eased frame by frame **in the hub**:

```ts
if (phase === 'hub') {
  /* ease toward target */
} else if (phase === 'back' ? phase !== lastPhase : phase !== 'peek') {
  c.px = tx;
  c.py = ty; // jump, while invisible
}
```

Outside the hub it jumps straight to its target rather than easing — on the
first frame of the return, so the carriage is already aimed at the pointer when
it arrives; held still during `peek`; zeroed otherwise. Easing `.look` while the
camera is still zooming would repaint the whole carriage every frame. The
inline transform is also compared against its previous value and only written
when it changes.

The city outside is always visible, so its offset is always eased.

## Input

Handled in `scene/index.ts`, not in the engine:

| Event                            | Behaviour                                                                                                  |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `pointermove` (mouse)            | hub: full focus resolution. Other phases: record the position only, so the parallax is in place on arrival |
| `pointermove` (touch)            | ignored — touch has no hover                                                                               |
| `click` outside the hub          | go back to the carriage                                                                                    |
| `click` in the hub, mouse        | enter whatever currently has focus                                                                         |
| `click` in the hub, touch        | first tap focuses, second tap on the same object enters                                                    |
| `focusin` on a hotspot button    | focus it, but only for `:focus-visible`, so keyboard navigation lights the scene and mouse clicks do not   |
| `keydown` Enter / Space / Escape | go back to the carriage                                                                                    |
| `wheel`                          | go back to the carriage                                                                                    |

Keyboard activation of a hotspot button reports `detail === 0`, which is how
`onClick` distinguishes it from a real click and trusts the button's own
`data-go` rather than the pointer-derived focus.

The hotspot buttons are real `<button>` elements with `aria-label`, so the scene
is tabbable. `pointer-events` is only enabled on them in the hub.

## Tuning reference

| Constant            | Value | Effect of raising it                                 |
| ------------------- | ----- | ---------------------------------------------------- |
| `SNAP_RANGE`        | 22    | Objects grab the pointer from further away           |
| `PULL_RANGE`        | 78    | The light starts bending toward objects sooner       |
| `PULL_MAX`          | 0.42  | A stronger bend at the snap boundary                 |
| `DIRECTION_EPSILON` | 1.2   | More tolerant of tremor, slower to notice a reversal |
| `FREE_RADIUS`       | 30    | A larger pool before snapping                        |
| `TAU.camera`        | 0.34  | Slower framing and outside-layer easing              |
| `TAU.parallax`      | 0.09  | Laggier parallax                                     |
| `TAU.poolMove`      | 0.045 | The pool chases the object more slowly               |
