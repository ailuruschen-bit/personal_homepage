# 11 Premise and voice

**Status: proposed. Nothing in this page is implemented.** It settles what the
content _is_; [10 Scroll narrative](10-scroll-narrative.md) settles how the
camera moves through it, and [12 Script](12-script.md) writes it out scene by
scene.

## The premise

A private detective has been hired to find out what kind of person the occupant
of a sleeper compartment is. The occupant has stepped out to take a phone call.
The detective walks down the corridor from the next carriage, lets himself in,
and goes through the man's things — wearing a camera, because the client wants
to see for themselves.

**The reader is the client.** They watch the feed through the detective's eyes
and hear him mutter as he works. They never chose to be a detective; they
wanted to know about this person, which is the real reason anyone opens a
personal site. The fiction does not ask the reader to pretend anything. It
describes what they are already doing.

Who the client is, is never said. A recruiter will recognise themselves and
smile; everyone else is simply curious, which is also a kind of client.

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

**Why the reader can scroll back.** It is a feed with a buffer. See
[The recording](#the-recording).

**Why the chat exists.** Because he gets caught, and the occupant would rather
answer questions than be investigated. See
[The confrontation](#the-confrontation).

## Plausibility audit

Every hole found in the earlier drafts, and what closes it. A fiction that
wants the reader to smile cannot afford one detail that makes them frown.

| Hole                                                                  | Fix                                                                                                           |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Nobody climbs into a moving train through a window                    | He comes down the corridor and through the compartment door                                                   |
| The detective had no reason to be there                               | He is on a job. The client wants to know who this man is                                                      |
| The reader was told to be a detective, but wants what a client wants  | The reader is the client, watching through his camera                                                         |
| A break-in cannot be rewound                                          | It is a feed with a buffer; scrolling back is reviewing footage                                               |
| A reader can take an hour; he has a minute                            | The timecode is a function of scroll, not of the clock. The tape is under ten minutes however long it is read |
| A passenger does not scribble on the railway's wall map               | The wall map stays as a decoy he dismisses. The journey is a rolled map of his own                            |
| A ticket does not say who someone is                                  | His business card is tucked behind it. The ticket says where he is going; the card says who he is             |
| "Tools of the trade" in a briefcase was a metaphor with nothing in it | It holds books. Worn spines are what he uses, the bookmarked one is what he is learning                       |
| An engineer who leaves a laptop unlocked looks careless               | Everything open on it is a public repository. Nothing leaks, and the detective is the one who looks foolish   |
| Why is the coffee steaming if he went for coffee                      | He went to take a call in the vestibule, which is where calls are taken on a train                            |
| The reader's real questions are a client's, not a burglar's           | At the door the occupant takes the camera and addresses the client directly                                   |
| A camera on the detective cannot fly out of the window at the end     | The occupant turns it to face the window. The last shot is his, and so is the last line                       |

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

### A feed with a buffer

The detective's camera transmits to the client. Like any recorder with a
buffer, the feed can be scrubbed back and played forward, and it can be paused.
Scrolling is scrubbing. Stopping is pausing. Nothing about the interaction has
to be excused; it is what the device does.

Footage rather than memory, because a tape's signifiers are concrete and a
memory's are vague, and because the film grain already in the artwork stops
being a style and becomes a property of the picture.

### Three layers, two time frames

| Layer      | When        | Voice                                      |
| ---------- | ----------- | ------------------------------------------ |
| artifact   | on the tape | none — it is a document                    |
| spoken     | on the tape | what he muttered while working: short, dry |
| annotation | afterwards  | the written report to the client, composed |

The spoken lines can be unsure and the report can be certain without either
being out of character.

### What carries it

| Element    | Doing double duty as                                |
| ---------- | --------------------------------------------------- |
| timecode   | the scroll progress indicator                       |
| 回放 badge | the reminder that this has already happened         |
| ▶▶         | what a click-to-jump looks like: it is fast-forward |
| grain      | already in the artwork; now it has a reason         |
| subtitle   | his muttering, transcribed                          |

The timecode maps scroll offset onto elapsed time, not the reader's clock. The
whole intrusion runs a little under ten minutes however long it is read. That
makes a joke with no words in it: his "one minute" is on screen the whole time,
and by the door it reads `00:09:47`.

**Rejected: deliberate glitches.** Dropped frames and tearing look exactly like
the compositing fault this project spent seven attempts removing — see
[09](09-fix-log.md#f-001-chrome-the-city-drawn-over-the-carriage). Nothing
should pretend to be broken.

### Where playback ends

At the door. The badge changes from 回放 to LIVE: the buffer has caught up with
the present. It is one word changing in a corner, and it is the strongest beat
in the site, because everything before it was already over.

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

`chat` is the only chapter where the detective is not alone, and it is where
the reader stops being a spectator.

The door opens. He is a silhouette against the corridor and is never drawn
further than that. He looks at the detective, then at the camera, and he
understands the situation faster than the detective would like. He picks up the
camera and speaks into it:

> 还录着呢。那正好——不管是谁在看，想知道什么，直接问我。

That is the chat section. The occupant is talking to the client, who is the
reader, about the thing the reader came to find out. Nobody is asked to
roleplay. The questions a visitor actually has — what he has built, what he
works with, whether he is available — are exactly the questions the scene calls
for.

Rules, all downstream of facts-never-behind-fiction:

- **Asked a straight question, it answers straight.**
- **It gates nothing.** If the bot is unavailable the visitor loses a scene,
  not information.
- **Staying in character is soft.**

## The ending

When the conversation is over, the occupant puts the camera down facing the
window. The last shot is the city the tape opened on, and the last line is the
detective's first one, taken from him:

> 景色不错吧。

The window transit runs outward, as built. The footer lives out there — links,
colophon, source — as a place rather than a strip.

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

1. **The reader as client rather than detective.** This departs from the
   original brief, which cast the reader as the detective. The reader still
   sees everything through his eyes; what changes is who the tape is for. It is
   the fix for the chat making sense, and it is the largest single decision on
   this page.
2. **Is the client ever named?** Proposed: no.
3. **Does the detective get a last word in the chat?** There is a line for it
   in [12](12-script.md). It is the cheapest laugh in the script and the first
   to cut.
4. **What is the hobby object?** It should be the one thing in the room that
   has nothing to do with work.
5. **Language of first release.**

## Keep in sync

- The evidence map here, the aperture table in
  [10](10-scroll-narrative.md#the-aperture), `hotspots.ts`, and what
  `tools/art/room.py` draws. Three of the four objects need new artwork.
- The content model here and `SectionDef`.
- The lines quoted here and the line sheet in [12](12-script.md).
