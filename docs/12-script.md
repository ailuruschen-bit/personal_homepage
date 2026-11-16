# 12 Script

**Status: proposed, and the lines are drafts.** This is the shooting script for
the site: what the camera does, what is on screen, and what is said, scene by
scene. [10](10-scroll-narrative.md) defines the camera; [11](11-premise-and-voice.md)
defines the premise and the rules the writing has to obey. This page is where
they meet.

When the lines are final they move into `content/`, and this page keeps only
the structure.

## Conventions

The prose is English, like every other page here. **The lines themselves are
Chinese**, because they are content rather than documentation — the same rule
that kept the interface copy and the signage in the artwork untranslated.

```
[A]  anchored   a function of scroll offset; replays on a second pass
[R]  reactive   answers the pointer or idling; may never play at all
[L]  live       only in the confrontation, and only once
[   ] placeholder — needs a real fact and is not mine to invent
```

## Cast

| Who      | What they are                                                       |
| -------- | ------------------------------------------------------------------- |
| 侦探     | the reader. Heard, never seen. Every `[A]` and `[R]` line is his.   |
| 他       | the occupant. Appears once, in a doorway, as a silhouette.          |
| the tape | the third character: the timecode, the grain, the fact of playback. |

## The setting

A night train, somewhere between two cities, after midnight. One sleeper
compartment with the light left on.

The occupant has stepped out — to the dining car, the vestibule, a phone call;
it is never said. The detective lets himself in **through the connecting door
from the next carriage**, which is the only way into a compartment on a moving
train and the reason nobody climbs through a window.

