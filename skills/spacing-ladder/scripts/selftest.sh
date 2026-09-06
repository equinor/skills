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
# :root must precede the [data-density] blocks: equal specificity, source order decides
test "$(grep -E "^(:root|\[data-density=)" "$tmp/spacing.css" | head -1)" = ":root {"
echo "  css carries the ladder per density with :root first, every size's optical padding, and the icon gap"

"$py" "$here/scripts/spacing.py" css --css baked > "$tmp/baked.css"
grep -q -- '--optical-padding-md-squished: 10px; /\* inset' "$tmp/baked.css"
grep -q -- "^\[data-density='compact'\] {" "$tmp/baked.css"
grep -q -- '--optical-padding-md-squished: 6px;' "$tmp/baked.css"
echo "  baked css resolves the optical values per density with the expression in comments"

"$py" - "$tmp/tokens" <<'PY'
import json, sys, pathlib
tok = pathlib.Path(sys.argv[1])
g = json.load(open(tok/"spacing.comfortable.tokens.json"))["spacing"]["icon-gap"]
assert g["md"]["$value"]["value"] == 8, g["md"]
print("  icon-gap tokens exist and md is 8")
PY
