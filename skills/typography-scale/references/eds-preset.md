# The EDS preset

Referenced from `SKILL.md`. The constants for a scale built "based on the
Equinor Design System", with the comfortable ramp as a fixture to check a port
against.

These are the whole specification — everything else derives.

| Constant | Value |
| --- | --- |
| Ratio | `2` (octave) over `5` steps — `2^(1/5)` ≈ 1.1487 |
| Steps | `xs sm md lg xl 2xl 3xl 4xl 5xl 6xl` (ten), `lg` at the base → `i = labelIndex − 3` |
| Size snap | `0.03125rem` (0.5px) |
| Line-height curve, read | `max 1.39`, `drop 0.29` |
| Line-height curve, scanned | `max 1.13`, `drop 0.13` |
| Line-height snap | `4px` |
| Density (base) | `compact 0.875rem`, `comfortable 1rem`, `relaxed 1.15625rem` |

Comfortable, for checking an implementation — `size / line-height (read)`:

```
xs 10.5/16   sm 12/16   md 14/20   lg 16/24   xl 18.5/24
2xl 21/28   3xl 24.5/32   4xl 28/36   5xl 32/36   6xl 37/40
```

Reproduce these exactly before shipping a port: off by 0.5px means the snap is
wrong, off by 4px means the curve is indexed differently (section 3).

