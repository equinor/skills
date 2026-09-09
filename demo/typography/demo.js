// Typography demo — behaviour. Seven controls, four of them gated on another,
// one code panel showing the CSS the last request produced. Nothing here
// computes a typographic value: the numbers were emitted by the skills and
// are quoted, with the request that produced them.

const article = document.getElementById('article');
const codeEl = document.getElementById('code');
const titleEl = document.getElementById('code-title');
const stateEl = document.getElementById('code-state');
const inputs = Object.fromEntries(
  [...document.querySelectorAll('[data-control]')].map((el) => [el.dataset.control, el]),
);
const state = { guides: false, scale: false, baseline: false, swap: false, xheight: false, weight: false, tracking: false };
const seen = { swap: false };
const ORDER = ['guides', 'scale', 'baseline', 'swap', 'xheight', 'weight', 'tracking'];   // the telling order
// Honesty rule 1: the panel shows what is running. When a control goes off, fall
// back to the last control in the telling order that is still on — 'before' only
// when nothing is.
const lastApplied = () => [...ORDER].reverse().find((k) => state[k]) ?? 'before';

// Gates. baseline needs the scale (its line-heights are what land on the grid).
// xheight and weight unlock once the headings have been set in Equinor, and
// keep their state when Equinor is toggled off again — their effect is gated
// in the CSS on data-swap, so switching the face back and forth shows the fix.
const needs = { baseline: ['scale'] };

// typography-weight-matching, Inter → Equinor at the same perceived size, with
// Inter's opsz following the heading's px size and the x-height correction taken
// at that same opsz (Inter's x-height drifts with the axis; see INTENT §3).
// x-heights sampled 2026-09-07, stems 2026-09-08, with, per step:
//   xheight.py Inter.woff2 --location wght=400,opsz=<px>          → correction = xRatio / 0.48
//   stem.py Inter.woff2 EquinorVariable-VF.woff2 --match 300,400,500 --opsz <px> --correction <that>
// Bolder tier, Inter 500 (the EDS rework's bolder tier; 600 until 9 September): h1 5xl 32px, h2 3xl 24.5px, h3 2xl 21px.
// Browser-default headings are 700, which no weight on Equinor's 300–700 axis
// reaches: the skill reports null and the value holds at the axis maximum.
const matched = {
  scaleOn: { h1: 563.1, h2: 558.5, h3: 556.5 },
  scaleOff: { h1: 700, h2: 700, h3: 700 },
};
// typography-weight-matching §4, the spacing half: Inter's opsz axis tightens its
// side space (advance − ink, a–z) as the size grows; Equinor has no axis. The
// letter-spacing Equinor needs, in its own em, to leave Inter's gap at the same
// perceived size: sideSpace(Inter @ opsz) / correction − sideSpace(Equinor @ matched).
// Measured 2026-09-08 with, per step:
//   stem.py Inter.woff2 EquinorVariable-VF.woff2 --letter-spacing --at <tier>,<matched> --opsz <px> --correction <that step's> --px <px>
// Bolder tier: 5xl −0.0141em (−0.48px), 3xl −0.0065em (−0.18px), 2xl −0.0031em (−0.07px).
// Browser defaults (700 vs Equinor 700 clamped): 32px −0.0183em, 24px −0.0117em, 18.72px −0.0075em.
const tracked = {
  scaleOn: { h1: -0.0141, h2: -0.0065, h3: -0.0031 },
  scaleOff: { h1: -0.0183, h2: -0.0117, h3: -0.0075 },
};

