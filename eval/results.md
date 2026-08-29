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
