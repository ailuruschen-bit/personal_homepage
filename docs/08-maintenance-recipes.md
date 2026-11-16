# 08 Maintenance recipes

Step-by-step for the changes most likely to come up. Each one lists the files
to touch and what to check afterwards.

## Change the copy

1. Edit `src/content/site.ts` for the cover headline and links.
2. Edit `src/content/sections.ts` for section titles, ledes and blocks.
3. Search for `TODO` to find anything still unwritten, including the `<title>`
   and meta description in `index.html`.

Check: `heroTitle` still contains exactly one `\n` — `scene/dom.ts` splits on it
and renders two lines.

## Recolour the site

Edit `src/styles/tokens.css`. The dark half drives the scene, the light half
drives the section pages. Never hard-code a colour in a component.

The scene artwork is not themed by tokens — its colours are baked into the
generated images. Recolouring the scene means editing the palettes in
`tools/art/` and regenerating.

## Retune the opening

Everything is in `scene.css` under `/* phases */`. Change the `duration` and
`delay` on the `.intro .*` rules. The phase ends when an animation ends, so if
you change which animation finishes last, update the `animationend` listener in
`opening.ts` to match.

See the timeline table in [03](03-phases-and-opening.md).

## Move a focusable object

1. Change its `at` in `OBJECTS` at the top of `tools/art/room.py`. Its zone and
   light are relative to it and move with it; adjust them there if the object's
   size changed.
2. `npm run art` — rebuilds the assets, the sprite and the geometry, then checks.

Check: open the page with `?debug=geometry`. The dashed zone should be a little
larger than the object, the ellipse should sit on it, the blue box should hug
it.

## Add a new section reachable from the carriage

1. Add an entry to `src/content/sections.ts` with a new `id`.
2. In `tools/art/room.py`, add the object to `OBJECTS` under that id, draw it
   through `place(g, '<id>', (0, 0))` relative to its own corner, and run
   `npm run art`.
3. Register a hotspot in `src/scene/hotspots.ts` with `target` set to that id
   and `...geo('<id>')`. `npm run art:check` fails until steps 2 and 3 agree.
4. If the section needs a layout of its own, branch in `sections/layout.ts`.

Check: the caption shows the section title rather than the raw id, and clicking
navigates to `#/<id>`.

## Change the artwork

1. Edit the relevant script in `tools/art/` — see [06](06-art-pipeline.md) for
   which file owns what.
2. `npm run art`
3. If a city layer's pixel dimensions changed, update `.ly`'s `height` and that
   layer's `--tile` in `scene.css`; `npm run art:check` says so if you forget.
4. `npm run art:preview` writes comparison images to `.review/`.

A rebuild only rewrites an asset whose pixels changed, so an unchanged picture
leaves no diff even though WebP encoders differ between machines.

## Add a new object to the carriage without making it focusable

Draw it in `room.py` and regenerate. Nothing else is needed — only entries in
`hotspots.ts` become interactive.

## Debug the scene's state

In the console:

```js
const st = document.querySelector('#stage');
st.className; // current phase
st.style.getPropertyValue('--fz'); // framing zoom
document.querySelectorAll('.pop.on'); // which object is focused
st.getAnimations().map((a) => a.animationName);
```

To jump straight to a phase without waiting for the opening, click **跳过** or
reload with `prefers-reduced-motion` forced on in DevTools' Rendering panel.

## Before committing

```bash
npm run build     # type check plus bundle
npm run format    # Prettier
```

The repository uses English conventional commit messages, for example
`fix(scene): ...`, `feat(scene): ...`, `docs: ...`.

`?debug=geometry` overlays every object's zone, light and sprite box, the
window and the camera origin.

## Things that are easy to get wrong

- **Editing `public/assets/` by hand.** It is build output. The next
  regeneration overwrites it.
- **Writing a coordinate by hand in `src/`.** Positions come from
  `tools/art/room.py` via `geometry.gen.*`; never edit those files, and never
  repeat a number from them.
- **Adding `will-change` to scene elements.** It is load-bearing and tuned by
  experiment; see [05](05-rendering-and-compositing.md) before adding or
  removing any.
- **Using `overflow: hidden` on `.stage`.** It must stay `clip`, or focusing an
  off-screen hotspot scrolls the whole scene out of view.
- **Assuming `npm run build` type checks the art scripts.** It does not. Python
  is checked only by running it.
