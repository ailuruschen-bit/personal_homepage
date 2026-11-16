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

**Focus, not zoom.** The camera holds one fixed wide framing and never pushes
in with the pointer. What snaps is the light and the object: the light is
pulled in as the pointer approaches, snaps on entering range, and lets go on
leaving. The references are the iPadOS pointer and tvOS focus — lift and
brighten the target rather than dimming everything else.

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

## Roadmap

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
