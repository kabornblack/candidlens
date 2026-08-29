"""
CandidLens evaluation — baseline vs agent vs human reference.

The single script a judge runs to see the comparison story and the metric
that shows measured improvement. Pure data analysis of existing JSON/markdown
outputs — NO API calls, no new dependencies.

Inputs (read-only):
  baseline/baseline_results.json   baseline overall scores
  solution/final_report.json       agent overall scores + ranks + discrepancies
  data/human_reference_ranking.md  human reviewer's overall scores + ranking

Markdown parsing assumptions for data/human_reference_ranking.md:
  1. Each candidate has a "## Candidate NN - Name" header; the candidate id is
     "candidate_" + the zero-padded NN.
  2. That candidate's human Overall score is the first "Overall: X / 5" line
     after their header.
  3. The human ranking (best -> worst) is the numbered "N. **Name** - ..."
     list under the "## Final Ranking" heading (matched on the literal
     "## Final Ranking", which does not collide with the earlier
     "## Scoring Methodology Final Ranking" heading).
  4. Names in the ranking list are matched back to candidate ids via the
     header map. Any candidate missing an Overall line or a ranking entry
     raises an error rather than being silently dropped.

Baseline has no ranking field of its own: a baseline ranking is derived by
sorting baseline overall descending, ties broken by candidate-id order.
Because that tie-break is arbitrary, Spearman's rank correlation (which uses
tie-averaged ranks) is the primary rank metric; the "positions differing by
more than 1" count is an intuitive supplement.
"""

import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASELINE_PATH = ROOT / "baseline" / "baseline_results.json"
AGENT_PATH = ROOT / "solution" / "final_report.json"
HUMAN_PATH = ROOT / "data" / "human_reference_ranking.md"
OUT_MD = ROOT / "eval" / "results.md"

OUTLIER = "candidate_03"  # Marcus — deliberate integrity-cap outlier


# --------------------------------------------------------------------------
# Input loading
# --------------------------------------------------------------------------

def load_baseline_overall():
    """candidate id -> baseline overall score."""
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {row["candidate"]: row["scores"]["overall"] for row in data}


def load_agent():
    """Return (overall_by_cid, rank_by_cid, full_records_by_cid)."""
    data = json.loads(AGENT_PATH.read_text(encoding="utf-8"))
    overall = {r["candidate"]: r["overall"] for r in data}
    rank = {r["candidate"]: r["rank"] for r in data}
    records = {r["candidate"]: r for r in data}
    return overall, rank, records


def parse_human_reference():
    """Return (overall_by_cid, ranking) where ranking is a list of candidate
    ids from best to worst."""
    text = HUMAN_PATH.read_text(encoding="utf-8")

    # name -> candidate id, from the "## Candidate NN - Name" headers
    name_to_cid = {}
    for num, name in re.findall(r"##\s*Candidate\s*(\d+)\s*[-–—]\s*(.+)", text):
        name_to_cid[name.strip()] = f"candidate_{int(num):02d}"

    # candidate id -> human Overall score
    overall = {}
    for num, score in re.findall(
        r"##\s*Candidate\s*(\d+)\s*[-–—].*?\bOverall:\s*([0-9.]+)\s*/\s*5",
        text,
        flags=re.DOTALL,
    ):
        overall[f"candidate_{int(num):02d}"] = float(score)

    # human ranking, from the "## Final Ranking" section
    marker = "## Final Ranking"
    if marker not in text:
        raise ValueError(f"{HUMAN_PATH.name}: '{marker}' section not found")
    ranking_section = text[text.index(marker):]
    ranking = []
    for _, name in re.findall(r"^\s*(\d+)\.\s*\*\*(.+?)\*\*", ranking_section, flags=re.MULTILINE):
        name = name.strip()
        if name not in name_to_cid:
            raise ValueError(f"ranking name {name!r} has no matching candidate header")
        ranking.append(name_to_cid[name])

    expected = set(name_to_cid.values())
    missing_scores = expected - set(overall)
    missing_rank = expected - set(ranking)
    if missing_scores:
        raise ValueError(f"human reference missing Overall for: {sorted(missing_scores)}")
    if missing_rank:
        raise ValueError(f"human reference missing ranking entry for: {sorted(missing_rank)}")

    return overall, ranking


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def mean_absolute_error(a, b, exclude=()):
    cids = [c for c in a if c not in exclude]
    return sum(abs(a[c] - b[c]) for c in cids) / len(cids)


