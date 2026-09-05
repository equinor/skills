---
name: design-system-adr
description: 'Writes, checks, supersedes and indexes Architecture Decision Records in the Equinor Design System format — MADR with bullet-list metadata, per-option pros and cons, a flat Decision with Consequences and Confirmation. USE FOR: drafting an ADR from notes or a discussion, superseding or deprecating an accepted ADR, reviewing an ADR before merge, finding the next ADR number, generating the ADR index. DO NOT USE FOR: release notes, changelogs, component or API reference documentation, meeting minutes, or a convention with no alternatives (a record needs options and a choice).'
---

# Architecture Decision Records

A decision record answers one question a future reader will ask: *why is it
like this?* It names the situation, the options that were on the table, the
one chosen and what it cost. Written well, it outlives the people who wrote
it, which is the point — a design system team turns over, and the record is
the channel between one iteration of the team and the next.

The format here is the Equinor Design System team's: Michael Nygard's record
(context, decision, consequences) as structured by MADR (drivers, options with
pros and cons, `Good, because` / `Bad, because` consequences, confirmation),
with the team's own choices — bullet-list metadata instead of YAML front
matter, pros and cons inline under each option, a flat `## Decision` with
`### Consequences` and `### Confirmation` beneath it, and `## Related` last.
The template is [`references/template.md`](references/template.md), verbatim.

This skill **emits no values**: its output is a Markdown record, an index and
a lint result, not tokens.

## What you need before starting

1. **The decision, or the discussion that needs one.** Notes, a thread, a
   pull request. If there is only a conclusion and no alternatives, say so:
   a record with one option is a memo, and the reader deserves to know that.
2. **The directory.** `documentation/adr/` in the target repository, created
   if missing, with the template copied in as `0000-template.md`.
3. **Who decided.** The `Decision makers` line names people or a team; "the
   team" with no name is a record nobody can ask about.

## Ask before emitting anything

> Is this decision proposed, or already made? And does the record go in a
> public repository?

Both change the output. *Proposed* is a draft for review, dated today, with
the options still open in tone; *Accepted* records a decision with its date
and the drivers it satisfied. Public is the default for decisions about
components, tokens, APIs, tooling and processes; only sensitive content —
security details, internal infrastructure — goes to an internal repository,
and the record says nothing that would not survive being public later.

If the decision supersedes an earlier record, that is the third question, and
section 4 applies.

## 1. Number and name the record

```bash
skill=.claude/skills/design-system-adr             # where the installed copy lives
python3 $skill/scripts/adr.py next --gh            # next free number, counting open PRs
python3 $skill/scripts/adr.py new "Use vanilla CSS with design tokens" --deciders "EDS Core Team"
```

The number is one more than the highest in the directory **and** in open
pull requests that add a record. Two people who each take "the next one" in
the same week produce two records with one number — a public directory has two
such pairs — and renumbering afterwards breaks every link already pointing at
them. So: claim the number in the pull request, never reuse or renumber, and
let a closed-unmerged PR leave a gap, recorded in the index as `Unused`. When
`gh` is not available, pass `--also N,N` with the numbers you can see in open
pull requests.

The filename is `NNNN-short-kebab-title.md`; the H1 is the title in sentence
case with **no number** — the filename carries it. `adr.py new` writes the
template with the guidance comments removed and the metadata filled in.

## 2. Fill the record

Work down the template. What each section is for, and the mistake it exists to
stop:

- **Context** — the situation and what triggered the decision, with the
  background a newcomer lacks. Not the decision; that comes later.
- **Decision Drivers** — the requirements and constraints the options are
  judged against. If you cannot list them, you cannot say why the winner won.
- **Options Considered** — every realistic option, each with **Pros** and
  **Cons**. An option with no pros was not considered; it was set up to lose.
  Fewer than two options is not a decision, and the linter says so.
- **Decision** — what was chosen and *why*, in terms of the drivers. Often a
  short code example of the resulting pattern.
- **Consequences** — `Good, because …` and `Bad, because …`: what the team
  does differently now, what migrates, what gets harder. These are
  implications *after* deciding; the pros and cons were arguments *before*. A
  record whose consequences restate its pros has argued for itself twice and
  never said what it costs. Every decision costs something.
