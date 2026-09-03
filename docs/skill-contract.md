# Skill contract

What every skill in this repository delivers, stated once so that a new skill
can be built to it and an existing one checked against it. `CLAUDE.md` says
how to work here; this says what the output has to be. Items marked **(C)**
are the parts `scripts/check-skills.py` can see; it reports each as a
`contract` warning. The rest are checked by using the skill in a fresh session
and writing down what happened, in `docs/feedback/`.

## 1. Tokens first (C)

Every skill that produces values emits them as **DTCG design tokens**, and
everything else — CSS, Figma variables and text styles, React Native values —
is an output derived from those tokens. Never the other way round.

The derivation travels with the value, in `$extensions` under a reverse-DNS
namespace of ours — `com.equinor.typography`, `com.equinor.color`,
`com.equinor.spacing`, in code spelling because it is a key in a file — as
`derived: { expression, inputs }`. Where the value was measured rather than
computed, the extension also carries what was measured: `instance`, `method`,
`source`, `sha256`, and a date.

The skill shows the shape in `references/token-shape.md`, as a JSON block that
parses, and the selftest runs the skill's emitter against that block rather
than against a fixture written for the test.

## 2. Ask before emitting (C)

Two questions, asked before any output, wherever they apply:

- **Target.** CSS only, or also Figma, React Native or another non-CSS
  platform? The answer changes the artefact — for example one corrected ramp
  with `size-adjust` against two baked ramps — not its packaging.
- **Browser matrix.** Evergreen only, or older browsers in scope? Decides
  expressions against baked literals, and is a question for the project's
  `browserslist`, never a verdict the skill hands down.

A question that would not change the output is not asked.

## 3. Measure, never recall

Numbers come from the artefact: the font binary, the rendered page, the token
file. Not from memory, not from a specification page, not from a previous
version of the same skill. Any factual claim with a shelf life — browser
support, a font's metrics, an axis range — names where to check it
(webstatus.dev, caniuse `features-json`, "re-run the script") and carries the
date it was last checked.

## 4. Scripts, not snippets (C)

A number the reader will build on comes from a script in `scripts/`, not from
a code block they retype. Scripts take `argparse` arguments and answer
`--help`, print JSON on stdout and warnings on stderr, and exit 2 with
instructions when a dependency is missing rather than dying inside a redirect.
They never tell the reader to create anything inside the installed skill
directory, which `npx skills update` replaces.

`scripts/selftest.sh` runs the worked examples against the fixtures the skill
documents and asserts the published numbers. A skill without one has
unverified examples.

## 5. Representative requests (C)

At least three, in `references/representative-requests.md`, written before
drafting and re-checked after: the trigger a user would type, the behaviour
the skill should produce, and the mistake it must prevent. One of them is the
**audit case** — an implementation already exists; is it right? — with the
order: reproduce the fixture, compare against the committed values and their
recorded inputs, regenerate and diff byte-for-byte, then test. A routing check
against the nearest sibling skill closes the list.

## 6. Positions with their evidence (C)

Where the skill takes a side that a system under delivery pressure would
simplify, `references/positions.md` states the position, the measurement
behind it, and the cost of simplifying. It never compares against a named
party's decision, never cites another organisation's records, and never
carries internal specifics; a lesson is taught through the bundled assets or a
public pair, not through the incident that produced it.

## 7. Assets

Bundled files are under a licence that permits redistribution (SIL OFL or
equivalent), with the licence text and a `SHA256SUMS` alongside, and a
`README` saying what each file is for. Anything else — a proprietary typeface,
a private token set — is referenced by URL and never committed.

## 8. Shape (C)

The conventions in `CLAUDE.md`. Checked mechanically: two frontmatter keys;
`USE FOR:` and `DO NOT USE FOR:` cues that name the neighbouring skill;
`SKILL.md` within the 300-line gate with overflow in `references/` one level
deep; a `## Related` section instead of a merged skill. Checked by reading:
Oxford English in prose and US English in code.

## 9. Degrade, never demand

An integration the skill can use but cannot assume — a Figma MCP, a browser
for readback, `node` for an emitter — is detected first. When present it is
used; when absent the skill still delivers everything else and writes what it
would have sent to a file, with a note on how to apply it by hand. A user who
wants only the CSS is never asked to set up Figma.

## Applying it

Run `python3 scripts/check-skills.py`. Each `contract` warning is a to-do for
that skill; open an issue for it or fix it in the same change. A new skill is
not ready while any remain. An existing skill may carry them for a while, but
the warning stays visible until it does not need to.

**A skill that produces no values may waive items 1 and 4.** Some skills are
guidance — a way of writing CSS, a review discipline — and have no number for a
token to hold or a script to compute. Such a skill says so in one sentence near
the top of `SKILL.md`, containing the words **emits no values**, and the checker
then reports items 1 and 4 as notes rather than warnings. This is a declaration,
not a fix: a skill that does produce numbers and writes the sentence anyway has
lied to the checker, and a fresh-session test will show it. Items 2, 3, 5, 6, 8
and 9 apply to every skill; the fixed cost of a narrow skill is a requests file,
a positions file and a `## Related` section, which is what makes it a skill
rather than a page.
