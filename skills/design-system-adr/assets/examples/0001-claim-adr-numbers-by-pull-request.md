# Claim ADR numbers by pull request, allow gaps, never renumber

- **Status:** Accepted
- **Date:** 2026-09-05
- **Decision makers:** equinor/skills authors

## Context

Architecture Decision Records are numbered sequentially and hand-copied from a
template. Two people opening pull requests in the same week each take "the next
number", and the directory ends up with two records sharing it. Renumbering one
of them later breaks every link that already points at it, in other records,
issues and chat. A public directory of fifteen records has two such pairs.

## Decision Drivers

- A number, once published, must keep pointing at the same decision
- Two contributors must be able to draft records in parallel
- A reader must be able to tell a gap from a lost record

## Options Considered

### Option 1: Next number is one more than the highest in the directory

The rule everyone assumes; it needs no coordination.

**Pros:**

- Nothing to look up beyond `ls`

**Cons:**

- Two open pull requests both compute the same number
- Collisions are found at merge, when both authors have linked the number

### Option 2: Claim the number in the pull request, count open PRs, keep gaps

The next number is one more than the highest across the directory *and* open
pull requests that add a record. A closed-unmerged PR leaves its number unused,
recorded as such in the index.

**Pros:**

- Parallel drafting without collisions
- A published number is permanent, also for rejected records

**Cons:**

- Needs a look at open pull requests, by hand or with `gh`
- Gaps look like missing files until the index explains them

### Option 3: A central counter file bumped in every PR

**Pros:**

- Merge conflicts make a collision impossible

**Cons:**

- Every ADR PR conflicts with every other on one line
- The counter is another file to forget

## Decision

Option 2. The number is claimed by the pull request, computed against the
directory and open pull requests, and never reused or changed. When a
collision has already happened, both records keep their number and the index
disambiguates them; renumbering would break inbound links for a cosmetic gain.

### Consequences

- Good, because two contributors can draft in the same week without a race
- Good, because a number in an old issue still resolves to the same decision
- Bad, because the sequence has gaps, which the index has to explain
- Bad, because computing the next number takes one more step than `ls`

### Confirmation

- `adr.py check` fails on a duplicated number and warns when the index is
  missing
- `adr.py next --gh` computes the number across open pull requests

## Related

- [MADR](https://adr.github.io/madr/)
- [Michael Nygard, Documenting architecture decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
