# Feedback: `typography-x-height-alignment`

From a real run on 2026-08-30. Two requests were exercised:

1. *"How does x-height alignment work?"* → representative request #1 (no fonts named)
2. *"Align Monserrat with OpenSans"* → representative request #3 (fonts named), except
   the files turned out to be sitting in the working directory

Everything below is reproducible from this directory. Findings are ordered by how
badly they affect the output.

---

## What worked

- **The normalise-before-comparing lesson lands.** It was load-bearing in the real
  pairing too: raw x-heights of 1096 (Open Sans) vs 517 (Montserrat) read as "twice
  the size" until you divide by `unitsPerEm`. The demo pair's 1118-vs-400 is a good
  exaggeration of a trap that genuinely recurs.
- **The §4 delivery gate is the right shape.** Asking CSS-only vs Figma/RN *before*
  emitting anything changed the deliverable materially — the `size-adjust` path would
  have been silently wrong. Good that this is a hard stop rather than a footnote.
- **"Ask for the namespace rather than invent one"** (`references/token-shape.md`)
  worked exactly as intended.
- **The 105.9% case study in §5 is the most persuasive part of the skill.** It makes
  `derived: {expression, inputs}` feel necessary rather than ceremonial.
- **Deriving from raw font units rather than the rounded `xRatio`** — the comment in
  `xheight.py` explaining why is a good catch and worth keeping.

---

## 1. Variable fonts are unhandled, and the failure is silent — the big one

`xheight.py` reads whatever the font's **default instance** happens to be, with
nothing in the output saying so.

Montserrat's variable file defaults to `wght 100`:

```
axes: [('wght', min 100.0, default 100.0, max 900.0)]
name ID 1: "Montserrat Thin"
```

So the straightforward run produced a **correction of 1.035118 — the Thin figure**.
Nothing in the JSON hints at it. The number is plausible, in the expected range, and
wrong for essentially any real pairing. I only caught it by separately dumping
`fvar`, which the skill never asks you to do.

It compounds: Montserrat ships an `MVAR` table, so its x-height genuinely varies
along the axis, and a single scalar per family is structurally insufficient.

| wght | xRatio | correction vs Open Sans |
|---|---|---|
| 100 *(file default)* | 0.517000 | 1.035118 |
| 400 | 0.525000 | 1.019345 |
| 600 | 0.534000 | 1.002165 |
| 700 | 0.538000 | 0.994714 |
| 900 | 0.547000 | 0.978348 |

The correction **crosses 1.0 near wght 600** — pair at Bold and the "smaller" face
needs to be set *smaller still*, inverting the correction's direction. A skill whose
entire premise is "derive, don't guess" currently hands back a number that is
weight-specific without saying which weight.

**Suggested fixes**, cheapest first:

- Print the resolved instance in the output: `"instance": {"wght": 100}`, plus name
  ID 1 (`"Montserrat Thin"`), which is the tell.
- Warn loudly when the default instance is not Regular — `default != 400` on `wght`
  is a near-certain sign the user wants a different instance.
- Detect `MVAR` and warn that x-height is axis-dependent, so one scalar only holds
  at one location.
- Accept an instance location: `xheight.py FONT.ttf --location wght=400`, using
  `fontTools.varLib.instancer`.
- In `SKILL.md`, add a "which instance?" step between §1 and §2, and add "ask which
  weight the pairing is set at" to the §4 questions.

## 2. The demo pair hides finding #1 — and its headline number is itself weight-specific

I assumed the bundled fonts were static. They are not:

```
Inter.woff2       variable: True   MVAR: True   axes: opsz(14), wght(100/400/900)
EBGaramond.woff2  variable: True   MVAR: True   axes: wght(400/400/800)
```

Both default to `wght 400`, so the trap never fires and the demo looks clean. Worse,
EB Garamond's x-height *does* move across the axis:

```
EB Garamond  wght 400 → 0.400000     Inter wght 400 → 0.545898
             wght 700 → 0.419000           wght 700 → 0.545898  (flat)
             wght 800 → 0.423000

correction @ wght 400 = 1.364746     ← the number in SKILL.md
correction @ wght 700 = 1.302860
```

