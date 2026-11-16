# Personal site

A pixel-art personal site. It opens on a night train: the camera tilts the
blinds open, flies out through the window, and settles on the city outside.
Click once and it flies back in — and the carriage itself is the menu. Whatever
object the light settles on is the section you enter.

The current version is **structure and interaction only**. Every piece of copy
is a placeholder; search for `TODO` to find what still needs writing.

Stack: Vite + TypeScript, no runtime dependencies.

## Development

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # type check, then bundle into dist/
npm run preview  # serve the built output
npm run format   # Prettier
```

The site is fully static: `dist/` can be dropped onto any static host. Routing
uses the hash (`#/about`), so no server rewrite rules are needed.

## Layout

```
docs/                 technical documentation (start at docs/README.md)
public/assets/        scene artwork (WebP, generated — do not edit by hand)
tools/art/            the Python scripts that generate that artwork
src/
  main.ts             entry point: renders either the scene or a section page
  router.ts           hash router
  content/
    site.ts           site-wide copy (cover headline, external links)  <- edit
    sections.ts       section registry: id / name / placeholder blocks <- edit
  scene/
    units.ts          the 480x480 scene grid and its screen conversions
    hotspots.ts       focusable objects: target, snap region, light, outline
    dom.ts            builds the carriage DOM
    focus.ts          snapping, spotlight and camera, driven per frame
    opening.ts        phase machine: intro / idle / back / settling / hub / peek
    scene.css         scene styles and every animation timing
  sections/
    layout.ts         section page shell (shared by all sections for now)
    sections.css
  styles/
    tokens.css        colour, type and motion variables  <- recolour here
    base.css
```

## Artwork

Everything in `public/assets/` — the sky, the three city layers, the carriage —
is produced by the scripts in `tools/art/`, not exported from an image editor.
To change the picture, change the script and regenerate:

```bash
pip install pillow numpy scipy
python3 tools/art/build.py
```

- `street.py` / `city.py` — mid distance: the neon district plus a stretch of
  derelict blocks (`c2.webp`, one long looping strip)
- `far.py` — distant skyline `c1.webp`, trackside gear `c3.webp`, sky `sky.webp`
- `room.py` — the carriage `room.webp` and its side extensions
  `room-l.webp` / `room-r.webp`
- `px.py` / `parts.py` — canvas, lighting and the shared building blocks

Art is drawn on a 1x pixel grid and written out at 2x: EPX trims the
stair-stepping off diagonals in the albedo, while lighting and bloom are
computed at the output resolution. The factor lives in `px.SCALE`, set by
`build.py`.

Two things have to stay in sync by hand. The focusable objects' outlines in
`src/scene/hotspots.ts` must match where `room.py` actually draws them, and if
a city layer changes size, `.ly`'s height and each layer's `--tile` in
`scene.css` have to follow.

## Documentation

`docs/` covers the architecture, the scene coordinate system, the phase
machine, the focus system, the compositing rules and the art pipeline in
detail. Start at [docs/README.md](docs/README.md).

## Key design decisions

**One scene grid.** The carriage is a 480x480 drawing. Object positions, snap
regions and light pools are all expressed on that grid, independent of screen
size; `units.ts` does the conversion. Moving an object means editing
`hotspots.ts` and nothing else.

**Focus, not zoom.** The camera holds one fixed wide framing and never pushes
in with the pointer. What snaps is the light and the object: the light is
pulled in as the pointer approaches, snaps on entering range, and lets go on
leaving. The references are the iPadOS pointer and tvOS focus — lift and
brighten the target rather than dimming everything else.

**Phases in CSS, switching in TS.** A class on `.stage` selects the phase and
every duration lives in `scene.css`; TypeScript only swaps the class. To retune
the opening, edit the `duration` and `delay` on the `.intro .*` rules.

## To do

- [ ] Write the real copy: `content/site.ts`, `content/sections.ts`
- [ ] notes / hobby / chat have no object yet — draw the artwork, then register
      them in `hotspots.ts`
- [ ] Section entry transition (currently a fade; the goal is an object being
      picked up)
- [ ] Notes system: Markdown sources, categories, search
- [ ] Chat section and a machine-readable entry point
- [ ] Remember that a returning visitor has seen the opening (currently only
      within a single visit)
- [ ] Verify touch on a real device: tap to focus, tap again to enter
- [ ] Internationalisation
- [ ] Chrome: the city outside is drawn over the carriage and flickers after
      the opening and when focus changes. See
      [docs/05-rendering-and-compositing.md](docs/05-rendering-and-compositing.md)
