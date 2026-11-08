# Renderer reference

Operational detail for the deterministic Python pipeline. For *when* and
*whether* to render, see `SKILL.md` §6.

## Pipeline

```text
source.json
  -> localize(lang)
  -> validate (schema, unique stable ids)
  -> normalize (semantic model)
  -> one Jinja template
  -> HTML
  -> Chromium
  -> PDF
  -> preview PNG
  -> QA
```

There is no overlay/resolver layer, placement file, theme registry, or
template selector. A source file is a complete resume snapshot.

## Commands

Run from the skill root (`skills/resume-buddy/`). Scripts carry PEP 723
metadata, so `uv run` resolves dependencies automatically.

```bash
uv run scripts/render.py --selftest
uv run scripts/render.py fixtures/sample.json out/ --lang en
uv run scripts/render.py <snapshot.json> <out>/ --lang zh
```

| Flag | Default | Notes |
|---|---|---|
| `src` | `fixtures/sample.json` | complete resume JSON |
| `out` | `<src dir>/output` | directory, created if missing |
| `--lang` | `en` | `en` or `zh`; localizes bilingual leaves |
| `--max-pages` | `2` | QA fails above this |
| `--accent` | from `meta.accent` | e.g. `--accent #58758A` |
| `--selftest` | — | fixture regression suite |

Exit codes: **`0`** pass · **`1`** QA errors · **`2`** schema or render error.

## Input

- **Bilingual leaves**: a translatable value is a plain string or
  `{"en": ..., "zh": ...}`.
- **Stable ids**: every entry and every bullet has an `id`; ids are unique
  within the document. The schema rejects missing, duplicate, or legacy
  plain-string bullets.
- **Snapshot**: a complete resume file. Tailoring edits a snapshot with
  `edit.py`; it does not inherit from another file at render time.
- **`meta.accent`**: optional hex color; `--accent` overrides it.

## Output

Named from the source stem:

```text
<stem>-<lang>.html
<stem>-<lang>.pdf
preview_<stem>-<lang>.png
```

All pages are stacked vertically into one preview PNG.

## QA

**Structural** (always): `name`, `sections`, `entries`, `empty-section`,
`unsafe-links`, `content-loss`, `forbidden-literal`.

**PDF** (needs `pymupdf`): `pdf-exists`, `page-count`, `density`, and
`cjk-font` when `--lang zh`.

Reading the report:

- Trust the **exit code**, not individual PASS lines.
- Any `ERROR` is blocking; `WARN` is advisory.
- `content-loss` compares entry titles, skill labels, contact emails and DOI
  values against the rendered visible text and hrefs. A miss is an ERROR.
- `density` WARN = last page under 15% of the text. Fix by trimming content,
  never by shrinking type.
- `cjk-font` ERROR = no CJK face embedded; install a CJK font on the machine
  rather than editing the resume.

## Determinism

- **HTML**: byte-deterministic for the same JSON, template and flags.
- **PDF**: content, text and page layout are stable; PDF bytes are **not**
  promised identical because metadata timestamps can differ.
- **Preview PNG**: useful for visual checks; pixel identity across
  environments is not promised.

## Environment

- Python ≥ 3.13 and `uv`. Dependencies are declared inline (PEP 723) at the
  top of `scripts/render.py`; `uv run` creates an isolated environment.
- PDF uses headless Chromium: Chrome or Edge, auto-detected, overridable with
  `CV_EDGE_BIN`.
- Preview PNG needs `pillow`; without it the PNG step is skipped.
- CJK output depends on **system** fonts; no font files ship in the repo.

## Limitations

- The renderer does not judge content quality, only whether it survived.
- No theme, template, or placement selection; one layout and one accent.
- No overlay inheritance; snapshots are complete files.
- No DOCX/ATS output and no network access.
- `edit.py` is the recommended write path, but it is not a permission system:
  it checks the edits it performs, not every write on the machine.
