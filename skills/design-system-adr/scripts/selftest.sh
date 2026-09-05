#!/usr/bin/env bash
# Prove this skill's worked example and its script still agree with what the
# skill documents. Run from the skill root. Needs only python3.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
py="${PYTHON:-python3}"
adr="$here/scripts/adr.py"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# 1. The shipped example is a valid record and its directory has a valid index.
"$py" "$adr" check "$here/assets/examples" > "$tmp/ex.txt"
grep -q "1 records — 0 errors, 0 warnings" "$tmp/ex.txt"
echo "  the worked example passes check with no warnings, index included"

# 2. Numbering: highest of directory and --also, never the lowest gap.
mkdir -p "$tmp/adr"
cp "$here/references/template.md" "$tmp/adr/0000-template.md"
cp "$here/assets/examples/0001-"*.md "$tmp/adr/0004-first.md"
cp "$here/assets/examples/0001-"*.md "$tmp/adr/0005-second.md"
test "$("$py" "$adr" next --dir "$tmp/adr")" = "0006"
test "$("$py" "$adr" next --dir "$tmp/adr" --also 0007,0002)" = "0008"
echo "  next number counts the directory and --also, and skips gaps"

# 3. new: the template with comments stripped and metadata filled; it passes check.
out="$("$py" "$adr" new "Adopt conventional commits" --dir "$tmp/adr" --deciders "Selftest")"
test "$(basename "$out")" = "0006-adopt-conventional-commits.md"
! grep -q '<!--' "$out"
grep -q '^# Adopt conventional commits$' "$out"
grep -q '^- \*\*Status:\*\* Proposed$' "$out"
"$py" "$adr" check "$out" > "$tmp/new.txt"
echo "  new writes NNNN-kebab-title.md from the template, comments gone, and it checks clean"

# 4. check fails on the defects the skill names: status synonym, duplicate number, one option.
sed 's/^- \*\*Status:\*\* Accepted$/- **Status:** Approved/' "$tmp/adr/0004-first.md" > "$tmp/adr/0007-approved.md"
if "$py" "$adr" check "$tmp/adr/0007-approved.md" > "$tmp/bad.txt"; then echo "  expected a failure on 'Approved'"; exit 1; fi
grep -q "Approved" "$tmp/bad.txt"
cp "$tmp/adr/0004-first.md" "$tmp/adr/0004-again.md"
if "$py" "$adr" check "$tmp/adr" > "$tmp/dup.txt"; then echo "  expected a failure on the duplicate 0004"; exit 1; fi
grep -q "number 0004 is used by more than one record" "$tmp/dup.txt"
"$py" - "$tmp/adr/0004-first.md" "$tmp/adr/0008-one-option.md" <<'PY'
import re, sys
t = open(sys.argv[1]).read()
t = re.sub(r"### Option 2:.*?(?=## Decision)", "", t, flags=re.S)   # drop options 2 and 3
open(sys.argv[2], "w").write(t)
PY
if "$py" "$adr" check "$tmp/adr/0008-one-option.md" > "$tmp/one.txt"; then echo "  expected a failure on one option"; exit 1; fi
grep -q "1 option(s)" "$tmp/one.txt"
echo "  check fails on a status synonym, a duplicated number and a single option"

# 5. index: one row per record, gaps as Unused, and check accepts the written index.
rm "$tmp/adr/0004-again.md" "$tmp/adr/0007-approved.md" "$tmp/adr/0008-one-option.md"
"$py" "$adr" index --dir "$tmp/adr" --write > /dev/null
grep -q '^| \[0004\](0004-first.md) |' "$tmp/adr/README.md"
grep -q '^| 0003 | — | Unused | — |' "$tmp/adr/README.md"
"$py" "$adr" check "$tmp/adr" > "$tmp/idx.txt"
grep -q "3 records — 0 errors" "$tmp/idx.txt"
echo "  index lists every record, marks gaps Unused, and the directory then checks clean"
