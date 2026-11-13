---
name: resume-buddy
description: >-
  Local-first resume skill. Use when the user wants to maintain a base resume,
  analyze a job description against real evidence, tailor a complete resume
  snapshot, edit one bullet by stable id with diff-and-confirm, render a PDF
  through a deterministic Python pipeline, or record a job application.
  Triggers include resume, CV, curriculum vitae, job description, JD, job
  posting, tailoring a resume, and job applications. All personal data stays
  on the user's machine; nothing personal is ever written into this repository
  or transmitted anywhere.
license: MIT
compatibility: >-
  Requires Python 3.13+ and uv (bundled scripts are PEP 723 self-contained).
  PDF output requires a Chromium/Edge browser; zh rendering requires a system
  CJK font. The scripts perform no network access; `uv` may fetch declared
  dependencies on first run, after which rendering works offline.
metadata:
  version: "1.0.0"
---

# resume-buddy

## 0. The one non-negotiable rule

> **AI does not own the resume.**
>
> AI may propose changes. A change is written to the real resume **only after
> the user confirms it**. **Anything the user did not name must stay
> unchanged.**

Every rule below exists to make that sentence mechanically true where the
code can enforce it, and explicit where only the conversation can.

For content strategy, technical writing rules, and independent hiring review,
use the companion `resume-writing` skill
(`skills/resume-writing/SKILL.md`). This skill owns data integrity, snapshots,
rendering, and QA; that skill owns editorial judgment.

---

## 1. Two workflows

Pick by intent; they can chain in one conversation.

| Workflow | User goal | Writes |
|---|---|---|
| **Capture** | Maintain the long-term base resume and remember raw source material | `base/raw/`, then `base/base.json` after confirmation |
| **Tailor** | Analyze a JD, make a complete snapshot, edit, render, QA | `applications/<date>/<slug>/` |

**Record** is optional, not a workflow: append one row to `applications.md`
when the user reports an application.

---

## 2. Data layout

All personal data lives under one gitignored root, `data/`, at the repository
root:

```
data/                            # gitignored; never commit
├── base/
│   ├── raw/                     # verbatim user input, append-only
│   │   └── <date>-<label>.md
│   └── base.json                # long-term base resume
├── applications/
│   └── <YYYY-MM-DD>/            # one directory per application day
│       └── <slug>/              # one directory per application
│           ├── jd.md            # JD text + evidence analysis
│           ├── snapshot-01.json # complete snapshot; each edit writes 02, 03…
│           └── output/          # rendered HTML / PDF / preview PNG
└── applications.md              # optional: one row per application
```

- **The application directory is the unit of work and of statistics.**
  `applications/<date>/<slug>/` keeps the JD, every snapshot version and its
  render together. Counting the `<slug>` directories under a date gives that
  day's application count; counting dates gives the active days.
- **`base.json` is the long-term base resume**, not a separate fact database.
  A **snapshot is a complete copy** for one application; it does not inherit
  from base at render time. Tailor edits only snapshots; change base only when
  the user explicitly asks, and keep a dated copy first.
- Always pass the application's own `output/` to the renderer; never let
  renders from different applications share one output directory.
- Never commit `data/`; never put a real name, email, phone, employer,
  school, GPA, publication or date into a tracked file; never transmit
  personal data. This skill has no network step. The root is fixed at
  `data/` — do not reintroduce a second data root such as `~/.resume-buddy`.
- **Installed skill vs. data root.** Copying this skill into
  `~/.claude/skills/` or `~/.config/opencode/skills/` only makes it
  discoverable; it does not move the data root. Keep one clone as the
  project home and read/write `data/` there. Pass absolute paths to the
  scripts, or run them from that clone. Never create `data/` inside the
  global skill directory.

---

## 3. Capture

1. Write the user's input **verbatim** to `base/raw/`; never edit or "improve" it.
2. Propose structured entries/bullets with stable ids.
3. Walk the user through them; revise on feedback.
4. Only on explicit confirmation, update `base/base.json`.
5. Report what changed, by id.

Rules:

- **Never invent** experience, responsibility, technology, number, scale or
  outcome. A gap is a question, not content.
- **Fact ≠ phrasing.** `base.json` stores the canonical statement; a snapshot
  may phrase it for one JD. Do not overwrite the base with a tailored wording.
- Every entry and bullet keeps a stable id (`work.4s`, `work.4s.b2`, …).
  Missing or duplicate ids are rejected by the schema.

---

## 4. Evidence (JD analysis)

For each concrete JD requirement, use exactly three states:

