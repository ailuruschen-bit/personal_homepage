# Documentation

Reference material for reviewing and maintaining this site. The
[project README](../README.md) covers what the site is and how to run it;
these pages explain how it works and why it is built this way.

Read in order on a first pass. After that, each page stands on its own.

Pages 01-08 describe the site as it is built. 09 records fixes worth
remembering. 10 to 13 are proposals and plans and are not implemented; where they
contradict an earlier page, the earlier page is still what the code does.

| Page                                                            | What it covers                                                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| [01 Architecture](01-architecture.md)                           | Module map, boot sequence, where state lives, build and deploy                  |
| [02 Scene coordinates](02-scene-coordinates.md)                 | The 480x480 grid, the camera model, the conversions in `units.ts`               |
| [03 Phases and the opening](03-phases-and-opening.md)           | The phase machine, the opening timeline, how CSS and TypeScript divide the work |
| [04 Focus system](04-focus-system.md)                           | Snapping, the pull on the light, the spotlight pool, parallax, input handling   |
| [05 Rendering and compositing](05-rendering-and-compositing.md) | Layer order, what is promoted and when, which rules exist for Chrome            |
| [06 Art pipeline](06-art-pipeline.md)                           | `tools/art/`: the canvas model, lighting, EPX, each layer, regenerating         |
| [07 Content and routing](07-content-and-routing.md)             | The hash router, the section registry, the page shell                           |
| [08 Maintenance recipes](08-maintenance-recipes.md)             | Step-by-step for the changes you are most likely to make                        |
| [09 Fix log](09-fix-log.md)                                     | Bugs whose fix left rules in the code that look arbitrary without the story     |
| [10 Scroll narrative](10-scroll-narrative.md)                   | _Proposed._ Scroll as the only clock: chapters, apertures, carry and dolly      |
| [11 Premise and voice](11-premise-and-voice.md)                 | _Proposed._ The detective and his tape; a plausibility audit; the objects       |
| [12 Script](12-script.md)                                       | _Proposed._ The setting, the cast and the lines, scene by scene                 |
| [13 Art review](13-art-review.md)                               | _Plan._ A strict critique of the artwork and a numbered list of fixes           |

## Conventions used in these pages

- **Scene unit** — one step on the 480x480 grid the carriage is drawn on. Not a
  CSS pixel. See [02](02-scene-coordinates.md).
- **Art pixel** — one pixel of the 1x grid the artwork is drawn on in
  `tools/art/`, before the 2x upscale. See [06](06-art-pipeline.md).
- **Phase** — one of `intro`, `idle`, `back`, `settling`, `hub`, `peek`, carried
  as a class on `.stage`. See [03](03-phases-and-opening.md).
- File references are repository-relative, for example `src/scene/focus.ts`.

## Keeping these pages honest

Several facts are duplicated between the code and these pages — timings, the
`6.5` zoom factor, layer sizes. When you change one of those, grep `docs/` for
the number. Anything that must stay in sync across files is called out in the
relevant page under a **Keep in sync** heading.
