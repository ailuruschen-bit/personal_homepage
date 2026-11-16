# 07 Content and routing

> **Planned change.** Routes resolve to scroll offsets in one document rather than to separate views, and this page's section shell becomes the no-JavaScript fallback. See [10 Scroll narrative](10-scroll-narrative.md).

## Routing

`src/router.ts` is 25 lines and deliberately so.

```
#/              the scene
#/about         a section page, keyed by id
#/anything-else falls back to the scene
```

A `Route` is `{ name: 'scene' }` or `{ name: 'section', id }`. `parse()` strips
the leading `#/` and treats anything left as an id; `go()` writes the hash;
`onChange()` subscribes to `hashchange`.

`go()` has one wrinkle: if the requested hash is already current it dispatches
a synthetic `hashchange` rather than doing nothing. That is what makes "back to
the carriage" work from the scene itself — leaving the hub to look outside does
not change the URL, so without it the re-render would be swallowed.

**Hash, not the History API.** The whole point is that `dist/` can be dropped
on any static host with no rewrite rule sending unknown paths to `index.html`.
The cost is the `#` in URLs and no per-section server-rendered metadata, both
of which are acceptable for a personal site.

Unknown ids currently redirect to the scene. A real 404 page is on the to-do
list.

## The section registry

`src/content/sections.ts` is the single list of sections. Each entry:

```ts
{
  id: 'about',      // the #/about part of the URL
  title: '档案',     // shown in the focus caption and as the page title
  lede: '...',      // page lede
  blocks: ['...'],  // placeholder blocks, replaced by real content later
}
```

Seven are registered: `about`, `journey`, `stack`, `projects`, `notes`,
`hobby`, `chat`. Four of them are reachable from the carriage; `notes`, `hobby`
and `chat` have no object drawn yet and are only reachable by URL.

`sectionById` is the lookup used by both the router and the scene's caption.

## How a section connects to the carriage

Two files have to agree:

- `content/sections.ts` defines that the section exists.
- `scene/hotspots.ts` defines an object whose `target` is that id.

Nothing enforces the link. A hotspot pointing at an unknown id will show the
raw id as its caption and navigate to a route that redirects back to the scene.

The one special target is `COVER`, exported from `hotspots.ts`. It is not a
section: selecting the window switches the scene to `peek` rather than
navigating.

## The page shell

`src/sections/layout.ts` renders every section with the same markup: a top bar
with a back button and the id as a kicker, then title, lede and one block per
`blocks` entry.

This is intentionally plain. The scene is the thing that is meant to impress;
the section pages are meant to be read, and use the light half of the token
palette in `styles/tokens.css`.

When a section needs its own treatment, the shape to reach for is a map from id
to render function, falling back to this shell.

### A note on `innerHTML`

Both `layout.ts` and `scene/dom.ts` build markup by string interpolation. That
is safe here because every interpolated value comes from a checked-in source
file, not from user input or a network response. If content ever starts coming
from Markdown files, a URL or an API, this has to be revisited — escape at the
interpolation points or switch to `createElement`.

## Copy

`src/content/site.ts` holds the cover headline, the one-line introduction and
the external links. `heroTitle` is split on `\n` by `scene/dom.ts` into two
lines, so it must contain exactly one newline.

All copy is currently placeholder and marked `TODO`. The strings themselves are
still in Chinese; the code around them is English. Internationalisation is on
the to-do list and would start here — probably by making `site` and `sections`
keyed by locale, with the locale chosen in `main.ts`.
