"""Resume rendering pipeline (orchestrator, stdlib + Jinja2).

Pipeline:
    resume.json -> localize(lang) -> validate (schema) -> normalize (ResumeModel)
                -> single Jinja template -> HTML -> Chromium -> PDF
                -> preview PNG -> QA

The source is bilingual: translatable leaves are ``{"en": ..., "zh": ...}``.
A tailored resume is a complete snapshot; there is no overlay/resolver layer.
Everything renders per language (``--lang en|zh``) into
``<stem>-<lang>.pdf`` plus one stacked ``preview_<stem>-<lang>.png``.

Usage (from the skill root):
    uv run scripts/render.py fixtures/sample.json --lang en
    uv run scripts/render.py --selftest

Without an explicit output directory, renders go to ``<src dir>/output`` so a
snapshot and its artifacts stay inside the same application directory.
"""
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "jinja2>=3.1.6",
#   "markupsafe>=3.0.4",
#   "pillow>=13.0.0",
#   "pymupdf>=2.1",
# ]
# ///
# PEP 723 inline metadata: `uv run scripts/render.py ...` builds an isolated
# environment from the block above. No `uv sync`, no install step, no
# pyproject.toml required for a fresh install of this skill.
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

# Public synthetic catalog. Search upward so the same expression resolves in
# both the repo layout and the packaged skill. Selftest never touches personal
# data.
def _find_fixtures() -> Path:
    for p in (HERE, *HERE.parents):
        cand = p / "fixtures"
        if (cand / "sample.json").is_file():
            return cand
    return HERE.parent / "fixtures"


FIXTURE_DIR = _find_fixtures()
FIXTURE = FIXTURE_DIR / "sample.json"
DEFAULT_SRC = FIXTURE

if __package__ in (None, ""):  # script mode: uv run scripts/render.py
    sys.path.insert(0, str(HERE))
    from edit import EditError, apply_edit, find_target
    from normalize import SECTION_KEYS, normalize_resume
    from palette import accent_palette
    from qa import print_report, run_pdf_qa, run_structural_qa
    from renderer import render_header, render_nodes, render_section
    from resolve import LANGS, localize, resolve_source
    from schema import ResumeValidationError, validate_raw
else:  # package mode: python -m scripts
    from .edit import EditError, apply_edit, find_target
    from .normalize import SECTION_KEYS, normalize_resume
    from .palette import accent_palette
    from .qa import print_report, run_pdf_qa, run_structural_qa
    from .renderer import render_header, render_nodes, render_section
    from .resolve import LANGS, localize, resolve_source
    from .schema import ResumeValidationError, validate_raw

import jinja2
from markupsafe import Markup

SECTION_TITLES = {
    "skills": {"en": "Skills", "zh": "技术技能"},
    "work": {"en": "Experience", "zh": "工作经历"},
    "projects": {"en": "Selected Projects", "zh": "代表项目"},
    "education": {"en": "Education", "zh": "教育"},
    "publications": {"en": "Publication", "zh": "学术成果"},
}
ACCENT_SMOKE = ("#B14E2E", "#58758A", "#657A70", "#756F82", "#805F63")


# ---------------- PDF backend ----------------
def find_edge():
    env = os.environ.get("CV_EDGE_BIN")
    if env and Path(env).exists():
        return env
    import shutil
    for cmd in ("google-chrome", "google-chrome-stable", "chromium",
                "chromium-browser", "msedge", "chrome"):
        found = shutil.which(cmd)
        if found:
            return found
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              "/usr/bin/google-chrome",
              "/usr/bin/chromium",
              "/usr/bin/chromium-browser"):
        if Path(p).exists():
            return p
    return None


def build_pdf(html_path: Path, pdf_path: Path) -> bool:
    edge = find_edge()
    if not edge:
        print("WARN: no Edge/Chrome found (set CV_EDGE_BIN); skipped PDF")
        return False
    cmd = [edge, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
           html_path.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not pdf_path.exists():
        print("WARN: print-to-pdf produced nothing")
        print(r.stdout[-2000:] + r.stderr[-2000:])
        return False
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size/1024:.0f} KB)")
    return True


