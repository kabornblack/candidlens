# Trajectory — Eval Build (run 1)

## Verbatim prompt

> Task: Build eval/run_eval.py — the evaluation/comparison script.
>
> Purpose: this is the single script a judge would run to see the full
> comparison story: baseline vs agent vs human reference, with the metric
> that proves measured improvement. It should NOT make any new API calls —
> everything it needs already exists as JSON output from prior stages.
>
> Inputs (read-only, no re-computation):
> - baseline/baseline_results.json
> - solution/final_report.json
> - data/human_reference_ranking.md (parse the Overall scores and Final
>   Ranking section — if parsing markdown is fragile, read the scores
>   reasonably and note any parsing assumptions clearly in a comment)
>
> Requirements:
> 1. Build a table: candidate, baseline overall, agent overall, human overall
> 2. Compute Mean Absolute Error (MAE) of baseline vs human, and agent vs human
> 3. Compute the same MAE excluding candidate_03 (Marcus), labeled clearly as
>    "excluding the deliberate integrity-cap outlier"
> 4. Compute a simple rank-correlation measure (Spearman's rank correlation,
>    or ... a simpler "number of ranking positions that differ by more than 1"
>    count) between baseline ranking vs human ranking, and agent ranking vs
>    human ranking
> 5. Specifically report: did the agent correctly flag candidate_03's
>    contradiction where baseline did not? (Yes/no with the evidence —
>    baseline has no discrepancy field at all, agent's final_report.json does)
> 6. Print a clean summary to console AND write the same summary to
>    eval/results.md as a readable markdown report
>
> Keep this script simple and readable — no new API costs... If you need a
> library for Spearman's (e.g. scipy), ask before installing; otherwise
> implement the simpler ranking-difference count with plain Python.
>
> Do not run yet — I'll review the logic first, then we run it together.
>
> Log this in trajectories/eval_build_run1.md per the agent instructions.

## Plan / reasoning

- Pure Python, NO API, NO new dependency. Spearman's rank correlation is a closed-form formula (Pearson on rank vectors, with tie-averaged ranks) — implementable in ~10 lines of plain Python, so I'll include BOTH Spearman **and** the "positions differing by >1" count. No scipy, nothing to ask about.
- Inputs:
  - `baseline/baseline_results.json` — list of `{candidate, scores:{..., overall}}` → baseline overall.
  - `solution/final_report.json` — list of `{candidate, name, overall, rank, discrepancy_summary, contradicted_claims, ...}` → agent overall + agent rank + discrepancy evidence.
  - `data/human_reference_ranking.md` — parsed (see assumptions below).
- **Markdown parsing assumptions (documented in the script):**
  1. Human per-candidate Overall = the `Overall: X / 5` line inside each `## Candidate NN — Name` section.
  2. Human ranking order = the numbered `N. **Name** — ...` list inside the `## Final Ranking (1–10, best to worst)` section (distinct from the earlier `## Scoring Methodology Final Ranking` heading — matched on the literal `## Final Ranking`).
  3. Candidate id = `candidate_` + the zero-padded `NN` from the `## Candidate NN` header; name→id map built from those headers to resolve the `**Name**` entries in the ranking list.
  4. If any candidate is missing an Overall line or a ranking entry → raise (no silent drop).
- **Baseline has no ranking field.** Derived by sorting baseline overall descending, ties broken by candidate-id order (stable). Same tie-break used for the integer-position "differ by >1" count on the agent. Because that count is tie-break-sensitive, **Spearman (with tie-averaged ranks) is the primary rank metric**; the count is reported as an intuitive supplement.
- Metrics:
  1. Table: cid, baseline, agent, human.
  2. MAE(baseline, human) and MAE(agent, human) over all 10.
  3. Same two MAEs excluding `candidate_03`, labelled "excluding the deliberate integrity-cap outlier".
  4. Spearman(baseline_ranks, human_ranks) and Spearman(agent_ranks, human_ranks); plus count of candidates whose integer ranking position differs from the human position by >1, for baseline and for agent.
  5. candidate_03 contradiction: baseline entry has NO discrepancy/contradiction key at all (keys are just `candidate`, `scores`); agent entry has `contradicted_claims` (2) + `discrepancy_summary` (2). Report YES with that evidence.
  6. Build the report as a list of lines → `print()` to console AND write to `eval/results.md` (identical content).
- Do NOT run.

### Expected numbers (hand-computed for review — script is authoritative)

Human overall: 01=4.5 02=1.5 03=2.5 04=3.5 05=4.0 06=4.0 07=3.5 08=4.0 09=3.5 10=3.0
Baseline overall: 01=5 02=1 03=2 04=3 05=3 06=4 07=3 08=3 09=3 10=3
Agent overall: 01=4 02=2 03=1 04=3 05=4 06=4 07=3 08=4 09=4 10=3

- MAE baseline vs human = 5.0 / 10 = **0.50**
- MAE agent vs human = 4.0 / 10 = **0.40**
  (note: this corrects an arithmetic slip in score_build_run1.md Retry 4, which wrote 0.45 — the per-row abs diffs there were right, the sum was mis-added; 0.5+0.5+1.5+0.5+0+0+0.5+0+0.5+0 = 4.0)
- MAE excluding candidate_03: baseline 4.5/9 = **0.50**, agent 2.5/9 ≈ **0.28**
- Spearman vs human ranking: baseline ≈ **0.79**, agent ≈ **0.86**
- Integer-position differs from human by >1: baseline = **5** candidates (04,05,06,07,08), agent = **0** candidates
- candidate_03 contradiction flagged: baseline **NO** (no discrepancy field exists), agent **YES** (2 contradicted_claims + 2 discrepancy_summary items)

## Tool calls

- `Read data/human_reference_ranking.md` → confirmed exact format (`Overall: X / 5` lines; `## Final Ranking (1–10, best to worst)` with `N. **Name** — X / 5`).
- `Write trajectories/eval_build_run1.md` → this file.
- `Write eval/run_eval.py` → created (see final result).
- `python -m py_compile eval/run_eval.py` → compiles OK.

## Final result

Created `eval/run_eval.py` — pure Python, no API, no new deps:

- `load_baseline_overall()`, `load_agent()`, `parse_human_reference()` (with the documented parsing assumptions as a module docstring / comments).
- `mean_absolute_error(a, b, exclude=())`, `average_ranks(score_by_cid)` (tie-averaged), `pearson(xs, ys)`, `spearman(...)`, `integer_positions(...)`, `positions_off_by_more_than_one(...)`.
- `build_report()` assembles the table + metrics + the candidate_03 finding into markdown lines; `main()` prints them and writes `eval/results.md`.
- Not run — awaiting user logic review.

---

## Retry 2

### Verbatim prompt

> Approved — logic looks correct, good catch on the MAE arithmetic slip.
> Go ahead and run: python eval/run_eval.py
>
> Show me the full contents of eval/results.md once written.
>
> Log this as Retry 2 in trajectories/eval_build_run1.md.

### Tool calls

- `python eval/run_eval.py` → ran cleanly, printed the report, wrote `eval/results.md`. (Console echo again shows `�` for em dashes — Windows cp1252 stdout only; `OUT_MD.write_text(..., encoding="utf-8")` writes a clean UTF-8 file, verified by re-reading.)
- `Read eval/results.md` → full clean contents (below).

### Computed results — all match the run-1 hand estimates

| Metric | Baseline | Agent |
|--------|--:|--:|
| MAE vs human, all 10 | **0.500** | **0.400** |
| MAE vs human, excl. candidate_03 | **0.500** | **0.278** |
| Spearman's ρ vs human ranking | **0.792** | **0.859** |
| Positions off from human by >1 | **5** (04, 05, 06, 07, 08) | **0** (none) |
| Flagged candidate_03 contradiction | **No** — record keys are just `['candidate', 'scores']`, no discrepancy field | **Yes** — 2 `contradicted_claims` + 2 `discrepancy_summary` findings, with cited interview evidence |

Every figure matches the values pre-computed in run 1 (MAE 0.50/0.40, excl. 0.50/0.278, ρ 0.792/0.859, positions 5/0). The run-1 note stands: this supersedes the 0.45 figure mis-added in `score_build_run1.md` Retry 4 — the correct agent MAE is **0.400**.

### `eval/results.md` full contents

```markdown
# CandidLens Evaluation — Baseline vs Agent vs Human Reference

No API calls — pure comparison of existing stage outputs.

## Overall scores

| Candidate | Baseline | Agent | Human |
| --- | --- | --- | --- |
| candidate_01 | 5 | 4 | 4.5 |
| candidate_02 | 1 | 2 | 1.5 |
| candidate_03 | 2 | 1 | 2.5 |
| candidate_04 | 3 | 3 | 3.5 |
| candidate_05 | 3 | 4 | 4.0 |
| candidate_06 | 4 | 4 | 4.0 |
| candidate_07 | 3 | 3 | 3.5 |
| candidate_08 | 3 | 4 | 4.0 |
| candidate_09 | 3 | 4 | 3.5 |
| candidate_10 | 3 | 3 | 3.0 |

## Mean Absolute Error vs human reference (lower is better)

| | Baseline | Agent |
| --- | --- | --- |
| All 10 candidates | 0.500 | 0.400 |
| Excluding candidate_03 (deliberate integrity-cap outlier) | 0.500 | 0.278 |

Agent MAE improves on baseline by 0.100 across all 10, and by 0.222 once the deliberate candidate_03 integrity-cap outlier is excluded.

## Rank agreement with human ranking (higher rho is better)

| | Baseline | Agent |
| --- | --- | --- |
| Spearman's rho (tie-averaged ranks) | 0.792 | 0.859 |
| Candidates whose position differs from human by > 1 | 5 | 0 |

- Baseline positions off by > 1: candidate_04, candidate_05, candidate_06, candidate_07, candidate_08
- Agent positions off by > 1: none

Spearman's rho is the primary rank metric (it handles the many tied overall scores correctly). The position-difference count breaks ties by candidate id, so it is an intuitive supplement rather than the headline number.

## Did the agent flag candidate_03's contradiction where the baseline did not?

**Yes.**

- Baseline: its `candidate_03` record has keys ['candidate', 'scores'] — there is no discrepancy/contradiction field at all. The baseline has no mechanism to surface a CV/interview conflict.
- Agent: its `candidate_03` record carries 2 contradicted CV claim(s) and 2 discrepancy-summary finding(s):
  - CV claims sole ownership of designing Verdano's API architecture, but candidate could not explain service boundaries, auth decisions, versioning, or tradeoffs behind that design
  - CV claims leading a team of 5 engineers, but reference and candidate's own comments describe an individual-contributor role with someone else as tech lead
  - contradicted: "Claims to have designed Verdano's core API architecture from the ground up, including service boundaries, auth model, and data contracts"
    - conflicting interview evidence: "Gave a vague box-and-arrows diagram when asked to whiteboard the Verdano API architecture"
    - conflicting interview evidence: "Could not explain why services were split where they were"
    - conflicting interview evidence: "Could not explain who made the auth decision, said 'that was kind of a group thing, it evolved'"
    - conflicting interview evidence: "Could not describe the versioning strategy for the data contracts"
    - conflicting interview evidence: "Could not describe a single concrete tradeoff regarding the data contracts"
  - contradicted: "Claims to have led a team of 5 engineers delivering the dispatch platform rewrite on schedule"
    - conflicting interview evidence: "Backchannel reference describes Marcus as 'a solid individual contributor on the dispatch team — he owned the ETA calculation module'"
    - conflicting interview evidence: "Reference names a different person as the tech lead"
    - conflicting interview evidence: "Reference makes no mention of Marcus leading anyone"
    - conflicting interview evidence: "When asked about handling a disagreement between two reports, said 'I don't really do the people stuff, I just made sure my parts landed'"

## Bottom line

- Overall-score accuracy: agent MAE 0.400 vs baseline 0.500 (all 10); 0.278 vs 0.500 excluding candidate_03.
- Rank agreement: agent Spearman 0.859 vs baseline 0.792; agent has 0 badly-misplaced candidate(s) vs baseline's 5.
- Contradiction detection: agent flags candidate_03 with cited evidence; baseline structurally cannot.
```

### Final result

`python eval/run_eval.py` run: `eval/results.md` written (clean UTF-8, verified). Headline: **agent MAE 0.400 vs baseline 0.500** (0.278 vs 0.500 excluding the deliberate Marcus outlier); **agent Spearman 0.859 vs baseline 0.792**; **0 vs 5** candidates badly misplaced; agent flags candidate_03's two fabricated claims with cited evidence, baseline structurally cannot. The 4-stage agent pipeline + eval harness is complete and the improvement over the baseline is measured.
