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

## F-009 Chrome: the language switch faults over the carriage

**Symptom.** Switching language at the hub drew garbled rectangles over the
carriage for a moment in Chrome. Safari was fine.

**Cause.** The same family as F-006 and F-007: the switch rewrites the text
over the carriage (the route, the caption, the buttons) in sight, all at once.

**Fix.** Not fixed at the source. The switch goes through black instead, like
every other cut: `#app` fades out (220 ms), the language changes, two frames
are drawn, and it fades back (`index.ts`, `LANG_FADE`).

## F-008 Chrome: a chapter page does not scroll at all

**Symptom.** On a chapter page in Chrome the wheel showed the scrollbar but
the page never moved. Safari was fine.

**Cause.** `overscroll-behavior-y: none` was set on `body` as well as `html`
while reading. With both set to `overflow-y: auto`, `body` is a scroll
container of its own, with nothing to scroll. Chrome sends the wheel to it
first, and `overscroll-behavior` there stops it being handed on to the
viewport, which is what actually scrolls.

**Fix.** `overscroll-behavior-y: none` on the root only (`base.css`). That
still removes the rubber band past a page's ends.

## F-007 Chrome: any panel painted over the carriage faults

**Symptom.** A speech bubble for the detective's lines (a dark panel with a
rim and a shadow, over the lower middle of the carriage) brought back the
rectangular faults on the first focus of each object and when its text first
appeared. Safari was clean.

**Cause.** Being over the carriage at all. `?talk=off` was clean; `?talk=static`,
the bubble always shown with no transition, still faulted, and so did giving it
its own layer from the first frame (`will-change`). Showing it by opacity
written per frame, then by a class and a transition, made no difference.

**Fix.** The bubble was dropped. The lines go into the focus caption, plain
text that has always been clean, which only changes its text and its class.

**Load-bearing.** Over the carriage: the caption's text and nothing painted
behind it. No panels, boxes, backgrounds or shadows, however they are shown.

## F-006 Chrome: panels over the carriage fault on first focus

**Symptom.** With the scroll skeleton, Chrome drew rectangular faults on the
first return to the carriage and on the first focus of each object. Safari was
clean.

**Cause.** The chapters' content panels sat over the carriage, transparent,
inside a box covering the stage. `?no=panel`, which left them out, cleared the
faults; hiding them with `visibility` did not.

**Fix.** The design changed rather than the CSS: content is never over the
carriage. Reaching an object cuts through black to a separate page, and the
carriage is hidden while it is read (docs/10, Skeleton).

**Load-bearing.** Nothing is layered over the carriage but the object being
lifted. Text goes on its own page.

## F-005 Chrome: nearest-neighbour scaling of the carriage stutters

**Symptom.** With `image-rendering: pixelated` on the carriage's images
(`.room`, the side images, the sprites and their fronts), tried for sharpness
in docs/13 step 4.1, the page stuttered clearly in Chrome, and the picture was
not much sharper.

**Cause.** Not traced. Those images scale with the camera, and Chrome appears to
take a slower path for nearest-neighbour scaling of large images under a
transform.

**Fix.** Reverted; the images scale smoothly again.

**Load-bearing.** Do not set `image-rendering` on anything that scales with the
camera. Sharpness has to come from the art.

## F-004 Chrome: the return from outside stutters with more paint on the glass

**Symptom.** After stage 3.6 added two faint edge gradients to `.glass` (a
reflection of the neon and the lamp at the glass's edges), the camera's flight
back from outside into the carriage stuttered badly in Chrome.

**Cause.** Not traced to the frame, but the gradients were the only runtime
change in that step; the art passes in it are baked into the image and the
assets did not grow. `.glass` fills the window and scales with `.cam` through
the whole return, and each extra layer is repainted at every scale.

**Fix.** `.glass` went back to its single streak gradient, and the stutter went
away. The reflection made little visible difference and was dropped.

**Load-bearing.** Keep `.win` and everything in it as light to paint as it is:
no added gradients, shadows or filters on elements that scale with the camera's
flight. Effects for the glass belong in the art or nowhere.

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

### Follow-up: the central dimming is back

The central `.spot` was restored after the side images were redrawn as a dark
foreground (docs/13, D-01a), so the dimming stops where the room ends rather
than in the middle of a side wall. Only `.spot` came back, exactly as before
F-003 with its gradient reaching full strength at 320% of the light's radius.
`.dimside`, the `.pop` glint and `screen` blending on `.ml` and `.beam` stay
out. The user had verified the central dimming on its own in Chrome before
this; the combination with the new foreground still wants the usual check.

### Current rules and limits

- Do not reintroduce `.dimside`, `.pop` glint, or live side-wall filters, and
  do not widen `.spot` beyond the scene. The present focus treatment uses object lift, the pointer light and
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
