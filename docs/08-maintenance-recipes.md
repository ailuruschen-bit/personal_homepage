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

1. Move it in `tools/art/room.py`.
2. Regenerate: `python3 tools/art/build.py`.
3. Update the matching entry in `src/scene/hotspots.ts`:
   - `shape` must hug the object's new outline exactly.
   - `zone` should be a little larger than the object.
   - `light` is where the pool lands and how big it is.

Check: focus the object in the browser. If a strip of wall or table lifts with
it, `shape` is too generous. If the pool sits off the object, `light` is wrong.

## Add a new section reachable from the carriage

1. Add an entry to `src/content/sections.ts` with a new `id`.
2. Draw an object in `tools/art/room.py` and regenerate.
3. Register a hotspot in `src/scene/hotspots.ts` with `target` set to that id,
   plus `zone`, `light` and `shape`.
4. If the section needs a layout of its own, branch in `sections/layout.ts`.

Check: the caption shows the section title rather than the raw id, and clicking
navigates to `#/<id>`.

## Change the artwork

1. Edit the relevant script in `tools/art/` — see [06](06-art-pipeline.md) for
   which file owns what.
2. `python3 tools/art/build.py`
3. If a city layer's pixel dimensions changed, update `.ly`'s `height` and that
   layer's `--tile` in `scene.css`.
4. If anything focusable moved, update `hotspots.ts`.

Note: regenerating always produces a diff in `public/assets/` even with no
change, because the WebP encoder version differs between machines. Check the
images, not the diff.

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

If you regenerated artwork, confirm the images actually changed before
committing them — see the note above about encoder differences.

## Things that are easy to get wrong

- **Editing `public/assets/` by hand.** It is build output. The next
  regeneration overwrites it.
- **Changing `transform-origin` on `.cam`** without updating `CAM_ORIGIN_Y` in
  `focus.ts`. The hub framing goes vertically off.
- **Adding `will-change` to scene elements.** It is load-bearing and tuned by
  experiment; see [05](05-rendering-and-compositing.md) before adding or
  removing any.
- **Using `overflow: hidden` on `.stage`.** It must stay `clip`, or focusing an
  off-screen hotspot scrolls the whole scene out of view.
- **Assuming `npm run build` type checks the art scripts.** It does not. Python
  is checked only by running it.
