---
name: resume-writing-evaluation
description: Evaluation set and rubric for the resume-writing skill. Use when changing models, prompts, or the writer/reviewer workflow, to check whether resume quality actually improved rather than only becoming more polished.
---

# Resume-writing evaluation set

This is a regression suite, not a style guide. Use it after any change to the
writer prompt, reviewer prompt, model, or orchestration. The goal is to detect
whether the system still produces **credible engineering evidence**, not merely
better prose.

All candidate data stays under the gitignored `data/` root. This file contains
role profiles and evaluation criteria only — no names, contact details,
employers, dates, URLs, application IDs, or raw evidence.

## 0. Privacy boundary

- Use the current JD and snapshot under `data/` at evaluation time; do not copy
  their contents into this file.
- Refer to application data with placeholders such as
  `data/applications/<date>/<slug>/`.
- Keep role profiles synthetic. If a real case is useful, paraphrase it and
  remove the candidate's identity and project-specific details.
- A privacy failure is a hard-gate failure: if a tracked skill file contains
  candidate personal data, the change is rejected.

## 1. Evaluation cases

### Case A — Startup full-stack (primary)

**Role profile**
- 1–3 years experience.
- Node.js + TypeScript, React, SQL/ORM, REST/tRPC.
- AI-assisted coding expected.
- Product ownership and shipping matter more than large-company pedigree.
- One page.

**Evaluation input**
- Use the current JD and snapshot under the gitignored `data/` root.
- Do not copy their contents into this file.

**Expected positioning**
- Full-stack engineer who can take a product from unfinished to shipped.
- AI systems experience is an advantage, not the identity.

**Must preserve**
- Node/TypeScript + React full-stack delivery.
- A real product context and ownership.
- Auth, caching, tests, CI/CD, cloud and reverse proxy only if confirmed.
- At least one distinctive AI/infrastructure fact (e.g. real-time inference,
  retrieval service split, tool orchestration).

**Must not claim**
- Big-company scale or team leadership not evidenced.
- Production metrics or concurrency that cannot be defended.
- “AI-native” or “end-to-end” as substitutes for concrete work.

### Case B — AI systems engineer

**Role profile**
- Python, FastAPI, RAG, vector search, model serving, Docker/Linux.
- Emphasis on inference pipelines, service boundaries, and deployment.
- Less emphasis on frontend breadth.

**Expected positioning**
- Engineer who builds and operates AI services, not a model researcher.

**Must preserve**
- RAG ingestion/embedding/retrieval/answer chain.
- Service boundaries and deployment constraints.
- Real-time vision pipeline details and GPU deployment constraints.
- Concrete data/scale facts only if confirmed.

**Must not claim**
- Model training or research contributions not evidenced.
- Latency/throughput numbers that were not measured.

### Case C — AI application engineer

**Role profile**
- Product-facing AI: agent tools, SSE/streaming, frontend integration, UX.
- TypeScript/React plus Python services.
- Ability to connect model behavior to a usable product.

**Expected positioning**
- Product engineer who can wire AI capabilities into a real interface.

**Must preserve**
- Natural-language tool orchestration.
- Streaming/progress behavior.
- Map or UI integration.
- The user-facing problem, not only the model stack.

**Must not claim**
- Product usage or retention metrics.
- Agent capabilities that were not implemented.

### Case D — Portability and privacy

**Purpose**
- Verify the skill is reusable beyond one candidate.

**Pass criteria**
- The workflow can run with a different candidate and JD without editing the
  skill's rules.
- No tracked skill file contains candidate names, contact details, employers,
  dates, URLs, application IDs, or raw evidence.
- Examples in the skill are synthetic or sufficiently paraphrased.
- The evaluation set uses role profiles and placeholders, not a real candidate's
  record.

**Fail**
- The skill depends on one candidate's project, employer, or application path.
- A real resume or personal data is embedded in a tracked file.

## 2. Hard gates

A revision fails if any of these are true:

- [ ] A fact, metric, technology, title, date, or ownership claim is invented.
- [ ] “Led” is used where the evidence says “contributed” or “built”.
- [ ] Theoretical scale is presented as measured concurrency.
- [ ] Work experience and projects describe the same system twice without
      distinguishing the angle.
- [ ] Chinese and English versions disagree on a fact.
- [ ] One-page requirement is violated for a one-page application.
- [ ] The candidate's confirmed preferences are silently overridden.
- [ ] A tracked skill file contains candidate personal data.

## 3. Scoring

Score each dimension independently, 1–5.

### Content quality
- 1: Generic duties; no engineering evidence.
- 3: Real work, but mostly task description.
- 5: Clear problem, technical decision, personal contribution, and result.

### Expression quality
- 1: Translated, inflated, repetitive, or AI-sounding.
- 3: Clear but conventional.
- 5: Natural, precise, varied, and specific to this engineer.

### Hiring value
- 1: Could be removed without weakening the application.
- 3: Relevant but not differentiating.
- 5: Makes the candidate easier to shortlist or interview.

Do not compute an overall score. A resume can be a 5 in expression and a 2 in
hiring value; that is exactly the failure mode this rubric is designed to catch.

## 4. Anti-AI-ism checklist

Flag any resume that relies on:

- repeated bullet openings (Built / Delivered / Led / Implemented);
- “end-to-end”, “full-stack delivery”, “robust”, “seamless”, “scalable”,
  “cutting-edge”, “AI-native” without concrete support;
- triads of abstract nouns;
- technology lists with no engineering decision attached;
- Chinese translationese (“把…推进到…”, “基于…实现…”, “覆盖…到…”);
- every bullet at maximum intensity;
- adjectives doing the work that evidence should do.

## 5. Regression procedure

0. Run the privacy check: no candidate PII in tracked skill files.
1. Freeze the source facts and JD.
2. Generate a new snapshot with the current writer/orchestrator.
3. Run the Independent Hiring Critic on the new snapshot **without** the
   writer's explanation.
4. Score the three dimensions.
5. Compare with the previous snapshot on the same cases.
6. Accept the change only if content quality and hiring value improve, or if
   expression improves without losing technical specificity.
7. Record unresolved factual questions separately. Do not fill them with prose.

## 6. What “better” means

A better resume should show at least three of:

- a clearer professional identity;
- stronger evidence of engineering judgment;
- fewer generic sentences;
- less duplication between sections;
- more distinctive, verifiable details;
- a shorter distance between “what the candidate says” and “what an interviewer
  can probe”.

If the new version is merely smoother, it did not improve.
