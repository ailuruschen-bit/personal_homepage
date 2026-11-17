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

## F-003 Chrome: focus shading flicker and slow pointer light

**Fixed for the current scene; manual Chrome checks passed.** The exact browser
compositing failure was not established with a performance trace. This work was
done after F-002, during the side-wall tone matching on `art/redraw`.

### Symptoms

- Adding focus dimming to the side extensions made colour patches flash when
  switching objects. Even variants stable during focus could flash for one frame
  when an early opening skip settled into the hub or a background tab became
  visible again.
- A later no-flash variant moved the grain by repainting its background every
  80 ms. It kept the texture but made the pointer light and opening noticeably
  less fluid in Chrome than in Safari.

### Controlled checks, in order

1. Builds **G** (`public/_bisect/g/`) and **H** (`public/_bisect/h/`) gave the
   same side-wall tone with, respectively, two flat opacity strips and shadows
   extending from the central dimmer. Both stopped steady-state colour flashing,
   but still flashed at skip landing and on tab return.
2. Moving the flat strips into `.ext` pseudo-elements made flashing worse,
   including during ordinary focus changes; this was reverted.
3. Removing the side strips stopped focus-change flashes. Skip landing and tab
   return still flashed, so the side strips were not their only trigger.
4. Disabling the periodic `.pop` filter glint stopped the skip-landing flash.
5. Holding the film grain still stopped the tab-return flash, but visibly hurt
   its texture. Animating `background-position` restored motion without that
   flash, at the cost of conspicuous Chrome input and opening latency.
6. Filtering the existing side artwork with `brightness()` brought back focus
   flashes and slowed the pointer. Fading the central dimmer to transparent at
   its edges produced an objectionable dark halo. Both were reverted.
7. Removing central focus dimming as well as the side strips kept the object
   lift and warm `.beam` but eliminated the tone boundary. Removing `screen`
   blending from `.ml` and `.beam` improved pointer response somewhat.
8. The grain returned to transform animation. `visibilitychange` now removes
   that moving layer while the tab is hidden and restarts it after two visible
   animation frames. The user accepted the resulting Chrome fluidity and found
   no remaining flashes in the tested interactions.

### Current rules and limits

- Do not silently reintroduce `.spot`, `.dimside`, `.pop` glint, or live side-wall
  filters. The present focus treatment uses object lift, the pointer light and
  `.beam`, with no scene-wide darkening.
- Keep the grain's transform animation and the visibility lifecycle in sync.
  Replacing it with full-viewport `background-position` animation traded the
  flash for perceptible Chrome latency. Keep `screen` blending off the pointer
  light and beam unless it is measured and manually checked again.
- A darker focused state is still an open design option, not an impossible
  effect. Pre-rendered artwork is a candidate, but has not been tested. Check
  focus changes, early skip landing, tab return, pointer latency, and opening
  smoothness in a visible desktop Chrome window before adopting it.

---

## F-002 Chrome: flicker after shading the side panels

**The vignette fix remains; the focus-dimming part was superseded by F-003.**
Chrome only. The exact original trigger was not isolated.

### Symptoms

Patches of the picture's top colour flickered at the start of the opening, at
the end of the return to the carriage, and when focus moved between objects.
Unlike F-001 it was not the city showing through.

### Cause

Introduced while removing a step in tone between the room and its side
extensions. Two attempts both flickered:

1. Widening `.vig`, `.spot` and `.beam` to cover the extensions — three layers
   half as large again as the scene, one of them blended.
2. Putting them back and painting the same gradients inside the extensions
   with `::before` and `::after`, centred far outside their own boxes.

Both also rewrote `.vig`'s gradient with an explicit ellipse size, and that
size was wrong. Snapshots of four commits served side by side settled which
range was at fault; which of these changes was the trigger was not pursued.

### Fix

Page code for the overlays is back to what it was. The step in tone is removed
without touching them:

- the vignette over the side extensions is **baked into the artwork** by
  `room.py`, using `.vig`'s gradient exactly;
- focus dimming over the extensions was initially implemented as separate
  `.spot.side` elements. F-003 records why all focus dimming was later removed.

### Load-bearing afterwards

- No overlay inside `.scene` larger than the scene. The current focus treatment
  has no `.spot` or side dimming elements.
- No gradients painted in pseudo-elements of `.ext`.
- `.vig` keeps `ellipse at 50% 42%` with no explicit size.

### How it was found

Guessing failed twice. What worked was building the site at several commits and
serving the builds side by side under `public/_bisect/` for the browser that
showed the fault. Do that first next time.

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
