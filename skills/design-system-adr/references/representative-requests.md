# Representative requests

Acceptance criteria for this skill, per the authoring gate in the repo's
`CLAUDE.md`. A change that breaks any of these is a regression, whatever else
it improves.

**1. "Write an ADR for using vanilla CSS instead of styled-components."**
→ Ask whether it is proposed or already decided, and whether the repository is
public, before writing. Run `adr.py new` for the number and file; fill Context,
at least two options with fair pros and cons, the decision with its drivers,
and consequences as practical implications. Where the notes give no drivers or
no alternatives, ask for them; do not invent a rejected option to make the
record look complete.
*Prevents:* a record with one option and no drivers, which is a memo, not a
decision.

**2. "Supersede ADR-0006; we are going back to modifier classes."**
→ A new record that links the old one under Related, and the one permitted
edit to the old record: its Status line becomes
`Superseded by [ADR-NNNN](NNNN-....md)`. Both index rows change in the same
pull request. If only one aspect is replaced, the old status stays `Accepted`
with a scoped note instead.
*Prevents:* editing the body of an accepted record, and a supersession that
leaves the old record claiming to be current.

**3. "Is this ADR ready to merge?"**
→ `adr.py check FILE` and read the result back with the reasons: sections in
the template's order, status in the vocabulary, an ISO date, every option
with pros and cons, consequences phrased as `Good, because` / `Bad, because`,
number unique, index row present. Then the judgement the linter cannot make:
are the consequences implications after deciding, or the pros restated?
*Prevents:* approving on shape alone, and rejecting on taste alone.

**4. "What number does the next ADR get?"** → `adr.py next --gh`, which counts
open pull requests as well as the directory; without `gh`, `--also` with the
numbers seen in open PRs. Never the lowest gap.
*Prevents:* the collision that gave a public directory two 0004s and two
0005s.

A fifth, for routing: **"write the release notes for 2.1"** and **"document the
button's props"** are not this skill. A record exists where there were options
and a choice; notes, changelogs and reference documentation have neither.
