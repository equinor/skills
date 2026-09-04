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
assert want["typography"]["font-size"]["md"] == got["font-size"]["md"], "font-size.md drifted from token-shape.md"
assert want["typography"]["line-height"]["md"]["default"] == got["line-height"]["md"]["default"], "line-height.md drifted"
print("  token-shape.md matches the emitted md tokens")
PY

# 3. The Figma scripts are generated, bind rather than bake, and parse.
"$py" "$here/scripts/scale.py" --format figma --correction 1.137288 --display Equinor --out "$tmp/figma" 2>/dev/null
grep -q "setBoundVariable('fontSize'" "$tmp/figma/figma-text-styles.js"
grep -q "setBoundVariable('lineHeight'" "$tmp/figma/figma-text-styles.js"
grep -q '"font-size-display/md"' "$tmp/figma/figma-variables.js"
grep -q '"scopes": \[' "$tmp/figma/figma-variables.js"
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
echo "  css: 10 steps, expressions shipped or kept in comments"