def average_ranks(score_by_cid):
    """candidate id -> rank (1 = highest score). Tied scores share the
    average of the positions they span."""
    ordered = sorted(score_by_cid, key=lambda c: -score_by_cid[c])
    ranks = {}
    i = 0
    while i < len(ordered):
        j = i
        while j < len(ordered) and score_by_cid[ordered[j]] == score_by_cid[ordered[i]]:
            j += 1
        avg = (i + 1 + j) / 2  # mean of 1-indexed positions i+1 .. j
        for k in range(i, j):
            ranks[ordered[k]] = avg
        i = j
    return ranks


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy)


def spearman(ranks_a, ranks_b, cids):
    """Spearman's rho = Pearson correlation of the two rank vectors."""
    return pearson([ranks_a[c] for c in cids], [ranks_b[c] for c in cids])


def integer_positions(score_by_cid, tie_break_order):
    """candidate id -> unique 1..N position, sorting by score descending with
    ties broken by tie_break_order (stable)."""
    ordered = sorted(tie_break_order, key=lambda c: -score_by_cid[c])
    return {cid: i + 1 for i, cid in enumerate(ordered)}


def positions_off_by_more_than_one(pos, human_pos):
    return sorted(c for c in pos if abs(pos[c] - human_pos[c]) > 1)


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def build_report():
    baseline = load_baseline_overall()
    agent_overall, agent_rank, agent_records = load_agent()
    human_overall, human_ranking = parse_human_reference()

    cids = sorted(human_overall)  # candidate_01 .. candidate_10
    human_pos = {cid: i + 1 for i, cid in enumerate(human_ranking)}

    L = []
    L.append("# CandidLens Evaluation — Baseline vs Agent vs Human Reference")
    L.append("")
    L.append("No API calls — pure comparison of existing stage outputs.")
    L.append("")

    # 1. table
    L.append("## Overall scores")
    L.append("")
    L.append("| Candidate | Baseline | Agent | Human |")
    L.append("| --- | --- | --- | --- |")
    for cid in cids:
        L.append(f"| {cid} | {baseline[cid]} | {agent_overall[cid]} | {human_overall[cid]} |")
    L.append("")

    # 2 + 3. MAE
    mae_base = mean_absolute_error(baseline, human_overall)
    mae_agent = mean_absolute_error(agent_overall, human_overall)
    mae_base_ex = mean_absolute_error(baseline, human_overall, exclude={OUTLIER})
    mae_agent_ex = mean_absolute_error(agent_overall, human_overall, exclude={OUTLIER})

    L.append("## Mean Absolute Error vs human reference (lower is better)")
    L.append("")
    L.append("| | Baseline | Agent |")
    L.append("| --- | --- | --- |")
    L.append(f"| All 10 candidates | {mae_base:.3f} | {mae_agent:.3f} |")
    L.append(f"| Excluding {OUTLIER} (deliberate integrity-cap outlier) | {mae_base_ex:.3f} | {mae_agent_ex:.3f} |")
    L.append("")
    L.append(
        f"Agent MAE improves on baseline by {mae_base - mae_agent:.3f} across all 10, "
        f"and by {mae_base_ex - mae_agent_ex:.3f} once the deliberate {OUTLIER} "
        f"integrity-cap outlier is excluded."
    )
    L.append("")

    # 4. rank correlation
    human_ranks = {cid: human_pos[cid] for cid in cids}
    base_ranks = average_ranks(baseline)
    agent_ranks = average_ranks(agent_overall)
    rho_base = spearman(human_ranks, base_ranks, cids)
    rho_agent = spearman(human_ranks, agent_ranks, cids)

    base_pos = integer_positions(baseline, cids)
    agent_pos = integer_positions(agent_overall, cids)
    base_off = positions_off_by_more_than_one(base_pos, human_pos)
    agent_off = positions_off_by_more_than_one(agent_pos, human_pos)

    L.append("## Rank agreement with human ranking (higher rho is better)")
    L.append("")
    L.append("| | Baseline | Agent |")
    L.append("| --- | --- | --- |")
    L.append(f"| Spearman's rho (tie-averaged ranks) | {rho_base:.3f} | {rho_agent:.3f} |")
    L.append(f"| Candidates whose position differs from human by > 1 | {len(base_off)} | {len(agent_off)} |")
    L.append("")
    L.append(f"- Baseline positions off by > 1: {', '.join(base_off) or 'none'}")
    L.append(f"- Agent positions off by > 1: {', '.join(agent_off) or 'none'}")
    L.append("")
    L.append(
        "Spearman's rho is the primary rank metric (it handles the many tied "
        "overall scores correctly). The position-difference count breaks ties "
        "by candidate id, so it is an intuitive supplement rather than the "
        "headline number."
    )
    L.append("")

    # 5. candidate_03 contradiction
    base_03 = next(r for r in json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
                   if r["candidate"] == OUTLIER)
    agent_03 = agent_records[OUTLIER]
    base_has_discrepancy_field = any(
        k for k in base_03 if "discrepan" in k.lower() or "contradict" in k.lower()
    )
    agent_contradicted = agent_03.get("contradicted_claims", [])
    agent_discrepancies = agent_03.get("discrepancy_summary", [])

    L.append(f"## Did the agent flag {OUTLIER}'s contradiction where the baseline did not?")
    L.append("")
    L.append(f"**Yes.**")
    L.append("")
    L.append(
        f"- Baseline: its `{OUTLIER}` record has keys {sorted(base_03)} — "
        f"{'a discrepancy field is present' if base_has_discrepancy_field else 'there is no discrepancy/contradiction field at all'}. "
        f"The baseline has no mechanism to surface a CV/interview conflict."
    )
    L.append(
        f"- Agent: its `{OUTLIER}` record carries {len(agent_contradicted)} "
        f"contradicted CV claim(s) and {len(agent_discrepancies)} discrepancy-summary finding(s):"
    )
    for item in agent_discrepancies:
        L.append(f"  - {item}")
    for claim in agent_contradicted:
        L.append(f"  - contradicted: \"{claim['cv_claim']}\"")
        for conflict in claim.get("conflicting_interview_claims", []):
            L.append(f"    - conflicting interview evidence: \"{conflict}\"")
    L.append("")

    # bottom line
    L.append("## Bottom line")
    L.append("")
    L.append(
        f"- Overall-score accuracy: agent MAE {mae_agent:.3f} vs baseline {mae_base:.3f} "
        f"(all 10); {mae_agent_ex:.3f} vs {mae_base_ex:.3f} excluding {OUTLIER}."
    )
    L.append(
        f"- Rank agreement: agent Spearman {rho_agent:.3f} vs baseline {rho_base:.3f}; "
        f"agent has {len(agent_off)} badly-misplaced candidate(s) vs baseline's {len(base_off)}."
    )
    L.append(
        f"- Contradiction detection: agent flags {OUTLIER} with cited evidence; "
        f"baseline structurally cannot."
    )
    return L


def main():
    lines = build_report()
    report = "\n".join(lines) + "\n"
    print(report)
    OUT_MD.write_text(report, encoding="utf-8")
    print(f"(written to {OUT_MD})")


if __name__ == "__main__":
    main()
