# Emitting `@font-face` from the correction token

The CSS-only delivery path from section 4 of `SKILL.md`. The point is that the
percentage is produced by the build from the token, never typed by a person.

The percentage must be **written by the generator**, not by a person:

```js
// emit-font-faces.js — reads the token file, writes the stylesheet
const t = JSON.parse(readFileSync('tokens/typography.tokens.json', 'utf8'))
const corrections = t.typography['x-height-correction']

for (const [family, token] of Object.entries(corrections)) {
  const ext = token.$extensions?.['com.equinor.typography']
  const pct = +(token.$value * 100).toFixed(4)
  out.push(`@font-face {
  font-family: '${ext.metrics.family}';
  src: url('${ext.metrics.source}') format('woff2');${
    token.$value === 1 ? '' : `
  /* generated from ${ext.metrics.method}, extracted ${ext.metrics.extractedAt} */
  size-adjust: ${pct}%;`}
}`)
}
```

```css
/* Generated — do not edit. Source: tokens/typography.tokens.json */
@font-face {
  font-family: 'Equinor';
  src: url('https://cdn.example.com/font/EquinorVariable-VF.woff2') format('woff2');
  /* generated from OS/2.sxHeight, extracted 2026-08-29 */
  size-adjust: 113.7288%;
}
```

