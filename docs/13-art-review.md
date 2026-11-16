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
objects `O`. Work them in the order given in [Order of work](#order-of-work),
because most object fixes are wasted if the structure under them moves.

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

## Order of work

The order matters more than the list. Each stage invalidates the hotspots'
outlines, so [06](06-art-pipeline.md#keeping-the-outlines-in-sync) applies at
every step.

1. **Perspective.** S-01, then S-02, S-03, S-04, S-05, S-06, S-07. Block the
   whole room in flat colour in the new projection before finishing anything.
2. **Scale and placement.** S-09, O-10, O-11, O-12, and reserve space for the
   new objects.
3. **Light.** L-06 first, to set the value plan, then L-01, L-02, L-04, L-03,
   L-05.
4. **Rendering.** R-01, R-02, R-03, R-04. These are pipeline changes in
   `px.py` and touch every asset, the city included.
5. **Objects.** Redraws before refines, large before small.
6. **Foreground.** S-08, last, because it is framed against everything else.
7. **Open states and the door.** After the room is final.

After stage 1 the picture will look worse than it does now. That is expected:
it will be correct and unfinished instead of finished and wrong.

## Keep in sync

- Every outline in `hotspots.ts` against `room.py`, after each stage.
- The vanishing point in `room.py` and `CAM_ORIGIN_Y` in `focus.ts`: the camera
  already zooms about the gap in the blinds, and the perspective should
  converge where the camera pushes.
- The objects here and the evidence map in
  [11](11-premise-and-voice.md#the-evidence-map).