const CODE = {
  before: {
    title: 'Before: browser defaults',
    state: 'nothing applied',
    css: `<span class="c">/* No stylesheet beyond the @font-face rules. Body is Inter
   at 16px; the headings are whatever the browser does when
   nobody decides. */</span>
h1 { font-size: 2em;    font-weight: bold; line-height: normal; }
h2 { font-size: 1.5em;  font-weight: bold; line-height: normal; }
h3 { font-size: 1.17em; font-weight: bold; line-height: normal; }`,
  },
  guides: {
    title: 'Show the 4px layout grid',
    state: 'pure CSS, on the surface',
    css: `<span class="c">/* Drawn on the container, inset by its padding, so grid and
   text share an origin. The padding is a multiple of 4. */</span>
.surface::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: repeating-linear-gradient(
    to bottom, var(--guide) 0, var(--guide) 1px, transparent 1px, transparent 4px);
}`,
  },
  scale: {
    title: 'Build a type scale based on the EDS scale',
    state: 'typography-scale · comfortable',
    css: `<span class="c">/* One base, one ratio, one snap. Sizes double every five steps. */</span>
:root {
  --_base: 1rem;
  --font-size-lg:  var(--_base);                                         <span class="c">/* 16px  */</span>
  --font-size-xl:  round(calc(var(--_base) * pow(2, 1/5)), 0.03125rem);  <span class="c">/* 18.5px */</span>
  --font-size-2xl: round(calc(var(--_base) * pow(2, 2/5)), 0.03125rem);  <span class="c">/* 21px  */</span>
  --font-size-3xl: round(calc(var(--_base) * pow(2, 3/5)), 0.03125rem);  <span class="c">/* 24.5px */</span>
  --font-size-5xl: round(calc(var(--_base) * pow(2, 5/5)), 0.03125rem);  <span class="c">/* 32px  */</span>
  <span class="c">/* Line-height is a curve indexed by step, snapped to the 4px grid. */</span>
  --line-height-lg:  round(calc(var(--font-size-lg)  * (1.39 - pow(3/9, 3) * 0.29)), 4px);  <span class="c">/* 24px */</span>
  --line-height-xl:  round(calc(var(--font-size-xl)  * (1.39 - pow(4/9, 3) * 0.29)), 4px);  <span class="c">/* 24px */</span>
  --line-height-2xl: round(calc(var(--font-size-2xl) * (1.39 - pow(5/9, 3) * 0.29)), 4px);  <span class="c">/* 28px */</span>
  --line-height-3xl: round(calc(var(--font-size-3xl) * (1.39 - pow(6/9, 3) * 0.29)), 4px);  <span class="c">/* 32px */</span>
  --line-height-5xl: round(calc(var(--font-size-5xl) * (1.39 - pow(8/9, 3) * 0.29)), 4px);  <span class="c">/* 36px */</span>
}
p  { font-size: var(--font-size-lg);  line-height: var(--line-height-lg); }
h1 { font-size: var(--font-size-5xl); line-height: var(--line-height-5xl); font-weight: 500; }
h2 { font-size: var(--font-size-3xl); line-height: var(--line-height-3xl); font-weight: 500; }
h3 { font-size: var(--font-size-2xl); line-height: var(--line-height-2xl); font-weight: 500; }
<span class="c">/* Space before each block, as in EDS: h1 40px, h2 32px, h3 24px, p 20px.
   Density is one number: [data-density='compact'] { --_base: 0.875rem; } */</span>`,
  },
  baseline: {
    title: 'Align the text to the baseline grid',
    state: 'text in flow snaps, headings included',
    css: `<span class="c">/* Trim the box to x-height and baseline, then pad the top up
   to the cap height rounded to 4px. The block ends on its last
   baseline, the first baseline sits a multiple of 4 from the
   top, and the flow margins are multiples of 4 — so every
   baseline lands on the grid, in both faces. */</span>
:root { --padding-top-baseline: calc(round(1cap, 4px) - 1ex); }
@supports (text-box: trim-both ex alphabetic) {
  :is(h1, h2, h3, p) {
    text-box: trim-both ex alphabetic;
    padding-top: var(--padding-top-baseline);
    padding-bottom: 0;
  }
}
<span class="c">/* 1cap and 1ex are the current font's, so this recomputes when
   the heading face swaps and when its size grows after the
   x-height correction. */</span>`,
  },
  swap: {
    title: 'Set the headings in Equinor',
    state: 'the problem',
    css: `<span class="c">/* The raw font file. No size-adjust, no weight correction:
   the same nominal size and weight as Inter, and it reads
   smaller and thinner. */</span>
@font-face {
  font-family: Equinor;
  src: url(…/EquinorVariable-VF.woff2) format("woff2-variations");
  font-weight: 300 700;   <span class="c">/* the file's wght axis */</span>
}
h1, h2, h3 { font-family: Equinor; }`,
  },
  xheight: {
    title: 'Align the x-height of Equinor and Inter, Inter is the master',
    state: 'typography-x-height-alignment',
    css: `<span class="c">/* Measured from the two files, not from a spec page — and Inter's
   x-height is one number per optical size, not per family:
   Inter   xRatio 0.545898 @ opsz 14 … 0.515625 @ opsz 32  (wght 400)
   Equinor xRatio 0.480000, flat along its axis
   correction at the text step = 0.545898 / 0.48 = <span class="n">1.137288</span> */</span>
<span class="c">/* 5.9% clears the tolerance: one correction per step, not one per
   family (x-height-alignment, optical-size.md, outcome 2) */</span>
<span class="k">"x-height-correction"</span>: { <span class="k">"display"</span>: {
  <span class="k">"$extensions"</span>: { <span class="k">"com.equinor.typography"</span>: { <span class="k">"drift"</span>: { <span class="k">"axis"</span>: "opsz",
    <span class="k">"sampledAt"</span>: [10.5, 12, 14, 16, 18.5, 21, 24.5, 28, 32, 37],
    <span class="k">"range"</span>: [<span class="n">1.074219</span>, <span class="n">1.137288</span>], <span class="k">"max"</span>: <span class="n">0.0587</span> } } },
  <span class="k">"2xl"</span>: { <span class="k">"$type"</span>: "number", <span class="k">"$value"</span>: <span class="n">1.112875</span>, <span class="k">"$extensions"</span>: { <span class="k">"com.equinor.typography"</span>: {
    <span class="k">"derived"</span>: { <span class="k">"expression"</span>: "referenceXRatio / selfXRatio", <span class="k">"inputs"</span>: { <span class="k">"referenceXRatio"</span>: <span class="n">0.534180</span>, <span class="k">"selfXRatio"</span>: <span class="n">0.48</span> } },
    <span class="k">"metrics"</span>: { <span class="k">"instance"</span>: { <span class="k">"opsz"</span>: <span class="n">21</span>, <span class="k">"wght"</span>: <span class="n">400</span> } } } } },
  <span class="k">"3xl"</span>: { <span class="k">"$value"</span>: <span class="n">1.100667</span>, … <span class="k">"instance"</span>: { <span class="k">"opsz"</span>: <span class="n">24.5</span> } },
  <span class="k">"5xl"</span>: { <span class="k">"$value"</span>: <span class="n">1.074219</span>, … <span class="k">"instance"</span>: { <span class="k">"opsz"</span>: <span class="n">32</span> } } } }
<span class="c">/* Two ramps: each display step baked with its own correction,
   re-snapped to the same 0.5px grid. Line-heights are shared. */</span>
:root {
  --font-size-display-2xl: round(calc(var(--font-size-2xl) * <span class="n">1.112875</span>), 0.03125rem); <span class="c">/* 23.5px · opsz 21   */</span>
  --font-size-display-3xl: round(calc(var(--font-size-3xl) * <span class="n">1.100667</span>), 0.03125rem); <span class="c">/* 27px   · opsz 24.5 */</span>
  --font-size-display-5xl: round(calc(var(--font-size-5xl) * <span class="n">1.074219</span>), 0.03125rem); <span class="c">/* 34.5px · opsz 32   */</span>
}
h1 { font-size: var(--font-size-display-5xl); }  <span class="c">/* 32   → 34.5 */</span>
h2 { font-size: var(--font-size-display-3xl); }  <span class="c">/* 24.5 → 27   */</span>
h3 { font-size: var(--font-size-display-2xl); }  <span class="c">/* 21   → 23.5 */</span>`,
    cssUnscaled: `<span class="c">/* Measured from the two files, not from a spec page:
   Inter   xRatio 0.545898 @ opsz 14 … 0.515625 @ opsz 32
   Equinor xRatio 0.480000, flat
   The correction is taken at each heading's own px, which is
   where Inter's opsz axis puts it. */</span>
<span class="c">/* No scale yet, so the browser's em sizes are multiplied as
   they are. With the scale on, the corrected sizes snap to the
   same half-pixel grid as the text ramp. */</span>
h1 { font-size: calc(2em    * <span class="n">1.074219</span>); }  <span class="c">/* 32px    · opsz 32    */</span>
h2 { font-size: calc(1.5em  * <span class="n">1.102702</span>); }  <span class="c">/* 24px    · opsz 24    */</span>
h3 { font-size: calc(1.17em * <span class="n">1.121012</span>); }  <span class="c">/* 18.72px · opsz 18.72 */</span>`,
  },
  weight: {
    title: 'Equinor looks lighter than Inter at the same weight. What should it be?',
    state: 'typography-weight-matching',
    css: `<span class="c">/* Stem width at the glyph midpoint, from the outlines, at the
   same perceived size — each step's own x-height correction
   applied. Inter's opsz axis thins its stems as the size grows
   and lowers its x-height, so Equinor is set smaller at the large
   steps and the bolder tier has to keep up. Bolder tier, Inter 500: */</span>
<span class="k">"font-weight"</span>: { <span class="k">"Equinor"</span>: { <span class="k">"bolder"</span>: {
  <span class="k">"xs"</span>–<span class="k">"md"</span>: <span class="n">552.7</span>,  <span class="k">"lg"</span>: <span class="n">553.9</span>,  <span class="k">"xl"</span>: <span class="n">554.9</span>,  <span class="k">"2xl"</span>: <span class="n">556.5</span>,
  <span class="k">"3xl"</span>: <span class="n">558.5</span>, <span class="k">"4xl"</span>: <span class="n">560.5</span>, <span class="k">"5xl"</span>–<span class="k">"6xl"</span>: <span class="n">563.1</span> } } }
h1 { font-weight: <span class="n">563.1</span>; }  <span class="c">/* 5xl · Inter 500 @ opsz 32   */</span>
h2 { font-weight: <span class="n">558.5</span>; }  <span class="c">/* 3xl · Inter 500 @ opsz 24.5 */</span>
h3 { font-weight: <span class="n">556.5</span>; }  <span class="c">/* 2xl · Inter 500 @ opsz 21   */</span>
<span class="c">/* Normal tier, Inter 400: 458.5 at every step — the thinner stem
   and the smaller size cancel. Lighter, Inter 300: 376.2 → 377.5. */</span>`,
    cssClamped: `<span class="c">/* Stem width at the glyph midpoint, from the outlines. The
   headings are at the browser's bold, 700. Inter 700 has a stem
   of 0.1464em; Equinor's axis stops at 700 with 0.1180em, so no
   weight on its axis matches. stem.py says:
   warning: tier 700 falls outside the target's weight axis (null)
   Holding at the axis maximum is this demo's choice, not the
   skill's. Apply the scale: EDS headings take the bolder tier,
   500, which Equinor can match. */</span>
h1, h2, h3 { font-weight: <span class="n">700</span>; } <span class="c">/* clamped — nothing changes */</span>`,
  },
  tracking: {
    title: "Inter tightens its letter-spacing at heading sizes. Equinor doesn't — match it.",
    state: 'typography-weight-matching · spacing',
    css: `<span class="c">/* Side space — advance minus ink, mean over a–z — at the same
   perceived size. Inter's opsz axis cuts its own by a quarter
   between 14px and 32px; Equinor has no axis, so at heading
   sizes it reads looser at the matched weight. In Equinor's em:
   sideSpace(Inter @ opsz) / correction − sideSpace(Equinor).
   Bolder tier, Inter 500 → Equinor at its matched weight: */</span>
<span class="k">"letter-spacing"</span>: { <span class="k">"Equinor"</span>: { <span class="k">"bolder"</span>: {
  <span class="k">"xs"</span>–<span class="k">"md"</span>: <span class="n">+0.0038</span>, <span class="k">"lg"</span>: <span class="n">+0.0019</span>, <span class="k">"xl"</span>: <span class="n">−0.0005</span>, <span class="k">"2xl"</span>: <span class="n">−0.0031</span>,
  <span class="k">"3xl"</span>: <span class="n">−0.0065</span>, <span class="k">"4xl"</span>: <span class="n">−0.0099</span>, <span class="k">"5xl"</span>–<span class="k">"6xl"</span>: <span class="n">−0.0141</span> } } }  <span class="c">/* em */</span>
h1 { letter-spacing: <span class="n">-0.0141em</span>; }  <span class="c">/* 5xl · 0.0718 / 1.074219 − 0.0808 · −0.48px at 34.5px */</span>
h2 { letter-spacing: <span class="n">-0.0065em</span>; }  <span class="c">/* 3xl · Inter 500 @ opsz 24.5 · −0.18px at 27px    */</span>
h3 { letter-spacing: <span class="n">-0.0031em</span>; }  <span class="c">/* 2xl · Inter 500 @ opsz 21   · −0.07px at 23.5px  */</span>
<span class="c">/* The text steps need none: the two faces agree within a tenth of
   a pixel at 14px. Normal tier: +0.0061 at md, −0.0139 at 5xl. */</span>`,
    cssClamped: `<span class="c">/* Side space — advance minus ink, mean over a–z — at the same
   perceived size. The headings are at the browser's bold, 700, and
   Equinor is held at its axis maximum, 700. Inter 700 at each
   heading's own opsz against Equinor 700, in Equinor's em: */</span>
h1 { letter-spacing: <span class="n">-0.0183em</span>; }  <span class="c">/* 32px    · opsz 32    · −0.63px */</span>
h2 { letter-spacing: <span class="n">-0.0117em</span>; }  <span class="c">/* 24px    · opsz 24    · −0.31px */</span>
h3 { letter-spacing: <span class="n">-0.0075em</span>; }  <span class="c">/* 18.72px · opsz 18.72 · −0.16px */</span>
<span class="c">/* Apply the scale and the values move with the matched weights. */</span>`,
  },
};

