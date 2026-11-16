# 01 Architecture

> **Planned change.** A scroll driver and a chapter module join the map, and the section shell stops being a separate view. See [10 Scroll narrative](10-scroll-narrative.md).

## The shape of the thing

The site is a single static page. There is no framework, no runtime dependency
and no build-time code generation beyond what Vite does to bundle TypeScript.
Everything that moves is either a CSS animation or a value written to an inline
style from a `requestAnimationFrame` loop.

There are exactly two kinds of screen:

1. **The scene** — the night train. This is the landing page and the menu.
2. **A section page** — a conventional, light, readable document page.

The router decides which one is mounted. They never coexist.

## Module map

```
main.ts ──────────── owns the mount point, listens to the router
  │
  ├── router.ts ──── parses location.hash into a Route
  │
  ├── scene/index.ts ─ mounts the scene, wires input, returns a destroy handle
  │     ├── dom.ts ──── builds the markup once, returns the live nodes
  │     ├── opening.ts ─ phase machine (which class is on .stage)
  │     ├── focus.ts ─── per-frame loop: framing, parallax, snapping, light
  │     ├── hotspots.ts  data: the focusable objects
  │     └── units.ts ─── scene <-> screen coordinate conversion
  │
  └── sections/layout.ts ─ renders a section page from its definition
        └── content/sections.ts  data: the section registry
```

`content/site.ts` and `content/sections.ts` hold all the copy. Nothing else in
`src/` contains prose that is meant to ship.

## Boot sequence

`main.ts` runs once on load:

1. `parse()` turns `location.hash` into a `Route`.
2. `render(route)` tears down whatever is mounted and mounts the new screen.
3. `onChange(render)` re-runs step 2 on every `hashchange`.

Mounting the scene is the interesting path:

1. `buildScene(root)` writes the entire carriage markup in one `innerHTML`
   assignment and returns a `SceneEls` record of the nodes that are touched at
   runtime. The markup is static apart from three interpolated pieces: the
   blind slats, the lifted object copies and the hotspot buttons, all derived
   from `hotspots.ts`.
2. `new Opening(els)` installs the phase machine. It starts in `intro`.
3. `new FocusEngine(els, phase, labelOf)` is constructed but does nothing until
   `start()` is called.
4. `opening.onPhase` is pointed at `focus.syncFrame` so the framing variables
   are recomputed the instant a phase changes, before the browser does its
   style recalculation for that frame.
5. If the visitor has already seen the opening this visit, `opening.skip()`
   runs immediately.
6. `focus.start()` begins the `requestAnimationFrame` loop.

`mountScene` returns a handle whose `destroy()` stops the loop, cancels pending
animations, removes the document-level key listener and empties the root. The
router calls it before every navigation. Listeners attached to elements inside
the root do not need removing — the elements go with the root.

## Where state lives

There is no store. State sits in four places, each with one owner:

| State                       | Owner                                                                       | Shape         |
| --------------------------- | --------------------------------------------------------------------------- | ------------- |
| Which screen is mounted     | `location.hash`                                                             | the URL       |
| Which phase the scene is in | `Opening._phase`, mirrored as a class on `.stage`                           | string        |
| Camera framing              | `--fz` / `--fy` custom properties on `.stage`, written by `focus.syncFrame` | CSS variables |
| Focus, light pool, parallax | `FocusEngine` fields, written to inline styles each frame                   | numbers       |

Two of those are deliberately mirrored into the DOM. The phase is a class
because every animation in `scene.css` is selected by it. The framing is a pair
of custom properties because the camera transform has to be composed by CSS —
the opening animation multiplies the framing zoom rather than replacing it, so
a skipped opening lands on exactly the same framing the return animation does.

`main.ts` holds one module-level flag, `openingSeen`, so returning from a
section page does not replay the opening. It resets on a full page load, which
is why "remember a returning visitor" is still on the to-do list.

## Build and deploy

`npm run build` runs `tsc --noEmit` and then `vite build`. The type check is a
gate, not a compile step; Vite does its own transpilation and does not type
check. Output lands in `dist/` and is pure static files.

`public/assets/` is copied through verbatim, so the `/assets/...` URLs in CSS
and in `room.webp` references are stable between dev and production.

Routing is hash-based specifically so that `dist/` can be served by anything
that can serve files. There is no history API use and no server rewrite
requirement.

### Browser support

The code assumes a modern evergreen browser. The notable requirements are
CSS custom properties in `calc()`, the Web Animations
API (`Element.animate`, used by `Opening.skip`), `overflow: clip` and
`:focus-visible`. `prefers-reduced-motion: reduce` is honoured by skipping
straight to the hub and freezing the film grain.

## Keep in sync

- `src/scene/units.ts` `SCENE = 480` and the 480x480 grid assumed throughout
  `scene.css` — see [02](02-scene-coordinates.md).
- Nothing positional: object geometry, the window, the camera origin and the
  glows are generated from `tools/art/room.py` into `src/scene/geometry.gen.*`,
  and `npm run art:check` fails the build if they drift — see
  [06](06-art-pipeline.md#geometry-comes-from-the-art).
