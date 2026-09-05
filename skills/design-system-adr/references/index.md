# The index

Referenced from section 5 of `SKILL.md`. A directory of records carries a
`README.md` so that status is visible without opening every file, and so that
a gap in the numbering can be told from a lost record. `scripts/adr.py index
--write` regenerates it from the files; it is never edited by hand.

```markdown
# Architecture Decision Records

Decisions follow the format in [0000-template.md](0000-template.md). See ADR-0001 for
when to write one, the numbering rule and the status lifecycle. One row per record,
regenerated with `adr.py index --write`; a number with no record is a PR that closed
unmerged, kept so a gap is distinguishable from a lost file.

| ADR | Title | Status | Date |
| --- | --- | --- | --- |
| [0001](0001-use-adr-for-architecture-decisions.md) | Use ADR for architecture decisions | Accepted | 2026-02-02 |
| [0002](0002-use-vanilla-css-with-design-tokens.md) | Use vanilla CSS with design tokens | Accepted (CSS naming superseded by [ADR 0006](0006-flat-class-names.md)) | 2026-02-02 |
| 0003 | — | Unused | — |
| [0004](0004-component-conventions.md) | Component conventions | Accepted | 2026-03-10 |
```

## Rules

- **One row per record, in number order, newest last.** The Status column is
  the record's own status line, verbatim, so a partial supersession reads the
  same in both places.
- **Gaps are rows.** `Unused` with no link says a pull request claimed the
  number and closed without merging. Deleting the row would make the gap look
  like a lost file.
- **Duplicates stay.** When two records share a number (it has happened), both
  get a row; the title tells them apart. Renumbering breaks every inbound link.
- **Updated in the same pull request** as the record it describes, including
  the old record's row when a new one supersedes it. `adr.py check` fails when
  a record is missing from the index or the index links to a file that is gone.
