---
name: resume-writing
description: >-
  Technical resume writing and independent review workflow. Use when the user
  wants to position a technical candidate, decide what evidence belongs in a
  resume, rewrite experience bullets without inventing facts, run an independent
  hiring-manager critique, or evaluate resume quality beyond surface polish.
  Works with resume-buddy snapshots, but owns content strategy and editorial
  judgment rather than rendering.
license: MIT
metadata:
  version: "0.2.0"
---

# resume-writing

A model-agnostic skill for producing technical resumes that are **credible,
specific, and useful to a hiring manager** — not merely well-written.

## 0. The non-negotiable rule

> **Never manufacture excellence through language.**

Every claim must trace to source material the candidate actually provided.
When evidence is missing, ask. Do not fill gaps with plausible-sounding detail.

The priority order is:

1. Factual accuracy.
2. Relevance to the target role.
3. Specificity and technical credibility.
4. Clarity of personal contribution.
5. Natural, professional language.
6. Conciseness.

Style never outranks facts. A beautiful sentence that overstates ownership is a
defect, not an improvement.

### 0.1 Privacy boundary

This skill is a tracked, reusable artifact. It must contain **no candidate
personal data**: no names, contact details, employer names, dates, application
IDs, URLs, raw evidence, or application-specific paths.

- Read candidate data at runtime from the gitignored `data/` root.
- Use generic placeholders such as `data/applications/<date>/<slug>/`.
- Keep examples synthetic; do not use a real candidate's project as the example.
- Application-specific facts belong in the application snapshot, not in this
  skill or its evaluation set.
- Before committing, search the files you are adding or changing for the
  candidate's name, email, phone, employers, URLs, and application IDs.

If a rule needs a real example, paraphrase it and remove identifying details.

## 1. What this skill is for

This skill separates three jobs that are often incorrectly merged:

| Job | Question | Owner |
|---|---|---|
| **Strategy** | What should be written, and why? | Hiring Strategist |
| **Writing** | How should it be expressed? | Resume Writer |
| **Review** | Why is it still not convincing? | Independent Critic |

The writer and critic must not share the same objective function. The writer
tries to express value accurately. The critic tries to find every reason a
hiring manager would remain unconvinced.

## 2. Evidence discipline

Maintain an internal evidence ledger for every bullet:

- **Claim** — what the resume says.
- **Source** — where the candidate said it.
- **Responsibility** — designed / implemented / contributed / led / maintained /
  deployed / tested / experimented.
- **Confidence** — confirmed / probable / unclear.
- **Missing information** — what would make the claim stronger.

Never invent:

- performance metrics, user counts, revenue, or business impact;
- team size, reporting lines, or ownership;
- production status, concurrency, scale, or uptime;
- technologies the candidate did not confirm;
- outcomes that cannot be defended in an interview.

Verbs are not interchangeable. “Led”, “built”, “contributed to”, “maintained”,
“tested”, and “experimented with” describe different levels of ownership.

## 3. Content strategy before writing

Analyze the target JD and identify:

1. Core technical requirements.
2. Secondary requirements.
3. Expected engineering responsibilities.
4. Relevant technologies.
5. Evidence that distinguishes this candidate.
6. Gaps or risks.

Then decide:

- the candidate's professional identity for this application;
- which experiences carry the story;
- which details prove engineering judgment rather than tool familiarity;
- what to remove because it adds noise;
- where the resume needs a targeted question instead of a guess.

A strong resume has information hierarchy. Not every experience should be
written at maximum intensity. Some entries establish context; some prove depth;
one or two prove distinctiveness.

### 3.1 Work vs projects

Use work entries for what the candidate was paid to own: scope, constraints,
collaboration, delivery and outcomes. Use project entries for independent or
additional work that shows a different capability or deeper technical design.

If the same system appears in both, keep the primary story in work and use the
project entry only for a distinct angle. Otherwise remove the duplicate. Two
descriptions of one system read as padding, not depth.

## 4. Writing rules

### 4.1 Write like an engineer, not a resume generator

Avoid generic corporate language unless the context genuinely justifies it:

- “Delivered end-to-end solutions”
- “Owned full-stack development”
- “Leveraged cutting-edge technologies”
- “Spearheaded innovative initiatives”
- “Seamlessly integrated”
- “Robust and scalable architecture”
- “Empowered business workflows”
- “Drove digital transformation”

Prefer concrete work: what was broken, what was built, what decision was made,
what changed for the system or the user.

### 4.2 Vary sentence structure

Do not force every bullet to start with Built / Developed / Implemented /
Delivered / Led. A bullet may start with:

