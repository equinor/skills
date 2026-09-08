#!/usr/bin/env bash
# Prove this skill's worked examples still run against the fixtures it documents.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

"$py" "$here/scripts/spacing.py" check

"$py" "$here/scripts/spacing.py" tokens --out "$tmp/tokens" 2>/dev/null
"$py" - "$here" "$tmp/tokens" <<'PY'
import json, re, sys, pathlib
here, tok = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
doc = json.loads(re.search(r"```json\n(.*?)```", (here/"references/token-shape.md").read_text(), re.S).group(1))["spacing"]
got = json.load(open(tok/"spacing.comfortable.tokens.json"))["spacing"]
dump = lambda o: json.dumps(o, sort_keys=True)
assert dump(doc["ladder"]["md"]) == dump(got["ladder"]["md"]), "ladder.md drifted from token-shape.md"
assert dump(doc["inset"]["md"]) == dump(got["inset"]["md"]), "inset.md drifted"
assert dump(doc["optical-padding"]["md-squished"]) == dump(got["optical-padding"]["md-squished"]), "optical-padding.md-squished drifted"
assert dump(doc["sizing-icon"]["md"]) == dump(got["sizing-icon"]["md"]), "sizing-icon.md drifted from token-shape.md"
rel = json.load(open(tok/"spacing.relaxed.tokens.json"))["spacing"]["ladder"]["3xl"]
assert rel["$extensions"]["com.equinor.spacing"].get("extrapolated") is True, "relaxed 3xl not flagged extrapolated"
print("  token-shape.md matches the emitted comfortable tokens; relaxed 3xl is flagged extrapolated")
PY

"$py" "$here/scripts/spacing.py" css > "$tmp/spacing.css"
grep -q -- '--spacing-md: 16px;' "$tmp/spacing.css"
grep -q -- '--inset-md-vertical-squished: var(--spacing-sm);' "$tmp/spacing.css"
grep -q -- '--optical-padding-md-squished: calc(var(--inset-md-vertical-squished) - var(--half-leading-md));' "$tmp/spacing.css"
grep -q -- '--optical-padding-sm-squished:' "$tmp/spacing.css"      # every size, not only md
grep -q -- '--icon-gap-md: round(' "$tmp/spacing.css"
grep -q -- '--sizing-icon-md: 20px;' "$tmp/spacing.css"
grep -q -- '--glyph-margin-md: calc((var(--cap-rounded-md) - var(--sizing-icon-md)) / 2);' "$tmp/spacing.css"
grep -q -- '--glyph-margin-2xl: calc((var(--cap-rounded-2xl) - var(--sizing-icon-2xl)) / 2);' "$tmp/spacing.css"   # every icon step, not only inset sizes
grep -q -- '--cap-rounded-2xl: round(' "$tmp/spacing.css"
# :root must precede the [data-density] blocks: equal specificity, source order decides
test "$(grep -E "^(:root|\[data-density=)" "$tmp/spacing.css" | head -1)" = ":root {"
echo "  css carries the ladder per density with :root first, every size's optical padding, the icon gap and the glyph seat"

"$py" "$here/scripts/spacing.py" css --css baked > "$tmp/baked.css"
grep -q -- '--optical-padding-md-squished: 10px; /\* inset' "$tmp/baked.css"
grep -q -- "^\[data-density='compact'\] {" "$tmp/baked.css"
grep -q -- '--optical-padding-md-squished: 6px;' "$tmp/baked.css"
grep -q -- '--glyph-margin-md: -4px; /\* (cap 12 − glyph 20) / 2, label and icon both md' "$tmp/baked.css"
echo "  baked css resolves the optical values per density with the expression in comments"

"$py" - "$tmp/tokens" <<'PY'
import json, sys, pathlib
tok = pathlib.Path(sys.argv[1])
g = json.load(open(tok/"spacing.comfortable.tokens.json"))["spacing"]["icon-gap"]
assert g["md"]["$value"]["value"] == 8, g["md"]
i = json.load(open(tok/"spacing.comfortable.tokens.json"))["spacing"]["sizing-icon"]
assert i["md"]["$value"]["value"] == 20, i["md"]
assert json.load(open(tok/"spacing.relaxed.tokens.json"))["spacing"]["sizing-icon"]["6xl"]["$extensions"]["com.equinor.spacing"].get("extrapolated") is True
print("  icon-gap md is 8; sizing-icon md is 20 and relaxed 6xl is flagged extrapolated")
PY

# the glyph seat the skill documents: md/md comfortable is a 20px glyph in a 12px cap cell, margin -4
"$py" - "$here" <<'PY'
import json, subprocess, sys, pathlib
here = pathlib.Path(sys.argv[1])
g = json.loads(subprocess.check_output([sys.executable, here/"scripts/spacing.py", "glyph", "--label", "md", "--icon", "md", "--density", "comfortable"]))[0]
assert (g["footprint"], g["glyph"], g["margin"]) == (12, 20, -4), g
c = json.loads(subprocess.check_output([sys.executable, here/"scripts/spacing.py", "control", "--icon", "md", "--density", "comfortable"]))[0]
assert c["glyph"]["margin"] == -4 and c["height"] == 36, c
print("  glyph seat: md glyph in the md label's cap cell is 20px with margin -4, inside the 36px button")
PY
