# Trajectory — Crosscheck Build (run 1)

## Verbatim prompt

> Task: Build solution/crosscheck.py — Stage 2 of the agent pipeline (crosscheck,
> runs before scoring).
>
> Purpose: this is the stage extract.py deliberately deferred. It compares each
> candidate's cv_claims against their interview_claims and flags discrepancies —
> claims that are corroborated, uncorroborated (no interview evidence either
> way), or contradicted (interview evidence conflicts with the CV claim).
>
> Requirements:
> - Use the same MODEL constant (claude-sonnet-5), same pattern as extract.py
>   and baseline.py.
> - Read solution/extracted_claims.json (output of Stage 1) as input — do not
>   re-read the raw candidate files directly; this stage only works from the
>   structured claims, so it can't smuggle in outside judgment.
> - For each candidate, send one prompt to Claude containing that candidate's
>   cv_claims and interview_claims, asking it to:
>   - Go through each cv_claim and classify it as one of:
>     "corroborated" (interview claims support it)
>     "uncorroborated" (no interview claims address it either way)
>     "contradicted" (interview claims conflict with it)
>   - For "contradicted" claims specifically, cite which interview_claim(s)
>     conflict with it (quote or closely paraphrase them)
>   - Output a discrepancy_summary: a short list of the most significant
>     contradictions found (empty list if none)
> - Output format per candidate:
>   {"candidate": "candidate_03",
>    "claim_checks": [{"cv_claim": "...", "status": "contradicted",
>                       "conflicting_interview_claims": ["..."]}],
>    "discrepancy_summary": ["..."]}
> - Save all 10 to solution/crosscheck_results.json
> - Same max_tokens lesson as extract.py — use 8192 to avoid truncation, and
>   add the same stop_reason check that names the candidate on truncation
> - Same dotenv/.env pattern as the other stages
>
> Do not run yet — I'll test on candidate_03 first, same as before, since
> that's the case this whole stage exists to catch.
>
> Log this in trajectories/crosscheck_build_run1.md per the agent instructions.

## Plan / reasoning

- Stage 2 of 4 (extract → **crosscheck** → score → aggregate).
- Input is `solution/extracted_claims.json` ONLY — never the raw `data/candidates/*.md`. This keeps the stage honest: it can only reason over Stage 1's structured claims.
- Mirror the structure of `extract.py`: duplicated `MODEL = "claude-sonnet-5"` constant + comment, `load_dotenv()` at top of `main()`, `anthropic.Anthropic()`, `parse_json()` with brace-slice fallback, `max_tokens=8192`, `stop_reason == "max_tokens"` → `RuntimeError` naming the candidate.
- One Claude call per candidate. Prompt gets that candidate's `cv_claims` + `interview_claims` (as JSON) and must return:
  - `claim_checks`: one entry per cv_claim → `{cv_claim, status, conflicting_interview_claims}` where status ∈ {corroborated, uncorroborated, contradicted}; `conflicting_interview_claims` is `[]` unless status is `contradicted`.
  - `discrepancy_summary`: short list of the most significant contradictions (or `[]`).
- Define the three statuses precisely in the prompt so "uncorroborated" (silence) is not confused with "contradicted" (conflict).
- Instruct the model to work strictly from the provided claims — no outside knowledge, no re-judging the candidate.
- Write list of 10 `{candidate, claim_checks, discrepancy_summary}` to `solution/crosscheck_results.json`.
- Do NOT run.

## Tool calls

- `Write trajectories/crosscheck_build_run1.md` → this file.
- `Write solution/crosscheck.py` → created (see final result).
- `python -m py_compile solution/crosscheck.py` → compiles OK.

## Final result

Created `solution/crosscheck.py`:

- `MODEL = "claude-sonnet-5"` (identical constant + comment as the other stages).
- `IN_PATH = solution/extracted_claims.json`, `OUT_PATH = solution/crosscheck_results.json`.
- `load_extractions()` — reads Stage 1 output.
- `build_prompt(cv_claims, interview_claims)` — defines the 3 statuses, requires per-cv_claim classification, requires cited conflicting interview claims for contradictions, requires a `discrepancy_summary`; forbids outside knowledge / re-scoring.
- `crosscheck_candidate(client, name, cv_claims, interview_claims)` — one `client.messages.create`, `max_tokens=8192`, `stop_reason` guard raising `RuntimeError("Crosscheck truncated for {name}: response hit max_tokens limit before completing")`, JSON parse w/ fallback.
- `main()` — `load_dotenv()`, loop all candidates from the JSON, write `solution/crosscheck_results.json`.
- Not run — user will test candidate_03 first.

