# 03 Phases and the opening

## The division of labour

Every duration, delay and easing curve in the scene lives in `scene.css`.
TypeScript never sets a timing. `Opening` does exactly one thing: it decides
which class sits on `.stage`, and the stylesheet does the rest.

```
.stage.intro      .stage.idle      .stage.back      .stage.hub ...
      │                 │                │                │
      └── .intro .cam { animation: push 1.4s linear 1.4s both }
                        └── .idle .cam { transform: ...; visibility: hidden }
```

To retune the opening, edit the `.intro .*` rules. To change _when_ a phase
ends, look at the `animationend` listeners in `opening.ts`.

## The six phases

| Phase      | What the visitor sees                                                    | How it ends                                       |
| ---------- | ------------------------------------------------------------------------ | ------------------------------------------------- |
| `intro`    | Carriage close-up, blinds tilt open, camera flies out through the window | the headline finishes fading in                   |
| `idle`     | City outside, headline, hint to go back                                  | a click, a wheel event, Enter / Space / Escape    |
| `back`     | Camera retreats back through the window                                  | the camera animation finishes                     |
| `settling` | Easing from a skipped opening to the seated framing                      | the tween promises resolve                        |
| `hub`      | Seated in the carriage, objects can take focus                           | entering a section, or looking outside            |
| `peek`     | Looking back out of the window from the hub                              | the headline finishes fading in, ending in `idle` |

`settling` exists only so the hub's interactions and looping animations stay
switched off while the camera is still moving after a skip. Without it the
objects' filters and the pointer parallax would start up mid-zoom.

## The opening timeline

All of this is in `scene.css` under the `/* phases */` comment.

| Time   | What happens                                                                             | Rule                                                |
| ------ | ---------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 0.0s   | Carriage, blinds shut, passing lights sweeping                                           | base styles                                         |
| 0.7s   | Blinds tilt open over 0.55s, in 6 steps; the sweep fades; the glow from outside comes up | `.intro .blinds i`, `.intro .pass`, `.intro .g-out` |
| 1.4s   | Camera pushes through the gap over 1.4s; the city outside scales up in step              | `.intro .cam`, `.intro .out`                        |
| 2.1s   | Rain in front of the city fades in                                                       | `.intro .rain2`                                     |
| 2.85s  | Headline fades in over 0.6s                                                              | `.intro .hero`                                      |
| ~3.45s | `animationend` on the headline switches to `idle`                                        | `opening.ts`                                        |

Returning is the same motion reversed and slightly quicker:

- `.back .cam` and `.back .out` replay `push` and `outgo` with
  `animation-direction: reverse` over 1.2s.
- `.back .hero` fades the headline out over 0.3s.
- `animationend` for `push` on `.cam` switches to `hub`.

`peek` reuses the `intro` rules with overrides — 1.3s for the camera instead of
1.4s, no delays — so going back out from the hub is a touch faster than the
opening.

## The camera curve

`@keyframes push` is 25 sampled keyframes, not a smooth function. They are
generated so that:

- The **zoom is even on a logarithmic scale**. Linear interpolation of `scale`
  reads as a camera that starts fast and ends slow; even steps in `log(scale)`
  read as a constant push.
- A **sine ease in and out** is applied over the whole move, so it starts and
  ends at rest.
- Every keyframe **multiplies the framing**: `scale(calc(var(--fz, 1) * N))`.
  The first keyframe is exactly the framing, the last is 6.5 times it.
- **Opacity fades out** over roughly the last 40% of the zoom, finishing with
  `visibility: hidden`. By then the carriage is far out of frame.

`@keyframes outgo` follows the identical curve, scaling the city outside from
`--os` (0.42 landscape, 0.9 portrait) up to 1. Because both use the same
sampling, the window and the city stay locked together through the whole move.

The 6.5 figure is a compromise: large enough that the window frame leaves the
screen before the carriage has faded out, small enough to limit how far Chrome
raises the layer's raster scale. See [05](05-rendering-and-compositing.md).

## Skipping

`Opening.skip()` has to cope with being called at any point during the opening,
including halfway through the fly-through. Cutting straight to `hub` would
teleport the camera from, say, 3x back to the framing in one frame.

Instead it samples the current computed `transform` and `opacity` of the three
layers that are moving — `.cam`, `.out` and `.rain2` — switches to `settling`,
and starts a Web Animations tween from those values:

```ts
el.animate([from, {}], { duration: 700, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
```

The empty final keyframe means "whatever this element should look like in the
new phase", which the browser fills in from the cascade. When all three
promises resolve, the phase moves to `hub`.

Two guards matter:

- `skip()` returns immediately unless the phase is `intro`, so a stray click
  cannot restart the tween.
- The resolution handler checks that the stored animation array is still the
  current one _and_ that the phase is still `settling`. A replay or a navigation
  during the tween cancels the animations, and a stale callback must not drag
  the scene back into the hub afterwards.

Under `prefers-reduced-motion: reduce`, `skip()` jumps straight to `hub` and the
constructor does the same on load.

## The forced reflow in `set()`

```ts
this.els.stage.className = `stage ${p}`;
void this.els.stage.offsetWidth;
```

That line is load-bearing. The return animation and the opening both use the
same `@keyframes push`. If two phase changes land in the same frame — idle is
entered and a click is handled before the browser has recalculated styles — the
browser never sees the intermediate state. Since the animation name has not
changed, it treats the return as a continuation of the opening's animation,
which has already finished. The return then never advances a frame and the
scene stays stuck halfway.

Reading `offsetWidth` forces the style recalculation for each phase as it is
set, so each animation is created and destroyed properly. It costs one
synchronous layout, five or six times per visit.

## Ending a phase

Two `animationend` listeners drive the automatic transitions, and both are
defensive:

```ts
els.hero.addEventListener('animationend', (e) => {
  if (
    e.target === els.hero &&
    e.animationName === 'heroin' &&
    (this._phase === 'intro' || this._phase === 'peek')
  )
    this.set('idle');
});
```

The `e.target` check is needed because animation events from descendants bubble,
and the carriage contains a dozen looping animations. The phase check prevents a
late event from a cancelled animation moving the scene somewhere unexpected.

## Pausing the carriage

```css
.idle .cam *,
.back .cam *,
.settling .cam * {
  animation: none !important;
}
```

While the camera is zoomed out or moving, every looping animation inside the
carriage — rain on the glass, steam, the blinking cursor, the neon flicker — is
switched off. They are invisible at that point anyway, and leaving them running
means Chrome keeps promoting those elements while the ancestor's raster scale is
being driven up by the zoom. See [05](05-rendering-and-compositing.md).

## Keep in sync

- The timeline table above and the `.intro .*` rules in `scene.css`.
- The `6.5` factor appears in `@keyframes push`, in `.idle .cam`, and in
  [05](05-rendering-and-compositing.md).
- `CAM_ORIGIN_Y` in `focus.ts` and `transform-origin` on `.cam`.
