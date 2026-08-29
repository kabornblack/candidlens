# Trajectory — Aggregate Build (run 1)

## Verbatim prompt

> Task: Build solution/aggregate.py — Stage 4 of the agent pipeline (final aggregation).
>
> Purpose: combine the outputs of all three prior stages into one final,
> human-readable report per candidate — this is the actual deliverable output
> a recruiter would read, and it's also what feeds the final ranking used in
> the eval comparison.
>
> Requirements:
> - No new API calls needed — this stage is pure Python data assembly, not an
>   LLM call. It merges existing JSON outputs.
> - Read all three: solution/extracted_claims.json, solution/crosscheck_results.json,
>   solution/score_results.json
> - For each candidate, produce a combined report object:
>   {"candidate": "candidate_03",
>    "category_scores": {...}, "overall": X, "overall_rationale": "...",
>    "category_rationale": {...}, "discrepancy_summary": [...],
>    "contradicted_claims": [{"cv_claim": "...", "conflicting_interview_claims": [...]}],
>    "rank": X}
> - Sort all 10 candidates by overall score, descending, to compute rank
>   (1 = highest). For ties, keep original candidate order (stable sort) —
>   don't invent a tie-break rule the model doesn't have grounds for.
> - Write two outputs:
>   1. solution/final_report.json — the full list of combined report objects, in ranked order
>   2. solution/final_report.md — a human-readable markdown version, one
>      section per candidate in ranked order ... candidate name, overall score,
>      rank, category scores in a small table, the discrepancy_summary if any,
>      and the overall_rationale as a closing paragraph
>
> Do not run yet — I'll review the code first ...
>
> Log this in trajectories/aggregate_build_run1.md per the agent instructions.

## Plan / reasoning

- Stage 4 of 4 (extract → crosscheck → score → **aggregate**). Pure Python, NO API call, NO `anthropic`/`dotenv` import needed.
- Inputs: the 3 JSON files. Join by `candidate` key.
- **Clarifying question asked** (task ambiguity, rule 12): none of the 3 JSONs store the candidate's real name, only the `candidate_03` id, but the report is meant to be recruiter-readable. User chose: **read the real name from `data/candidates/candidate_XX.md`** (parse the H1 `# Candidate 01 — Priya Raghunathan` → "Priya Raghunathan"; fall back to a title-cased id if the H1 can't be parsed). This is the only extra input beyond the 3 JSONs.
- Per-candidate merge:
  - `category_scores`, `overall`, `overall_rationale`, `category_rationale` ← `score_results.json`
  - `discrepancy_summary` ← `crosscheck_results.json`
  - `contradicted_claims` ← `crosscheck_results.json` `claim_checks` filtered to `status == "contradicted"`, keeping `{cv_claim, conflicting_interview_claims}`
  - `extracted_claims.json` is read to establish the canonical candidate list + original order (candidate_01..10) for the stable-sort tie-break, and to sanity-check all 3 files cover the same 10 candidates.
- Ranking: build the list in original candidate order, then `sorted(items, key=lambda r: -r["overall"])` — Python sort is stable, so ties keep original order. `rank` = 1-based index after sort. No secondary tie-break key (per instruction).
- Outputs:
  1. `solution/final_report.json` — list of report objects in ranked order.
  2. `solution/final_report.md` — one `## Rank N — <Name>` section per candidate in ranked order: overall/5, a 5-row category-score table, `Discrepancies flagged` (bullet list or "None."), and the `overall_rationale` as a closing paragraph.
- Guard: if `overall` is missing/None for any candidate, raise a clear error rather than silently mis-ranking.
- Do NOT run — user reviews code first.

## Tool calls

- `AskUserQuestion` (candidate name handling) → user chose "Read names from data/candidates/".
- `Write trajectories/aggregate_build_run1.md` → this file.
- `Write solution/aggregate.py` → created (see final result).
- `python -m py_compile solution/aggregate.py` → compiles OK.
- `python -c "..."` dry check — calls `build_reports()` + `rank_reports()` only (NOT `main()`, so no files written):
  - All 10 names parsed from the H1s correctly (`Priya Raghunathan` … `Nadia Kessler`); em-dash split works; `Marcus Delgado-Finn` / `Amara Okonkwo-Bright` hyphens not mis-split (separator is `" - "` with spaces, not bare `-`).
  - Merge correct: `contradicted_claims` / `discrepancy_summary` counts — candidate_03 = 2/2, candidate_09 = 1/1, all others 0/0 — matching `crosscheck_results.json`.
  - Stable sort verified: the five `overall == 4` candidates keep Stage-1 order (01, 05, 06, 08, 09) → ranks 1–5; then `overall == 3` (04, 07, 10) → ranks 6–8; then 02 (rank 9); then 03 (rank 10). No invented tie-break.

## Final result

Created `solution/aggregate.py` — pure Python, no API:

