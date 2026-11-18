# 13 Art review

**Status: review and plan. Nothing here is implemented.** A strict critique of
the artwork as it renders today, held to the standard of a finished piece
rather than a prototype, and a numbered list of fixes to work through one at a
time.

Reviewed from the built assets in `public/assets/` composited as the hub shows
them: `room.webp` with `room-l.webp` and `room-r.webp` either side and the city
behind the window. How those assets are produced is in
[06 Art pipeline](06-art-pipeline.md); every fix below is a change to a script
in `tools/art/`, not to an image.

Each item has an id. Structural items are `S`, lighting `L`, rendering `R`,
objects `O`, new objects `N`. The second half of the page is the
[Workflow](#workflow) that works through them: a foundation stage that
removes the hand-copied geometry first, then seven stages with review gates.
To begin, say **开始 docs/13**.

## Verdict

The scene has a strong palette, a clear focal point and a mood. It does not
have depth. The reason is not a shortage of detail; it is that **the picture is
drawn in three different projections at once**, lit by glows that do not cast
shadows, and rendered with lighting that is smoother than the pixels it lands
on. Adding detail on top of that would make it busier, not better. The
structure has to be fixed first.

## Structure

### S-01 Three projections in one picture

This is the root cause of the flatness and of both things that are wrong at a
glance.

| Element                            | Projection it is drawn in                       |
| ---------------------------------- | ----------------------------------------------- |
| Window wall, rack, ceiling, panels | flat elevation: no depth at all                 |
| Table top, floor tiles             | one-point perspective, converging on the window |
| Seat backs                         | an oblique view, as if turned toward the viewer |
| Seat cushions                      | flat horizontal bands with a frontal edge       |
| Laptop                             | its own isometric, unrelated to the table       |

The eye reads the table and concludes there is a vanishing point near the
middle of the window, then finds that nothing else agrees with it.

**Fix: commit to one-point perspective with the vanishing point at the centre
of the window.** It is the only choice that keeps the window wall face-on,
which the opening needs — the camera flies straight through that window, and
the city behind it is a flat parallax stack. Everything that runs toward the
viewer then converges on one point: table edges, seat cushions, seat backs, the
underside of the rack, the floor, the side walls.

Record the vanishing point and the horizon as constants in `room.py` and derive
every receding edge from them. No edge that recedes should be drawn by eye.

### S-02 The seat backs

What is drawn: a wide quilted panel whose top edge rises toward the middle of
the picture, capped by a pale band, with the quilting diamonds unforeshortened.
A backrest on a bench that faces across the compartment is nearly edge-on from
here. Drawn wide and frontal it reads as a partition wall, and the top edge
slopes against the table's perspective.

Problems, specifically:

- The top edge slopes the wrong way for the vanishing point in S-01.
- The quilting is drawn flat-on; it should compress toward the window.
- The backrest has no thickness, no top roll, no headrest form.
- There is no seam, gap or shadow where the back meets the cushion.
- The pale cap has a ragged red upper edge that reads as an artefact.

**Fix:** redraw each backrest as a slab in perspective: a visible inner face
narrowing toward the window, a rounded top roll catching the ceiling light, a
dark crease where it meets the cushion, quilting rows that converge. Replace
the pale band with a headrest cover that wraps the top roll and has a hem.

### S-03 The walls either side of the seats

In the side extensions the seat back runs into a pale block and a dark red
block that are flat rectangles with no stated relationship to the seat, the
wall or the floor. They can be read as the back of the next bay's seat, as a
partition, or as a cupboard, and the picture does not say which.

**Fix:** decide what they are and draw that. Proposed: the compartment's side
walls, receding toward the window wall in the same perspective, with the seat
backs standing against them. The coat hooks, the mesh pockets and the fire
extinguisher then sit on a surface that has an angle, and each gets a cast
shadow that states it.

### S-04 The seat cushions

Three flat bands of red with a row of studs. No front roll, no sag, no
foreshortening, and the front edge is a straight frontal line although the
bench runs toward the viewer.

**Fix:** a trapezoid converging on the vanishing point, a rounded front roll
with a highlight along it, piping, a shallow dip where someone sits, and a
shadow under the overhang onto the seat base.

### S-05 The luggage rack is a line

Luggage sits on a single horizontal stroke. From seated eye height the
underside of a rack is the most visible part of it.

**Fix:** draw the rack as a shelf seen from below — a front rail, slats or mesh
receding to the wall, brackets with depth — with the luggage overhanging the
rail and casting shadow down the wall behind.

### S-06 The ceiling

A flat band with a light strip running the full width, drawn in elevation. In
perspective the ceiling is a plane coming toward the viewer and the fixture is
on it.

**Fix:** a short receding ceiling plane with a cove where it meets the wall,
the light fixture drawn with a housing and a diffuser, and vents that sit on
the plane rather than on the wall.

### S-07 The table does not meet the wall

The far edge of the table stops against the wainscot with no bracket, no gap
and no contact shadow, and the pedestal stands in front of a heater grille with
nothing between them. The table floats.

**Fix:** either mount it to the wall under the sill with a visible bracket and
a contact shadow, or pull it clear and show the gap. Give the top an underside
shadow on the pedestal and a shadow on the floor.

### S-08 No foreground

Everything sits in the middle distance. A picture with depth has something
close to the lens.

**Fix:** add a near layer that overlaps the scene's lower corners — the top
rolls of the nearest seat backs, an armrest, a hanging strap — dark, large and
slightly soft. If it is exported as its own image it can move more than the
room under pointer parallax, which buys depth in motion as well as in the
still. That last part is a change to the scene, not only to the art, and
belongs with [10](10-scroll-narrative.md).

### S-09 Scale

Measured against the laptop, the cup is about half again too large and the
ticket about half its plausible size. The keyboard's keys are several times too
big for the machine. The rack's suitcase is small against the duffel beside it.

**Fix:** pick the laptop as the ruler — a 13 to 14 inch machine — and rescale
the cup, saucer, pen and ticket to it. The ticket has to grow in any case to
carry what [11](11-premise-and-voice.md#the-evidence-map) asks of it.

## Lighting

### L-01 Lights glow but do not cast

The neon tube, the lamp and the ceiling strip each add a soft halo. None of
them throws a shadow. The poster, the panel, the hammer box, the lamp itself
and the luggage sit on their walls with no shadow at all, which is the single
largest reason objects look pasted on.

**Fix:** every object on a wall gets a cast shadow whose direction is set by
its nearest light: away from the neon on the left half, away from the lamp on
the right, downward from the ceiling strip along the rack. Hard near the
object, softer further away.

### L-02 No occlusion

Where two surfaces meet there is no darkening: seat against wall, sill against
wall, rack against wall, table against wainscot, floor against seat base.

**Fix:** an occlusion pass along every inside corner. It is cheap in the
pipeline — a blurred mask of the contact edges multiplied in — and it is what
makes forms sit on each other.

### L-03 Forms have no core shadow or rim

Cylindrical and rounded things — the curtains, the cup, the duffel, the seat
rolls — are lit as flat shapes with a gradient across them. None has a
highlight, a core shadow and a reflected edge in that order.

**Fix:** three-value shading on every rounded form, and a thin rim of the
neon's colour on edges that face it. The rim light is what makes neon scenes
read as lit by neon rather than tinted pink.

### L-04 The lamp lights nothing

The shade glows and the wall below it is barely warmer. There is no cone, no
pool on the panel beneath, no warm spill onto the right-hand seat.

**Fix:** a warm cone down the wall, a pool on the control panel and the top of
the seat back, and a visible bright interior at the shade's lower rim.

### L-05 Nothing reflects

The window glass, the table top, the floor and the laptop lid are all matte. A
night interior with neon in it is defined by its reflections.

**Fix:** a faint reflection of the room in the window glass, strongest at the
edges; the laptop screen's light on the table in front of it; a streak of the
neon and of the lamp on the floor; a soft specular along the table's front
edge.

### L-06 Values are compressed

Most of the picture sits in a narrow mid-dark band with a purple cast. The
foreground is not darker than the midground and the wall is not lighter than
the seats, so depth planes do not separate.

**Fix:** assign each depth plane a value range — foreground darkest, table and
seats in the middle, the window wall lighter and cooler — and hold the
brightest values for the window and the three light sources.

## Rendering

### R-01 The picture is soft

Pixel edges are blurred: the poster frame, the panel, the text bars and the
seat's top edge all have a haze around them. Bloom and spill are bleeding into
albedo edges, and it reads as an upscaled image rather than as pixel art.

**Fix:** confine bloom to emitters, keep spill out of edge pixels, and check
the result at 1:1 with nearest-neighbour scaling. Sharpness is most of what
"refined" means in this style.

### R-02 Smooth light on chunky pixels

Lighting is computed as a smooth gradient over art drawn on a coarse grid. The
two resolutions are visible against each other, most of all in the neon's halo
on the wall.

**Fix:** quantise the lighting into a small number of bands, with an ordered
dither between them if needed, so light is made of the same pixels as the
things it falls on.

### R-03 Ragged silhouettes

The laptop's lid and base have torn-looking edges, and the seat's pale cap has
a sawtooth upper edge. These are the upscale reacting to shallow diagonals.

**Fix:** draw shallow diagonals as clean runs of equal length before upscaling,
or draw those edges on the fine layer.

### R-04 Material is the same everywhere

Metal, leather, wood, fabric and plastic differ only in colour. The wall's
panel seams and rivets are good; nothing else has a surface.

**Fix:** one distinguishing mark per material — a sharp specular for metal, a
broad soft sheen for leather, grain and an edge highlight for wood, a
weave or fold shadow for fabric.

## Objects

Large to small. `Redraw` means the form is wrong; `Refine` means the form is
right and the finish is not.

| Id   | Object                     | Verdict | What is wrong                                                                          | What it needs                                                                                                |
| ---- | -------------------------- | ------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| O-01 | Window frame               | Refine  | Good shape; the reveal has no depth and the glass no surface                           | An inner bevel with a lit and a shadowed side, bolts with highlights, glass reflection (L-05), raindrops     |
| O-02 | Sill and the vent under it | Refine  | A thin strip; the plant on it is a few pixels                                          | A sill with thickness and an underside shadow; a plant with a pot and leaves that read                       |
| O-03 | Curtains                   | Redraw  | Read as pipes: thin, straight, three stripes                                           | Gathered fabric with folds of varying width, a tie-back that pinches it, a hem, rings on the rod             |
| O-04 | Seats                      | Redraw  | See S-02, S-04                                                                         |                                                                                                              |
| O-05 | Table                      | Refine  | Good grain; floats (S-07); edge trim is flat                                           | Contact and cast shadows, a metal edge strip with specular, ring marks, wear at the near edge                |
| O-06 | Laptop                     | Redraw  | Own projection, ragged edges, giant keys, blob shadow, screen has no bezel             | Redraw in the table's perspective; bezel, hinge, key rows at scale, screen glow on the keys and table        |
| O-07 | Cup and saucer             | Refine  | Too large (S-09); flat white                                                           | Rescale; a rim highlight, a core shadow, a reflection of the neon, steam that the script already calls for   |
| O-08 | Ticket                     | Redraw  | Too small to carry anything; unreadable                                                | Larger, with a perforated edge, a fold, print rows, and the card behind it showing at one corner             |
| O-09 | Pen                        | Refine  | A dark smear                                                                           | A clip, a highlight, a shadow                                                                                |
| O-10 | Rack luggage               | Redraw  | Sits on a line (S-05); the suitcase is the briefcase and does not look like one        | Overhang and shadow; a briefcase that reads as one, with a handle and clasps, since it is a chapter          |
| O-11 | Line indicator             | Redraw  | A display standing on the rack among the luggage                                       | Mount it on the wall above the window, under the rack, with a housing. It is the decoy map                   |
| O-12 | Rolled paper on the rack   | Redraw  | A small white tube at the far left, easy to miss                                       | This is the journey chapter. Larger, visibly a map, rubber band, an end curling open, leaning or overhanging |
| O-13 | Cardboard box, umbrella    | Refine  | Flat                                                                                   | Tape and a label for the box; a handle and a strap for the umbrella                                          |
| O-14 | Neon tube                  | Refine  | The best thing in the picture; its mounts are blocks and its halo is smooth (R-02)     | End caps, a cable, a bracket; banded halo; rim light on everything facing it (L-03)                          |
| O-15 | Poster                     | Refine  | Good; no shadow, no surface                                                            | Cast shadow, a curl at one corner, tape or pins, a glare streak from the neon                                |
| O-16 | Polaroids by the neon      | Refine  | Two coloured squares                                                                   | A white border with thickness, a tilt, a pin, a shadow                                                       |
| O-17 | Wall lamp                  | Redraw  | The bracket floats above the shade; no arm; lights nothing (L-04)                      | An arm from a wall plate, a shade with pleats and a bright rim, a pull chain that hangs from something       |
| O-18 | Control panel              | Refine  | Reads well; flat                                                                       | A raised housing with a shadow, screws, screen glow onto its own frame                                       |
| O-19 | Hammer box, small frame    | Refine  | Flat stickers on the wall                                                              | Depth, glass glare, shadow                                                                                   |
| O-20 | Wainscot and trim light    | Refine  | Ribbing is even and flat; the teal strip is good                                       | Ribs with a lit and a dark side, scuffs at seat height, the strip's light on the surface under it            |
| O-21 | Heater grille              | Refine  | Even stripes                                                                           | Slats with depth, a frame, a warm glow from inside                                                           |
| O-22 | Floor                      | Redraw  | Very dark, featureless, reflects nothing                                               | Tiles that read, a worn path, reflections of the neon and lamp (L-05), shadow from table and seats           |
| O-23 | Side walls' fittings       | Redraw  | Coat is a flat silhouette; pockets and extinguisher sit on an undefined surface (S-03) | Redraw after S-03, each with form and a cast shadow                                                          |
| O-24 | Wall panels                | Refine  | Seams and rivets are good; every panel is identical                                    | Variation: a scratch, a stain, a replaced panel in a slightly different tone                                 |

### New objects the story needs

From [11](11-premise-and-voice.md#the-evidence-map) and
[12](12-script.md). These do not exist in the picture yet and should be designed
with the redraw rather than added afterwards.

| Id   | Object                 | Notes                                                                                                 |
| ---- | ---------------------- | ----------------------------------------------------------------------------------------------------- |
| N-01 | Business card          | Behind the ticket, one corner showing. Part of O-08                                                   |
| N-02 | Books in the briefcase | Only seen when it opens; the open state is its own drawing                                            |
| N-03 | The door               | Behind the camera in this view. The confrontation needs a second picture, not an addition to this one |
| N-04 | Notebook, hobby object | No design yet; reserve table space for them                                                           |

Each chapter object also needs its **open state** drawn — the ticket's two
faces, the map unrolled, the briefcase open, the screen at reading size. None
of those exist. They are separate drawings and are the larger part of the art
still to do.

## Workflow

Everything from here down is the procedure. It is written so that the work can
start from a single instruction and resume from the same one after any break.

### Starting and resuming

To start:

> 开始 docs/13

To resume after a break, the same phrase works: the
[Progress](#progress) table at the bottom of this page records the last
finished step, and work continues from the next one. To jump, name the id:

> 继续 docs/13，从 S-02 开始

On either instruction the first thing that happens is [Preflight](#preflight).
Nothing is drawn until it passes.

### Preflight

1. **Pull.** Bring the working copy to the tip of `origin/main`, then create or
   check out the branch `art/redraw`. All art work happens there; `main` keeps
   the current picture until a stage is accepted.
2. **Choose the mode.**
   - **Mode A — on your Mac, live.** Used when this conversation is linked to
     the Mac and its shell can run Python with `numpy` and `Pillow` (installed
     into the shell's environment if missing). Edits and art builds happen
     directly in the project folder, and the `npm run dev` you already have
     running serves the new assets on refresh. This is the mode for live
     review.
   - **Mode B — remote.** Used otherwise. Work happens in the cloud copy, each
     reviewable step is pushed to `art/redraw`, and review is `git pull` then
     refresh.
3. **Check the toolchain.** `tsc --noEmit` passes and the art scripts build.
   (In Mode A the shell is a Linux environment and cannot run `vite build` —
   the native modules in `node_modules` are for macOS — so the full build is
   checked remotely. Type checking and the art scripts both work.)
4. **Record the baseline**, once, before step 0.1: build every asset and save
   the decoded pixels and preview composites to `.review/baseline/`. Stage 0 is
   judged against it.

### On your side

Keep `npm run dev` running and the page open in **Chrome**, which is the
browser that has broken before. At each gate you will be told what changed and
asked to refresh. If an image looks stale, hard-refresh with `Cmd+Shift+R`.

From step 0.5 onward, adding `?debug=geometry` to the address draws every
outline, snap zone, light, the window rectangle and the camera origin over the
scene. From stage 1 it also draws the perspective guides. Use it at every gate.

### The loop, for every step

1. Change the script, or the code in stage 0.
2. `npm run art` — rebuild every asset and the geometry manifest.
3. `npm run art:check` — the manifest, the hotspots and the asset sizes agree.
4. `tsc --noEmit`.
5. `npm run art:preview` — composites and before/after crops into
   `.review/<id>/`, including the luminance-only view from stage 3.
6. Commit to `art/redraw` as `art(<id>): <what changed>`.
7. If the step ends at a gate, stop and wait. Otherwise carry on and post the
   preview.

A step that fails 3 or 4 is not finished, whatever it looks like.

### Gates

Work stops at each gate until you have looked at it in the browser and said so.
Every gate includes the **Chrome check**, which is the F-001 reproduction:

- [ ] Let the opening run about a second, skip it, and land in the carriage.
      Nothing from the city shows over the carriage.
- [ ] Let it run to the end and return by clicking. Same.
- [ ] Sweep the pointer across every object, then back. No flicker, no wall
      lifted with an object, the light lands on the object.
- [ ] With `?debug=geometry`, every outline sits on its object.
- [ ] A quick look in Safari.

Pass, and the stage is merged to `main` and pushed. Fail, and the step is
reworked; nothing proceeds past a failed gate.

### Commits

One commit per item id, on `art/redraw`, merged to `main` at each accepted
stage. Messages name the id and say what changed. **No AI attribution of any
kind** — no co-author lines, no session links — and the author is the
repository owner's identity.

Because WebP encoders differ between machines, assets built on the Mac and in
the cloud differ in bytes even when the pixels are identical. Comparisons in
this workflow decode the images and compare pixels, never bytes.

## Stage 0 — Foundation

**Changes no pixel.** The point of this stage is that every later stage can
move objects without anything else having to be updated by hand. It removes the
root of the bug class described in
[06](06-art-pipeline.md#this-used-to-be-a-source-of-bugs): geometry written down
twice.

### 0.1 Geometry manifest

`room.py` currently draws each object at coordinates written into the drawing
code, and `hotspots.ts` repeats those coordinates by hand. Move every
interactive object's position into named constants at the top of `room.py`,
draw from those constants, and have `build.py` write them out as
`src/scene/geometry.gen.ts`: for each object its id, bounding box, snap zone
and light, plus the asset sizes. The generated file is committed and carries a
do-not-edit header.

`hotspots.ts` keeps what is not geometry — target, object name, and later the
lines — and takes everything else from the manifest by id.

**Done when** the rebuilt assets are pixel-identical to the baseline and the
hub behaves exactly as before.

### 0.2 Window, camera and glows from the manifest

The window was written down four times: `hole.png`, the `.win` rectangle in
`scene.css` (150, 124, 180 × 140 in scene units), `transform-origin: 50%
43.71%` on `.cam`, and `CAM_ORIGIN_Y` in `focus.ts`. The four animated glows
(`.g-lamp`, `.g-neon`, `.g-lap`, `.g-out`) were placed by hand over the
artwork as well, and `.g-lap` would have stayed behind the moment the laptop
moved.

`room.py` now owns all of it: `WINDOW`, `CAM_GAP` (the gap in the blinds,
relative to the window) and `GLOWS` (the laptop's and the window's relative to
their objects). The hole is drawn from `WINDOW` — one unit inside it, which is
exactly what `hole.png` held — and `hole.png` is gone. The build writes
`src/scene/geometry.gen.css` with the position rules for `.win`, `.cam`'s
origin and the glows, and `CAMERA` into the manifest for `focus.ts`.
`scene.css` keeps only appearance.

**Done when** the assets are pixel-identical to the baseline and the opening,
the skip and the return look the same frame for frame.

### 0.3 Objects as sprites

Each focusable object is rendered a second time, alone, to
`public/assets/obj-<id>.webp`, with its own alpha. The pop uses that image
instead of a copy of `room.webp` clipped by a polygon, so its edge is the edge
of the drawing and cannot pick up the wall. The `shape` polygons and
`popStyle()` go away; hit testing already uses the snap zone.

The compositing rules from F-001 hold: a sprite at rest is an ordinary
painted element, not a layer of its own; `will-change` appears only while it
animates; its `z-index` stays pinned. **Check in Chrome DevTools' Layers panel
that the layer count at rest is the same as before.**

This is also the shape [10](10-scroll-narrative.md) needs: an object that can
be carried has to exist apart from the room.

**Done when** the room is pixel-identical, the focused objects look the same or
cleaner at the edges, and the Layers count has not changed.

### 0.4 Check

`tools/art/check.mjs`, run as `npm run art:check`, at the end of `npm run art`,
and as the first step of `npm run build`: every manifest id has exactly one
hotspot and every hotspot an id; every sprite exists and covers its box; the
room, side and city assets have the sizes `scene.css` lays them out at, `--tile`
included; the window sits inside the scene. A mismatch fails with a message
that names the file to fix.

It is written for Node with no dependencies rather than in Python, because
`npm run build` has to work on any machine that builds the site, and those are
not guaranteed to have Python and Pillow.

### 0.5 Debug overlay

`?debug=geometry` loads a small module — imported only when the flag is
present, so the normal bundle does not grow — that draws the manifest over the
scene: zones, lights, sprite boxes, the window rectangle, the camera origin.
From stage 1 it adds the vanishing point and horizon.

### 0.6 Preview

`tools/art/preview.py`, run as `npm run art:preview -- [label]`, reads the built
assets and the generated geometry and writes to `.review/<label>/` (the label
defaults to the current commit):

- `hub.png` — the carriage composited as the page lays it out;
- `hub-debug.png` — the same with the geometry drawn over it;
- `luma.png` — luminance only, for judging values in stage 3;
- `objects.png` — every sprite at 3× on magenta, so stray pixels show;
- `crops/` — the seats, the table, the rack, both walls and the window at 3×;
- `compare-*.png` — the baseline on the left and now on the right, for the hub
  and every crop. `--against DIR` compares with another asset folder.

It takes about a second, so it runs after every step.

Scripts added to `package.json`: `art` (build, then check), `art:check`,
`art:preview`.

### 0.7 Chrome smoke test — optional

A Playwright script that performs the F-001 reproduction in Chrome and saves a
screenshot after each step. Headless Chrome does not composite exactly as a
desktop window does, so it cannot prove the bug absent; it can catch the
obvious return of it between gates. Decide at the stage 0 gate whether it is
worth the setup.

### Stage 0 gate

The full Chrome check, plus: the scene is indistinguishable from `main`. Merge.

## Stage 1 — Perspective

The structural redraw. **Constraint for the whole stage: the window rectangle
does not move.** The opening, the city layers and the camera origin all hang
on it, and keeping it fixed removes the largest risk in the redraw.

| Step | Ids        | What                                                                                               | Gate |
| ---- | ---------- | -------------------------------------------------------------------------------------------------- | ---- |
| 1.0  | S-01       | Vanishing point at the window centre and the horizon, as manifest constants; guides in the overlay |      |
| 1.1  | S-01       | Block-in: the whole room in flat colour in the new projection, no detail                           | yes  |
| 1.2  | S-02, S-04 | Seat backs and cushions as slabs in perspective                                                    | yes  |
| 1.3  | S-03       | Side walls, receding, with the side fittings placed on them                                        |      |
| 1.4  | S-05       | Luggage rack seen from below                                                                       |      |
| 1.5  | S-06       | Ceiling plane and fixture                                                                          |      |
| 1.6  | S-07       | Table meets the wall; contact shadows                                                              | yes  |

The side walls are the partitions of a sleeper compartment, and 1.1 already
gives each one its folded upper berth with straps, plus a reading lamp or a net
pocket in the strip below it: blank planes did not read as a train. 1.3 finishes
those fittings.

After 1.1 the picture will look worse than `main`. That is the block-in doing
its job; the gate is about whether the space is right, not whether it is
finished.

## Stage 2 — Scale and placement

| Step | Ids              | What                                                                     | Gate |
| ---- | ---------------- | ------------------------------------------------------------------------ | ---- |
| 2.1  | S-09             | Rescale cup, saucer, pen and ticket to the laptop                        |      |
| 2.2  | O-10, O-11, O-12 | Briefcase, line indicator to the wall, rolled map on the rack            |      |
| 2.3  | N-01, N-04       | Card behind the ticket; space reserved for the notebook and hobby object | yes  |

## Stage 3 — Light

| Step | Ids  | What                                                     | Gate |
| ---- | ---- | -------------------------------------------------------- | ---- |
| 3.1  | L-06 | Value plan per depth plane, judged on the luminance view | yes  |
| 3.2  | L-01 | Cast shadows from every wall object                      |      |
| 3.3  | L-02 | Occlusion in every inside corner                         |      |
| 3.4  | L-04 | The lamp lights its surroundings                         |      |
| 3.5  | L-03 | Core shadow and rim light on rounded forms               |      |
| 3.6  | L-05 | Reflections: glass, table, floor, laptop                 | yes  |

## Stage 4 — Rendering

These change `px.py` and therefore every asset, the city included. Each step's
preview covers the whole scene, not only the room.

| Step | Ids  | What                                             | Gate |
| ---- | ---- | ------------------------------------------------ | ---- |
| 4.1  | R-01 | Bloom confined to emitters; pixel edges sharp    |      |
| 4.2  | R-02 | Lighting quantised to bands, with ordered dither |      |
| 4.3  | R-03 | Clean runs on shallow diagonals                  |      |
| 4.4  | R-04 | One distinguishing mark per material             | yes  |

## Stage 5 — Objects

Redraws first, largest first; refines after, in batches. Each redraw is its own
step; refines are grouped by area.

| Step | Ids                                                            | Gate |
| ---- | -------------------------------------------------------------- | ---- |
| 5.1  | O-06 laptop                                                    | yes  |
| 5.2  | O-03 curtains, O-17 lamp                                       |      |
| 5.3  | O-08 ticket, O-22 floor, O-23 side fittings                    | yes  |
| 5.4  | Refines, window wall: O-01, O-02, O-14, O-15, O-16, O-18, O-19 |      |
| 5.5  | Refines, table: O-05, O-07, O-09                               |      |
| 5.6  | Refines, lower room: O-13, O-20, O-21, O-24                    | yes  |

## Stage 6 — Foreground

S-08, drawn **into `room.webp`** first, as part of the static picture. Making it
a separate layer that moves under parallax is a scene change with exactly the
compositing risk recorded in F-001, so it is a separate decision taken after
this stage, with its own Chrome check.

Gate: the full Chrome check.

## Stage 7 — Open states and the door

The ticket's two faces, the map unrolled, the briefcase open with its books,
the screen at reading size, and the door. These are new drawings for
[10](10-scroll-narrative.md) and [12](12-script.md), and their apertures go
into the manifest. They are drawn here and wired up when the scroll narrative
is built.

## Deferred

Things set aside on purpose, to come back to after the artwork is redrawn.
Each needs its own Chrome check before it is adopted.

### D-01 Darkening the scene around a focused object

**Restored** with the side images redrawn as a foreground (D-01a), using the
door frame and curtain variant. What follows is the history.

**Removed for a while.** Until F-003 the page dimmed everything but the focused
object with a radial overlay (`.spot`), which is what made focus read as a
spotlight. Extending that dimming over the side extensions flickered in Chrome
in every variant tried, and the central dimming was taken out with it so that
the room and its sides stay the same tone. Focus is currently the object's
lift, the pointer light and the warm `.beam`, with nothing darkened.

The full record, including the six variants that failed, is F-002 and F-003 in
[09 Fix log](09-fix-log.md). What is known:

- Overlays wider than the scene, gradients painted inside the side extensions,
  flat opacity strips beside the scene and live `brightness()` filters on the
  side artwork all flickered or cost pointer latency in Chrome.
- Fading the central dimmer out toward its edges avoided the step in tone but
  left a dark halo.

The ways forward are D-01a, which leaves the page alone, and D-01b, which does
not.

### D-01a Bring the dimming back by designing the seam away

**Proposed; nothing here is built.** The original focus lighting was good
everywhere except at one place, and that place is a line, not an effect. So
instead of changing how the page dims, change what the picture has on that
line, and put the original `.spot` back untouched. Everything below is artwork
only, which is the kind of change that has never flickered.

#### What the seam is

`.spot` covers the 480 scene and nothing else, so the dimming stops at the
scene's left and right edges: two vertical lines on screen, at x = 0 and
x = 480, the full height of the picture. The side extensions beyond them are
never dimmed.

Where those lines fall in the room as it is drawn now:

- The corner between the window wall and each side wall is at x = 24 and 456,
  so the seam is 24 units **outside** the corner, on the side wall, 1.8 m from
  the camera.
- Lower down the same line crosses the backrest, the cushion and the base of
  each bench.
- The extensions are only on screen when the viewport is wider than about
  1.43 : 1. A 16:9 window shows roughly 57 units of each; a 4:3 window shows
  none, and has no seam.

One fact decides which ideas can work: **a vertical line on screen is not a
vertical line in the room.** It is the trace of a plane through the camera. A
real edge follows it only if that edge lies in that plane or is close enough to
the camera to be flat-on. So there are two honest ways to hide it: make
something end exactly there, or put something in front of it.

#### The options

**A. The corner on the seam, backrests let into the walls.** _(The idea this
section started from.)_ Widen the compartment so the window wall is exactly the
scene: half-width 240 / 180 = 1.33 m instead of 1.2. The corner then sits on
the seam, and the side walls lie wholly in the extensions. Make the backrests
thin and recessed into the partitions so they go with the walls.

- Solves the seam on the wall completely, from the ceiling down to the top of
  the cushion (y = 359): a change of tone at a corner is what corners do.
- Does not solve it below that. The cushion and the base run toward the camera
  and cross the line for the remaining 120 units; nothing about a bench ends
  there.
- Costs the 24-unit strips of side wall that are in the scene today, which are
  most of the depth a 4:3 window sees.
- Needs a partner for the lower part: C or D below, or a dark blanket and bag on
  each seat where the line crosses.

**B. Look in through the doorway.** The camera is already standing just inside
the door. Put the door frame in the picture: two jambs close to the camera,
their inner edges exactly on the seam. A door 0.9 m wide, 0.68 m from the
camera, projects to x = 0 and 480.

- Solves it completely and at full height: the jamb is a near, flat-on object,
  so its edge is a true vertical on screen, and it is nearly black, so whether
  it is dimmed or not cannot be seen.
- Gives the picture the foreground it lacks (S-08) with no extra layer.
- Fits the story: the detective has just come through this door, and the
  occupant comes back through it.
- **It cannot be narrow.** A jamb is the end of a wall, and the wall goes on
  outward from it. Anything fixed to the side of the room that reaches in as
  far as the seam hides all that lies beyond the seam. So B keeps the side
  walls only where they are already inside the scene, the 24-unit strips, and
  the berths, straps, lamp and net pocket in the extensions go behind it.

**C. Berth curtains, drawn back.** What covers the seam does not have to cover
the wall. It only has to stand **in the room, clear of the wall, and nearer
than whatever crosses the line**; then it is a narrow band, and the side wall
is seen past it on both sides.

A sleeper has exactly that. Each berth has a privacy curtain on a rail along
its open side, above the front of the bench, and when it is drawn back it
gathers at the door end. Put the rail 0.67 m from the centre line and the
gathered curtain 1.0 m from the camera: it projects onto x = 0 and x = 480. A
bundle 5 to 6 cm thick is about 20 units wide on screen, enough to straddle the
line, and it hangs from the ceiling to below the bottom of the picture, in
front of the bench.

- Solves it at full height, by interruption rather than by hiding: the two
  tones are no longer side by side, and a gathered curtain is alternating light
  and dark folds already, so a change of tone across it reads as fabric.
- **Keeps everything.** The side walls, the berths and their fittings stay
  visible outside the curtains on a wide screen, and the 24-unit strips stay
  visible inside them.
- Adds depth for free: the two rails run along the ceiling to the window wall
  and converge on the vanishing point, and the curtains are a foreground.
- Has to be drawn as a real object — folds, a hem, rings on the rail — and not
  as a strip. Too narrow or too flat and the line shows through the idea.
- The curtain is nearer than the benches, so nothing crosses in front of it.
  That is what a post or a pilaster on the side wall cannot offer: the bench
  runs in front of anything fixed to the wall, and the line reappears on the
  bench.

**D. Let the sides fall into shadow.** Put back what the artwork did
originally: the extensions darken steeply toward the edges. The explanation in
the room is that the light is all at the window end — the neon, the lamp, the
ceiling strip by the wall — and the door end is unlit.

- The cheapest: a few lines in `room.py`, already written once.
- Hides the seam only as far as both sides of it are near black. Bright things
  that cross the line, the headrest covers above all, would have to be toned
  down or moved.
- Costs the side walls: on a wide screen they would be shapes in the dark. This
  is how the picture looked before the redraw, and "the walls have disappeared"
  was the complaint that followed when it happened by accident.

**E. A tape frame.** Do not show anything beyond the scene. On a wide window,
pillarbox the hub and use the bars for what
[11](11-premise-and-voice.md#what-carries-it) already wants on screen: the
timecode and the recording badge.

- Removes the seam by removing what is beside it. No artwork needed.
- Costs the full-bleed picture on wide screens, which is where the scene looks
  its best, and the opening is full-bleed, so the bars would have to arrive
  after it.
- A page change rather than an art change, small and static.

#### Decision

**Replace the two side images with a foreground.** `room-l.webp` and
`room-r.webp` stop being a continuation of the room and become something that
stands in front of it: the door frame, a curtain, or both. The seam is then the
boundary between the room's image and the foreground's image, which is exactly
where the dimming stops, so the line needs no further covering: a near, dark
object beside a lit room is expected to differ in tone from it.

This is option B in its plainest form, with C's curtain available as what the
foreground is made of. It is chosen over the narrow curtain inside the room
because it changes nothing inside the scene: no new geometry, no object placed
to the unit, two images redrawn.

What it means:

- The room inside the scene is untouched, including the 24-unit strips of side
  wall next to the corners. Those are the side-wall detail that stays.
- The side walls drawn in the extensions go: the folded berths, straps,
  reading lamp and net pocket. Step 1.3 shrinks to finishing the strips that
  are inside the scene.
- The foreground's inner edge is a straight vertical at the image boundary. A
  door jamb has such an edge. A curtain does not, so a curtain needs either a
  jamb or a track post at its inner edge, or a hem that hangs straight there.
- Keep it dark and low in contrast. It is never dimmed, so the darker it is,
  the less its tone can disagree with the dimmed room beside it.
- It is the foreground stage 6 asks for (S-08), still inside the room's own
  layer, so it does not move against the room. Moving it separately stays
  deferred as D-03.
- On a 4:3 window the extensions are off screen, so nothing changes there.

What the foreground is — door frame, curtain, or a frame with a curtain
gathered against it — is still to be chosen. A frame with a curtain is the
fullest: the frame gives the straight edge and the story's door, the curtain
gives colour and folds.

A, the corner moved onto the seam, is not needed for this and stays open as a
question about the compartment's width.

#### When

Before step 1.3, since it removes most of what 1.3 would have drawn.

#### What to do, in order

1. Restore `.spot` exactly as it was before F-003, and nothing else that F-003
   removed. Check Chrome first with the artwork unchanged: the seam will show,
   but there should be no flicker. If there is, stop — the premise of this
   section is wrong.
2. Draw the foreground in `room.py` in place of what the side extensions hold
   now. The two images keep their size and position, so nothing on the page
   changes.
3. Check at 16:9 and wider, focusing each object in turn, the window most of
   all: its light is the largest and leaves the least dimming at the edges.
4. Record the outcome in [09](09-fix-log.md) either way.

### D-01b Dimming from the page instead

The alternative to D-01a: change the mechanism rather than the picture. Neither
of these has been tried, and both are page changes that need the full Chrome
check.

1. **A dimming that follows the room.** Have `room.py` render a dark overlay
   whose shape is the architecture: full strength over the window wall right up
   to its corners, where a change of tone is natural, and fading out along the
   benches and the floor well before they reach the scene's edge. The earlier
   attempt to fade the dimmer at its edges left a halo because it faded across
   the wall, a continuous surface; this fades only along surfaces that run
   toward the camera. One static image, one opacity.
2. **One image for the whole width.** If the room and its side extensions were
   a single 720-wide element, an overlay the size of that element would not be
   "wider than the scene". This changes the scene's structure and so belongs
   with the scroll narrative work in [10](10-scroll-narrative.md).

### D-02 The periodic glint on focusable objects

**Removed in F-003.** The `.pop` filter animation that made objects glint every
few seconds caused a flash when an early skip landed in the hub. It was the
hint that an object can be picked up. If that hint is missed, bake a small
highlight into each sprite or animate opacity on a separate, tiny element
rather than filtering the sprite.

### D-03 A separate foreground layer

Stage 6 draws the foreground into `room.webp`. Making it its own layer for
parallax is deferred for the same reason as D-01: it is a new moving layer
over the carriage.

## Rollback

Every step is one commit on `art/redraw`, and `main` only moves at a gate, so:

- a step that looks wrong is reverted on the branch and redone;
- a stage that fails its gate is not merged, and `main` still has the last good
  picture;
- if something breaks after a merge, reverting the merge commit restores the
  previous stage exactly.

## Progress

Updated in the same commit as each step. `review` means built and waiting
for the Chrome check; `partial` means started ahead of its turn while fixing
something else.

| Stage | Step | Status  | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----- | ---- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0     | 0.1  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0     | 0.2  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0     | 0.3  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0     | 0.4  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0     | 0.5  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0     | 0.6  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 0     | 0.7  | skipped | decided against at the stage 0 gate                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 1     | 1.0  | done    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 1     | 1.1  | done    | block-in, plus side walls as sleeper partitions and their baked vignette                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 1     | 1.2  | done    | benches as swept cross-sections with soft edges                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 1     | 1.3  | done    | side-wall fittings in the strips the scene shows: reading lamp with a lit hood, net pocket with a timetable; the rest of each side wall is behind the foreground                                                                                                                                                                                                                                                                                                                                                               |
| 1     | 1.4  | done    | two racks, luggage standing on them with sides; the briefcase lifts whole behind the rail                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 1     | 1.5  | done    | ceiling cove at the wall, vents within the strip of ceiling in view, light on the ceiling                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 1     | 1.6  | done    | the table hinged to the wall: struts under it to plates on the wall, and the wall under it in shadow                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 2     | 2.1  | done    | cup and saucer drawn at 0.62 about the saucer's foot; pen lengthened to about 14 cm; steam and cursor positions generated                                                                                                                                                                                                                                                                                                                                                                                                      |
| 2     | 2.2  | done    | journey is a map along the back of the table, mostly rolled into a tube with a rubber band, the open strip askew, creased, a coffee ring, its near corner curling up; the cup stays where it was, in front of it, and is cut out of the map's sprite; the pen moves to the left of the laptop; the line display is a decoy with no hotspot; the rack keeps its box                                                                                                                                                             |
| 2     | 2.3  | done    | business card behind the ticket, peeking out on the table side; ticket moved in from the edge; reserved: notebook at the table's front-left corner, hobby object in place of the holdall                                                                                                                                                                                                                                                                                                                                       |
| 3     | 3.1  | done    | value plan as a grade on the render (`VALUE_PLAN` in `room.py`): the window wall lifted 16% and cooled, fading out below the table; benches down 14%; headrest covers darker; the foreground was already darkest                                                                                                                                                                                                                                                                                                               |
| 3     | 3.2  | done    | `cast()` in `room.py`: each wall fitting's outline slid away from its nearest light, dark against the object and fading; the poster and photos away from the neon, the panel, hammer box and frame away from the lamp, a band under each rack from the ceiling strip                                                                                                                                                                                                                                                           |
| 3     | 3.3  | done    | `occlusion()` in `room.py`: soft dark lines along the creases, written in compartment coordinates: the window wall's floor, ceiling and corners, the side walls' ceiling edge, each bench's end against the window wall, its base on the floor and its backrest against the side wall, and the table's back edge; creases behind a bench do not show through it                                                                                                                                                                |
| 3     | 3.4  | done    | the shade's open bottom glows; a cone of saturated warm light down the wall from it (`light_poly`), brightest near the shade, a pool on the panel and on the top of the right-hand backrest by the wall                                                                                                                                                                                                                                                                                                                        |
| 3     | 3.5  | done    | window curtains as two round folds each, reflected edge, core shadow, half-tone, highlight, lit from their own light's side; `rim()` in `room.py` lays a thin edge of a light's colour on the side facing it (neon magenta, lamp warm) on the benches, curtains, luggage and cup; earlier in the stage the tube's sockets and the lamp's mount were given depth                                                                                                                                                                |
| 3     | 3.6  | done    | `reflections()` in `room.py`: the laptop screen's blue on the table in front of it, the lamp's sheen at the back right, a specular along the brass front edge, on the table only; a faint edge tint on the glass (`.glass` in scene.css) was tried and dropped: the return from outside stuttered in Chrome with it, and it made little difference (F-004 in 09); the floor's reflections would fall below the frame and were left out; along the way the laptop's base got its thickness and the cup moved forward of the map |
| 4     | 4.1  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 4     | 4.2  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 4     | 4.3  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 4     | 4.4  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 5     | 5.1  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 5     | 5.2  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 5     | 5.3  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 5     | 5.4  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 5     | 5.5  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 5     | 5.6  | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 6     | 6    | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 7     | 7    | pending |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

### Where things stand

Stage 0 is merged to `main`. Stage 1 was merged to `main` as a stable point
after the side foreground was settled, ahead of its own gate after 1.6; the rest
of stage 1 continues on `art/redraw` and merges at that gate as planned.

Done so far in stage 1, beyond what the step table names:

- The compartment is a model in metres (`P()` in `room.py`); every receding
  surface is projected from it.
- The side walls carry folded upper berths, and the side extensions have the
  page's vignette baked into the artwork (F-002 in [09](09-fix-log.md)).
- The benches are cross-sections swept along their length, so an edge is
  softened or hardened by moving points in a table.
- There are two luggage racks, 13 cm deep, either side of the line display.
  Luggage stands on them at its own depth, with undersides and inner sides. The
  canvas wrapper's `depth()` scales art written for the window wall to stand
  nearer the camera.
- The side images are a foreground (D-01a): a pilaster in the walls' panelling
  and a curtain in the benches' upholstery, and the central focus dimming is
  back.
- An object that something stands in front of gets a second sprite for the
  thing in front (`front` in the generated geometry). The briefcase lifts whole
  behind the rack's rail this way.

Stage 1 passed its gate and is merged. Stage 2 passed its gate and is merged.
Stage 3 is under way: the value plan (3.1) passed its gate; cast shadows (3.2) passed review, with the tube's sockets and the lamp's mount given depth along the way; occlusion (3.3) passed review; the lamp's light (3.4) passed review; core shadows and rim light (3.5) passed review; reflections (3.6) are done, and stage 3 passed its gate and is merged. Stage 4 is next.

## Keep in sync

- After stage 0, geometry has one source: `room.py`. If a coordinate appears by
  hand anywhere in `src/`, stage 0 is incomplete.
- [06 Art pipeline](06-art-pipeline.md) and
  [08 Maintenance recipes](08-maintenance-recipes.md) describe the hand-synced
  outlines and change with stage 0.
- The objects here and the evidence map in
  [11](11-premise-and-voice.md#the-evidence-map).
- The [Progress](#progress) table and the commits on `art/redraw`.
