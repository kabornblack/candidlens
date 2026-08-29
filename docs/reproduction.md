# Reproduction guide

Step-by-step instructions to run CandidLens from a clean machine. Follow the
commands in order. Run every command from the repository root.

---

## 1. Prerequisites

- **Python 3.12 or newer.** Check with `python --version`.
- **An Anthropic API key** (your own). The pipeline calls the Anthropic API
  (`claude-sonnet-5`) for 40 requests total across a full run. Based on the
  token sizes observed while building this project, **one full run costs
  roughly USD $0.50** (well under $1). See section 6 for the breakdown.
- **git**, to clone the repository.

No other services, databases, or accounts are required. All candidate data
in the repo is synthetic.

---

## 2. Clone and install

```bash
git clone <repo-url>
cd candidlens
pip install -r requirements.txt
```

`requirements.txt` installs two packages: `anthropic` (the API client) and
`python-dotenv` (loads the API key from a local file).

**Optional but recommended** — use a virtual environment so the install
doesn't touch your system Python:

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

`.venv/` is already git-ignored.

---

## 3. API key setup

Copy the example env file and add your key:

```bash
cp .env.example .env        # macOS/Linux
copy .env.example .env      # Windows
```

Then open `.env` and replace the placeholder:

```
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

The key must be **workspace-scoped** (created inside a workspace in the
Anthropic Console). An identity- or organization-scoped key will fail — see
section 7.

`.env` is git-ignored; your key is never committed. The scripts read it via
`python-dotenv`, which searches upward from the current directory, so run the
commands from the repository root.

---

## 4. Run order

Run these six commands one at a time, in this order. The first four call the
API; the last two are pure Python.

**The order is a hard requirement, not a suggestion.** Each solution stage
reads the JSON written by the previous one (`crosscheck` reads `extract`'s
output, `score` reads `crosscheck`'s, `aggregate` reads all three, `eval`
reads `aggregate`'s `final_report.json`). Running a stage before the one it
depends on will fail outright or produce results built from stale data. If
you re-run one stage, re-run every stage after it as well. (`baseline` is
independent of the solution stages and may be run at any point, but it must
have run before `eval`.)

### 4.1 Baseline

```bash
python baseline/baseline.py
```

- **Produces:** `baseline/baseline_results.json`
- **API calls:** 10 (one per candidate) · **Time:** ~1–2 minutes
- **Successful console output:**
  ```
  Scoring candidate_01...
  Scoring candidate_02...
  ...
  Scoring candidate_10...
  Wrote 10 results to <repo>/baseline/baseline_results.json
  ```

### 4.2 Extract (solution stage 1)

```bash
python solution/extract.py
```

- **Produces:** `solution/extracted_claims.json`
- **API calls:** 10 · **Time:** ~2–3 minutes (this stage produces the most output)
- **Successful console output:**
  ```
  Extracting candidate_01...
  ...
  Extracting candidate_10...
  Wrote 10 extractions to <repo>/solution/extracted_claims.json
  ```

### 4.3 Crosscheck (solution stage 2)

```bash
python solution/crosscheck.py
```

- **Reads:** `solution/extracted_claims.json`
- **Produces:** `solution/crosscheck_results.json`
- **API calls:** 10 · **Time:** ~1–3 minutes
- **Successful console output:**
  ```
  Cross-checking candidate_01...
  ...
  Cross-checking candidate_10...
  Wrote 10 crosscheck results to <repo>/solution/crosscheck_results.json
  ```

### 4.4 Score (solution stage 3)

```bash
python solution/score.py
```

- **Reads:** `solution/crosscheck_results.json` and `solution/extracted_claims.json`
- **Produces:** `solution/score_results.json`
- **API calls:** 10 · **Time:** ~1–3 minutes
- **Successful console output:**
  ```
  Scoring candidate_01...
  ...
  Scoring candidate_10...
  Wrote 10 score results to <repo>/solution/score_results.json
  ```

### 4.5 Aggregate (solution stage 4)

```bash
python solution/aggregate.py
```

- **Reads:** `solution/extracted_claims.json`, `solution/crosscheck_results.json`,
  `solution/score_results.json`, and the candidate file headers in `data/candidates/`
- **Produces:** `solution/final_report.json` and `solution/final_report.md`
- **API calls:** 0 (pure Python) · **Time:** < 1 second
- **Successful console output:**
  ```
  Wrote <repo>/solution/final_report.json
  Wrote <repo>/solution/final_report.md

     1. Priya Raghunathan (candidate_01) — overall 4
     2. Tomasz Wrenfield (candidate_05) — overall 4
     ...
    10. Marcus Delgado-Finn (candidate_03) — overall 1
  ```

### 4.6 Evaluation

```bash
python eval/run_eval.py
```

- **Reads:** `baseline/baseline_results.json`, `solution/final_report.json`,
  `data/human_reference_ranking.md`
- **Produces:** `eval/results.md`
- **API calls:** 0 (pure Python) · **Time:** < 1 second
- **Successful console output:** the full comparison report is printed to the
  console, ending with:
  ```
  (written to <repo>/eval/results.md)
  ```

---

## 5. Where to look at the results

- **`eval/results.md`** — the main comparison: baseline vs agent vs human
  reference, with MAE, Spearman's ρ, the position-difference count, and the
  candidate_03 contradiction finding.
- **`solution/final_report.md`** — the readable candidate report: all 10
  candidates in ranked order, each with a category-score table, any flagged
  discrepancies, and the overall rationale.
- `solution/final_report.json` — the same report as structured data.
- `baseline/baseline_results.json`, `solution/*.json` — the raw per-stage
  outputs if you want to inspect intermediate steps.

---

## 6. Cost estimate for a full run

Pricing for `claude-sonnet-5`: **$2.00 per 1M input tokens, $10.00 per 1M
output tokens.**

| Stage | API calls | Approx. tokens (all 10 candidates) | Approx. cost |
| --- | --- | --- | --- |
| baseline | 10 | ~13k in / ~1k out | ~$0.04 |
| extract | 10 | ~14k in / ~14k out | ~$0.17 |
| crosscheck | 10 | ~30k in / ~9k out | ~$0.15 |
| score | 10 | ~35k in / ~7k out | ~$0.14 |
| aggregate | 0 | — | $0.00 |
| eval | 0 | — | $0.00 |
| **Total** | **40** | | **~$0.50** |

These are estimates from the prompt sizes and observed output lengths, not
metered billing. Expect roughly $0.40–$0.70 for a clean end-to-end run.

---

## 7. Troubleshooting

### `RuntimeError: <stage> truncated for candidate_XX: response hit max_tokens limit before completing`

(Where `<stage>` is `Extraction`, `Crosscheck`, or `Scoring`.)

**Meaning:** the model's JSON response was cut off before it finished, so it
couldn't be parsed. The stage stops immediately and names the candidate
rather than failing with an opaque JSON error.

**Fix:** `extract.py`, `crosscheck.py`, and `score.py` already use
`max_tokens=8192`, which covered all 10 candidates in testing. If you hit
this:

1. Re-run the command — a truncated response is often a transient blip.
2. If it recurs on the same candidate, raise `max_tokens` in that stage's
   `*_candidate()` function (e.g. `extract_candidate()` in `extract.py`) and
   re-run.

### Authentication or permission error mentioning a workspace / `anthropic-workspace-id`

**Meaning:** the API key in `.env` is identity-scoped or organization-scoped
rather than workspace-scoped. The pipeline sends no workspace header, so the
key itself has to belong to a workspace.

**Fix:** in the Anthropic Console, open a workspace and create an API key
from inside it. Put that key in `.env` (replacing the previous one) and
re-run. An organization/admin key (`sk-ant-admin...`) will not work here.
