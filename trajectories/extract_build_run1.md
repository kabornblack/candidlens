# Trajectory — Extract Build (run 1)

## Verbatim prompt

> Task: Build solution/extract.py — the first stage of the agent solution pipeline.
>
> Purpose: unlike the baseline's single flat prompt, this stage extracts
> discrete, structured claims from each candidate file BEFORE any scoring
> happens, separating CV claims from interview claims so they can be
> cross-checked against each other later.
>
> Requirements:
> - Use the same MODEL constant pattern as baseline.py (claude-sonnet-5) —
>   import or duplicate the constant, but keep it identical.
> - For each candidate file in data/candidates/, send one prompt to Claude
>   asking it to extract:
>   - cv_claims: a list of discrete claims from the CV section, each as a
>     short string (e.g. "Led a team of 5 engineers", "Designed the core
>     API architecture from the ground up", "3.5 years experience")
>   - interview_claims: a list of discrete observations/statements from the
>     interview notes section, each as a short string
>   - For each claim, tag which of the 5 JD skill categories it relates to
>     (python_go, rest_api_design, sql_data_modeling, cloud_infrastructure,
>     ownership_collab), or "general" if it doesn't fit one category
> - Output format: JSON per candidate, like:
>   {"candidate": "candidate_03", "cv_claims": [{"text": "...", "category": "..."}],
>    "interview_claims": [{"text": "...", "category": "..."}]}
> - Save all 10 candidates' extractions to solution/extracted_claims.json
>   (a list of these objects)
> - Read from .env via python-dotenv, same pattern as baseline.py
>
> Do not run this yet — I'll test it on one candidate first, same as before.
>
> Log this in trajectories/extract_build_run1.md per the agent instructions.

## Plan / reasoning

- Stage 1 of the 4-stage pipeline (extract → score → crosscheck → aggregate).
- Mirror `baseline.py`'s structure (paths from `__file__`, `load_dotenv()` at top of `main()`, `anthropic.Anthropic()` reads `ANTHROPIC_API_KEY`).
- **MODEL constant:** duplicate `MODEL = "claude-sonnet-5"` verbatim (with the same "must match across baseline + solution modules" comment). Duplicating rather than importing keeps each solution module self-contained and avoids a `solution` ↔ `baseline` import dependency; the user explicitly allowed "import or duplicate".
- One Claude call per candidate. Prompt asks it to:
  - split the file into its CV section and its Interview Notes section,
  - list discrete `cv_claims` and `interview_claims` as short strings,
  - tag each with one of the 5 category slugs or `"general"`.
- Output: strict JSON object per candidate; parse with `json.loads` + brace-slice fallback (same helper shape as baseline).
- `max_tokens` raised to 2048 (claim lists are longer than the baseline's score blob).
- Write list of 10 objects to `solution/extracted_claims.json`.
- Category slugs inlined in the prompt (no need to read `jd.md` — only the slugs matter here).
- Do NOT run.

## Tool calls

- `Write trajectories/extract_build_run1.md` → this file.
- `Write solution/extract.py` → created (see final result).
- `python -m py_compile solution/extract.py` → compiles OK.

## Final result

Created `solution/extract.py`:

- `MODEL = "claude-sonnet-5"` (identical constant + comment as `baseline.py`).
- `CATEGORIES` = the 5 slugs; `CATEGORY_SLUGS` also allows `"general"`.
- `load_candidates()` — sorted `data/candidates/candidate_*.md`.
- `build_prompt(candidate_text)` — instructs the model to separate CV vs interview notes, extract discrete short-string claims, tag each with a category slug or `general`, respond with JSON only.
- `extract_candidate()` — one `client.messages.create`, `max_tokens=2048`, JSON parse w/ fallback.
- `main()` — `load_dotenv()`, loop 10 candidates, write `solution/extracted_claims.json` as a list of `{candidate, cv_claims, interview_claims}`.
- Not run — user will test one candidate first.

---

## Retry 2

### Verbatim prompt

> The extraction test on candidate_03 worked well overall — good granularity
> and correct category tagging on nearly everything. But a few interview_claims
> in the output are conclusions/judgments rather than raw observations, which
> violates the "don't judge or reconcile" instruction:
>
> - "Response contradicts the CV claim of leading a team"
> - "CV claims of architecture ownership and team lead are not corroborated
>   and partly contradicted"
> - "Actual level looks like a competent mid-level individual contributor"
>
> These should not exist at the extraction stage — that judgment belongs to
> the crosscheck stage, not here. Extraction should only pull out what was
> literally said or observed (e.g. "Reference names a different person as the
> tech lead" is fine — that's a raw fact from the interview. "Response
> contradicts the CV" is not — that's a comparison/conclusion).
>
> Update the prompt in build_prompt() in solution/extract.py to more strongly
> enforce this boundary — add explicit negative examples showing the
> difference between a raw observation (keep) and a comparative/evaluative
> conclusion (exclude), so it doesn't produce claims that already reference
> "the CV" or use words like "contradicts", "corroborated", or "actual level".
>
> Don't run anything yet — I'll re-test on candidate_03 again after this fix.
>
> Log this as Retry 2 in trajectories/extract_build_run1.md.

### Plan / reasoning

Only `build_prompt()` changes. Add a "CRITICAL BOUNDARY" paragraph: extract only what was literally said/observed; ban the words "CV", "contradicts", "corroborated"/"uncorroborated", "actual level", "in reality", "does not match"; state that comparison is a later stage's job. Add a KEEP vs DROP example block using the exact failure cases the user cited (plus a couple of good ones). Add a line: if a source note already states a conclusion, extract only the underlying observation. No code/logic changes. Do not run.

### Tool calls

- `Read solution/extract.py` (lines 61–93) → confirmed current `build_prompt()` wording.
- `Edit solution/extract.py` → replaced the single "Do NOT judge..." line with the CRITICAL BOUNDARY paragraph + KEEP/DROP examples + the "extract the underlying observation, not the conclusion" line.
- `python -m py_compile solution/extract.py` → compiles OK.

### Final result

`build_prompt()` in `solution/extract.py` now hard-enforces the extraction/judgment boundary:
- banned-vocabulary list ("CV", "contradicts", "corroborated"/"uncorroborated", "actual level", "in reality", "does not match");
- 3 KEEP examples (raw fact / raw observation / direct paraphrase) and 3 DROP examples — the DROP examples are verbatim the three bad outputs the user flagged;
- explicit instruction to extract only the underlying observation when a source note already states a conclusion.
No other code changed. Not run — user will re-test candidate_03.

---

## Retry 3

### Verbatim prompt

> The extraction prompt fix worked — re-tested on candidate_03 and confirmed
> all three flagged conclusion-style claims are gone, replaced with clean raw
> observations, with no loss of the underlying evidence (reference naming a
> different tech lead, the "I don't really do the people stuff" quote, the
> deflection to "the docs would have that", etc. are all still captured).
>
> Task: Run the full extraction on all 10 candidates.
>
> 1. Run: python solution/extract.py
> 2. This will make 10 API calls and write solution/extracted_claims.json
> 3. After it completes, read back the file and give me a quick sanity check:
>    - Confirm all 10 candidates are present
>    - Confirm no cv_claims or interview_claims contain comparative/judgment
>      language (words like "contradicts", "corroborated", "actual level",
>      or explicit references to "the CV")
>    - Flag any candidate where extraction looks noticeably thinner or
>      richer than expected given their file length
>
> Log this as Retry 3 in trajectories/extract_build_run1.md.
>
> Do not modify extract.py in this task — if something looks wrong, report
> it and stop.

### Plan / reasoning

Run the script, read back the JSON, sanity-check. Do not modify `extract.py`. If it errors, report and stop.

### Tool calls

- `python solution/extract.py` → **FAILED on the first candidate (candidate_01).**
  `json.decoder.JSONDecodeError: Unterminated string starting at: line 32 column 12` from `json.loads(reply_text)`, and then `Expecting ',' delimiter: line 31 column 86` from the brace-slice fallback. Exit code 1. `solution/extracted_claims.json` was NOT written (the crash happens before any file write).

### Diagnosis (no fix applied, per instruction)

The model's extraction response for candidate_01 was **truncated mid-string** — the JSON ends partway through a claim, so it is not valid and neither `json.loads` nor the `{`…`}` slice can parse it.

Root cause: **`max_tokens=2048` in `extract_candidate()` is too small for the full claim list.** candidate_01 (Priya) is one of the richest files — many CV achievements + 5 detailed interview bullets — and the structured `{"text":..., "category":...}` output for every discrete claim exceeds 2048 output tokens, so the response is cut off (`stop_reason` would be `"max_tokens"`). The single-candidate tests only ever ran candidate_03, whose output fit under the cap, so this was not caught earlier.

Contributing weakness: `parse_json()` silently attempts recovery but has no handling for a genuinely truncated response, and `extract_candidate()` never checks `response.stop_reason`, so a truncation surfaces only as an opaque `JSONDecodeError`.

### Suggested fix (for the user to approve — NOT applied)

1. Raise `max_tokens` in `extract_candidate()` substantially (e.g. 4096–8192), enough for the largest candidate's full claim list.
2. Optionally: check `response.stop_reason == "max_tokens"` and raise a clear error ("extraction truncated for <candidate>, raise max_tokens") instead of letting it fail as a JSON parse error.

### Final result

Full extraction **did not complete**. Failed immediately on candidate_01 due to a truncated model response (`max_tokens=2048` too low). No `solution/extracted_claims.json` produced. `extract.py` not modified. Stopped and reported per instruction — awaiting direction on the fix.

---

## Retry 4

### Verbatim prompt

> Approved — apply both fixes:
>
> 1. Raise max_tokens in extract_candidate() to 8192, to safely cover the
>    richest candidate files' full claim lists with headroom.
> 2. Add a check: if response.stop_reason == "max_tokens", raise a clear
>    error naming the candidate (e.g. "Extraction truncated for {candidate}:
>    response hit max_tokens limit before completing").
>
> After applying, re-run: python solution/extract.py
>
> Same sanity checks as before once it completes:
> - Confirm all 10 candidates are present
> - Confirm no comparative/judgment language leaked into any claims
> - Flag anything noticeably thin or rich relative to file length
>
> Log this as Retry 4 in trajectories/extract_build_run1.md.

### Plan / reasoning

Apply both approved fixes to `extract_candidate()`. The `stop_reason` check needs the candidate name, so add a `name` parameter to `extract_candidate()` and pass it from `main()`. Then run and sanity-check.

### Tool calls

- `Edit solution/extract.py` → `extract_candidate(client, candidate_text)` → `extract_candidate(client, name, candidate_text)`; `max_tokens` 2048 → 8192; added `if response.stop_reason == "max_tokens": raise RuntimeError("Extraction truncated for {name}: response hit max_tokens limit before completing")`.
- `Edit solution/extract.py` → updated the call site in `main()` to `extract_candidate(client, name, candidate_text)`.
- `python -m py_compile solution/extract.py` → compiles OK.
- `python solution/extract.py` → completed. Printed `Extracting candidate_01...` … `candidate_10`, then `Wrote 10 extractions to ...\solution\extracted_claims.json`. No errors, no truncation.
- `Read solution/extracted_claims.json` → 10 objects.

### Sanity check

**1. All 10 present:** yes — `candidate_01` … `candidate_10`, each with non-empty `cv_claims` and `interview_claims`.

**2. No comparative/judgment language:** pass. Searched the whole file for `contradict`, `corroborat`, `actual level`, `the CV`, `does not match`, `in reality` → zero hits. The three conclusion-style claims that broke candidate_03 in the earlier single-candidate test are absent; the underlying evidence is retained as raw observations:
- "Reference names a different person as the tech lead"
- "Reference makes no mention of Marcus leading anyone"
- "When asked about handling a disagreement between two reports, said 'I don't really do the people stuff, I just made sure my parts landed'"
- "Deflected question by saying 'the docs would have that'"

Two minor, non-blocking interpretive phrasings (not CV-vs-interview comparisons, not banned vocab):
- candidate_02: *"Said 'the tables were already there', indicating no schema design experience"* — the "indicating…" tail is a light inference bolted onto a direct quote.
- candidate_02 / candidate_08: a few "Described as…" observations that echo the recruiter's own wording (e.g. "Described as the best SQL of the batch so far"). These are observations lifted from the notes, so acceptable.

**3. Thin / rich relative to file length:**

| Cand | cv_claims | interview_claims | total | note |
|------|-----------|------------------|-------|------|
| 01 | 13 | 17 | 30 | richest file, richest extraction — proportionate |
| 02 | 16 | 12 | 28 | cv side slightly granular — each one-word skill ("Skill: Git", "Skill: HTML/CSS") is its own claim |
| 03 | 11 | 11 | 22 | **lowest total** — but Marcus's file is genuinely short (3 terse roles, few skills); every key evidence point is captured, so content-complete, not thin |
| 04 | 14 | 18 | 32 | most interview_claims — 04's 5 interview bullets are compound; decomposition looks right |
| 05 | 12 | 11 | 23 | proportionate |
| 06 | 15 | 14 | 29 | proportionate |
| 07 | 14 | 16 | 30 | proportionate |
| 08 | 13 | 16 | 29 | proportionate |
| 09 | 13 | 17 | 30 | proportionate (captures the tenure/job-hopping facts as `general`) |
| 10 | 13 | 12 | 25 | proportionate |

No candidate is alarmingly thin or bloated. candidate_03 is the lightest in raw count but that tracks its short source file and misses none of the substance. candidate_02's CV extraction is the most granular (skill-per-line) — cosmetic, not a problem for the crosscheck stage.

Category tagging spot-checked across all 10 — accurate. A couple of defensible "general" tags on performance-optimisation achievements (e.g. candidate_09 connection-pooling latency work) that could arguably be `python_go`.

### Final result

Both fixes applied to `solution/extract.py` (`max_tokens=8192`; `max_tokens` stop-reason guard naming the candidate). Full run succeeded — `solution/extracted_claims.json` written with all 10 candidates. Sanity checks pass: 10/10 present, no comparative/judgment leakage, extraction volume proportionate to each file. Ready for the crosscheck stage.