function render(key) {
  const entry = CODE[key];
  let css = entry.css;
  let stateText = entry.state;
  if ((key === 'weight' || key === 'tracking') && !state.scale) css = entry.cssClamped;
  if (key === 'xheight' && !state.scale) css = entry.cssUnscaled;
  if ((key === 'xheight' || key === 'weight' || key === 'tracking') && !state.swap) {
    // The fix is switched on but the headings are back in Inter: it has nothing
    // to act on until Equinor is on again. Say so rather than show CSS as if it ran.
    css = `<span class="c">/* Waiting. The headings are in Inter, so this correction has
   nothing to act on. Switch "Set the headings in Equinor" back on
   and it applies again — the comparison this pair of toggles is for. */</span>`;
    stateText = 'on, but the headings are in Inter';
  }
  titleEl.textContent = entry.title;
  stateEl.textContent = stateText;
  codeEl.innerHTML = `<code>${css}</code>`;
}

function applyWeight() {
  const set = state.scale ? matched.scaleOn : matched.scaleOff;
  const trk = state.scale ? tracked.scaleOn : tracked.scaleOff;
  for (const h of ['h1', 'h2', 'h3']) {
    article.style.setProperty(`--_${h}-matched`, String(set[h]));
    article.style.setProperty(`--_${h}-tracking`, String(trk[h]));
  }
}

