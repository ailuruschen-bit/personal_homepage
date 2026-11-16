# 05 Rendering and compositing

This page is mostly about one thing: the scene stacks a lot of large, animated,
GPU-composited layers on top of each other, and browsers are not equally good
at keeping them in order. Most of the non-obvious CSS in `scene.css` exists
because of that.

**There is an open bug here.** See [Known issue](#known-issue-chrome) at the
bottom before changing anything on this page.

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

## Known issue: Chrome

**Status: open. Reproduces in Chrome only; Safari and the Chromium-based
in-app browser are unaffected.**

Symptoms, as observed:

- After the camera returns from the city to the carriage, the city outside is
  drawn over the carriage and flickers.
- Worst when the opening is skipped while the camera is mid-flight.
- Milder after a full opening followed by a click to return.
- Moving the pointer, or changing which object has focus, makes it worse — one
  or two frames of tearing each time.
- An earlier variant of the same failure showed the window's interior (blinds,
  glass, rain) simply not drawn.

What has been tried, and did not resolve it:

1. Forcing a re-raster by toggling `will-change` on the wrapper layers.
2. Rebuilding the carriage's compositing layers (`display: none` and back) on
   landing. This fixed the rendering but introduced a visible twitch; moving it
   to the idle phase removed the twitch and brought the rendering fault back.
3. Lowering the maximum zoom from 80x to 6.5x.
4. Pinning `z-index` on every child of `.stage` (kept — correct regardless).
5. Removing `mix-blend-mode` from the grain (kept).
6. Keeping the composited layer set constant across focus changes (reverted;
   permanent `will-change` on `.pop` made it worse).
7. Shrinking the city layers from `300vw` to `150vw` (kept).

Current working hypothesis: the carriage's layer has its raster scale driven up
by the opening zoom and is not correctly re-rasterised afterwards, so its tiles
are missing and the city behind it shows through. This is consistent with the
in-app browser being unaffected — its viewport is roughly a third of the area,
so the same zoom produces a much smaller surface.

The obstacle to confirming it has been reproduction: a Chrome window that is
fully occluded by another window is marked hidden by macOS, at which point
Chrome freezes `requestAnimationFrame` and the animation timeline entirely.
Forced screenshots either return a stale frame or jump the timeline to the
present, so a transient compositing artefact cannot be captured that way. The
window has to be genuinely visible — side by side with whatever else is on
screen — for any live diagnosis.

If you pick this up, the things worth trying next:

- Record a trace in Chrome DevTools' Performance panel with "Layers" enabled
  across the return animation, and look at the raster scale of `.look` and
  `.sway` before and after.
- Try eliminating the hole entirely: give `.win` an opaque backdrop and move a
  second copy of the city inside it, so the carriage never depends on painting
  above a sibling. This is a larger change and would need the inner copy to be
  counter-scaled against the camera.
- Try lowering the zoom factor further than 6.5 and fading the carriage out
  earlier, which reduces the peak raster scale at the cost of a less dramatic
  fly-through.