- **Confirmation** — how anyone will know the decision is followed: a review
  check, a lint rule, a CI step. Optional in the template, and the section most
  often left out, which is why the linter warns when it is missing.
- **Related** — other records, issues, discussions, the sources the decision
  leaned on. Linked, not paraphrased from memory.

Delete every guidance comment. The worked example this skill ships,
[`assets/examples/0001-claim-adr-numbers-by-pull-request.md`](assets/examples/0001-claim-adr-numbers-by-pull-request.md),
is a complete record in this shape, and the one the selftest checks.

## 3. Check it before it merges

```bash
python3 $skill/scripts/adr.py check documentation/adr        # the directory, with its index
python3 $skill/scripts/adr.py check documentation/adr/0016-*.md
```

The linter fails on what the template and the accepted records agree on and
warns on the rest: filename shape; an H1 without a number; `Status`, `Date`
and `Decision makers` present, the status in the closed vocabulary
(`Approved` is not in it), the date `YYYY-MM-DD` and nothing else; the six
required sections present and in the template's order; at least two options,
each with pros and cons; consequences as `Good, because` / `Bad, because`
bullets; a `Superseded by` link that resolves; a number used once; an index
that lists the record. It warns when `Confirmation` is missing, when no
consequence is bad, when guidance comments are still in the file, and when
the directory has no index.

Then the judgement no linter makes: are the consequences implications or
restated pros, are the rejected options fairly described, does the decision
cite its drivers? Read for those. Run against a public fifteen-record
directory on 2026-09-05, the linter found the two duplicated numbers, one
status outside the vocabulary, one date line carrying a revision log, one
option without pros or cons and one record without consequences — each a
place where a reader would have had to guess.

## 4. Status: supersede, do not edit

`Proposed → Accepted` or `Proposed → Rejected`. After acceptance the body is
immutable, and the one permitted edit is the Status line:

- **Full supersession.** The new record links the old under `## Related`; the
  old record's status becomes `Superseded by [ADR-NNNN](NNNN-title.md)`.
- **Partial supersession.** One aspect replaced, the rest standing: the old
  record keeps `Accepted` with a scoped note —
  `Accepted (CSS naming convention superseded by [ADR 0006](0006-….md))`.
- **Deprecated.** The decision no longer applies and nothing replaced it.
- **Rejected** records keep their number; the record of what was *not* chosen
  is worth as much as the record of what was.

Both index rows change in the same pull request as the new record.

## 5. Keep the index

```bash
python3 $skill/scripts/adr.py index --write          # documentation/adr/README.md
```

A directory of records carries a `README.md` table — number, title, status,
date — so status is visible without opening every file and a gap can be told
from a lost record. It is generated from the files and never edited by hand;
the linter fails when a record is missing from it. Shape and rules:
[`references/index.md`](references/index.md).

## 6. When a record establishes a rule agents must follow

Add it to the list of records in the repository's `CLAUDE.md` or `AGENTS.md`,
so an agent reads the decision before touching the pattern it governs. A
record nobody is pointed at is a record nobody follows.

## Representative requests

Four acceptance criteria — drafting from notes, superseding an accepted
record, reviewing before merge, finding the next number — plus a routing
check: [`references/representative-requests.md`](references/representative-requests.md).

## Positions this skill takes

Seven, each with what was observed when it was not held: immutability with
supersession, consequences as implications not restated pros, numbers claimed
by pull request and never renumbered, a generated index, fair treatment and at
least two options, a closed status vocabulary, and public by default:
[`references/positions.md`](references/positions.md).

## Related

- **`css-authoring`** — the pattern many EDS records decide about; not yet
  published in this repository.
- **`typography-scale`** and the other typography skills — record their
  positions in `references/positions.md`, which is the same discipline at the
  skill level: a position with its evidence, kept where the reader is.

## Provenance

The format is `documentation/adr/0000-template.md` in `equinor/design-system`
(MIT), and its ADR-0001 declares the choice of MADR. The numbering rule, the
partial-supersession status, the index and the agent-instructions pointer were
worked out with the EDS token rework in `equinor/ids-meetup-oslo-26`
(Equinor-internal) for the Into Design Systems Oslo meetup, 9 September 2026,
after the directory's own collisions made the need visible.
