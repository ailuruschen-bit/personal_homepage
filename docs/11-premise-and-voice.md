# 11 Premise and voice

**Status: proposed. Nothing in this page is implemented.** It settles what the
content _is_; [10 Scroll narrative](10-scroll-narrative.md) settles how the
camera moves through it. Read them together — several decisions here only make
sense alongside that one.

## The premise

The reader is not browsing a profile. They are a detective who has let
themselves into a sleeper carriage while its occupant is away, and they have
until he comes back to work out who he is.

Everything in the carriage is evidence. The ticket on the table, the route map
on the wall, what is open on the laptop, what is in the briefcase. Nothing
introduces itself. The reader picks things up and draws conclusions.

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

**Why the site opens by going through a window.** The existing opening tilts the
blinds, flies out, and comes back in. That animation was written before the
premise and does not need to change; it simply acquires a meaning it did not
have. The way in is the window. That is how the reader got here.

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

## Two layers

Every chapter has the same structure, and it maps onto the read beat in
[10](10-scroll-narrative.md#reading).

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
| `chat`     | _no art yet_       | the one thing the reader acts on — see below   |

`about` is first because it is the thing in front of you when you sit down.
`journey` is a route map, which is already a timeline on a wall, so it carries a
career with no translation needed. The last three cannot become chapters until
they have artwork and therefore an aperture.

### The one interaction

`chat` is the only chapter where the detective does something rather than
observes. They leave their card.

This gives the contact form a reason to exist in the world instead of being a
form bolted to the end of a story, and it is the natural place for links and
anything machine-readable. It is the last chapter.

## The ending

The site currently has no ending; the scroll just stops. The premise supplies
one, and it costs almost nothing to build because it reuses the opening in
reverse.

After the last chapter, he is coming back. The camera retreats to the window and
the window transit plays outward — the same locked segment as the way in, run
the other way. The reader is left outside on the city, where they started.

Two things fall out of that:

- **The footer is diegetic.** It is the view from outside after you have left:
  links, colophon, source. It is a place, not a strip at the bottom of a page.
- **The document is a ring.** The city is at both ends. Scrolling back up
  re-enters the carriage rather than rewinding a page, which is what
  [10](10-scroll-narrative.md)'s axis does anyway.

**Rejected: a timer.** The obvious move is to make his return a deadline. It is
wrong. A reader who is being hurried cannot read, and punishing someone for
reading slowly on a page whose purpose is to be read is self-defeating. The
pressure stays atmospheric and has no mechanics: an announcement over the
tannoy, a shadow in the corridor, the door. Nothing on screen ever counts down,
and nothing is ever lost by stopping.

## What this changes in the content model

`content/sections.ts` currently has `lede` and `blocks`, which assumed one voice
and one column. It needs to carry both layers:

| Field      | Layer      | Shape                                                   |
| ---------- | ---------- | ------------------------------------------------------- |
| `artifact` | artifact   | typed fields printed on the object, not prose           |
| `notes`    | annotation | the long-form blocks that scroll past it                |
| `facts`    | neither    | the machine-readable truth: role, stack, links, contact |

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
3. **Does he actually return at the end, on screen?** Proposed: no. A door
   handle and a cut to the window is stronger than a sprite walking in, and
   drawing a person breaks a scene that has so far only drawn his things.
4. **Does the cover state the premise?** A detective who is told they are a
   detective is being handed the answer. Proposed: one line at most, or nothing,
   and let the empty carriage do it.
5. **Language of first release.** Proposed: write the annotation layer in one
   language, properly, and ship `facts` in all three rather than translating a
   voice badly.

## Keep in sync

- The evidence map here and the chapter order in
  [10](10-scroll-narrative.md#open-questions) and `content/sections.ts`.
- The three-field content model here and the `SectionDef` interface.
- The ending described here and the final segment of
  [10](10-scroll-narrative.md#the-axis).
