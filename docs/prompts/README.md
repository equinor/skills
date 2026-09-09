# Prompts

Example requests that span several skills, one per file, each with the
acceptance criteria a correct result meets. A skill's own requests live in its
`references/representative-requests.md`; these are the ones that need two or
more skills together, written the way a designer or developer would actually
ask.

| Prompt | Skills | Result |
| --- | --- | --- |
| [Set up the typography for a design system](typography-system.md) | `typography-scale`, `typography-x-height-alignment`, `typography-weight-matching` | [`demo/typography-tokens/`](../../demo/typography-tokens/) |

They double as the fresh-session tests the authoring gates in `CLAUDE.md` ask
for: install the skills into an empty folder, paste the prompt, and check the
result against the criteria without having read the skills.