So `0.545898 / 0.400 = 1.364746`, quoted three times in `SKILL.md` as *the* answer,
is really the **wght-400** answer. The skill teaches "a derived number stored without
its inputs goes stale silently" and then quotes a number without one of its inputs.

**Suggested fix:** state the instance wherever that figure appears, and use the
Inter-flat / Garamond-varying contrast as the teaching example for finding #1 — it's
already in the bundled assets, costs no new binaries, and turns the demo into a
demonstration of the axis problem rather than a place it hides.

## 3. `scripts/xheight.py` never emits `method`, which the token shape requires

`references/token-shape.md` requires `method`, and correctly insists that
`OS/2.sxHeight` and `measured:x-glyph-bounds` "are not the same quality of evidence."
`SKILL.md` §1 says to "note it in the output when you had to measure."

But the script's `metrics()` has the fallback branch and simply doesn't record which
one fired — the returned dict has no `method` key. To fill in a required token field
I had to write a separate script dumping `OS/2.version` and `sxHeight`. Every user
will either repeat that work or, more likely, guess the value — in a field that
exists precisely so nobody has to guess.

**Suggested fix:** set `method` in the branch that already exists:

```python
x, method = os2.sxHeight, "OS/2.sxHeight"
if not x or x <= 0:
    x, method = glyph_top(font, "x"), "measured:x-glyph-bounds"
```

and include it in the returned dict. Roughly four lines, and it closes the gap
between the two files.

## 4. "Fonts named but no file" should say to look in the working directory first

Representative request #3 says: a font is named, no file available → ask for it.
Here, `Montserrat-VariableFont_wght.ttf` and `OpenSans-VariableFont_wdth,wght.ttf`
were in the working directory, unmentioned by the user. Searching first was obviously
right and saved a needless round trip, but the skill's phrasing pushes toward asking.

**Suggested fix:** reword #3 to *"look in the working directory and the usual font
locations first; ask only if that turns up nothing."* The anti-goal being protected —
never answer from remembered metrics — is untouched by this.

## 5. `source` assumes a URL exists

§1 says to commit "the extracted metrics plus the source URL." When measuring local
files there is no URL, and the rule can't be satisfied. I left a `TODO` in the token
and flagged it, but the skill should say what to do: record path + `extractedAt` +
a checksum, and treat the missing URL as a known gap. `assets/fonts/SHA256SUMS`
suggests the checksum habit already exists here — worth promoting into the token
shape as a fallback when no URL is available.

---

## Smaller notes

- **Reference direction.** "Align X with Y" implies Y is the master. I inferred it and
  said so; one line in §2 would remove the ambiguity.
- **`family` naming.** `getDebugName(16) or getDebugName(1)` returned `"Montserrat"`
  via ID 16 — but ID 1 was `"Montserrat Thin"`, the strongest available signal about
  the default instance, and it gets discarded. Surface both.
- **Setup friction.** `python3 -m venv .venv && .venv/bin/pip install fonttools brotli`
  is in §1 and worked first try. `brotli` is only needed for `.woff2` — both fonts here
  were `.ttf` and wouldn't have needed it. Not a problem, just noting the guidance is
  correctly conservative.
- **§6's overflow tip paid off.** Open Sans extent 1.362em vs Montserrat 1.219em, so
  the corrected face is again not the overflow candidate — the tip generalises past
  the Equinor case it came from.
- **The `DO NOT USE FOR:` routing cue worked.** Never felt tempted toward
  `typography-scale` until the baked-sizes step genuinely called for it.

---

## Summary

The reasoning is sound and the token/provenance discipline is the best part. The gap
is that **the tooling assumes static fonts while the bundled assets, and most fonts
anyone will actually pass it, are variable** — and the failure mode is a plausible
wrong number rather than an error. Findings #1–#3 are all one root cause: the script
reports *what* it measured but not *where on the axis* or *by what method*. Making
`xheight.py` report its own provenance would close all three.