What the reader is watching is **the recording of that intrusion**, which is why
it can be rewound. See [11](11-premise-and-voice.md#the-recording).

---

## Scene 0 — The tape begins

**Segment:** the opening, locked. **Camera:** as built today — the blinds tilt
open, the camera pushes through the window and out to the city.

No new artwork. What changes is only what it means: he has just come in, and
the first thing he does is check where the train is.

```
[A] 门在我身后合上了。
[A] 他出去了。十分钟，也许更短。
```

The second line is the only clock the site ever puts on screen, and it is a
line of dialogue rather than a mechanic. Nothing counts down. See
[11](11-premise-and-voice.md#the-ending).

## Scene 1 — The window

**Segment:** cover, `s` 0 → 240. **Camera:** outside on the city, parallax
only. **On screen:** the city, the rain, the timecode.

```
[A] 景色不错。
[A] 但是该干正事了。
```

Two beats rather than one line, anchored a little apart, so the scroll itself
performs the turn from looking to working. The second line is also the scroll
affordance: it says what to do next. Keep a quiet scroll indicator anyway.

## Scene 2 — The carriage

**Segment:** porch, window transit inward, hub. **Camera:** the existing
transit, landing on the hub framing. **On screen:** the compartment, pointer
focus live.

The transit is a glance away and back, not an entrance. He is already inside.

```
[A] 一个人住，东西却摆得像随时要走。

[R] 车窗    外面还是那片城市。
[R] 电脑    屏幕还亮着。
[R] 公文包  没上锁。
[R] idle    ……
[R] 看过的  这个我看过了。
```

The reactive lines are the character's whole personality budget. Five is
enough; the hub is where a reader lingers, and lingering is exactly where a
line repeats itself into irritation.

## Scene 3 — 车票 (about)

**Segment:** chapter 1. **Camera:** carry — it comes up off the table to the
middle of the frame.

**Artifact:** the face of the ticket. `[姓名]` · `[出发地] → [目的地]` ·
`[日期]`.

**Annotation:** who he is, in the detective's report voice, written after the
fact.

```
[A] open   一张票，折过两次。
[A] close  放回去，位置不能动。
```

## Scene 4 — 线路图 (journey)

**Segment:** chapter 2. **Camera:** dolly — it is screwed to the wall.

**Artifact:** the line, with stations. A route map is already a timeline on a
wall, which is why this chapter needs no translating: the stops are `[经历]`.

**Annotation:** where he has been, and what he was doing there.

```
[A] open   墙上的线路图。有几站被圈出来了。
[A] close  他记得每一站。
```

## Scene 5 — 公文包 (stack)

**Segment:** chapter 3. **Camera:** carry — down off the luggage rack, lid
open, and the interior is the aperture.

**Artifact:** what he carries. `[技术栈]`, laid out like tools rather than
listed like a CV.

```
[A] open   公文包没锁。
[A] close  比我想的整齐。
```

## Scene 6 — 电脑 (projects)

**Segment:** chapter 4. **Camera:** dolly — the screen rect becomes the panel.

**Artifact:** what is still open on it. `[项目]`.

```
[A] open   屏幕没锁。他走得很急。
[A] close  合上盖子之前，我记了几个名字。
```

## Scene 7 — 笔记 and 兴趣

**Blocked on artwork.** No object, no aperture, no chapter — see
[11](11-premise-and-voice.md#the-evidence-map). When they exist they sit
between scenes 6 and 8, and they are the two chapters where the detective
should be least sure what he is looking at.

## Scene 8 — The door

**Segment:** the last chapter. **Camera:** the only cut-in in the whole site —
the camera turns to the connecting door as it opens.

He is backlit from the corridor and is a silhouette. He is never drawn further
than that.

```
[A] 门开了。
```

Then the tape chrome goes. The timecode stops, the indicator goes out, the
grain settles, the subtitle loses its transcript styling. Playback has caught
up with the present, and what follows is live. The whole effect is a few
elements fading out, and it is the strongest beat the site has for the price.

```
[L] 他  ……你是谁？
```

Everything after that line is the conversation, and the conversation is the
chat section. He asks what the reader has been reading. The reader can ask him
anything back and gets a straight answer.

He is standing in the doorway the detective came in by. **The other end of the
carriage is open the whole time** — leaving is always available, which is what
makes staying a choice rather than a toll.

## Scene 9 — The last frame

**Segment:** porch out, window transit outward, departure.

However the conversation goes, it ends on the window: the camera pulls back
through it to the city, which is the frame the tape opened on. The footer lives
out here — links, colophon, source — as a place rather than a strip at the
bottom of a page.

```
[A] [结束语 — 一句，侦探的报告收尾]
```

---

## Line sheet

Every line, with where it hangs. This table is the implementation surface; the
scenes above are the reason.

| #   | Tag | Anchor               | Line                                                   |
| --- | --- | -------------------- | ------------------------------------------------------ |
| 1   | A   | opening, 0.35        | 门在我身后合上了。                                     |
| 2   | A   | opening, 0.75        | 他出去了。十分钟，也许更短。                           |
| 3   | A   | cover, 0.15          | 景色不错。                                             |
| 4   | A   | cover, 0.60          | 但是该干正事了。                                       |
| 5   | A   | hub, 0.30            | 一个人住，东西却摆得像随时要走。                       |
| 6   | R   | focus 车窗           | 外面还是那片城市。                                     |
| 7   | R   | focus 电脑           | 屏幕还亮着。                                           |
| 8   | R   | focus 公文包         | 没上锁。                                               |
| 9   | R   | idle at hub          | ……                                                     |
| 10  | R   | refocus, seen before | 这个我看过了。                                         |
| 11  | A   | ch.1 open / close    | 一张票，折过两次。／放回去，位置不能动。               |
| 12  | A   | ch.2 open / close    | 墙上的线路图。有几站被圈出来了。／他记得每一站。       |
| 13  | A   | ch.3 open / close    | 公文包没锁。／比我想的整齐。                           |
| 14  | A   | ch.4 open / close    | 屏幕没锁。他走得很急。／合上盖子之前，我记了几个名字。 |
| 15  | A   | ch.5 open            | 门开了。                                               |
| 16  | L   | live                 | ……你是谁？                                             |
| 17  | A   | departure            | [结束语]                                               |

Sixteen lines and one to write, against the budget of twelve to fifteen in
[11](11-premise-and-voice.md#budget). That is the right size and it is the
ceiling, not the floor — the next line added should replace one, not join it.

## What is still mine to write and what is not

Everything in brackets needs a real fact: the ticket's fields, the stations on
the map, what is in the briefcase, what is on the screen, and the closing line.
The annotation layer for each chapter is not drafted here at all — it is the
longest writing in the project and the most personal, and it is the part that
has to sound like one person rather than like a device.

The order to write in, from [11](11-premise-and-voice.md#budget): `facts`
first, then the artifact fields, then these anchored lines, then the annotation,
then the reactive lines, then the confrontation's persona.

## Keep in sync

- The line sheet here and wherever lines end up living in `content/`.
- Scene numbers here and the segment map in
  [10](10-scroll-narrative.md#the-axis).
- The cast and the drop-the-chrome beat in scene 8 and
  [11](11-premise-and-voice.md#the-recording).
