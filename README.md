# CandidLens

**CandidLens — an evidence-grounded candidate evaluator for backend engineering roles.**

CandidLens takes a job description, a candidate's CV, and a recruiter's interview notes, and produces a 1–5 score per skill category plus an overall score — but only after it has pulled the individual claims apart and checked the CV against the interview for things that don't line up. The output is a ranked report a hiring manager can actually read, with every score attached to the evidence behind it.

---

## The problem

If you've ever screened mid-level backend candidates, you know the shape of it. You've got a job description open in one tab, a CV in another, and a page of interview notes in a third. You read them one at a time. The CV says "designed the core API architecture from the ground up." The interview notes, twenty lines down, say the candidate couldn't explain why the services were split the way they were. Those two facts are in different documents, you read them four minutes apart, and it is genuinely easy to not notice that they contradict each other.

That's the bottleneck: a human reviewer holding three documents in their head at once, trying to weigh five different skill signals consistently across a stack of candidates, while also catching the places where a CV claim quietly falls apart under interview scrutiny. People are bad at doing all of that at the same time. You end up weighting the same signal differently for candidate 2 and candidate 7 because you were tired, or you take an impressive-sounding CV line at face value because nothing in the interview notes jumped out to contradict it — even though, read carefully, something did.

This matters because the failure is asymmetric. Missing a genuine weakness costs you a bad hire. Missing a _contradiction_ — where someone's claims don't survive contact with their own interview — is worse, because it's a signal about trust, and you only find out after they've started.

---

## Scope and human oversight

Everything in this repository — data, prompts, and code — was built during this hackathon; nothing existed beforehand. CandidLens is designed as a decision-support tool, not a decision-maker: it produces a ranked report with cited evidence, but the final hiring call stays with a human reviewer. The tool's job is to surface what a careful reviewer might miss across three documents, not to replace their judgment — this is also why the project's own ground truth (`data/human_reference_ranking.md`) is a human reviewer's ranking, not another model's.

---

## What CandidLens does

CandidLens runs the evaluation as four separate stages instead of one. Each stage exists because doing it all in a single pass is exactly where the baseline fails.

**1. Extract** (`solution/extract.py`) — Pull discrete claims out of the candidate file, keeping CV claims and interview observations in separate lists, and tag each with the skill category it relates to. This stage is deliberately not allowed to judge anything: it extracts what was literally said or observed ("could not explain why services were split where they were"), never a conclusion ("this contradicts the CV"). Separating extraction from judgment is what makes the next stage possible.

**2. Crosscheck** (`solution/crosscheck.py`) — Go through every CV claim and mark it _corroborated_, _uncorroborated_, or _contradicted_ against the interview observations. This stage exists because the baseline takes CV claims at face value with no way to catch inflation or fabrication. Crosscheck is the part that notices "led a team of 5 engineers" is contradicted by a reference who names someone else as the tech lead. It works only from the extracted claims — it never re-reads the raw file — so it can't smuggle in outside opinion.

**3. Score** (`solution/score.py`) — Produce the 1–5 category scores and the overall, using the crosscheck output. The rules are explicit: corroborated claims weigh positively, uncorroborated claims are weak evidence (not a penalty on their own), and a _contradicted_ claim weighs negatively — it's worse than no claim at all, because it's a credibility problem, not just missing evidence. If two or more contradicted claims together amount to a credibility problem, an integrity cap pulls the overall below the raw category average. This mirrors the same weighting the human reviewer applied in `data/human_reference_ranking.md` (Credibility/Integrity Cap, Behavioral/Collaboration Discount, JD-Critical Category Weighting).

**4. Aggregate** (`solution/aggregate.py`) — Pure Python, no model call. Merge the three prior stages into one report per candidate, rank all candidates by overall score (stable sort, ties keep input order), and write both `final_report.json` and a recruiter-readable `final_report.md`.

---

## The baseline

The baseline (`baseline/baseline.py`) is what CandidLens is measured against: one direct prompt with basic instructions, per the hackathon rules. For each candidate it sends Claude the job description and the full candidate file (CV + interview notes) in a single prompt and asks for a 1–5 score per category and an overall score. It is intentionally not engineered — there is no claim extraction, no cross-checking, no discrepancy flagging, and nowhere in its output to record one. It represents the "just ask the model" approach, and its main weakness is structural: it blends every signal into one number in a single pass, so an inflated CV line and a corroborated one are worth the same to it.

---

## Measured improvement

From `eval/results.md` (run by `eval/run_eval.py`, no API calls — pure comparison of existing stage outputs against `data/human_reference_ranking.md`):

| Metric                                                                          | Baseline | Agent     |
| ------------------------------------------------------------------------------- | -------- | --------- |
| Mean Absolute Error vs human overall (all 10 candidates)                        | 0.500    | **0.400** |
| MAE vs human overall, excluding candidate_03 (deliberate integrity-cap outlier) | 0.500    | **0.278** |
| Spearman's ρ vs human ranking (tie-averaged ranks)                              | 0.792    | **0.859** |
| Candidates whose ranking position differs from human by more than 1             | 5        | **0**     |
| Flagged candidate_03's CV/interview contradiction                               | No       | **Yes**   |