def build_preview(pdf_path: Path, png_path: Path) -> None:
    """Write one deterministic preview image for the whole PDF.

    Every page is rendered full-width (real page margins preserved) with only
    its trailing blank rows trimmed, then stacked vertically. Applying the same
    rule to single- and multi-page PDFs keeps EN and ZH previews consistent.
    Exactly one file is written so the frontend can link
    ``preview_<stem>-<lang>.png`` without knowing the page count.
    """
    try:
        import pymupdf
    except ImportError:
        print("pymupdf missing, skipped preview")
        return
    d = pymupdf.open(str(pdf_path))
    if len(d) == 0:
        return
    pixmaps = [d[i].get_pixmap(dpi=110) for i in range(len(d))]
    try:
        from PIL import Image, ImageChops
    except ImportError:
        pixmaps[0].save(str(png_path))
        return
    slices = []
    for p in pixmaps:
        im = Image.frombytes("RGB", (p.width, p.height), p.samples)
        # Keep x/left/right/top margins intact; drop only the blank bottom band
        # so a mostly-empty last page does not leave a huge white gap.
        diff = ImageChops.difference(im, Image.new("RGB", im.size, "white"))
        bbox = diff.convert("L").point(lambda x: 255 if x > 12 else 0).getbbox()
        bottom = bbox[3] if bbox is not None else 0
        if bottom <= 0:
            continue  # fully blank page
        slices.append(im.crop((0, 0, im.width, bottom)))
    if not slices:
        pixmaps[0].save(str(png_path))
        return
    width = max(im.width for im in slices)
    height = sum(im.height for im in slices)
    canvas = Image.new("RGB", (width, height), "white")
    y = 0
    for im in slices:
        canvas.paste(im, (0, y))
        y += im.height
    canvas.save(str(png_path))


# ---------------- pipeline ----------------
def render_html(model: dict, accent: dict, template_text: str,
                lang: str = "en") -> str:
    """Execute the single template with the normalized model.

    Sections are rendered in canonical order; empty sections are already
    omitted by normalize_resume. The template receives the accent palette,
    safe header HTML, and the pre-rendered sections.
    """
    env = jinja2.Environment(autoescape=True)
    env.globals["inline"] = lambda nodes: Markup(render_nodes(nodes or []))
    tpl = env.from_string(template_text)
    name_html, role_html, contact_html = render_header(model)
    parts = []
    for key in SECTION_KEYS:
        sec = model["sections"].get(key)
        if not sec:
            continue
        title = (SECTION_TITLES.get(key, {}).get(lang)
                 or SECTION_TITLES.get(key, {}).get("en")
                 or key)
        parts.append(render_section(sec, title, ""))
    return tpl.render(
        title=f"{model['name']} — {model['role']}",
        lang=lang,
        accent=accent,
        name=name_html,
        role=role_html,
        contact=contact_html,
        sections="\n\n".join(parts),
    )


def _count_link_nodes(nodes: list) -> int:
    return sum(1 for nd in nodes
               if nd.get("t") == "link" and nd.get("href"))


def expected_link_count(model: dict) -> int:
    """Expected ``href=`` count, derived from the model — never hardcoded.

    Counts every anchor the renderer will emit: contact links, entry title
    URLs, publication links, and inline links inside any text node.
    """
    n = sum(1 for c in model["contact"] if c.get("href"))
    for s in model["sections"].values():
        for sk in s.get("skills", []):
            n += _count_link_nodes(sk.get("nodes", []))
        for e in s["entries"]:
            if e.get("url"):
                n += 1
            n += _count_link_nodes(e["title_nodes"])
            n += _count_link_nodes(e["stack_nodes"])
            for p in e["paras"]:
                n += _count_link_nodes(p)
            for b in e["bullets"]:
                n += _count_link_nodes(b["nodes"])
            n += sum(1 for lk in e["links"] if lk.get("href"))
    return n


