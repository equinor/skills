# Building the button, attempt 2: the icon sat 4px low

**Date:** 2026-09-06. **Skill:** `spacing-ladder` as merged in #32.
**Task:** the meetup's "building the button" experiment, attempt 2 — a fresh
agent given the five skills and the button contract, asked to build the EDS
button in CSS. Run and measured by the session working in the meetup repo;
Victor spotted the offset visually the same evening, and the artefact was then
rendered in headless Chrome and read back.

## What held

- Every height emerged from `spacing.py control`: 24 / 36 / 44 for the `md`
  button and 20 / 24 / 36 for the small one, with the paddings left at 6 / 10 /
  12 and not rounded to the grid.
- The icon gap was derived, not typed: 8 / 8 / 10 for `md`.
- The label's centre was true to the button's centre (−0.5px measured).

## What the skill did not teach, and the agent invented

- **The icon's centre sat 4px below the button's.** The skill gave the icon
  *gap* and, in passing, a footprint sentence under icon-only controls; it did
  not give the seat. The agent built a cap-sized wrapper around the svg with
  `display: grid; place-items: center; overflow: visible` and sized the svg
  inside it. The inline svg landed on the wrapper's baseline rather than its
  centre, and a `−1px` hand-fudge appeared on the padding elsewhere to make the
  result look right.
- **The icon size was held flat across densities** (20px for `md`, 18px for
  `sm`) and marked as a guess in the agent's own notes, because the skill
  carried no icon-size sequence.
- **Icon-only was read as `squared`**, giving 32 / 44 / 52 rather than a
  square at the labelled control's height. This one the skill already fixes
  (#32: the horizontal inset collapses to the vertical), and the attempt
  pre-dates that fix.

## Where the findings went

All in the same change as this report:

| Finding | Outcome |
| --- | --- |
| No glyph seat; a wrapper was invented and the glyph sat 4px low | Fixed — `SKILL.md` §5: footprint is the label's cap cell, `margin: (cap − glyph) / 2` negative by construction, the svg is one element; `spacing.py glyph` and `control --icon` compute it; fixtures −5 / −4 / −6 pinned in `check` and the selftest; positions §5 carries the measurement |
| Icon size flat across densities | Fixed — `sizing-icon` sequence with the ladder's density offset, emitted as tokens and CSS, relaxed `6xl` flagged extrapolated |
| Icon-only treated as squared | Already fixed in #32; §4 now says "no pixel to fudge" and points at the seat |

## Re-run against the fix

Attempt 2 was re-run the same night from this branch — same prompt, same
model, the five skills installed from the checkout — and measured the same
way in headless Chrome. Icon drift on every labelled button: **0.00px** (was
4px low). The agent ran `spacing.py glyph`, reproduced the small button's
worked example (cap 8, glyph 16, margin −4 at comfortable) and ran the
fixtures before trusting them. The re-run guessed elsewhere instead — an
attribute-omitted default read the wrong way, so unmarked buttons rendered
bordered at 38px — which is a contract-reading finding for the meetup repo,
not a spacing one: guessing migrates to wherever nothing is derived.

## Reproduction

```bash
python3 skills/spacing-ladder/scripts/spacing.py glyph --label md --icon md
python3 skills/spacing-ladder/scripts/spacing.py check
```

The seat is the `.icon` rule every component in the EDS contracts emits
(`inline-size` and `block-size` from the icon size, `margin` from the cap
and the glyph), read back from the built CSS rather than recalled.
