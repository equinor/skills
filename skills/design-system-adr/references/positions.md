# Positions this skill takes

Each rests on something observed in a real record directory rather than on
preference. The format itself is the EDS team's; these are the points where the
skill insists, because leaving them optional is how they were lost.

## 1. An accepted record is immutable; decisions supersede, they do not edit

The one permitted edit is the Status line, to point at the successor. The
cost of the rule is a second file for what feels like a small change. The
cost of not having it: a fifteen-record directory where one record's date
line reads as a four-entry revision log and its consequences are prose, so a
reader can no longer tell which decision was made when, or which text was
reviewed. Partial supersession keeps `Accepted` and scopes the note, so a
record that is mostly current is not marked dead.

## 2. Consequences are not the pros restated

MADR's `Good, because` / `Bad, because` bullets are what happens *after*
deciding: what the team does differently, what migrates, what gets harder.
The options' pros and cons are the arguments *before*. Collapsing the two
produces a record that argues for itself twice and never says what it costs.
`adr.py check` warns when no consequence is bad; every decision costs
something, and a record that lists none has not finished thinking.

## 3. Numbers are claimed by the pull request, gaps are kept, nothing is renumbered

Computed against the directory and open pull requests, not the directory
alone. Evidence: two duplicated numbers in a public directory, both from
parallel pull requests that each took "the next one". Renumbering after the
fact breaks every inbound link for a cosmetic gain, so both records keep the
number and the index disambiguates. A closed-unmerged pull request leaves a
gap, recorded as `Unused` so it is not mistaken for a lost file.

## 4. The directory carries an index

Without one, status is only visible by opening every record, and a partial
supersession is invisible from the listing. The index is generated from the
files (`adr.py index --write`), never edited by hand, and updated in the same
pull request as the record. The linter fails on a record the index does not
list.

## 5. Rejected options get fair treatment, and there are at least two

An option with no pros was not considered; it was set up to lose. A record
with one option was not a decision. The linter fails on either, because both
are how a decision memo gets dressed as a record.

## 6. The status vocabulary is closed

`Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by …`. A
synonym (`Approved` has appeared) is not a style choice: it breaks the index,
any search, and the reader's confidence that the word means what the
template says it means.

## 7. Public by default

Decisions about components, tokens, APIs, tooling and processes are public
records. Only sensitive content — security details, internal infrastructure —
goes to an internal repository. The skill asks before writing, because the
answer changes where the file goes, not how it is written.