On the contradiction: the baseline's `candidate_03` record has no discrepancy or contradiction field at all — it structurally cannot surface a CV/interview conflict. The agent's `candidate_03` record carries 2 contradicted CV claims and 2 discrepancy-summary findings with cited interview evidence ("Claims to have led a team of 5 engineers…" → "Reference names a different person as the tech lead", "Reference makes no mention of Marcus leading anyone", and the candidate's own "I don't really do the people stuff").

The five candidates the baseline misplaces by more than one position (04, 05, 06, 07, 08) are all in the middle of the field, where the baseline collapses six candidates into a tie at overall 3 and can't separate them. The agent's scoring pulls Tomasz (05) and Rohan (08) up into the top group where the human ranked them.

---

## Improvement changelog

Every entry here is a real iteration from `trajectories/` — what was tried, what evidence showed the problem, what was decided.

### Baseline — established starting point

Built as a single-prompt scorer. During the build the model constant was corrected from `claude-opus-5` to `claude-sonnet-5` so the baseline and all four solution stages run on the same model and the comparison isn't confounded by model choice. The full baseline run confirmed it gets the top and bottom of the field roughly right but produces a six-way tie in the middle (overall 3 for candidates 04, 05, 07, 08, 09, 10) and scores Marcus a 2 only because his interview notes read negatively on their face — not because it detected the CV/interview contradiction, which it has no mechanism to do.

### Extraction v1 → v2 — `max_tokens` truncation bug

v1 used `max_tokens=2048`. The first full run failed immediately on candidate_01 (the richest file) with `json.decoder.JSONDecodeError: Unterminated string` — the model's claim list was cut off mid-output and the result was unparseable. The single-candidate tests had only ever exercised candidate_03, whose output fit under the cap, so it wasn't caught earlier. **Decision:** raise `max_tokens` to 8192 and add a `response.stop_reason == "max_tokens"` guard that raises a clear error naming the candidate instead of failing as an opaque JSON error. The same guard pattern was then carried into every later stage.

### Extraction — judgment leaking into raw claims

The candidate_03 test produced `interview_claims` that were conclusions, not observations: "Response contradicts the CV claim of leading a team", "CV claims of architecture ownership and team lead are not corroborated", "Actual level looks like a competent mid-level individual contributor". Comparison is the crosscheck stage's job; extraction is not supposed to do it. **Decision:** add a "critical boundary" section to the prompt — extract only what was literally said or observed, ban claims containing "CV" / "contradicts" / "corroborated" / "actual level", and give three KEEP vs three DROP worked examples using the exact bad outputs. Re-test confirmed the conclusions were gone and the underlying evidence (the reference naming a different tech lead, the "I don't really do the people stuff" quote, the "the docs would have that" deflection) was all still captured.

### Crosscheck v1 → v2 — limited depth misclassified as contradiction

The first full crosscheck run flagged false-positive contradictions on "listed skill + limited interview demo": candidate_06's "Lists PostgreSQL as a key skill" was marked _contradicted_ because she needed a hint on a window function (even though the same interview showed she got a join right); candidate_09's "AWS (ECS, ALB, RDS) skill" was _contradicted_ for "less sure on networking/IaC" (despite "comfortable deploying to ECS" in the same notes); candidate_02's "Skill: SQLite" was _contradicted_ for a struggled join. The bar was also applied inconsistently — candidate_07 had a _weaker_ demonstrated SQL showing and wasn't flagged at all. **Decision:** add explicit guidance that _contradicted_ requires evidence of actual inability or something actively incompatible, not merely limited depth, needing a hint, or modesty about skill level — and that the model must first check whether any interview claim also _supports_ the claim. Added a worked PostgreSQL example. The subset re-test and full re-run resolved candidate_02, candidate_06, and candidate_09 to _corroborated_, kept candidate_07 consistent, and dropped the batch-wide contradiction count from 6 to 3. Marcus's two genuine contradictions were untouched.

- **Kept, not removed:** candidate_09's "Quillstone Software 1.5 years" vs the interview's "none over ~14 months" stayed flagged as _contradicted_. It was considered for removal as over-strict, but it's a literal numeric conflict (18 months vs ~14), a different class from the skill-depth false positives, and the fix was deliberately scoped to leave it in place.

### Scoring v1 → v2 — collaboration over-penalised, demonstrated failure under-penalised

The first full scoring run surfaced two problems. **(a) Tomasz (candidate_05):** the model applied the collaboration/behavioural discount (rule 4: standalone negative interview evidence) as harshly as the integrity cap (rule 5: CV/interview contradictions). His technical categories averaged ~4.25 but the overall was pulled to 3, versus the human's 4.0 — a behavioural red flag is a softer thing than a credibility violation and shouldn't cost the same. **(b) Dylan (candidate_02):** several CV skill claims were marked "uncorroborated" by crosscheck and then scored as "no penalty", even though the interview showed active inability ("couldn't do a two-table join", "never deployed anything") — a demonstrated failure, not just an absence of evidence. **Decision:** rule 3 now states that demonstrated failure in the interview must pull the category down regardless of the crosscheck label; rule 4 is now an explicit _moderate_ discount, softer than rule 5; rule 5 is reserved for CV/interview contradictions only. After the fix, Tomasz's overall went 3 → 4 (matching the human), and the demonstrated-failure reasoning became explicit in the rationales for Dylan, Sistine, and Rohan.

- **Model choice, held constant:** `claude-sonnet-5` is pinned in a commented constant in `baseline/baseline.py` and all four `solution/*.py` stages, specifically so no result can be explained away by a model difference between baseline and agent.

---

## Main failure mode + hot take

**The ceiling is compressed.** No candidate ever scores a perfect overall 5. In the final run, five candidates (01, 05, 06, 08, 09) tie at overall 4, which flattens the top of the ranking — Priya, who the human reviewer put clearly first at 4.5, ends up sharing the top slot with four other people. The cause is a specific scoring rule: an "uncorroborated" CV claim is treated as moderate-credit-only, and that hits even the strongest candidate, because her CV lists Go and the interview happened to focus on Python, so `python_go` gets a 3. The rule is doing what it's told; the side effect is that a genuinely excellent candidate can't get full marks on a category the interview didn't specifically probe. This is a known, accepted limitation, not a bug — but for a production version it's the first thing I'd tune.

**The integrity cap is stricter than a human's, on purpose.** On Marcus (candidate_03), the agent gives an overall of 1 where the human reviewer gave 2.5. Both are applying the same principle — two contradicted claims about seniority and ownership are a credibility problem, and the overall should sit below the raw category average of ~2.2. The human pulled it down to 2.5; the agent pulled it to 1. Neither is wrong; the distance the cap travels below the raw average is a real tunable parameter, and a production deployment should expose it rather than bake in "as strict as possible". I named this explicitly rather than hiding it, and the eval reports MAE both with and without Marcus so the deliberate divergence is visible instead of quietly inflating the error number.

**The takeaway.** The thing that actually made this work wasn't any single clever prompt — it was that every fix in the changelog above came from a specific observed failure, not a hunch, and the only reason those failures were visible is that every stage was tested and reviewed before moving to the next one, with the full history kept in the trajectory logs. Two things generalise. First, a verification step only helps if the verifier is calibrated: the crosscheck stage was actively harmful in v1 because it called "limited depth" a "contradiction", and it took a worked counter-example in the prompt to fix that. Second, splitting the job into extract → check → score beats one big prompt precisely because you can inspect and correct each stage independently — the single-pass baseline gives you one number and no way to ask why. Reliable evaluation agents look less like a good prompt and more like a pipeline you can debug.

---

## Setup / tech stack

- **Python** (developed on 3.12)
- **Anthropic API** — `claude-sonnet-5`, used identically across `baseline/baseline.py` and all four `solution/*.py` stages
- **python-dotenv** — the API key is read from a local `.env` file (`ANTHROPIC_API_KEY`), never hardcoded or committed (`.env` is gitignored; see `.env.example`)

```bash
pip install -r requirements.txt
cp .env.example .env        # macOS/Linux   — then put your key in .env
copy .env.example .env      # Windows
```

Run order: `python baseline/baseline.py`, then `python solution/extract.py` → `crosscheck.py` → `score.py` → `aggregate.py`, then `python eval/run_eval.py`.

Full setup and reproduction steps: [`docs/reproduction.md`](docs/reproduction.md) _(built next)_.

---

## Project structure

```
candidlens/
├── README.md
├── AGENT_INSTRUCTIONS.md          # rules the coding agent followed
├── requirements.txt
├── .env.example
├── baseline/
│   ├── baseline.py                # single-prompt baseline scorer
│   └── baseline_results.json
├── solution/
│   ├── extract.py                 # stage 1 → extracted_claims.json
│   ├── crosscheck.py              # stage 2 → crosscheck_results.json
│   ├── score.py                   # stage 3 → score_results.json
│   ├── aggregate.py               # stage 4 → final_report.json / final_report.md
│   └── *.json / final_report.md
├── eval/
│   ├── run_eval.py                # baseline vs agent vs human → results.md
│   └── results.md
├── data/
│   ├── jd.md                      # the role
│   ├── human_reference_ranking.md # human reviewer's scores + methodology
│   └── candidates/
│       └── candidate_01.md … candidate_10.md   # synthetic candidates
├── docs/
│   └── reproduction.md
└── trajectories/                  # full build history, one file per task
```

All candidate data in `data/` is synthetic.

---

## Disclosure

Coding agent used: **Claude Code** — via a claude.ai subscription for development (writing the pipeline, iterating on prompts, running the eval). The runtime pipeline itself calls the **Anthropic API** directly (`claude-sonnet-5`).

The complete development history — every prompt, plan, tool call, error, retry, and decision — is logged in [`trajectories/`](trajectories/), one file per task.
