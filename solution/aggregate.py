"""
CandidLens agent solution — Stage 4: final aggregation.

Pure Python data assembly — NO API call. Merges the outputs of the three
prior stages into one combined report per candidate, ranks all 10 by overall
score, and writes both a JSON and a recruiter-readable markdown report.

Inputs:
  solution/extracted_claims.json    (Stage 1 — used for the canonical
                                     candidate list / original order)
  solution/crosscheck_results.json  (Stage 2 — discrepancy_summary + the
                                     contradicted claims)
  solution/score_results.json       (Stage 3 — category + overall scores
                                     and rationales)

The candidate's display name is read from the H1 of
data/candidates/<candidate>.md (the only input beyond the three JSONs).

Outputs:
  solution/final_report.json   list of combined report objects, ranked
  solution/final_report.md     human-readable, one section per candidate

Usage:
    python solution/aggregate.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXTRACTED_PATH = ROOT / "solution" / "extracted_claims.json"
CROSSCHECK_PATH = ROOT / "solution" / "crosscheck_results.json"
SCORE_PATH = ROOT / "solution" / "score_results.json"
CANDIDATES_DIR = ROOT / "data" / "candidates"
OUT_JSON = ROOT / "solution" / "final_report.json"
OUT_MD = ROOT / "solution" / "final_report.md"

CATEGORIES = [
    "python_go",
    "rest_api_design",
    "sql_data_modeling",
    "cloud_infrastructure",
    "ownership_collab",
]
CATEGORY_LABELS = {
    "python_go": "Python / Go proficiency",
    "rest_api_design": "REST API design",
    "sql_data_modeling": "SQL / data modeling",
    "cloud_infrastructure": "Cloud infrastructure",
    "ownership_collab": "Ownership & collaboration",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_name(candidate_id):
    """Real name from the candidate file's H1, e.g.
    '# Candidate 01 - Priya Raghunathan' -> 'Priya Raghunathan'.
    Falls back to a title-cased id if the H1 can't be parsed."""
    path = CANDIDATES_DIR / f"{candidate_id}.md"
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("# "):
                heading = line[2:].strip()
                for sep in ("—", "–", " - "):  # em dash, en dash, hyphen
                    if sep in heading:
                        return heading.split(sep, 1)[1].strip()
                return heading
    except OSError:
        pass
    return candidate_id.replace("_", " ").title()


def build_reports():
    """Merge the three stage outputs into one report object per candidate."""
    extracted = load_json(EXTRACTED_PATH)
    crosscheck = {c["candidate"]: c for c in load_json(CROSSCHECK_PATH)}
    scores = {s["candidate"]: s for s in load_json(SCORE_PATH)}

    order = [e["candidate"] for e in extracted]  # canonical Stage 1 order

    missing = [cid for cid in order if cid not in crosscheck or cid not in scores]
    if missing:
        raise ValueError(f"crosscheck/score results missing candidates: {missing}")

    reports = []
    for cid in order:
        cc = crosscheck[cid]
        sc = scores[cid]

        if sc.get("overall") is None:
            raise ValueError(f"{cid}: score_results.json has no 'overall' score")

        contradicted = [
            {
                "cv_claim": chk["cv_claim"],
                "conflicting_interview_claims": chk.get("conflicting_interview_claims", []),
            }
            for chk in cc.get("claim_checks", [])
            if chk.get("status") == "contradicted"
        ]

        reports.append({
            "candidate": cid,
            "name": candidate_name(cid),
            "category_scores": sc.get("category_scores", {}),
            "overall": sc["overall"],
            "overall_rationale": sc.get("overall_rationale", ""),
            "category_rationale": sc.get("category_rationale", {}),
            "discrepancy_summary": cc.get("discrepancy_summary", []),
            "contradicted_claims": contradicted,
        })
    return reports


def rank_reports(reports):
    """Sort by overall descending; stable, so ties keep original order."""
    ranked = sorted(reports, key=lambda r: -r["overall"])
    for i, report in enumerate(ranked, start=1):
        report["rank"] = i
    return ranked


def write_json(ranked):
    OUT_JSON.write_text(json.dumps(ranked, indent=2), encoding="utf-8")


def write_markdown(ranked):
    lines = ["# CandidLens — Final Candidate Report", ""]
    lines.append(f"{len(ranked)} candidates, ranked by overall score.")
    lines.append("")

    for report in ranked:
        lines.append(f"## Rank {report['rank']} — {report['name']} ({report['candidate']})")
        lines.append("")
        lines.append(f"**Overall score: {report['overall']} / 5**")
        lines.append("")
        lines.append("| Category | Score |")
        lines.append("| --- | --- |")
        for cat in CATEGORIES:
            score = report["category_scores"].get(cat, "-")
            lines.append(f"| {CATEGORY_LABELS[cat]} | {score} / 5 |")
        lines.append("")

        summary = report["discrepancy_summary"]
        if summary:
            lines.append("**Discrepancies flagged:**")
            lines.append("")
            for item in summary:
                lines.append(f"- {item}")
        else:
            lines.append("**Discrepancies flagged:** None.")
        lines.append("")

        lines.append(report["overall_rationale"])
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    ranked = rank_reports(build_reports())
    write_json(ranked)
    write_markdown(ranked)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print()
    for report in ranked:
        print(f"  {report['rank']:>2}. {report['name']} ({report['candidate']}) — overall {report['overall']}")


if __name__ == "__main__":
    main()
