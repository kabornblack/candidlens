# Trajectory — Reference Ranking Template (run 1)

## Verbatim prompt

> Task: Create data/human_reference_ranking.md as an empty scoring template
> (no scores filled in — I will fill these in myself as the human reviewer).
>
> For each of the 10 candidates, create a section with:
> - Candidate name and number
> - Five score fields (1-5 each): Python/Go, REST API design, SQL/data
>   modeling, Cloud infrastructure, Ownership & collaboration
> - An Overall score field (1-5)
> - A short notes field for discrepancies/flags I observe
>
> End the file with a "Final Ranking (1-10, best to worst)" section as an
> empty ordered list for me to fill in after scoring everyone.
>
> Log this in trajectories/reference_ranking_template_run1.md per the agent
> instructions.

## Plan / reasoning

- `data/human_reference_ranking.md` already exists but is EMPTY. This task explicitly asks me to create/populate it, so filling it is the active task on that exact file — no separate confirmation needed.
- Score fields use the 5 JD evaluation categories, all blank (`__ / 5`), so the human reviewer fills them in.
- Candidate names/numbers taken from `data/candidates/candidate_01.md`..`candidate_10.md` created in the prior task.
- Add an empty notes line per candidate.
- End with "Final Ranking (1–10, best to worst)" as a blank numbered list 1–10.
- No scores, no opinions, no pre-filled ranking — template only.

## Tool calls

- `Write trajectories/reference_ranking_template_run1.md` → this file.
- `Write data/human_reference_ranking.md` → template created (was empty).

## Final result

Created `data/human_reference_ranking.md`: 10 blank candidate scoring blocks (5 category fields + Overall + Notes, all unfilled) followed by an empty "Final Ranking (1–10, best to worst)" numbered list. No scores filled in.
