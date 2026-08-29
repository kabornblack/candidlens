# Trajectory — Baseline Build (run 1)

## Verbatim prompt

> Task: Build the baseline evaluator in baseline/baseline.py.
>
> This is the SIMPLE baseline our agent solution will be measured against —
> keep it intentionally basic, not engineered. It represents "one direct
> prompt with basic instructions," per the hackathon rules.
>
> Requirements:
> - Read data/jd.md and one candidate file at a time from data/candidates/
> - Send a single prompt to Claude (via the Anthropic API) containing the JD
>   and the full candidate file (CV + interview notes), asking it to output:
>   - A score 1-5 for each of the 5 categories listed in jd.md
>   - An overall score 1-5
>   - No requirement to cite evidence, cross-check claims, or flag
>     discrepancies — this is intentionally the "no verification" baseline
> - Loop through all 10 candidates and save results to baseline/baseline_results.json
> - Use environment variable ANTHROPIC_API_KEY for the API key — do not
>   hardcode it, do not write it to any file
> - Keep the code simple and readable — this should look like a first-pass
>   script, not production code
>
> Log this task in trajectories/baseline_build_run1.md per the agent
> instructions.

## Plan / reasoning

- Loaded the `claude-api` skill (Python project). Use the official `anthropic` SDK, `client.messages.create`, one call per candidate.
- `baseline/baseline.py` currently exists but is EMPTY; the `solution/` files and `eval/run_eval.py` are also empty. Nothing to compare model choice against, so use `claude-opus-5` (skill default) as a module constant and tell the user to keep the solution on the same model for a fair comparison.
- Intentionally basic: no prompt caching, no retries beyond SDK default, no thinking config, no evidence/cross-check instructions. Single flat prompt = JD + full candidate file + "give 1-5 per category + overall, respond as JSON."
- API key: rely on the SDK reading `ANTHROPIC_API_KEY` from the environment (`anthropic.Anthropic()` with no args). Never printed, never written to results.
- Output: list of `{candidate, file, scores:{...}, overall}` dicts → `baseline/baseline_results.json`.
- Simple JSON parse of the model reply, with a brace-slice fallback if it wraps the JSON in prose/fences.

## Tool calls

- `Skill claude-api` → Python guidance loaded.
- `Glob **/*.{py,txt,toml,cfg,json}` → `baseline/baseline.py`, `solution/*.py`, `eval/run_eval.py` (all empty).
- `Read python/claude-api/README.md` (skill) → SDK usage patterns.
- `Read solution/score.py` → empty.
- `Read baseline/baseline.py` → empty.
- `Write baseline/baseline.py` → created (see final result).
- `Write trajectories/baseline_build_run1.md` → this file.
- `python -m py_compile baseline/baseline.py` → compiles OK.
- `python -c "import anthropic"` → `ModuleNotFoundError: No module named 'anthropic'`. The `anthropic` SDK is not installed in this environment. Per rule 9 I did NOT install it — flagged to the user for approval (`pip install anthropic`).

## Final result

Created `baseline/baseline.py` — ~70 lines, first-pass style:

- `MODEL = "claude-opus-5"`, `CATEGORIES` list matching `jd.md`.
- `load_candidates()` reads every `data/candidates/candidate_*.md` in sorted order.
- `build_prompt(jd, candidate_text)` — one flat prompt, asks for JSON with the 5 category scores + `overall`, explicitly no evidence/cross-checking.
- `score_candidate()` — single `client.messages.create` call, `max_tokens=1024`, parses JSON (with brace-slice fallback).
- `main()` loops all 10 candidates, prints progress, writes `baseline/baseline_results.json`.
- API key read from `ANTHROPIC_API_KEY` via `anthropic.Anthropic()`; not referenced or written anywhere.

Not run (would make 10 billed API calls) — the user can run `python baseline/baseline.py` with `ANTHROPIC_API_KEY` set. `baseline/baseline_results.json` is produced by that run.

---

## Retry 2

### Verbatim prompt

