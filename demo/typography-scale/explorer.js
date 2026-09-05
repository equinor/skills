// Scale explorer — the same constants and the same arithmetic as
// typography-scale/scripts/scale.py, in the browser, one step at a time.
const STEPS = ['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl'];
const BASE_STEP = 3;                 // lg is the base
const STEPS_PER_OCTAVE = 5;
const SIZE_SNAP = 0.5;               // px, at a 16px root
const LH_SNAP = 4;
const CURVES = { default: { max: 1.39, drop: 0.29 }, compressed: { max: 1.13, drop: 0.13 } };
const DENSITIES = { compact: 14, comfortable: 16, relaxed: 18.5 };   // base, px

// CSS round(nearest): halfway goes up. JS Math.round does the same for positives.
const cssRound = (v, step) => Math.round(v / step) * step;
const clean = (n) => Math.round(n * 1e6) / 1e6;

function size(basePx, i) { return clean(cssRound(basePx * 2 ** ((i - BASE_STEP) / STEPS_PER_OCTAVE), SIZE_SNAP)); }
function multiplier(i, curve) { const { max, drop } = CURVES[curve]; return max - (i / (STEPS.length - 1)) ** 3 * drop; }
function lineHeight(px, i, curve, snap = true) { const raw = px * multiplier(i, curve); return clean(snap ? cssRound(raw, LH_SNAP) : raw); }

const $ = (id) => document.getElementById(id);
const stepInput = $('step');
const preview = $('preview');
const sample = $('sample');
const state = { i: 3, curve: 'default', density: 'comfortable', snap: true };

// ticks
const ticks = $('ticks');
STEPS.forEach((s, i) => { const li = document.createElement('li'); li.textContent = s; li.dataset.i = i; li.style.setProperty('--i', i); ticks.append(li); });

function fmt(n, d = 2) { return Number.isInteger(n) ? String(n) : n.toFixed(d).replace(/\.?0+$/, ''); }

function render() {
  const base = DENSITIES[state.density];
  const i = state.i, s = STEPS[i];
  const px = size(base, i);
  const m = multiplier(i, state.curve);
  const lh = lineHeight(px, i, state.curve, state.snap);
  const raw = px * m;

  $('step-label').textContent = `${s} · ${fmt(px)}px`;
  ticks.querySelectorAll('li').forEach((li) => li.toggleAttribute('aria-current', Number(li.dataset.i) === i));

  sample.style.fontSize = `${px}px`;
  sample.style.lineHeight = `${lh}px`;

  $('t-size').textContent = `${fmt(px)}px`;
  $('t-size-note').textContent = `i = ${i - BASE_STEP}: base × 2^(${i - BASE_STEP}/5)`;
  $('t-lh').textContent = `${fmt(lh)}px`;
  $('t-lh-note').textContent = `${fmt(lh / px * 100, 1)}% of the size`;
  $('t-mult').textContent = fmt(m, 4);
  $('t-mult-note').textContent = `${state.curve}: ${CURVES[state.curve].max} − ${CURVES[state.curve].drop} × (${i}/9)³${state.snap ? ', before the 4px snap' : ', no snap'}`;

  const rows = [
    ['base', `${fmt(base)}px <small>(${state.density})</small>`],
    ['size', `round(${fmt(base)} × 2^(${i - BASE_STEP}/5), 0.5px) = round(${fmt(base * 2 ** ((i - BASE_STEP) / 5), 3)}, 0.5) = <b>${fmt(px)}px</b>`],
    ['multiplier', `${CURVES[state.curve].max} − (${i}/9)³ × ${CURVES[state.curve].drop} = ${CURVES[state.curve].max} − ${fmt((i / 9) ** 3, 4)} × ${CURVES[state.curve].drop} = <b>${fmt(m, 4)}</b>`],
    ['line-height', state.snap
      ? `round(${fmt(px)} × ${fmt(m, 4)}, 4px) = round(${fmt(raw, 2)}, 4) = <b>${lh}px</b>`
      : `${fmt(px)} × ${fmt(m, 4)} = <b>${fmt(lh)}px</b> — not on the grid`],
    ['ratio', state.snap
      ? `${lh} / ${fmt(px)} = <b>${fmt(lh / px * 100, 1)}%</b> — the grid is the invariant, the ratio is derived`
      : `${fmt(lh)} / ${fmt(px)} = <b>${fmt(lh / px * 100, 1)}%</b> — the curve itself, smooth and off-grid`],
  ];
  $('breakdown').innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('');

  $('table-density').textContent = state.density;
  const tbody = document.querySelector('#table tbody');
  tbody.innerHTML = STEPS.map((name, k) => {
    const p = size(base, k), d = lineHeight(p, k, 'default', state.snap), c = lineHeight(p, k, 'compressed', state.snap);
    return `<tr${k === i ? ' aria-current="true"' : ''}><td>${name}</td><td>${k - BASE_STEP}</td><td>${fmt(p)}px</td><td>${fmt(d)}px</td><td>${fmt(d / p * 100, 1)}%</td><td>${fmt(c)}px</td><td>${fmt(c / p * 100, 1)}%</td></tr>`;
  }).join('');
}

stepInput.addEventListener('input', () => { state.i = Number(stepInput.value); render(); });
document.querySelectorAll('input[name="curve"]').forEach((r) => r.addEventListener('change', () => { state.curve = r.value; render(); }));
document.querySelectorAll('input[name="density"]').forEach((r) => r.addEventListener('change', () => { state.density = r.value; render(); }));
$('guides').addEventListener('change', (e) => { preview.dataset.guides = e.target.checked ? 'on' : 'off'; });
$('snap').addEventListener('change', (e) => { state.snap = e.target.checked; render(); });
ticks.addEventListener('click', (e) => { const li = e.target.closest('li'); if (li) { state.i = Number(li.dataset.i); stepInput.value = state.i; render(); } });
render();
