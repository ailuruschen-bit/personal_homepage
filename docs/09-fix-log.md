# 09 Fix log

A record of bugs that were hard to find, and of what finally fixed them. The
purpose is not changelog completeness — git history already has that. An entry
earns its place here when the fix left rules in the codebase that look arbitrary
without the story behind them, or when the same fault is likely to come back.

Entries are newest first. Each one states the symptom, the cause, the fix, and
anything that is now load-bearing because of it.

## Keep this file honest

- Add an entry when a fix leaves behind code or CSS whose reason is not obvious
  from reading it.
- Do not add an entry for ordinary feature work or for a bug whose fix is
  self-explanatory.
- When an entry's "load-bearing" rules are later removed or retested, say so in
  the entry rather than deleting it.

---

## F-001 Chrome: the city drawn over the carriage

**Fixed.** Reproduced in Chrome only; Safari and the Chromium-based in-app
browser were never affected.

### Symptoms

- After the camera returned from the city to the carriage, the city outside was
  drawn over the carriage and flickered.
- Worst when the opening was skipped while the camera was mid-flight.
- Milder after a full opening followed by a click to return.
- Moving the pointer, or changing which object had focus, made it worse — one or
  two frames of tearing each time.
- An earlier variant of the same failure showed the window's interior (blinds,
  glass, rain) simply not drawn.

### Cause

Chrome was left holding a compositing layer set it could not keep consistent
across the opening zoom. Two things fed it:

1. `.pop` carried `will-change` for the whole session, on the theory that focus
   changes should not create and destroy layers. In Chrome this instead kept a
   large layer set alive through the zoom and made the fault worse.
2. Skipping the opening mid-flight changed phase twice inside one frame, so the
   camera, the city and the rain snapped to their resting transforms while
   Chrome was still rasterising the zoomed-in surface.

The hypothesis that fits the rest of the symptoms: the carriage's layer had its
raster scale driven up by the zoom and was not re-rasterised afterwards, so its
tiles were missing and the city behind it showed through. That matches the
in-app browser being unaffected — its viewport is roughly a third of the area,
so the same zoom produced a much smaller surface.

### Fix

In `src/scene/opening.ts` and `src/scene/scene.css`:

1. **`will-change` only while animating.** The hint is applied to a focusable
   object for the duration of its animation and removed afterwards.
2. **A `settling` phase between a skipped opening and `hub`.** `settling` tweens
   the camera, the city and the rain from their current computed values
   (`el.animate([from, {}], ...)`) and hands control to `hub` only when that
   tween ends. Focus interaction stays disabled until then, and stale animations
   are cancelled on every phase change, on replay and on disposal.

The forced reflow in `OpeningSequence.set()` (`void stage.offsetWidth`) belongs
to the same fix: without it two phase changes in one frame reuse the finished
`push` animation and the scene sticks in `back`. See
[03 Phases and the opening](03-phases-and-opening.md).

### Load-bearing afterwards

Each of these was tried while diagnosing the fault. None fixed it alone, and all
were kept because they are correct regardless. Removing one has not been
retested against Chrome:

- Explicit `z-index` on every child of `.stage`.
- No `mix-blend-mode` on the grain overlay.
- City layers at `150vw` rather than `300vw`.
- Maximum zoom in `@keyframes push` capped at 6.5x, down from 80x.

See [05 Rendering and compositing](05-rendering-and-compositing.md) for what
each of those rules does.

### Dead ends

- Forcing a re-raster by toggling `will-change` on the wrapper layers.
- Rebuilding the carriage's compositing layers (`display: none` and back) on
  landing. This fixed the rendering but introduced a visible twitch; moving it
  into the idle phase removed the twitch and brought the rendering fault back.

### If something like it returns

Record a trace in Chrome DevTools' Performance panel with "Layers" enabled
across the return animation and compare the raster scale of `.look` and `.sway`
before and after.

One practical note on reproducing anything of this kind: a Chrome window fully
occluded by another window is marked hidden by macOS, and Chrome then freezes
`requestAnimationFrame` and the animation timeline. Forced screenshots return
either a stale frame or a jump to the present, so a transient compositing
artefact cannot be captured that way. The window has to be genuinely visible —
side by side with whatever else is on screen — for any live diagnosis.
