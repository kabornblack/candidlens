"""
CandidLens agent solution — Stage 3: scoring.

Produces the 1-5 per-category scores and the overall score from the
crosscheck results — NOT from the raw candidate files. This is where the
agent solution is meant to beat the baseline: a contradicted CV claim
counts against a candidate here, instead of being silently averaged in.

Inputs:
  solution/crosscheck_results.json  — per-cv_claim status + discrepancy_summary
  solution/extracted_claims.json    — the category tag on every claim
  (joined by candidate; raw candidate files are never read here)

Output: solution/score_results.json — a list of
    {"candidate": "candidate_03",
     "category_scores":    {"python_go": 3, "rest_api_design": 2, ...},
     "category_rationale": {"python_go": "...", ...},
     "overall": 2,
     "overall_rationale": "..."}

Usage:
    pip install -r requirements.txt
    # put ANTHROPIC_API_KEY in a local .env file
    python solution/score.py
"""

import json
import pathlib

import anthropic
from dotenv import load_dotenv

# This exact model string must be identical across baseline/baseline.py and
# every solution/*.py stage (extract, score, crosscheck, aggregate) so the
# baseline and the agent solution are compared fairly using the same model.
MODEL = "claude-sonnet-5"

CATEGORIES = [
    "python_go",
    "rest_api_design",
    "sql_data_modeling",
    "cloud_infrastructure",
    "ownership_collab",
]

ROOT = pathlib.Path(__file__).resolve().parent.parent
CROSSCHECK_PATH = ROOT / "solution" / "crosscheck_results.json"
EXTRACTED_PATH = ROOT / "solution" / "extracted_claims.json"
OUT_PATH = ROOT / "solution" / "score_results.json"


def load_inputs():
    """Merge the two Stage 1/2 files into one payload per candidate."""
    extracted = {e["candidate"]: e for e in json.loads(EXTRACTED_PATH.read_text(encoding="utf-8"))}
    crosscheck = {c["candidate"]: c for c in json.loads(CROSSCHECK_PATH.read_text(encoding="utf-8"))}

    payloads = []
    for name, ext in extracted.items():
        cc = crosscheck.get(name, {"claim_checks": [], "discrepancy_summary": []})
        status_by_claim = {chk["cv_claim"]: chk["status"] for chk in cc.get("claim_checks", [])}

        categories = {cat: {"cv_claims": [], "interview_claims": []} for cat in CATEGORIES}
        general = {"cv_claims": [], "interview_claims": []}

        for claim in ext.get("cv_claims", []):
            bucket = categories.get(claim["category"], general)
            bucket["cv_claims"].append({
                "text": claim["text"],
                "status": status_by_claim.get(claim["text"], "uncorroborated"),
            })
        for claim in ext.get("interview_claims", []):
            bucket = categories.get(claim["category"], general)
            bucket["interview_claims"].append(claim["text"])

        payloads.append({
            "candidate": name,
            "categories": categories,
            "general_claims": general,
            "discrepancy_summary": cc.get("discrepancy_summary", []),
        })
    return payloads