> Four things to do:
>
> 1. Run: pip install anthropic python-dotenv
>    (approved — anthropic for API calls, python-dotenv so the script reads
>    the ANTHROPIC_API_KEY from a local .env file automatically)
>
> 2. Add `from dotenv import load_dotenv` and call `load_dotenv()` near the
>    top of main() in baseline/baseline.py, before the Anthropic client is
>    created, so it picks up .env automatically.
>
> 3. Change MODEL = "claude-opus-5" to MODEL = "claude-sonnet-5". Add a
>    comment above the constant noting this exact model string must be reused
>    identically in solution/extract.py, solution/score.py,
>    solution/crosscheck.py, and solution/aggregate.py, so the baseline and
>    solution are compared fairly using the same model.
>
> 4. Add python-dotenv to a requirements.txt file at the project root (create
>    it if it doesn't exist) alongside anthropic, so the reproduction guide
>    can reference "pip install -r requirements.txt".
>
> Do not run baseline.py yet — I'll test it myself on a single candidate first.
>
> Log this as Retry 2 in trajectories/baseline_build_run1.md, appended to the
> existing file.

### Plan / reasoning

All four items are explicitly approved. `MODEL` change is a deliberate switch to `claude-sonnet-5` and the constant is now the single source of truth the solution modules must copy. Do not run the script.

### Tool calls

- `pip install anthropic python-dotenv` → first attempt (system Python `C:\Python312`) failed: `OSError [WinError 2]` rolling the `idna` 3.11→3.19 upgrade (`idna.exe` not writable). Rolled back, nothing installed.
- `pip install --user anthropic python-dotenv` → success: `anthropic-1.2.0`, `httpx2-2.12.0`, `idna-3.19`, etc. installed to `C:\Users\admin\AppData\Roaming\Python\Python312`. `python-dotenv` already satisfied. (Non-fatal warning: user Scripts dir not on PATH — irrelevant, we import the package, not a CLI.)
- `python -c "import anthropic, dotenv"` → `anthropic 1.2.0`, `dotenv OK`.
- `Edit baseline/baseline.py` ×3 → (a) added `from dotenv import load_dotenv`; (b) added comment block + `MODEL = "claude-sonnet-5"`; (c) added `load_dotenv()` as the first line of `main()`, before `anthropic.Anthropic()`.
- `Write requirements.txt` (project root, did not exist) → `anthropic` + `python-dotenv`.
- `python -m py_compile baseline/baseline.py` → compiles OK.

### Final result

- `baseline/baseline.py`: `MODEL = "claude-sonnet-5"` with the "reuse this exact string in the 4 solution modules" comment; `load_dotenv()` called at the top of `main()`.
- `requirements.txt` created at project root with `anthropic` and `python-dotenv`.
- `anthropic` 1.2.0 installed (user site-packages, `--user` — system-site install was blocked by a Windows file-lock on `idna.exe`).
- Script NOT run, per instruction — user will test on a single candidate first.

---

## Retry 3

### Verbatim prompt

> The single-candidate manual test succeeded — confirmed baseline.py correctly
> loads .env, authenticates with the workspace-scoped API key, and returns
> valid JSON scores for candidate_01 (Priya Raghunathan), with results that
> directionally matched expectations (high scores across categories, matching
> her strong human reference ranking).
>
> Task: Run the full baseline evaluation.
>
> 1. Run: python baseline/baseline.py
> 2. This will make 10 API calls (one per candidate) and write results to
>    baseline/baseline_results.json
> 3. After it completes, read back baseline/baseline_results.json and give me
>    a summary table: candidate name, overall score, and how it compares to
>    the human reference ranking in data/human_reference_ranking.md —
>    specifically call out:
>    - Whether the baseline's ranking order differs from the human ranking
>    - How the baseline scored candidate_03 (Marcus) given his CV/interview
>      contradiction — did it catch any inconsistency, or take the CV claims
>      at face value? (Expected: it should NOT catch this, since the baseline
>      has no cross-checking step — this is what our agent solution needs to fix)
>
> Log this as Retry 3 in trajectories/baseline_build_run1.md, appended to the
> existing file — this was still fundamentally the same baseline-build task,
> just the actual execution step.
>
> Do not modify baseline.py itself in this task. If it errors, report the
> error and stop — don't attempt fixes without telling me first.

### Plan / reasoning

Run the script once, read the JSON, compare to `data/human_reference_ranking.md`. Do not touch `baseline.py`. No fixes without asking.

### Tool calls

- `python baseline/baseline.py` → completed cleanly. Printed `Scoring candidate_01...` … `candidate_10`, then `Wrote 10 results to ...\baseline\baseline_results.json`. No errors.
- `Read baseline/baseline_results.json` → 10 entries, each `{candidate, scores:{python_go, rest_api_design, sql_data_modeling, cloud_infrastructure, ownership_collab, overall}}`.
- `Read data/human_reference_ranking.md` (tail) → human final ranking + methodology.

### Baseline results (overall)

| Cand | Name | py/go | REST | SQL | Cloud | Own/Collab | Overall |
|------|------|-------|------|-----|-------|-----------|---------|
| 01 | Priya Raghunathan | 5 | 5 | 5 | 4 | 5 | **5** |
| 02 | Dylan Prewitt | 2 | 1 | 1 | 1 | 3 | **1** |
| 03 | Marcus Delgado-Finn | 3 | 2 | 2 | 3 | 2 | **2** |
| 04 | Yuki Abernathy | 5 | 3 | 5 | 1 | 4 | **3** |
| 05 | Tomasz Wrenfield | 5 | 5 | 5 | 5 | 2 | **3** |
| 06 | Amara Okonkwo-Bright | 4 | 5 | 3 | 3 | 5 | **4** |
| 07 | Sistine Vale | 4 | 3 | 2 | 5 | 4 | **3** |
| 08 | Rohan Marchetti | 3 | 2 | 5 | 4 | 4 | **3** |
| 09 | Bjorn Castellanos | 4 | 5 | 3 | 3 | 3 | **3** |
| 10 | Nadia Kessler | 3 | 3 | 2 | 3 | 3 | **3** |

### Ranking comparison

Human order (best→worst): Priya(01) · Tomasz(05) · Rohan(08) · Amara(06) · Yuki(04) · Bjorn(09) · Sistine(07) · Nadia(10) · Marcus(03) · Dylan(02)

Baseline order by `overall` (ties broken by sum of category scores): Priya(01, 5) · Amara(06, 4) · Tomasz(05, 3/Σ22) · [Yuki(04) · Sistine(07) · Rohan(08) · Bjorn(09) — all 3/Σ18, unordered] · Nadia(10, 3/Σ14) · Marcus(03, 2) · Dylan(02, 1)

Differences:
- **Endpoints agree.** Priya #1, Marcus #9, Dylan #10 in both.
- **The middle collapses.** Six candidates (04,05,07,08,09,10) all get `overall = 3`. The human spread those same people across ranks 2–8 (4.0 down to 3.0). The baseline's 1–5 integer scale + single-pass judgement has almost no resolving power in the middle of the field.
- **Amara over-ranked** (#2 baseline vs #4 human) — baseline rewards her strong collaboration/REST without discounting for the modest SQL/Cloud.
- **Tomasz under-ranked** (#3→ effectively mid-pack, overall 3, vs human #2 / 4.0). Baseline over-penalised the 2/5 collaboration, dropping a 4.4-raw-average candidate to a flat 3.
- **Rohan under-ranked** (human #3 / 4.0 vs baseline overall 3, buried in the tie).

### Candidate 03 (Marcus) — did the baseline catch the contradiction?

**No — as expected.** Details:
- The baseline emits only numbers (no text), so it produces **no discrepancy flag, no note, nothing** stating "CV claims architecture ownership / team lead, interview + reference contradict it." There is no cross-checking step and no place in the output for a finding.
- It scored him `overall = 2` (human: 2.5). The number *looks* right, but that low score is explained by candidate_03.md's interview notes being written negatively on their face (vague whiteboard, "the docs would have that", deflection) — a face-value read of the interview text alone yields low category scores (REST 2, SQL 2, collab 2). It is **not** evidence the model reconciled the CV-vs-interview contradiction.
- The inflated CV claims ("designed the core API architecture from the ground up", "led a team of 5") were **taken at face value** — nothing in the run identifies them as uncorroborated or contradicted. If Marcus's interview notes had been neutral or positive while still contradicting the CV, the baseline would very likely have scored him as a strong candidate.
- Contrast with the human sheet, which applies an explicit **"Credibility / Integrity Cap"** rule and documents the CV↔interview↔reference conflict.

This is precisely the gap the agent solution's `crosscheck.py` step is meant to close.

### Final result

Full baseline run complete; `baseline/baseline_results.json` written with 10 candidates. Baseline agrees with the human ranking at the top and bottom but cannot resolve the middle (6-way tie at overall 3) and has no mechanism to detect or report the candidate_03 CV/interview contradiction — it scored Marcus low only because his interview notes read poorly, not because it caught the inconsistency. `baseline.py` not modified. No errors.
