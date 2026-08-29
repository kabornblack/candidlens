# Trajectory — README Build (run 1)

## Verbatim prompt

> Task: Build the project README.md at the repo root.
>
> This is the most important document for judges — draft it using ONLY
> material that already exists in this project (don't invent anything new).
> Pull from:
> - data/jd.md (the role)
> - data/human_reference_ranking.md (the human reviewer's scoring methodology)
> - eval/results.md (the measured improvement numbers)
> - The four solution/*.py files and their trajectories (for describing the pipeline architecture)
> - baseline/baseline.py (for describing what the baseline is)
>
> Structure the README as:
> 1. Title + one-line description: "CandidLens — an evidence-grounded candidate evaluator for backend engineering roles"
> 2. Who has this problem / the bottleneck / why it matters
> 3. What CandidLens does — 4-stage pipeline in plain language, explaining WHY each stage exists
> 4. The baseline — one paragraph, why it's intentionally simple
> 5. Measured Improvement — pull actual numbers from eval/results.md verbatim, as a table
> 6. Improvement Changelog — built from actual trajectory history, real entries; note removed/rejected approaches
> 7. Main failure mode + Hot Take (5 points) — ceiling compression; Marcus judgment-severity divergence; genuine takeaway
> 8. Setup / Tech stack — Python, Anthropic API (claude-sonnet-5 consistent), python-dotenv; link docs/reproduction.md
> 9. Project structure — brief tree
> 10. Disclosure: coding agent = Claude Code (claude.ai subscription for dev; Anthropic API for runtime). Link trajectories/.
>
> Write this as a draft for my review — I may want to adjust tone/wording,
> especially sections 2 and 7 which should sound like my voice, not overly formal.
>
> Log this in trajectories/readme_build_run1.md per the agent instructions.

## Plan / reasoning

- Draft only; user reviews tone (esp. §2 and §7 — keep those plainer / first-person-ish, flag them).
- Source material only — no invented facts. Sources read this task:
  - `README.md` (existing) — a 2-line stub ("# candidlens / CandidLens, evaluating candidates transparently"). Replacing a stub with the full draft; noting the replacement to the user.
  - `data/jd.md` — Mid-Level Backend Engineer, 3–5 yrs; 5 eval categories (Python/Go, REST API design, SQL/data modeling, cloud infra, ownership & collaboration).
  - `data/human_reference_ranking.md` — 3 explicit methodology rules: Credibility/Integrity Cap, Behavioral/Collaboration Discount, JD-Critical Category Weighting; per-candidate Overall scores; Final Ranking list.
  - `eval/results.md` — the numbers (MAE 0.400 vs 0.500; excl. candidate_03 0.278 vs 0.500; Spearman 0.859 vs 0.792; positions off by >1: 0 vs 5; candidate_03 contradiction: agent flags with cited evidence, baseline has no field).
  - `baseline/baseline.py` — one flat prompt (JD + full candidate file → JSON 5 category scores + overall), no evidence/cross-check/discrepancy, `max_tokens=1024`.
  - `solution/{extract,crosscheck,score,aggregate}.py` — the 4 stages; `MODEL = "claude-sonnet-5"` identical in all + baseline.
  - Trajectories `baseline_build_run1.md`, `extract_build_run1.md`, `crosscheck_build_run1.md`, `score_build_run1.md`, `eval_build_run1.md` — for the changelog (real Retry history).
  - `.env.example` (single `ANTHROPIC_API_KEY` line), `.gitignore` (`.env` ignored), `docs/reproduction.md` (currently empty — link it as "full setup, built next").
- Changelog entries, each = what was tried / what evidence showed the problem / what was decided:
  1. Baseline established — model corrected Opus 5 → Sonnet 5 (Retry 2) for a fair same-model comparison; full run showed top/bottom right but a 6-way overall-3 tie in the middle and no contradiction detection on Marcus.
  2. Extraction v1 → v2 — `max_tokens=2048` truncated candidate_01's JSON (`Unterminated string`, run failed on candidate 1); raised to 8192 + added a `stop_reason == "max_tokens"` guard that names the candidate.
  3. Extraction prompt fix — candidate_03 test leaked conclusions into raw claims ("Response contradicts the CV claim of leading a team", "…not corroborated", "Actual level looks like a competent mid-level IC"); added a CRITICAL BOUNDARY block + banned vocabulary + KEEP/DROP worked examples; re-test confirmed conclusions gone, evidence retained.
  4. Crosscheck v1 → v2 — full run over-called `contradicted` on "listed skill + limited interview depth": candidate_06 PostgreSQL (needed a hint on a window function), candidate_09 AWS (less sure on IaC), candidate_02 SQLite (stuck on a join); and applied it inconsistently (candidate_07's worse SQL demo not flagged). Fix: `contradicted` requires actual inability / active incompatibility, and the model must check for supporting interview evidence first; worked PostgreSQL example. Contradiction count 6 → 3; Marcus's 2 real contradictions untouched.
     - Rejected/kept: considered dropping candidate_09's "Quillstone 1.5 yr vs 'none over ~14 months'" flag as over-strict — **kept** it: it's a literal numeric conflict, a different class from the skill-depth false positives, and the fix was scoped to leave it in place.
  5. Scoring v1 → v2 — full run showed (a) Tomasz over-penalised: rule 4 (standalone collaboration red flags) was hitting as hard as rule 5 (integrity cap), pulling a 3.8-technical-average to overall 3 vs the human's 4.0; (b) Dylan under-penalised: CV skill claims marked "uncorroborated" got "no penalty" even where the interview showed demonstrated inability ("couldn't do a two-table join", "never deployed anything"). Fix: rule 3 now says demonstrated failure must pull the category down regardless of the crosscheck label; rule 4 is now an explicit *moderate* discount, softer than rule 5; rule 5 is reserved for CV/interview contradictions. Result: Tomasz overall 3 → 4 (matches human); demonstrated-failure reasoning now explicit in the Dylan / Sistine / Rohan rationales.
     - Model choice: `claude-sonnet-5` fixed across baseline + all 4 stages (constant + comment in every file) specifically so the comparison isn't confounded by model.
- §7 failure mode / hot take: ceiling compression (no overall 5, five tie at 4) — documented as known/accepted in `score_build_run1.md`; Marcus severity divergence (agent 1 vs human 2.5) — deliberate, a real tunable (how far below raw average the cap pulls); takeaway about calibrating the verifier + separating extraction from judgment + the eval harness making iteration possible.
- §8 disclaimer link to `docs/reproduction.md` (to be built next).

## Tool calls

- `Glob **/*` → repo layout; confirmed existing `README.md` is a 2-line stub, `docs/reproduction.md` empty, `.env.example` present.
- `Read README.md` → 2-line stub (safe to replace with the full draft).
- `Read docs/reproduction.md` → empty.
- `Read .gitignore` → `.env` is ignored (line 151); no secrets will be committed.
- `Read .env.example` → single `ANTHROPIC_API_KEY=...` line.
- (Prior tasks already read jd.md, human_reference_ranking.md, eval/results.md, all solution/*.py, baseline/baseline.py, and every trajectory — reused from context.)
- `Write trajectories/readme_build_run1.md` → this file.
- `Write README.md` → full draft (replaces the 2-line stub).

## Final result

Replaced the 2-line `README.md` stub with a full 10-section draft built entirely from existing project material:
- Title + one-liner; problem statement (§2, plainer voice — flagged for user); 4-stage pipeline with per-stage "why" (§3); baseline description (§4); Measured Improvement table with the verbatim `eval/results.md` numbers (§5); Improvement Changelog with 5 real entries + 2 noted rejected/kept decisions drawn from the trajectories (§6); Main failure mode + Hot Take (§7, plainer voice — flagged); Setup / Tech stack pointing at `docs/reproduction.md` (§8); repo tree (§9); Claude Code disclosure + `trajectories/` link (§10).
- Nothing invented — every number, rule, and changelog entry traces to a file in the repo.
- Draft only; §2 and §7 explicitly called out to the user as the tone-adjust candidates.

---

## Retry 2

### Verbatim prompt

> Four small edits to README.md:
>
> 1. In the hot take section, change "We named this explicitly" to "I named this explicitly" for first-person consistency with the rest of the doc.
>
> 2. In the takeaway paragraph, replace "the only reason those failures were visible is the eval harness and the trajectory logs" with "the only reason those failures were visible is that every stage was tested and reviewed before moving to the next one, with the full history kept in the trajectory logs" — the eval harness only existed at the very end, so the original wording overclaims its role in catching the earlier bugs.
>
> 3. Add a new "## Scope and human oversight" section, placed after "The problem" and before "What CandidLens does": [text: hackathon-built; decision-support not decision-maker; final call stays with a human; ground truth is a human ranking not another model].
>
> 4. In the Setup section, change the single "cp .env.example .env" line to show both cp (macOS/Linux) and copy (Windows).
>
> Log this as Retry 2 in trajectories/readme_build_run1.md.

### Plan / reasoning

Four targeted edits. The user had already reformatted `README.md` on disk (tables realigned, `*italics*` → `_italics_`) — worked from the current on-disk state, matched exact strings. Edit 2 is a factual correction the user caught: the eval harness (`eval/run_eval.py`) was built last, so it couldn't have surfaced the extraction/crosscheck/scoring bugs — those were caught by per-stage test-and-review. Edit 3 inserts a new section between "The problem" and "What CandidLens does". No invented content — the new section restates project facts (hackathon-built, human ground truth in `data/human_reference_ranking.md`, decision-support framing).

### Tool calls

- `Read README.md` (current on-disk state, §§ setup / structure / disclosure and the hot-take/takeaway paragraphs) → exact strings for the edits.
- `Edit README.md` ×4:
  1. hot take: "We named this explicitly" → "I named this explicitly".
  2. takeaway: "…visible is the eval harness and the trajectory logs." → "…visible is that every stage was tested and reviewed before moving to the next one, with the full history kept in the trajectory logs."
  3. inserted `## Scope and human oversight` section (verbatim from the user's prompt) after "The problem", before "What CandidLens does".
  4. setup: single `cp .env.example .env` line → two lines, `cp` (macOS/Linux) + `copy` (Windows).

### Final result

All four edits applied to `README.md`. First-person voice now consistent in §7; the takeaway no longer overclaims the eval harness's role in early bug-catching; a new "Scope and human oversight" section sets the decision-support framing and notes the human-ranking ground truth; the setup block shows both the macOS/Linux and Windows env-file copy commands. Still a draft pending final user sign-off.