function refreshGates() {
  for (const [key, deps] of Object.entries(needs)) {
    const ok = deps.every((d) => state[d]);
    inputs[key].disabled = !ok;
    if (!ok && state[key]) {             // a dependency went off: release the dependant too
      state[key] = false;
      inputs[key].checked = false;
      article.dataset[key] = 'off';
    }
  }
  if (state.swap) seen.swap = true;
  inputs.xheight.disabled = !seen.swap;   // unlocked by the first swap; state survives toggling it
  inputs.weight.disabled = !seen.swap;
  inputs.tracking.disabled = !seen.swap;
}

for (const [key, el] of Object.entries(inputs)) {
  el.addEventListener('change', () => {
    state[key] = el.checked;
    article.dataset[key] = el.checked ? 'on' : 'off';
    if (key === 'scale' || key === 'weight' || key === 'tracking') applyWeight();
    refreshGates();
    render(el.checked ? key : lastApplied());
  });
}
applyWeight();
render('before');

// Deep links for the talk: ?on=guides,scale,baseline,swap,xheight,weight,tracking — the
// telling order — applies the controls in that order. A key that cannot apply
// yet (its dependency is off) is reported rather than dropped silently.
const params = new URLSearchParams(location.search);
if (params.has('on')) {
  for (const key of params.get('on').split(',')) {
    const el = inputs[key];
    if (!el) { console.warn(`?on: unknown control "${key}"`); continue; }
    if (el.disabled) { console.warn(`?on: "${key}" needs its dependency on first; skipped`); continue; }
    el.checked = true;
    el.dispatchEvent(new Event('change'));
  }
  render(lastApplied());
}

