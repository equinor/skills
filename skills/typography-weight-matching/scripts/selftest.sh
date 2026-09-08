#!/usr/bin/env bash
# Prove this skill's worked examples still run — against the fixture the skill
# documents (the bundled Inter), not fixtures invented for the test. Run from
# the skill root. Takes about half a minute: matching instances a variable font.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

"$py" -c 'import fontTools, brotli' 2>/dev/null || {
  echo "  SKIP: $py has no fonttools/brotli." >&2
  echo "  Point PYTHON at one that does — a venv at the project root, not here:" >&2
  echo "    (cd <project> && python3 -m venv .venv && .venv/bin/pip install fonttools brotli)" >&2
  echo "    PYTHON=<project>/.venv/bin/python bash scripts/selftest.sh" >&2
  exit 2
}
F="$here/assets/fonts/Inter.woff2"

# 1. The bundled font is the one the numbers were measured from.
(cd "$here/assets/fonts" && shasum -a 256 -c SHA256SUMS >/dev/null)
echo "  bundled Inter matches SHA256SUMS"

# 2. Stems, axis unevenness and the opsz effect reproduce the documented figures.
"$py" - "$here" <<'PY'
import sys, json, subprocess, pathlib
here = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(here / "scripts"))
import stem as S
F = str(here / "assets/fonts/Inter.woff2")
out = json.loads(subprocess.run([sys.executable, str(here/"scripts/stem.py"), F, "--weights", "300,400,500,700"],
                                capture_output=True, text=True, check=True).stdout)
assert out["stem"] == {"300": 0.066082, "400": 0.087891, "500": 0.107402, "700": 0.146423}, out["stem"]
g1 = out["stem"]["400"] / out["stem"]["300"] - 1; g2 = out["stem"]["500"] / out["stem"]["400"] - 1
assert abs(g1 - 0.330) < 0.001 and abs(g2 - 0.222) < 0.001, (g1, g2)          # SKILL.md §2: +33.0% / +22.2%
for w, want in ((300, -4.93), (400, -5.56), (700, -1.89)):                        # positions.md §4
    a = S.stem(S.at(F, {"wght": w, "opsz": 14})); b = S.stem(S.at(F, {"wght": w, "opsz": 32}))
    got = round((b / a - 1) * 100, 2)
    assert abs(got - want) <= 0.02, (w, got, want)
print("  stems 0.066082 / 0.087891 / 0.107402 / 0.146423; +33.0% then +22.2%; opsz thins -4.93 / -5.56 / -1.89%")
PY

# 3. Side space at 400 is the denominator the skill documents, and a self-pair ports at 1.0.
"$py" "$here/scripts/stem.py" "$F" "$F" --tracking --at 400,400 > "$tmp/trk.json"
"$py" - "$tmp/trk.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["reference"]["sideSpaceEm"] == 0.104154 and round(d["reference"]["sideSpaceShare"], 3) == 0.194, d["reference"]
assert d["portFactor"] == 1.0
print("  side space 0.104154em (19.4%) at 400; self-pair port factor 1.0")
PY

# 3b. The opsz axis tightens side space: Inter at 500 is 0.0967em at opsz 14 and 0.0718em at opsz 32 (SKILL.md §4),
#     so pinning the reference at 32 against the same face at its default gives the axis's own letter-spacing, −0.0249em.
"$py" "$here/scripts/stem.py" "$F" "$F" --letter-spacing --at 500,500 --opsz 32 --correction 1 > "$tmp/ls.json"
"$py" - "$tmp/ls.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert round(d["reference"]["sideSpaceEm"], 4) == 0.0718 and round(d["target"]["sideSpaceEm"], 4) == 0.0967, d
assert round(d["letterSpacingEm"], 4) == -0.0249, d["letterSpacingEm"]
print("  side space at 500: 0.0967em at opsz 14, 0.0718em at opsz 32; the axis alone is −0.0249em of letter-spacing")
PY

# 4. Matching a face against itself returns the tier back, and the documented tokens are the emitted tokens.
"$py" "$here/scripts/stem.py" "$F" "$F" --match 400 --format tokens --display Inter > "$tmp/tok.json"
"$py" "$here/scripts/stem.py" "$F" "$F" --tracking --at 400,400 --format tokens --display Inter > "$tmp/trktok.json"
"$py" "$here/scripts/stem.py" "$F" "$F" --letter-spacing --at 400,400 --opsz 32 --correction 1 --format tokens --display Inter > "$tmp/lstok.json"
"$py" - "$here" "$tmp/tok.json" "$tmp/trktok.json" "$tmp/lstok.json" <<'PY'
import json, re, sys, pathlib
here = pathlib.Path(sys.argv[1]); got = json.load(open(sys.argv[2]))
w = got["typography"]["font-weight"]["Inter"]["400"]["$value"]
assert abs(w - 400) <= 0.5, f"self-match returned {w}"
doc = json.loads(re.search(r"```json\n(.*?)```", (here/"references/token-shape.md").read_text(), re.S).group(1))
def norm(o):     # path varies with cwd and extractedAt with the day; the sha256 and every derived value must not
    if isinstance(o, dict):
        return {k: ("<path>" if k == "path" else "<date>" if k == "extractedAt" else norm(v)) for k, v in o.items()}
    return o
dump = lambda o: json.dumps(norm(o), sort_keys=True)
assert dump(doc["typography"]["font-weight"]) == dump(got["typography"]["font-weight"]), "font-weight token drifted from token-shape.md"
trk = json.load(open(sys.argv[3]))
assert dump(doc["typography"]["letter-spacing-port-factor"]) == dump(trk["typography"]["letter-spacing-port-factor"]), "port-factor token drifted from token-shape.md"
lst = json.load(open(sys.argv[4]))
assert dump(doc["typography"]["letter-spacing"]) == dump(lst["typography"]["letter-spacing"]), "letter-spacing token drifted from token-shape.md"
print(f"  self-match returns {w}; all three documented tokens match the emitted ones (paths and dates normalised)")
PY
