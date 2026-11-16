# 02 Scene coordinates

## Why there is a grid at all

The carriage is one drawing. Everything placed in it — a coffee cup, the region
the pointer snaps from, the pool of light that lands on an object — has to be
positioned relative to that drawing, not relative to the viewport. Otherwise
every object would need its own responsive rules.

So the scene defines its own coordinate space and the conversion to screen
space happens in exactly one module, `src/scene/units.ts`.

## The grid

The carriage occupies a square, 480 units on a side. `SCENE = 480`. Positions
are written as plain numbers in that space: the laptop screen's top-left corner
is at `(148, 292)`, the window spans roughly `x` 150 to 330.

On screen that square is `100vmax` wide and tall, centred on the viewport. One
scene unit is therefore:

```ts
unitSize() = max(innerWidth, innerHeight) / 480;
```

`vmax` rather than `vmin` means the square always covers the viewport's longer
axis, so the carriage fills the screen in both orientations and is cropped on
the shorter axis rather than letterboxed.

In CSS the same relationship is expressed as `--u: calc(100vmax/480)` on
`.stage`, and static elements are positioned with percentages of the square —
`left: 31.25%` is scene x 150. `pct()` in `units.ts` produces those percentage
strings for the elements that are generated from `hotspots.ts`.

Note that the artwork's own pixel grid is a separate thing. `room.webp` is
960x960, which is two image pixels per scene unit; the city layers are not tied
to the scene grid at all and are sized in CSS pixels. See
[06](06-art-pipeline.md).

## The camera

The camera is four numbers, defined by the `Camera` interface:

| Field      | Meaning                                                                |
| ---------- | ---------------------------------------------------------------------- |
| `z`        | zoom — the hub framing pulls back slightly, so this is usually below 1 |
| `by`       | vertical offset that sets the framing                                  |
| `px`, `py` | a few pixels of parallax that follow the pointer                       |

`toScene(px, py, camera)` and `toScreen(X, Y, camera)` convert between a point
on the screen and a point on the grid, taking all four into account. They are
inverses of each other and are the only place the mapping is written down.

`toScene` is what makes pointer input work: the pointer arrives in client
coordinates, gets converted once, and every snapping decision after that is
made in scene units, where the hotspot data lives.

## How the framing reaches the screen

The camera is not applied as one transform by JavaScript. It is split in two,
and the split matters:

**The framing** (`z` and `by`) is written to `--fz` and `--fy` on `.stage` by
`FocusEngine.syncFrame`, and consumed by CSS:

```css
.cam {
  transform-origin: 50% 43.71%;
  transform: translateY(var(--fy, 0px)) scale(var(--fz, 1));
}
```

**The parallax** (`px`, `py`) is written as an inline transform on `.look`, a
child of `.cam`, each frame.

The reason for the split is the opening animation. `@keyframes push` multiplies
the framing rather than replacing it — every keyframe reads
`scale(calc(var(--fz, 1) * N))`. That way the return animation's final frame is
exactly the hub framing, with no second movement after it lands, and a skipped
opening can tween to the same place. If JavaScript owned the whole transform it
would have to fight the animation for the same property.

`syncFrame` also short-circuits: it builds a key from the rounded zoom and
offset and returns early if nothing changed, so the custom properties are only
written on an actual resize or phase change, not sixty times a second.

### The zoom origin

`.cam`'s `transform-origin` is `50% 43.71%`, not the centre. That point sits in
the gap between two blind slats — it is the hole the camera flies through
during the opening.

Because the origin is off centre, a change in zoom also shifts the image
vertically. `syncFrame` compensates:

```ts
const shift = baseY + (240 - CAM_ORIGIN_Y) * u * (1 - zoom);
```

`CAM_ORIGIN_Y = 480 * 0.4371` is the same origin expressed in scene units.
**These two values must match.** If you move the origin in CSS, update
`CAM_ORIGIN_Y`, or the hub framing will be vertically off by a few percent of
the viewport.

## The hub framing

```ts
const zoom = clamp(Math.min(vw / (u * 300), vh / (u * 335)), 0.72, 1);
const baseY = (240 - 216) * u * zoom;
```

In words: pull back far enough that 300 scene units of width and 335 of height
are visible, never zoom in past 1, never pull back past 0.72, and raise the
centre of interest from scene y 240 to 216 — roughly from the middle of the
drawing to the window and the table.

During `intro` the framing is bypassed entirely (`--fz` 1, `--fy` 0) so the
opening starts on the close-up the artwork was composed for.

## Coordinate cheat sheet

| Space                     | Range / unit                   | Used by                                  |
| ------------------------- | ------------------------------ | ---------------------------------------- |
| Scene units               | 0..480 on each axis            | `hotspots.ts`, `units.ts`, art scripts   |
| Percentages of the square | 0..100%                        | static positions in `scene.css`, `pct()` |
| `--u`                     | one scene unit as a CSS length | sizes in `scene.css` that must scale     |
| Client pixels             | viewport                       | pointer events, `toScene` / `toScreen`   |
| Art pixels                | the 1x grid in `tools/art/`    | the generator scripts only               |

## Keep in sync

- `SCENE` in `units.ts`, `--u` in `scene.css`, and the 480 grid the art scripts
  draw on.
- `CAM_ORIGIN_Y` in `focus.ts` and `transform-origin` on `.cam` in `scene.css`.
