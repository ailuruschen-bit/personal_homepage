# 11 Premise and voice

**Status: proposed. Nothing in this page is implemented.** It settles what the
content _is_; [10 Scroll narrative](10-scroll-narrative.md) settles how the
camera moves through it, and [12 Script](12-script.md) writes it out scene by
scene.

## The premise

**The reader is the detective.** He has been hired to find out what kind of
person the occupant of a sleeper compartment is — by whom is never said and
does not matter. The occupant has stepped out to take a phone call. The
detective walks down the corridor from the next carriage, lets himself in, and
goes through the man's things.

He records the job, as he records every job, and what the reader is doing is
going back through that recording to write it up. That is the whole structure:
one person, one room, one tape.

## What this fixes

**Why the carriage is empty.** He has just stepped out. The coffee is still
steaming and the laptop is still on. The scene gains a clock without putting
one on screen.

**Why scrolling opens things.** [10](10-scroll-narrative.md) defines carry and
dolly as transitions. Here they are actions: carry is _he picks it up_, dolly
is _he leans in_. The interaction grammar means something in the world.

**Why the opening goes out of the window.** The existing animation tilts the
blinds, flies out to the city and comes back. It does not change. He has just
come in, and the first thing he does is look out. The window is a glance, never
a way in or out — on a moving train the only way in is the door.