---

## Retry 2

### Verbatim prompt

> The candidate_03 test passed cleanly — both inflated CV claims correctly
> marked "contradicted" with accurate cited evidence, all skill/experience
> claims correctly marked "uncorroborated" (not contradicted), confirming the
> silence-vs-conflict distinction holds in practice.
>
> Task: Run the full crosscheck on all 10 candidates.
>
> 1. Run: python solution/crosscheck.py
> 2. Writes solution/crosscheck_results.json
> 3. After completion, give me a summary:
>    - Confirm all 10 candidates present
>    - For each candidate, report how many claim_checks were contradicted
>      vs uncorroborated vs corroborated, and list discrepancy_summary if
>      non-empty
>    - Flag anything that looks like a false positive (a claim marked
>      "contradicted" when it should be "uncorroborated") or a false
>      negative (an inflated-sounding claim marked "corroborated" or
>      "uncorroborated" when interview evidence should have caught it)
>
> Log this as Retry 2 in trajectories/crosscheck_build_run1.md.
>
> Do not modify crosscheck.py — report and stop if anything looks wrong.

### Plan / reasoning

Run once, read `solution/crosscheck_results.json`, tally statuses per candidate, audit each `contradicted` for false positives and each candidate for missed inflated claims. Do not modify `crosscheck.py`.

### Tool calls

- `python solution/crosscheck.py` → completed cleanly. `Cross-checking candidate_01...` … `candidate_10`, then `Wrote 10 crosscheck results to ...\solution\crosscheck_results.json`. No errors, no truncation.
- `Read solution/crosscheck_results.json` → 10 objects.

### Status tally

| Cand | corroborated | uncorroborated | contradicted | discrepancy_summary |
|------|:---:|:---:|:---:|---|
| 01 Priya    | 6 | 7 | 0 | — |
| 02 Dylan    | 3 | 12 | 1 | SQLite skill vs. weak SQL demo |
| 03 Marcus   | 0 | 9 | 2 | architecture-ownership claim unsupported in interview; team-lead claim contradicted by reference + own answer |
| 04 Yuki     | 8 | 6 | 0 | — |
| 05 Tomasz   | 7 | 5 | 0 | — |
| 06 Amara    | 7 | 7 | 1 | PostgreSQL key-skill vs. needed window-function hint / "deep tuning isn't my strong area" |
| 07 Sistine  | 6 | 8 | 0 | — |
| 08 Rohan    | 8 | 5 | 0 | — |
| 09 Bjorn    | 9 | 2 | 2 | Quillstone 1.5 yr vs. "none over ~14 months"; AWS skill vs. "less sure on networking/IaC, hasn't owned infra" |
| 10 Nadia    | 7 | 6 | 0 | — |

All 10 present.

### Audit — false positives / false negatives

**candidate_03 (the target case): correct.** Both inflated claims `contradicted` with full, accurate cited evidence; the 9 ordinary skill/experience claims all `uncorroborated`, not `contradicted`. The `discrepancy_summary` is precise. This is exactly what the stage exists to do.

**False positives — `contradicted` that should be `uncorroborated`/`corroborated`:**

1. **candidate_06 — "Lists PostgreSQL as a key skill" → `contradicted`. Clear false positive.** The cited conflicts are "needed a hint on a window function" and "deep query tuning isn't her strong area yet". The same interview list also contains "Got a SQL join right" — she demonstrably has the skill. Needing a hint on an advanced feature and being modest about depth does not *conflict* with listing PostgreSQL as a skill; this is `uncorroborated` at most (arguably partially `corroborated`). Human reference scores her SQL 3/5 — a real, moderate skill, not a false claim.

2. **candidate_09 — "AWS (ECS, ALB, RDS) skill" → `contradicted`. Clear false positive.** Cited conflicts: "less sure on networking/IaC", "hasn't owned infra". The interview list also has "comfortable deploying to ECS" — which *corroborates* the skill listing. "Hasn't owned infra" narrows the scope; it doesn't contradict having ECS/ALB/RDS skill. Should be `corroborated` or `uncorroborated`.

