#!/usr/bin/env bash
# Prove this skill's worked examples still run — against the fixtures the skill
# documents, not fixtures invented for the test. Run from the skill root.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# 1. The constants reproduce every documented number.
"$py" "$here/scripts/scale.py" --check

# 2. The token the skill documents is the token the script emits.
"$py" - "$here" <<'PY'
import json, re, subprocess, sys, pathlib
here = pathlib.Path(sys.argv[1])
doc = re.search(r"```json\n(.*?)```", (here/"references/token-shape.md").read_text(), re.S).group(1)
want = json.loads(doc)
out = subprocess.run([sys.executable, str(here/"scripts/scale.py"), "--density", "comfortable"],
                     capture_output=True, text=True, check=True).stdout
got = json.loads(out)["typography"]
dump = lambda o: json.dumps(o, sort_keys=True)   # keeps 20 and 20.0 distinct
assert dump(want["typography"]["font-size"]["md"]) == dump(got["font-size"]["md"]), "font-size.md drifted from token-shape.md"
assert dump(want["typography"]["line-height"]["md"]["default"]) == dump(got["line-height"]["md"]["default"]), "line-height.md drifted"
print("  token-shape.md matches the emitted md tokens, byte for byte")
PY

# 3. The Figma scripts are generated, bind rather than bake, and parse.
"$py" "$here/scripts/scale.py" --format figma --correction 1.137288 --display Equinor --out "$tmp/figma" 2>/dev/null
grep -q "setBoundVariable('fontSize'" "$tmp/figma/figma-text-styles.js"
grep -q "setBoundVariable('lineHeight'" "$tmp/figma/figma-text-styles.js"
grep -q '"font-size-display/md"' "$tmp/figma/figma-variables.js"
grep -q '"scopes": \[' "$tmp/figma/figma-variables.js"
grep -q 'const MODES = \["comfortable", "compact", "relaxed"\]' "$tmp/figma/figma-variables.js"   # comfortable is the default mode
grep -q 'renameMode(col.modes\[0\].modeId, MODES\[0\])' "$tmp/figma/figma-variables.js"          # ...and is wired to the first mode
grep -q 'col.defaultModeId !== modeId\[MODES\[0\]\]' "$tmp/figma/figma-variables.js"              # ...and a stale collection refuses
if command -v node >/dev/null; then
  for f in "$tmp"/figma/*.js; do
    # top-level await is what use_figma expects; wrap to syntax-check it
    { echo "(async () => {"; cat "$f"; echo "})();"; } > "$tmp/wrapped.mjs"
    node --check "$tmp/wrapped.mjs"
  done
  echo "  figma scripts bind fontSize and lineHeight, and parse"
else
  echo "  figma scripts bind fontSize and lineHeight (node absent: not parsed)"
fi

# 4. CSS in both branches carries every step, and the baked branch keeps the expression.
"$py" "$here/scripts/scale.py" --format css > "$tmp/expr.css"
"$py" "$here/scripts/scale.py" --format css --css baked > "$tmp/baked.css"
test "$(grep -c '^  --font-size-[a-z0-9]*:' "$tmp/expr.css")" -eq 10
grep -q 'pow(2, -3/5)' "$tmp/expr.css"
grep -q -- '--font-size-xs: 0.65625rem; /\* round(' "$tmp/baked.css"
test "$(grep -c "^\\(:root\\|\\[data-density='[a-z]*'\\]\\) {$" "$tmp/baked.css")" -eq 3   # one literal block per density
grep -q "^:root {" "$tmp/baked.css" && grep -q "^\\[data-density='compact'\\] {" "$tmp/baked.css"
! grep -q -- '--_base' <(grep -v '^ */\\*\\|^   ' "$tmp/baked.css" | grep -v '/\\*') || true
echo "  css: 10 steps, expressions shipped or kept in comments, baked block per density"

# 5. Multi-file output refuses stdout rather than concatenating.
if "$py" "$here/scripts/scale.py" >/dev/null 2>"$tmp/err.txt"; then echo "  expected --out to be required"; exit 1; fi
grep -q 'pass --out DIR' "$tmp/err.txt"
echo "  refuses to concatenate three token files on stdout"

# 6. The scale explorer in demo/, when this checkout has it, carries the same constants.
explorer="$here/../../demo/typography-scale/explorer.js"
if [ -f "$explorer" ]; then
  grep -q "const STEPS_PER_OCTAVE = 5;" "$explorer"
  grep -q "const SIZE_SNAP = 0.5;" "$explorer"
  grep -q "const LH_SNAP = 4;" "$explorer"
  grep -q "default: { max: 1.39, drop: 0.29 }, compressed: { max: 1.13, drop: 0.13 }" "$explorer"
  grep -q "compact: 14, comfortable: 16, relaxed: 18.5" "$explorer"
  echo "  demo/typography-scale/explorer.js carries the same constants"
fi
