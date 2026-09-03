# Skill test feedback

Skills tested against a real repository, 2026-09-03. Each finding is something I hit while
running the skill, with the evidence that produced it. "Verified working" items are recorded
because both skills invite the reader to distrust their own documented numbers — so I checked
them rather than assuming.

- [`typography-x-height-alignment`](#skill-typography-x-height-alignment)
- [`typography-scale`](#skill-typography-scale)

---

## Skill: `typography-x-height-alignment`

**Tested:** 2026-09-03
**Skill version tested:** `.claude/skills/typography-x-height-alignment` as installed
**Tasks run:** (1) "Show me how x-height alignment works" → demo path; (2) "Align the x-height
of the two fonts in `fonts/`, Literata is the master" → real-pair path against an existing,
already-committed correction.

Overall: the skill works, and its central discipline — derive, record the inputs, assert in a
test — is what surfaced the one real defect in the fixture repo. Findings below are ordered by
how much they'd cost a user who hit them.

---

### 1. HIGH — `opsz` and `font-optical-sizing: auto` are not covered at all

`grep -rin "opsz\|optical" SKILL.md references/` returns exactly one hit, and it is an
incidental example value in `references/token-shape.md:31`. The variable-font section is
entirely `wght`.

This matters because `opsz` is not just "another axis to pin" — it breaks the skill's core
instruction. SKILL.md §1 says:

> Pin the weight the pairing is actually set at.

There is no analogue for `opsz`, because `font-optical-sizing` defaults to `auto`: the browser
picks the axis value at render time, per element, from the rendered px size. So when the
**reference** family has an `opsz` axis, its own `xRatio` is a function of the step — and a
single scalar correction is structurally an approximation across a ramp, not a value that is
exact at one pinned instance.

Measured on the fixture pair (Literata master, `opsz` 7–72, `MVAR` present; Work Sans has no
`MVAR` so it sits at 0.500 throughout):

```
 step      px   opsz   Literata xR   true corr   emitted 1.014      err
   xs   10.5p   10.5        0.5110      1.0220              →     -0.78%
   lg   16.0p   16.0        0.5070      1.0140              →      0.00%
  6xl   37.0p   37.0        0.5090      1.0180              →     -0.39%
```

Here it is benign — 0.78% worst case, under the ~1–2% where a size difference reads. But that
is a property of this pair, not of the method. At the axis floor (`opsz=7`) the true correction
is 1.038 against an emitted 1.014, a 2.4% error, and nothing in the skill would lead a user to
check.

**Suggested fix:** a subsection under "Variable fonts: pin the instance" covering the case where
the *reference* has an `opsz` axis. The guidance is different in kind: you cannot pin, so bound
the drift instead — sample the correction at each step of the actual ramp and assert the flat
scalar stays within tolerance. Worth stating explicitly that `font-optical-sizing: auto` is the
CSS default, since that is what makes it unavoidable rather than opt-in.

### 2. MEDIUM — no procedure for auditing an *existing* committed correction

§5 ("Why this must be derived, not transcribed") is the most persuasive part of the skill and
diagnoses the stale-derived-value failure mode precisely. But every entry point is greenfield:
`references/representative-requests.md` covers the no-fonts demo path, the files-given path, the
refusal path, and a routing check.

The task I was actually given turned out to be the audit case — the repo already had
`tokens/typography.tokens.json`, an emitter, and a test. The skill describes that world's
failure mode without giving a procedure for entering it, so I improvised: re-measure from the
binaries, compare against the committed `$value` *and* against its recorded `instance`, confirm
the `sha256`s still match, then check the test can actually run.

**Suggested fix:** a fifth representative request — "a correction is already committed; verify
it" — with that ordering. It is a common real-world shape and it is where §5's argument pays off.

### 3. MEDIUM — unpinned axes default silently, one axis over from a trap you already document

SKILL.md warns that a variable font's default instance is often not Regular (the Montserrat
Thin example). The adjacent case is not covered: pinning *some* axes and leaving others to
default.

```
$ xheight.py --location wght=400 fonts/Literata.ttf fonts/WorkSans.ttf
warning: Literata: MVAR present: x-height varies along the axes, ...
      "instance": { "opsz": 12.0, "wght": 400.0 }
```

`opsz` silently took its default of 12. The output does report the resolved `instance` (good,
and it is how I noticed), and the generic `MVAR` warning fires — but nothing says "you named
`wght` and left `opsz` to default." In this pair the mistake is invisible, because `opsz` 12 and
16 both yield `xRatio` 0.507; it would only have surfaced at display sizes.

**Suggested fix:** warn per-axis when a font has an `fvar` axis the `--location` did not name.
Cheap, and it fails loud in exactly the case that is otherwise undetectable.

### 4. LOW — venv placement implies a throwaway venv inside the skill directory

§1 gives `python3 -m venv .venv && .venv/bin/pip install fonttools brotli`, and combined with
"cd there first" this puts a venv inside `.claude/skills/typography-x-height-alignment/`. The
fixture project already had `.venv` with `fonttools 4.64.0` at the root, so I built a second,
identical one before noticing.

**Suggested fix:** one line noting any environment with `fonttools` + `brotli` will do, and to
check for a project venv first. The `brotli`-is-for-`.woff2` note is genuinely useful and should
stay.

### 5. LOW — `scripts/xheight.py` arg handling

Hand-rolled parsing in `xheight.py:117-124`. Two rough edges:

- `--help` is treated as a font path: `FileNotFoundError: ... '--help'`, with a traceback.
- `--location` is only recognised as `argv[0]`. Passing it after the font paths also tracebacks.

Both fail loudly rather than producing a wrong number, so this is cosmetic — but a traceback is
a poor first contact with a script whose output is described, correctly, as load-bearing.
`argparse` would fix both and give `--help` for free.

---

### Verified working

Recording these because the skill invites distrust of its own documented numbers, and they held:

- **Demo pair reproduces exactly.** `1.364746` at `wght 400` and `1.302860` at `wght 700`, as
  documented. The weight-axis inversion lesson lands.
- **The `unitsPerEm` teaching point works.** The fixture pair is both-1000-upm, so it does *not*
  teach it — the bundled 2048-vs-1000 pair is doing real work and should stay.
- **`xRatio` plausibility band was useful.** Literata 0.507, Work Sans 0.500, both unremarkable;
  the band correctly stayed quiet.
- **The `$extensions` shape transplanted cleanly.** `derived.expression` + `inputs` was directly
  recomputable by a test with no reinterpretation.
- **The "assert in a test" instruction earned its place.** It is what turned a vague "this looks
  fine" into finding that the fixture's test crashed on line 8 before asserting anything.
- **§4's "never both" check is worth keeping.** Cheap to verify mechanically (no per-family baked
  sizes alongside `size-adjust`), and easy to get wrong when two skills feed each other.