**Why the reader can scroll back.** It is a tape, and he is reviewing it. See
[The recording](#the-recording).

**Why the chat exists.** Because he gets caught, and the occupant would rather
answer questions than have his things gone through. See
[The confrontation](#the-confrontation).

## Plausibility audit

Every hole found in the earlier drafts, and what closes it. A fiction that
wants the reader to smile cannot afford one detail that makes them frown.

| Hole                                                    | Fix                                                                                               |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Nobody climbs into a moving train through a window      | He comes down the corridor and through the compartment door                                       |
| The detective had no reason to be there                 | He is on a job. Who hired him is never said                                                       |
| A break-in cannot be rewound                            | It is his own recording, and he is reviewing it                                                   |
| A reader can take an hour; he has a minute              | The timecode is a function of scroll. The tape is under ten minutes however long it is read       |
| A passenger does not scribble on the railway's wall map | The wall map stays as a decoy he dismisses. The journey is a rolled map of his own                |
| A ticket does not say who someone is                    | His business card is tucked behind it. The ticket says where he is going; the card says who he is |
| "Tools of the trade" in a case was an empty metaphor    | It holds books. Worn spines are what he uses, the bookmarked one is what he is learning           |
| An engineer who leaves a laptop unlocked looks careless | Everything open on it is a public repository. The detective is the one who looks foolish          |
| Why is the coffee steaming if he went for coffee        | He went to take a call in the vestibule, which is where calls are taken on a train                |
| Why would a man who has been burgled chat               | Because answering is less trouble than being searched, and he says so                             |
| The tape cannot contain the conversation                | It does not. He stops recording at the door; the chat is off the record                           |

## What it costs

**A recruiter has thirty seconds.** A conceit that makes facts oblique works
against the job this site has. The rule is absolute:

> **The fiction is never the only path to a fact.**

Every hard fact — name, role, stack, where he is, how to reach him — is
readable in the artifact layer without parsing any fiction, is present in the
flat no-JavaScript document, and is reachable by deep link.

**It multiplies the writing, and bad writing is worse than none.** A plain
profile is fine. A merely competent detective story is embarrassing. Build the
artifact layer first; it stands up alone.

**UI chrome stays out of the fiction** unless it is doing double duty. Buttons
say what they do. The timecode is allowed because it is also the progress
indicator.

**Tone: invited, not voyeuristic.** The detective judges the room the way a
guest would, and concedes more than he sneers.

**Three languages.** A voice is the hardest thing to translate. Write the
spoken and annotation layers natively in one language first and ship the facts
in all three.

## The recording

### His own tape

The detective records his jobs and reviews the tape to write the report. A tape
can be scrubbed back, played forward and paused. Scrolling is scrubbing.
Stopping is pausing. Nothing about the interaction has to be excused; it is
what one does with a recording.

Footage rather than memory, because a tape's signifiers are concrete and a
memory's are vague, and because the film grain already in the artwork stops
being a style and becomes a property of the picture.

### Three layers, two time frames

| Layer      | When        | Voice                                      |
| ---------- | ----------- | ------------------------------------------ |
| artifact   | on the tape | none — it is a document                    |
| spoken     | on the tape | what he muttered while working: short, dry |
| annotation | afterwards  | the written report, composed               |

The spoken lines can be unsure and the report can be certain without either
being out of character.

### What carries it

| Element   | Doing double duty as                                           |
| --------- | -------------------------------------------------------------- |
| timecode  | the scroll progress indicator                                  |
| REC badge | the reminder that this is a recording; it goes out at the door |
| ▶▶        | what a click-to-jump looks like: it is fast-forward            |
| grain     | already in the artwork; now it has a reason                    |
| subtitle  | his muttering, transcribed                                     |

The timecode maps scroll offset onto elapsed time, not the reader's clock. The
whole intrusion runs a little under ten minutes however long it is read. That
makes a joke with no words in it: his "one minute" is on screen the whole time,
and by the door it reads `00:09:47`.

**Rejected: deliberate glitches.** Dropped frames and tearing look exactly like
the compositing fault this project spent seven attempts removing — see
[09](09-fix-log.md#f-001-chrome-the-city-drawn-over-the-carriage). Nothing
should pretend to be broken.

### Where the tape ends

At the door. A professional does not keep footage of himself being caught, so
he switches it off: the badge goes out, the timecode freezes, the grain
settles. Everything before that moment was already over. What follows is not
on any tape, which is exactly what a conversation with a chatbot is — it is
happening now, and it is off the record.

## Two layers

Every chapter has the same structure, and it maps onto the read beat in
[10](10-scroll-narrative.md#reading). The spoken layer sits over both and has
[its own section](#the-spoken-layer).

**The artifact layer** is what is actually printed on the thing. Short, dense,
factual. It fills the frame when the aperture opens and stays for the whole
chapter.

**The annotation layer** is the report. It is the long-form, and it scrolls
past the artifact rather than replacing it, so the reader is still looking at
the thing in his hands.

### Voice

The artifact has no voice. A ticket reads like a ticket.

The detective is not a bystander with a good eye. He has done this many times
and finds it routine, and the comedy is the gap between how dramatic breaking
into a stranger's compartment is and how unimpressed he is by it. He is never
excited and never afraid. He is mildly put out, mostly by other people's
carelessness, occasionally by his own.

- **The turn.** A flat observation, then a short sentence that undercuts it.
- **Specificity is the joke.** The line should contain no funny words.
- **Judge the room, not the reader.** The snark lands as a compliment about as
  often as a complaint. By the last chapter he rather likes the man.
- **Mostly straight.** If every line is a quip, none of them is.
- **One sincere line** in the whole site. [12](12-script.md) spends it on the
  laptop.

The device earns its keep in one way above all: it says things about the
occupant that he could not say about himself without sounding as if he wanted
credit.

## The spoken layer

The cover does not greet anyone; the occupant is not there to do it. The first
words on the site are the detective's, and the second of them is the scroll
affordance. Keep a quiet scroll indicator anyway.

The occupant's name and role live in a visually hidden `h1` and the metadata,
so anything that does not render the scene still reads a name.

### Anchored and reactive

**Anchored lines** hang on a scroll range and fade as a function of `s`, like
everything else in [10](10-scroll-narrative.md#principles). They cannot vanish
while being read: stop, and they stay. They replay on a second pass, which is
what footage does.

**Reactive lines** answer the pointer or idling. They live on the pointer
channel, which is event-driven already. Nothing on the scroll axis is ever an
event.

### One slot

One fixed subtitle at the bottom of the frame, shared with today's focus
caption. No speech bubbles: they pull the eye off what the camera framed.

### Budget

What wears a reader down is repetition and frequency, not the total.

- **Anchored lines are cheap.** One as a chapter opens, one as it closes, at
  most one or two inside it. Around twenty-five across the site.
- **Reactive lines are expensive**, because the hub is where a reader lingers.
  Six is the ceiling, and none plays twice for the same trigger in a session.

The next line added should replace one rather than join it. Write in this
order: `facts`, artifacts, anchored lines, annotation, reactive lines, the
occupant's persona.

## The evidence map

Each object has to pass three tests: a passenger would plausibly have it, it
has a surface the text can live on, and handling it does something a scroll
can drive.

| Chapter    | Object                      | Why he would have it          | What scrolling does   |
| ---------- | --------------------------- | ----------------------------- | --------------------- |
| `about`    | 车票, with a 名片 behind it | everyone has a ticket         | turns it over         |
| `journey`  | 卷起来的线路图, his own     | he drew it; it is his to mark | unrolls it            |
| `stack`    | 公文包, full of books       | it is what is in a briefcase  | draws the books out   |
| `projects` | 电脑                        | he was working                | runs the progress bar |
| `notes`    | _no art yet_ — a notebook   |                               | turns pages           |
| `hobby`    | _no art yet_                |                               |                       |
| `chat`     | 门                          |                               | —                     |

**The scroll is a scroll.** Unrolling the map is the one interaction in the
site where the gesture and the object are the same word — 卷轴 — and the
journey appears station by station as it opens.

**The briefcase reads like a shelf.** Worn spines are what he uses daily. One
still has a bookmark in it: that is what he is learning. Proficiency is shown
by wear instead of by a bar chart.

**The laptop is open and it does not matter.** Every tab is a public
repository. The progress bar of whatever he left running is the chapter's own
reading progress.

**Decoys.** The railway's route map on the wall and the coffee on the table can
be pointed at and open nothing. He dismisses each with a line. A room where
everything is a button is a menu; two things that are not are what make it a
room.

### The confrontation

`chat` is the only chapter where the detective is not alone.

The door opens behind him. The occupant is never drawn: the scene is text
only, over the carriage as it stands, and he is a voice. He takes in the open
briefcase and the unrolled map, and he is less angry than tired:

> 想知道什么，直接问我。翻东西多累。

That is the chat section. The reader has spent the whole site finding things
out the hard way; the occupant offers the easy way. The questions a visitor
actually has — what he has built, what he works with, whether he is available —
are what a detective on this job would ask.

Rules, all downstream of facts-never-behind-fiction:

- **Asked a straight question, it answers straight.**
- **It gates nothing.** If the bot is unavailable the visitor loses a scene,
  not information.
- **Staying in character is soft.**

## The ending

When the conversation is over the detective leaves by the door he came in by,
and the occupant, who has every right to the last word, takes the detective's
first line from him:

> 景色不错吧。

The window transit runs outward, as built, and ends on the city the site
opened on. The footer lives out there — links, colophon, source — as a place
rather than a strip.

**Rejected: a timer.** His return is positional: it happens because the reader
reached the last chapter, not because they were slow. Nothing counts down, and
nothing is lost by stopping.

## What this changes in the content model

| Field      | Layer      | Shape                                                   |
| ---------- | ---------- | ------------------------------------------------------- |
| `artifact` | artifact   | typed fields printed on the object, not prose           |
| `notes`    | annotation | the report: long-form blocks that scroll past it        |
| `lines`    | spoken     | anchored and reactive lines, each with its anchor       |
| `facts`    | none       | the machine-readable truth: role, stack, links, contact |

`facts` is the hedge. Delete the other three and it is still a working personal
site. `content/site.ts` loses its greeting; the cover carries the detective's
opening line.

Decoys need a hotspot with a line and no target, which `hotspots.ts` does not
have today.

## Open questions

1. **What is the hobby object?** It should be the one thing in the room that
   has nothing to do with work.
2. **How hard does the tape press?** The timecode and the grain are the floor.
   Add upward only if the framing is not landing.
3. **Language of first release.**

## Keep in sync

- The evidence map here, the aperture table in
  [10](10-scroll-narrative.md#the-aperture), `hotspots.ts`, and what
  `tools/art/room.py` draws. Three of the four objects need new artwork.
- The content model here and `SectionDef`.
- The lines quoted here and the line sheet in [12](12-script.md).
