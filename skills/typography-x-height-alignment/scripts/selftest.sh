#!/usr/bin/env bash
# Prove this skill's worked examples still run — against the fixtures the skill
# documents, not against fixtures invented for the test. Run from the skill root.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# Fail loudly on a missing dependency rather than dying inside a redirect.
"$py" -c 'import fontTools, brotli' 2>/dev/null || {
  echo "  SKIP: $py has no fonttools/brotli." >&2
  echo "  Point PYTHON at one that does — a venv at the project root, not here:" >&2
  echo "    (cd <project> && python3 -m venv .venv && .venv/bin/pip install fonttools brotli)" >&2
  echo "    PYTHON=<project>/.venv/bin/python bash scripts/selftest.sh" >&2
  exit 2
}
command -v node >/dev/null || { echo "  SKIP: node not found (the emitter check needs it)" >&2; exit 2; }

# 1. The extractor runs with no arguments and reproduces the published figures.
"$py" "$here/scripts/xheight.py" > "$tmp/out.json" 2>"$tmp/err.txt" \
  || { echo "  xheight.py failed:"; cat "$tmp/err.txt"; exit 1; }
"$py" - "$tmp/out.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
ref, sec = d["fonts"]
assert ref["family"] == "Inter", ref["family"]
assert ref["xRatio"] == 0.545898, ref["xRatio"]
assert sec["xRatio"] == 0.4, sec["xRatio"]
assert sec["correction"] == 1.364746, sec["correction"]
assert sec["instance"] == {"wght": 400.0}, sec["instance"]
assert sec["method"] == "OS/2.sxHeight", sec["method"]
print("  demo pair reproduces 1.364746 @ wght 400")
PY

# 2. The @font-face emitter runs against the token file this skill documents.
"$py" - "$here" "$tmp" <<'PY'
import re, sys, json, pathlib
here, tmp = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
tok = re.search(r"```json\n(.*?)```", (here/"references/token-shape.md").read_text(), re.S).group(1)
json.loads(tok)
(tmp/"tok.json").write_text(tok)
js = re.search(r"```js\n(.*?)```", (here/"references/emit-font-faces.md").read_text(), re.S).group(1)
js = js.replace("'tokens/typography.tokens.json'", f"'{tmp/'tok.json'}'")
(tmp/"emit.mjs").write_text("import {readFileSync} from 'node:fs'\nconst out=[]\n"+js+"\nconsole.log(out.join('\\n'))\n")
PY
node "$tmp/emit.mjs" > "$tmp/out.css"
grep -q "size-adjust: 113.7288%" "$tmp/out.css"
grep -q "font-family: 'Inter'" "$tmp/out.css"
test "$(grep -c '@font-face' "$tmp/out.css")" -eq 2
echo "  emitter runs against references/token-shape.md and emits both faces"

# 3. The bundled fonts are the ones the metrics were taken from.
(cd "$here/assets/fonts" && shasum -a 256 -c SHA256SUMS >/dev/null)
echo "  bundled fonts match SHA256SUMS"
