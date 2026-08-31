# The bundled demo pair

`assets/fonts/` ships Inter and EB Garamond, both SIL OFL, so
`scripts/xheight.py` runs with nothing supplied. Referenced from `SKILL.md`.

Run it with no arguments to check your environment works. It prints JSON; the
figures that matter are:

```
Inter        upm 2048  xHeight 1118  xRatio 0.545898  @ wght 400   (reference)
EB Garamond  upm 1000  xHeight  400  xRatio 0.400000  @ wght 400   correction 1.364746
```

This pair is chosen to teach, not to flatter, and it teaches two things.

**Normalise before comparing.** The fonts have different `unitsPerEm`, so the
raw x-heights (1118 against 400) suggest Inter's is nearly *three* times larger
when it is 1.36×. Skip the division and be wrong by a factor of two.

**A correction belongs to an instance.** Both files are variable with an `MVAR`
table, and EB Garamond's x-height moves along the weight axis while Inter's does
not:

```
             wght 400   wght 700   wght 800
Inter        0.545898   0.545898   0.545898   (flat)
EB Garamond  0.400000   0.419000   0.423000
correction   1.364746   1.302860   1.290540
```

So `1.364746` is not *the* answer for this pairing — it is the **wght 400**
answer, and quoting it without that is the same defect as section 5's.

It is also a fair test of the alternative: ask a language model how to pair
these two and you get "EB Garamond has a low x-height, so boost your headings —
32px or more." Correct diagnosis, guessed number. The measured answer is
`0.545898 / 0.400 = 1.364746` at wght 400, which at a 32px step sets EB Garamond
at 43.5px.

Bundling these binaries does not contradict the no-vendoring rule in `SKILL.md`
section 1. That rule is about **licence-restricted** faces — Equinor's cannot be
redistributed. OFL fonts can, provided the licence travels with them; see
[`assets/fonts/README.md`](../assets/fonts/README.md) for authorship, provenance
and the terms, which are **not** this repository's MIT licence.

