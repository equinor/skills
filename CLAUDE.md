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
.github/workflows/claude.yml       @claude bot, gated to write-access collaborators
```

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
description: Use when …      # trigger conditions first, then what the skill covers
---
```

The `description` is the only thing an agent sees before deciding to load the skill, so it must lead with *when to use this* — not a topic label. Body is prose + fenced examples, hard-wrapped around 78 columns, `##`-numbered top-level sections.

Work on a new skill happens on a `skill/<skill-name>` branch (see `origin/skill/css-authoring` for the reference draft, which establishes the house style: a named core pattern first, then supporting practice, then discipline/anti-patterns).

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

## Installation surfaces to keep working

The README advertises two install paths, and changes to repository layout can break either:

```bash
npx skills add equinor/skills --skill <skill-name>   # agentskills.io standard
/plugin marketplace add equinor/skills               # Claude Code plugin marketplace
/plugin install <skill-name>@equinor-skills
```

## Reviewing pull requests

Skills are derived from Equinor Design System conventions at the time of
writing — this repo doesn't promise to track every later EDS change, and a
skill isn't wrong just because EDS's colour or typography conventions have
since moved on. When eds.equinor.com and a skill diverge, note it as an
informational aside at the end of a review, clearly separated from
actionable findings — never as a blocking issue.

Otherwise, flag: secrets or internal, non-public Equinor URLs in examples;
missing or broken links; a skill with no worked example.