// ?measure: prove the baseline claim. Applies scale, swap, x-height and
// weight (not tracking: letter-spacing cannot move a baseline), then reports
// each block's first baseline modulo 4 with the grid toggle off and on. On
// the grid means every remainder is 0.
if (params.has('measure')) {
  document.fonts.ready.then(() => {
    const rows = [];
    for (const k of ['scale', 'swap', 'xheight', 'weight']) { inputs[k].checked = true; inputs[k].dispatchEvent(new Event('change')); }
    const probe = (label) => {
      const top = article.getBoundingClientRect().top + parseFloat(getComputedStyle(article).paddingTop);
      article.querySelectorAll('h1, h2, h3, p').forEach((el, i) => {
        const s = document.createElement('span');
        s.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
        el.prepend(s);
        const b = s.getBoundingClientRect().bottom - top;
        s.remove();
        const cs = getComputedStyle(el);
        rows.push([label, el.tagName + i, cs.fontFamily.split(',')[0], cs.fontSize, cs.fontWeight, 'baseline', b.toFixed(2), 'mod4=' + (((b % 4) + 4) % 4).toFixed(2)].join('\t'));
      });
    };
    probe('baseline-off');
    inputs.baseline.checked = true; inputs.baseline.dispatchEvent(new Event('change'));
    probe('baseline-on');
    const pre = document.createElement('pre'); pre.id = 'measure';
    pre.textContent = 'MEASURE\n' + rows.join('\n');
    document.body.append(pre);
  });
}
