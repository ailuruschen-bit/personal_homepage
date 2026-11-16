# 05 Rendering and compositing

This page is mostly about one thing: the scene stacks a lot of large, animated,
GPU-composited layers on top of each other, and browsers are not equally good
at keeping them in order. Most of the non-obvious CSS in `scene.css` exists
because of that.

**Several rules on this page exist only to keep Chrome's compositor stable.**
They are marked below. The bug that produced them is written up in
[09 Fix log](09-fix-log.md#f-001-chrome-the-city-drawn-over-the-carriage); read
that before removing one.

## Paint order

`.stage` contains these children, in this order, with explicit `z-index`:

| z-index | Element                               | What it is                                 |
| ------- | ------------------------------------- | ------------------------------------------ |
| 0       | `.sky`                                | static sky image                           |
| 1       | `.ow` > `.out` > `.ly` x3 + `.base`   | the city outside, three parallax layers    |
| 2       | `.rain2`                              | rain in front of the city                  |
| 3       | `.cam` > `.look` > `.sway` > `.scene` | the whole carriage                         |
| 4       | `.hero`                               | cover headline                             |
| 5       | `.ghost`                              | the dark bands that cue "click to go back" |
| 6       | `.lens`                               | vignette                                   |
| 7       | `.grain`                              | film grain                                 |
| 8       | `.hint`, `.cap`, `.ml`                | hint, focus caption, pointer light         |
| 9       | `.skip`, `.re`                        | buttons                                    |

The `z-index` values were added deliberately, not for tidiness. Chrome promotes
the city layers, the carriage and the grain to compositing layers of their own,
and with enough of them a stacking order inferred from DOM order alone can come
out wrong across a phase change — the city gets drawn over the carriage.
Pinning `z-index` removes the inference.

The carriage sits above the city and the window is a **hole**: `room.webp` has
transparent pixels where the glass is, and the city shows through from behind.
This is what makes the ordering load-bearing rather than cosmetic. If the
carriage layer fails to paint, you do not get a gap — you get the city.

## What is promoted, and when

| Element  | Promoted because                                              | When                                   |
| -------- | ------------------------------------------------------------- | -------------------------------------- |
| `.ly` x3 | `will-change: transform` plus an infinite transform animation | always                                 |
| `.ow`    | `will-change: transform`                                      | always                                 |
| `.look`  | `will-change: transform`                                      | hub only (`.ow, .hub .look`)           |
| `.cam`   | transform animation                                           | during `intro`, `back`, `peek`         |
| `.sway`  | infinite transform animation                                  | except in `idle` / `back` / `settling` |
| `.grain` | `will-change: transform` plus a stepped animation             | always                                 |
| `.pop`   | transform and filter changes                                  | left to the browser, deliberately      |

Three of those choices are worth explaining.

**`.look` is only promoted in the hub.** It wraps the entire carriage. While
the camera is zooming, a promoted `.look` has its raster scale driven up by the
ancestor's `scale()`, and Chrome does not reliably lower it again afterwards.
Restricting the promotion to the hub keeps it off during the zoom.

**The carriage's looping animations are switched off outside the hub.**

```css
.idle .cam *,
.back .cam *,
.settling .cam * {
  animation: none !important;
}
```

Rain, steam, the blinking cursor, the neon flicker — all invisible at that
point, and all of them would otherwise be promoted while the ancestor is being
zoomed.

**`.pop` has no permanent `will-change`.** This is the opposite of the usual
advice and was arrived at empirically: in Chrome, keeping the lifted object
copies promoted after the opening zoom made focus enter and leave flicker.

## Sizes

The city layers are the largest surfaces on the page:

```css
.ly {
  left: -25vw;
  width: calc(150vw + var(--tile));
  height: 640px;
}
.c1 {
  --tile: 1440px;
}
.c2 {
  --tile: 4320px;
}
.c3 {
  --tile: 1440px;
}
```

The width is not arbitrary. Each layer has to cover the window when scaled down
to `--os` (0.42 in landscape), cover the whole viewport at full size during
`idle`, and carry one extra `--tile` so the `loop` animation — which translates
by exactly one tile width — never exposes an edge. `150vw` is the smallest
width that satisfies all three with margin.

At a 1440px viewport `.c2` is therefore 6480 CSS pixels wide. Chrome tiles
layers and only rasterises what is near the viewport, so this is not as
expensive as it looks, but it is the reason the width was reduced from an
earlier `300vw`.

## The window is clipped and rounded

`.win` uses `overflow: hidden` with a `border-radius`, and contains animated
children (rain, glass reflection, the passing-light sweep). That combination —
a rounded clip around moving content, nested inside an element that is being
scaled by several times — is the most fragile construct in the scene, and is
implicated in the Chrome issue below.

## Deliberate omissions

**No `mix-blend-mode` on the grain.** A blend mode on a full-screen element
forces the browser to flatten everything below it into a single backdrop
texture before blending, every frame. Plain alpha over black and white dots
reads almost the same and costs nothing.

**`overflow: clip`, not `hidden`, on `.stage`.** A `hidden` container is still
scrollable programmatically: focusing an off-screen hotspot button, or any
`scrollIntoView`, would shift the entire scene by hundreds of pixels. `clip`
cannot scroll.

**No `transition` on `.pop` filters during a phase change.** Transitions on
filters create and destroy layers at exactly the moments when the layer set is
already churning.

## Rules that exist for Chrome

Chrome drew the city over the carriage and flickered after the opening, until
the fix recorded in
[09 Fix log](09-fix-log.md#f-001-chrome-the-city-drawn-over-the-carriage).
Four rules on this page were kept from that investigation. None of them fixed
the fault alone, all of them are correct regardless, and none has been retested
against Chrome since:

| Rule                                          | Section above                                         |
| --------------------------------------------- | ----------------------------------------------------- |
| Explicit `z-index` on every child of `.stage` | [Paint order](#paint-order)                           |
| No `mix-blend-mode` on the grain overlay      | [Deliberate omissions](#deliberate-omissions)         |
| City layers at `150vw` rather than `300vw`    | [Sizes](#sizes)                                       |
| Maximum zoom capped at 6.5x, down from 80x    | [03 Phases and the opening](03-phases-and-opening.md) |

`will-change` on a focusable object is applied only while that object is
animating, never for the whole session — see
[What is promoted, and when](#what-is-promoted-and-when).

> **Planned change.** The scroll narrative adds a camera dolly onto individual
> objects, which drives raster scale up the same way the opening does. The zoom
> ceiling it proposes (2.5-3x) exists for this reason. See
> [10 Scroll narrative](10-scroll-narrative.md#performance).
