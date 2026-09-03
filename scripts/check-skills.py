#!/usr/bin/env python3
"""Check every skill in skills/ for the things that keep going wrong.

    python3 scripts/check-skills.py            # static checks
    python3 scripts/check-skills.py --deep     # also run each skill's selftest

Static checks are cheap and safe to run on every commit. `--deep` executes
`scripts/selftest.sh` in any skill that has one — that is where a skill proves
its own worked examples still run, against the fixtures it documents rather
than fixtures the author invented.

Exit status is non-zero if anything fails. Warnings do not fail the run.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
SOFT_LINES, HARD_LINES = 300, 500

fails, warns = [], []
def fail(where, msg): fails.append(f"{where}: {msg}")
def warn(where, msg): warns.append(f"{where}: {msg}")


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        fail(path, "no YAML frontmatter"); return None, text
    end = text.index("\n---\n", 3)
    raw, body = text[4:end], text[end + 5:]
    data = {}
    for line in raw.split("\n"):
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m:
            v = m.group(2).strip()
            if len(v) > 1 and v[0] == v[-1] and v[0] in "'\"":
                v = v[1:-1]
            data[m.group(1)] = v
    return data, body


def check_frontmatter(skill, path):
    data, _ = frontmatter(path)
    if data is None:
        return
    extra = set(data) - {"name", "description"}
    if extra:
        fail(path, f"frontmatter has unexpected keys: {sorted(extra)}")
    if data.get("name") != skill.name:
        fail(path, f"name {data.get('name')!r} != directory {skill.name!r}")
    d = data.get("description", "")
    if not d:
        fail(path, "empty description")
    if len(d) > 1024:
        fail(path, f"description is {len(d)} chars, over the 1024 limit")
    for cue in ("USE FOR:", "DO NOT USE FOR:"):
        if cue not in d:
            fail(path, f"description is missing {cue} (see CLAUDE.md)")


def check_length(path):
    n = len(path.read_text().splitlines())
    if n > HARD_LINES:
        fail(path, f"{n} lines, over the {HARD_LINES}-line hard limit")
    elif n > SOFT_LINES:
        warn(path, f"{n} lines, over the {SOFT_LINES}-line gate — move overflow to references/")


def check_links(path):
    for target in re.findall(r"\]\(([^)#][^)]*)\)", path.read_text()):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).exists():
            fail(path, f"link does not resolve: {target}")


def check_blocks(path):
    text = path.read_text()
    for lang, body in re.findall(r"```(\w+)\n(.*?)```", text, re.S):
        if lang == "json":
            try:
                json.loads(body)
            except json.JSONDecodeError:
                try:                      # docs often show a fragment, not a whole file
                    json.loads("{" + body.rstrip().rstrip(",") + "}")
                except json.JSONDecodeError as e:
                    fail(path, f"json block does not parse, whole or wrapped: {e}")
        elif lang == "python":
            try:
                compile(body, str(path), "exec")
            except SyntaxError as e:
                fail(path, f"python block does not compile: line {e.lineno}, {e.msg}")


def check_scripts(skill):
    for py in (skill / "scripts").glob("*.py"):
        try:
            compile(py.read_text(), str(py), "exec")
        except SyntaxError as e:
            fail(py, f"does not compile: line {e.lineno}, {e.msg}")


def check_venv_advice(skill):
    """A venv created inside an installed skill is clobbered by `skills update`.
    Any `-m venv` in a skill file must say, within two lines, that it runs at
    the project root."""
    files = [skill / "SKILL.md", *skill.glob("references/*.md"),
             *skill.glob("assets/**/*.md"), *skill.glob("scripts/*.sh")]
    for f in files:
        if not f.exists():
            continue
        lines = f.read_text().splitlines()
        for i, line in enumerate(lines):
            if re.search(r"-m venv", line):
                window = "\n".join(lines[max(0, i - 2):i + 3])
                if not re.search(r"project root", window, re.I):
                    warn(f, f"line {i + 1}: creates a venv without saying it goes at the "
                            "project root — it lands inside the installed package (issue #20)")


def selftest(skill):
    script = skill / "scripts" / "selftest.sh"
    if not script.exists():
        warn(skill, "no scripts/selftest.sh — worked examples are unverified")
        return
    r = subprocess.run(["bash", str(script)], cwd=skill, capture_output=True, text=True)
    if r.returncode == 2:
        warn(skill, "selftest skipped — " + (r.stdout + r.stderr).strip().splitlines()[0])
    elif r.returncode != 0:
        fail(skill, "selftest failed:\n" + (r.stdout + r.stderr).strip()[:1500])
    else:
        print(f"  selftest passed: {skill.name}\n" + r.stdout.rstrip())


def main():
    deep = "--deep" in sys.argv
    skills = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if not skills:
        print("no skills found"); return 1
    for skill in skills:
        md = skill / "SKILL.md"
        if not md.exists():
            fail(skill, "no SKILL.md"); continue
        check_frontmatter(skill, md)
        check_length(md)
        check_venv_advice(skill)
        check_scripts(skill)
        for doc in [md, *sorted(skill.rglob("*.md"))]:
            check_links(doc)
            check_blocks(doc)
        if deep:
            selftest(skill)

    for w in warns: print(f"warn  {w}")
    for f in fails: print(f"FAIL  {f}")
    print(f"\n{len(skills)} skills — {len(fails)} failures, {len(warns)} warnings")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
