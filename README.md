# Personal site

A pixel-art personal site. It opens on a night train: the camera tilts the
blinds open, flies out through the window, and settles on the city outside.
Click once and it flies back in — and the carriage itself is the menu. Whatever
object the light settles on is the section you enter.

The reader is cast as a detective who has let themselves in while the occupant
is away. Nothing in the carriage introduces itself: the ticket, the route map,
the briefcase and what is still open on the laptop are evidence, and the site is
what you make of them.

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

## Documentation

Everything below the level of "what this project is" lives in `docs/`: the
module map and boot sequence, the scene coordinate system, the phase machine,
the focus system, the compositing rules, the art pipeline, routing, maintenance
recipes, and a log of fixes worth remembering. Start at
[docs/README.md](docs/README.md).

## Design direction

**One scene grid.** The carriage is a 480x480 drawing. Object positions, snap
regions and light pools are all expressed on that grid, independent of screen
size; `units.ts` does the conversion. Moving an object means editing
`hotspots.ts` and nothing else.

**Focus, not zoom.** Pointing at the scene never moves the camera. What snaps
is the light and the object: the light is pulled in as the pointer approaches,
snaps on entering range, and lets go on leaving. The references are the iPadOS
pointer and tvOS focus — lift and brighten the target rather than dimming
everything else. (Scroll is a different matter — see below.)

**Phases in CSS, switching in TS.** A class on `.stage` selects the phase and
every duration lives in `scene.css`; TypeScript only swaps the class. To retune
the opening, edit the `duration` and `delay` on the `.intro .*` rules.

**Artwork is code.** Nothing in `public/assets/` comes out of an image editor.
The sky, the three city layers and the carriage are all drawn by the Python
scripts in `tools/art/`, which means lighting, bloom and the 2x upscale are
reproducible and a change to the picture is a change to a script. See
[docs/06](docs/06-art-pipeline.md).

**No framework, no runtime dependencies.** The scene is a few hundred lines of
DOM and CSS driven by one per-frame loop. A framework would add a reconciler
between the pointer and the paint without buying anything the scene needs.

**Where it is going: scroll as the only clock.** The site should read like an
ordinary long page and look like a single unbroken take. Scrolling down from
the carriage walks the camera through the objects in order and opens each one
into its own reading; scrolling up goes back out of the window. Every transform
becomes a function of scroll position rather than of elapsed time, so the
picture stops wherever the reader stops. Clicking an object stays as a fast
path along the same shot. Under the premise above those stop being transitions
and become actions: you pick a thing up, or you lean in. Written up in
[docs/10](docs/10-scroll-narrative.md) and
[docs/11](docs/11-premise-and-voice.md); none of it is built yet.

**Facts are never behind the fiction.** Who this is, what he works on, how to
reach him: plain in the artifact itself, present in the no-JavaScript document,
reachable by deep link. The voice is the second layer, never the carrier.

## Roadmap

- [ ] **Scroll narrative** — the refactor described in
      [docs/10](docs/10-scroll-narrative.md): one document, one camera, chapters
      opened by scroll instead of pages opened by click
- [ ] **Content model** — split sections into artifact, annotation and plain
      facts, per [docs/11](docs/11-premise-and-voice.md)
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