### Fixture note (not skill feedback)

`scripts/emit-xheight-tokens.py`, `test_xheight_tokens.py` and `emit-font-faces.py` shipped with
`ROOT`/`SKILL` hardcoded to `/private/tmp/skilltest2`, so none could run in this checkout — the
test raised `FileNotFoundError` before reaching a single assertion. I made those three
root-relative and regenerated. `emit-scale.py`, `test_scale.py` and `check_scale.py` had the
identical bug and were fixed the same way in the second task below — all six scripts now derive
their paths from `__file__`. Flagging in case the fixture is meant to be portable rather than
deliberately broken; it is worth noting that in both pipelines the *tests* were the files that
could not run, so nothing was verifying anything until the paths were fixed.

---

## Skill: `typography-scale`

**Tested:** 2026-09-03
**Skill version tested:** `.claude/skills/typography-scale` as installed
**Task run:** "Build a type scale based on the Equinor Design System scale" — which turned out,
again, to be an audit: the scale was already implemented and committed.

Overall: this skill is in better shape than the x-height one. I tried to falsify three of its
specific numerical claims and failed on all three. The findings below are about where
instructions live and how two sections interact, not about correctness.

### 1. MEDIUM — §6's verification list omits the octave-deviation fixture

`references/positions.md` §5 ends with a clear, testable instruction:

> Treat the list as a fixture. A sixth deviation means the constants or the snap moved, and
> should fail a build rather than pass quietly.

That is exactly right, and it is the kind of thing §6 ("Verification discipline") exists to
collect — but §6 lists four disciplines and this is not among them. Someone building a harness
works from §6; they will not find it three links deep in a positions document.

