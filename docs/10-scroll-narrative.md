# 10 Scroll narrative

**Status: skeleton built** (`scene/scroll.ts`; see [Skeleton](#skeleton)).
The rest is proposed. Pages 01-08 describe
the site as it is; this one describes where it is going and is the reference for
the refactor. It settles how the camera moves;
[11 Premise and voice](11-premise-and-voice.md) settles what it moves through,
and [12 Script](12-script.md) puts the two together scene by scene. Numbers given here are starting points to tune against the real
thing, not measurements.

## The idea

One document, one camera, one shot.

Scroll becomes the only clock. The carriage stays the index, but it is no longer
a menu you click out of — scrolling down walks the camera through the objects in
order, and each object opens into its own reading. Scrolling up from the
carriage goes back out of the window to the city. Clicking an object still
works; it becomes a fast path along the same shot rather than a second mechanism
beside it.

The site should read like an ordinary long page — you scroll, text arrives — and
look like a single unbroken take.

## Principles

These govern every decision further down. Where a later section seems to
contradict one, the principle wins and the section is wrong.

**1. Scroll is a position, not an event.** Every transform in the scene is a
pure function of one scalar, the scroll offset. No CSS transitions and no timed
keyframes anywhere scroll can reach. This is what makes "stop halfway and the
picture stops" fall out for free rather than needing to be engineered: a
half-open card is not a paused animation, it is simply the value of the function
at that offset.

The spoken layer is the one thing that looks like an exception and is not.
Lines anchored to the scene fade in and out as a function of `s` like
everything else; lines that answer the pointer live on the pointer channel,
which is event-driven already. Nothing on the scroll axis is ever an event. See
[11](11-premise-and-voice.md#anchored-and-reactive).

**2. One shot.** No cuts, ever. Any two reachable states are connected by a
continuous camera path, including the ones reached by clicking.

**3. The page never scrolls; the scene reads the scroll.** `.stage` stays
fixed and full-bleed. The document is tall only so the browser gives us a real
scrollbar, real trackpad inertia, real `Page Down`, and real `scrollTo`. Nothing
in the scene is laid out along that height.

**4. Reading is ordinary.** Once a chapter is open, text moves at the speed of
text and nothing else happens. The cinema lives at the seams between chapters,
not underneath the paragraphs.

**5. Click is a shortcut through the same shot.** It never teleports and never
plays a different transition from the one scrolling would have played.

**6. Two time-based animations survive, and only two.** The opening, and the
window transit in each direction. They are the only moments when the user is not
driving, which is exactly why they are allowed their own clock. Everything else
answers to the scroll position.

## The axis

The whole site is one monotonic scalar. Call it `s`, measured in scroll pixels
from the top of the document.

```
s=0                                                                      s=end
 │                                                                         │
 ├─ cover ─┤porch├═window═┤ hub ├─ ch.1 ─┬─ … ─┬─ ch.n ─┤porch├═window═┤ out ┤
 │         │     │ locked │index│        │     │        │     │ locked │     │
 0        240   480      ---   900    ~3000           ~9000                end
```

It is a ring: the city is at both ends, and the way out is the way in run
backwards. See [the ending](11-premise-and-voice.md#the-ending).

| Segment     | Span            | What the scroll does                                             | Stoppable |
| ----------- | --------------- | ---------------------------------------------------------------- | --------- |
| Cover       | 0 → 240         | city parallax; the opening line is anchored here, not a greeting | yes       |
| Porch       | 240 → 480       | camera eases back toward the window, blinds brighten             | yes       |
| Window in   | locked, ~1100ms | the existing animation, run inward; scroll input captured        | no        |
| Hub         | 480 → 900       | nothing moves; pointer parallax and pointer focus are live       | yes       |
| Chapter _n_ | see below       | approach, open, read, close, handoff                             | yes       |
| Porch out   | 240             | camera retreats to the window after the confrontation            | yes       |
| Window out  | locked, ~1100ms | the same fixed animation, run outward                            | no        |
| Departure   | 360             | the city again; links and colophon live here                     | yes       |

Upward from any point the same map runs in reverse. The two porches are the
same zone and the two window transits are the same locked segment, which is why
the ending costs almost nothing to build.

The transit is a glance out of the window and back, not a way in or out. Under
the premise the detective is already inside, having come through the connecting
door — see [11](11-premise-and-voice.md#the-premise).

### Why a porch

The window transit is locked, so it needs a run-up — otherwise a stray upward
flick at the hub fires a 1.1-second animation the user did not ask for. The
porch is a zone you can enter and back out of: the camera drifts toward the
window, the blinds brighten, nothing is committed. Crossing its far edge arms
the transit. The same zone exists on the way in, which is also what gives the
locked animation somewhere to hand control back to.

### Chapter spans

Per chapter, in scroll pixels:

| Beat     | Span                      | Notes                                                 |
| -------- | ------------------------- | ----------------------------------------------------- |
| approach | 560                       | object lifts, or camera dollies                       |
| open     | 420                       | the aperture expands to the viewport                  |
| read     | `max(contentHeight, 600)` | ordinary reading; nothing else moves                  |
| close    | 360                       | shorter than open — leaving should feel quicker       |
| handoff  | 480                       | camera pans to the next object, overlapping both ends |

Total document height is the sum, recomputed on resize and whenever section
content changes. It is not authored; it falls out of the map.

## A chapter, beat by beat

```
  approach ──────────────▶
              open ───────────▶
                     content ─────▶          (fades in over the last 45% of open)
                            read ────────────────────────▶
                                              close ──────────▶
                                                  pan ─────────────▶
                                                       next approach ─────▶
```

The overlaps are the whole point. Close, pan and the next approach are not three
steps in a queue; they share scroll range, so at no offset is exactly one thing
moving and at no offset is nothing moving. That is what keeps it a single take
rather than a sequence of transitions.

Content opacity deliberately lags: it starts at 55% through the open beat and
reaches 1 at the end. A half-open chapter should read as an object caught
mid-lift — a pose — not as a page with half-faded text on it. This is the main
mitigation for the fact that every intermediate state is now a legal resting
state.

## The aperture

The primitive that makes all of this one mechanism instead of four.

**Every chapter object declares a rectangle, in scene units, that becomes the
content viewport.** Opening a chapter is that rectangle morphing to fill the
screen while the object's artwork scales and fades around it. Closing is the
same function run backwards.

```
Hotspot                aperture (scene units)       becomes
─────────────────────────────────────────────────────────────────
车票  on the table      the ticket, and the card     the About panel
                       behind it
线路图 half unrolled,   the sheet as it unrolls      the Journey panel
      on a backrest
公文包 on the rack       the open lid's interior      the Stack panel
电脑  on the table      the screen                   the Projects panel
门    no hotspot        none: text only, over the    the chat
                       carriage as it stands
```

Two things follow from this that are worth stating plainly:

- The object does not "turn into a page". Its own surface is the page. The
  ticket, the laptop screen and the unrolled map are already rectangles the camera
  can be square-on to, so the morph is a rect-to-rect interpolation plus a
  cross-fade of what is printed on it. Nothing needs to be modelled in 3D.
- Because the aperture is declared per object rather than per section, an object
  with no plausible surface cannot be a chapter. That is a feature: it forces the
  artwork to answer "where does the text live" before the chapter exists.

## Carry or dolly

The two ways an object presents itself.

**Carry** — the object leaves its resting place and comes to the middle of the
frame. For anything a passenger could pick up: the ticket, the rolled map, the
briefcase.
The camera barely moves (a slight push, `fz` 1 → ~1.08, for depth); the object's
own transform interpolates from its resting rect to a centred rect, and the
carriage behind it blurs and dims.

**Dolly** — the object stays exactly where it is and the camera goes to it. For
anything that stays put: the laptop. The object's
transform is identity throughout; the camera's framing interpolates to fit the
aperture.

The test is physical plausibility first, and rectangles second: if the object
could be picked up, carry it; if carrying it would look absurd, dolly. Do not
mix the two on one object.

### What the read beat drives

Three chapters in a row are carries, so what keeps them apart is what the
scroll does once the object is open. Each has one motion of its own, and each
is a function of read progress like everything else:

| Object | Read progress drives                       |
| ------ | ------------------------------------------ |
| 车票   | turning it over, at the halfway point      |
| 线路图 | unrolling it, station by station           |
| 公文包 | drawing the books out, one spine at a time |
| 电脑   | the progress bar of the job left running   |

See [11](11-premise-and-voice.md#the-evidence-map) for why each object is what
it is.

### Framing maths

Carry, for aperture `A` resting at `A.cx, A.cy` and a target rect `V` centred in
the viewport:

```
k      = lerp(1, min(V.w/A.w, V.h/A.h) * FILL, t)     FILL ≈ 0.86
offset = lerp(0, V.centre - A.centre, ease(t))
```

Dolly, same fit but applied to the camera rather than the object:

```
fz = lerp(hubZoom, min(V.w/A.w, V.h/A.h) * FILL, t)   capped at DOLLY_MAX
fx = -(A.cx - 240) * u * fz
fy = -(A.cy - CAM_ORIGIN_Y) * u * fz
```

**The camera currently has no horizontal axis.** `focus.ts` writes `--fz` and
`--fy` only, because every framing so far has been vertically centred. Dolly
needs `--fx`, and `.cam`'s transform has to consume it. This is the one piece of
existing machinery the refactor genuinely has to extend rather than reuse.

Note also that `.cam`'s `transform-origin` is `50% 43.71%` — the gap in the
blinds, chosen for the window flight, not the centre of the frame. `syncFrame()`
already converts a desired framing offset into the equivalent translation for
that origin on the y axis; the same conversion is needed on x. See
[02 Scene coordinates](02-scene-coordinates.md).

`DOLLY_MAX` should be low — around 2.5 to 3. See [Performance](#performance)
for why that is a correctness constraint and not a taste one.

## Reading

The read beat is part of the same axis, and it carries two layers: the artifact
stays fixed in the frame for the whole chapter while the annotation scrolls past
it. See [11 Premise and voice](11-premise-and-voice.md#two-layers) — only the
annotation moves here.

The content panel is **not** a nested scroll container; its inner element is
translated:

```
y = -clamp(readProgress, 0, 1) * max(0, contentHeight - viewportHeight)
```

No nested scrolling means no scroll chaining, no two-scrollbar confusion, no
touch handoff bugs at the top and bottom edges, and one honest progress
indicator for the whole journey — which, under
[11](11-premise-and-voice.md#what-carries-it), is a timecode rather than a bar. The cost is that a very long chapter makes the global
scrollbar coarse; if a chapter ever runs past about three screens, that is a
signal to split it rather than to add a second scroller.

## Click, and the three locked segments

Clicking an object at the hub is a **transport**: a time-based camera move from
wherever the scroll currently is to the target chapter's read start, after which
the scroll position is force-set to match. Duration scales with distance and
caps at about 800ms.

Transport is deliberately built on the same mechanism as the window transit, so
there are exactly three locked segments in the whole site:

| Locked segment | Duration | Entered by                           |
| -------------- | -------- | ------------------------------------ |
| Opening        | existing | first load                           |
| Window transit | existing | crossing the porch, either way       |
| Transport      | ≤ 800ms  | clicking an object, Esc, a hash link |

During a locked segment the scroll listener is muted and the camera runs on its
own clock. **Any scroll input cancels it** and hands control back at the current
state, which keeps principle 1 intact: the user can always stop the picture.

On screen a transport is fast-forward, which is what it is on a tape — see
[11](11-premise-and-voice.md#what-carries-it).

Transport is why clicking chapter 4 from the hub does not flip through chapters
1 to 3. It is one camera move across the carriage, not a fast-forward.

## Routing

The route stops being a view and becomes a position.

- `#/about` resolves to a scroll offset — the read start of that chapter.
- On first load **with** a hash: skip the opening, place the scroll offset
  directly, render at that offset on the first frame. No animation, no flash of
  the carriage.
- While running: the hash follows the current chapter via throttled
  `replaceState`.
- `history.scrollRestoration = 'manual'`, or the browser will fight the map on
  back-navigation and reload.
- Back and forward become transports.

The section pages as they exist now — a shell that replaces the scene — go away.
What should replace them is a **plain document fallback**: with JavaScript off,
or `prefers-reduced-motion: reduce`, the sections render as one ordinary
vertical page in chapter order. That fallback is not a consolation prize; it is
the baseline this whole design is an enhancement of, and it is what search
engines and screen readers should see first. See
[07 Content and routing](07-content-and-routing.md).

## What happens to focus

The existing focus system is not replaced — its scope narrows.

- **At the hub** it works exactly as it does today: magnetic snapping with
  hysteresis, the pulled light, the lift. The hub is still an index you point at.
- **Inside a chapter** pointer focus is suspended. The chapter owns its object,
  and the scroll owns the camera. Pointer parallax is damped to zero across the
  approach beat so the camera does not fight two inputs.
- The per-object `presence` value that chapters interpolate is the same quantity
  focus already computes as a binary snap. It becomes continuous and
  scroll-driven; the constants in [04 Focus system](04-focus-system.md) keep
  their meaning at the hub.

## Phases

Resist adding a phase per beat. The phase machine's job shrinks to one thing:
**which locked segment, if any, is running.** Everything else is the scalar.

Proposed set: `intro`, `transit`, `transport`, `free`. The current `idle`,
`back`, `settling` and `peek` collapse into `transit` and `free`, and the
chapter beats are not phases at all. If a bug ever tempts you to add
`phase === 'opening-chapter-3'`, the scalar has stopped being the single source
of truth and the fix is elsewhere.

## Performance

This design puts a magnifying glass on the exact failure recorded in
[09 Fix log](09-fix-log.md#f-001-chrome-the-city-drawn-over-the-carriage). Dolly
is a camera zoom; a camera zoom drives the carriage layer's raster scale up; that
is what produced the Chrome fault in the first place. The constraints:

- **Cap `DOLLY_MAX` at 2.5-3.** This is affordable because the dolly does not
  have to magnify the aperture to legibility — it only has to get close enough
  that the cross-fade to the content panel is invisible. The panel itself is a
  normal DOM layer rendered at 1:1, never a scaled bitmap. Past the cross-fade
  the zoom is doing no work and should not keep climbing.
- **Transform and opacity only** in the per-frame path. Nothing that triggers
  layout, nothing that creates or destroys a compositing layer mid-scroll.
- **One `rAF` loop.** The scroll listener is passive and writes a number; all
  reading of layout happens once per frame, before any writing.
- **`content-visibility: auto` on closed chapters**, and the panels kept in the
  DOM in reading order for assistive technology rather than built on entry.
- **Recompute the segment map on resize**, and size the stage in `svh`/`dvh`:
  the iOS address bar changes viewport height mid-scroll, which would otherwise
  shift every offset underneath the user.

### On CSS scroll-driven animations

`animation-timeline: scroll()` is the declarative version of principle 1 and
runs off the main thread, which is tempting. Support as of early 2026 is Chrome
and Edge from 115 and Safari from 26, with Firefox behind a flag; iOS needs
checking before it is relied on. The reason not to build the camera on it is not
support but shape: scroll timelines express linear mappings from scroll to
keyframes, and the camera needs per-object framing computed from live viewport
size, overlapping handoffs, and branching for locked segments. That is
JavaScript's job. It remains a good fit for the simple always-on layers — the
city parallax, the rain — which could move off the main thread without touching
the camera model.

## What this touches

A survey, not an implementation plan. No code has been changed.

| File                 | Change                                                                    |
| -------------------- | ------------------------------------------------------------------------- |
| `scene/scroll.ts`    | new: the segment map, `s`, and the locked-segment arbiter                 |
| `scene/chapter.ts`   | new: per-chapter beat interpolation, carry and dolly                      |
| `scene/focus.ts`     | add `--fx`; narrow pointer focus to the hub; expose `presence`            |
| `scene/hotspots.ts`  | add `aperture` and `transit` per object; chapter order; decoys            |
| `tools/art/room.py`  | draw the rolled map, the card behind the ticket, the books                |
| `scene/opening.ts`   | phases reduce to the locked segments; transport joins the machine         |
| `scene/scene.css`    | remove transitions from anything scroll drives; `.cam` consumes `--fx`    |
| `router.ts`          | routes resolve to offsets; manual scroll restoration                      |
| `sections/layout.ts` | panels live in the scene; the standalone shell becomes the no-JS fallback |

## Open questions

1. **Auto-settle.** Should releasing in a transition zone ease to the nearer
   end? Recommendation: no. It contradicts principle 1, and the content fade
   above is the cheaper fix for the thing auto-settling would be protecting
   against.
2. **Chapter order.** Proposed: about (ticket) → journey (rolled map) → stack
   (briefcase) → projects (laptop) → chat. The first three are carries, kept
   distinct by what the read beat drives, and it is the order the evidence
   would be found in — see
   [11](11-premise-and-voice.md#the-evidence-map). `chat` is last by
   construction: it is the confrontation, and the only chapter with no object
   and no picture of its own: it is played as text over the carriage.
   `notes`, `hobby` and `chat` cannot become chapters until they have artwork
   and therefore an aperture.
3. **Is the cover the top of the document?** Proposed yes: `s = 0` is outside,
   matching where the opening leaves the camera.
4. **Mobile apertures.** A 390px-wide viewport is nearly the inverse of the
   ticket's aspect ratio. Either the aperture is declared per breakpoint, or the
   carried object rotates upright during the approach — the second is more
   interesting and more work.
5. **Does the window transit stay locked in both directions?** Proposed yes.
   It is the one moment the site asks to be watched rather than driven.

## Skeleton

What `scene/scroll.ts` does now, and what it does not yet.

Built:

- Once seated (phase `hub`), `html.story` makes the document as tall as the map
  (`.track`) and the scroll offset drives the scene. Leaving the hub phase (the
  window, a replay) holds the page at the top again.
- The axis starts at the hub (420 px), then about → journey → stack → projects,
  each approach 560, open 420, read (content overflow + 600), close 360.
- Carry for the ticket, the map and the briefcase: a `.carry` element, sized
  once per chapter, is transformed from the object's resting rect to the middle
  of the frame. Its sprite on the table hides and `.gone`, a patch of the room
  rendered without it (`build.py`, `CARRIED`), shows where it lay. The carriage
  dims around it through `.spot`.
- Dolly for the laptop: the camera gains `--fx`, and `focus.ts` frames any scene
  point at any zoom, capped at `DOLLY_MAX` 2.5.
- Panels: one per chapter, always in the DOM, faded in over the last 45% of the
  open beat and translated through the read. All layout is read in `layout()`,
  on load and resize, never per frame.
- Pointer focus and parallax are scaled by the hub weight, so they give way as
  a chapter is approached.
- Click, Esc and `#/id`: a transport, ≤ 800 ms, cancelled by wheel, touch or a
  key. `#/id` on load lands with the chapter open and no opening. The hash
  follows the open chapter by `replaceState`.

Not yet:

- The cover, porches and window transits on the axis; the opening still runs
  on its own phases before the axis begins.
- Overlapping handoffs: chapters follow one another with a moment of rest in
  between, and there is one carry element, so two objects never move at once.
- The transport scrolls through the chapters between, rather than moving the
  camera once across the carriage.
- The read beat's own motion per object, the open-state art (stage 7 in
  [13](13-art-review.md)), the chat, the timecode and the spoken lines.
- The plain-document fallback; the old section pages (`sections/layout.ts`)
  are no longer reached.

## Keep in sync

- The segment table here and the constants in `scene/scroll.ts` once it exists.
- `DOLLY_MAX` here, in `scene/chapter.ts`, and the raster-scale reasoning in
  [05 Rendering and compositing](05-rendering-and-compositing.md).
- The aperture table here and the `aperture` fields in `hotspots.ts`, which must
  also match what `tools/art/room.py` actually draws.
- The chapter order here and the order in `content/sections.ts`.