def build_prompt(payload):
    categories_json = json.dumps(payload["categories"], indent=2)
    general_json = json.dumps(payload["general_claims"], indent=2)
    discrepancy_json = json.dumps(payload["discrepancy_summary"], indent=2)
    return f"""You are scoring a backend engineer candidate against a job description
with 5 skill categories: python_go, rest_api_design, sql_data_modeling,
cloud_infrastructure, ownership_collab.

You are given, per category, the candidate's CV claims (each tagged with a
crosscheck status) and their interview observations. Work ONLY from this
data — do not invent evidence.

Score each category from 1 (poor) to 5 (excellent), and give an overall
score from 1 to 5. Scores are integers.

Apply these rules exactly:
1. A "corroborated" CV claim weighs POSITIVELY toward its category score —
   the interview backed it up.
2. A "contradicted" CV claim weighs NEGATIVELY. It is worse than having no
   claim at all: it is not merely missing evidence, it is a credibility
   problem. A category with a contradicted claim should score lower than the
   same category would with that claim simply absent.
3. An "uncorroborated" CV claim is WEAK/MODERATE evidence — some credit, not
   full credit, and not a penalty for the claim's status alone.
   BUT: the "uncorroborated" label only means the crosscheck stage found no
   CV/interview conflict. It does NOT mean the interview was silent. If the
   interview_claims for that category show the candidate ACTIVELY FAILING or
   being UNABLE to do a task in that area (e.g. "could not write a two-table
   join", "never deployed anything", "could not explain X"), that
   demonstrated weakness MUST pull the category score down — score the
   category on what the interview actually demonstrated, not on the status
   label. Demonstrated inability is real negative evidence even when the
   crosscheck called the CV claim merely "uncorroborated".
4. Interview observations that are not tied to a CV claim still inform the
   score (positive or negative) on their own. When such standalone negative
   evidence exists WITHOUT any corresponding "contradicted" CV claim (e.g. a
   behavioural or collaboration red flag, but the CV never claimed
   otherwise), discount the affected category MODERATELY. This is a softer
   penalty than the integrity cap in rule 5 — a behavioural red flag is not
   a credibility violation. Do not treat it as severely as a CV/interview
   contradiction.
5. INTEGRITY CAP: if there are 2 or more "contradicted" CV claims in
   ownership_collab, OR 2 or more "contradicted" claims that together
   amount to a credibility problem (e.g. overstated seniority, fabricated
   ownership, claimed leadership the interview disproves), then the OVERALL
   score MUST be capped below the raw average of the 5 category scores —
   reflect the broken trust, not just the arithmetic. This cap is reserved
   for CV/interview CONTRADICTIONS — do not apply it for standalone
   behavioural evidence (that is rule 4's moderate discount).

For every category score AND the overall score, include a one-line
rationale referencing the actual evidence (not just restating the number).

=== CLAIMS BY CATEGORY (with crosscheck status on CV claims) ===
{categories_json}

=== GENERAL CLAIMS (context, not a scored category) ===
{general_json}

=== DISCREPANCY SUMMARY (from the crosscheck stage) ===
{discrepancy_json}

Respond with ONLY a JSON object of this shape:
{{"category_scores": {{"python_go": 3, "rest_api_design": 2, "sql_data_modeling": 3, "cloud_infrastructure": 3, "ownership_collab": 2}},
  "category_rationale": {{"python_go": "...", "rest_api_design": "...", "sql_data_modeling": "...", "cloud_infrastructure": "...", "ownership_collab": "..."}},
  "overall": 2,
  "overall_rationale": "..."}}
"""


def parse_json(reply_text):
    """Pull the JSON object out of the model reply."""
    try:
        return json.loads(reply_text)
    except json.JSONDecodeError:
        start = reply_text.find("{")
        end = reply_text.rfind("}")
        return json.loads(reply_text[start:end + 1])


def score_candidate(client, name, payload):
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        messages=[{"role": "user", "content": build_prompt(payload)}],
    )
    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            f"Scoring truncated for {name}: response hit max_tokens limit "
            f"before completing"
        )
    reply_text = "".join(b.text for b in response.content if b.type == "text")
    return parse_json(reply_text)


def main():
    load_dotenv()  # picks up ANTHROPIC_API_KEY from a local .env file if present
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    results = []
    for payload in load_inputs():
        name = payload["candidate"]
        print(f"Scoring {name}...")
        scored = score_candidate(client, name, payload)
        results.append({
            "candidate": name,
            "category_scores": scored.get("category_scores", {}),
            "category_rationale": scored.get("category_rationale", {}),
            "overall": scored.get("overall"),
            "overall_rationale": scored.get("overall_rationale", ""),
        })

    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} score results to {OUT_PATH}")


if __name__ == "__main__":
    main()