3. **candidate_02 — "Skill: SQLite" → `contradicted`. Soft false positive.** Listing SQLite as a skill is a weak claim; the interview shows poor SQL ("stuck on a two-table join"). Defensible as a real conflict, but inconsistent with how candidate_07 was handled (see below). `uncorroborated` would be the safer call.

4. **candidate_09 — "Quillstone Software for 1.5 years" → `contradicted` by "4 jobs in 5 years, none over ~14 months". Debatable / low-significance.** There *is* a literal numeric conflict (CV says 18 months, interviewer's approximation says "~14 months max"), so this is technically a valid catch — but it's the interviewer's rough characterisation vs. a CV specific, not candidate dishonesty. Keeping it is not wrong; a stricter reading would drop it.

**Consistency problem across the batch:** candidate_07 (Sistine) lists "ORMs (SQLAlchemy, Django ORM)" as a skill and her interview shows *worse* SQL than Amara — "struggled to write a two-table join by hand", "I basically never write raw SQL", "could not explain what index the query would use", "had not thought about normalization tradeoffs" — yet every one of her claims is `corroborated`/`uncorroborated`, nothing `contradicted`. So the "skill listed but weak in the interview → contradicted" bar was applied to 02 and 06 but not to 07, which is the one where it would have been most justified. The stage is inconsistent about whether a listed skill + a weak demo counts as a contradiction.

**False negatives — inflated claims that slipped through:** none material.
- candidate_03's inflated claims were caught.
- candidate_05's collaboration red flags and candidate_07's SQL weakness are **not CV claims**, so they correctly do not appear as `claim_checks` contradictions — those are scoring-stage signals, not CV/interview discrepancies. No overstated CV claim was wrongly marked `corroborated`/`uncorroborated`.
- Minor: candidate_08's "modeled the patient-events warehouse schema, source of truth for 6 teams" is `uncorroborated` though the interview strongly confirms the underlying modeling skill ("best in the batch", SCD/partitioning/normalization) — conservative, not a miss.

### Final result

Full crosscheck complete; `solution/crosscheck_results.json` written with all 10 candidates. The core objective works — candidate_03's fabricated seniority claims are caught with evidence, and the silence-vs-conflict line holds for genuinely unmentioned claims. **However, the stage over-calls `contradicted` on "listed skill vs. modest interview demo" (candidate_06 and candidate_09 AWS are clear false positives; candidate_02 SQLite is borderline) and applies that bar inconsistently (candidate_07 not flagged despite weaker SQL evidence).** `crosscheck.py` not modified. Stopping here to report per instruction — recommend a prompt tweak so a listed skill is only `contradicted` when the interview shows an *actual* inability that conflicts with the claim, and the model must weigh corroborating interview claims (e.g. "got the join right", "comfortable deploying to ECS") before choosing `contradicted`.

---

## Retry 3

### Verbatim prompt

> Approved — apply this fix to the crosscheck prompt in solution/crosscheck.py.
>
> The core issue: the model is conflating "corroborating evidence shows limited
> depth" with "contradiction." A listed skill should only be marked
> "contradicted" if the interview shows the candidate cannot do the thing at
> all, or shows something actively incompatible with the claim — not if the
> interview simply shows partial ability, needing a hint, or self-reported
> modesty about depth.
>
> Add explicit guidance to the prompt:
> - "Contradicted" requires evidence of actual inability or a direct conflict
>   — not merely limited depth, needing help, or a candidate being modest
>   about their skill level.
> - Before marking a claim "contradicted," the model must check whether ANY
>   interview_claim also supports the same skill/claim (even partially) — if
>   so, and the only "negative" evidence is about depth/scope rather than
>   inability, the correct status is "corroborated" or "uncorroborated," not
>   "contradicted."
> - Add a worked example showing this exact distinction: e.g. "Lists
>   PostgreSQL as a skill" + interview shows "got a join right" AND "needed a
>   hint on a window function" → corroborated (basic ability demonstrated),
>   NOT contradicted.
>
> After the prompt fix, re-run crosscheck on candidate_06, candidate_09, and
> candidate_02 specifically (not the full batch yet) and show me the new
> results for just those three, so we confirm the false positives are fixed
> before re-running everyone.
>
> Also check: does candidate_07's SQL weakness now correctly stay
> uncorroborated/corroborated rather than getting inconsistently flagged,
> confirming the fix applies evenly?
>
> Log this as Retry 3 in trajectories/crosscheck_build_run1.md.

### Plan / reasoning

Add the depth-vs-inability guidance + the "check for supporting evidence first" rule + the PostgreSQL worked example to `build_prompt()` in `crosscheck.py`. Then re-run only candidates 02, 06, 09 (the false positives) plus 07 (the consistency check) via a throwaway scratch script that imports `crosscheck` — this leaves `solution/crosscheck_results.json` untouched (full re-run is a later step per the user's instruction).

### Tool calls

- `Edit solution/crosscheck.py` → inserted after the "requires an actual conflict" line: (a) a paragraph that `contradicted` needs actual INABILITY or something ACTIVELY INCOMPATIBLE, not limited depth / needing a hint / modesty; (b) a "before marking contradicted, check whether ANY interview claim also SUPPORTS the claim — if the only negative is depth/scope/seniority, use corroborated or uncorroborated" rule; (c) the PostgreSQL worked example (got-a-join-right + needed-a-hint → corroborated, NOT contradicted).
- `python -m py_compile solution/crosscheck.py` → compiles OK.
- `Write <scratchpad>/subset_crosscheck.py` → throwaway; imports `crosscheck`, runs only candidates {02, 06, 07, 09}, prints JSON, writes nothing.
- `python <scratchpad>/subset_crosscheck.py` → results below.

### Subset results after the fix

| Cand | Claim | Before (Retry 2) | After (Retry 3) |
|------|-------|------------------|-----------------|
| 02 | "Skill: SQLite" | contradicted | **corroborated** — discrepancy_summary now `[]` |
| 06 | "Lists PostgreSQL as a key skill" | contradicted | **corroborated** — discrepancy_summary now `[]` (matches the worked example exactly) |
| 09 | "AWS (ECS, ALB, RDS) skill" | contradicted | **corroborated** (supported by "comfortable deploying to ECS") |
| 09 | "Backend Engineer at Quillstone Software for 1.5 years" | contradicted | **still contradicted** — by "4 jobs in 5 years, none over ~14 months" |

- **All three targeted false positives are fixed.** candidate_02 and candidate_06 now have empty `discrepancy_summary`; candidate_09 drops from 2 contradictions to 1.
- **candidate_09's Quillstone tenure remains `contradicted`.** This is a *different class* — a literal numeric conflict (CV says 18 months, interview says "none over ~14 months"), not a depth/inability misread — so the new guidance correctly does not suppress it. It is defensible as a real inconsistency; flagging it for the user in case they want it toned down, but leaving it as-is (the fix was scoped to skill-depth false positives).

### candidate_07 consistency check — PASS

candidate_07 re-ran with **zero contradictions** (unchanged from Retry 2): all claims `corroborated`/`uncorroborated`, including "ORMs (SQLAlchemy, Django ORM) listed as a skill" → `corroborated`. Her SQL weakness in the interview ("struggled with a two-table join", "never write raw SQL") is *not* a CV claim she made — her CV only lists ORMs, not SQL mastery — so there is nothing to contradict. The fix applies evenly: the model is no longer flagging "listed skill + shallow interview demo" as a contradiction for anyone (06, 02), and it was never doing so for 07.

### Final result

Prompt fix applied to `solution/crosscheck.py` (`build_prompt()` only — no logic change). Subset re-run confirms the three false positives (candidate_02 SQLite, candidate_06 PostgreSQL, candidate_09 AWS) are all resolved and candidate_07 stays consistent. One contradiction remains on candidate_09 (Quillstone 18mo vs. "~14 months max") — a genuine numeric conflict, not a regression. `solution/crosscheck_results.json` still holds the pre-fix full-batch run; a full re-run of all 10 is the next step (pending user go-ahead).

---

## Retry 4

### Verbatim prompt

> Approved — the fix looks correct and appropriately scoped. Go ahead and
> run the full 10-candidate crosscheck now.
>
> 1. Run: python solution/crosscheck.py (overwrites solution/crosscheck_results.json
>    with the fixed prompt across all 10)
> 2. Give me the same summary table as before: corroborated/uncorroborated/
>    contradicted counts per candidate, plus discrepancy_summary where
>    non-empty
> 3. Specifically confirm candidate_03 (Marcus) is unaffected by the fix —
>    his two genuine contradictions should be untouched
> 4. Flag anything that looks like a new false positive or false negative
>    introduced by this prompt change
>
> Log this as Retry 4 in trajectories/crosscheck_build_run1.md.

### Tool calls

- `python solution/crosscheck.py` → completed cleanly, `Wrote 10 crosscheck results to ...\solution\crosscheck_results.json`. No errors/truncation. `solution/crosscheck_results.json` overwritten with the fixed-prompt run (approved).
- `Read solution/crosscheck_results.json` → 10 objects.

### Status tally (fixed-prompt full run) with delta vs. the pre-fix run (Retry 2)

| Cand | corrob. | uncorrob. | contradicted | Δ vs pre-fix | discrepancy_summary |
|------|:---:|:---:|:---:|---|---|
| 01 Priya   | 6 | 7 | 0 | — | — |
| 02 Dylan   | 4 | 12 | 0 | contra 1→0 (SQLite → corroborated) | — |
| 03 Marcus  | 0 | 9 | **2** | unchanged | architecture-ownership claim unsupported; team-lead claim contradicted by reference + own answer |
| 04 Yuki    | 8 | 6 | 0 | — | — |
| 05 Tomasz  | 6 | 6 | 0 | 1 job-history line corr→uncorr (nondeterminism) | — |
| 06 Amara   | 9 | 6 | 0 | contra 1→0 (PostgreSQL → corroborated); +1 achievement uncorr→corr | — |
| 07 Sistine | 6 | 8 | 0 | — | — |
| 08 Rohan   | 9 | 4 | 0 | +1 achievement uncorr→corr (2TB/day pipeline) | — |
| 09 Bjorn   | 10 | 2 | **1** | contra 2→1 (AWS skill → corroborated) | Quillstone role listed as 1.5 yr but interview says no job exceeded ~14 months |
| 10 Nadia   | 7 | 6 | 0 | — | — |

All 10 present. Total contradictions across the batch: **3** (Marcus 2 + Bjorn 1), down from 6 pre-fix.

### candidate_03 (Marcus) — CONFIRMED UNAFFECTED

Both genuine contradictions intact:
- "designed Verdano's core API architecture from the ground up" → `contradicted`, cited by 5 interview claims (vague whiteboard, couldn't explain service split, couldn't explain the auth decision, couldn't describe the versioning strategy, couldn't name a tradeoff).
- "led a team of 5 engineers" → `contradicted`, cited by the same 4 interview claims as before (reference calls him a solid IC on the ETA module, reference names a different tech lead, reference doesn't mention him leading anyone, his own "I don't really do the people stuff" quote).
- All 9 ordinary skill/experience claims still `uncorroborated`, none newly downgraded.
- `discrepancy_summary` still carries both findings (wording slightly reworded, substance identical).

Only cosmetic change: the architecture claim's citation list dropped one entry ("Deflected question by saying 'the docs would have that'") — 5 cited conflicts instead of 6. The claim is still solidly `contradicted`; that observation is still present in the extracted claims, just not in the citation list. No material impact.

### New false positives / false negatives from the prompt change

**New false positives: none.** The only non-Marcus contradiction is Bjorn's Quillstone tenure (CV 18 months vs. interview "none over ~14 months") — a literal numeric conflict, present before the fix, correctly untouched by guidance aimed at skill-depth misreads.

**New false negatives: none.** The three contradictions that disappeared (candidate_02 SQLite, candidate_06 PostgreSQL, candidate_09 AWS) were all confirmed false positives in Retry 2 — correct to drop. No genuine contradiction was suppressed; Marcus's survived intact.

**Incidental corroborated↔uncorroborated flips** (candidate_05 one job-history line corr→uncorr; candidate_06 and candidate_08 one achievement each uncorr→corr): these are run-to-run nondeterminism at the support/silence boundary, not driven by the new guidance, and the uncorr→corr flips are arguably more accurate (the interviews do partly support those achievements). None hides a real discrepancy.

### Final result

Fixed-prompt full crosscheck complete; `solution/crosscheck_results.json` overwritten with all 10 candidates. Contradiction count 6 → 3, entirely by removing the three confirmed skill-depth false positives. Marcus's two real contradictions are untouched. No new false positive or false negative introduced. Stage 2 is ready for the scoring stage.
