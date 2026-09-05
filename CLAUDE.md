# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

`equinor/skills` is a **content repository**, not a software project. It publishes Agent Skills — design-system guidance (typography, colour, spacing) written as Markdown — built to the open [Agent Skills](https://agentskills.io) standard so they run across Claude Code, Copilot, Cursor, Codex and other compatible agents.

Consequences for how you work here:

- There is **no build, no lint, no test suite, and no package manager** — no `package.json`, no CI beyond the Claude Code action. Do not add tooling unless asked.
- The deliverable is prose that an agent will follow. Review it the way you would review code that runs: check that instructions are unambiguous, that examples are correct, and that nothing tells the agent to rely on stale knowledge.
- Status is pre-release (README: 🚧). First skills land after the Into Design Systems Oslo meetup, 9 September 2026.

## Layout and conventions

```
skills/<domain>-<topic>/SKILL.md   one skill per directory, kebab-case
demo/<topic>/                      talk artefacts; each has an INTENT.md that governs it
.github/workflows/claude.yml       @claude bot, gated to write-access collaborators
```

`demo/` pages quote the skills' emitted numbers and reference fonts from the
EDS CDN, never bundle them; `demo/typography/INTENT.md` records the rules.

**Skill names are prefixed by domain** — `typography-`, `colour-`, `spacing-`,
`design-system-` — so the install command reads as a namespace:
`typography-scale`, `typography-x-height-alignment`, `colour-contrast`. The prefix is
a namespace, not the document title; the `# H1` inside `SKILL.md` is written for a human
("# x-height alignment").

**Prefer several narrow skills over one broad one.** The `description` is the only thing
an agent reads when deciding whether to load a skill, so each skill should answer one
trigger. Two topics that share an implementation are still two skills if a reader would
arrive at them from different questions — x-height alignment is derived from the type
scale's steps, and is a separate skill because "I'm pairing two fonts" is not "I'm
defining a scale". Cross-link with a `## Related` section instead of merging.

`SKILL.md` starts with YAML frontmatter carrying exactly two keys:

```yaml
---
name: css-authoring          # must match the directory name
description: '…'            # see the routing-cue format below
---
```

The `description` is the only thing an agent sees before deciding to load the skill,
so it carries explicit routing cues, in the format used by `equinor/fusion-skills`:

```
description: '<what it does>. USE FOR: <trigger phrases and situations>.
DO NOT USE FOR: <anti-triggers, naming the neighbouring skill>.'
```

**Anti-triggers stop being optional as soon as two skills are adjacent.** Siblings
share vocabulary — `typography-scale` and `typography-x-height-alignment` both talk
about fonts, sizes, steps and tokens — and no amount of positive phrasing tells an
agent which one a question belongs to. Naming the neighbour does.

This applies to the description only. It is a routing signal, matched against rather
than followed; the skill *body* keeps positive framing, because an instruction written
as a negation still puts the thing it forbids in play.

Body is prose + fenced examples, hard-wrapped around 78 columns, `##`-numbered
top-level sections.

Work on a new skill happens on a `skill/<skill-name>` branch (see `origin/skill/css-authoring` for the reference draft, which establishes the house style: a named core pattern first, then supporting practice, then discipline/anti-patterns).

## Authoring gates

Five checks before a skill is ready, adopted from the `fusion-skill-authoring`
skill in [`equinor/fusion-skills`](https://github.com/equinor/fusion-skills)
(`@equinor/fusion-core`). That repo is further along than this one on catalog
tooling — per-skill versioning, lifecycle metadata, and validation CI — and is
worth reading in full before writing a new skill.

**0. Read [`docs/skill-contract.md`](docs/skill-contract.md) first.** It
states what every skill must deliver — tokens first, ask before emitting,
scripts not snippets, positions with evidence — once, so a new skill can be
built to it and an existing one checked against it. `check-skills.py` reports
each item it can see as a `contract` warning.

**1. Write the representative requests before drafting** — the shape and the
file they live in are [contract §5](docs/skill-contract.md). They are the
acceptance criteria: check the finished skill against them, not against your
intent while writing it. If you cannot write three, the scope is underspecified
or too narrow to be reusable. This is also the cheapest way to catch two skills
that should be one, or one that should be two.

**2. Keep `SKILL.md` under 300 lines.** Long files degrade on smaller runtimes,
and 500 is a hard failure in Fusion's CI. Move overflow into `references/` one
level deep — never a chain of links that forces partial reads. The typography
skills sit at 188-300 lines, so there is less headroom than it looks.

**3. Check `skills-lock.json` before editing an existing `SKILL.md`.** If the
file is an *installed copy* — its `skillPath` matches and `source` names another
repository — editing it locally is pointless: `npx skills update` overwrites the
change and no other consumer ever sees it. Make the change at the source, or
open an issue there. `ids-meetup-oslo-26` has such a lockfile with four
installed skills, so this is a live hazard rather than a hypothetical one.

**4. Run `python3 scripts/check-skills.py` before committing a skill change**,
and `--deep` after a round of fixes. It encodes the checks that kept being done
by hand: frontmatter shape, the 300-line gate, relative links, JSON and Python
blocks, and each skill's `scripts/selftest.sh`. A selftest exists to run a
skill's worked examples **against the fixtures the skill documents** — not
against fixtures written for the test, which is how an emitter that crashed on
its own token file passed review.

Neither catches the other class: an instruction that runs fine and leads
somewhere bad. That needs a fresh session with the skill installed, working
through its representative requests with no memory of having written it. Both
defects found that way — the crashing emitter and the venv landing inside the
installed package — survived every re-reading. Reports go in `docs/feedback/`.

**What we deliberately do not adopt from that repo.** Its section structure
(`When to use` / `When not to use` / `Required inputs` / …) and its richer
frontmatter
(`license`, `compatibility`, `metadata.version`/`status`/`owner`) belong to a
catalog governance model with releases and ownership that this repo has not
taken on. Ours stay at two frontmatter keys and the section shape described
above. Do not reformat existing skills to match Fusion's conventions without
that being an explicit, repo-wide decision.

## Spelling: Oxford English in prose, US English in code

Equinor writes Oxford English, so documentation, headings, descriptions and
skill names use **colour**, **behaviour**, **normalise**. Code keeps US
spelling, because the languages do: `color`, `background-color`, `--eds-color-*`,
`colorSpace`. So `skills/colour-contrast/SKILL.md` is correct, and every CSS
property and token name inside it is spelled `color`. Do not "fix" either side
into the other.

## Editorial stance in existing skills

Two positions run through the published content and should be preserved in new skills:

- **Verify, don't recall.** Skills instruct the agent to check browser support live against caniuse's `features-json` endpoint or webstatus.dev rather than answer from training data, on the explicit grounds that the model has a cutoff and the web does not. Any factual claim with a shelf life should get the same treatment.
- **Modern CSS, deliberately.** Prefer the newer feature when it states intent better (`:has()`, `:where()`, `@layer`, logical properties, nesting) — but pair it with support verification and a fallback, never a blanket recommendation.

## Browser target: evergreen, and say so

Skills here recommend modern CSS on the basis that a feature is **Baseline
available**, not that it is universally supported. The products this material
comes from run on centrally managed browsers that update within weeks of an
upstream Chromium release, with iOS Safari as the mobile target and Firefox
supported on a best-effort basis rather than as strategy.

Two consequences when authoring:

- **Baseline *newly* is not an automatic veto.** Treat it as a question for the
  consuming project's matrix (`browserslist`, `.browserslistrc`, build
  targets), not as a rule that every modern feature must ship a fallback. A
  skill that hedges everything is no more useful than one that hedges nothing.
- **Global usage percentages are context, not a gate.** They are market-share
  weighted and lag interop, so a feature can be Baseline widely and still sit
  below 95% — `:has()` and CSS nesting both do. Where the two measures
  disagree, Baseline governs.

Backward compatibility is the consuming project's responsibility, and the
README says so. Do not silently assume a long-tail matrix on a reader's behalf.

**Keep the published description generic; put the concrete matrix in a
`browserslist` config.** This repo is public, so prose here reaches anyone. It
also cannot be checked by a tool, cannot be versioned against a product, and
goes stale silently. A `.browserslistrc` in the product repo is the opposite on
every count — machine-readable, already read by the build, and specific to the
product it governs. So skills describe the *shape* of the target and tell a
reader how to find or declare their own; they do not enumerate a fleet.

## Installation surfaces to keep working

One path is advertised, and changes to repository layout can break it:

```bash
npx skills add equinor/skills --skill <skill-name>   # agentskills.io standard
```

The Claude Code plugin marketplace path (`/plugin marketplace add equinor/skills`)
was removed from the README because it needs a `.claude-plugin/marketplace.json`
that does not exist. Do not re-add it to the README without adding that file —
an advertised path that fails costs a review remark every time someone checks.

## Reviewing pull requests

Skills are derived from Equinor Design System conventions at the time of
writing — this repo doesn't promise to track every later EDS change, and a
skill isn't wrong just because EDS's colour or typography conventions have
since moved on. When eds.equinor.com and a skill diverge, note it as an
informational aside at the end of a review, clearly separated from
actionable findings — never as a blocking issue.

Otherwise, flag: secrets or internal, non-public Equinor URLs in examples;
missing or broken links; a skill with no worked example.