- the engineering problem;
- the system or technical constraint;
- the candidate's responsibility;
- a technical decision;
- a concrete result.

### 4.3 Preserve technical specificity

Do not replace meaningful engineering details with abstractions.

Weak: “Developed an AI-powered enterprise knowledge management solution.”

Better: “Built a document Q&A service with separate ingestion, embedding and
agent services.”

Keep technologies that demonstrate relevant capability. Remove technologies
that are only listed to increase keyword density.

### 4.4 English style

- Clear, idiomatic engineering English.
- Avoid excessive nominalization and consulting vocabulary.
- Avoid inflated verbs.
- Keep technical terms accurate.
- Do not translate Chinese sentence structures literally.
- Write as one engineer describing work to another.

### 4.5 Chinese style

- Natural, professional Chinese — not conversational, not bureaucratic.
- Avoid “跑通”, “搞定”, “做到一半”, “推到上线” unless the context genuinely
  calls for that register.
- Avoid “基于…实现…”, “覆盖从…到…”, “赋能…”, “推动…落地”.
- Prefer direct descriptions of responsibility, implementation and result.
- Do not repeatedly insert “本人” or “由我负责”.
- Do not translate English resume phrasing word for word.

### 4.6 Information density

Every sentence must justify its space. Remove repeated technology names,
generic introductions, empty adjectives, and obvious implementation details.
Do not shorten away important engineering information.

### 4.7 AI-assisted coding

Do not treat a tool name as evidence of AI-assisted coding ability. If the
candidate has a concrete example, describe the task and the review/test step
without inventing productivity metrics. If there is no concrete example, keep
the tools in Skills only and flag the gap for interview preparation; do not
write a generic “used AI daily” bullet.

### 4.8 One-page trade-off

A one-page limit is a selection problem, not a compression problem. Remove
lower-value evidence; do not shrink type, strip technical specificity, or keep
every experience at equal length. The strongest evidence for the target role
should get the space.

## 5. Orchestration

Use this workflow for substantive resume work. For a one-line edit, skip to the
relevant stage.

### Stage 0 — Context and constraints

Read the source materials, the target JD, the existing snapshot, and the
candidate's confirmed preferences. Identify what is confirmed, what is unclear,
and what must not be changed. Do not rewrite yet.

### Stage 1 — Candidate understanding

Build a structured view of the candidate:

- roles and dates;
- actual responsibilities;
- systems built;
- technical decisions;
- scale and constraints;
- outcomes;
- evidence gaps.

### Stage 2 — Hiring strategy (separate agent)

Ask the Hiring Strategist to produce:

- JD requirement analysis;
- candidate-to-JD match;
- strongest relevant experiences;
- missing evidence;
- recommended positioning;
- section priorities;
- explicit reasons for inclusion/exclusion;
- targeted questions for the candidate.

The strategist does **not** rewrite bullets.

### Stage 3 — Resume draft (separate agent)

Give the Resume Writer:

- original factual materials;
- approved positioning;
- JD analysis;
- this skill's writing rules;
- the existing snapshot and stable IDs.

Require a complete draft plus a list of facts needing confirmation. The writer
must not invent facts or flatten technical specificity for style.

### Stage 4 — Independent review (separate agent)

The Hiring Reviewer must read the **original evidence, the JD, and the proposed
resume** — not the writer's self-evaluation. The orchestrator must not pass the
writer's rationale, change summary, or self-defense into the critic prompt. Ask
it to identify:

- generic or AI-sounding sentences;
- weak engineering evidence;
- missing technical details;
- unsupported claims;
- duplicated content;
- poor information prioritization;
- unconvincing professional positioning;
- sections that fail to differentiate the candidate.

Require sentence-level criticism and suggested evidence, not a full rewrite.

### Stage 5 — Targeted revision

Return valid criticism to the writer. Preserve verified facts. Reject changes
that invent achievements, exaggerate ownership, remove important technical
evidence, or introduce marketing language. Limit review/revision to two
substantive rounds unless a critical problem remains.

### Stage 6 — Delivery QA

Check, separately:

**Content QA**
- factual accuracy;
- responsibility attribution;
- English/Chinese parity;
- dates and chronology;
- technical terminology;
- JD relevance;
- duplication between work and projects.

**Layout QA**
- page count;
- ATS readability;
- PDF rendering;
- CJK font;
- links.

A one-page PDF with zero formatting errors is not automatically a good resume.

## 6. Prompt templates

### 6.1 Hiring Strategist

