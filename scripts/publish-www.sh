#!/usr/bin/env bash
# Publish the demo pages to the `www` branch, for GitHub Pages: the contents of
# demo/ hoisted to the branch root, a generated index.html at the root listing
# the pages, a generated index.html inside any folder that ships files but no
# page of its own (Pages does not list directories), and .nojekyll. Copies only
# what git tracks on the current commit — never the working tree, which may
# hold ignored files (last year's pen carries a key).
#
#   bash scripts/publish-www.sh          # rebuild www from HEAD and push it
#   bash scripts/publish-www.sh --no-push
#
# Pages settings: deploy from branch `www`, folder `/ (root)`. Run this after
# every merge that touches demo/; the commit message records the source sha.
# The site: https://equinor.github.io/skills/
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
src="$(git -C "$root" rev-parse --short HEAD)"
tmp="$(mktemp -d)"; trap 'git -C "$root" worktree remove --force "$tmp" 2>/dev/null || rm -rf "$tmp"' EXIT

if git -C "$root" show-ref --quiet refs/heads/www || git -C "$root" ls-remote --exit-code --heads origin www >/dev/null 2>&1; then
  git -C "$root" fetch -q origin www 2>/dev/null || true
  git -C "$root" worktree add -q "$tmp" www 2>/dev/null || git -C "$root" worktree add -q -b www "$tmp" origin/www
  git -C "$tmp" rm -rq . 2>/dev/null || true
else
  git -C "$root" worktree add -q --detach "$tmp"
  git -C "$tmp" switch -q --orphan www
  git -C "$tmp" rm -rqf . 2>/dev/null || true
fi
find "$tmp" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +

# tracked files under demo/, hoisted one level
git -C "$root" archive HEAD demo | tar -x -C "$tmp" --strip-components=1
touch "$tmp/.nojekyll"

# index.html at the root, and one inside each files-only folder
python3 - "$tmp" "$src" <<'PY'
import html, pathlib, re, sys
from urllib.parse import quote
root, src = pathlib.Path(sys.argv[1]), sys.argv[2]

CSS = """  @font-face { font-family: Inter; src: url(https://cdn.eds.equinor.com/font/InterVariable.woff2) format("woff2-variations"); font-weight: 100 900; font-display: swap; }
  html { background: oklch(0.97 0 0); color: oklch(0.23 0 0); }
  body { margin: 0; font-family: Inter, system-ui, sans-serif; font-size: 1rem; line-height: 1.5; }
  main { max-width: 44rem; margin: 0 auto; padding: 2.5rem 2rem; }
  h1 { font-size: 1.75rem; line-height: 2.25rem; font-weight: 500; margin: 0 0 0.5rem; }
  p, li { color: oklch(0.35 0 0); }
  ul { padding: 0; list-style: none; display: grid; gap: 1rem; margin: 1.5rem 0; }
  li { padding: 1rem 1.25rem; background: oklch(0.999 0 0); border-radius: 4px; box-shadow: inset 0 0 0 1px oklch(0.87 0 0); }
  ul.files { gap: 0.5rem; }
  ul.files li { padding: 0.75rem 1rem; font-family: ui-monospace, monospace; font-size: 0.9375rem; }
  a { color: oklch(0.5 0.075 204.6); } a b { font-weight: 500; }
  small { color: oklch(0.46 0 0); font-family: Inter, system-ui, sans-serif; }
  ul.files small { margin-left: 0.5rem; }
  footer { margin-top: 2rem; font-size: 0.875rem; color: oklch(0.46 0 0); }"""

def page(title, body):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{html.escape(title)}</title>\n<style>\n{CSS}\n</style>\n</head>\n<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n')

def first_paragraph(md_path):
    """The first prose paragraph of a Markdown file: no headings, fences, tables,
    quotes or lists; a trailing colon becomes a full stop, since it is shown alone."""
    if not md_path.exists():
        return ""
    paras = [p for p in md_path.read_text(errors="replace").split("\n\n")
             if p.strip() and not p.lstrip().startswith(("#", "```", "|", ">", "-", "*"))]
    if not paras:
        return ""
    lead = " ".join(paras[0].split())
    lead = re.sub(r"`([^`]*)`", r"\1", lead)                      # inline code → plain
    lead = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", lead)          # [text](url) → text
    return lead[:-1] + "." if lead.endswith(":") else lead

pages = []
for idx in sorted(root.glob("*/index.html")):
    t = idx.read_text(errors="replace")
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    hint = re.search(r'<p class="hint">(.*?)</p>', t, re.S)
    pages.append((idx.parent.name, html.unescape(title.group(1).strip()) if title else idx.parent.name,
                  re.sub(r"<[^>]+>", "", html.unescape(hint.group(1))).strip() if hint else ""))

others = [d.name for d in sorted(root.iterdir()) if d.is_dir() and d.name != ".git" and not (d / "index.html").exists()]
leads = {}
for n in others:
    d = root / n
    files = sorted(f for f in d.rglob("*") if f.is_file())
    lead = first_paragraph(d / "INTENT.md")
    leads[n] = lead
    rows = "\n".join(
        f'      <li><a href="{html.escape(quote(f.relative_to(d).as_posix()))}">{html.escape(f.relative_to(d).as_posix())}</a>'
        f' <small>{max(1, round(f.stat().st_size / 1024))} KB</small></li>' for f in files)
    body = (f"  <h1>{html.escape(n)}</h1>\n"
            + (f"  <p>{html.escape(lead)}</p>\n" if lead else "")
            + "  <p>Files in this folder. The <code>INTENT.md</code> records why it is built the way it is;\n"
              '     <a href="../">back to the demos</a>.</p>\n'
            + f'  <ul class="files">\n{rows}\n  </ul>')
    (d / "index.html").write_text(page(f"{n} — equinor/skills", body))

items = "\n".join(
    f'      <li><a href="{html.escape(quote(n))}/"><b>{html.escape(ti)}</b></a>' + (f'<br><small>{html.escape(h)}</small>' if h else "") + "</li>"
    for n, ti, h in pages)
extra = "\n".join(
    f'      <li><a href="{html.escape(quote(n))}/"><b>{html.escape(n)}</b></a>' + (f'<br><small>{html.escape(leads[n])}</small>' if leads.get(n) else "") + "</li>"
    for n in others)
body = ("  <h1>Demos from equinor/skills</h1>\n"
        "  <p>Pages shown at Into Design Systems Oslo, 9 September 2026. Each folder in the\n"
        "     repository's <code>demo/</code> carries an <code>INTENT.md</code> that records why it is\n"
        "     built the way it is.</p>\n"
        f"  <ul>\n{items}\n{extra}\n  </ul>\n"
        '  <footer>Skills: <a href="https://github.com/equinor/skills">github.com/equinor/skills</a> ·\n'
        f'    <code>npx skills add equinor/skills --skill &lt;name&gt;</code> · built from <code>{html.escape(src)}</code></footer>')
(root / "index.html").write_text(page("equinor/skills — demos", body))
print(f"index.html: {len(pages)} pages, {len(others)} folders")
PY

git -C "$tmp" add -A
if git -C "$tmp" diff --cached --quiet; then echo "www is already up to date with $src"; exit 0; fi
git -C "$tmp" -c core.hooksPath=/dev/null commit -q -m "Publish demo/ from $src

Generated by scripts/publish-www.sh; do not edit here — change demo/ on main and re-run."
if [ "${1:-}" != "--no-push" ]; then git -C "$tmp" push -q -u origin www; fi
echo "www ← demo/ @ $src$( [ "${1:-}" = "--no-push" ] && echo ' (not pushed)')"