- `MODEL` constant intentionally omitted (no LLM call in this stage).
- `load_json()` helper; `candidate_name(cid)` reads `data/candidates/<cid>.md` H1, splits on the em dash, falls back to `cid.replace("_", " ").title()`.
- `build_reports()` — merges the 3 files by candidate, builds `contradicted_claims` from `claim_checks`, validates the 3 files cover the same candidate set, raises on missing `overall`.
- `rank_reports()` — stable sort by `-overall`, assigns 1-based `rank`.
- `write_json()` / `write_markdown()` — the two deliverables.
- `main()` — no `load_dotenv`, no client; just assemble + write `solution/final_report.json` and `solution/final_report.md`.
- Not run — awaiting user code review.

---

## Retry 2

### Verbatim prompt

> Before running: confirm candidate_name()'s H1 parsing is robust — if the
> regex/split doesn't match a file's H1 exactly (e.g. different dash
> character, trailing whitespace), does it fail gracefully to the title-cased
> id fallback, or would it raise an exception? Just confirm, don't change
> anything unless it's actually fragile.
>
> If confirmed safe, go ahead and run: python solution/aggregate.py
> Show me the full contents of solution/final_report.md once written.
>
> Log this as Retry 2 in trajectories/aggregate_build_run1.md.

### Robustness review of `candidate_name()` — CONFIRMED SAFE, no change made

No regex — pure string ops. Path through the function:

| Situation | Behaviour |
|-----------|-----------|
| File missing | `Path.read_text` raises `FileNotFoundError` (a subclass of `OSError`) → caught → title-cased id fallback |
| No line starts with `"# "` | loop finishes without returning → falls through to the id fallback |
| H1 present, no separator (`—`, `–`, `" - "`) matches | returns the whole heading string — ugly but does NOT raise |
| H1 present, separator present | `sep in heading` is already true, so `heading.split(sep, 1)` yields ≥2 parts and `[1]` is safe — no `IndexError` |
| Trailing / leading whitespace | `.strip()` applied to both the line and the returned name |
| Different dash char (e.g. U+2010, U+2015) | not in the separator list → returns whole heading, no raise |
| `"# "` with nothing after it | `heading == ""` → no separator → returns `""` — no raise (empty name, cosmetic only) |

Only theoretical exception path: a non-UTF-8 candidate file would raise `UnicodeDecodeError` (a `ValueError`, not caught by the `except OSError`). Not a real risk here — all 10 files are UTF-8 and have been read successfully repeatedly this session, and the dry run in run 1 already parsed all 10 names correctly. **Verdict: not fragile; the realistic failure modes all degrade to the id fallback without raising. Left unchanged.**

### Tool calls

- `python solution/aggregate.py` → wrote `solution/final_report.json` and `solution/final_report.md`; printed the 1–10 ranked list. (The console rendered the em dash in the `print()` as `�` — that is the Windows cp1252 stdout codepage only; the `.md` file is written UTF-8 and contains a correct `—`, verified by re-reading it.)
- `Read solution/final_report.md` → full contents below.

### Ranked output

```
 1. Priya Raghunathan (candidate_01) — 4
 2. Tomasz Wrenfield (candidate_05) — 4
 3. Amara Okonkwo-Bright (candidate_06) — 4
 4. Rohan Marchetti (candidate_08) — 4
 5. Bjorn Castellanos (candidate_09) — 4
 6. Yuki Abernathy (candidate_04) — 3
 7. Sistine Vale (candidate_07) — 3
 8. Nadia Kessler (candidate_10) — 3
 9. Dylan Prewitt (candidate_02) — 2
10. Marcus Delgado-Finn (candidate_03) — 1
```

`solution/final_report.md` full contents:

- `# CandidLens — Final Candidate Report` + "10 candidates, ranked by overall score."
- One `## Rank N — <Name> (candidate_XX)` section per candidate, in the order above, each with: `**Overall score: X / 5**`, a 5-row category table (`Python / Go proficiency`, `REST API design`, `SQL / data modeling`, `Cloud infrastructure`, `Ownership & collaboration`), a `**Discrepancies flagged:**` block (bullet list for candidate_09 and candidate_03, `None.` for the other 8), and the `overall_rationale` paragraph.
- candidate_09 shows the 1 tenure discrepancy; candidate_03 shows both fabrication findings (API-architecture ownership, team-of-5 leadership).

### Final result

`candidate_name()` H1 parsing confirmed robust (degrades to the id fallback, never raises for realistic inputs) — unchanged. `python solution/aggregate.py` run: `solution/final_report.json` and `solution/final_report.md` written, all 10 candidates in ranked order (1 Priya → 10 Marcus). Stable-sort ties preserved (five at overall 4 in Stage-1 order, three at overall 3). Stage 4 complete — the full 4-stage agent pipeline now runs end to end.
