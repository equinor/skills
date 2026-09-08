#!/usr/bin/env python3
"""Create, check and index Architecture Decision Records in the EDS team format.

Usage:
  python adr.py new "Short title of the decision" [--dir documentation/adr]
                    [--status Proposed] [--deciders "EDS Core Team"] [--also 0017,0018]
  python adr.py check [DIR | FILE ...]          # lint; exit 1 on errors
  python adr.py index [--dir documentation/adr] [--write]   # the README table
  python adr.py next [--dir documentation/adr] [--also N,N]  # next free number

The format is the EDS team's customised MADR: bullet-list metadata, per-option
Pros/Cons under "Options Considered", a flat "## Decision" with "### Consequences"
and an optional "### Confirmation", then "## Related". `check` enforces what the
template and the accepted records agree on, and warns on the rest.

Requires: Python 3.9+, nothing else. `--gh` asks the GitHub CLI for numbers
claimed by open pull requests, if `gh` is installed and authenticated.
"""
import argparse, datetime, json, re, subprocess, sys
from pathlib import Path

FILENAME = re.compile(r"^(\d{4})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
STATUSES = ("Proposed", "Accepted", "Rejected", "Deprecated", "Superseded")
REQUIRED = ["## Context", "## Decision Drivers", "## Options Considered", "## Decision",
            "### Consequences", "## Related"]
OPTIONAL = ["### Confirmation"]
TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "template.md"
# every `[...]` in the template that is not a link is a placeholder to be replaced
PLACEHOLDERS = sorted({m.group(0) for m in re.finditer(r"\[[^\]\n]+\](?!\()", TEMPLATE.read_text())})


# ---- reading -----------------------------------------------------------------
def records(directory):
    out = []
    for f in sorted(Path(directory).glob("*.md")):
        m = FILENAME.match(f.name)
        if m and int(m.group(1)) > 0:
            out.append((int(m.group(1)), f))
    return out


def meta(text):
    """The bullet-list metadata under the H1: status, date, decision makers."""
    d = {}
    for key, pat in (("status", r"^- \*\*Status:\*\*\s*(.+)$"), ("date", r"^- \*\*Date:\*\*\s*(.+)$"),
                     ("deciders", r"^- \*\*Decision makers:\*\*\s*(.+)$")):
        m = re.search(pat, text, re.M)
        d[key] = m.group(1).strip() if m else None
    return d


def headings(text):
    return [line.rstrip() for line in text.splitlines() if re.match(r"^#{1,3} ", line)]


# ---- check -------------------------------------------------------------------
def check_file(path, all_numbers=None):
    """Return (errors, warnings) for one record."""
    errors, warns = [], []
    text = path.read_text()
    m = FILENAME.match(path.name)
    if not m:
        errors.append("filename is not NNNN-kebab-title.md")
    h1 = re.search(r"^# (.+)$", text, re.M)
    if not h1:
        errors.append("no H1 title")
    elif re.match(r"^\s*(ADR[- ]?)?\d{4}\b", h1.group(1)):
        errors.append("H1 carries the number; the filename does, the title does not")
    if "<!--" in text:
        warns.append("guidance comments left in; the template's comments are deleted in a finished record")
    left = [ph for ph in PLACEHOLDERS if ph in text]
    if left:
        errors.append(f"template placeholders left in: {', '.join(left[:4])}{' …' if len(left) > 4 else ''}")
    md = meta(text)
    if not md["status"]:
        errors.append("no `- **Status:**` line")
    else:
        head = md["status"].split(" ")[0].strip("(")
        if head not in STATUSES:
            errors.append(f"status {md['status']!r} is not one of {'/'.join(STATUSES)}"
                          + (" — 'Approved' is not in the vocabulary; use Accepted" if head == "Approved" else ""))
        if head == "Superseded" or "uperseded by" in md["status"]:
            link = re.search(r"\[[^\]]*\]\(([^)]+)\)", md["status"])
            if not link:
                errors.append("Superseded status names no ADR: `Superseded by [ADR-NNNN](NNNN-....md)`")
            elif not (path.parent / link.group(1)).exists():
                errors.append(f"Superseded link does not resolve: {link.group(1)}")
    if not md["date"]:
        errors.append("no `- **Date:**` line")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", md["date"]):
        errors.append(f"date {md['date']!r} is not YYYY-MM-DD")
    if not md["deciders"]:
        errors.append("no `- **Decision makers:**` line")
    hs = headings(text)
    pos = {h: i for i, h in enumerate(hs)}
    missing = [h for h in REQUIRED if h not in pos]
    for h in missing:
        errors.append(f"missing section {h}")
    present = [h for h in REQUIRED if h in pos]
    if [pos[h] for h in present] != sorted(pos[h] for h in present):
        errors.append("sections are out of the template's order")
    for h in OPTIONAL:
        if h not in pos:
            warns.append(f"no {h} — how will anyone verify the decision is followed?")
    options = [h for h in hs if re.match(r"^### Option \d+", h)]
    if "## Options Considered" in pos:
        if len(options) < 2:
            errors.append(f"{len(options)} option(s) under Options Considered; a decision needs at least two")
        body = text[text.index("## Options Considered"):]
        body = body[:body.index("\n## Decision")] if "\n## Decision" in body else body
        for opt in options:
            seg_start = body.find(opt)
            if seg_start < 0:
                errors.append(f"{opt} appears outside Options Considered"); continue
            seg = body[seg_start:]
            nxt = re.search(r"\n### Option \d+", seg[1:])
            seg = seg[: nxt.start() + 1] if nxt else seg
            if "**Pros:**" not in seg or "**Cons:**" not in seg:
                errors.append(f"{opt!r} lacks **Pros:** or **Cons:** — every option gets fair treatment")
    if "### Consequences" in pos:
        cons = text[text.index("### Consequences"):]
        cons = re.split(r"\n#{2,3} ", cons, maxsplit=1)[0]
        bullets = re.findall(r"^- (Good|Bad|Neutral), because", cons, re.M)
        if not bullets:
            errors.append("Consequences has no `- Good, because` / `- Bad, because` bullets")
        elif "Bad" not in bullets:
            warns.append("Consequences lists nothing bad; every decision costs something")
    if all_numbers is not None and m:
        n = int(m.group(1))
        if all_numbers.count(n) > 1:
            errors.append(f"number {n:04d} is used by more than one record")
    return errors, warns


def check_index(directory, recs):
    """The README index, if present, must list every record and no ghosts."""
    readme = Path(directory) / "README.md"
    if not readme.exists():
        return [], ["no README.md index — status is invisible without opening every file (see references/index.md)"]
    text = readme.read_text()
    errors, warns = [], []
    for n, f in recs:
        if f.name not in text:
            errors.append(f"index does not list {f.name}")
    for link in re.findall(r"\]\((\d{4}-[^)]+\.md)\)", text):
        if not (Path(directory) / link).exists():
            errors.append(f"index links to a missing file: {link}")
    return errors, warns


def cmd_check(args):
    paths = [Path(p) for p in args.paths] or [Path("documentation/adr")]
    files, dirs = [], []
    for p in paths:
        (dirs if p.is_dir() else files).append(p)
    for d in dirs:
        files += [f for _, f in records(d)]
    if not files:
        print("no records found", file=sys.stderr); return 2
    numbers = [int(FILENAME.match(f.name).group(1)) for f in files if FILENAME.match(f.name)]
    total_e = total_w = 0
    report = {}
    for f in files:
        e, w = check_file(f, numbers)
        report[str(f)] = {"errors": e, "warnings": w}
        total_e += len(e); total_w += len(w)
    for d in dirs:
        e, w = check_index(d, records(d))
        report[str(d / "README.md")] = {"errors": e, "warnings": w}
        total_e += len(e); total_w += len(w)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for where, r in report.items():
            for e in r["errors"]:
                print(f"ERROR {where}: {e}")
            for w in r["warnings"]:
                print(f"warn  {where}: {w}")
        print(f"{len(files)} records — {total_e} errors, {total_w} warnings")
    return 1 if total_e else 0


# ---- numbering ---------------------------------------------------------------
def repo_relative(directory):
    """The ADR directory as a path inside the repository, for matching PR file lists."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=directory, capture_output=True,
                             text=True, check=True).stdout.strip()
        return Path(directory).resolve().relative_to(Path(top).resolve()).as_posix()
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return Path(directory).name


def claimed_by_open_prs(directory, repo=None):
    """Numbers used by ADR files *in the ADR directory* in open pull requests, via the GitHub CLI."""
    prefix = repo_relative(directory).rstrip("/") + "/"
    try:
        cmd = ["gh", "pr", "list", "--state", "open", "--json", "number,files", "--limit", "1000"]
        if repo:
            cmd += ["--repo", repo]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"warning: could not ask gh for open PRs ({e}); pass --also with any numbers you know of",
              file=sys.stderr)
        return []
    prs = json.loads(out)
    if len(prs) >= 1000:
        print("warning: 1000 open PRs listed; the scan may be capped — pass --also with numbers you know of", file=sys.stderr)
    nums = []
    for pr in prs:
        for f in pr.get("files", []):
            p = f.get("path", "")
            m = FILENAME.match(Path(p).name) if p.startswith(prefix) else None
            if m:
                nums.append(int(m.group(1)))
    return nums


def next_number(directory, also=(), gh=False, repo=None):
    used = [n for n, _ in records(directory)] + list(also) + (claimed_by_open_prs(directory, repo) if gh else [])
    return (max(used) + 1) if used else 1


def slug(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)


def cmd_next(args):
    print(f"{next_number(args.dir, parse_also(args.also), args.gh, args.repo):04d}")
    return 0


def parse_also(s):
    return [int(x) for x in s.split(",") if x.strip()] if s else []


def cmd_new(args):
    d = Path(args.dir); d.mkdir(parents=True, exist_ok=True)
    n = next_number(d, parse_also(args.also), args.gh, args.repo)
    path = d / f"{n:04d}-{slug(args.title)}.md"
    if path.exists():
        print(f"refusing to overwrite {path}", file=sys.stderr); return 1
    body = TEMPLATE.read_text()
    body = re.sub(r"<!--.*?-->\n?", "", body, flags=re.S)                    # guidance out
    body = body.replace("# [Short title of the decision]", f"# {args.title}", 1)
    body = body.replace("- **Status:** Proposed | Accepted | Rejected | Deprecated | Superseded by [ADR-NNNN]",
                        f"- **Status:** {args.status}", 1)
    body = body.replace("- **Date:** YYYY-MM-DD", f"- **Date:** {args.date or datetime.date.today().isoformat()}", 1)
    body = body.replace("- **Decision makers:** [List the people involved in making this decision]",
                        f"- **Decision makers:** {args.deciders}", 1)
    body = re.sub(r"\n{3,}", "\n\n", body)
    path.write_text(body)
    print(path)
    return 0


# ---- index -------------------------------------------------------------------
def cmd_index(args):
    d = Path(args.dir)
    recs = records(d)
    rows = ["| ADR | Title | Status | Date |", "| --- | --- | --- | --- |"]
    by_number = {n: f for n, f in recs}
    for n in range(1, max(by_number) + 1) if by_number else []:      # number order, gaps in place
        f = by_number.get(n)
        if f is None:
            rows.append(f"| {n:04d} | — | Unused | — |"); continue
        text = f.read_text(); md = meta(text)
        h1 = re.search(r"^# (.+)$", text, re.M)
        rows.append(f"| [{n:04d}]({f.name}) | {h1.group(1) if h1 else f.stem} | {md['status'] or '?'} | {md['date'] or '?'} |")
    table = "\n".join(rows)
    tmpl = "[0000-template.md](0000-template.md)" if (d / "0000-template.md").exists() else "`0000-template.md`"
    first = f"ADR-{min(by_number):04d}" if by_number else "the first record"
    out = ("# Architecture Decision Records\n\n"
           f"Decisions follow the format in {tmpl}. See {first} for\n"
           "when to write one, the numbering rule and the status lifecycle. One row per record,\n"
           "regenerated with `adr.py index --write`; a number with no record is a PR that closed\n"
           "unmerged, kept so a gap is distinguishable from a lost file.\n\n" + table + "\n")
    if args.write:
        (d / "README.md").write_text(out); print(d / "README.md")
    else:
        sys.stdout.write(out)
    return 0


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="lint records; exit 1 on errors")
    c.add_argument("paths", nargs="*", metavar="DIR|FILE")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_check)
    for name, fn, help_ in (("new", cmd_new, "create the next record from the template"),
                            ("next", cmd_next, "print the next free number"),
                            ("index", cmd_index, "print (or --write) the README index")):
        q = sub.add_parser(name, help=help_)
        q.add_argument("--dir", default="documentation/adr")
        if name in ("new", "next"):
            q.add_argument("--also", metavar="N,N", help="numbers claimed elsewhere, e.g. in open PRs")
            q.add_argument("--gh", action="store_true", help="ask the GitHub CLI for numbers in open PRs")
            q.add_argument("--repo", help="owner/name for --gh, when not in the repo")
        if name == "new":
            q.add_argument("title")
            q.add_argument("--status", default="Proposed", choices=STATUSES[:2])
            q.add_argument("--date", help="YYYY-MM-DD, default today")
            q.add_argument("--deciders", default="[List the people involved in making this decision]")
        if name == "index":
            q.add_argument("--write", action="store_true")
        q.set_defaults(fn=fn)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