def selftest() -> int:
    """Fixture regression: IDs, render, accent, links, and QA.

    Runs entirely against the committed synthetic fixture so a fresh clone
    can execute it without any personal data on disk.
    """
    assert FIXTURE.is_file(), f"fixture missing: {FIXTURE}"
    template_text = (HERE / "template.html").read_text(encoding="utf-8")

    def model_for(src: Path, lang: str) -> dict:
        # Localize first: schema/normalize only ever see plain strings, so a
        # leaked localized leaf fails validation instead of reaching the PDF.
        localized = resolve_source(src, lang)
        validate_raw(localized)
        return normalize_resume(localized)

    # The fixture is the single bilingual fact catalog shipped with the repo.
    model_en = model_for(FIXTURE, "en")
    model_zh = model_for(FIXTURE, "zh")
    c = model_en["counts"]
    assert c["sections"] == 5, f"sections {c['sections']} != 5"
    assert c["entries"] >= 5, f"entries {c['entries']} < 5"
    assert c["skill_groups"] >= 1, "no skill groups"
    assert model_en["name"].strip(), "en name empty"
    assert model_zh["name"].strip(), "zh name empty"
    assert model_en["name"] != model_zh["name"], "localization had no effect"

    # Every entry and bullet must carry a unique stable id. The schema rejects
    # missing ids, duplicate ids, and legacy plain-string highlights.
    entry_ids = [e["id"] for s in model_en["sections"].values()
                 for e in s["entries"]]
    assert all(entry_ids), f"entry without stable id: {entry_ids}"
    bullet_ids = [b["id"] for s in model_en["sections"].values()
                  for e in s["entries"] for b in e["bullets"]]
    assert all(bullet_ids), f"bullet without stable id: {bullet_ids}"
    assert len(entry_ids + bullet_ids) == len(set(entry_ids + bullet_ids)), \
        "duplicate id in fixture"

    fixture_raw = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def schema_rejects(mutator, label: str) -> None:
        data = json.loads(json.dumps(fixture_raw))
        mutator(data)
        try:
            validate_raw(localize(data, "en"))
        except ResumeValidationError:
            return
        raise AssertionError(f"schema accepted {label}")

    schema_rejects(lambda d: d["work"][0]["highlights"][1].__setitem__(
        "id", d["work"][0]["highlights"][0]["id"]), "duplicate id")
    schema_rejects(lambda d: d["work"][0].pop("id"), "missing entry id")
    schema_rejects(lambda d: d["work"][0]["highlights"][0].pop("id"),
                   "missing bullet id")
    schema_rejects(lambda d: d["work"][0]["highlights"].append("legacy string"),
                   "legacy string bullet")

    # edit.py: the only recommended write path. It must change exactly one
    # text leaf, preserve the other language, and reject risky edits.
    _, _, _, bullet = find_target(fixture_raw, "work.northwind.b1")
    old_en = bullet["text"]["en"]
    edited = apply_edit(fixture_raw, "work.northwind.b1", old_en,
                        "Edited bullet", lang="en")
    _, _, _, new_bullet = find_target(edited, "work.northwind.b1")
    assert new_bullet["text"]["en"] == "Edited bullet"
    assert new_bullet["text"]["zh"] == bullet["text"]["zh"]
    assert find_target(fixture_raw, "work.northwind.b2")[3]["text"]["en"] == \
        find_target(edited, "work.northwind.b2")[3]["text"]["en"]

    _, _, _, b2 = find_target(fixture_raw, "work.northwind.b2")
    removed = apply_edit(fixture_raw, "work.northwind.b2", b2["text"]["en"],
                         remove=True, lang="en")
    try:
        find_target(removed, "work.northwind.b2")
    except EditError:
        pass
    else:
        raise AssertionError("edit.py failed to remove the target bullet")

    dup = json.loads(json.dumps(fixture_raw))
    dup["work"][0]["highlights"][1]["id"] = "work.northwind.b1"
    for label, call in (
        ("duplicate id", lambda: apply_edit(
            dup, "work.northwind.b1", old_en, "Nope", lang="en")),
        ("wrong expect", lambda: apply_edit(
            fixture_raw, "work.northwind.b1", "wrong", "Nope", lang="en")),
    ):
        try:
            call()
        except EditError:
            pass
        else:
            raise AssertionError(f"edit.py accepted {label}")

    base_html = render_html(model_en, accent_palette(model_en["accent"]),
                            template_text, lang="en")
    # Expectations are DERIVED from the loaded model, never hardcoded facts:
    # this file has to stay publishable next to a public fixture.
    assert "Experience" in base_html, "section title missing"
    for sec in model_en["sections"].values():
        for e in sec["entries"]:
            head = (e["title_text"] or "").split("|")[0].strip()
            if head and head not in base_html and html.escape(head) not in base_html:
                raise AssertionError(f"entry title dropped: {head!r}")
            if e.get("date") and e["date"] not in base_html:
                raise AssertionError(f"entry date dropped: {e['date']!r}")
            for para in e["paras"]:
                assert render_nodes(para) in base_html, "entry paragraph dropped"
            for b in e["bullets"]:
                assert render_nodes(b["nodes"]) in base_html, "entry bullet dropped"
    for lit in ("undefined", "[object Object]", ">None<"):
        assert lit not in base_html, f"forbidden literal {lit!r}"
    n_links = len(re.findall(r'href="', base_html))
    want_links = expected_link_count(model_en)
    assert n_links == want_links, f"links {n_links} != derived {want_links}"
    # Stable anchors: every id must reach the HTML so edits can be addressed.
    for eid in entry_ids:
        assert f'data-id="{html.escape(eid, quote=True)}"' in base_html, \
            f"entry id not anchored: {eid}"
    for bid in [b for b in bullet_ids if b]:
        assert f'data-id="{html.escape(bid, quote=True)}"' in base_html, \
            f"bullet id not anchored: {bid}"
    # QA must actually flag a planted leak (regression for the for/else bug):
    # the ERROR must appear AND the green PASS line must not, since the old
    # loop printed PASS unconditionally.
    planted = base_html.replace("</body>", "undefined</body>", 1)
    rep = run_structural_qa(model_en, planted)
    names = {nm: st for st, nm, _ in rep["checks"]}
    assert names.get("forbidden-literal") == "ERROR", \
        "QA failed to flag a planted forbidden literal"
    assert names.get("no-forbidden-literals") is None, \
        "QA printed no-forbidden-literals PASS while a leak was present"
    clean = run_structural_qa(model_en, base_html)
    assert {nm: st for st, nm, _ in clean["checks"]}
    assert not any(nm == "forbidden-literal" for _, nm, _ in clean["checks"]), \
        "clean render reported a forbidden literal"
    assert not any(nm == "content-loss" for _, nm, _ in clean["checks"]), \
        "clean render reported content loss"
    first_head = next(
        e["title_text"].split("|")[0].strip()
        for e in model_en["sections"]["work"]["entries"]
        if e["title_text"].strip())
    loss_rep = run_structural_qa(model_en, base_html.replace(first_head, "XXXXXXXX"))
    assert any(st == "ERROR" and nm == "content-loss"
               for st, nm, _ in loss_rep["checks"]), \
        "QA failed to flag content loss"
    for accent in ACCENT_SMOKE:
        h = render_html(model_en, accent_palette(accent), template_text, lang="en")
        assert accent in h and "[object Object]" not in h
    zh_html = render_html(model_zh, accent_palette(model_zh["accent"]),
                          template_text, lang="zh")
    assert model_zh["name"] in zh_html
    assert "工作经历" in zh_html, "zh section title missing"
    print(f"selftest PASS: fixture={FIXTURE.name} / "
          f"{c['sections']} sections / {c['entries']} entries / "
          f"{n_links} links (derived) / "
          f"{len(LANGS)} langs / "
          f"{len(ACCENT_SMOKE)} accents / "
          f"id validation / edit isolation / QA leak detection")
    return 0


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Resume JSON -> HTML -> PDF pipeline")
    p.add_argument("src", nargs="?", default=str(DEFAULT_SRC))
    p.add_argument("out", nargs="?",
                   default=None,
                   help="output directory; default: <src dir>/output")
    p.add_argument("--accent", default=None, help="override accent, e.g. #58758A")
    p.add_argument("--lang", default="en", choices=list(LANGS),
                   help="output language (localizes bilingual leaves)")
    p.add_argument("--max-pages", type=int, default=2)
    p.add_argument("--selftest", action="store_true")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.selftest:
        return selftest()
    src = Path(args.src).resolve()
    # One source of truth: the snapshot's own directory. Never fall back to
    # the skill directory, or renders from different applications mix.
    out_dir = (Path(args.out).resolve() if args.out
               else src.parent / "output")
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        raw = resolve_source(src, args.lang)
        validate_raw(raw)
    except (ResumeValidationError, json.JSONDecodeError, OSError) as exc:
        print(f"ResumeValidationError: {exc}")
        return 2
    if args.accent:
        raw = dict(raw, meta=dict(raw.get("meta", {}), accent=args.accent))
        try:
            validate_raw(raw)
        except ResumeValidationError as exc:
            print(f"ResumeValidationError: {exc}")
            return 2

    try:
        template_text = (HERE / "template.html").read_text(encoding="utf-8")
        model = normalize_resume(raw)
    except OSError as exc:
        print(f"TemplateError: {exc}")
        return 2

    html_out = render_html(model, accent_palette(model["accent"]),
                           template_text, lang=args.lang)

    stem = f"{src.stem}-{args.lang}"
    html_path = out_dir / f"{stem}.html"
    html_path.write_text(html_out, encoding="utf-8")
    print("wrote", html_path)

    pdf_path = out_dir / f"{stem}.pdf"
    if build_pdf(html_path, pdf_path):
        build_preview(pdf_path, out_dir / f"preview_{stem}.png")

    struct = run_structural_qa(model, html_out)
    pdfqa = run_pdf_qa(pdf_path, max_pages=args.max_pages, lang=args.lang)
    print_report(struct, pdfqa)
    if struct["errors"] + pdfqa["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
