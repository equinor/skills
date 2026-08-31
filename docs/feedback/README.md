# Skill feedback reports

Reports from using a skill on a real task, rather than reading it. Kept verbatim
as primary records — findings are answered in the repo, not by editing the
report.

Both of these earned their keep. Between them they caught a published number
that was wrong, a script that returned a plausible wrong answer in silence, and
two claims that were true of the formula and false of the output. Testing a
skill by using it found things no amount of re-reading did.

| Report | Skill | Task it came from |
| --- | --- | --- |
| [2026-08-30-typography-x-height-alignment.md](2026-08-30-typography-x-height-alignment.md) | `typography-x-height-alignment` | Aligning Montserrat with Open Sans |
| [2026-08-30-typography-scale.md](2026-08-30-typography-scale.md) | `typography-scale` | Building the EDS-preset scale for that pair, Figma/RN target |

## Where the findings went

### typography-x-height-alignment

| Finding | Outcome |
| --- | --- |
| 1. Variable fonts unhandled, silent wrong answer | Fixed — `xheight.py` reports `instance`, warns when a default is not `wght 400`, warns on `MVAR`, accepts `--location` |
| 2. The demo pair hid finding 1, and its headline number is weight-specific | Fixed — `1.364746` is stated as the wght-400 answer, and the axis contrast became the teaching example |
| 3. `method` never emitted though the token shape requires it | Fixed — emitted and carried into the token |
| 4. "Fonts named but no file" should search first | Fixed — representative request 3 says to look in the working directory before asking |
| 5. `source` assumes a URL exists | Fixed — records path plus `sha256` when there is no URL |
| Reference direction ambiguous | Fixed — "align X with Y" now says which way it reads |
| `nameID1` discarded though it names the instance | Fixed — surfaced in the script output |
| **A single scalar per family is structurally insufficient** | **Open.** Recording the instance makes the current scalar *honest*; making the token hold a per-instance curve is a design decision with consequences for consumers, and has not been taken |

### typography-scale

All four became #17, merged via #14:

| Finding | Outcome |
| --- | --- |
| 1. "Doubles every n steps" is true of the formula, not the output — 5 of 15 pairs miss | Fixed — `references/positions.md`, with the exception list |
| 2. A correction smaller than the snap grid does not survive it | Fixed — `references/positions.md` §6 |
| 3. Say this is a scale for an application interface | Fixed — stated in `SKILL.md` and argued in `positions.md` |
| 4. The ramp is a palette, not a sequence | Fixed — the sub-selection ratio is now given |

## Why these are worth keeping

The authoring gates in `CLAUDE.md` ask for three representative requests before
drafting. These reports are what that looks like done properly and after the
fact: someone used the skill for a real task and wrote down where it misled
them. The pattern worth repeating is that both reports lead with **what
worked** — which is what makes the criticism usable — and both give the
reproduction path for every number they dispute.
