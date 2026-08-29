# Trajectory — Reproduction Guide Build (run 1)

## Verbatim prompt

> Task: Build docs/reproduction.md — the detailed reproduction guide.
>
> Purpose: written for someone starting from a completely clean environment
> (a judge who has never seen this repo). Should be more granular than the
> README's brief setup section — exact commands, in order, with what to
> expect at each step.
>
> Structure:
> 1. Prerequisites: Python 3.12+, an Anthropic API key (their own — note this
>    costs a small amount, ballpark the actual cost from what we've spent so far)
> 2. Clone + install (mention venv as optional best practice)
> 3. API key setup: copy .env.example to .env (both OS variants), add key
> 4. Run order, one command at a time, each with: exact command; file(s) produced;
>    rough time + API-call count (baseline=10, extract=10, crosscheck=10, score=10,
>    aggregate=0, eval=0); what a successful run looks like in the console
> 5. Where to look at results: eval/results.md (main comparison), solution/final_report.md
> 6. Approximate total cost for a full run based on claude-sonnet-5 pricing + observed usage
> 7. Troubleshooting: the two real errors (max_tokens truncation guard; anthropic-workspace-id
>    error from an identity-scoped key)
>
> Keep this document purely instructional — no narrative, no changelog.
>
> Log this in trajectories/reproduction_build_run1.md per the agent instructions.

## Plan / reasoning

- `docs/reproduction.md` currently exists but is empty — filling it is the task.
- Purely instructional; no narrative/changelog (that lives in README + trajectories).
- Real numbers to use:
  - API calls per stage: baseline 10, extract 10, crosscheck 10, score 10, aggregate 0 (pure Python), eval 0 (pure Python).
  - Console success strings — taken verbatim from the actual runs this project did:
    - baseline: `Scoring candidate_01...` … `Wrote 10 results to ...\baseline\baseline_results.json`
    - extract: `Extracting candidate_01...` … `Wrote 10 extractions to ...\solution\extracted_claims.json`
    - crosscheck: `Cross-checking candidate_01...` … `Wrote 10 crosscheck results to ...\solution\crosscheck_results.json`
    - score: `Scoring candidate_01...` … `Wrote 10 score results to ...\solution\score_results.json`
    - aggregate: `Wrote ...\final_report.json` / `Wrote ...\final_report.md` + the ranked 1–10 list
    - eval: prints the full report, ends `(written to ...\eval\results.md)`
  - Model + pricing: `claude-sonnet-5`, $2.00 / 1M input tokens, $10.00 / 1M output tokens (from the claude-api skill's model table).
  - Cost estimate (per-call token ballpark from the prompt sizes + observed output sizes):
    - baseline: ~1.3k in / ~0.1k out per call → 10 calls ≈ 13k in / 1k out ≈ $0.04
    - extract: ~1.4k in / ~1.4k out per call → ≈ 14k in / 14k out ≈ $0.17 (output-heavy; this is the stage that hit the 2048 truncation in dev)
    - crosscheck: ~3k in / ~0.9k out per call → ≈ 30k in / 9k out ≈ $0.15
    - score: ~3.5k in / ~0.7k out per call → ≈ 35k in / 7k out ≈ $0.14
    - aggregate + eval: $0
    - **Full clean run total ≈ $0.45–$0.55; call it well under $1.** Development (many reruns, a failed extract + retry, two crosscheck full runs + a subset, two score full runs + a subset, single-candidate tests) spent roughly 3–4× that — a couple of dollars total.
  - Timing: each 10-call stage completed in ~1–3 minutes in practice; aggregate and eval are effectively instant.
- venv: mention as optional best practice, `python -m venv .venv` + activate (both OS), then `pip install -r requirements.txt`. `.venv` is already in `.gitignore`.
- Repo URL unknown (no git remote configured in this environment) → use `<repo-url>` placeholder with a note to substitute.
- Run everything from the repo root so `python-dotenv` finds `.env` (it searches upward from the cwd) and the scripts' `ROOT` path resolves.
- Troubleshooting entries:
  1. `RuntimeError: <Stage> truncated for candidate_XX: response hit max_tokens limit before completing` — the model's JSON was cut off. `max_tokens` is already 8192 in extract/crosscheck/score, which covered all 10 candidates in practice; if it recurs it's usually transient (rerun) or needs a higher `max_tokens` in that stage's `*_candidate()` function.
  2. Auth/permission error mentioning a workspace or `anthropic-workspace-id` — the key is identity/org-scoped, not workspace-scoped. Create a workspace-scoped key in the Anthropic Console and put that in `.env`.

## Tool calls

- `Read docs/reproduction.md` (prior task) → empty; confirmed still the target.
- `Write trajectories/reproduction_build_run1.md` → this file.
- `Write docs/reproduction.md` → created (see final result).

## Final result

Created `docs/reproduction.md` — 7 sections, purely instructional:
1. Prerequisites (Python 3.12+, own Anthropic API key, ~$0.50 for a full run).
2. Clone + install, with optional venv.
3. `.env` setup (cp / copy).
4. The six commands in order, each with: command, outputs, API-call count + rough time, and the verbatim console success output.
5. Where to read results (`eval/results.md`, `solution/final_report.md`).
6. Cost breakdown per stage + total, from `claude-sonnet-5` pricing and observed token sizes.
7. The two real errors as "if you see this…" entries.
- No narrative or changelog. Nothing invented — call counts and console strings are from actual runs.

---

## Retry 2

### Verbatim prompt

> Quick check on docs/reproduction.md: does the "Run order" section explicitly
> state that extract → crosscheck → score → aggregate → eval MUST run in that
> exact sequence (not just "here's an example order"), since each stage reads
> the prior stage's JSON output and will fail or produce garbage if run out
> of order? If it's only implied by the list order, add one explicit sentence
> making this a hard requirement, not just a suggestion.
>
> Log this as Retry 2 in trajectories/reproduction_build_run1.md if a change
> is made; if it's already explicit, no change needed, just confirm.

### Assessment

The section 4 intro said "in this order" but did NOT state it was a hard
requirement or explain the data-dependency consequence — it was only implied
by the list order. Change warranted.

### Tool calls

- `Edit docs/reproduction.md` → added a bold paragraph after the section 4
  intro: "The order is a hard requirement, not a suggestion." — spelling out
  the dependency chain (crosscheck←extract, score←crosscheck, aggregate←all
  three, eval←final_report.json), that running out of order fails or uses
  stale data, that re-running one stage means re-running every later stage,
  and that `baseline` is independent but must precede `eval`.

### Final result

`docs/reproduction.md` section 4 now states the sequence is mandatory and
why, with the explicit stage-by-stage read dependencies and a
re-run-downstream rule. One paragraph added; nothing else changed.