Evidence from this repo, which is otherwise a faithful port: `scripts/test_scale.py` runs 353
assertions and checks the octave deviations **zero** times. `scripts/check_scale.py` prints them,
but only at comfortable density, and never fails on a sixth. So the instruction was written,
the port was careful, and the check still didn't get built — which is what a placement problem
looks like from the outside.

**Suggested fix:** add a fifth bullet to §6 pointing at the `positions.md` §5 list, phrased as
the deviation-enumeration discipline §6 already describes for build-over-build changes.

### 2. MEDIUM — §6's "read back from a real browser" collides with §5's baked branch

§6 says:

> Every emitted value equals what the engine computes from the expression. Read back computed
> styles from a real browser, not from the generator that produced them — otherwise the test
> only proves the generator agrees with itself.

§5 says that when older browsers are in scope, emit baked values everywhere and keep the
expression in a comment. Take that branch — as this repo did, and recorded in its CSS header —
and there is no expression left for the engine to evaluate. A browser readback then proves only
that the browser can parse a literal. §6 does not acknowledge the interaction.

It is worth reconciling because the value is *inverted* from what the current phrasing implies.
Readback matters most in the evergreen/expression branch, and the reason is visible in this
repo's own `scripts/scale.py`:

```python
def snap(value, grid):
    """Round half away from zero, matching CSS round(nearest, ...).
    Python's round() is half-to-even and would disagree with the browser on
    exact .25 / .5 boundaries."""
```

A rounding-mode mismatch between generator and engine is precisely what a readback catches, and
it can only bite when the browser is the one evaluating `round()`. In the baked branch the
generator's rounding *is* the answer, and the useful check is the one this repo already has —
recompute the literals from the constants.

**Suggested fix:** split §6's first bullet by the §5 branch. Evergreen → read back computed
styles, and say that the rounding mode is the thing you are actually testing. Baked → recompute
the literals from the constants, and note that readback is near-vacuous here.

### 3. LOW — the audit path is missing here too (cross-cutting, see the other skill)

Same shape as finding 2 in the x-height section: both skills assume greenfield, and both times
the real task was "an implementation already exists — is it right?". Doing that well needs an
ordering the skills don't give: reproduce the published fixture first, then check the committed
artefacts against the formula, then check the generator still reproduces the artefacts
byte-for-byte, and only then look at the values.

That last step is worth naming explicitly because it is cheap and neither skill mentions it —
regenerating into a checksum comparison is what distinguishes "these numbers are correct" from
"these numbers are correct *and* nobody has hand-edited the generated file since."

**Suggested fix:** one shared representative request across the typography skills rather than
one per skill.

### Verified working

I attempted to falsify each of these and could not:

- **The EDS preset fixture reproduces exactly** — 20/20 values, sizes and line-heights, at
  comfortable. The diagnostic framing on `references/eds-preset.md` ("off by 0.5px means the
  snap is wrong, off by 4px means the curve is indexed differently") is unusually good: it
  converts a mismatch into a diagnosis instead of leaving the porter to bisect.
- **The octave deviation list in `positions.md` §5 is exact.** I enumerated all 15 pairs across
  the three densities independently before reading it, and got the same 5 — including the sign
  flip at `relaxed xl→6xl`, which is −0.5px where the other four are +0.5px. A reference that
  survives being checked digit-by-digit against a fresh implementation has earned trust.
- **§5's browser-support pointer is specific and correct.** The note that caniuse has no feature
  for `round()` and that webstatus calls it `round-mod-rem` saved a wrong lookup;
  `api.webstatus.dev/v1/features/round-mod-rem` returns `status: "newly"`,
  `low_date: "2024-05-17"`, matching the claim this repo's CSS header makes. Most skills say
  "check current support" and leave you to find the endpoint. This one names it.
- **§3's label-indexing trade-off reproduces in the built output**, exactly as the worked example
  in the skill predicts: `compact/xl` 16px→20px, `comfortable/lg` 16px→24px, `relaxed/md`
  16px→24px. Documenting the consequence as a table of collisions is more convincing than
  describing it in prose would have been.
- **The instruction to ask before emitting (§4, §5) is placed correctly** — before output, not
  after — and both questions genuinely change the artefact rather than its packaging.
