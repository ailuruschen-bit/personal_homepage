# 11 Premise and voice

**Status: proposed. Nothing in this page is implemented.** It settles what the
content _is_; [10 Scroll narrative](10-scroll-narrative.md) settles how the
camera moves through it. Read them together — several decisions here only make
sense alongside that one.

## The premise

The reader is not browsing a profile. They are a detective who has let
themselves into a sleeper carriage while its occupant is away, and they have
until he comes back to work out who he is.

He comes in through the connecting door from the next carriage, because that is
the only way into a compartment on a moving train. Nobody climbs through a
window at speed.

Everything in the carriage is evidence. The ticket on the table, the route map
on the wall, what is open on the laptop, what is in the briefcase. Nothing
introduces itself. The reader picks things up and draws conclusions.

And none of it is happening now. What the reader is watching is the recording
of it, which is the part that makes the rest hold together — see
[The recording](#the-recording).

## What this fixes

The premise is not decoration. It resolves three things that were unanswered.

**Why the carriage is empty.** It was an aesthetic choice with no reason behind
it. Now the absence is the whole setup: he has just stepped out, the coffee is
still warm, the laptop is still open. The scene gains a clock without needing
one on screen.

**Why scrolling opens things.** [10](10-scroll-narrative.md) defines two
transitions — carry and dolly — and justifies them physically: an object you
could pick up gets carried, one that is bolted down gets approached. Under the
premise those stop being transitions and become actions. Carry is _you pick it
up_. Dolly is _you lean in_. The interaction grammar now means something in the
world, which is the difference between a motion design and a scene.

**Why the site opens by going out of a window.** The existing opening tilts the
blinds, flies out to the city, and comes back in. That animation was written
before the premise, does not need to change, and acquires a meaning it did not
have: he has just let himself in, and the first thing he does is look out to
see where the train is. The transit is a glance, not an entrance. Treating it
as an entrance was the earlier reading, and it was wrong — on a moving train
there is no way in but the door.

## What it costs

Stated plainly, because these are the ways this goes wrong.

**A recruiter has thirty seconds.** This is a personal site with a job to do.
A conceit that makes facts oblique works against that job, and charm does not
survive a reader who could not find out what you do. The rule that follows is
absolute:

> **The fiction is never the only path to a fact.**

Every hard fact — name, role, stack, where you are, how to reach you — is
readable in the artifact layer below without parsing any fiction, is present in
the flat no-JavaScript document, and is reachable by deep link. The detective
voice is the second layer, never the carrier.

**It doubles the writing, and bad writing is worse than none.** A profile that
is merely plain is fine. A detective story that is merely competent is
embarrassing. If the annotation layer cannot be written well, the artifact layer
alone still stands up as a site — so build it in that order and let the voice
arrive when it is good.

**UI chrome stays out of the fiction.** Buttons say what they do. Navigation,
labels, the skip control, error states and form fields are literal. The fiction
lives in content, artwork and copy. The failure mode this avoids is the clever
portfolio nobody can navigate.

**Tone: invited, not voyeuristic.** The door was left unlocked. The register is
a character study with a wry narrator, not surveillance. If a line would read as
intrusive about a real person, it is the wrong line.

**Three languages.** Internationalisation is already on the roadmap, and a voice
is the hardest thing to carry across languages. A pastiche that lands in Chinese
may be flat in English and stilted in Japanese. Either the voice gets written
natively in each language or the annotation layer ships in one and the artifact
layer in all three.

## The recording

The reader can scroll back. That is not a concession to usability, it is a fact
about the medium that the fiction has to account for, because a break-in does
not have an undo. The answer is that **the intrusion is not happening now. It
is footage, and the reader is reviewing it.**

### Recording rather than memory

Both would rationalise rewinding. Footage wins on everything else.

It is literal: scrubbing back and forth is what footage is for, and pausing is
something you do to a tape. It gives the site a set of diegetic interface
elements that are cheap, always visible, and would otherwise have had to be
invented as ordinary chrome. And it retroactively justifies a decision already
taken — the film grain added to the artwork stops being a style and becomes the
reason you can see it.

Memory would excuse a selective, moving, subjective camera more gracefully, and
that is a real argument. But its signifiers are vague — vignettes, desaturation,
soft edges — where a tape's are concrete and legible at a glance.

### Who is watching

The detective, afterwards, writing it up.

This is what sorts the three layers into two time frames, and it is the reason
the voices do not collide:

| Layer      | When       | Voice                                    |
| ---------- | ---------- | ---------------------------------------- |
| artifact   | then       | none — it is a document                  |
| spoken     | then       | in the moment, present tense, short      |
| annotation | now, after | the report, reflective, knows the ending |

So the spoken lines can be unsure and the annotation can be certain, without
either being out of character. That is a free gift from the framing and worth
more than the atmosphere.

### What carries it

| Element    | Doing double duty as                        |
| ---------- | ------------------------------------------- |
| timecode   | the scroll progress indicator               |
| play state | a reminder that this already happened       |
| grain      | already in the artwork; now it has a reason |
| subtitle   | a transcript rather than a caption          |

The timecode is the one worth building first. A progress bar would have been
needed anyway for a document this tall, and a timecode is the same information
wearing the premise. Map `s` onto elapsed minutes and it reads as a tape
position.

**Rejected: deliberate glitches.** Dropped frames, tearing and scanline judder
at the seams are the obvious additions and they are a bad idea here. This
project spent seven attempts removing an accidental compositing artefact in
Chrome — see
[09](09-fix-log.md#f-001-chrome-the-city-drawn-over-the-carriage) — and
deliberately adding artefacts that look like it would make every future bug
report ambiguous. Grain and a timecode carry the idea. Nothing else should
pretend to be broken.

### Where playback ends

At the confrontation. He opens the door, and the tape chrome goes: the timecode
stops, the indicator goes out, the subtitle sheds its transcript styling.
Playback has caught up with the present and the conversation is live.

It costs a few elements fading out and it is the strongest beat in the site.
Everything the reader has seen so far was over before they arrived; this is the
one thing that is not.

## Two layers

Every chapter has the same structure, and it maps onto the read beat in
[10](10-scroll-narrative.md#reading). A third layer, the spoken one, sits over
both and runs across the whole site rather than per chapter; it has
[its own section](#the-spoken-layer) below.

**The artifact layer** is what is actually printed on the thing. Short, dense,
scannable, factual. It fills the frame when the aperture opens and it stays
there for the whole chapter — the object never leaves the screen.

**The annotation layer** is what the detective makes of it. This is the
long-form, and it is what scrolls during the read beat, moving past the artifact
rather than replacing it.

```
   ┌─────────────────────────┐
   │   artifact — fixed      │   the ticket, the screen, the map
   │                         │
   │   ┌─────────────────┐   │
   │   │ annotation      │ ▲ │   scrolls during the read beat
   │   │ — scrolls       │ │ │
   │   └─────────────────┘   │
   └─────────────────────────┘
```

Keeping the artifact fixed while the notes move is what stops a chapter from
feeling like a page that has been navigated to. The reader is still standing in
the carriage holding the thing.

### Voice

The artifact layer has no voice. It is a document; it reads like one. A ticket
has a name, an origin, a destination and a date, set in whatever face a ticket
is set in.

The annotation layer is the detective's notebook: second person or bare
observation, present tense, short sentences, no adjectives doing work that a
detail could do. It states what is in front of it and lets the reader draw the
conclusion. It never explains the joke.

Illustrative only — not copy, and inventing no facts:

> A boarding pass, folded twice. [ORIGIN] to [DESTINATION]. The date is four
> years old and he has kept it where he can see it.

Compare the same fact in first person — "I moved from [ORIGIN] to [DESTINATION]
four years ago and it mattered to me" — and the reason for the device becomes
clear. The premise buys a way to say things about yourself that are unsayable
in your own voice. That is the actual payoff, more than the atmosphere.

## The spoken layer

Over the top of both content layers, the detective talks.

The cover does not greet anyone. A greeting assumes the occupant is there to
give it, and he is not. What stands in its place is the first line of the
character the reader is playing, spoken on the city before going in:

> 景色不错，但是该干正事了。

That line does three jobs at once. It establishes the voice, it casts the
reader, and it is the scroll affordance — it says _get to work_, which is the
instruction. Keep an unobtrusive scroll indicator anyway; a line of dialogue is
not an accessible affordance on its own.

It also takes the cover's old job away, so the identity has to live somewhere
else: the document's `h1` is the occupant's name and role, visually hidden
behind the scene but present for assistive technology, for search, and in the
flat document. What is _drawn_ is the detective's line. What is _read_ by
anything that does not render the scene is still a name.

### Anchored and reactive

Principle 1 in [10](10-scroll-narrative.md#principles) says scroll is a
position and not an event, which looks like it forbids a line that fires. It
does not. It sorts lines into two kinds and keeps them on separate channels.

**Anchored lines** are tied to a scroll range, and their opacity is a function
of `s` like everything else: in over a short range, held over a long one, out
again. Scroll back and the line is there again, because it never happened — it
is simply true at that offset.

This is better than the timed version, not a compromise. **A line on a timer
can vanish while you are still reading it.** An anchored line cannot: stop, and
it stays as long as you like. In a design whose whole point is that you may
stop anywhere, a timed subtitle would be the single element that refuses to.

**Reactive lines** answer something that is not scroll: pointing at an object
at the hub, returning to one already examined, going idle. These are genuinely
events, and they are allowed — because they live on the pointer channel, which
is event-driven today, and never on the scroll channel. The rule that holds the
architecture together: **nothing on the scroll axis is ever an event, and the
spoken layer gets no exception.**

The cost of anchored lines is that they replay on a second pass. That is
accepted. The alternative is remembering what has been seen, which is state,
and state is what makes a scroll position stop being enough to draw a frame.

### One slot

All of it renders in a single fixed subtitle at the bottom of the frame. One
voice, one place, never moving.

Speech bubbles pinned to objects were considered and are wrong here. They pull
the eye away from the thing the camera has just framed, in a design whose whole
premise is that the camera decides what you look at. A subtitle is also the
convention of the two games the art is modelled on.

The focus caption that exists today — the object name under the section name —
is the same slot. Two text layers competing for the bottom of the frame is one
too many.

### Budget

Restraint is the whole difference between a character and a chat box. One line
as a chapter opens, sometimes one as it closes, and a handful of reactive lines
at the hub: on the order of twelve to fifteen for a first pass, not fifty. A
quip on everything every time is noise, and noise is what teaches people to
scroll past text.

Write in this order, because each is useless without the one before it:
`facts`, the artifact layer, anchored lines, annotation, reactive lines, the
confrontation.

## The evidence map

Chapter order is the order a detective would find things in, which is also the
order [10](10-scroll-narrative.md#open-questions) proposes on interaction
grounds. The two agree, which is a good sign.

| Chapter    | Object             | As evidence                                    |
| ---------- | ------------------ | ---------------------------------------------- |
| `about`    | 车票 on the table  | ticket or pass: who he is, where he came from  |
| `journey`  | 线路图 on the wall | the line with stops marked: where he has been  |
| `stack`    | 公文包 on the rack | what he carries: the tools of the trade        |
| `projects` | 电脑 on the table  | what is still open on the screen: current work |
| `notes`    | _no art yet_       | loose papers, a notebook                       |
| `hobby`    | _no art yet_       | something personal left out, not work          |
| `chat`     | 门 — _no art yet_  | the doorway, and the man in it — see below     |

`about` is first because it is the thing in front of you when you sit down.
`journey` is a route map, which is already a timeline on a wall, so it carries a
career with no translation needed. The last three cannot become chapters until
they have artwork and therefore an aperture.

### The confrontation

`chat` is the only chapter where the reader is not alone.

He comes back. He was not supposed to, and the detective is standing in the
middle of his carriage holding his things. The conversation that follows is the
chat section — not a widget bolted to the end of a story, but the scene the
story has been walking towards.

The aperture is the doorway: a lit rectangle with him in it. It needs no new
primitive, and it is the one aperture that opens onto a person rather than a
surface.

What the frame buys:

- **The bot has a reason and a persona.** Not "ask me about my CV" — him,
  wanting to know who you are and what you have been reading, and answering
  what you ask back. A personal-site chatbot is roleplaying its owner anyway;
  this makes that honest instead of a gimmick.
- **He never has to be drawn.** A silhouette, backlit from the corridor. This
  answers the question the premise had left open — a scene that has only ever
  drawn a man's possessions should not suddenly draw the man — and a backlit
  figure in a doorway is exactly the register of the art it is modelled on.
- **The exit stays open.** He fills one doorway; a carriage has two, and the
  far end is open the whole time. The reader can leave at any point in the
  conversation. That is what makes staying a choice instead of a toll. (The
  window is not the exit and never was — see
  [the premise](#the-premise).)

Two voices now share the subtitle, so it needs a speaker label. It stays one
slot.

Rules it must obey, all of them downstream of facts-never-behind-fiction:

- **Asked a straight question, it answers straight.** "What has he done with
  X" gets a real answer — in character, but informative. A character who
  deflects is a site that does not work.
- **It gates nothing.** Every fact is already readable before this chapter. If
  the bot is unavailable, the visitor loses a scene, not information.
- **Staying in character is soft.** Anyone who wants the plain version gets it
  without a fight.

## The ending

The site currently has no ending; the scroll just stops. The premise supplies
one, and it costs almost nothing to build because it reuses the opening in
reverse.

The confrontation is the last chapter. However it goes, it ends the same way:
the camera pulls back through the window to the city, which is the frame the
tape opened on. The same locked segment, run outward.

Two things fall out of that:

- **The footer is diegetic.** It is the view from outside after you have left:
  links, colophon, source. A place, not a strip at the bottom of a page.
- **The document is a ring.** The city is at both ends, because a tape ends on
  the frame it began with. Scrolling back up re-enters the carriage rather than
  rewinding a page, which is what [10](10-scroll-narrative.md)'s axis does
  anyway — and under the recording it is simply rewinding.

**Rejected: a timer.** The obvious move is to make his return a deadline. It is
wrong. A reader who is being hurried cannot read, and punishing someone for
reading slowly on a page whose purpose is to be read is self-defeating. His
return is positional, not temporal: it happens because the reader reached the
last chapter, not because they were slow. The pressure stays atmospheric and
has no mechanics — an announcement over the tannoy, a shadow in the corridor,
the door. Nothing counts down, and nothing is ever lost by stopping.

## What this changes in the content model

`content/sections.ts` currently has `lede` and `blocks`, which assumed one voice
and one column. It needs to carry both layers:

| Field      | Layer      | Shape                                                   |
| ---------- | ---------- | ------------------------------------------------------- |
| `artifact` | artifact   | typed fields printed on the object, not prose           |
| `notes`    | annotation | the long-form blocks that scroll past it                |
| `facts`    | neither    | the machine-readable truth: role, stack, links, contact |

`content/site.ts` changes with it. `heroTitle` and `heroLede` assumed a
greeting; the cover now carries the detective's opening line, and the
occupant's name and role move to the hidden `h1` and the metadata.

`facts` is the hedge against the premise. It is what the flat document renders,
what structured data is generated from, and what someone in a hurry sees. If the
artifact and annotation layers were deleted tomorrow, `facts` alone would still
be a working personal site.

See [07 Content and routing](07-content-and-routing.md).

## Open questions

1. **How far into fiction?** Proposed: the hybrid above — artifact carries the
   facts, annotation carries the voice. The two ends of the scale are pure
   artifact (atmospheric, too oblique to be useful) and pure monologue (first
   person in a hat).
2. **Who is the narrator?** The annotation is written by the site's owner about
   a stranger examining him. That doubling is deliberate and is where the device
   earns its keep, but it needs to be consistent: the detective never addresses
   the owner and the owner never breaks in.
3. **How much of him is drawn?** Settled by the confrontation: a silhouette in
   the lit doorway and nothing more. If that ever stops being enough, the thing
   to add is light and the corridor behind him, not a face.
4. **Does the cover state the premise?** A detective who is told they are a
   detective is being handed the answer. Proposed: one line at most, or nothing,
   and let the empty carriage and the timecode do it.
5. **How hard does the tape press?** The timecode and the grain are the floor.
   Above that sit a scrub bar, a play indicator, a transcript-styled subtitle
   and a tape-stock colour cast, in roughly that order of how much they commit.
   Proposed: build the floor, live with it a while, and add upward only if the
   framing is not landing.
6. **Language of first release.** Proposed: write the annotation layer in one
   language, properly, and ship `facts` in all three rather than translating a
   voice badly.

## Keep in sync

- The evidence map here and the chapter order in
  [10](10-scroll-narrative.md#open-questions) and `content/sections.ts`.
- The three-field content model here and the `SectionDef` interface.
- The ending described here and the final segment of
  [10](10-scroll-narrative.md#the-axis).