> You are a hiring strategist for technical roles. You are not a resume writer.
>
> Read the candidate's original evidence, the target JD, and the current resume.
> Produce:
> 1. The role's real evaluation criteria, not just keyword matches.
> 2. A candid candidate-to-JD match.
> 3. The three strongest pieces of evidence.
> 4. The weakest or most generic parts.
> 5. A recommended professional identity for this application.
> 6. Section-by-section content priorities.
> 7. Explicit inclusion/exclusion decisions and why.
> 8. Targeted questions that would unlock missing evidence.
>
> Do not rewrite bullets. Do not invent facts. Be specific about what a hiring
> manager would doubt.

### 6.2 Resume Writer

> You are a technical resume writer and editor. Your job is not to make the
> candidate sound impressive; it is to make their actual engineering work
> legible, credible, and relevant.
>
> Follow the evidence ledger and writing rules in this skill. Preserve verified
> facts and important technical details. Vary sentence structure. Prefer
> concrete engineering facts over adjectives. Write natural English and natural
> Chinese, not translations of each other.
>
> Produce a complete draft and a list of claims that still need confirmation.
> Never invent metrics, ownership, scale, production status, or technologies.

### 6.3 Independent Hiring Critic

> You are an extremely critical engineering hiring manager. You are not a
> resume writer.
>
> Read the original evidence, the target JD, and the proposed resume. Do not
> rely on the writer's explanation.
>
> For every bullet, evaluate:
> 1. Is this a real engineering achievement or merely a task description?
> 2. Does it contain specific, verifiable information?
> 3. Can I understand what the candidate personally contributed?
> 4. Does it demonstrate engineering judgment or technical depth?
> 5. Is the wording abstract, inflated, repetitive, or AI-generated?
> 6. Could hundreds of other engineers write exactly the same sentence?
> 7. Is an important technical detail missing?
> 8. Is this information worth the space?
>
> For each weak bullet, give:
> - the original sentence;
> - the specific problem;
> - why a hiring manager would remain unconvinced;
> - what evidence would improve it;
> - one conservative revision using only existing facts.
>
> Do not praise grammar. Do not rewrite the whole resume. Do not invent metrics.
> Be direct, skeptical, and evidence-driven.

## 7. Evaluation rubric

Score each dimension 1–5, separately. Do not collapse them into one score.

| Dimension | Question |
|---|---|
| **Content quality** | Are there engineering facts worth a hiring manager's attention? |
| **Expression quality** | Is it natural, clear, precise, and professional? |
| **Hiring value** | Does each item help this candidate get an interview? |

Hard gates:

- Any invented fact: fail.
- Any unverifiable metric presented as fact: fail.
- Wrong ownership level: fail.
- One-page constraint violated for a one-page application: fail.
- Candidate personal data present in a tracked skill file: fail.

A sentence can be beautifully written and still score 1 on hiring value. That
is a useful result, not a contradiction.

## 8. Integration with resume-buddy

- Personal data and application snapshots live under the gitignored `data/`
  root. Never put candidate data into tracked files.
- The complete resume JSON is the unit of editing; stable IDs are preserved.
- Do not modify `data/base/base.json` without explicit user authorization.
- Application-specific work goes under
  `data/applications/<date>/<slug>/`.
- Render and QA with `skills/resume-buddy/scripts/render.py`; content decisions
  remain this skill's responsibility.
- When a rewrite changes content, show the user what changed and why. A prose
  rewrite is still a content change.

### 8.1 Privacy check before committing

Search tracked skill files for the candidate's name, email, phone, employer
names, project URLs, application IDs, and raw evidence. The evaluation set may
reference paths under `data/` only with placeholders. If a real example is
needed, paraphrase it and remove identifying details.

## 9. Deliverables and stop conditions

When running the full workflow, produce:

1. Final resume in the requested language(s).
2. A short change summary: what changed and why.
3. Unresolved factual questions, separated from prose decisions.
4. Reviewer findings, including rejected criticism and why.
5. QA result: content checks, page count, rendering, ATS/CJK.

Stop conditions:

- Stop after two substantive review/revision rounds unless a hard-gate issue
  remains.
- Stop when the remaining feedback is only personal style preference.
- Stop when the next improvement requires facts the candidate has not provided.
  Ask for the facts; do not fill the gap with language.

## 10. Final principle

The best resume is not the one that sounds most impressive.

It is the one that lets a hiring manager quickly understand:

- what this candidate can actually do;
- what they have actually built;
- what engineering problems they can solve;
- what makes them different from other candidates.

Be precise. Be credible. Be specific. Never manufacture excellence through
language.
