# Trajectory — Candidate Generation (run 1)

## Verbatim prompt

> Before starting the actual task below, first create trajectories/00_setup.md
> and log the following as its content, labeled clearly as "Setup — Agent
> Instructions & Acknowledgment":
> - The full AGENT_INSTRUCTIONS.md content I gave you as the first prompt
> - Your acknowledgment response (the one you gave me)
>
> Once that's saved, proceed with the first real task:
>
> Task: Generate 10 synthetic candidate profiles for the CandidLens project.
>
> Read data/jd.md first for context.
>
> Create 10 files: data/candidates/candidate_01.md through candidate_10.md.
> Each file should contain:
> 1. A short CV summary (name, years experience, past 2-3 roles, key skills,
>    1-2 claimed achievements)
> 2. Interview notes (3-5 short bullet points, written like a recruiter's
>    raw notes, covering technical depth, communication, and any red/green flags)
>
> Requirements across the set of 10:
> - Candidate 01 should be a clearly STRONG match to the JD (real depth across
>   all 5 skill categories, interview notes corroborate the CV).
> - Candidate 02 should be a clearly WEAK match (junior-level experience
>   mismatched to a mid-level role, thin technical answers in interview).
> - Candidate 03 should have a DELIBERATE CONTRADICTION: the CV claims a
>   significant achievement (e.g. "led a team of 5 engineers" or "designed
>   the company's core API architecture") that the interview notes either
>   fail to corroborate or actively contradict (e.g. interview notes show
>   the candidate couldn't explain basic architecture decisions, or teammates
>   describe them as an individual contributor, not a lead).
> - Candidates 04-10 should be a realistic mixed spread: varying strength
>   across the 5 skill categories, some stronger in SQL but weaker in cloud,
>   some strong technically but weak on collaboration signals, etc. Make them
>   feel like real, distinct people, not templated variations.
> - All names, companies, and details must be fully synthetic/fictional.
>
> Log this task in trajectories/candidate_generation_run1.md per the agent
> instructions.

## Plan / reasoning

1. Create `trajectories/00_setup.md` with the agent instructions + acknowledgment (done first, separate deliverable).
2. Read `data/jd.md` for the 5 scoring categories: (1) Python/Go, (2) REST API design, (3) SQL/data modeling, (4) Cloud infra, (5) Ownership & collaboration. Role is mid-level, 3–5 yrs.
3. Also checked `data/human_reference_ranking.md` (empty) and existing `data/` layout — no `data/candidates/` dir yet, will be created by the first Write.
4. Design 10 distinct people:
   - 01 Priya Raghunathan — STRONG: real depth in all 5, interview corroborates.
   - 02 Dylan Prewitt — WEAK: ~1 yr / bootcamp, thin answers, mid-level mismatch.
   - 03 Marcus Delgado-Finn — CONTRADICTION: CV claims "designed core API architecture" + "led a team of 5"; interview + references show IC-only, can't explain arch decisions.
   - 04 Yuki Abernathy — strong SQL + Python, weak cloud (on-prem past), solid collaboration.
   - 05 Tomasz Wrenfield — strong Go/REST/cloud, weak collaboration (abrasive in review).
   - 06 Amara Okonkwo-Bright — solid all-round, slightly junior (3 yrs), strong mentoring/collab, average SQL.
   - 07 Sistine Vale — strong cloud + Python, weak SQL (ORM-reliant, couldn't write a join).
   - 08 Rohan Marchetti — ex-data-engineer: strong SQL + GCP, weaker REST API design, good collab.
   - 09 Bjorn Castellanos — Go specialist, strong REST, medium SQL/cloud, terse comms, job-hopping concern.
   - 10 Nadia Kessler — true borderline generalist (~3.5 yrs), middling everywhere, no alarms.
5. Write each file: CV summary block + Interview notes bullets. All names/companies fictional. No real-person data. No credentials anywhere.
6. Append tool calls + final result to this trajectory.

## Tool calls

- `Read data/jd.md` → mid-level backend JD, 5 eval skill categories (see plan).
- `Read AGENT_INSTRUCTIONS.md` → matches first prompt (repo copy titled "CandidLens Project").
- `Glob data/**` → `data/jd.md`, `data/human_reference_ranking.md`.
- `Read data/human_reference_ranking.md` → empty file.
- `Write trajectories/00_setup.md` → created.
- `Write trajectories/candidate_generation_run1.md` → this file.
- `Write data/candidates/candidate_01.md` .. `candidate_10.md` → see final result below.

## Final result

Created 10 files `data/candidates/candidate_01.md` … `candidate_10.md`. Summary of the intended match profile for each:

| # | Name | Intended signal |
|---|------|-----------------|
| 01 | Priya Raghunathan | Strong across all 5; interview corroborates CV |
| 02 | Dylan Prewitt | Weak — junior (~1 yr), thin technical answers |
| 03 | Marcus Delgado-Finn | Contradiction — CV claims architecture lead + team of 5; interview/refs show IC, can't explain arch |
| 04 | Yuki Abernathy | Strong SQL/Python, weak cloud, solid collab |
| 05 | Tomasz Wrenfield | Strong Go/REST/cloud, weak collaboration (abrasive) |
| 06 | Amara Okonkwo-Bright | Solid all-round, slightly junior, strong mentoring; green flags |
| 07 | Sistine Vale | Strong cloud/Python, weak SQL/data modeling |
| 08 | Rohan Marchetti | Ex-data-eng: strong SQL + GCP, weaker REST API design |
| 09 | Bjorn Castellanos | Go specialist, strong REST, medium SQL/cloud, terse comms, job-hopping flag |
| 10 | Nadia Kessler | Borderline generalist — middling on every category, no red flags |

All names, companies, projects, and metrics are fictional. No real resume/LinkedIn data used. No credentials or secrets written to any file.