| State | Meaning | Action |
|---|---|---|
| `EVIDENCED` | A base entry/bullet supports it | cite the id |
| `GAP` | No evidence found in the base | ask the user; it may be unrecorded |
| `ABSENT` | User confirms they do not have it | must not appear in the resume |

`GAP` and `ABSENT` are different claims. Treating `GAP` as `ABSENT` hides
experience; treating `ABSENT` as `GAP` invites fabrication. This rule applies
to JD requirements, not to every field in the data file.

Save the JD verbatim to `applications/<date>/<slug>/jd.md`, then append the
requirement analysis there. Do not copy the JD into `applications.md`.

---

## 5. Editing a snapshot

This is the strictest section. Follow it in order, every time.

1. **Locate by id, never by position or text match.**
   Targets are an entry id (`work.4s`) or a bullet id (`work.4s.b2`). If the
   target has no id, or the id is duplicated, **stop** and report it.
2. **Name the scope before touching anything.** State which ids change and
   which ids must not.
3. **Show the diff first.** Present old → new for each named id, and nothing
   else. Show both languages when the text is bilingual.
4. **Wait for explicit confirmation.** No confirmation ⇒ no write. Silence,
   ambiguity, or an earlier blanket "go ahead" is not confirmation for a new
   change.
5. **Run `edit.py`, write a new snapshot.** Never edit a confirmed snapshot in
   place and never overwrite an existing file:
   ```bash
   uv run scripts/edit.py <snapshot.json> \
     --id work.4s.b2 --expect "<old text>" --new "<new text>" \
     --lang en --out <new-snapshot.json>
   ```
   `edit.py` refuses a missing/duplicate id, a mismatched `--expect`, a
   no-op change, an existing `--out`, and any diff outside the target leaf.
   It validates the edited document in both languages.
6. **Render and QA.** Read the exit code and treat any `ERROR` as blocking.
7. **On approval, the new snapshot is confirmed.** Keep it as a new file; the
   previous version remains untouched.

`edit.py` is the **only recommended editing path**, not an absolute security
boundary: another tool could still write a file directly. The guarantees are
therefore: this path checks the rules mechanically, and confirmed snapshots
are new files rather than in-place edits. `edit.py` currently covers bullets;
entry-level fields (company, dates) use the same scope/diff/confirm discipline
manually.

**No overlays, no field overrides.** A snapshot is complete; do not replace a
whole `highlights` array to change one bullet.

---

## 6. Working with the renderer

The AI decides **what** the content says and confirms changes; the renderer
decides **how** it is laid out. Never hand-craft HTML/CSS; never rewrite or
invent facts.

Commands (run from the skill root):

```bash
# regression check — run after touching Python or the template
uv run scripts/render.py --selftest

# render a snapshot; artifacts default to <snapshot dir>/output/
uv run scripts/render.py <application dir>/snapshot-01.json --lang en
uv run scripts/render.py <application dir>/snapshot-01.json --lang zh

# the public synthetic fixture also renders without an explicit out dir
uv run scripts/render.py fixtures/sample.json --lang en
```

Flags: `--lang en|zh`, `--max-pages N` (default 2), `--accent #RRGGBB`.

Outputs, named from the source stem: `<stem>-<lang>.html`,
`<stem>-<lang>.pdf`, `preview_<stem>-<lang>.png`.

QA: exit `0` pass, `1` QA errors, `2` validation/render error; any `ERROR`
blocks. Determinism: HTML is byte-stable; PDF content/text/layout are stable
but bytes may differ; preview PNG is not pixel-guaranteed. Details in
`references/renderer.md`.

---

## 7. Tailor workflow

1. Identify the target JD and the base resume.
2. Create `applications/<YYYY-MM-DD>/<slug>/` and copy
   `base/base.json` to `snapshot-01.json` there. The date is the application
   day; one directory per day and per application.
3. Classify each JD requirement as `EVIDENCED` / `GAP` / `ABSENT`; interview
   every `GAP`.
4. Edit via §5: show the diff, wait for confirmation, run `edit.py` with
   `--out applications/<date>/<slug>/snapshot-02.json`, render into that
   directory's `output/`, and QA.
5. On approval, keep the snapshot. Optionally append one row to
   `applications.md`.

Do not modify `base.json` during tailoring; a base update is a separate
Capture request.

---

## 8. Reference and limits

Detailed renderer/QA mechanics live in `references/renderer.md`.

Not implemented — say so rather than improvising: automated fact extraction,
diff UI, lock enforcement, DOCX/ATS/network, theme/placement selection, and
overlay inheritance. There is one template and one accent; snapshots are
complete files. A synthetic fixture exists, so `--selftest` works on a fresh
clone.
